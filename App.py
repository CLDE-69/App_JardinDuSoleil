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
            st.image(row['URL_Image_Vintage'],
                     use_container_width=True)

        # Structure en colonnes des données agronomiques
        st.markdown("### 🛠️ Itinéraire technique")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**📏 Écartement sur le rang :** \n{row['Distance_Rang']}")
            st.markdown(f"**↔️ Écartement entre rangs :** \n{row['Distance_Entre_Rang']}")
            st.markdown(f"**🪱 Gourmandise du sol :** \n{row['Gourmandise']}")
        with c2:
            st.markdown(f"**🌱 Période de semis :** \n{row['Semis_Periode']}")
            st.markdown(f"**🪴 Période de plantation :** \n{row['Plantation_Periode']}")

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
    "Choisissez une saison :",
    saisons_disponibles,
    horizontal=True
)

df_filtre = df[df['Saison'] == saison_choisie]

# 2. Filtres complémentaires secondaires (Mois / Quinzaine / Zone)
mois_ordre = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

if 'mois_choisi' not in st.session_state:
    st.session_state['mois_choisi'] = None

col1, col2, col3 = st.columns(3)

with col1:
    mois_disponibles = [m for m in mois_ordre if m in set(df_filtre['Mois'].unique())] if not df_filtre.empty else []

    if mois_disponibles:
        if st.session_state['mois_choisi'] not in mois_disponibles:
            st.session_state['mois_choisi'] = mois_disponibles[0]

        c_prev, c_sel, c_next = st.columns([1, 3, 1])
        with c_prev:
            if st.button("←", key="btn_mois_prev", help="Mois précédent", use_container_width=True):
                idx = mois_disponibles.index(st.session_state['mois_choisi'])
                st.session_state['mois_choisi'] = mois_disponibles[idx - 1] if idx > 0 else mois_disponibles[-1]
        with c_sel:
            mois_choisi = st.selectbox("📅 Mois :", mois_disponibles, index=mois_disponibles.index(st.session_state['mois_choisi']))
            st.session_state['mois_choisi'] = mois_choisi
        with c_next:
            if st.button("→", key="btn_mois_next", help="Mois suivant", use_container_width=True):
                idx = mois_disponibles.index(st.session_state['mois_choisi'])
                st.session_state['mois_choisi'] = mois_disponibles[(idx + 1) % len(mois_disponibles)]

        if mois_choisi:
            df_filtre = df_filtre[df_filtre['Mois'] == mois_choisi]
    else:
        mois_choisi = None
        st.info("Aucun mois disponible pour cette saison.")

with col2:
    quinzaine_choisie = st.selectbox("⏳ Période :", ["Toutes", "1ère quinzaine", "2ème quinzaine"])
    if quinzaine_choisie != "Toutes" and not df_filtre.empty:
        df_filtre = df_filtre[df_filtre['Quinzaine'] == quinzaine_choisie]

with col3:
    zone_choisie = st.selectbox("🏡 Zone :", ["Tout", "Potager", "Jardin"])
    if zone_choisie != "Tout" and not df_filtre.empty:
        df_filtre = df_filtre[df_filtre['Zone'] == zone_choisie]

# --- AFFICHAGE DES VUES : LISTE OU CALENDRIER ---
def afficher_boutons_fiches(row, identifiant, df_plantes):
    cellule_plante = str(row['Plante / Cible'])
    plantes_candidates = [p.strip() for p in cellule_plante.split(",") if p.strip()]

    for plante_nom in plantes_candidates:
        existe = df_plantes['Plante'].str.lower().eq(plante_nom.lower()).any()
        if existe:
            if st.button(f"📖 {plante_nom}", key=f"btn_{identifiant}_{plante_nom}"):
                afficher_fiche_plante(plante_nom)


