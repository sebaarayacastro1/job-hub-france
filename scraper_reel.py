from jobspy import scrape_jobs
import pandas as pd
import os
import datetime

def run_real_scraper():
    # Adding SIAD and Stage specific terms to the query
    search_query = "Data Analyst Stage, Data Engineer Stage, Data Scientist, Informatique Décisionnelle"
    print(f"🚀 Recherche d'offres en France pour : {search_query}...")

    try:
        # Added google (for WTTJ/Hellowork) and pole_emploi (France Travail)
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "google", "glassdoor", "pole_emploi"],
            search_term=search_query,
            location="France",
            results_wanted=150, 
            hours_old=168,
            country_freedom=True,
        )

        if not jobs.empty:
            df_final = jobs[['title', 'company', 'location', 'job_url', 'site']].copy()
            
            df_final.columns = ['Poste', 'Entreprise', 'Ville', 'Lien', 'Source']
            df_final['Date'] = datetime.date.today().strftime('%d/%m/%Y')
            
            def classify(title):
                t = str(title).lower()
                # Prioritizing Stage classification
                if any(x in t for x in ['stage', 'intern', 'stagiaire', 'internship']):
                    return "Stage"
                if any(x in t for x in ['alternance', 'apprenti', 'apprentissage']):
                    return "Alternance"
                return "CDI/Autre"
            
            df_final['Type'] = df_final['Poste'].apply(classify)

            # Data Engineering: Drop duplicates by Link and sort by Type
            df_final = df_final.drop_duplicates(subset=['Lien'])
            
            # Sort to show Stage first in the CSV
            priority = {'Stage': 0, 'Alternance': 1, 'CDI/Autre': 2}
            df_final['Priority'] = df_final['Type'].map(priority)
            df_final = df_final.sort_values(by='Priority').drop(columns=['Priority'])
            
            os.makedirs('data', exist_ok=True)
            df_final.to_csv("data/jobs.csv", index=False, encoding='utf-8')
            print(f"✅ Succès ! {len(df_final)} offres récupérées.")
        else:
            print("⚠️ Aucune offre trouvée dans les dernières 72 heures.")

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {e}")

if __name__ == "__main__":
    run_real_scraper()