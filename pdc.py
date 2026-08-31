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
from generate_croquis import generer_croquis_parcelle
import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def effectuer_diagnostic_exhaustif_json(data):
    score = 100
    alertes_critiques = []
    avertissements = []
    points_forts = []

    # =========================================================
    # 1. IDENTIFICATION, MÉNAGE & LOCALISATION (5 critères)
    # =========================================================
    # Critère 1 : Zone géographique
    zone = data.get("zone", "")
    if zone:
        points_forts.append(f"Zone d'intervention identifiée : Zone {zone}.")
    else:
        avertissements.append("Zone géographique non spécifiée.")
        score -= 2

    # Critère 2 : Ville / Localité
    ville = data.get("ville", "")
    if ville:
        points_forts.append(f"Localisation renseignée : {ville}.")
    else:
        avertissements.append("Localité/Ville non renseignée.")
        score -= 2

    # Critère 3 : Coordonnées GPS
    lat = data.get("lat", 0)
    lon = data.get("lon", 0)
    if lat != 0 and lon != 0:
        points_forts.append(f"Géolocalisation valide ({lat}, {lon}).")
    else:
        avertissements.append("Coordonnées GPS absentes ou nulles.")
        score -= 3

    # Critère 4 : Statut du membre & Ménage
    statut_fam = data.get("statut_famille", "")
    annee_naiss = data.get("annee_naissance", 0)
    if statut_fam and annee_naiss > 0:
        points_forts.append(f"Profil membre renseigné ({statut_fam}, Né(e) en {annee_naiss}).")
    else:
        avertissements.append("Profil du membre/ménage incomplet.")
        score -= 2

    # Critère 5 : Niveau d'instruction & Catégorie
    niveau_inst = data.get("niveau_instruction", "")
    if niveau_inst:
        points_forts.append(f"Niveau d'instruction caractérisé : {niveau_inst}.")
    else:
        avertissements.append("Niveau d'instruction non renseigné.")
        score -= 1


    # =========================================================
    # 2. STRUCTURE FONCIÈRE & DIVERSIFICATION (4 critères)
    # =========================================================
    # Critère 6 : Parcelles cacaoyères
    parcelles = data.get("parcelles_cacaoyer", [])
    superficie_totale = sum([p.get("Superficie (ha)", 0) for p in parcelles])
    if superficie_totale > 0:
        points_forts.append(f"Superficie cacaoyère caractérisée : {superficie_totale} ha sur {len(parcelles)} parcelle(s).")
    else:
        alertes_critiques.append("Superficie cacaoyère totale nulle ou non renseignée.")
        score -= 15

    # Critère 7 : Historique cultural & Matériel végétal
    parcelles_sans_origen = [p for p in parcelles if not p.get("Origine matériel végétal") or p.get("Origine matériel végétal") == "Tout venant"]
    if parcelles_sans_origen:
        avertissements.append(f"{len(parcelles_sans_origen)} parcelle(s) avec matériel végétal 'Tout venant' ou non certifié.")
        score -= 3

    # Critère 8 : Diversification agricole (Autres cultures)
    autres_cultures = data.get("autres_cultures", [])
    if len(autres_cultures) > 0:
        points_forts.append(f"Diversification agricole effective : {len(autres_cultures)} autre(s) culture(s) déclarée(s).")
    else:
        avertissements.append("Aucune culture de diversification enregistrée (Mono-culture cacaoyère).")

    # Critère 9 : Réserve foncière disponible
    terres_disp = data.get("terres_disponibles", 0)
    if terres_disp > 0:
        points_forts.append(f"Réserve foncière disponible pour extension : {terres_disp} ha.")


    # =========================================================
    # 3. DENSITÉ & AGROFORESTERIE (3 critères)
    # =========================================================
    # Critère 10 : Relevé des carrés de densité
    donnees_densite = data.get("donnees_densite", [])
    if len(donnees_densite) >= 4:
        points_forts.append(f"Comptage de densité conforme ({len(donnees_densite)} carrés renseignés).")
    else:
        avertissements.append("Comptage de densité partiel (moins de 4 carrés).")
        score -= 3

    # Critère 11 : Densité calculée à l'hectare
    densite = data.get("densite_calculee_ha", 0)
    if 1100 <= densite <= 1400:
        points_forts.append(f"Densité conforme aux normes agronomiques ({densite} pieds/ha).")
    elif 0 < densite < 1100:
        avertissements.append(f"Sous-densité détectée ({densite} pieds/ha). Risque de sous-rendement.")
        score -= 5
    elif densite > 1400:
        avertissements.append(f"Sur-densité détectée ({densite} pieds/ha). Risque d'étiolement et compétition.")
        score -= 5
    else:
        alertes_critiques.append("Densité globale nulle ou invalide.")
        score -= 10

    # Critère 12 : Arbres d'ombrage & Agroforesterie
    arbres = data.get("arbres_ombrage", [])
    total_arbres = sum([a.get("Nombre", 0) for a in arbres])
    if total_arbres > 0:
        points_forts.append(f"Agroforesterie active : {total_arbres} arbre(s) d'ombrage répertorié(s).")
    else:
        avertissements.append("Absence totale d'arbres d'ombrage (Stress thermique/hydrique élevé).")
        score -= 5


    # =========================================================
    # 4. DIAGNOSTICS PÉDOLOGIQUE & SANITAIRE (3 critères)
    # =========================================================
    # Critère 13 : Suivi de la santé cacaoyère
    sante = data.get("sante_cacaoyere", [])
    if sante:
        attaques_graves = [s for s in sante if "3." in str(s.get("Sévérité", "")) or "Élevé" in str(s.get("Sévérité", ""))]
        if attaques_graves:
            avertissements.append(f"Pression sanitaire élevée détectée ({len(attaques_graves)} problème(s) sévère(s)).")
            score -= 5
        else:
            points_forts.append("Suivi sanitaire de la cacaoyère enregistré (Pression modérée).")
    else:
        avertissements.append("Évaluation sanitaire de la plantation absente.")
        score -= 5

    # Critère 14 : Relief & Toposéquence
    toposequence = data.get("toposequence", "")
    if toposequence:
        points_forts.append(f"Toposéquence identifiée : {toposequence}.")
    else:
        avertissements.append("Toposéquence non précisée.")
        score -= 2

    # Critère 15 : Caractéristiques du sol
    sols = data.get("caracteristiques_sol", [])
    if len(sols) >= 3:
        points_forts.append(f"Profil Pédologique analysé ({len(sols)} paramètres renseignés).")
    else:
        avertissements.append("Analyse visuelle du sol incomplète.")
        score -= 3


    # =========================================================
    # 5. ITINÉRAIRE TECHNIQUE & QUALITÉ POST-RÉCOLTE (5 critères)
    # =========================================================
    # Critère 16 : Fréquence de récolte
    freq_recolte = data.get("frequence_recolte_jours", 0)
    if 10 <= freq_recolte <= 15:
        points_forts.append(f"Fréquence de récolte optimale ({freq_recolte} jours).")
    elif freq_recolte > 15:
        avertissements.append(f"Fréquence de récolte espacée ({freq_recolte} jours) : Risque de sur-maturation/germination.")
        score -= 3

    # Critère 17 : Temps d'écabossage
    temps_ecab = data.get("temps_ecabossage_jours", 0)
    if 1 <= temps_ecab <= 3:
        points_forts.append(f"Délai d'écabossage conforme ({temps_ecab} jour(s)).")
    elif temps_ecab > 3:
        avertissements.append(f"Délai d'écabossage trop long ({temps_ecab} jours) : Risque de moisissures.")
        score -= 3

    # Critère 18 : Durée de fermentation
    duree_ferm = data.get("duree_fermentation_jours", 0)
    if 5 <= duree_ferm <= 6:
        points_forts.append(f"Durée de fermentation conforme ({duree_ferm} jours).")
    else:
        avertissements.append(f"Durée de fermentation atypique ({duree_ferm} jours).")
        score -= 3

    # Critère 19 : Mode de fermentation
    mode_ferm = data.get("mode_fermentation", "")
    if mode_ferm:
        points_forts.append(f"Mode de fermentation spécifié ({mode_ferm}).")

    # Critère 20 : Méthode de séchage (RÈGLE CRITIQUE QUALITÉ)
    sechage = data.get("methode_sechage", "")
    if "goudron" in sechage.lower():
        alertes_critiques.append("NON-CONFORMITÉ QUALITÉ : Le séchage sur goudron est strictement interdit (risques HAP).")
        score -= 25
    elif sechage:
        points_forts.append("Méthode de séchage conforme aux exigences de qualité.")


    # =========================================================
    # 6. INTRANTS, ÉQUIPEMENTS & MAIN-D'ŒUVRE (4 critères)
    # =========================================================
    # Critère 21 : Utilisation d'engrais
    engrais = data.get("utilisation_engrais", [])
    if len(engrais) > 0:
        points_forts.append(f"Programme de fertilisation renseigné ({len(engrais)} type(s) d'engrais).")

    # Critère 22 : Produits phytosanitaires
    phyto = data.get("produits_phytosanitaires", [])
    if len(phyto) > 0:
        points_forts.append(f"Protection phytosanitaire renseignée ({len(phyto)} produit(s)).")

    # Critère 23 : Gestion des emballages
    emb = data.get("gestion_emballages", "")
    if emb:
        points_forts.append("Mode de gestion des emballages de produits renseigné.")
    else:
        avertissements.append("Gestion des emballages vides non renseignée (Risque environnemental).")
        score -= 2

    # Critère 24 : Matériel & Équipements
    equipements = data.get("equipements", [])
    if len(equipements) > 0:
        points_forts.append(f"Équipements et matériels répertoriés ({len(equipements)} équipement(s)).")
    elif superficie_totale > 2:
        avertissements.append("Aucun équipement enregistré pour la superficie exploitée.")
        score -= 3


    # =========================================================
    # 7. BILAN ÉCONOMIQUE, FINANCIER & FOYER (14 critères)
    # =========================================================
    # Critère 25, 26, 27 : Inclusion financière (Services, Épargne, Crédit)
    financements = data.get("financement", [])
    comptes_epargne = [f for f in financements if f.get("Compte d'épargne (Oui/Non)") == "Oui"]
    if comptes_epargne:
        points_forts.append(f"Inclusion financière effective : Compte d'épargne actif ({len(comptes_epargne)} service(s)).")
    else:
        avertissements.append("Absence de compte d'épargne formel déclaré.")
        score -= 2

    demandes_credit = [f for f in financements if f.get("Demande de crédit (Oui/Non)") == "Oui"]
    if demandes_credit:
        points_forts.append("Accès au crédit sollicité/obtenu auprès des institutions.")

    # Critères 28, 29, 30 : Production historique (Années N-1, N-2, N-3)
    prod_historique = data.get("prod_historique", [])
    total_prod = sum([p.get("Production (kg)", 0) for p in prod_historique])
    if total_prod > 0:
        points_forts.append(f"Historique de production renseigné ({total_prod} kg enregistrés au total).")
    else:
        avertissements.append("Historique de production nul ou non renseigné (0 kg).")
        score -= 5

    # Croisement Intrants vs Production
    if (len(engrais) > 0 or len(phyto) > 0) and total_prod == 0:
        avertissements.append("Incohérence : Intrants/Engrais déclarés alors que la production historique affichée est 0 kg.")
        score -= 5

    # Critères 31, 32 : Autres revenus du foyer
    autres_rev = data.get("autres_revenus", [])
    total_rev_annexes = sum([r.get("Montant estimé/an (FCFA)", 0) for r in autres_rev])
    if total_rev_annexes > 0:
        points_forts.append(f"Revenus complémentaires du foyer enregistrés ({total_rev_annexes:,} FCFA/an).".replace(",", " "))

    # Critères 33 à 38 : Dépenses du foyer (Scolarité, Nourriture, Santé, Électricité, Eau, Charges sociales)
    depenses = data.get("depenses_foyer", [])
    total_depenses = sum([d.get("Montant moyen (FCFA)", 0) for d in depenses])
    if total_depenses > 0:
        points_forts.append(f"Charges du foyer chiffrées : {total_depenses:,} FCFA.".replace(",", " "))
    else:
        avertissements.append("Bilan financier du foyer incomplet : Dépenses non chiffrées (0 FCFA).")
        score -= 5

    # Main-d'œuvre & Coûts
    main_oeuvre = data.get("main_oeuvre", [])
    if len(main_oeuvre) > 0:
        points_forts.append(f"Main-d'œuvre identifiée ({len(main_oeuvre)} intervenant(s)/groupe(s)).")
    else:
        avertissements.append("Aucun détail renseigné sur la main-d'œuvre.")
        score -= 3

    # Ajustement final du score
    score = max(0, score)
    return score, points_forts, avertissements, alertes_critiques


