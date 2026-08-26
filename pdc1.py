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

import streamlit as st
def afficher():
    st.subheader(f"DOCUMENT ARS 1000 - PAGE {st.session_state.page_actuelle}")
# =========================================================================
# 🎛️ INITIALISATION CENTRALISÉE DE TOUTES LES PAGES (MÉMOIRE GLOBALE LEILA)
# =========================================================================
if "initialisation_complete" not in st.session_state:
    valeurs_par_defaut = {
        # --- Identification & Paramètres de navigation ---
        "page_actuelle": -1,
        "info_coop_nom": "Non renseigné",
        "info_coop_ville": "Non renseignée",
        "info_coop_contact": "Non renseigné",
        
        # --- Bloc Spécifique Page 14 : Détermination Densité ---
        "p14_nb_carres": 4,
        "p14_densite_calculee": 0,
        "p14_moyenne_tiges": 1.1,
        "p14_etat_peuplement": "Non diagnostiqué",
        "p14_valeurs_cacaoyers": {f"cac_{i}": 12 for i in range(20)},
        "p14_valeurs_tiges": {f"tig_{i}": 1.1 for i in range(20)},
        
        # --- Variables d'Audit et Norme ARS 1000 (Utilisées par la Page 37 & 49) ---
        "ars_travail_enfants": "En attente",         # Pages Sociales (ex: P8, P20, P41)
        "ars_mapping_gps": False,                   # Pages Cartographie (ex: P9, P43)
        "ars_arbres_hectare": 0,                    # Pages Agroforesterie (ex: P12, P45)
        "ars_gestion_emballages": False,             # Pages Environnement (ex: P19, P46)
        
        # --- Tableaux complexes & Budgets ---
        "p34_donnees": {},                          # Page 34 : Tableau des Moyens et Coûts
        "donnees_activites": {},                     # Fallback structure d'activités
        "score_page_37": 0,                         # Sauvegarde du verdict d'audit
        
        # --- Données Générales de Cultures (Variétés, etc.) ---
        "culture_selectionnee": None,
        "varieties_sorties": [],
        
        # --- Initialisation dynamique par défaut pour TOUTES les pages (1 à 49) ---
        # On s'assure que chaque page dispose d'une clé de validation globale
        **{f"page_{i}_validee": False for i in range(50)}
    }
    
    # Injection automatique dans le session_state si la clé n'existe pas
    for cle, valeur in valeurs_par_defaut.items():
        if cle not in st.session_state:
            st.session_state[cle] = valeur
            
    st.session_state["initialisation_complete"] = True

# ==========================================================
# 1. CONFIGURATION DE LA PAGE (Doit être exécutée en premier)
# ==========================================================
st.set_page_config(
    page_title="LAYLA IA - Agro-Biodiversité",
    page_icon="🌿",
    layout="wide"
)

# ==========================================================
# 2. FONCTIONS DE BASE & SYSTÈME DE JOURNALISATION (LOGS)
# ==========================================================
def memoriser_marche(message):
    """ Enregistre silencieusement les modifications dans le fichier texte. """
    horodatage = time.strftime("%d/%m/%Y %H:%M:%S")
    log = f"[{horodatage}] {message}"
    try:
        with open("journal_layla.txt", "a", encoding="utf-8") as f:
            f.write(log + "\n")
    except Exception:
        pass 

def log_action(message):
    """Équivalent de mémoriser_marche pour l'interface."""
    horodatage = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{horodatage}] {message}"
    st.session_state.logs.append(entry)
    st.toast(message, icon="📝")


# ==========================================================
# 3. ÉCOUTEUR UNIVERSEL (TRACKER DE LEILA CORRIGÉ)
# ==========================================================
def leila_tracker_central():
    """ Écouteur universel protégeant les structures et les modifications de l'application. """
    # INITIALISATION SANS RETURN BLOQUANT
    if "leila_memoire_tampon" not in st.session_state:
        st.session_state.leila_memoire_tampon = {}

    cles_a_ignorer = ["leila_memoire_tampon", "page_actuelle", "logs", "editor_"]

    for cle, valeur_actuelle in list(st.session_state.items()):
        if any(ignore in cle for ignore in cles_a_ignorer) or callable(valeur_actuelle):
            continue

        ancienne_valeur = st.session_state.leila_memoire_tampon.get(cle, None)

        if ancienne_valeur is not None:
            if hasattr(valeur_actuelle, "equals"): 
                if not ancienne_valeur.equals(valeur_actuelle):
                    memoriser_marche(f"Le tableau élastique [{cle}] a été mis à jour.")
            elif hasattr(ancienne_valeur, "equals"):
                memoriser_marche(f"La structure de [{cle}] a changé de format.")
            else:
                if ancienne_valeur != valeur_actuelle:
                    if isinstance(valeur_actuelle, list) and cle == "arbres_inventoriez":
                        memoriser_marche(f"L'inventaire global [{cle}] a été mis à jour (Page 45).")
                    else:
                        memoriser_marche(f"Le champ [{cle}] a changé : '{ancienne_valeur}' ➡️ '{valeur_actuelle}'")

        # Sauvegarde systématique dans le tampon
        if hasattr(valeur_actuelle, "copy"):
            st.session_state.leila_memoire_tampon[cle] = valeur_actuelle.copy()
        else:
            st.session_state.leila_memoire_tampon[cle] = valeur_actuelle


# ==========================================================
# 4. LOGIQUE MÉTIER & INITIALISATION DE LA MÉMOIRE (Session State)
# ==========================================================
if 'donnees_pdc' not in st.session_state:
    st.session_state.donnees_pdc = {}

if 'page_actuelle' not in st.session_state:
    st.session_state.page_actuelle = -1

if "logs" not in st.session_state:
    st.session_state.logs = []

if 'data_ars' not in st.session_state:
    st.session_state.data_ars = {
        11: {"colonnes": ["Type", "Désignation", "Quantité", "Année", "Coût", "Bon", "Acceptable", "Mauvais"]},
        12: {"cols": ["N°", "Nom Local", "Nom botanique", "Circonférence (cm)", "Latitude", "Longitude", "Origine", "Avantages", "Usage", "Décision", "Raison"]},
        14: {"colonnes": ["Carré P", "Nombre d'arbres", "Observation"]},
        16: {"colonnes": ["Paramètre", "Observation / Score", "Commentaires"]},
        19: {"sections": [
            {"titre": "Suivi des Engrais", "cols": ["Date", "Type", "Quantité", "Parcelle"]},
            {"titre": "Produits Phytosanitaires", "cols": ["Date", "Produit", "Cible", "Dosage"]},
            {"titre": "Gestion des Emballages", "question": "Où sont stockés les emballages vides ?"}
        ]}
    }

# 📑 Déclenchement automatique du tracker pour capturer l'état au chargement de la page
leila_tracker_central()

