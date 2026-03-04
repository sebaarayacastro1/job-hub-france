import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_icon="🇫🇷", page_title="Job Hub Data France", layout="wide")

st.title("🎯 Hub d'Offres Data France")
st.markdown("Find your future **Stage** or **Alternance** in one click.")

csv_path = "data/jobs.csv"

if os.path.exists(csv_path):
    # --- LAST UPDATE LOGIC ---
    mod_time = os.path.getmtime(csv_path)
    last_update = datetime.fromtimestamp(mod_time).strftime("%d/%m/%Y %H:%M")
    
    df = pd.read_csv(csv_path)
    
    st.sidebar.header("🔍 Configuration")

    # 1. Contract Type
    tipo_contrato = st.sidebar.radio(
        "Contract type:",
        options=["Stage", "Alternance"],
        index=0
    )

    # 2. City Selection
    villes_list = [
        "Toute la France", "Lille", "Paris", "Lyon", "Bordeaux", 
        "Nantes", "Toulouse", "Marseille", "Strasbourg", "Montpellier"
    ]
    selected_ville = st.sidebar.selectbox("City:", options=villes_list)

    # 3. Role Specialization
    roles = ["All Roles", "Data Analyst", "Data Engineer", "Data Scientist", "Other / BI / Software"]
    selected_role = st.sidebar.selectbox("Specialization:", options=roles)

    # --- FILTERING LOGIC ---
    # Filter by Contract Type first
    mask = (df['Type'] == tipo_contrato)
    
    # Filter by City if a specific one is selected
    if selected_ville != "Toute la France":
        mask = mask & (df['Ville'].str.contains(selected_ville, case=False, na=False))
    
    # Filter by Role Keywords
    if selected_role == "Data Analyst":
        # Includes Business Intelligence and Decision-making keywords (SIAD profile)
        mask = mask & (df['Poste'].str.contains("Analyst|BI|Business Intelligence|Décisionnel|Reporting|Data Viz", case=False, na=False))
    
    elif selected_role == "Data Engineer":
        # Includes Engineering, Cloud, and ETL keywords
        mask = mask & (df['Poste'].str.contains("Engineer|Ingénieur|Big Data|Cloud|ETL|Flow|Architecture", case=False, na=False))
    
    elif selected_role == "Data Scientist":
        # Includes Machine Learning and AI keywords
        mask = mask & (df['Poste'].str.contains("Scientist|Science|ML|Machine Learning|IA|AI|Deep Learning", case=False, na=False))
    
    elif selected_role == "Other / BI / Software":
        # Capture everything else that doesn't fit the main 3 categories
        main_keywords = "Analyst|Engineer|Ingénieur|Scientist|Science"
        mask = mask & (~df['Poste'].str.contains(main_keywords, case=False, na=False))
    
    # Apply filters
    df_filtered = df[mask]

    # --- KPI INDICATORS ---
    col1, col2 = st.columns(2)
    col1.metric("Offers Found", len(df_filtered))
    col2.metric("Last Update", last_update)
    
    st.divider()

    # --- RESULTS DISPLAY ---
    if not df_filtered.empty:
        for _, row in df_filtered.iterrows():
            with st.expander(f"💼 {row['Poste']} - {row['Entreprise']}"):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.write(f"📍 **City:** {row['Ville']}")
                    st.write(f"📄 **Type:** {row['Type']}")
                    st.write(f"🌐 **Source:** {row['Source'].capitalize()}")
                    st.write(f"📅 **Added on:** {row['Date']}")
                with c2:
                    st.link_button("View Offer ↗️", row['Lien'], use_container_width=True)
    else:
        loc_phrase = "in France" if selected_ville == "Toute la France" else f"in {selected_ville}"
        st.info(f"No {tipo_contrato} offers found for {selected_role} {loc_phrase} in the last 72h.")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"🕒 Database updated: {last_update}")
    st.sidebar.info("Data scraped from LinkedIn, Indeed, Google Jobs and France Travail.")

else:
    st.error("Database not found. Please run the scraper script first.")