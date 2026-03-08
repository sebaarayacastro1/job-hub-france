import pandas as pd
import os
import datetime
from jobspy import scrape_jobs

def run_real_scraper():
    # 1. Definimos las búsquedas
    # Usamos operadores de Google para forzar resultados de WTTJ y otros portales
    queries = [
        "Data Analyst Stage France",
        "Data Engineer Stage France",
        "site:welcometothejungle.com Data Analyst Stage",
        "site:hellowork.com Data Engineer France"
    ]
    
    print(f"🚀 Démarrage du scraping global (LinkedIn, Indeed, Glassdoor, WTTJ via Google)...")
    
    all_results = []

    for q in queries:
        try:
            print(f"🔍 Recherche de : {q}...")
            # 'google' en site_name permite buscar en WTTJ/Hellowork sin bloqueos
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor", "google"], 
                search_term=q,
                location="France",
                results_wanted=40,
                hours_old=168,
                country_freedom=True 
            )
            
            if not jobs.empty:
                all_results.append(jobs)
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche '{q}': {e}")

    # 2. Procesar los resultados
    if all_results:
        df_new = pd.concat(all_results, ignore_index=True)
        
        # Selección y renombrado de columnas
        df_new = df_new[['title', 'company', 'location', 'job_url', 'site']].copy()
        df_new.columns = ['Poste', 'Entreprise', 'Ville', 'Lien', 'Source']
        
        # Limpieza de la columna Source para que sea más legible
        df_new['Source'] = df_new['Source'].apply(lambda x: "WTTJ/Hellowork" if x == "google" else x)
        
        # Añadir fecha y clasificar
        df_new['Date'] = datetime.date.today().strftime('%d/%m/%Y')
        
        def classify(title):
            t = str(title).lower()
            if any(x in t for x in ['stage', 'intern', 'stagiaire']): return "Stage"
            if any(x in t for x in ['alternance', 'apprenti', 'apprentissage']): return "Alternance"
            return "CDI/Autre"
        
        df_new['Type'] = df_new['Poste'].apply(classify)

        # 3. Lógica de Actualización (Merge con archivo existente)
        csv_path = "data/jobs.csv"
        os.makedirs('data', exist_ok=True)
        
        if os.path.exists(csv_path):
            df_old = pd.read_csv(csv_path)
            # Combinamos y eliminamos duplicados por el enlace (Lien)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
            df_final = df_final.drop_duplicates(subset=['Lien'], keep='first')
        else:
            df_final = df_new

        # Ordenar: Stage primero, luego por fecha
        priority = {'Stage': 0, 'Alternance': 1, 'CDI/Autre': 2}
        df_final['Priority'] = df_final['Type'].map(priority)
        df_final = df_final.sort_values(by=['Priority', 'Date'], ascending=[True, False]).drop(columns=['Priority'])
        
        # Guardar
        df_final.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"🎉 Succès ! {len(df_final)} offres totales dans le fichier data/jobs.csv")
    else:
        print("❌ Aucune offre trouvée aujourd'hui.")

if __name__ == "__main__":
    run_real_scraper()