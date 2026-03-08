import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(page_icon="🇫🇷", page_title="Job Hub Data France", layout="wide")

st.title("🎯 Hub d'Offres Data France")
st.markdown("Trouvez votre futur **Stage** ou **Alternance** en un clic.")

csv_path = "data/jobs.csv"

if os.path.exists(csv_path):
    # --- LOGIQUE DE DATE DE MISE À JOUR ---
    mod_time = os.path.getmtime(csv_path)
    last_update = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
    
    # Lecture du CSV (sans cache pour voir les mises à jour du scraper immédiatement)
    df = pd.read_csv(csv_path)
    
    st.sidebar.header("🔍 Configuration")

    # 1. Type de Contrat
    tipo_contrato = st.sidebar.radio(
        "Type de contrat souhaité :",
        options=["Stage", "Alternance", "CDI/Autre"], # Ajout de CDI/Autre si besoin
        index=0
    )

    # 2. Ville
    villes_list = [
        "Toute la France", "Paris", "Lyon", "Lille", "Bordeaux", 
        "Nantes", "Toulouse", "Marseille", "Strasbourg", "Montpellier"
    ]
    selected_ville = st.sidebar.selectbox("Ville :", options=villes_list)

    # 3. Spécialité
    roles = ["Tous les rôles", "Data Analyst", "Data Engineer", "Data Scientist", "BI / Décisionnel"]
    selected_role = st.sidebar.selectbox("Spécialité :", options=roles)

    # --- LOGIQUE DE FILTRAGE ---
    mask = (df['Type'] == tipo_contrato)
    
    if selected_ville != "Toute la France":
        mask = mask & (df['Ville'].str.contains(selected_ville, case=False, na=False))
    
    # Filtres par mots-clés dans le titre du poste
    if selected_role == "Data Analyst":
        mask = mask & (df['Poste'].str.contains("Analyst|Analytics", case=False, na=False))
    
    elif selected_role == "Data Engineer":
        mask = mask & (df['Poste'].str.contains("Engineer|Ingénieur|Data Eng", case=False, na=False))
    
    elif selected_role == "Data Scientist":
        mask = mask & (df['Poste'].str.contains("Scientist|Science", case=False, na=False))
    
    elif selected_role == "BI / Décisionnel":
        mask = mask & (df['Poste'].str.contains("BI|Business Intelligence|Décisionnel|Power BI|Tableau", case=False, na=False))
    
    df_filtered = df[mask]

    # --- AFFICHAGE DES INDICATEURS (KPIs) ---
    col1, col2 = st.columns(2)
    col1.metric("Offres trouvées", len(df_filtered))
    col2.metric("Dernière mise à jour", last_update)
    
    st.divider()

    # --- AFFICHAGE DES RÉSULTATS ---
    if not df_filtered.empty:
        # Trier par date (les plus récents en premier)
        for _, row in df_filtered.iterrows():
            # Nettoyage de l'affichage de la source
            source_display = row['Source'].upper() 
            
            with st.expander(f"💼 {row['Poste']} - {row['Entreprise']}"):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"📍 **Ville :** {row['Ville']}")
                    st.write(f"📄 **Type :** {row['Type']}")
                    st.write(f"🌐 **Source :** `{source_display}`")
                    st.write(f"📅 **Ajouté le :** {row['Date']}")
                with c2:
                    st.link_button("Voir l'offre ↗️", row['Lien'], use_container_width=True)
    else:
        st.info(f"Aucune offre de {tipo_contrato} trouvée pour {selected_role} actuellement.")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"🕒 Données actualisées le : {last_update}")
else:
    st.error("Base de données introuvable. Veuillez lancer le scraper d'abord.")