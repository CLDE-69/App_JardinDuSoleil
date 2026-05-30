import streamlit as st
import pandas as pd

# Configuration de la page mobile-friendly
st.set_page_config(page_title="Jardin du Soleil", page_icon="🌱", layout="centered")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=600)  # Met en cache 10 min pour éviter de saturer le Sheets
def charger_donnees():
    url_taches = st.secrets["url_donnees"] #onglet Données
    url_plantes = st.secrets["url_plantes"] #onglet plantes

    df_t = pd.read_csv(url_taches)
    df_p = pd.read_csv(url_plantes)

    # Nettoyage rapide des espaces dans les noms pour correspondre parfaitement
    df_t['Plante / Cible'] = df_t['Plante / Cible'].str.strip()
    df_p['Plante'] = df_p['Plante'].str.strip()

    return df_t, df_p

try:
    df, df_plantes = charger_donnees()
# except Exception as e:
#     st.error("Erreur lors du chargement des onglets Google Sheets. Vérifiez les URLs dans les Secrets.")
#     st.stop()
except Exception as e:
    st.error(f"Détail de l'erreur : {e}")
    st.stop()

# --- FONCTION POP-UP (FICHE DE CULTURE VINTAGE) ---
@st.dialog("📖 Fiche de Culture Technique")
def afficher_fiche_plante(nom_plante):
    # Recherche du légume dans la base "Plantes"
    info = df_plantes[df_plantes['Plante'].str.lower() == nom_plante.lower()]

    if not info.empty:
        row = info.iloc[0]
        st.markdown(f"## {row['Plante']}  \n*Famille des {row['Famille']}*")

        # Affichage de l'illustration ancienne
        if pd.notna(row['URL_Image_Vintage']):
            st.image(row['URL_Image_Vintage'], caption=f"Illustration ancienne de {row['Plante']}",
                     use_container_width=True)

        # Structure en colonnes des données agronomiques
        st.markdown("### 🛠️ Itinéraire technique")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**📏 Écartement sur le rang :** \n{row['Distance_Rang']}")
            st.markdown(f"**↔️ Écartement entre rangs :** \n{row['Distance_Entre_Rang']}")
            st.markdown(f"**🥩 Gourmandise du sol :** \n{row['Gourmandise']}")
        with c2:
            st.markdown(f"**🌱 Période de semis :** \n{row['Semis_Periode']}")
            st.markdown(f"**🪵 Période de plantation :** \n{row['Plantation_Periode']}")

        st.divider()

        # Compagnonnage
        st.markdown("### 🤝 Compagnonnage (Compagnons pro)")
        st.success(f"**👍 Plantes amies :** \n{row['Associations_Amies']}")
        st.error(f"**👎 Plantes ennemies :** \n{row['Associations_Ennemies']}")

        st.divider()

        # Mémo pro
        st.markdown("### 💡 Conseils & Mémo technique")
        st.info(row['Memo_Technique'])
    else:
        st.warning(
            f"Désolé, aucune fiche technique détaillée n'a été trouvée pour '{nom_plante}' dans l'onglet Plantes.")
        st.info("Vérifiez que l'orthographe dans votre calendrier correspond exactement à l'onglet Plantes.")

# --- INTERFACE GRAPHIQUE ---
st.title("🌱 Mon Jardin du Soleil")

# 1. Filtre par Saison via des onglets horizontaux cliquables
saisons_disponibles = ["Hiver", "Printemps", "Été", "Automne"]
saison_choisie = st.radio(
    "🍂 Choisissez une saison :",
    saisons_disponibles,
    horizontal=True
)

df_filtre = df[df['Saison'] == saison_choisie]

# 2. Filtres complémentaires secondaires (Mois / Quinzaine / Zone)
col1, col2, col3 = st.columns(3)

with col1:
    mois_disponibles = df_filtre['Mois'].unique() if not df_filtre.empty else []
    mois_choisi = st.selectbox("📅 Mois :", mois_disponibles)
    if mois_choisi:
        df_filtre = df_filtre[df_filtre['Mois'] == mois_choisi]

with col2:
    quinzaine_choisie = st.selectbox("⏳ Période :", ["Toutes", "1ère quinzaine", "2ème quinzaine"])
    if quinzaine_choisie != "Toutes" and not df_filtre.empty:
        df_filtre = df_filtre[df_filtre['Quinzaine'] == quinzaine_choisie]

with col3:
    zone_choisie = st.selectbox("🏡 Zone :", ["Tout", "Potager", "Jardin"])
    if zone_choisie != "Tout" and not df_filtre.empty:
        df_filtre = df_filtre[df_filtre['Zone'] == zone_choisie]

# --- AFFICHAGE DES CARTES DE TRAVAUX ---
st.divider()
if mois_choisi:
    st.subheader(
        f"📋 Travaux de {mois_choisi} ({quinzaine_choisie.lower() if quinzaine_choisie != 'Toutes' else 'mois complet'})")

if df_filtre.empty:
    st.info("🦥 Pas de travaux spécifiques prévus pour cette sélection. Repos ou observation !")
else:
    for index, row in df_filtre.iterrows():
        emoji = "🥕" if row['Zone'] == "Potager" else "🌸"
        badge = "📚 Source" if row['Type'] == 'Livre' else "➕ Mon Ajout"

        # Création de la carte pour chaque tâche
        with st.container(border=True):
            # Zone de texte à gauche, zone de boutons à droite
            c_texte, c_bouton = st.columns([0.70, 0.30], vertical_alignment="center")

            with c_texte:
                st.markdown(f"### {emoji} {row['Action']} : **{row['Plante / Cible']}**")
                st.write(row['Description / Précision'])
                st.caption(f"📍 {row['Zone']} | {row['Quinzaine']} | {badge}")

            with c_bouton:
                # 1. On récupère la cellule "Plante / Cible" (ex: "Carotte, Chou, Laitue")
                cellule_plante = str(row['Plante / Cible'])

                # 2. On la découpe par les virgules et on nettoie les espaces
                plantes_candidates = [p.strip() for p in cellule_plante.split(",")]

                # 3. Pour chaque plante isolée, on vérifie si sa fiche existe
                for plante_nom in plantes_candidates:
                    # Vérification insensible à la casse
                    existe = df_plantes['Plante'].str.lower().eq(plante_nom.lower()).any()

                    if existe:
                        # On affiche un bouton personnalisé pour CHAQUE légume trouvé
                        if st.button(f"📖 {plante_nom}", key=f"btn_{index}_{plante_nom}"):
                            afficher_fiche_plante(plante_nom)

# --- AJOUT DU FOOTER VALIDE ---
with st.bottom:
    st.caption(
        "© 2026 made with love by CLDE. All rights reserved",
        text_alignment="center",
    )