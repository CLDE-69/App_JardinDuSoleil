import streamlit as st
import pandas as pd

# Configuration de la page mobile-friendly
st.set_page_config(page_title="Mon Jardin", layout="centered")


st.title("🌱 Mon Agenda Jardin & Potager")

# 1. Connexion sécurisée et directe via Pandas
@st.cache_data(ttl=600)  # Cache de 10 minutes
def charger_donnees():
    # On va chercher l'URL cachée dans les secrets
    url = st.secrets["url_donnees"]
    # Pandas télécharge et lit directement le CSV
    return pd.read_csv(url)

try:
    df = charger_donnees()
    st.success("Connexion réussie ! 🎉 Les données sont chargées.")
except Exception as e:
    st.error("Erreur de récupération des données :")
    st.exception(e)
    st.stop()

# 2. Filtre par mois
liste_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre",
              "Novembre", "Décembre"]
mois_choisi = st.selectbox("Choisissez un mois à afficher :", liste_mois, index=4)  # Mai par défaut

# 3. Filtrage des données
travaux_du_mois = df[df["Mois"] == mois_choisi]

# 4. Affichage des résultats
st.subheader(f"🗓️ Travaux de {mois_choisi}")

if travaux_du_mois.empty:
    st.info("Aucun travail de prévu pour ce mois-ci. Profitez-en pour vous reposer ! ☕")
else:
    zones = travaux_du_mois["Zone"].unique()
    for zone in zones:
        st.write(f"### 🏡 {zone}")
        travaux_zone = travaux_du_mois[travaux_du_mois["Zone"] == zone]

        for index, row in travaux_zone.iterrows():
            st.markdown(f"**{row['Action']}** : *{row['Plante']}*")
            if pd.notna(row['Description']):
                st.caption(f"ℹ️ {row['Description']}")
            st.divider()

# 5. Zone d'ajout de tâche personnalisée (à coller tout en bas de app.py)
st.divider()

# Un "expander" permet de cacher le formulaire pour ne pas encombrer l'écran du téléphone
with st.expander("➕ Ajouter un travail personnalisé"):
    st.write("Remplissez le formulaire ci-dessous pour ajouter une tâche à votre calendrier :")

    # REMPLACEZ LE LIEN CI-DESSOUS PAR VOTRE LIEN GOOGLE FORM COPIÉ À L'ÉTAPE 1
    url_formulaire = "https://docs.google.com/forms/d/e/1FAIpQLSc0_V-2o_wAWKTJW2PvHLgbqro_Dq5PjvrpRXwso5vxtR1tiA/viewform?usp=publish-editor"

    # Cette ligne permet d'intégrer proprement le formulaire Google dans l'interface Streamlit
    st.components.v1.iframe(url_formulaire, height=600, scrolling=True)

    st.info("💡 Une fois envoyé, rafraîchissez la page de l'application pour voir votre nouvelle tâche apparaître !")