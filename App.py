import streamlit as st
import pandas as pd

# --- CHARGEMENT DES DONNÉES ---
# (Assure-toi que l'onglet "Total" est bien le premier onglet à gauche dans ton Google Sheets)
url = st.secrets["url_donnees"]
df = pd.read_csv(url)

st.title("🌱 Mon Jardin du Soleil")

# --- SYSTÈME DE FILTRES ERGONOMIQUES ---

# 1. Filtre par Saison (génère de superbes onglets horizontaux)
saisons_disponibles = ["Hiver", "Printemps", "Été", "Automne"]
saison_choisie = st.radio(
    "🍂 Choisissez une saison :",
    saisons_disponibles,
    horizontal=True
)

# On filtre le tableau selon la saison choisie
df_filtre = df[df['Saison'] == saison_choisie]

# 2. Filtres complémentaires en ligne
col1, col2, col3 = st.columns(3)

with col1:
    # Liste dynamique des mois correspondants à cette saison
    mois_disponibles = df_filtre['Mois'].unique() if not df_filtre.empty else []
    mois_choisi = st.selectbox("📅 Mois :", mois_disponibles)
    if mois_choisi:
        df_filtre = df_filtre[df_filtre['Mois'] == mois_choisi]

with col2:
    # Choix de la quinzaine
    quinzaine_choisie = st.selectbox("⏳ Période :", ["Toutes", "1ère quinzaine", "2ème quinzaine"])
    if quinzaine_choisie != "Toutes" and not df_filtre.empty:
        df_filtre = df_filtre[df_filtre['Quinzaine'] == quinzaine_choisie]

with col3:
    # Choix de la zone
    zone_choisie = st.selectbox("🏡 Zone :", ["Tout le jardin", "Potager", "Jardin"])
    if zone_choisie != "Tout le jardin" and not df_filtre.empty:
        df_filtre = df_filtre[df_filtre['Zone'] == zone_choisie]

# --- AFFICHAGE DES TRAVAUX ---
st.divider()
if mois_choisi:
    st.subheader(
        f"📋 Travaux de {mois_choisi} ({quinzaine_choisie.lower() if quinzaine_choisie != 'Toutes' else 'mois complet'})")

if df_filtre.empty:
    st.info("🦥 Pas de travaux spécifiques prévus pour cette sélection. Repos ou observation !")
else:
    # Affichage propre sous forme de liste de cartes de lecture
    for index, row in df_filtre.iterrows():
        # Détermination d'un émoji sympa selon la zone
        emoji = "🥕" if row['Zone'] == "Potager" else "🌸"

        # Style du badge (Perso ou Livre)
        badge = "📚 Source" if row['Type'] == 'Livre' else "➕ Mon Ajout"

        with st.container(border=True):
            st.markdown(f"### {emoji} {row['Action']} : **{row['Plante / Cible']}**")
            st.write(row['Description / Précision'])
            st.caption(f"📍 {row['Zone']} | 📅 {row['Quinzaine']} . {row['Mois']} | {badge}")

# --- AJOUT DU FOOTER VALIDE ---
with st.bottom:
    st.caption("© 2026 made with love by CLDE. All rights reserved", text_alignment="center")