from jobspy import scrape_jobs
import pandas as pd
import os
import datetime

def run_real_scraper():
    search_query = "Data Analyst, Data Engineer, Data Scientist"
    print(f"🚀 Recherche d'offres en France pour : {search_query}...")

    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "glassdoor"],
            search_term=search_query,
            location="France",
            results_wanted=100, 
            hours_old=72,
            country_freedom=True,
        )

        if not jobs.empty:
            df_final = jobs[['title', 'company', 'location', 'job_url', 'site']].copy()
            
            df_final.columns = ['Poste', 'Entreprise', 'Ville', 'Lien', 'Source']
            df_final['Date'] = datetime.date.today()
            
            def classify(title):
                t = str(title).lower()
                if any(x in t for x in ['alternance', 'apprenti', 'apprentissage']):
                    return "Alternance"
                if any(x in t for x in ['stage', 'intern', 'stagiaire']):
                    return "Stage"
                return "CDI/Autre"
            
            df_final['Type'] = df_final['Poste'].apply(classify)
            
            os.makedirs('data', exist_ok=True)
            df_final.to_csv("data/jobs.csv", index=False, encoding='utf-8')
            print(f"✅ Succès ! {len(df_final)} offres récupérées.")
        else:
            print("⚠️ Aucune offre trouvée dans les dernières 72 heures.")

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")

if __name__ == "__main__":
    run_real_scraper()