def afficher_vue_liste(df_filtre, df_plantes):
    if df_filtre.empty:
        st.info("🦥 Pas de travaux spécifiques prévus pour cette sélection. Repos ou observation !")
        return

    for index, row in df_filtre.iterrows():
        emoji = "🥕" if row['Zone'] == "Potager" else "🌸"
        badge = "📚 Source" if row['Type'] == 'Livre' else "➕ Mon Ajout"

        with st.container(border=True):
            c_texte, c_bouton = st.columns([0.70, 0.30], vertical_alignment="center")

            with c_texte:
                st.markdown(f"### {emoji} {row['Action']} : **{row['Plante / Cible']}**")
                st.write(row['Description / Précision'])
                st.caption(f"📍 {row['Zone']} | {row['Quinzaine']} | {badge}")

            with c_bouton:
                afficher_boutons_fiches(row, f"liste_{index}", df_plantes)


def afficher_vue_calendrier(df_filtre, df_plantes):
    if df_filtre.empty:
        st.info("🗓️ Aucune intervention prévue pour cette sélection dans le calendrier par quinzaine.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Interventions", len(df_filtre))
    c2.metric("Potager", int((df_filtre['Zone'] == 'Potager').sum()))
    c3.metric("Jardin", int((df_filtre['Zone'] == 'Jardin').sum()))
    st.caption("Vue mensuelle par quinzaine pour visualiser les actions à anticiper.")

    quinzaines_ordonnees = ["1ère quinzaine", "2ème quinzaine"]
    groupes = {q: [] for q in quinzaines_ordonnees}

    for _, row in df_filtre.iterrows():
        quinzaine = str(row['Quinzaine']).strip() if pd.notna(row['Quinzaine']) else ""
        if quinzaine in groupes:
            groupes[quinzaine].append(row)
        elif quinzaine:
            groupes.setdefault(quinzaine, []).append(row)

    for quinzaine in quinzaines_ordonnees:
        if not groupes[quinzaine]:
            continue

        bg_color = "#ecfdf3" if quinzaine == "1ère quinzaine" else "#fefce8"
        border_color = "#22c55e" if quinzaine == "1ère quinzaine" else "#f59e0b"

        st.markdown(
            f"""
            <div style="background-color:{bg_color}; border:1px solid {border_color}; border-radius:10px; padding:12px 14px; margin-bottom:12px;">
                <div style="font-weight:700; color:#14532d; margin-bottom:8px;">📅 {quinzaine}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, row in enumerate(groupes[quinzaine]):
            emoji = "🥕" if row['Zone'] == "Potager" else "🌸"
            badge = "📚 Source" if row['Type'] == 'Livre' else "➕ Mon Ajout"
            card_bg = "#f0fdf4" if row['Zone'] == "Potager" else "#fff7ed"
            accent_color = "#16a34a" if row['Zone'] == "Potager" else "#ea580c"
            description = str(row['Description / Précision']).strip() if pd.notna(row['Description / Précision']) else ""

            st.markdown(
                f"""
                <div style="background-color:{card_bg}; border-left:4px solid {accent_color}; border-radius:8px; padding:10px 12px; margin-bottom:8px;">
                    <div style="font-weight:700; margin-bottom:4px;">{emoji} {row['Action']} — {row['Plante / Cible']}</div>
                    <div style="margin-bottom:4px;">{description}</div>
                    <div style="font-size:0.9em; color:#475569;">📍 {row['Zone']} · {row['Mois']} · {badge}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            afficher_boutons_fiches(row, f"cal_{quinzaine}_{idx}", df_plantes)
            st.divider()


def afficher_vue_agenda(df_filtre, df_plantes):
    if df_filtre.empty:
        st.info("📆 Aucune intervention prévue pour cette sélection dans l'agenda.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Interventions", len(df_filtre))
    c2.metric("Potager", int((df_filtre['Zone'] == 'Potager').sum()))
    c3.metric("Jardin", int((df_filtre['Zone'] == 'Jardin').sum()))
    st.caption("Vue agenda : visualisez les deux quinzaines du mois côte à côte.")

    quinzaines_ordonnees = ["1ère quinzaine", "2ème quinzaine"]
    groupes = {q: [] for q in quinzaines_ordonnees}

    for _, row in df_filtre.iterrows():
        quinzaine = str(row['Quinzaine']).strip() if pd.notna(row['Quinzaine']) else ""
        if quinzaine in groupes:
            groupes[quinzaine].append(row)
        elif quinzaine:
            groupes.setdefault(quinzaine, []).append(row)

    col_q1, col_q2 = st.columns(2, gap="medium")

    for idx, quinzaine in enumerate(quinzaines_ordonnees):
        col = col_q1 if idx == 0 else col_q2
        with col:
            if not groupes[quinzaine]:
                col.markdown(
                    f"""
                    <div style="background-color:#f3f4f6; border-radius:10px; padding:20px; text-align:center; color:#6b7280;">
                        <div style="font-size:14px;">Aucune intervention</div>
                        <div style="font-size:12px; margin-top:8px;">{quinzaine}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                bg_header = "#dcfce7" if quinzaine == "1ère quinzaine" else "#fef3c7"
                text_header = "#15803d" if quinzaine == "1ère quinzaine" else "#b45309"

                col.markdown(
                    f"""
                    <div style="background-color:{bg_header}; border-radius:8px 8px 0 0; padding:14px; text-align:center; border-bottom:2px solid {'#22c55e' if quinzaine == '1ère quinzaine' else '#f59e0b'};">
                        <div style="font-weight:800; font-size:16px; color:{text_header};">📅 {quinzaine}</div>
                        <div style="font-size:12px; color:{text_header}; margin-top:4px;">({len(groupes[quinzaine])} action{'s' if len(groupes[quinzaine]) > 1 else ''})</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                for idx, row in enumerate(groupes[quinzaine]):
                    emoji = "🥕" if row['Zone'] == "Potager" else "🌸"
                    badge_text = "📚" if row['Type'] == 'Livre' else "✏️"
                    card_bg = "#f0fdf4" if row['Zone'] == "Potager" else "#fff7ed"
                    accent_color = "#22c55e" if row['Zone'] == "Potager" else "#f59e0b"
                    description = str(row['Description / Précision']).strip() if pd.notna(row['Description / Précision']) else ""

                    col.markdown(
                        f"""
                        <div style="background-color:{card_bg}; border-left:3px solid {accent_color}; border-radius:4px; padding:10px; margin-top:8px;">
                            <div style="font-weight:700; font-size:13px; margin-bottom:3px;">{emoji} {row['Action']}</div>
                            <div style="font-size:12px; font-weight:600; margin-bottom:3px; color:#404040;">{row['Plante / Cible']}</div>
                            <div style="font-size:11px; color:#666; margin-bottom:6px; line-height:1.4;">{description}</div>
                            <div style="font-size:10px; color:#888;">🏷️ {row['Zone']} {badge_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    afficher_boutons_fiches(row, f"agenda_{quinzaine}_{idx}", df_plantes)


st.divider()
if mois_choisi:
    st.subheader(
        f"📋 Travaux de {mois_choisi} ({quinzaine_choisie.lower() if quinzaine_choisie != 'Toutes' else 'mois complet'})")

vue_choisie = st.radio(
    "🧭 Affichage :",
    ["Liste", "Calendrier", "Agenda"],
    horizontal=True,
    key="vue_affichage"
)

if vue_choisie == "Agenda":
    afficher_vue_agenda(df_filtre, df_plantes)
elif vue_choisie == "Calendrier":
    afficher_vue_calendrier(df_filtre, df_plantes)
else:
    afficher_vue_liste(df_filtre, df_plantes)

# --- AJOUT DU FOOTER VALIDE ---
with st.bottom():
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 0.8em;'>"
        "© 2026 made with love by CLDE. All rights reserved"
        "</p>", 
        unsafe_allow_html=True
    )