# ==========================================================
# 5. CLASSES ET FONCTIONS OUTILS
# ==========================================================
class RapportAgricoleWeb(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'LAYLA - RAPPORT DE DIAGNOSTIC AGRICOLE', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def changer_page(delta):
    """Gère le changement de page en forçant la sauvegarde immédiate."""
    # On force la mémorisation des saisies actuelles avant de changer de page
    leila_tracker_central()
    
    nouvelle_page = st.session_state.page_actuelle + delta
    if -1 <= nouvelle_page <= 49:
        st.session_state.page_actuelle = nouvelle_page
        st.rerun()

def appliquer_style_layla():
    st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    /* ... le reste de ton style ... */
    </style>
    """, unsafe_allow_html=True)

def parler(texte):
    """Note : En Streamlit Web, l'audio serveur (pyttsx3) ne s'entend pas chez l'utilisateur."""
    st.toast(texte, icon="🗣️")


def creer_champ_agri(label, id_technique):
    """Crée un champ texte pro avec persistance stricte au changement de page."""
    # Clé stable associée à la page en cours
    cle_unique = f"P{st.session_state.page_actuelle}_{id_technique}"
    
    # 1. Récupération : d'abord dans l'état actif, sinon dans le tampon central de Leila
    valeur_existante = st.session_state.get(cle_unique, "")
    if valeur_existante == "" and "leila_memoire_tampon" in st.session_state:
        valeur_existante = st.session_state.leila_memoire_tampon.get(cle_unique, "")

    # 2. Rendu du composant
    valeur = st.text_input(label, value=str(valeur_existante), key=cle_unique)
    
    # 3. Sauvegarde immédiate pour éviter les pertes au changement de page
    st.session_state[cle_unique] = valeur
    return valeur


def afficher_tableau_page():
    pid = st.session_state.page_actuelle
    st.subheader(f"📊 Tableau de suivi - Section {pid}")
    key_table = f"data_table_P{pid}"
    if key_table not in st.session_state:
        st.session_state[key_table] = [
            {"Désignation": "", "Quantité": 0, "Observation": ""}
        ]
    df_edite = st.data_editor(
        st.session_state[key_table],
        key=f"editor_P{pid}",
        num_rows="dynamic",
        width="stretch"
    )
    st.session_state[key_table] = df_edite

if st.button("➕ Ajouter un Tableau libre"):
    st.info("Utilisez le bouton '+' en bas du tableau ci-dessus pour ajouter des lignes.")

def afficher_page_dynamique(page_id):
    """Remplace rafraichir_universelle et la gestion manuelle des grids."""
    config = st.session_state.registre_pages_config.get(page_id)
    if not config:
        st.warning(f"Configuration pour {page_id} manquante.")
        return
    st.header(f"📋 {config.get('titre', 'Saisie de données')}")
    if f"data_{page_id}" not in st.session_state:
        st.session_state[f"data_{page_id}"] = pd.DataFrame(columns=config["cols"])
    df_actuel = st.session_state[f"data_{page_id}"]
    df_edite = st.data_editor(
        df_actuel,
        key=f"editor_{page_id}",
        num_rows="dynamic",
        width="stretch",
        hide_index=False
    )
    st.session_state[f"data_{page_id}"] = df_edite
    nom_methode_legende = f"ajouter_legendes_page_{page_id.replace('P', '')}"
    if hasattr(self_simule, nom_methode_legende):
        getattr(self_simule, nom_methode_legende)()

def interface_ajout_colonne(page_id):
    with st.expander("🛠️ Paramètres du tableau"):
        nouveau_nom = st.text_input("Nom de la nouvelle colonne :", key=f"new_col_{page_id}")
        if st.button("Ajouter la colonne"):
            if nouveau_nom:
                df = st.session_state[f"data_{page_id}"]
                if nouveau_nom not in df.columns:
                    df[nouveau_nom] = ""
                    st.session_state[f"data_{page_id}"] = df
                    st.rerun()

def nettoyer_page(self):
    for child in self.scrollable_frame.winfo_children():
        child.destroy()


def generer_grille_excel_universel(cle_unique, donnees_initiales, hauteur=350):
    """ Grille universelle style Excel/Word avec persistance stable. """
    if cle_unique not in st.session_state:
        st.session_state[cle_unique] = pd.DataFrame(donnees_initiales)

    df_actuel = st.session_state[cle_unique]

    st.markdown("##### 🛠️ Outils de structure de la grille")
    col_lignes, col_colonnes = st.columns(2)

    with col_lignes:
        st.write("**↕️ Gestion des Lignes**")
        c_add_r, c_del_r = st.columns(2)
        with c_add_r:
            intervalle_r = st.text_input("Insérer ligne (ex: 2-3)", key=f"inv_r_{cle_unique}", placeholder="Ex: 2-3")
            if st.button("➕ Insérer la Ligne", key=f"btn_add_r_{cle_unique}", width="stretch"):
                if "-" in intervalle_r:
                    try:
                        index_insertion = int(intervalle_r.split("-")[0])
                        nouvelle_ligne = pd.DataFrame([{col: "" for col in df_actuel.columns}])
                        df_haut = df_actuel.iloc[:index_insertion]
                        df_bas = df_actuel.iloc[index_insertion:]
                        df_actuel = pd.concat([df_haut, nouvelle_ligne, df_bas], ignore_index=True)
                        st.session_state[cle_unique] = df_actuel
                        st.rerun()
                    except Exception:
                        st.error("Format invalide. Utilisez 'Chiffre-Chiffre'")
                else:
                    nouvelle_ligne = pd.DataFrame([{col: "" for col in df_actuel.columns}])
                    df_actuel = pd.concat([df_actuel, nouvelle_ligne], ignore_index=True)
                    st.session_state[cle_unique] = df_actuel
                    st.rerun()

        with c_del_r:
            ligne_a_suppr = st.text_input("Numéro ligne à supprimer", key=f"inv_del_r_{cle_unique}", placeholder="Ex: 2")
            if st.button("❌ Supprimer la Ligne", key=f"btn_del_r_{cle_unique}", width="stretch"):
                if ligne_a_suppr.isdigit():
                    idx = int(ligne_a_suppr) - 1
                    if 0 <= idx < len(df_actuel):
                        df_actuel = df_actuel.drop(df_actuel.index[idx]).reset_index(drop=True)
                        st.session_state[cle_unique] = df_actuel
                        st.rerun()

    with col_colonnes:
        st.write("**↔️ Gestion des Colonnes**")
        c_add_c, c_del_c = st.columns(2)
        with c_add_c:
            intervalle_c = st.text_input("Insérer col. (ex: 2-3)", key=f"inv_c_{cle_unique}", placeholder="Ex: 2-3")
            nom_nouvelle_col = st.text_input("Nom de la colonne", key=f"nom_c_{cle_unique}", placeholder="Ex: Commentaire")
            if st.button("➕ Insérer la Colonne", key=f"btn_add_c_{cle_unique}", width="stretch"):
                if nom_nouvelle_col:
                    if "-" in intervalle_c:
                        try:
                            index_insertion_c = int(intervalle_c.split("-")[0])
                            df_actuel.insert(index_insertion_c, nom_nouvelle_col, "")
                            st.session_state[cle_unique] = df_actuel
                            st.rerun()
                        except Exception:
                            st.error("Format ou position invalide.")
                    else:
                        df_actuel[nom_nouvelle_col] = ""
                        st.session_state[cle_unique] = df_actuel
                        st.rerun()

        with c_del_c:
            col_a_suppr = st.text_input("Nom col. à supprimer", key=f"inv_del_c_{cle_unique}", placeholder="Ex: Superficie")
            if st.button("❌ Supprimer la Colonne", key=f"btn_del_c_{cle_unique}", width="stretch"):
                if col_a_suppr in df_actuel.columns:
                    df_actuel = df_actuel.drop(columns=[col_a_suppr])
                    st.session_state[cle_unique] = df_actuel
                    st.rerun()

    st.markdown("---")

    donnees_modifiees = st.data_editor(
        st.session_state[cle_unique],
        key=f"editeur_{cle_unique}",
        width="stretch",
        num_rows="dynamic",
        height=hauteur
    )
    st.session_state[cle_unique] = donnees_modifiees
    return donnees_modifiees


def creer_champ_palpable_universel_streamlit(libelle, cle_unique_page):
    """ Version Streamlit sécurisée pour la persistance globale. """
    cle_memoire = f"{cle_unique_page}_{libelle}"
    
    valeur_initiale = st.session_state.get(cle_memoire, "")
    if valeur_initiale == "" and "leila_memoire_tampon" in st.session_state:
        valeur_initiale = st.session_state.leila_memoire_tampon.get(cle_memoire, "")

    valeur_saisie = st.text_input(
        label=f"📝 {libelle} :",
        value=str(valeur_initiale),
        key=cle_memoire
    )
    
    st.session_state[cle_memoire] = valeur_saisie
    st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border:0; border-top:1px solid #bdbdbd;'>", unsafe_allow_html=True)
    return valeur_saisie

def afficher():
    st.subheader("Module PDC 2")
# ==========================================================
# 4. FONCTIONS DE DESSIN DES PAGES (Contenu réel intégré)
# ==========================================================
def dessiner_page_accueil():
    st.markdown("<h1 style='text-align: center; color: #1d8348;'>BIENVENUE SUR LAYLA AGRI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1d8348;'>Logiciel de Gestion PDC ARS 1000</h3>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("""
    <div style='text-align: center; font-size: 18px;'>
        Cet outil vous accompagne dans le diagnostic technique<br>
        et la planification des exploitations certifiées.
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("COMMENCER L'IDENTIFICATION", use_container_width=True, type="primary"):
        st.session_state.page_actuelle = 0
        st.rerun()
    st.markdown("---")
    st.caption("© 2026 - Développé par Djè Akadjé - Projet Master Agro-Biodiversité")

def dessiner_page_0_identification():
    import time  # Assure-toi que l'import est bien présent
    
    st.subheader("📝 FICHE D'IDENTIFICATION DU RECENSEUR")
    
    # 1. Utilisation de clés uniques et stables liées à la page 0
    val_nom = st.session_state.get("P0_nom", "")
    val_village = st.session_state.get("P0_village", "")
    val_tel = st.session_state.get("P0_tel", "")
    val_role = st.session_state.get("P0_role", "")
    
    # Si c'est vide dans la session active, on regarde dans le tampon de Leila
    if "leila_memoire_tampon" in st.session_state:
        if not val_nom: val_nom = st.session_state.leila_memoire_tampon.get("P0_nom", "")
        if not val_village: val_village = st.session_state.leila_memoire_tampon.get("P0_village", "")
        if not val_tel: val_tel = st.session_state.leila_memoire_tampon.get("P0_tel", "")
        if not val_role: val_role = st.session_state.leila_memoire_tampon.get("P0_role", "")

    # 2. Rendu des champs avec sauvegarde en temps réel via la 'key'
    nom = st.text_input("Nom & Prénoms :", value=str(val_nom), key="P0_nom")
    village = st.text_input("Village / Localité :", value=str(val_village), key="P0_village")
    tel = st.text_input("Téléphone :", value=str(val_tel), key="P0_tel")
    role = st.text_input("Fonction / Rôle :", value=str(val_role), key="P0_role")
    
    st.write("")
    
    # 3. Bouton unique de validation et de transition (Plus propre et évite les doubles clics)
    if st.button("Valider et commencer le PDC ➡️", type="primary", use_container_width=True):
        if nom.strip() == "":
            st.warning("⚠️ Veuillez entrer au moins votre nom pour continuer.")
        else:
            # Structuration pour ton ancienne variable ou compatibilité
            st.session_state.infos_producteur = {
                "nom": nom, 
                "village": village, 
                "tel": tel, 
                "role": role
            }   
            
            # --- LE TRIPLE VERROU DE SÉCURITÉ DE LEILA IA ---
            
            # 1. Sauvegarde via ton tracker centralisé
            leila_tracker_central()
            
            # 2. COCHAGE DE LA CASE MÉMOIRE POUR TOUTE L'APPLICATION (PAGE 0 VALIDÉE)
            st.session_state["page_0_validee"] = True  
            
            # Feedback visuel pour l'utilisateur de la SCOOP
            st.success(f"✅ Identité enregistrée pour : {nom}")
            time.sleep(0.4) # Petite pause fluide
            
            # 3. Changement de page propre vers la Page 1 (Schéma de Certification)
            st.session_state.page_actuelle = 1
            st.rerun()


import streamlit as st

def dessiner_page_1_Schema_Certification():
    import time  # 🟢 SÉCURITÉ 1 : Import local pour éviter le plantage du sleep
    
    # --- 1. STYLE CSS EXCLUSIF ET SÉCURISÉ POUR LA PAGE 1 ---
    st.markdown("""
    <style>
    /* Labels des étapes du schéma */
    .step-label-p1 {
        border-radius: 8px; 
        padding: 15px; 
        text-align: center; 
        font-weight: bold;
        font-family: 'Calibri', 'Arial', sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .lbl-engagement { background-color: #D5F5E3; border: 2px solid #27AE60; color: #196F3D; }
    .lbl-diagnostic { background-color: #FCF3CF; border: 2px solid #F39C12; color: #7E5109; }
    .lbl-execution { background-color: #EBF5FB; border: 2px solid #2980B9; color: #1B4F72; }
    .lbl-audit { background-color: #FDEDEC; border: 2px solid #C0392B; color: #641E16; }

    /* Blocs de description */
    .step-desc-p1 {
        background-color: #F8F9F9; 
        border-right: 1px solid #E0E0E0;
        border-top: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 12px; 
        margin-left: 10px; 
        border-radius: 0 4px 4px 0;
    }
    .desc-engagement { border-left: 5px solid #27AE60; }
    .desc-diagnostic { border-left: 5px solid #F39C12; }
    .desc-execution { border-left: 5px solid #2980B9; }
    .desc-audit { border-left: 5px solid #C0392B; }

    .step-desc-p1 span {
        color: black !important;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 14px;
    }

    /* Flèches de transition */
    .arrow-separator-p1 {
        text-align: center; 
        font-size: 24px; 
        margin: 8px 0;
    }

    /* Numérotation de page style PowerPoint fixe */
    .footer-page-p1 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 2.2. LE SCHÉMA DE CERTIFICATION")
    st.write("---")
    
    # --- BLOC 1 : ENGAGEMENT ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-engagement">👉 ENGAGEMENT</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-engagement">
                <span>🔹 <b>Adhésion du producteur :</b> Signature de la charte d'engagement et respect du règlement intérieur du groupe.</span><br>
                <span>🔹 <b>Sensibilisation :</b> Information sur les exigences de la norme ARS 1000 et les principes de durabilité.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="arrow-separator-p1" style="color: #27AE60;">⬇️</div>', unsafe_allow_html=True)

    # --- BLOC 2 : DIAGNOSTIC ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-diagnostic">🔍 DIAGNOSTIC</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-diagnostic">
                <span>🔹 <b>Évaluation initiale :</b> Réalisation du Plan de Développement du Producteur (PDC) pour identifier les écarts.</span><br>
                <span>🔹 <b>Cartographie :</b> Délimitation des parcelles et géolocalisation pour exclure les zones de déforestation.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="arrow-separator-p1" style="color: #F39C12;">⬇️</div>', unsafe_allow_html=True)

    # --- BLOC 3 : MISE EN ŒUVRE ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-execution">🚀 MISE EN ŒUVRE</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-execution">
                <span>🔹 <b>Application des Bonnes Pratiques :</b> Pratiques agricoles, environnementales et sociales conformes à la norme.</span><br>
                <span>🔹 <b>Formations continues :</b> Renforcement des capacités du producteur sur la gestion des sols, intrants et agroforesterie.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="arrow-separator-p1" style="color: #2980B9;">⬇️</div>', unsafe_allow_html=True)

    # --- BLOC 4 : CONTRÔLE ET AUDIT ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-audit">📋 AUDIT & SUIVI</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-audit">
                <span>🔹 <b>Contrôle Interne :</b> Inspections régulières par l'équipe technique de la coopérative pour valider les progrès.</span><br>
                <span>🔹 <b>Audit Externe :</b> Évaluation finale par un organisme de certification indépendant pour l'obtention du certificat.</span>
            </div>
            """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # --- BOUTON DE NAVIGATION ET VALIDATION GLOBALE ---
    if st.button("Valider et passer à l'étape suivante ➡️", type="primary", use_container_width=True):
        # 1. On coche la case mémoire de cette page
        st.session_state["page_1_validee"] = True  
        
        # 2. 🟢 SÉCURITÉ 2 : Correction de la faute sur locals() et appel sécurisé
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            try:
                leila_tracker_central()
            except Exception:
                pass
                
        # 3. Message de succès et redirection
        st.success("✅ Schéma de certification validé.")
        time.sleep(0.4)
        
        # 4. Changement de page vers la Page 2
        st.session_state.page_actuelle = 2
        st.rerun()

    st.write("---")
    st.warning("**Note de conformité :** Le passage d'une étape à l'autre est conditionné par la validation des critères critiques de l'étape précédente.")
    
    # 🟢 SÉCURITÉ 3 : Numérotation PowerPoint officielle en bas à droite
    st.markdown('<div class="footer-page-p1">1</div>', unsafe_allow_html=True)



def dessiner_page_2_Exigences_Suite():
    import time # Sécurité import local
    
    st.subheader("📌 Exigences de la Norme (Suite)")
    st.markdown("<span style='color: #2e86c1; font-weight: bold;'>Le producteur doit démontrer :</span>", unsafe_allow_html=True)
    st.markdown("""
    1. Une gestion durable des ressources naturelles.
    2. Le respect des droits humains et sociaux :
        - *a. Interdiction du travail des enfants.*
        - *b. Conditions de travail décentes.*
    3. La transparence dans les transactions commerciales.
    """)
    
    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p2", type="primary", use_container_width=True):
        st.session_state["page_2_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Exigences validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 3
        st.rerun()

    # Numérotation de page PowerPoint
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>9</span>", unsafe_allow_html=True)
    st.caption("Page 2 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_3_Exigences_Norme():
    import time
    
    st.subheader("📋 Critères de Conformité")
    points = [
        "Traçabilité totale du produit.",
        "Protection des zones forestières et de la biodiversité.",
        "Usage raisonné des produits phytosanitaires.",
        "Maintien de la fertilité des sols."
    ]
    for p in points:
        st.write(f"✅ {p}")
        
    st.warning("**Note :** Toute non-conformité majeure entraîne l'exclusion du programme.")
    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p3", type="primary", use_container_width=True):
        st.session_state["page_3_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Critères de conformité validés.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 4
        st.rerun()

    # Numérotation de page PowerPoint
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>10</span>", unsafe_allow_html=True)
    st.caption("Page 3 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_4_Exigences_Fin():
    import time
    
    # Style de l'entête de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 10px; margin-bottom: 25px;'>
        <h2 style='color: #2E86C1; margin: 0; font-size: 22px; text-transform: uppercase;'>
            1.2 EXIGENCES DE LA NORME RELATIVES AU PDC
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Conteneur principal pour les points 5 et 6 (Sécurité couleur texte pour l'exécutable)
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.7; margin-left: 10px; color: black;'>
        <p><b style='color: black;'>5. Le PDC doit être révisé et mis à jour au moins une fois par an pour refléter les progrès réalisés et les changements de situation.</b></p>
        <p><b style='color: black;'>6. Les enregistrements des activités réalisées et des données collectées dans le cadre du PDC doivent être conservés pendant au moins 5 ans.</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p4", type="primary", use_container_width=True):
        st.session_state["page_4_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Exigences de conservation validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 5
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>11</span>", unsafe_allow_html=True)
    st.caption("Page 4 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_5_Etapes_Elaboration():
    import time
    
    # Style de l'entête de section principale
    st.markdown("""
    <div style='background-color: #E8F8F5; border-left: 6px solid #117A65; padding: 12px; margin-bottom: 10px;'>
        <h2 style='color: #117A65; margin: 0; font-size: 24px; font-weight: bold;'>
            II. MISE EN ŒUVRE DU PLAN DE DÉVELOPPEMENT DE LA CACAOYÈRE (PDC)
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Style du sous-titre de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 8px; margin-bottom: 25px;'>
        <h3 style='color: #2E86C1; margin: 0; font-size: 20px; text-transform: uppercase; font-weight: bold;'>
            2.1 ÉTAPES D'ÉLABORATION DU PDC
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Liste des 4 étapes d'élaboration avec sécurité de couleur CSS
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.8; margin-left: 15px; color: black;'>
        <p><b style='color: black;'>1. Réalisation du diagnostic initial</b> de la cacaoyère (évaluation des écarts par rapport à la norme).</p>
        <p><b style='color: black;'>2. Définition des objectifs</b> du producteur (à court, moyen et long terme).</p>
        <p><b style='color: black;'>3. Planification des activités</b> et des investissements nécessaires pour atteindre les objectifs.</p>
        <p><b style='color: black;'>4. Validation et signature</b> du PDC par le producteur et l'entité reconnue (coopérative).</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p5", type="primary", use_container_width=True):
        st.session_state["page_5_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 6
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>12</span>", unsafe_allow_html=True)
    st.caption("Page 5 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_6_Diagnostic_Initial():
    import time
    
    # Style du sous-titre de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 8px; margin-bottom: 25px;'>
        <h3 style='color: #2E86C1; margin: 0; font-size: 20px; text-transform: uppercase; font-weight: bold;'>
            2.1 ÉTAPES D'ÉLABORATION DU PDC
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Titre de l'étape en cours
    st.markdown("""
    <p style='font-size: 20px; font-weight: bold; color: #117A65; margin-left: 10px; margin-bottom: 20px;'>
        1. Le diagnostic initial doit permettre d'évaluer :
    </p>
    """, unsafe_allow_html=True)

    # Liste des 4 points d'évaluation avec couleur stabilisée
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.8; margin-left: 40px; color: black;'>
        <p style='color: black;'>– Les caractéristiques de la cacaoyère (superficie, âge, densité, etc.) ;</p>
        <p style='color: black;'>– Les pratiques agricoles actuelles du producteur ;</p>
        <p style='color: black;'>– Les aspects environnementaux (présence d'arbres d'ombrage, zones protégées) ;</p>
        <p style='color: black;'>– Les aspects sociaux (conditions de travail, logement, non-travail des enfants).</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p6", type="primary", use_container_width=True):
        st.session_state["page_6_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Éléments du diagnostic initial validés.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 7
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>13</span>", unsafe_allow_html=True)
    st.caption("Page 6 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_7_Definition_Objectifs():
    import time
    
    # Style du sous-titre de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 8px; margin-bottom: 25px;'>
        <h3 style='color: #2E86C1; margin: 0; font-size: 20px; text-transform: uppercase; font-weight: bold;'>
            2.1 ÉTAPES D'ÉLABORATION DU PDC
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Titre de l'étape en cours
    st.markdown("""
    <p style='font-size: 20px; font-weight: bold; color: #117A65; margin-left: 10px; margin-bottom: 20px;'>
        2. La définition des objectifs doit être faite à court, moyen et long terme :
    </p>
    """, unsafe_allow_html=True)

    # Liste des 3 horizons d'objectifs
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.8; margin-left: 40px; color: black;'>
        <p style='color: black;'>– Court terme (1 an) : actions immédiates (taille, fertilisation, etc.) ;</p>
        <p style='color: black;'>– Moyen terme (2-3 ans) : actions progressives (ombrage, replantation, etc.) ;</p>
        <p style='color: black;'>– Long terme (4-5 ans et plus) : vision globale (renouvellement complet, diversification).</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p7", type="primary", use_container_width=True):
        st.session_state["page_7_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Horizons d'objectifs validés.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 8 # En route vers la Page 8 !
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>14</span>", unsafe_allow_html=True)
    st.caption("Page 7 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_8_Socio_Demographiques():
    import time   # 🟢 SÉCURITÉ : Imports locaux requis pour l'exécutable
    import pandas as pd
    
    # --- STYLE CSS REPRODUCTION PRESTIGE DIAPO ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-8 {
        background-color: #E2F0D9; /* Vert clair institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .titre-8 {
        color: #1F4E78; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .soustitre-8 {
        color: black;
        font-size: 16px;
        font-style: italic;
        margin-top: 5px;
    }

    .alert-layla-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .alert-layla-ok {
        background-color: #E2F0D9;
        color: #385723;
        border-left: 6px solid #385723;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE (Conforme à PAGE 8.jpg) ---
    st.markdown("""
    <div class="diapo-slide-8">
        <div class="titre-8">A - Données Socio-démographiques (fiche1)</div>
        <div class="soustitre-8">
            • Les personnes vivant dans le ménage, (ii) les actifs familiaux,<br>
            • La scolarisation des enfants, (iv) les travailleurs permanents et non permanents
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- INITIALISATION DE LA MÉMOIRE DE SAISIE (Ménage) ---
    if "membres_menage" not in st.session_state:
        st.session_state.membres_menage = [
            {"Nom et prénoms": "", "Statut Famille": "1. Chef de ménage", "Statut Plantation": "2. Propriétaire", "Statut Scolaire": "1. Scolarisé", "Contact": "", "Année de naissance": 1980, "Sexe": "M", "Niveau d'instruction": "3. Primaire", "Catégorie ethnique": "1. Autochtone"}
        ]

    # --- EN-TÊTE DE GESTION DES MEMBRES ---
    st.markdown("### 👥 Saisie des membres du ménage (Poupée Russe)")
    st.caption("Déployez chaque boîte pour configurer un membre du ménage. Layla IA analysera le tableau en temps réel.")

    # Boutons d'action pour la liste dynamique
    col_btn1, col_btn2 = st.columns([0.2, 0.8])
    with col_btn1:
        if st.button("➕ Ajouter un membre", key="btn_add_m", use_container_width=True):
            st.session_state.membres_menage.append(
                {"Nom et prénoms": "", "Statut Famille": "3. Enfant", "Statut Plantation": "1. Aucun", "Statut Scolaire": "1. Scolarisé", "Contact": "", "Année de naissance": 2012, "Sexe": "F", "Niveau d'instruction": "1. Aucun", "Catégorie ethnique": "1. Autochtone"}
            )
            if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
                leila_tracker_central()
            st.rerun()
            
    with col_btn2:
        if len(st.session_state.membres_menage) > 1:
            if st.button("❌ Supprimer le dernier membre", key="btn_del_m", type="secondary"):
                st.session_state.membres_menage.pop()
                if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
                    leila_tracker_central()
                st.rerun()

    # --- EXPANDERS IMBRIQUÉS ---
    opts_famille = ["1. Chef de ménage", "2. Conjoint", "3. Enfant", "4. Autre (Préciser)"]
    opts_plant = ["1. Aucun", "2. Propriétaire", "3. Gérant", "4. MO permanent", "5. MO Temporaire"]
    opts_scol = ["1. Scolarisé", "2. Déscolarisé"]
    opts_inst = ["1. Aucun", "2. Préscolaire", "3. Primaire", "4. Secondaire", "5. Supérieur", "6. Autres (préciser)"]
    opts_eth = ["1. Autochtone", "2. Allochtone", "3. Allogène"]

    for i, membre in enumerate(st.session_state.membres_menage):
        nom_affiche = membre['Nom et prénoms'] if membre['Nom et prénoms'] else 'Non renseigné'
        label_expander = f"👤 Membre #{i+1} : {nom_affiche} ({membre['Statut Famille']})"
        
        with st.expander(label_expander, expanded=(i == len(st.session_state.membres_menage)-1)):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.membres_menage[i]["Nom et prénoms"] = st.text_input(
                    f"Nom et prénoms #{i+1}", 
                    value=str(membre["Nom et prénoms"]), 
                    key=f"p8_nom_{i}"
                )
                st.session_state.membres_menage[i]["Statut Famille"] = st.selectbox(
                    f"Statut/Famille (lien de parenté) #{i+1}",
                    opts_famille,
                    index=opts_famille.index(membre["Statut Famille"]) if membre["Statut Famille"] in opts_famille else 0,
                    key=f"p8_famille_{i}"
                )
                st.session_state.membres_menage[i]["Statut Plantation"] = st.selectbox(
                    f"Statut/Plantation #{i+1}",
                    opts_plant,
                    index=opts_plant.index(membre["Statut Plantation"]) if membre["Statut Plantation"] in opts_plant else 0,
                    key=f"p8_plant_{i}"
                )
            with c2:
                st.session_state.membres_menage[i]["Sexe"] = st.radio(
                    f"Sexe #{i+1}", 
                    ["M", "F"], 
                    index=["M", "F"].index(membre["Sexe"]) if membre["Sexe"] in ["M", "F"] else 0, 
                    horizontal=True, 
                    key=f"p8_sexe_{i}"
                )
                st.session_state.membres_menage[i]["Année de naissance"] = st.number_input(
                    f"Année de naissance #{i+1}", 
                    min_value=1930, 
                    max_value=2026, 
                    value=int(membre["Année de naissance"]), 
                    key=f"p8_naiss_{i}"
                )
                st.session_state.membres_menage[i]["Contact"] = st.text_input(
                    f"Contact (Téléphone) #{i+1}", 
                    value=str(membre["Contact"]), 
                    key=f"p8_contact_{i}"
                )
            with c3:
                st.session_state.membres_menage[i]["Statut Scolaire"] = st.selectbox(
                    f"Statut Scolaire #{i+1}",
                    opts_scol,
                    index=opts_scol.index(membre["Statut Scolaire"]) if membre["Statut Scolaire"] in opts_scol else 0,
                    key=f"p8_scol_{i}"
                )
                st.session_state.membres_menage[i]["Niveau d'instruction"] = st.selectbox(
                    f"Niveau d'instruction #{i+1}",
                    opts_inst,
                    index=opts_inst.index(membre["Niveau d'instruction"]) if membre["Niveau d'instruction"] in opts_inst else 0,
                    key=f"p8_inst_{i}"
                )
                st.session_state.membres_menage[i]["Catégorie ethnique"] = st.selectbox(
                    f"Catégorie ethnique #{i+1}",
                    opts_eth,
                    index=opts_eth.index(membre["Catégorie ethnique"]) if membre["Catégorie ethnique"] in opts_eth else 0,
                    key=f"p8_eth_{i}"
                )

    if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
        leila_tracker_central()

    # --- AFFICHAGE DU TABLEAU SYNTHÈSE ---
    st.write("---")
    st.markdown("### 📋 Tableau Récapitulatif de la Fiche 1")
    df_menage = pd.DataFrame(st.session_state.membres_menage)
    st.dataframe(df_menage, use_container_width=True)

    # --- MOTEUR DE DIAGNOSTIC AUTOMATIQUE ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Diagnostic Social Automatique par Layla IA")
    
    annee_actuelle = 2026
    alertes_decouvertes = []
    cas_travail_enfants = False
    cas_discrimination_genre = False
    cas_travail_force = False

    total_femmes = len(df_menage[df_menage["Sexe"] == "F"])
    femmes_proprio_ou_gerant = len(df_menage[(df_menage["Sexe"] == "F") & (df_menage["Statut Plantation"].isin(["2. Propriétaire", "3. Gérant"]))])
    chefs_de_menage_femme = len(df_menage[(df_menage["Sexe"] == "F") & (df_menage["Statut Famille"] == "1. Chef de ménage")])

    for index, row in df_menage.iterrows():
        age = annee_actuelle - int(row["Année de naissance"]) if row["Année de naissance"] else 0
        nom_complet = row["Nom et prénoms"] if row["Nom et prénoms"] else f"Membre #{index+1}"

        if age < 15 and row["Statut Plantation"] in ["4. MO permanent", "5. MO Temporaire"]:
            cas_travail_enfants = True
            alertes_decouvertes.append(f"🚨 **Travail des Enfants** : {nom_complet} a {age} ans et est enregistré comme Main d'œuvre ({row['Statut Plantation']}). C'est strictement interdit par la norme.")
        
        if 6 <= age <= 16 and row["Statut Scolaire"] == "2. Déscolarisé":
            alertes_decouvertes.append(f"⚠️ **Alerte Scolarisation** : Enfant en âge d'obligation scolaire ({nom_complet}, {age} ans) est marqué comme Déscolarisé.")

        if row["Statut Plantation"] == "4. MO permanent" and not row["Contact"]:
            cas_travail_force = True
            alertes_decouvertes.append(f"🚨 **Suspicion de Travail Forcé / Vulnérabilité** : Le travailleur permanent {nom_complet} n'a aucun contact téléphonique renseigné. Risque d'isolement ou de non-contractualisation.")

    if total_femmes > 0 and femmes_proprio_ou_gerant == 0 and chefs_de_menage_femme == 0:
        cas_discrimination_genre = True
        alertes_decouvertes.append("⚠️ **Risque d'Inéquité de Genre** : Aucune femme du ménage ne possède de statut de décision (Propriétaire/Gérant) malgré leur présence active au sein de l'exploitation.")

    # Injection propre des diagnostics globaux dans la session
    st.session_state["p8_travail_enfants_detecte"] = cas_travail_enfants
    st.session_state["p8_discrimination_genre_detecte"] = cas_discrimination_genre
    st.session_state["p8_travail_force_detecte"] = cas_travail_force
    st.session_state["p8_fiche_complete"] = True

    if alertes_decouvertes:
        for alerte in alertes_decouvertes:
            st.markdown(f'<div class="alert-layla-danger">{alerte}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-layla-ok">✅ Analyse Layla IA : Aucune non-conformité sociale (Discrimination, genre, travail forcé ou travail des enfants) détectée sur cette fiche.</div>', unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # 🟢 AJOUT : Bouton de validation et navigation pour la Page 8
    if st.button("Valider la Fiche Sociale et Continuer ➡️", key="btn_p8_nav", type="primary", use_container_width=True):
        st.session_state["page_8_validee"] = True
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Données socio-démographiques validées avec succès.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 9
        st.rerun()

    # Numérotation en bas à droite
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>20</span>", unsafe_allow_html=True)
    st.caption("Page 8 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_9_Description_exploitation():
    import time  # 🟢 SÉCURITÉ : Import local pour le sleep
    
    st.markdown("""
    <style>
    .stApp {
        background-color: #E8F8F5;
    }
    .main-title-p9 {
        color: #1F618D;
        font-size: 26px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 30px;
        margin-left: 20px;
    }
    .custom-bullet-list-p9 {
        font-size: 19px;
        color: black; /* 🟢 FIX : Forcer le texte en noir pour la clarté dans l'exécutable */
        line-height: 1.8;
        margin-left: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Titre principal exact de la fiche 2
    st.markdown('<div class="main-title-p9">B - Description de l\'exploitation (fiche2)</div>', unsafe_allow_html=True)

    # 2. Liste à puces avec balises span pour assurer la couleur du texte
    st.markdown("""
    <div class="custom-bullet-list-p9">
        <span style='color: black;'>o &nbsp; Les informations sur la plantation de cacao,</span><br>
        <span style='color: black;'>o &nbsp; les superficies des autres cultures,</span><br>
        <span style='color: black;'>o &nbsp; la taille des autres spéculations (production animale, production halieutique, etc.),</span><br>
        <span style='color: black;'>o &nbsp; les terres disponibles,</span><br>
        <span style='color: black;'>o &nbsp; les outils de travail et équipements de production disponibles sur l'exploitation,</span><br>
        <span style='color: black;'>o &nbsp; la situation des arbres autres que le cacaoyer dans la cacaoyère.</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)

    # 🟢 AJOUT : Bouton de validation et navigation pour la Page 9
    if st.button("Ouvrir la fiche de description de l'exploitation ➡️", key="btn_p9_nav", type="primary", use_container_width=True):
        st.session_state["page_9_validee"] = True
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        time.sleep(0.2)
        st.session_state.page_actuelle = 10  # En route vers le premier formulaire de la Fiche 2 !
        st.rerun()

    # 3. Numéro de page exact en bas à droite (21)
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>21</span>", unsafe_allow_html=True)

    st.caption("Page 9 - Système Expert Leila (Norme ARS 1000)")



# Sécurité si la fonction globale n'est pas encore déclarée ailleurs
if "leila_tracker_central" not in globals():
    def leila_tracker_central():
        pass

def afficher():
    st.subheader("Module PDC 10")
# ==========================================================
# 5. MOTEURS D'AIGUILLAGE & CONTENU CENTRAL
# ==========================================================
def afficher_contenu():
    if st.session_state.page_actuelle == -1:
        st.title("🌿 Bienvenue sur LAYLA IA")
        st.subheader("Système Expert de Diagnostic Agricole")
        st.info(f"Utilisateur : Djè Akadjé | Date : {datetime.datetime.now().strftime('%d/%m/%Y')}")
        
        if st.button("Lancer le diagnostic"):
            st.session_state.page_actuelle = 0
            st.rerun()
    else:
        st.write(f"### Interface de saisie - Page {st.session_state.page_actuelle}")
        afficher_contenu_pdc()

def afficher_contenu_pdc():
    leila_tracker_central()
    n_page = st.session_state.page_actuelle
    pid = f"P{n_page}"

    # Configuration par défaut simulée pour injecter dans tes fonctions paramétrées (conf)
    mock_conf = {
        "titre": "Section Courante", "sous_titre": "Sous-section", "titre_epargne": "Suivi Épargne",
        "titre_production": "Historique Production", "titre_autres": "Autres revenus",
        "titre_depenses": "Dépenses d'Exploitation", "depenses_data": [["Entretien", "Annuel", 0]],
        "titre_main_oeuvre": "Main d'œuvre", "main_oeuvre_cols": ["Type", "Coût"],
        "decisions": ["Replantation globale", "Remplacement partiel", "Conservation"],
        "donnees": [["Exemple", "", ""]], "colonnes": ["Critère", "Statut", "Note"],
        "fiche_reference": "Ref-ARS1000", "description": "Description de section",
        "elements_requis": ["Indicateur 1", "Indicateur 2"], "etapes": ["Étape A", "Étape B"],
        "activite_label": "Détails Financiers", "champs": ["ID National", "Code Coopérative"],
        "lignes": ["Cacao", "Café", "Vivrier", "Autres"]
    }

    pages_map = {
        -1: dessiner_page_accueil,
        0:  dessiner_page_0_identification,
        1:  dessiner_page_1_Schema_Certification,
        2:  dessiner_page_2_Exigences_Suite,
        3:  dessiner_page_3_Exigences_Norme,
        4:  dessiner_page_4_Exigences_Fin,
        5:  dessiner_page_5_Etapes_Elaboration,
        6:  dessiner_page_6_Diagnostic_Initial,
        7:  dessiner_page_7_Definition_Objectifs,
        8:  dessiner_page_8_Socio_Demographiques,
        9:  dessiner_page_9_Description_exploitation,
        10: dessiner_page_10_Donnees_sur_les_cultures,
        11: dessiner_page_11_Materiel_Equipement,
        12: dessiner_page_12_Situation_Arbres_Forestiers,
        13: dessiner_page_13_Donnees_Agronomiques,
        14: dessiner_page_14_Determination_Densite,
        15: dessiner_page_15_Degradation_Arbres,
        16: dessiner_page_16_Etat_Cacaoyere_Strict,
        17: dessiner_page_17_Etat_Du_Sol_Strict,
        18: dessiner_page_18_post_recolte,
        19: dessiner_page_19_intrants,
        20: dessiner_page_20_socio_economique,
        21: dessiner_page_21_Finance_Production,
        22: dessiner_page_22_Depenses_Et_Main_Doeuvre,
        23: dessiner_page_23_Analyse_Des_Problemes,
        24: dessiner_page_24_Grille_Decision,
        25: dessiner_page_25_Analyse_Problemes,
        26: dessiner_page_26_Validation_Producteur,
        27: dessiner_page_27_Planification_Activites,
        28: dessiner_page_28_Planification_Des_Activites_Suite,
        29: dessiner_page_29_Calendrier_Activites,
        30: dessiner_page_30_Methodologie_Calendrier,
        31: dessiner_page_31_Programme_Annuel_Activites,
        32: dessiner_page_32_Determination_Moyens_Couts,
        33: dessiner_page_33_Moyens_Globaux_Couts,
        34: dessiner_page_34_Tableau_Moyens_Couts,
        35: dessiner_page_35_Orientations_Pratiques,
        36: dessiner_page_36_Mise_En_Oeuvre_Evaluation,
        37: dessiner_page_37_Cycle_Vie_PDC,
        38: dessiner_page_38_Structuration_PDC,
        39: dessiner_page_39_Identification_Producteur,
        40: dessiner_page_40_Situation_Epargne,
        41: dessiner_page_41_Situation_Main_Oeuvre,
        42: dessiner_page_42_Description_Exploitation,
        43: dessiner_page_43_Croquis_Polygone_Parcelle,
        44: dessiner_page_44_Cultures,
        45: dessiner_page_45_Situation_Arbres_Forestiers,
        46: dessiner_page_46_Verification_Materiel,
        47: dessiner_page_47_Planification_Strategique_Poupees_Russes,
        48: dessiner_page_48_Programme_Annuel_et_Facteurs,
        49: dessiner_page_49_Bilan_Global_Conformite_Decision,
    }

    dessiner_func = pages_map.get(n_page)
    if dessiner_func:
        dessiner_func()

    progression = max(0, min((n_page + 1) / 50, 1.0))
    st.sidebar.markdown("---")
    st.sidebar.write(f"Progression du PDC : {int(progression * 100)}%")
    st.sidebar.progress(progression)

def moteur_de_navigation(n_page_externe=None):
    pages_disponibles = {
        "Accueil": -1, "P0 - Identification": 0, "P1 - Schéma Certification": 1,
        "P2 - Exigences Suite": 2, "P3 - Exigences Norme": 3, "P4 - Titre Partie 2": 4,
        "P5 - Définition PDC": 5, "P6 - Caractéristiques": 6, "P7 - Introduction Collecte": 7,
        "P8 - Socio_Demographiques": 8, "P9 - Description Exploitation": 9, "P10 - Données Cultures": 10,
        "P11 - Materiel_Equipement": 11, "P12 - Situation_Arbres_Forestiers": 12, "P13 - Donnees_Agronomiques": 13,
        "P14 - Determination_Densite": 14, "P15 - Degradation_Arbres": 15, "P16 - Etat_Cacaoyere_Strict": 16,
        "P17 - Etat_Du_Sol_Strict": 17, "P18 - Post-Récolte": 18, "P19 - Intrants & Emballages": 19,
        "P20 - socio_economique": 20, "P21 - Finance Production": 21, "P22 - Charges Exploitation": 22,
        "P23 - Analyse Problèmes": 23, "P24 - Grille de Décision": 24, "P25 - Analyse Approfondie": 25,
        "P26 - Validation_Producteur": 26, "P27 - Planification_Activites": 27, "P28 - Planification_Activites_Suite": 28,
        "P29 - Calendrier_Activites": 29, "P30 - Méthode Calendrier": 30, "P31 - Programme Annuel": 31,
        "P32 - Détermination Moyens": 32, "P33 - Moyens_Globaux_Couts": 33, "P34 - Tableau Coûts Détails": 34,
        "P35 - Orientations_Pratiques": 35, "P36 - Mise_En_Oeuvre_Evaluation": 36, "P37 - Cycle_Vie_PDC": 37,
        "P38 - Structuration_PDC": 38, "P39 - Identification Producteur": 39, "P40 - Situation Épargne": 40,
        "P41 - Main d'Œuvre": 41, "P42 - Description_Exploitation": 42, "P43 - Croquis_Polygone_Parcelle": 43,
        "P44 - Inventaire Cultures": 44, "P45 - Situation_Arbres_Forestiers": 45, "P46 - Verification_Materiel": 46,
        "P47 - Planification 5 Ans": 47, "P48 - Programme Annuel (PDC)": 48, "P49 - Bilan_Global_Conformite_Decision": 49
    }

    st.sidebar.title("🌿 Navigation Layla")
    liste_noms = list(pages_disponibles.keys())
    liste_valeurs = list(pages_disponibles.values())
    index_actuel = liste_valeurs.index(st.session_state.page_actuelle) if st.session_state.page_actuelle in liste_valeurs else 0
    
    selection = st.sidebar.selectbox("Aller à la page :", liste_noms, index=index_actuel)
    n_page = pages_disponibles[selection]
    
    if n_page != st.session_state.page_actuelle:
        st.session_state.page_actuelle = n_page
        st.rerun()

# ==========================================================
# 6. CONFIGURATION VISUELLE & SIDEBAR
# ==========================================================
import streamlit as st
import pandas as pd

# 1. Définition de la fonction de style manquante
def appliquer_style_layla():
    """Applique le style CSS personnalisé pour le module LAYLA."""
    st.markdown("""
        <style>
        .stApp {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-title {
            color: #2E7D32;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# 2. Fonction facultative pour la synthèse vocale (sécurité si non définie)
def parler(texte):
    pass

# 3. Fonction pour la navigation de page (sécurité si non définie)
def moteur_de_navigation(page):
    pass

# ==========================================================
# FONCTION PRINCIPALE DU MODULE PDC 10
# ==========================================================
def afficher():
    # Initialisations requises du session_state
    if "page_actuelle" not in st.session_state:
        st.session_state.page_actuelle = 10
    if "donnees_pdc" not in st.session_state:
        st.session_state.donnees_pdc = {}

    # Application du style visuel
    appliquer_style_layla()

    # Barre latérale (Sidebar)
    with st.sidebar:
        try:
            st.image("logo_layla.png", width=150)
        except Exception:
            st.header("LAYLA IA")
        
        st.write("📍 **ZONE : Soubré**")
        st.divider()
        
        page_mode = st.radio(
            "NAVIGATION PDC 10",
            ["🏠 Accueil", "📄 GESTION PDC (ARS 1000)", "📊 STATISTIQUES", "⚙️ CONFIGURATION"],
            key="radio_pdc10"
        )
        st.info("Ingénieur Djè Akadjé")

    # Moteur de navigation
    moteur_de_navigation(st.session_state.page_actuelle)

    # Contenu principal
    if page_mode == "📄 GESTION PDC (ARS 1000)":
        st.title("📄 Système de Gestion PDC (ARS 1000)")
        
        st.subheader(f"DOCUMENT ARS 1000 - PAGE {st.session_state.page_actuelle}")

        cle_table = f"table_p{st.session_state.page_actuelle}"
        if cle_table not in st.session_state.donnees_pdc:
            df_init = pd.DataFrame([["", ""]], columns=["Description", "Valeur"])
            st.session_state.donnees_pdc[cle_table] = df_init

        edited_df = st.data_editor(
            st.session_state.donnees_pdc[cle_table],
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_p{st.session_state.page_actuelle}"
        )
        st.session_state.donnees_pdc[cle_table] = edited_df

        if st.button("💾 Synchroniser et Préparer PDF", key="btn_sync_pdc10"):
            st.success("Données synchronisées. Prêt pour l'export.")
            parler("Données synchronisées. Je prépare le document officiel.")


import streamlit as st
import pandas as pd

# ==========================================================
# FONCTIONS UTILITAIRES & LOGIQUE INTERNE
# ==========================================================
def initialiser_etats():
    """Initialise les variables globales de session si elles n'existent pas encore."""
    if "page_actuelle" not in st.session_state:
        st.session_state.page_actuelle = 1
    if "donnees_pdc" not in st.session_state:
        st.session_state.donnees_pdc = {}

def afficher_contenu():
    """Affiche le contenu principal en fonction de la page actuelle."""
    st.subheader(f"DOCUMENT ARS 1000 - PAGE {st.session_state.page_actuelle} / 49")
    
    cle_table = f"table_p{st.session_state.page_actuelle}"
    if cle_table not in st.session_state.donnees_pdc:
        df_init = pd.DataFrame([["", ""]], columns=["Description", "Valeur"])
        st.session_state.donnees_pdc[cle_table] = df_init

    edited_df = st.data_editor(
        st.session_state.donnees_pdc[cle_table],
        num_rows="dynamic",
        use_container_width=True,
        key=f"editor_p{st.session_state.page_actuelle}"
    )
    st.session_state.donnees_pdc[cle_table] = edited_df

# ==========================================================
# FONCTION PRINCIPALE APPELÉE PAR TABLETTE.PY
# ==========================================================
def afficher():
    # 1. Sécuriser le session_state
    initialiser_etats()
    
    st.title("📄 Système de Gestion PDC (ARS 1000) - PDC 10")

    # 2. Exécution du corps de la page
    afficher_contenu()

    # 3. Barre de navigation inférieure
    st.divider()
    col_prev, col_page, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️ Précédent", use_container_width=True, disabled=(st.session_state.page_actuelle <= 1), key="nav_prev_pdc10"): 
            st.session_state.page_actuelle -= 1
            st.rerun()

    with col_page:
        st.markdown(f"<h3 style='text-align: center; color: #2E7D32;'>📄 PAGE {st.session_state.page_actuelle} / 49</h3>", unsafe_allow_html=True)

    with col_next:
        if st.button("Suivant ➡️", use_container_width=True, disabled=(st.session_state.page_actuelle >= 49), key="nav_next_pdc10"):
            st.session_state.page_actuelle += 1
            st.rerun()
