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

    total_etapes = 7
    st.progress(st.session_state.etape_pdc / total_etapes)

    # ---------------------------------------------------------
    # ÉTAPE 1 : INFORMATIONS GÉNÉRALES
    # ---------------------------------------------------------
    if st.session_state.etape_pdc == 1:
        st.subheader("Étape 1/7 : Identification du Producteur")
        
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
        st.subheader("Étape 2/7 : Données de la Parcelle")

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
        st.subheader("Étape 3/7 : Données Socio-démographiques (Fiche 1)")
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
        st.subheader("Étape 4/7 : Description de l'Exploitation (Fiche 2)")

        st.markdown("### 🌾 1. Données sur les cultures")
        st.markdown("**A. Plantation de Cacao**")
        if 'df_cacao' not in st.session_state:
            st.session_state.df_cacao = [
                {"Parcelle": "Parcelle 1", "Superficie (ha)": 1.5, "Année création": 2010, "Précédent cultural": "Forêt", "Origine matériel végétal": "CNRA", "En production (OUI/NON)": "OUI"},
                {"Parcelle": "Parcelle 2", "Superficie (ha)": 2.0, "Année création": 2015, "Précédent cultural": "Jachère", "Origine matériel végétal": "Tout venant", "En production (OUI/NON)": "OUI"}
            ]
        cacao_df = st.data_editor(st.session_state.df_cacao, num_rows="dynamic", key="editor_cacao", use_container_width=True)

        st.markdown("**B. Autres cultures**")
        if 'df_autres_cultures' not in st.session_state:
            st.session_state.df_autres_cultures = [
                {"Culture": "Hévéa", "Superficie (ha)": 1.0, "Année création": 2018, "Précédent cultural": "Jachère", "Origine matériel végétal": "Vulgarisé", "En production (OUI/NON)": "NON"},
                {"Culture": "P. à huile", "Superficie (ha)": 0.5, "Année création": 2020, "Précédent cultural": "Savane", "Origine matériel végétal": "Sélectionné", "En production (OUI/NON)": "NON"}
            ]
        autres_cultures_df = st.data_editor(st.session_state.df_autres_cultures, num_rows="dynamic", key="editor_autres_cultures", use_container_width=True)

        st.markdown("---")
        st.markdown("### 🚜 2. Matériel agricole et équipements")
        if 'df_equipements' not in st.session_state:
            st.session_state.df_equipements = [
                {"Type": "Matériel de traitement", "Désignation": "Pulvérisateur", "Quantité": 1, "Année d'acquisition": 2021, "Coût (FCFA)": 35000, "État": "Bon"}
            ]
        equipements_df = st.data_editor(st.session_state.df_equipements, num_rows="dynamic", key="editor_equipements", use_container_width=True)

        st.markdown("---")
        st.markdown("### 🌳 3. Diagnostic des arbres autres que le cacaoyer")
        if 'df_arbres_ombrage' not in st.session_state:
            st.session_state.df_arbres_ombrage = [
                {"N°": 1, "Nom de l'arbre": "Akpi", "Nombre": 200, "Latitude": 6.020668, "Longitude": -4.3571323, "Statut": "Préservé", "Avantages cacaoyère": "1. Ombrage", "Usage": "4. Bois d'oeuvre", "Action": "A maintenir", "Observations": ""}
            ]
        arbres_ombrage_df = st.data_editor(
            st.session_state.df_arbres_ombrage,
            num_rows="dynamic",
            key="editor_arbres_ombrage",
            column_config={
                "Statut": st.column_config.SelectboxColumn("Statut", options=["Préservé", "Introduit", "Régénéré"]),
                "Avantages cacaoyère": st.column_config.SelectboxColumn("Avantages pour la cacaoyère", options=["1. Ombrage", "2. Fertilité du sol", "3. Protection contre l'érosion", "4. Maintien l'humidité", "5. Lutte contre l'enherbement"]),
                "Usage": st.column_config.SelectboxColumn("Usage", options=["1. Alimentaire", "2. Médicinale", "3. Protection des cacaoyers", "4. Bois d'oeuvre", "5. Bois de chauffage"]),
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
                    "parcelles_cacaoyer": cacao_df, "autres_cultures": autres_cultures_df,
                    "equipements": equipements_df, "arbres_ombrage": arbres_ombrage_df,
                    "terres_disponibles": terres_disponibles, "autre_speculations": autre_speculations
                })
                st.session_state.etape_pdc = 5
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 5 : DENSITÉ ET RENDEMENT (FICHE 3 - PARTIE 1)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 5:
        st.subheader("Étape 5/7 : Densité et Rendement (Fiche 3)")

        st.markdown("### 📐 1. Densité des cacaoyers")
        if 'df_densite_cacao' not in st.session_state:
            st.session_state.df_densite_cacao = [
                {"Carré": "Carré 1", "Nombre cacaoyers": 12, "Nb moyen de tiges/cacaoyer": 1.0},
                {"Carré": "Carré 2", "Nombre cacaoyers": 11, "Nb moyen de tiges/cacaoyer": 1.2},
                {"Carré": "Carré 3", "Nombre cacaoyers": 13, "Nb moyen de tiges/cacaoyer": 1.0},
                {"Carré": "Carré 4", "Nombre cacaoyers": 10, "Nb moyen de tiges/cacaoyer": 1.1}
            ]

        densite_df = st.data_editor(st.session_state.df_densite_cacao, num_rows="dynamic", key="editor_densite", use_container_width=True)

        if len(densite_df) > 0:
            df_temp = pd.DataFrame(densite_df)
            moyenne_arbres_carre = df_temp["Nombre cacaoyers"].mean() if "Nombre cacaoyers" in df_temp else 0
            densite_estimee = moyenne_arbres_carre * 100
            st.success(f"📊 **Densité estimée :** `{densite_estimee:.0f} cacaoyers / ha`")
        else:
            densite_estimee = 0

        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 4
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "donnees_densite": densite_df, "densite_calculee_ha": densite_estimee,
                    
                })
                st.session_state.etape_pdc = 6
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 6 : ÉTAT SANITAIRE, SOL, RÉCOLTE & ENGRAIS (FICHE 3 - PARTIE 2)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 6:
        st.subheader("Étape 6/7 : État Sanitaire, Sol, Récolte & Engrais (Fiche 3)")

        # 6.1 ÉTAT VÉGÉTATIF ET SANITAIRE DES CACAOYERS
        st.markdown("### 🐛 1. État végétatif et sanitaire")
        if 'df_sante_cacao' not in st.session_state:
            st.session_state.df_sante_cacao = [
                {"Maladies / Ravageurs": "Attaques de mirides", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "Présence de gourmands", "Valeur": "1. Aucun", "Observations P.": ""},
                {"Maladies / Ravageurs": "Attaques de Pourriture Brune", "Sévérité": "2. Faible", "Observations": "", "Paramètres": "Présence de cabosses momifiées", "Valeur": "2. Faible", "Observations P.": ""},
                {"Maladies / Ravageurs": "Présence de plantes épiphytes", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "Présence de loranthus", "Valeur": "1. Aucun", "Observations P.": ""},
                {"Maladies / Ravageurs": "Attaque Foreurs", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "Enherbedement", "Valeur": "3. moyen", "Observations P.": ""},
                {"Maladies / Ravageurs": "Attaque CSSVD", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "", "Valeur": "", "Observations P.": ""}
            ]

        sante_df = st.data_editor(
            st.session_state.df_sante_cacao,
            num_rows="dynamic",
            key="editor_sante",
            column_config={
                "Sévérité": st.column_config.SelectboxColumn("Sévérité", options=["1. Aucun", "2. Faible", "3. Moyen", "4. Fort"]),
                "Valeur": st.column_config.SelectboxColumn("Valeur", options=["1. Aucun", "2. Faible", "3. moyen", "4. Fort"])
            },
            use_container_width=True
        )

        st.markdown("---")

        # 6.2 CARACTÉRISTIQUES PHYSIQUES DU SOL
        st.markdown("### 🏔️ 2. État et caractéristiques du sol")
        toposequence = st.selectbox("Positionnement dans la toposéquence", ["Plateau", "Haut de versant", "Mi-versant", "Bas de versant", "Bas-fond"])

        if 'df_sol_caract' not in st.session_state:
            st.session_state.df_sol_caract = [
                {"Éléments d'observation (A)": "Couvert végétal", "Valeur A": "2. moyen", "Obs A": "", "Éléments d'observation (B)": "Existence de zones érodées", "Valeur B": "2. Non", "Obs B": "Ravinements..."},
                {"Éléments d'observation (A)": "Présence de Matière organique", "Valeur A": "1. beaucoup", "Obs A": "", "Éléments d'observation (B)": "Existence de zones à risque d'érosion", "Valeur B": "2. Non", "Obs B": "Pente..."},
                {"Éléments d'observation (A)": "Profondeur", "Valeur A": "2. moyen", "Obs A": "", "Éléments d'observation (B)": "", "Valeur B": "", "Obs B": ""},
                {"Éléments d'observation (A)": "Texture", "Valeur A": "2. moyen", "Obs A": "", "Éléments d'observation (B)": "", "Valeur B": "", "Obs B": ""}
            ]

        sol_df = st.data_editor(
            st.session_state.df_sol_caract,
            num_rows="dynamic",
            key="editor_sol",
            column_config={
                "Valeur A": st.column_config.SelectboxColumn("Valeur (A)", options=["1. beaucoup", "2. moyen", "3. Faible"]),
                "Valeur B": st.column_config.SelectboxColumn("Valeur (B)", options=["1. Oui", "2. Non"])
            },
            use_container_width=True
        )

        st.markdown("---")

        # 6.3 PRATIQUES DE RÉCOLTE ET POST-RÉCOLTE
        st.markdown("### 🧺 3. Pratiques de récolte et post-récolte")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            freq_recolte = st.number_input("Fréquence des récoltes (jours entre 2 récoltes)", min_value=1, max_value=60, value=14)
            temps_ecabossage = st.number_input("Temps entre récolte et écabossage (jours)", min_value=0, max_value=15, value=2)
            duree_fermentation = st.number_input("Durée de la fermentation (jours)", min_value=1, max_value=10, value=6)
        with col_p2:
            mode_fermentation = st.selectbox("Mode de fermentation", ["1. Bâche en plastique", "2. Feuilles de bananier", "3. Bac de fermentation", "4. Autre (à préciser)"])
            methode_sechage = st.selectbox("Méthodes de séchage", ["1. Sur goudron", "2. Sur aire cimentée", "3. Sur bâche en plastique à terre", "4. Sur claie", "5. Autre (à préciser)"])

        st.markdown("---")

                # 6.4 UTILISATION DES ENGRAIS ET AMENDEMENTS
        st.markdown("### 🧪 4. Utilisation des engrais / amendements")
        if 'df_engrais' not in st.session_state:
            st.session_state.df_engrais = [
                {
                    "Type d'engrais": "Minéraux",
                    "Nom commercial / Formule": "NPK 0-23-19",
                    "Quantité/an": "200 kg",
                    "Période d'apport": "Mai",
                    "Mode d'apport": "Au sol",
                    "Applicateur": "1. Producteur"
                }
            ]

        engrais_df = st.data_editor(
            st.session_state.df_engrais,
            num_rows="dynamic",
            key="editor_engrais",
            column_config={
                "Type d'engrais": st.column_config.SelectboxColumn("Type d'engrais", options=["Minéraux", "Organiques", "Autres"]),
                "Mode d'apport": st.column_config.SelectboxColumn("Mode d'apport", options=["Foliaire", "Au sol"]),
                "Applicateur": st.column_config.SelectboxColumn("Applicateur", options=["1. Producteur", "2. Applicateur"])
            },
            use_container_width=True
        )

        st.markdown("---")

        # 6.5 UTILISATION DES PRODUITS PHYTOSANITAIRES
        st.markdown("### 🛡️ 5. Produits phytosanitaires utilisés")
        if 'df_phyto' not in st.session_state:
            st.session_state.df_phyto = [
                {
                    "Type de produits": "Fongicide",
                    "Nom commercial / Formule": "Ridomil Gold",
                    "Quantité / traitement": "50g/15L",
                    "Période de traitement": "Juin-Juillet",
                    "Mode d'apport": "Pulvérisateur",
                    "Applicateur": "2. Applicateur"
                }
            ]

        phyto_df = st.data_editor(
            st.session_state.df_phyto,
            num_rows="dynamic",
            key="editor_phyto",
            column_config={
                "Type de produits": st.column_config.SelectboxColumn("Type de produits", options=["Insecticide", "Fongicide", "Herbicide", "Nematicide"]),
                "Mode d'apport": st.column_config.SelectboxColumn("Mode d'apport", options=["Atomiseur", "Pulvérisateur"]),
                "Applicateur": st.column_config.SelectboxColumn("Applicateur", options=["1. Producteur", "2. Applicateur"])
            },
            use_container_width=True
        )

        st.markdown("---")

        # 6.6 GESTION DES EMBALLAGES VIDES
        st.markdown("### 🗑️ 6. Gestion des emballages vides")
        gestion_emballages = st.text_area(
            "Que faites-vous des emballages après traitement/application ?",
            placeholder="Exemple : Rincés 3 fois, percés et ramassés par le programme de collecte de la coopérative...",
            height=100
        )

        # NAVIGATION ENTRE ÉTAPES
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 5
                st.rerun()
        with col2:
            if st.button("Suivant (Partie D) ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "sante_cacaoyere": sante_df,
                    "toposequence": toposequence,
                    "caracteristiques_sol": sol_df,
                    "frequence_recolte_jours": freq_recolte,
                    "temps_ecabossage_jours": temps_ecabossage,
                    "duree_fermentation_jours": duree_fermentation,
                    "mode_fermentation": mode_fermentation,
                    "methode_sechage": methode_sechage,
                    "utilisation_engrais": engrais_df,
                    "produits_phytosanitaires": phyto_df,
                    "gestion_emballages": gestion_emballages
                })
                st.session_state.etape_pdc = 7
                st.rerun()


        # ---------------------------------------------------------
    # ÉTAPE 7 : PARTIE D - DONNÉES SOCIO-ÉCONOMIQUES (FICHE 4)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 7:
        st.subheader("Étape 7/8 : Données Socio-économiques (Fiche 4)")

        # 1. COMPTE D'ÉPARGNE ET FINANCEMENT
        st.markdown("### 🏦 1. Compte d'épargne et Financement")
        if 'df_financement' not in st.session_state:
            st.session_state.df_financement = [
                {"Service": "Mobile Money", "Compte d'épargne (Oui/Non)": "Oui", "Demande de crédit (Oui/Non)": "Non", "Crédit obtenu (Oui/Non)": "Non", "Montant (FCFA)": 0},
                {"Service": "Microfinance", "Compte d'épargne (Oui/Non)": "Non", "Demande de crédit (Oui/Non)": "Non", "Crédit obtenu (Oui/Non)": "Non", "Montant (FCFA)": 0},
                {"Service": "Banque", "Compte d'épargne (Oui/Non)": "Non", "Demande de crédit (Oui/Non)": "Non", "Crédit obtenu (Oui/Non)": "Non", "Montant (FCFA)": 0}
            ]

        financement_df = st.data_editor(
            st.session_state.df_financement,
            num_rows="dynamic",
            key="editor_financement",
            column_config={
                "Compte d'épargne (Oui/Non)": st.column_config.SelectboxColumn("Compte d'épargne", options=["Oui", "Non"]),
                "Demande de crédit (Oui/Non)": st.column_config.SelectboxColumn("Demande de crédit", options=["Oui", "Non"]),
                "Crédit obtenu (Oui/Non)": st.column_config.SelectboxColumn("Crédit obtenu", options=["Oui", "Non"])
            },
            use_container_width=True
        )

        st.markdown("---")

        # 2. PRODUCTION DE CACAO DES 3 DERNIÈRES ANNÉES
        st.markdown("### 📦 2. Production de cacao des trois (3) dernières années")
        if 'df_prod_historique' not in st.session_state:
            st.session_state.df_prod_historique = [
                {"Campagne": "Année N-1", "Production (kg)": 0, "Prix moyen (FCFA/kg)": 1500},
                {"Campagne": "Année N-2", "Production (kg)": 0, "Prix moyen (FCFA/kg)": 1000},
                {"Campagne": "Année N-3", "Production (kg)": 0, "Prix moyen (FCFA/kg)": 900}
            ]

        prod_historique_df = st.data_editor(
            st.session_state.df_prod_historique,
            num_rows="dynamic",
            key="editor_prod_historique",
            use_container_width=True
        )

        st.markdown("---")

        # 3. SOURCES DE REVENUS AUTRES QUE LE CACAO
        st.markdown("### 💰 3. Sources de revenus autres que le cacao")
        if 'df_autres_revenus' not in st.session_state:
            st.session_state.df_autres_revenus = [
                {"Source de revenu / Activité": "Vente de vivriers", "Montant estimé/an (FCFA)": 0, "Observations": ""},
                {"Source de revenu / Activité": "Elevage", "Montant estimé/an (FCFA)": 0, "Observations": ""}
            ]

        autres_revenus_df = st.data_editor(
            st.session_state.df_autres_revenus,
            num_rows="dynamic",
            key="editor_autres_revenus",
            use_container_width=True
        )

        st.markdown("---")

        # 4. DÉPENSES COURANTES DU FOYER
        st.markdown("### 🛒 4. Dépenses courantes du foyer")
        if 'df_depenses' not in st.session_state:
            st.session_state.df_depenses = [
                {"Dépenses": "Scolarité", "Périodicité": "Année", "Montant moyen (FCFA)": 0},
                {"Dépenses": "Nourriture", "Périodicité": "Mois", "Montant moyen (FCFA)": 0},
                {"Dépenses": "Santé", "Périodicité": "Année", "Montant moyen (FCFA)": 0},
                {"Dépenses": "Électricité", "Périodicité": "2 mois", "Montant moyen (FCFA)": 0},
                {"Dépenses": "Eau courante", "Périodicité": "Mois", "Montant moyen (FCFA)": 0},
                {"Dépenses": "Charges sociales (Funérailles, fêtes...)", "Périodicité": "Année", "Montant moyen (FCFA)": 0}
            ]

        depenses_df = st.data_editor(
            st.session_state.df_depenses,
            num_rows="dynamic",
            key="editor_depenses",
            use_container_width=True
        )

        st.markdown("---")

        # 5. COÛT DE LA MAIN D'ŒUVRE
        st.markdown("### 👥 5. Coût et gestion de la main d'œuvre")
        if 'df_main_oeuvre' not in st.session_state:
            st.session_state.df_main_oeuvre = [
                {"Travailleur": "Travailleur 1", "Statut": "MO permanente", "Sexe": "M", "Coût annuel (FCFA)": 0, "Temps de travail / an (jours)": 0},
                {"Travailleur": "Groupe de travail (Entraide)", "Statut": "Non rémunérée (familiale)", "Sexe": "M", "Coût annuel (FCFA)": 0, "Temps de travail / an (jours)": 0}
            ]

        main_oeuvre_df = st.data_editor(
            st.session_state.df_main_oeuvre,
            num_rows="dynamic",
            key="editor_main_oeuvre",
            column_config={
                "Statut": st.column_config.SelectboxColumn("Statut de la main d'œuvre", options=["MO permanente", "MO occasionnelle", "Non rémunérée (familiale)"]),
                "Sexe": st.column_config.SelectboxColumn("Sexe", options=["M", "F"])
            },
            use_container_width=True
        )

        # NAVIGATION ENTRE ÉTAPES
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 6
                st.rerun()
        with col2:
            if st.button("Suivant (Synthèse) ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "financement": financement_df,
                    "prod_historique": prod_historique_df,
                    "autres_revenus": autres_revenus_df,
                    "depenses_foyer": depenses_df,
                    "main_oeuvre": main_oeuvre_df
                })
                st.session_state.etape_pdc = 8
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 8 : SYNTHÈSE TOTALE ET ENREGISTREMENT
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 8:
        st.subheader("Étape 8/8 : Validation et Enregistrement Global du PDC")
        st.info("Résumé de toutes les informations collectées durant les 8 étapes du formulaire PDC.")

        st.json(st.session_state.reponses_pdc)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 7
                st.rerun()
        with col2:
            if st.button("💾 Enregistrer le PDC", type="primary", use_container_width=True):
                st.balloons()
                st.success("🎉 Le Diagnostic et Plan de Développement de la Cacaoyère (PDC) a été totalement enregistré !")
                st.session_state.etape_pdc = 1
                st.session_state.reponses_pdc = {}