def afficher():
    st.title("📋 PDC - Diagnostic & Plan de Développement")

    # Initialisation de l'étape courante
    if 'etape_pdc' not in st.session_state:
        st.session_state.etape_pdc = 1

    # Dictionnaire pour stocker les réponses
    if 'reponses_pdc' not in st.session_state:
        st.session_state.reponses_pdc = {}

    total_etapes = 15
    st.progress(st.session_state.etape_pdc / total_etapes)


    # ---------------------------------------------------------
    # ÉTAPE 1 : INFORMATIONS GÉNÉRALES
    # ---------------------------------------------------------
    if st.session_state.etape_pdc == 1:
        st.subheader("Étape 1/15 : Identification du Producteur")
        
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
        st.subheader("Étape 2/15 : Données de la Parcelle")

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
        st.subheader("Étape 3/15 : Données Socio-démographiques (Fiche 1)")
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
        st.subheader("Étape 4/15 : Description de l'Exploitation (Fiche 2)")

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
        st.subheader("Étape 5/15 : Densité et Rendement (Fiche 3)")

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
        st.subheader("Étape 6/15 : État Sanitaire, Sol, Récolte & Engrais (Fiche 3)")

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
            if st.button("Suivant) ➡️", use_container_width=True):
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
        st.subheader("Étape 7/15 : Données Socio-économiques (Fiche 4)")

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
            if st.button("Suivant) ➡️", use_container_width=True):
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
    # ÉTAPE 8 : PLANIFICATION COMPLÈTE (PLAN 5 ANS & FICHE 7)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 8:
        st.subheader("Étape 8/15 : Plan d'Action & Programme Annuel (Fiche 7)")
        st.caption("Planification globale, matrice quinquennale, calendrier d'exécution")

        # --- 8.1 GRILLE DE DÉCISION DYNAMIQUE ---
        st.markdown("### 📊 1. Grille de décision")
        st.caption("Cochez les critères constatés sur la parcelle pour déterminer le type de décision.")

        criteres_replantation = [
            "Plantation âgée de plus de 30 ans",
            "Densité inférieure à 800 arbres productifs / ha",
            "Rendement inférieur à 400 kg / ha",
            "Sol favorable à la culture de cacao",
            "Présence de foyers de Swollen Shoot"
        ]

        criteres_rehabilitation = [
            "Plantation âgée de moins de 30 ans",
            "Densité : 800 à 1 000 arbres productifs / ha",
            "Rendement : au moins 400 kg / ha",
            "Absence de foyers de Swollen Shoot"
        ]

        criteres_reconversion = [
            "Pluviométrie inférieure à 1200 mm avec plus de 4 mois de saison sèche",
            "Présence de cuirasse à moins d'un mètre de profondeur"
        ]

        coche_replantation = []
        coche_rehabilitation = []
        coche_reconversion = []

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Critères Replantation / Réhabilitation**")
            for crit in criteres_replantation:
                if st.checkbox(crit, key=f"crit_{crit}"):
                    coche_replantation.append(crit)

            for crit in criteres_rehabilitation:
                if st.checkbox(crit, key=f"crit_{crit}"):
                    coche_rehabilitation.append(crit)

        with col_b:
            st.markdown("**Critères Reconversion**")
            for crit in criteres_reconversion:
                if st.checkbox(crit, key=f"crit_{crit}"):
                    coche_reconversion.append(crit)

        decision_calculee = "Non déterminée"
        if len(coche_reconversion) > 0:
            decision_calculee = "Reconversion"
        elif len(coche_replantation) > 0:
            decision_calculee = "Replantation"
        elif len(coche_rehabilitation) > 0:
            decision_calculee = "Réhabilitation"

        if decision_calculee == "Replantation":
            st.error(f"**Type de décision : {decision_calculee}**")
        elif decision_calculee == "Reconversion":
            st.warning(f"**Type de décision : {decision_calculee}**")
        elif decision_calculee == "Réhabilitation":
            st.success(f"**Type de décision : {decision_calculee}**")
        else:
            st.info("Veuillez cocher au moins un critère pour déterminer la décision.")

        st.markdown("---")

        # --- 8.2 TABLEAU D'ANALYSE DES PROBLÈMES ---
        st.markdown("### ⚠️ 2. Tableau d'analyse des problèmes")
        if 'df_analyse_problemes' not in st.session_state:
            st.session_state.df_analyse_problemes = [
                {
                    "Domaine": "Peuplement du verger",
                    "Problèmes ou Contraintes": "Forte densité (1500 pieds/ha)",
                    "Causes": "Non-respect du dispositif de plantation",
                    "Conséquences": "Prolifération des maladies et insectes",
                    "Solutions": "Régler la densité"
                },
                {
                    "Domaine": "Entretien du verger",
                    "Problèmes ou Contraintes": "Présence de nombreux gourmands",
                    "Causes": "Absence d'entretien",
                    "Conséquences": "Attire les mirides / Réduit la vigueur",
                    "Solutions": "Réaliser la taille d'entretien"
                }
            ]

        analyse_df = st.data_editor(
            st.session_state.df_analyse_problemes,
            num_rows="dynamic",
            key="editor_analyse_prob",
            column_config={
                "Domaine": st.column_config.SelectboxColumn(
                    "Domaine",
                    options=["Peuplement du verger", "Entretien du verger", "Protection phytosanitaire", "Gestion du sol / Ombrage"],
                    required=True
                ),
                "Problèmes ou Contraintes": st.column_config.TextColumn("Problèmes / Contraintes", width="medium"),
                "Causes": st.column_config.TextColumn("Causes", width="medium"),
                "Conséquences": st.column_config.TextColumn("Conséquences", width="medium"),
                "Solutions": st.column_config.TextColumn("Solutions préconisées", width="medium")
            },
            use_container_width=True
        )

        st.markdown("---")

        # --- 8.3 PLAN D'ACTION SUR 5 ANS ---
        st.markdown("### 📅 3. Plan d'Action Quinquennal (Sur 5 ans)")
        if 'df_plan_action_5ans' not in st.session_state:
            st.session_state.df_plan_action_5ans = [
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Objectifs": "Remettre la parcelle en bon état de production",
                    "Activités": "Régler la densité",
                    "Coût (FCFA)": 200000,
                    "A1": True, "A2": False, "A3": False, "A4": False, "A5": False,
                    "Responsable": "Producteur",
                    "Partenaires": "Coopérative"
                }
            ]

        plan_edited_df = st.data_editor(
            st.session_state.df_plan_action_5ans,
            num_rows="dynamic",
            key="editor_plan_action_5ans",
            column_config={
                "Axes stratégiques": st.column_config.SelectboxColumn(
                    "Axes stratégiques",
                    options=[
                        "Axe 1 : Réhabilitation du verger",
                        "Axe 2 : Replantation du verger",
                        "Axe 3 : Amélioration de la fertilité des sols",
                        "Axe 4 : Protection phytosanitaire intégrée"
                    ],
                    required=True,
                    width="medium"
                ),
                "Objectifs": st.column_config.TextColumn("Objectifs", width="medium"),
                "Activités": st.column_config.TextColumn("Activités à réaliser", width="large"),
                "Coût (FCFA)": st.column_config.NumberColumn("Coût (FCFA)", min_value=0, step=5000, format="%d FCFA"),
                "A1": st.column_config.CheckboxColumn("A1"),
                "A2": st.column_config.CheckboxColumn("A2"),
                "A3": st.column_config.CheckboxColumn("A3"),
                "A4": st.column_config.CheckboxColumn("A4"),
                "A5": st.column_config.CheckboxColumn("A5"),
                "Responsable": st.column_config.SelectboxColumn("Responsable", options=["Producteur", "Manœuvre", "Équipe spécialisée"], default="Producteur"),
                "Partenaires": st.column_config.TextColumn("Partenaires", width="medium")
            },
            use_container_width=True
        )

        total_budget_5ans = sum([row.get("Coût (FCFA)", 0) for row in plan_edited_df if isinstance(row, dict) and row.get("Coût (FCFA)")])
        st.info(f"💰 **Budget total estimé du plan d'action sur 5 ans :** `{total_budget_5ans:,} FCFA`".replace(",", " "))

        st.markdown("---")

        # --- 8.4 PROGRAMME ANNUEL D'ACTIVITÉS (FICHE 7) ---
        st.markdown("### 🗓️ 4. Programme Annuel d'Activités (Fiche 7)")
        if 'df_programme_annuel' not in st.session_state:
            st.session_state.df_programme_annuel = [
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Activités": "Régler la densité",
                    "Sous-activités": "Identifier les pieds à supprimer",
                    "Indicateurs": "80% des pieds à supprimer identifiés",
                    "T1": True, "T2": False, "T3": False, "T4": False,
                    "Responsable d'exécution": "Producteur",
                    "Responsable suivi": "Coopérative",
                    "Coût FCFA": 0
                }
            ]

        programme_df = st.data_editor(
            st.session_state.df_programme_annuel,
            num_rows="dynamic",
            key="editor_prog_annuel",
            column_config={
                "Axes stratégiques": st.column_config.SelectboxColumn("Axe stratégique", options=["Axe 1 : Réhabilitation du verger", "Axe 2 : Replantation du verger"], width="medium"),
                "Activités": st.column_config.TextColumn("Activité", width="medium"),
                "Sous-activités": st.column_config.TextColumn("Sous-activité", width="large"),
                "Indicateurs": st.column_config.TextColumn("Indicateur de suivi", width="large"),
                "T1": st.column_config.CheckboxColumn("T1"),
                "T2": st.column_config.CheckboxColumn("T2"),
                "T3": st.column_config.CheckboxColumn("T3"),
                "T4": st.column_config.CheckboxColumn("T4"),
                "Responsable d'exécution": st.column_config.SelectboxColumn("Exécution", options=["Producteur", "Manœuvre", "Équipe spécialisée"], default="Producteur"),
                "Responsable suivi": st.column_config.SelectboxColumn("Suivi", options=["Coopérative", "ANADER", "Agent terrain"], default="Coopérative"),
                "Coût FCFA": st.column_config.NumberColumn("Coût (FCFA)", min_value=0, step=2500, format="%d FCFA")
            },
            use_container_width=True
        )

        total_annuel = sum([row.get("Coût FCFA", 0) for row in programme_df if isinstance(row, dict) and row.get("Coût FCFA")])
        st.info(f"💰 **Budget total du programme annuel :** `{total_annuel:,} FCFA`".replace(",", " "))

        st.markdown("---")

        # BOUTONS DE NAVIGATION ÉTAPE 8
        col_e8_1, col_e8_2 = st.columns([1, 1])
        with col_e8_1:
            if st.button("⬅️ Retour (Étape 7)", key="btn_retour_etape8", use_container_width=True):
                st.session_state.etape_pdc = 7
                st.rerun()

        with col_e8_2:
            if st.button("Suivant ➡️ (Vers Moyens & Coûts - Fiche 8)", key="btn_suivant_etape8", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}
                
                st.session_state.reponses_pdc["decision_retenue"] = decision_calculee
                st.session_state.reponses_pdc["budget_total_5ans"] = total_budget_5ans
                st.session_state.reponses_pdc["budget_annuel_total"] = total_annuel
                
                # Passage à l'étape 9
                st.session_state.etape_pdc = 9
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 9 : DÉTERMINATION DES MOYENS ET COÛTS (FICHE 8)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 9:
        st.subheader("Étape 9/15 : Détermination des moyens et des coûts (Fiche 8)")
        st.caption("Évaluation détaillée des coûts d'investissement, intrants et main d'œuvre par activité sur 5 ans.")

        activite_selectionnee = st.text_input(
            "Activité concernée :",
            value="Activité 1 : Traitement phytosanitaire et fertilisation",
            placeholder="Entrez le nom de l'activité...",
            key="input_activite_fiche8"
        )

        if 'df_moyens_cou_fiche8' not in st.session_state:
            st.session_state.df_moyens_cou_fiche8 = [
                {"Catégorie": "Investissement", "Moyens spécifiques": "Atomiseur", "Unités": "Nombre", "Qté A1": 1, "Coût A1": 150000, "Qté A2": 0, "Coût A2": 0, "Qté A3": 0, "Coût A3": 0, "Qté A4": 0, "Coût A4": 0, "Qté A5": 0, "Coût A5": 0},
                {"Catégorie": "Intrants", "Moyens spécifiques": "Engrais", "Unités": "kg", "Qté A1": 200, "Coût A1": 70000, "Qté A2": 200, "Coût A2": 70000, "Qté A3": 250, "Coût A3": 87500, "Qté A4": 250, "Coût A4": 87500, "Qté A5": 300, "Coût A5": 105000}
            ]

        moyens_cou_df = st.data_editor(
            st.session_state.df_moyens_cou_fiche8,
            num_rows="dynamic",
            key="editor_fiche8_moyens_couts",
            column_config={
                "Catégorie": st.column_config.SelectboxColumn("Catégorie", options=["Investissement", "Intrants", "Main d'œuvre", "Activités d'appui/gestion"], required=True, width="medium"),
                "Moyens spécifiques": st.column_config.TextColumn("Moyens spécifiques", width="medium"),
                "Unités": st.column_config.TextColumn("Unités", width="small"),
                "Qté A1": st.column_config.NumberColumn("Qté A1", min_value=0, step=1),
                "Coût A1": st.column_config.NumberColumn("Coût A1 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A2": st.column_config.NumberColumn("Qté A2", min_value=0, step=1),
                "Coût A2": st.column_config.NumberColumn("Coût A2 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A3": st.column_config.NumberColumn("Qté A3", min_value=0, step=1),
                "Coût A3": st.column_config.NumberColumn("Coût A3 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A4": st.column_config.NumberColumn("Qté A4", min_value=0, step=1),
                "Coût A4": st.column_config.NumberColumn("Coût A4 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A5": st.column_config.NumberColumn("Qté A5", min_value=0, step=1),
                "Coût A5": st.column_config.NumberColumn("Coût A5 (FCFA)", min_value=0, step=1000, format="%d FCFA")
            },
            use_container_width=True
        )

        total_fiche8 = sum(
            (row.get("Coût A1") or 0) + (row.get("Coût A2") or 0) + (row.get("Coût A3") or 0) + (row.get("Coût A4") or 0) + (row.get("Coût A5") or 0)
            for row in moyens_cou_df if isinstance(row, dict)
        )

        st.info(f"💵 **Coût global estimé des moyens (Fiche 8) sur 5 ans :** `{total_fiche8:,} FCFA`".replace(",", " "))

        st.markdown("---")

        # BOUTONS DE NAVIGATION ÉTAPE 9
        col_e9_1, col_e9_2 = st.columns([1, 1])
        with col_e9_1:
            if st.button("⬅️ Retour (Étape 8)", key="btn_retour_etape9", use_container_width=True):
                st.session_state.etape_pdc = 8
                st.rerun()

        with col_e9_2:
            if st.button("Suivant ➡️ (Vers Diagnostic & Audit)", key="btn_suivant_etape9", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}
                
                st.session_state.reponses_pdc["activite_fiche8"] = activite_selectionnee
                st.session_state.reponses_pdc["moyens_fiche8_details"] = moyens_cou_df
                st.session_state.reponses_pdc["budget_fiche8_total"] = total_fiche8
                
                # Passage à l'étape 10 (Audit)
                st.session_state.etape_pdc = 10
                st.rerun()


    # ---------------------------------------------------------
    # ÉTAPE 9 : AUDIT & DIAGNOSTIC QUALITÉ ET BILAN JSON
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 9:
        st.subheader("Étape 9/15 : Audit & Diagnostic Qualité du PDC")
        st.caption("Évaluation de la conformité globale des données collectées")

        donnees_pdc = st.session_state.get("reponses_pdc", {})
        
        # Diagnostic et calcul de conformité
        score_global, pts_forts, avert, alertes = effectuer_diagnostic_exhaustif_json(donnees_pdc)

        st.metric(label="Score de Conformité Global (Étapes 1 à 8)", value=f"{score_global} / 100")

        if alertes:
            st.error("🚨 **Alertes Critiques / Non-Conformités Majeures :**")
            for alerte in alertes:
                st.write(f"- {alerte}")

        if avert:
            st.warning("⚠️ **Avertissements & Points d'attention :**")
            for av in avert:
                st.write(f"- {av}")

        with st.expander("✅ Voir les Points Forts validés"):
            if pts_forts:
                for pf in pts_forts:
                    st.write(f"- {pf}")
            else:
                st.write("Aucun point fort enregistré pour le moment.")

        st.markdown("---")
        st.markdown("### 📄 Bilan global des données collectées (JSON)")
        st.json(donnees_pdc)

        st.markdown("---")

        col_e9_1, col_e9_2 = st.columns([1, 1])
        with col_e9_1:
            if st.button("⬅️ Retour (Moyens Fiche 8)", key="btn_retour_etape9", use_container_width=True):
                st.session_state.etape_pdc = 8
                st.rerun()

        with col_e9_2:
            if st.button("Suivant ➡️ (Vers Clôture & Validation)", key="btn_suivant_etape9", type="primary", use_container_width=True):
                st.session_state.reponses_pdc["score_conformite_etape1_8"] = score_global
                st.session_state.etape_pdc = 10
                st.rerun()

                # ---------------------------------------------------------
    # ÉTAPE 10 : AUDIT & DIAGNOSTIC DE CONFORMITÉ (BILAN FINAL PARTIE 1)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 10:
        st.subheader("Étape 10/15 : Bilan & Diagnostic Qualité du PDC")
        st.caption("Synthèse globale du plan de développement et évaluation de conformité.")

        donnees = st.session_state.get("reponses_pdc", {})

        # --- 10.1 DIAGNOSTIC & AUDIT DE CONFORMITÉ ---
        st.markdown("### 🔍 Diagnostic Qualité du PDC")
        score_global, pts_forts, avert, alertes = effectuer_diagnostic_exhaustif_json(donnees)

        st.metric(label="Score de Conformité Global (Étapes 1 à 9)", value=f"{score_global} / 100")

        if alertes:
            st.error("🚨 **Alertes Critiques / Non-Conformités Majeures :**")
            for alerte in alertes:
                st.write(f"- {alerte}")

        if avert:
            st.warning("⚠️ **Avertissements & Points d'attention :**")
            for av in avert:
                st.write(f"- {av}")

        with st.expander("✅ Voir les Points Forts validés"):
            if pts_forts:
                for pf in pts_forts:
                    st.write(f"- {pf}")
            else:
                st.write("Aucun point fort enregistré pour le moment.")

        st.markdown("---")

        # --- 10.2 RÉCAPITULATIF ET BUDGETS ---
        st.markdown("### 📌 Récapitulatif Synthétique")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Producteur", donnees.get("nom", "Non renseigné"))
        col_s2.metric("Localité / Ville", donnees.get("ville", "Non renseigné"))
        col_s3.metric("Zone d'intervention", f"Zone {donnees.get('zone', '-')}")

        col_b1, col_b2, col_b3 = st.columns(3)
        col_b1.metric("Budget Plan 5 ans", f"{donnees.get('budget_total_5ans', 0):,} FCFA".replace(",", " "))
        col_b2.metric("Programme Annuel (A1)", f"{donnees.get('budget_annuel_total', 0):,} FCFA".replace(",", " "))
        col_b3.metric("Moyens & Intrants (F8)", f"{donnees.get('budget_fiche8_total', 0):,} FCFA".replace(",", " "))

        st.markdown("---")

        # --- 10.3 ACTIONS / NAVIGATION ---
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour (Étape 9 : Moyens & Coûts)", key="btn_retour_etape10", use_container_width=True):
                st.session_state.etape_pdc = 9
                st.rerun()
                
        with col_btn2:
            if st.button("Suivant (Vers Partie 2 : Identification) ➡️", key="btn_suivant_etape10", type="primary", use_container_width=True):
                st.session_state.etape_pdc = 11
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 11 : IDENTIFICATION DU PRODUCTEUR & LOCALISATION (PARTIE 2)
    # (PARTIE VI : STRUCTURATION DU PDC - 1.1 Identification)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 11:
        st.subheader("Étape 11/15 : Identification du Producteur (Situation de Référence)")
        st.info("Saisie des informations d'identification officielles selon le modèle Conseil Café-Cacao.")

        col_id1, col_id2 = st.columns(2)
        
        with col_id1:
            nom_prenoms = st.text_input("Nom et prénoms du producteur", key="input_nom_prenoms")
            contact_tel = st.text_input("Contact (Tél)", key="input_contact_tel")
            code_national = st.text_input("Code National du producteur (Le Conseil du Café-Cacao)", key="input_code_national")
            code_groupe = st.text_input("Code groupe", key="input_code_groupe")
            nom_entite = st.text_input("Nom Entité reconnue", key="input_nom_entite")
            code_entite = st.text_input("Code Entité reconnue", key="input_code_entite")

        with col_id2:
            delegation_regionale = st.text_input("Délégation Régionale du Conseil du Café-Cacao", key="input_delegation")
            departement = st.text_input("Département", key="input_departement")
            sous_prefecture = st.text_input("Sous-Préfecture", key="input_sprefecture")
            village = st.text_input("Village", key="input_village")
            campement = st.text_input("Campement", key="input_campement")

        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour (Étape 10 : Bilan & Diagnostic)", key="btn_retour_etape11", use_container_width=True):
                st.session_state.etape_pdc = 10
                st.rerun()

        with col2:
            if st.button("Suivant (Vers Étape 12 : Info Ménage) ➡️", key="btn_suivant_etape11", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}
                    
                st.session_state.reponses_pdc.update({
                    "nom_prenoms_producteur": nom_prenoms,
                    "contact_tel": contact_tel,
                    "code_national_producteur": code_national,
                    "code_groupe": code_groupe,
                    "nom_entite_reconnue": nom_entite,
                    "code_entite_reconnue": code_entite,
                    "delegation_regionale": delegation_regionale,
                    "departement": departement,
                    "sous_prefecture": sous_prefecture,
                    "village": village,
                    "campement": campement
                })
                st.session_state.etape_pdc = 12
                st.rerun()


        # ---------------------------------------------------------
    # ÉTAPE 12 : MÉNAGE & DESCRIPTION DE L'EXPLOITATION (NORMES CCC)
    # (PARTIE VI : STRUCTURATION DU PDC - 1.2 Ménage & 1.3 Exploitation)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 12:
        st.subheader("Étape 12/15 : Informations Ménage & Description de l'Exploitation")
        st.caption("Données financières, main-d'œuvre et croquis/caractérisation spatiale de la parcelle selon le barème du Conseil Café-Cacao.")

        # =========================================================
        # 12.1 SITUATION DE L'ÉPARGNE
        # =========================================================
        st.markdown("### 💳 1.2.1 Situation de l'épargne")

        if 'df_epargne_pdc' not in st.session_state:
            st.session_state.df_epargne_pdc = [
                {"Épargne": "Mobile Money", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
                {"Épargne": "Microfinance", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
                {"Épargne": "Banque", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
                {"Épargne": "Autres (à préciser)", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
            ]

        df_epargne_edite = st.data_editor(
            st.session_state.df_epargne_pdc,
            key="editor_epargne_pdc",
            column_config={
                "Épargne": st.column_config.TextColumn("Type d'épargne", disabled=True),
                "Avez-vous un compte ?": st.column_config.SelectboxColumn("Compte ?", options=["Oui", "Non"], default="Non"),
                "Avez-vous de l'argent sur le compte ?": st.column_config.SelectboxColumn("Argent disponible ?", options=["Oui", "Non"], default="Non"),
                "Avez-vous bénéficié de financement ?": st.column_config.SelectboxColumn("Financement reçu ?", options=["Oui", "Non"], default="Non"),
                "Montant (FCFA)": st.column_config.NumberColumn("Montant du financement", min_value=0, step=5000, format="%d FCFA")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 12.2 SITUATION DE LA MAIN-D'ŒUVRE
        # =========================================================
        st.markdown("### 👥 1.2.2 Situation de la main-d'œuvre")

        if 'df_main_oeuvre_pdc' not in st.session_state:
            st.session_state.df_main_oeuvre_pdc = [
                {"Membre du ménage": "Propriétaire de l'exploitation", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Plein temps"},
                {"Membre du ménage": "Gérant ou représentant", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Plein temps"},
                {"Membre du ménage": "Conjoints", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Occasionnel"},
                {"Membre du ménage": "Enfants 0 - 6 ans", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Occasionnel"},
                {"Membre du ménage": "Enfant 6 - 18 ans", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Primaire", "Temps de travail": "Occasionnel"},
                {"Membre du ménage": "Enfant + 18 ans", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Secondaire", "Temps de travail": "Plein temps"},
            ]

        df_mo_edite = st.data_editor(
            st.session_state.df_main_oeuvre_pdc,
            key="editor_main_oeuvre_pdc",
            column_config={
                "Membre du ménage": st.column_config.TextColumn("Catégorie membre", disabled=True),
                "Nb Femmes": st.column_config.NumberColumn("F", min_value=0, step=1, help="Nombre de femmes"),
                "Nb Hommes": st.column_config.NumberColumn("M", min_value=0, step=1, help="Nombre d'hommes"),
                "Nb à l'école": st.column_config.NumberColumn("Encore à l'école", min_value=0, step=1),
                "Instruction": st.column_config.SelectboxColumn("Niveau d'instruction", options=["Aucun", "Primaire", "Secondaire", "Universitaire"], default="Aucun"),
                "Temps de travail": st.column_config.SelectboxColumn("Temps de travail sur plantation", options=["Plein temps", "Occasionnel", "Aucun"], default="Occasionnel")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 12.3 DESCRIPTION & CARACTÉRISTIQUES DE L'EXPLOITATION
        # =========================================================
        st.markdown("### 🏡 1.3 Description & Caractéristiques de l'Exploitation")

        with st.expander("📋 **1. Formulaire Agronomique & Foncier**", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                statut_foncier = st.selectbox(
                    "📜 Statut foncier de la parcelle",
                    ["Propriétaire coutumier", "Titre foncier / Certificat foncier", "Métayage (Abougnon / Planteur-Partage)", "Location / Fermage"],
                    key="statut_foncier"
                )
                surf_totale = st.number_input("📐 Superficie totale de l'exploitation (ha)", min_value=0.1, value=5.0, step=0.5, key="surf_totale")
                surf_cacao_prod = st.number_input("🍫 Superficie en cacao productif (ha)", min_value=0.0, value=3.5, step=0.5, key="surf_cacao_prod")
                surf_cacao_jeune = st.number_input("🌱 Superficie cacao immature / immaturité (ha)", min_value=0.0, value=1.0, step=0.5, key="surf_cacao_jeune")

            with col2:
                age_moyen_plan = st.select_slider(
                    "🌳 Âge moyen du verger (années)",
                    options=["0-3 ans (Jeune)", "4-15 ans (Plein rendement)", "16-25 ans (Vieillissant)", "+25 ans (Vétuste)"],
                    value="4-15 ans (Plein rendement)",
                    key="age_moyen"
                )
                relief_sol = st.multiselect(
                    "⛰️ Relief & Type de sol prédominant",
                    ["Bas-fond / Hydromorphe", "Plat / Sol Ferrallitique", "Pente légère / Sol Gravillonnaire", "Zone Rocheuse / Latéritique"],
                    default=["Plat / Sol Ferrallitique"],
                    key="relief_sol"
                )
                contraintes = st.multiselect(
                    "⚠️ Contraintes & Risques observés sur la parcelle",
                    ["Attaque de Swollen Shoot", "Pression Foreurs de tiges / Punaise", "Pourriture brune des cabosses", "Ombrage excessif", "Manque d'eau / Sécheresse", "Inaccessibilité en saison de pluies"],
                    default=["Pression Foreurs de tiges / Punaise"],
                    key="contraintes_parcelle"
                )

                # ---------------------------------------------------------
        # NOUVEAU MODULE : ÉLÉMENTS CARTOGRAPHIQUES & AGROFORESTERIE (EXIGENCES CCC)
        # ---------------------------------------------------------
        with st.expander("🗺️ **2. Cartographie, Arbres Forestiers & Infrastructures (Exigences CCC)**", expanded=True):
            st.caption("Données relatives au croquis/polygone, aux arbres d'ombrage et aux repères géographiques.")

            col_geo1, col_geo2 = st.columns(2)

            with col_geo1:
                st.markdown("**📍 Repères & Voies d'accès**")
                voies_acces = st.multiselect(
                    "Pistes & Voies d'accès",
                    ["Piste cyclable / Piétonne", "Piste camionnière / Sommier", "Route bitumée à proximité", "Traversée par voie d'eau"],
                    default=["Piste camionnière / Sommier"],
                    key="voies_acces"
                )
                elements_parcelle = st.multiselect(
                    "Éléments remarquables de la parcelle",
                    ["Campement / Habitation", "Cours d'eau / Bas-fond", "Puits / Source d'eau", "Zone rocheuse non cultivable"],
                    default=["Campement / Habitation"],
                    key="elements_parcelle"
                )
                waypoint_gps = st.text_input("Coordonnées GPS centrales / Waypoint (Ex: 6.67262 N, -5.28095 W)", value="6.67262 N, -5.28095 W", key="waypoint_gps")

            with col_geo2:
                st.markdown("**🌳 Inventaire Agroforestier (Arbres existants)**")
                nb_arbres_forestiers = st.number_input("Nombre d'arbres forestiers d'ombrage recensés", min_value=0, value=18, step=1, key="nb_arbres_forestiers")
                essences_arbres = st.multiselect(
                    "Essences d'arbres prédominantes",
                    ["Akpi", "Iroko", "Kinkéliba / Fraké", "Framiré", "Avocatier", "Citronnier / Agrumes", "Petit Piment / Autres"],
                    default=["Akpi", "Iroko", "Framiré"],
                    key="essences_arbres"
                )
                densite_ombrage = st.select_slider(
                    "Niveau d'ombrage estimé",
                    options=["Faible (< 10 arbres/ha)", "Adéquat (10-25 arbres/ha)", "Excessif (> 25 arbres/ha)"],
                    value="Adéquat (10-25 arbres/ha)",
                    key="densite_ombrage"
                )

            st.markdown("---")
            st.markdown("**🎨 Rendu du Croquis de la Parcelle**")
            
            col_gen1, col_gen2 = st.columns([1, 1])
            with col_gen1:
                btn_generer_croquis = st.button("🖌️ Générer le croquis automatique (CCC)", use_container_width=True)
            
            with col_gen2:
                fichier_croquis = st.file_uploader("Ou importer un croquis manuel (PNG/JPG)", type=["png", "jpg", "jpeg"], key="fichier_croquis_parcelle")

            # Traitement de la génération automatique
            if btn_generer_croquis:
                img_buf = generer_croquis_parcelle(
                    nom_producteur=st.session_state.get("nom_producteur", "Inconnu"),
                    code_ccc=st.session_state.get("code_producteur", "CCC-001"),
                    surf_totale=surf_totale,
                    surf_prod=surf_cacao_prod,
                    surf_jeune=surf_cacao_jeune,
                    waypoint_gps=waypoint_gps,
                    nb_arbres=nb_arbres_forestiers,
                    essences=essences_arbres,
                    elements=elements_parcelle,
                    acces=voies_acces
                )
                st.session_state["croquis_genere"] = img_buf.getvalue()

            # Affichage de la priorité (Croquis manuel importé sinon croquis généré par Leyla)
            if fichier_croquis is not None:
                st.image(fichier_croquis, caption="Croquis manuel importé pour le dossier CCC", use_container_width=True)
            elif "croquis_genere" in st.session_state:
                st.image(st.session_state["croquis_genere"], caption="Croquis automatique généré par Leyla (Normes CCC)", use_container_width=True)


        # ---------------------------------------------------------
        # CALCULS AUTOMATIQUES & LOGIQUE DE DIAGNOSTIC
        # ---------------------------------------------------------
        surf_autre = max(0.0, surf_totale - (surf_cacao_prod + surf_cacao_jeune))
        pct_cacao = (surf_cacao_prod + surf_cacao_jeune) / surf_totale * 100 if surf_totale > 0 else 0

        # Formattage propre des listes
        relief_str = ", ".join(relief_sol) if relief_sol else "Non précisé"
        contraintes_str = ", ".join(contraintes) if contraintes else "Aucune contrainte majeure"
        elements_str = ", ".join(elements_parcelle) if elements_parcelle else "Aucun élément spécifique"
        voies_str = ", ".join(voies_acces) if voies_acces else "Non précisé"
        essences_str = ", ".join(essences_arbres) if essences_arbres else "Aucune essence spécifiée"

        if "Vétuste" in age_moyen_plan:
            diagnostic_age = "🚨 **Régénération urgente requise** (Verger en fin de cycle productif)."
            niveau_alerte = "error"
        elif "Vieillissant" in age_moyen_plan:
            diagnostic_age = "⚠️ **Replantation progressive à prévoir**."
            niveau_alerte = "warning"
        else:
            diagnostic_age = "✅ **Potentiel de production optimal**."
            niveau_alerte = "success"

        # ---------------------------------------------------------
        # TAB-DE-BORD VISUEL
        # ---------------------------------------------------------
        st.markdown("#### 📊 Tableau de Bord Synthétique de l'Exploitation")

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Superficie Totale", f"{surf_totale:.1f} ha")
        kpi2.metric("Cacao Productif", f"{surf_cacao_prod:.1f} ha", f"{pct_cacao:.0f}% du total")
        kpi3.metric("Arbres Forestiers", f"{nb_arbres_forestiers} pieds", f"{densite_ombrage}")
        kpi4.metric("Autre / Jachère", f"{surf_autre:.1f} ha")

        if niveau_alerte == "error":
            st.error(diagnostic_age)
        elif niveau_alerte == "warning":
            st.warning(diagnostic_age)
        else:
            st.success(diagnostic_age)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("##### 🏞️ Occupation du Sol, Foncier & GPS")
            st.info(
                f"• **Régime foncier :** {statut_foncier}\n\n"
                f"• **Taux d'occupation cacaoyère :** {pct_cacao:.1f}%\n\n"
                f"• **Relief/Sol :** {relief_str}\n\n"
                f"• **Waypoint Central :** `{waypoint_gps}`"
            )

        with col_c2:
            st.markdown("##### 🛡️ Éléments du Croquis & Agroforesterie")
            st.info(
                f"• **Infrastructures/Repères :** {elements_str}\n\n"
                f"• **Accès :** {voies_str}\n\n"
                f"• **Arbres d'ombrage :** {nb_arbres_forestiers} pieds ({essences_str})\n\n"
                f"• **Niveau d'ombrage :** {densite_ombrage}"
            )

        # ---------------------------------------------------------
        # DYNAMIQUE DU RAPPORT SYNTHÉTIQUE (100% CONFORME CONSEIL CAFÉ-CACAO)
        # ---------------------------------------------------------
        st.markdown("#### 📝 Description Officielle (Générée automatiquement pour le Dossier CCC)")

        texte_description = (
            f"L'exploitation sous le statut foncier **{statut_foncier}** couvre une superficie totale mesurée de **{surf_totale:.1f} hectares** (Waypoint GPS : {waypoint_gps}). "
            f"La spéculation principale est la cacaoculture qui occupe **{surf_cacao_prod + surf_cacao_jeune:.1f} ha** "
            f"(soit **{surf_cacao_prod:.1f} ha** en verger productif et **{surf_cacao_jeune:.1f} ha** en phase d'immaturité), représentant **{pct_cacao:.1f}%** de la surface globale. "
            f"Le verger présente un profil d'âge **{age_moyen_plan}**, installé sur un relief de type **{relief_str}**. "
            f"Le croquis cartographique identifie les voies d'accès (**{voies_str}**) ainsi que les infrastructures/repères physiques sur la parcelle (**{elements_str}**). "
            f"Sur le plan agroforestier, l'exploitation compte **{nb_arbres_forestiers} arbres forestiers d'ombrage** "
            f"(principalement : {essences_str}), garantissant un niveau d'ombrage évalué comme **{densite_ombrage}**. "
        )

        if contraintes:
            texte_description += f"Sur le plan phytosanitaire et pédo-climatique, la parcelle subit les contraintes suivantes : **{contraintes_str}**."
        else:
            texte_description += "Aucune contrainte phytosanitaire critique n'a été répertoriée lors de la visite terrain."

        st.markdown(texte_description)

        st.markdown("---")

        # =========================================================
        # NAVIGATION DE L'ÉTAPE 12
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour (Étape 11 : Identification)", key="btn_retour_etape12", use_container_width=True):
                st.session_state.etape_pdc = 11
                st.rerun()

        with col_btn2:
            if st.button("Suivant (Vers Étape 13) ➡️", key="btn_suivant_etape12", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Sauvegarde globale dans session_state
                st.session_state.reponses_pdc["situation_epargne"] = df_epargne_edite
                st.session_state.reponses_pdc["situation_main_oeuvre"] = df_mo_edite
                st.session_state.reponses_pdc["description_exploitation"] = {
                    "statut_foncier": statut_foncier,
                    "superficie_totale": surf_totale,
                    "superficie_cacao_productif": surf_cacao_prod,
                    "superficie_cacao_immature": surf_cacao_jeune,
                    "age_moyen": age_moyen_plan,
                    "relief_sol": relief_sol,
                    "contraintes": contraintes,
                    "waypoint_gps": waypoint_gps,
                    "voies_acces": voies_acces,
                    "elements_parcelle": elements_parcelle,
                    "nb_arbres_forestiers": nb_arbres_forestiers,
                    "essences_arbres": essences_arbres,
                    "densite_ombrage": densite_ombrage,
                    "texte_synthese_auto": texte_description
                }

                st.session_state.etape_pdc = 13
                st.rerun()



    # ---------------------------------------------------------
    # ÉTAPE 13 : CULTURES, AGROFORESTERIE & ÉQUIPEMENTS (CCC)
    # (PARTIE VI : STRUCTURATION DU PDC - 1.4 Cultures & Matériels)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 13:
        st.subheader("Étape 13/15 : Cultures, Agroforesterie & Matériel Agricole")
        st.caption("Caractérisation des spéculations, inventaire des arbres d'ombrage et bilan des équipements de l'exploitation.")

        # =========================================================
        # 13.1 SYSTÈME DE CULTURES & REVENUS
        # =========================================================
        st.markdown("### 🌾 1.3.1 Diversification & Cultures de l'Exploitation")

        if 'df_cultures_pdc' not in st.session_state:
            st.session_state.df_cultures_pdc = [
                {"Culture": "Cacao - Parcelle 1", "Superficie (ha)": 3.5, "Année de création": 2012, "Source matériel végétal": "SATMACI / ANADER / CNRA", "Production campagne préc. (kg)": 2100, "Revenu (FCFA)": 3150000},
                {"Culture": "Cacao - Parcelle 2", "Superficie (ha)": 1.0, "Année de création": 2023, "Source matériel végétal": "Pépiniériste privé", "Production campagne préc. (kg)": 0, "Revenu (FCFA)": 0},
                {"Culture": "Hévéa", "Superficie (ha)": 0.0, "Année de création": 2020, "Source matériel végétal": "Tout venant", "Production campagne préc. (kg)": 0, "Revenu (FCFA)": 0},
                {"Culture": "Palmier à huile", "Superficie (ha)": 0.0, "Année de création": 2020, "Source matériel végétal": "SATMACI / ANADER / CNRA", "Production campagne préc. (kg)": 0, "Revenu (FCFA)": 0},
                {"Culture": "Vivriers (Banane/Maïs/Cassava)", "Superficie (ha)": 0.5, "Année de création": 2024, "Source matériel végétal": "Tout venant", "Production campagne préc. (kg)": 1200, "Revenu (FCFA)": 450000},
                {"Culture": "Autres activités / Verger", "Superficie (ha)": 0.0, "Année de création": 2020, "Source matériel végétal": "Tout venant", "Production campagne préc. (kg)": 0, "Revenu (FCFA)": 0},
            ]

        df_cultures_edite = st.data_editor(
            st.session_state.df_cultures_pdc,
            key="editor_cultures_pdc",
            column_config={
                "Culture": st.column_config.TextColumn("Culture / Parcelle", disabled=False),
                "Superficie (ha)": st.column_config.NumberColumn("Superficie (ha)", min_value=0.0, step=0.1, format="%.2f ha"),
                "Année de création": st.column_config.NumberColumn("Année", min_value=1960, max_value=2030, step=1),
                "Source matériel végétal": st.column_config.SelectboxColumn("Source plants/semences", options=["SATMACI / ANADER / CNRA", "Tout venant", "Pépiniériste privé"], default="SATMACI / ANADER / CNRA"),
                "Production campagne préc. (kg)": st.column_config.NumberColumn("Prod. Précédente (kg)", min_value=0, step=50, format="%d kg"),
                "Revenu (FCFA)": st.column_config.NumberColumn("Revenu estimé (FCFA)", min_value=0, step=25000, format="%d FCFA")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 13.2 ARBRES ASSOCIÉS & INVENTAIRE AGROFORESTIER
        # =========================================================
        st.markdown("### 🌳 1.3.2 Inventaire des Arbres hors Cacaoyer (Normes CCC)")
        st.caption("Renseignez les arbres d'ombrage ou forestiers présents dans la cacaoyère et la décision d'aménagement.")

        if 'df_arbres_pdc' not in st.session_state:
            st.session_state.df_arbres_pdc = [
                {"Nom de l'arbre": "Akpi", "Nombre": 12, "Latitude (N)": 6.020668, "Longitude (W)": -4.3571323, "Statut actuel": "Préservé", "Rôle / Avantage": "Bois d'œuvre / Ombrage", "Décision": "À maintenir", "Remarque / Distance": "Bonne association"},
                {"Nom de l'arbre": "Fraké", "Nombre": 4, "Latitude (N)": 6.020664, "Longitude (W)": -4.3569498, "Statut actuel": "Préservé", "Rôle / Avantage": "Bois d'œuvre", "Décision": "À éliminer", "Remarque / Distance": "Situé à 1,5m d'un cacaoyer"},
                {"Nom de l'arbre": "Fromager", "Nombre": 2, "Latitude (N)": 6.020614, "Longitude (W)": -4.3561020, "Statut actuel": "Préservé", "Rôle / Avantage": "Ombrage haut", "Décision": "À maintenir", "Remarque / Distance": "En bordure de parcelle"},
            ]

        df_arbres_edite = st.data_editor(
            st.session_state.df_arbres_pdc,
            key="editor_arbres_pdc",
            column_config={
                "Nom de l'arbre": st.column_config.TextColumn("Essence / Nom", required=True),
                "Nombre": st.column_config.NumberColumn("Pieds", min_value=1, step=1),
                "Latitude (N)": st.column_config.NumberColumn("Lat (N)", format="%.6f"),
                "Longitude (W)": st.column_config.NumberColumn("Long (W)", format="%.6f"),
                "Statut actuel": st.column_config.SelectboxColumn("Statut", options=["Préservé", "Planté", "Régénération naturelle"], default="Préservé"),
                "Rôle / Avantage": st.column_config.SelectboxColumn("Rôle pour cacaoyer", options=["Bois d'œuvre", "Fertilité du sol", "Produit secondaire (PNFL)", "Ombrage excessif / Hôte pucerons"], default="Bois d'œuvre"),
                "Décision": st.column_config.SelectboxColumn("Action préconisée", options=["À maintenir", "À éliminer", "À élaguer"], default="À maintenir"),
                "Remarque / Distance": st.column_config.TextColumn("Remarques terrain")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 13.3 MATÉRIEL ET ÉQUIPEMENTS AGRICOLES
        # =========================================================
        st.markdown("### 🚜 1.3.3 Matériel Agricole & Équipements")

        if 'df_materiel_pdc' not in st.session_state:
            st.session_state.df_materiel_pdc = [
                {"Type": "Matériel de traitement", "Désignation": "Pulvérisateur à dos", "Quantité": 1, "Année acquisition": 2022, "Coût (FCFA)": 25000, "État": "Bon"},
                {"Type": "Matériel de traitement", "Désignation": "Atomiseur à moteur", "Quantité": 1, "Année acquisition": 2021, "Coût (FCFA)": 130000, "État": "Acceptable"},
                {"Type": "Matériel de transport", "Désignation": "Brouette", "Quantité": 2, "Année acquisition": 2023, "Coût (FCFA)": 30000, "État": "Bon"},
                {"Type": "Moyen de déplacement", "Désignation": "MOTO Tricycle / Moto 2 roues", "Quantité": 1, "Année acquisition": 2020, "Coût (FCFA)": 650000, "État": "Mauvais"},
            ]

        df_mat_edite = st.data_editor(
            st.session_state.df_materiel_pdc,
            key="editor_materiel_pdc",
            column_config={
                "Type": st.column_config.SelectboxColumn("Type d'équipement", options=["Matériel de traitement", "Matériel de récolte / Entretien", "Matériel de transport", "Moyen de déplacement"], default="Matériel de traitement"),
                "Désignation": st.column_config.TextColumn("Désignation du matériel", required=True),
                "Quantité": st.column_config.NumberColumn("Qté", min_value=0, step=1),
                "Année acquisition": st.column_config.NumberColumn("Année", min_value=1990, max_value=2030, step=1),
                "Coût (FCFA)": st.column_config.NumberColumn("Valeur / Coût", min_value=0, step=5000, format="%d FCFA"),
                "État": st.column_config.SelectboxColumn("État d'usure", options=["Bon", "Acceptable", "Mauvais"], default="Bon")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        # ---------------------------------------------------------
        # SYNTHÈSE AUTOMATIQUE DE L'ÉTAPE 13
        # ---------------------------------------------------------
        tot_revenu_agri = sum(item.get("Revenu (FCFA)", 0) for item in df_cultures_edite)
        tot_prod_cacao = sum(item.get("Production campagne préc. (kg)", 0) for item in df_cultures_edite if "Cacao" in item.get("Culture", ""))
        tot_arbres_maintenir = sum(item.get("Nombre", 1) for item in df_arbres_edite if item.get("Décision") == "À maintenir")
        tot_arbres_eliminer = sum(item.get("Nombre", 1) for item in df_arbres_edite if item.get("Décision") == "À éliminer")

        st.markdown("#### 📊 Bilan Synthétique de l'Étape 13")
        kpi_e1, kpi_e2, kpi_e3 = st.columns(3)
        kpi_e1.metric("Production Cacao Totale", f"{tot_prod_cacao:,} kg")
        kpi_e2.metric("Revenu Agricole Global", f"{tot_revenu_agri:,} FCFA")
        kpi_e3.metric("Bilan Agroforesterie", f"{tot_arbres_maintenir} à maintenir", f"{tot_arbres_eliminer} à éliminer/élaguer")

        st.markdown("---")

        # =========================================================
        # NAVIGATION DE L'ÉTAPE 13
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour (Étape 12 : Exploitation)", key="btn_retour_etape13", use_container_width=True):
                st.session_state.etape_pdc = 12
                st.rerun()

        with col_btn2:
            if st.button("Suivant (Vers Étape 14) ➡️", key="btn_suivant_etape13", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Sauvegarde globale
                st.session_state.reponses_pdc["cultures_et_revenus"] = df_cultures_edite
                st.session_state.reponses_pdc["inventaire_arbres"] = df_arbres_edite
                st.session_state.reponses_pdc["materiel_agricole"] = df_mat_edite

                st.session_state.etape_pdc = 14
                st.rerun()



    # ---------------------------------------------------------
    # ÉTAPE 14 : PLANIFICATION STRATÉGIQUE, PROGRAMME ANNUEL & FACTEURS DE SUCCÈS
    # (PARTIE II, III & IV DU PDC)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 14:
        st.subheader("Étape 14/15 : Planification Stratégique (5 Ans) & Programme Annuel d'Action")
        st.caption("Définition du plan quinquennal, du chronogramme opérationnel trimestriel et des facteurs clés de succès du PDC.")

        # =========================================================
        # 14.1 PLANIFICATION STRATÉGIQUE SUR 5 ANS
        # =========================================================
        st.markdown("### 📈 II - Planification Stratégique sur les Cinq (5) Prochaines Années")
        st.caption("Précisez les axes, objectifs, activités, budgets et responsables sur l'horizon 5 ans (A1 à A5).")

        if 'df_plan_quinquennal' not in st.session_state:
            st.session_state.df_plan_quinquennal = [
                {
                    "Stratégie / Axe": "Axe 1 : Réhabilitation du verger",
                    "Objectifs": "Restaurer la productivité des parcelles anciennes",
                    "Activités": "Régler la densité (égourmandage, égrapillage)",
                    "Coût (FCFA)": 150000,
                    "A1": True, "A2": True, "A3": False, "A4": False, "A5": False,
                    "Exécutant": "Producteur + M.O.",
                    "Partenaires": "Coopérative / ANADER"
                },
                {
                    "Stratégie / Axe": "Axe 1 : Réhabilitation du verger",
                    "Objectifs": "Réduire la pression parasitaire et parasitaire",
                    "Activités": "Taille des loranthacées (guis) et sanitation",
                    "Coût (FCFA)": 100000,
                    "A1": True, "A2": True, "A3": True, "A4": False, "A5": False,
                    "Exécutant": "Producteur",
                    "Partenaires": "ANADER"
                },
                {
                    "Stratégie / Axe": "Axe 2 : Plantation / Replantation",
                    "Objectifs": "Renouveler 2 ha en agroforesterie",
                    "Activités": "Replanter 2 ha avec espèces d'ombrage (Akpi/Iroko)",
                    "Coût (FCFA)": 600000,
                    "A1": False, "A2": True, "A3": True, "A4": False, "A5": False,
                    "Exécutant": "Producteur",
                    "Partenaires": "Conseil Café-Cacao"
                },
                {
                    "Stratégie / Axe": "Axe 3 : Diversification",
                    "Objectifs": "Sécuriser les revenus hors saison cacao",
                    "Activités": "Mise en place d'une parcelle vivrière (Banane/Piment)",
                    "Coût (FCFA)": 200000,
                    "A1": True, "A2": False, "A3": False, "A4": False, "A5": False,
                    "Exécutant": "Famille / Ménage",
                    "Partenaires": "Coopérative"
                }
            ]

        df_quinquennal_edite = st.data_editor(
            st.session_state.df_plan_quinquennal,
            key="editor_plan_quinquennal",
            column_config={
                "Stratégie / Axe": st.column_config.SelectboxColumn("Axe Stratégique", options=["Axe 1 : Réhabilitation du verger", "Axe 2 : Plantation / Replantation", "Axe 3 : Diversification"], required=True),
                "Objectifs": st.column_config.TextColumn("Objectifs visés"),
                "Activités": st.column_config.TextColumn("Activités à mener", required=True),
                "Coût (FCFA)": st.column_config.NumberColumn("Coût estimé (FCFA)", min_value=0, step=25000, format="%d FCFA"),
                "A1": st.column_config.CheckboxColumn("Année 1"),
                "A2": st.column_config.CheckboxColumn("Année 2"),
                "A3": st.column_config.CheckboxColumn("Année 3"),
                "A4": st.column_config.CheckboxColumn("Année 4"),
                "A5": st.column_config.CheckboxColumn("Année 5"),
                "Exécutant": st.column_config.TextColumn("Exécutant principal"),
                "Partenaires": st.column_config.TextColumn("Partenaires appui")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 14.2 PROGRAMME ANNUEL D'ACTION (CHRONOGRAMME A1)
        # =========================================================
        st.markdown("### 🗓️ III - Programme Annuel d'Action (Détail Année 1)")
        st.caption("Planification opérationnelle par trimestre (T1 à T4) pour la première année de mise en œuvre.")

        if 'df_programme_annuel' not in st.session_state:
            st.session_state.df_programme_annuel = [
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Activités / Sous-activités": "Régler la densité (égourmandage, échenillonnage)",
                    "Indicateur": "Nombre d'hectares traités (ex: 3.5 ha)",
                    "T1": True, "T2": True, "T3": False, "T4": False,
                    "Coût (FCFA)": 75000
                },
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Activités / Sous-activités": "Réaliser la taille des loranthacées",
                    "Indicateur": "Taux d'arbres nettoyés (%)",
                    "T1": False, "T2": True, "T3": True, "T4": False,
                    "Coût (FCFA)": 50000
                },
                {
                    "Axes stratégiques": "Axe 3 : Diversification",
                    "Activités / Sous-activités": "Préparation terrain & planting banane/piment",
                    "Indicateur": "Superficie installée (ha)",
                    "T1": True, "T2": False, "T3": False, "T4": False,
                    "Coût (FCFA)": 150000
                }
            ]

        df_annuel_edite = st.data_editor(
            st.session_state.df_programme_annuel,
            key="editor_programme_annuel",
            column_config={
                "Axes stratégiques": st.column_config.TextColumn("Axe Stratégique", required=True),
                "Activités / Sous-activités": st.column_config.TextColumn("Activités / Sous-activités", required=True),
                "Indicateur": st.column_config.TextColumn("Indicateur de suivi"),
                "T1": st.column_config.CheckboxColumn("T1 (Jan-Mar)"),
                "T2": st.column_config.CheckboxColumn("T2 (Avr-Juin)"),
                "T3": st.column_config.CheckboxColumn("T3 (Juil-Sept)"),
                "T4": st.column_config.CheckboxColumn("T4 (Oct-Déc)"),
                "Coût (FCFA)": st.column_config.NumberColumn("Coût Trimestriel (FCFA)", min_value=0, step=10000, format="%d FCFA")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 14.3 FACTEURS DE SUCCÈS ET D'ÉCHEC
        # =========================================================
        st.markdown("### ⚠️ IV - Facteurs de Succès et d'Échec")
        st.caption("Décrivez les conditions indispensables pour une mise en œuvre efficace du plan de développement.")

        def_facteurs = (
            "1. Accès à temps aux intrants homologués (engrais/fongicides) et plants d'arbres d'ombrage.\n"
            "2. Disponibilité de la main-d'œuvre familiale et occasionnelle qualifiée pour la taille.\n"
            "3. Accompagnement technique régulier par le conseiller agricole de la coopérative / ANADER.\n"
            "4. Maîtrise de la trésorerie et accès au crédit / préfinancement des activités de réhabilitation.\n"
            "5. Conditions climatiques favorables (pluviométrie régulière et absence de sécheresse sévère)."
        )

        facteurs_succes = st.text_area(
            "Conditions indispensables & risques identifiés",
            value=st.session_state.get("facteurs_succes_pdc", def_facteurs),
            height=150,
            key="input_facteurs_succes"
        )

        # ---------------------------------------------------------
        # SYNTHÈSE FINANCIÈRE DE LA PLANIFICATION
        # ---------------------------------------------------------
        cout_total_5ans = sum(item.get("Coût (FCFA)", 0) for item in df_quinquennal_edite)
        cout_total_a1 = sum(item.get("Coût (FCFA)", 0) for item in df_annuel_edite)

        st.markdown("#### 📊 Synthèse Budgétaire de la Planification")
        kpi_p1, kpi_p2 = st.columns(2)
        kpi_p1.metric("Budget Plan Quinquennal (5 Ans)", f"{cout_total_5ans:,} FCFA")
        kpi_p2.metric("Budget Année 1 (Programme d'Action)", f"{cout_total_a1:,} FCFA")

        st.markdown("---")

        # =========================================================
        # NAVIGATION DE L'ÉTAPE 14
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour (Étape 13 : Cultures & Matériel)", key="btn_retour_etape14", use_container_width=True):
                st.session_state.etape_pdc = 13
                st.rerun()

        with col_btn2:
            if st.button("Suivant (Vers Étape 15 : Bilan & PDF) ➡️", key="btn_suivant_etape14", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Sauvegarde globale
                st.session_state.reponses_pdc["plan_quinquennal"] = df_quinquennal_edite
                st.session_state.reponses_pdc["programme_annuel"] = df_annuel_edite
                st.session_state.reponses_pdc["facteurs_succes"] = facteurs_succes
                st.session_state["facteurs_succes_pdc"] = facteurs_succes

                st.session_state.etape_pdc = 15
                st.rerun()


