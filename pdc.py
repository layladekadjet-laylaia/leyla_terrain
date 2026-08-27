import streamlit as st
import os
import time
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
import urllib.parse
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from PIL import Image
from shapely.geometry import Point, Polygon
from fpdf import FPDF
import datetime

def afficher():
    st.title("📋 PDC - Diagnostic & Plan de Développement")

    # Initialisation de l'étape courante
    if 'etape_pdc' not in st.session_state:
        st.session_state.etape_pdc = 1

    # Dictionnaire pour stocker les réponses
    if 'reponses_pdc' not in st.session_state:
        st.session_state.reponses_pdc = {}

    total_etapes = 6
    st.progress(st.session_state.etape_pdc / total_etapes)

    # ---------------------------------------------------------
    # ÉTAPE 1 : INFORMATIONS GÉNÉRALES
    # ---------------------------------------------------------
    if st.session_state.etape_pdc == 1:
        st.subheader("Étape 1/6 : Identification du Producteur")
        
        zone = st.selectbox("Zone", ["A", "B", "C", "D", "E"], key="zone_input")
        ville = st.selectbox("Ville", ["Lakota", "Sassandra", "Fresco", "Gbagbam", "Gueyo"])
        nom_producteur = st.text_input("Nom et Prénoms du Producteur")
        contact = st.text_input("Contact")
        cooperative = st.text_input("Coopérative")

        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "zone": zone, "ville": ville, "nom": nom_producteur,
                    "contact": contact, "cooperative": cooperative
                })
                st.session_state.etape_pdc = 2
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 2 : CARACTÉRISTIQUES DE LA PARCELLE
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 2:
        st.subheader("Étape 2/6 : Données de la Parcelle")

        superficie = st.number_input("Superficie de la plantation (ha)", min_value=0.1, step=0.5)
        annee_creation = st.number_input("Année de création", min_value=1950, max_value=2026, value=2010)
        lat = st.number_input("Latitude GPS", format="%.6f", value=5.7881)
        lon = st.number_input("Longitude GPS", format="%.6f", value=-6.5918)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 1
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "superficie": superficie, "annee_creation": annee_creation,
                    "lat": lat, "lon": lon
                })
                st.session_state.etape_pdc = 3
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 3 : DONNÉES SOCIO-DÉMOGRAPHIQUES (FICHE 1)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 3:
        st.subheader("Étape 3/6 : Données Socio-démographiques (Fiche 1)")
        st.info("Informations sur les membres du ménage et les actifs familiaux/travailleurs")

        nom_membre = st.text_input("Nom et Prénoms du membre du ménage")
        statut_famille = st.selectbox("Statut/Famille (Lien de parenté)", ["1. Chef de ménage", "2. Conjoint", "3. Enfant", "4. Autre"])
        statut_plantation = st.selectbox("Statut/Plantation", ["1. Aucun", "2. Propriétaire", "3. Gérant", "4. MO permanent", "5. MO Temporaire"])
        statut_scolaire = st.selectbox("Statut Scolaire", ["1. Scolarisé", "2. Déscolarisé"])
        contact_membre = st.text_input("Contact (Téléphone)")
        annee_naissance = st.number_input("Année de naissance", min_value=1930, max_value=2026, value=1990)
        sexe = st.radio("Sexe", ["M", "F"], horizontal=True)
        niveau_instruction = st.selectbox("Niveau d'instruction", ["1. Aucun", "2. Préscolaire", "3. Primaire", "4. Secondaire", "5. Supérieur", "6. Autres"])
        categorie_ethnique = st.selectbox("Catégorie ethnique", ["1. Autochtone", "2. Allochtone", "3. Allogène"])

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 2
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "nom_membre": nom_membre, "statut_famille": statut_famille,
                    "statut_plantation": statut_plantation, "statut_scolaire": statut_scolaire,
                    "contact_membre": contact_membre, "annee_naissance": annee_naissance,
                    "sexe": sexe, "niveau_instruction": niveau_instruction,
                    "categorie_ethnique": categorie_ethnique
                })
                st.session_state.etape_pdc = 4
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 4 : DESCRIPTION DE L'EXPLOITATION (FICHE 2)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 4:
        st.subheader("Étape 4/6 : Description de l'Exploitation (Fiche 2)")

        # 4.1 DONNÉES SUR LES CULTURES
        st.markdown("### 🌾 1. Données sur les cultures")
        
        st.markdown("**A. Plantation de Cacao**")
        if 'df_cacao' not in st.session_state:
            st.session_state.df_cacao = [
                {"Parcelle": "Parcelle 1", "Superficie (ha)": 1.5, "Année création": 2010, "Précédent cultural": "Forêt", "Origine matériel végétal": "CNRA", "En production (OUI/NON)": "OUI"},
                {"Parcelle": "Parcelle 2", "Superficie (ha)": 2.0, "Année création": 2015, "Précédent cultural": "Jachère", "Origine matériel végétal": "Tout venant", "En production (OUI/NON)": "OUI"}
            ]
        
        cacao_df = st.data_editor(
            st.session_state.df_cacao,
            num_rows="dynamic",
            key="editor_cacao",
            use_container_width=True
        )

        st.markdown("**B. Autres cultures**")
        if 'df_autres_cultures' not in st.session_state:
            st.session_state.df_autres_cultures = [
                {"Culture": "Hévéa", "Superficie (ha)": 1.0, "Année création": 2018, "Précédent cultural": "Jachère", "Origine matériel végétal": "Vulgarisé", "En production (OUI/NON)": "NON"},
                {"Culture": "P. à huile", "Superficie (ha)": 0.5, "Année création": 2020, "Précédent cultural": "Savane", "Origine matériel végétal": "Sélectionné", "En production (OUI/NON)": "NON"},
                {"Culture": "Vivrier", "Superficie (ha)": 0.25, "Année création": 2025, "Précédent cultural": "Friche", "Origine matériel végétal": "Local", "En production (OUI/NON)": "OUI"}
            ]

        autres_cultures_df = st.data_editor(
            st.session_state.df_autres_cultures,
            num_rows="dynamic",
            key="editor_autres_cultures",
            use_container_width=True
        )

        st.markdown("---")

        # 4.2 MATÉRIEL AGRICOLE ET ÉQUIPEMENTS
        st.markdown("### 🚜 2. Matériel agricole et équipements")
        if 'df_equipements' not in st.session_state:
            st.session_state.df_equipements = [
                {"Type": "Matériel de traitement", "Désignation": "Pulvérisateur", "Quantité": 1, "Année d'acquisition": 2021, "Coût (FCFA)": 35000, "État": "Bon"},
                {"Type": "Matériel de traitement", "Désignation": "Atomiseur", "Quantité": 1, "Année d'acquisition": 2023, "Coût (FCFA)": 150000, "État": "Acceptable"},
                {"Type": "Matériel de transport", "Désignation": "Charette / Tricycle", "Quantité": 1, "Année d'acquisition": 2022, "Coût (FCFA)": 450000, "État": "Bon"}
            ]

        equipements_df = st.data_editor(
            st.session_state.df_equipements,
            num_rows="dynamic",
            key="editor_equipements",
            use_container_width=True
        )

        st.markdown("---")

        # 4.3 DIAGNOSTIC DES ARBRES AUTRES QUE LE CACAOYER
        st.markdown("### 🌳 3. Diagnostic des arbres autres que le cacaoyer")
        
        if 'df_arbres_ombrage' not in st.session_state:
            st.session_state.df_arbres_ombrage = [
                {"N°": 1, "Nom de l'arbre": "Akpi", "Nombre": 200, "Latitude": 6.020668, "Longitude": -4.3571323, "Statut": "Préservé", "Avantages cacaoyère": "1. Ombrage", "Usage": "4. Bois d'oeuvre", "Action": "A maintenir", "Observations": ""},
                {"N°": 2, "Nom de l'arbre": "Fraqué", "Nombre": 70, "Latitude": 6.020664, "Longitude": -4.3569498, "Statut": "Préservé", "Avantages cacaoyère": "2. Fertilité du sol", "Usage": "4. Bois d'oeuvre", "Action": "A éliminer", "Observations": "Situé à 1,5 m d'un autre"},
                {"N°": 3, "Nom de l'arbre": "Fromager", "Nombre": 212, "Latitude": 6.020614, "Longitude": -4.3569029, "Statut": "Préservé", "Avantages cacaoyère": "4. Maintien l'humidité", "Usage": "4. Bois d'oeuvre", "Action": "A maintenir", "Observations": ""}
            ]

        arbres_ombrage_df = st.data_editor(
            st.session_state.df_arbres_ombrage,
            num_rows="dynamic",
            key="editor_arbres_ombrage",
            column_config={
                "Statut": st.column_config.SelectboxColumn("Statut", options=["Préservé", "Introduit", "Régénéré"]),
                "Avantages cacaoyère": st.column_config.SelectboxColumn("Avantages pour la cacaoyère", options=[
                    "1. Ombrage", "2. Fertilité du sol", "3. Protection contre l'érosion", "4. Maintien l'humidité", "5. Lutte contre l'enherbement"
                ]),
                "Usage": st.column_config.SelectboxColumn("Usage", options=[
                    "1. Alimentaire", "2. Médicinale", "3. Protection des cacaoyers", "4. Bois d'oeuvre", "5. Bois de chauffage"
                ]),
                "Action": st.column_config.SelectboxColumn("Action recommandée", options=["A maintenir", "A éliminer", "A élaguer"])
            },
            use_container_width=True
        )

        st.markdown("---")
        terres_disponibles = st.number_input("Terres disponibles non exploitées (ha)", min_value=0.0, step=0.5, value=0.0)
        autre_speculations = st.text_input("Autres spéculations (Élevage, production halieutique, etc.)")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 3
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "parcelles_cacaoyer": cacao_df,
                    "autres_cultures": autres_cultures_df,
                    "equipements": equipements_df,
                    "arbres_ombrage": arbres_ombrage_df,
                    "terres_disponibles": terres_disponibles,
                    "autre_speculations": autre_speculations
                })
                st.session_state.etape_pdc = 5
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 5 : DONNÉES AGRONOMIQUES (FICHE 3)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 5:
        st.subheader("Étape 5/6 : C - Données Agronomiques (Fiche 3)")

        # 5.1 DENSITÉ DES CACAOYERS
        st.markdown("### 📐 1. Densité des cacaoyers")
        st.info(
            " Méthodologie :\n"
            "- Poser des carrés de densité de 10 m × 10 m sur la parcelle.\n"
            "- Choisir les carrés par la méthode des diagonales.\n"
            "- Dans chaque carré, compter les arbres productifs et noter le nombre de tiges par cacaoyer.\n"
            "- Multiplier le nombre moyen d'arbres par carré par 100 pour obtenir la densité moyenne par hectare."
        )

        if 'df_densite_cacao' not in st.session_state:
            st.session_state.df_densite_cacao = [
                {"Carré": "Carré 1", "Nombre cacaoyers": 12, "Nb moyen de tiges/cacaoyer": 1.0},
                {"Carré": "Carré 2", "Nombre cacaoyers": 11, "Nb moyen de tiges/cacaoyer": 1.2},
                {"Carré": "Carré 3", "Nombre cacaoyers": 13, "Nb moyen de tiges/cacaoyer": 1.0},
                {"Carré": "Carré 4", "Nombre cacaoyers": 10, "Nb moyen de tiges/cacaoyer": 1.1}
            ]

        densite_df = st.data_editor(
            st.session_state.df_densite_cacao,
            num_rows="dynamic",
            key="editor_densite",
            use_container_width=True
        )

        # Calcul automatique de la densité
        if len(densite_df) > 0:
            df_temp = pd.DataFrame(densite_df)
            moyenne_arbres_carre = df_temp["Nombre cacaoyers"].mean() if "Nombre cacaoyers" in df_temp else 0
            densite_estimee = moyenne_arbres_carre * 100
            st.success(f"📊 **Densité estimée :** `{densite_estimee:.0f} cacaoyers / ha` (Moyenne par carré de 100m² : `{moyenne_arbres_carre:.2f}`)")
        else:
            densite_estimee = 0

        st.markdown("---")

        

        # 5.3 ARBRES DÉGRADÉS ET NON PRODUCTIFS
        st.markdown("### ⚠️ 3. Critères d'identification des arbres dégradés")
        st.warning(
            "Un arbre est considéré comme dégradé et non productif s'il présente au moins l'une des caractéristiques suivantes :\n"
            "1. La frondaison est ouverte et si dégradée qu'aucune action technique ne peut permettre de la corriger ;\n"
            "2. L'attaque de loranthus (plantes parasites) est si forte qu'aucune taille ne permet de redonner de la vigueur aux arbres ;\n"
            "3. Le tronc est si dégradé que l'arbre n'a plus la possibilité de porter des cabosses ;\n"
            "4. Les arbres chétifs ne pouvant plus produire de cabosses."
        )

        toux_degradation = st.slider("Pourcentage estimé d'arbres dégradés sur la parcelle (%)", min_value=0, max_value=100, value=15)

        # NAVIGATION ENTRE ÉTAPES
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 4
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "donnees_densite": densite_df,
                    "densite_calculee_ha": densite_estimee,
                    
                    "taux_arbres_degrades_pct": toux_degradation
                })
                st.session_state.etape_pdc = 6
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 6 : SYNTHÈSE ET ENREGISTREMENT
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 6:
        st.subheader("Étape 6/6 : Validation et Enregistrement du Diagnostic")
        
        st.json(st.session_state.reponses_pdc)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 5
                st.rerun()
        with col2:
            if st.button("💾 Enregistrer", type="primary", use_container_width=True):
                st.success("Données du diagnostic PDC enregistrées avec succès !")
                st.session_state.etape_pdc = 1
                st.session_state.reponses_pdc = {}
