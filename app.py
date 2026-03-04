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
    
    df = pd.read_csv(csv_path)
    
    st.sidebar.header("🔍 Configuration")

    # 1. Type de Contrat
    tipo_contrato = st.sidebar.radio(
        "Type de contrat souhaité :",
        options=["Stage", "Alternance"],
        index=0
    )

    # 2. Ville
    villes_list = [
        "Toute la France", "Lille", "Paris", "Lyon", "Bordeaux", 
        "Nantes", "Toulouse", "Marseille", "Strasbourg", "Montpellier"
    ]
    selected_ville = st.sidebar.selectbox("Ville :", options=villes_list)

    # 3. Spécialité
    roles = ["Tous les rôles", "Data Analyst", "Data Engineer", "Data Scientist", "Autre / BI / Software"]
    selected_role = st.sidebar.selectbox("Spécialité :", options=roles)

    # --- LOGIQUE DE FILTRAGE ---
    mask = (df['Type'] == tipo_contrato)
    
    if selected_ville != "Toute la France":
        mask = mask & (df['Ville'].str.contains(selected_ville, case=False, na=False))
    
    # Logic for strict and specific filtering
    if selected_role == "Data Analyst":
        mask = mask & (df['Poste'].str.contains("Analyst|BI|Business Intelligence|Décisionnel", case=False, na=False))
    
    elif selected_role == "Data Engineer":
        mask = mask & (df['Poste'].str.contains("Engineer|Ingénieur|Big Data|ETL", case=False, na=False))
    
    elif selected_role == "Data Scientist":
        # Strict filter for Data Scientist or Data Science only
        mask = mask & (df['Poste'].str.contains("Data Scientist|Data Science", case=False, na=False))
    
    elif selected_role == "Autre / BI / Software":
        # Exclude common keywords to show everything else
        excluded = "Analyst|Engineer|Ingénieur|Scientist|Science|BI|Business Intelligence"
        mask = mask & (~df['Poste'].str.contains(excluded, case=False, na=False))
    
    df_filtered = df[mask]

    # --- AFFICHAGE DES INDICATEURS (KPIs) ---
    col1, col2 = st.columns(2)
    col1.metric("Offres trouvées", len(df_filtered))
    col2.metric("Dernière mise à jour", last_update)
    
    st.divider()

    # --- AFFICHAGE DES RÉSULTATS ---
    if not df_filtered.empty:
        for _, row in df_filtered.iterrows():
            with st.expander(f"💼 {row['Poste']} - {row['Entreprise']}"):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"📍 **Ville :** {row['Ville']}")
                    st.write(f"📄 **Type :** {row['Type']}")
                    st.write(f"🌐 **Source :** {row['Source'].capitalize()}")
                    st.write(f"📅 **Ajouté le :** {row['Date']}")
                with c2:
                    st.link_button("Voir l'offre ↗️", row['Lien'], use_container_width=True)
    else:
        loc_phrase = "en France" if selected_ville == "Toute la France" else f"à {selected_ville}"
        st.info(f"Désolé, aucune offre de {tipo_contrato} n'est disponible pour {selected_role} {loc_phrase}.")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"🕒 Données actualisées le : {last_update}")
else:
    st.error("Base de données introuvable. Lancez d'abord 'python scraper_reel.py'.")