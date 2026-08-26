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

    total_etapes = 5
    st.progress(st.session_state.etape_pdc / total_etapes)

    # ---------------------------------------------------------
    # ÉTAPE 1 : INFORMATIONS GÉNÉRALES
    # ---------------------------------------------------------
    if st.session_state.etape_pdc == 1:
        st.subheader("Étape 1/5 : Identification du Producteur")
        
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
        st.subheader("Étape 2/5 : Données de la Parcelle")

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
        st.subheader("Étape 3/5 : Données Socio-démographiques (Fiche 1)")
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
        st.subheader("Étape 4/5 : Description de l'Exploitation (Fiche 2)")

        # 4.1 DONNÉES SUR LES CULTURES (Cacao & Autres Cultures N)
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
        st.info("Recensement et diagnostic des arbres d'ombrage et essences associées dans la cacaoyère.")

        if 'df_arbres_ombrage' not in st.session_state:
            st.session_state.df_arbres_ombrage = [
                {
                    "N°": 1,
                    "Nom de l'arbre": "Akpi",
                    "Nombre": 200,
                    "Latitude": 6.020668,
                    "Longitude": -4.3571323,
                    "Statut": "Préservé",
                    "Avantages cacaoyère": "Ombrage",
                    "Usage": "Bois d'oeuvre",
                    "Action": "A maintenir",
                    "Observations": ""
                },
                {
                    "N°": 2,
                    "Nom de l'arbre": "Fraqué",
                    "Nombre": 70,
                    "Latitude": 6.020664,
                    "Longitude": -4.3569498,
                    "Statut": "Préservé",
                    "Avantages cacaoyère": "Fertilité du sol",
                    "Usage": "Bois d'oeuvre",
                    "Action": "A éliminer",
                    "Observations": "Situé à 1,5 m d'un autre"
                },
                {
                    "N°": 3,
                    "Nom de l'arbre": "Fromager",
                    "Nombre": 212,
                    "Latitude": 6.020614,
                    "Longitude": -4.3569029,
                    "Statut": "Préservé",
                    "Avantages cacaoyère": "Maintien l'humidité",
                    "Usage": "Bois d'oeuvre",
                    "Action": "A maintenir",
                    "Observations": ""
                }
            ]

        arbres_ombrage_df = st.data_editor(
            st.session_state.df_arbres_ombrage,
            num_rows="dynamic",
            key="editor_arbres_ombrage",
            column_config={
                "Statut": st.column_config.SelectboxColumn("Statut", options=["Préservé", "Introduit", "Régénéré"]),
                "Avantages cacaoyère": st.column_config.SelectboxColumn("Avantages pour la cacaoyère", options=[
                    "1. Ombrage",
                    "2. Fertilité du sol",
                    "3. Protection contre l'érosion",
                    "4. Maintien l'humidité",
                    "5. Lutte contre l'enherbement"
                ]),
                "Usage": st.column_config.SelectboxColumn("Usage", options=[
                    "1. Alimentaire",
                    "2. Médicinale",
                    "3. Protection des cacaoyers",
                    "4. Bois d'oeuvre",
                    "5. Bois de chauffage"
                ]),
                "Action": st.column_config.SelectboxColumn("Action recommandée", options=["A maintenir", "A éliminer", "A élaguer"])
            },
            use_container_width=True
        )

        st.markdown("---")
        terres_disponibles = st.number_input("Terres disponibles non exploitées (ha)", min_value=0.0, step=0.5, value=0.0)
        autre_speculations = st.text_input("Autres spéculations (Élevage, production halieutique, etc.)")

        # NAVIGATION ENTRE ÉTAPES
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
    # ÉTAPE 5 : SYNTHÈSE ET ENREGISTREMENT
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 5:
        st.subheader("Étape 5/5 : Validation des Données")
        
        st.json(st.session_state.reponses_pdc)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 4
                st.rerun()
        with col2:
            if st.button("💾 Enregistrer", type="primary", use_container_width=True):
                st.success("Données enregistrées avec succès !")
                st.session_state.etape_pdc = 1
                st.session_state.reponses_pdc = {}
