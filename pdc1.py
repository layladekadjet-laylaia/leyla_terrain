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
    if "leila_memoire_tampon" not in st.session_state:
        st.session_state.leila_memoire_tampon = {}

    cles_a_ignorer = ["leila_memoire_tampon", "page_actuelle", "logs", "editor_"]

    for cle, valeur_actuelle in list(st.session_state.items()):
        if any(ignore in cle for ignore in cles_a_ignorer) or callable(valeur_actuelle):
            continue

        ancienne_valeur = st.session_state.leila_memoire_tampon.get(cle, None)

        if ancienne_valeur is not None:
            # 1. Traitement spécifique si l'un des deux objets est un DataFrame
            is_actuelle_df = isinstance(valeur_actuelle, pd.DataFrame)
            is_ancienne_df = isinstance(ancienne_valeur, pd.DataFrame)

            if is_actuelle_df or is_ancienne_df:
                if is_actuelle_df and is_ancienne_df:
                    if not ancienne_valeur.equals(valeur_actuelle):
                        memoriser_marche(f"Le tableau élastique [{cle}] a été mis à jour.")
                else:
                    memoriser_marche(f"La structure de [{cle}] a changé de format.")
            
            # 2. Traitement pour tous les autres types de données (listes, str, int, float, dict)
            else:
                try:
                    if ancienne_valeur != valeur_actuelle:
                        if isinstance(valeur_actuelle, list) and cle == "arbres_inventoriez":
                            memoriser_marche(f"L'inventaire global [{cle}] a été mis à jour.")
                        else:
                            memoriser_marche(f"Le champ [{cle}] a changé : '{ancienne_valeur}' ➡️ '{valeur_actuelle}'")
                except Exception:
                    pass

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


def dessiner_page_10_Donnees_sur_les_cultures():
    # --- STYLE CSS REPRODUCTION PRESTIGE DIAPO ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-10 {
        background-color: #E2F0D9; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .titre-10 {
        color: #1F4E78; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .alert-layla-agro-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-warning {
        background-color: #FFF2CC;
        color: #B25E00;
        border-left: 6px solid #FFC000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-ok {
        background-color: #E2F0D9;
        color: #385723;
        border-left: 6px solid #385723;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-10">
        <div class="titre-10">• Données sur les cultures & Statut Réglementaire</div>
    </div>
    """, unsafe_allow_html=True)

    # --- DICTIONNAIRE DES VARIÉTÉS (Triées par ordre de couleur, des meilleures aux moins bonnes) ---
    dict_varietes = {
        "Cacao": ["CNRA (Mercedes)", "Tout-Venant"],
        "Hévéa": ["IRCA 41", "IRCA 18", "GT 1"],
        "P. à huile": ["Tenera", "Dura", "Pisifera"],
        "Vivrier": ["Banane Corne", "Manioc Sika", "Maïs Blanc"],
        "Autres cultures": ["Café Robustat", "Anacarde Recrut"]
    }

    # --- INITIALISATION DE LA MÉMOIRE GLOBALE ---
    if "parcelles_cultures" not in st.session_state:
        st.session_state.parcelles_cultures = [
            {
                "Culture": "Cacao", 
                "Nom Parcelle": "Parcelle 1", 
                "Superficie (ha)": 2.5, 
                "Année de création": 2015, 
                "Précédent cultural": "Forêt secondaire", 
                "Origine matériel végétal": "CNRA (Mercedes)", 
                "En production": "OUI",
                "Zone Classée": "NON (Déclaration)",
                "Proche Aire Protégée": "NON",
                "Litige Foncier": "NON"
            }
        ]

    # Initialisation des flags de session pour la page 49
    st.session_state["p10_has_declared_infraction"] = False
    st.session_state["p10_risques_deforestation"] = False
    st.session_state["p10_alerte_hcv_suspendu"] = False
    st.session_state["p10_agroforesterie_naturelle_active"] = False

    # --- GESTION DYNAMIQUE DES PARCELLES ---
    st.markdown("### 🗺️ Recensement et Intégrité des Parcelles")
    st.caption("Renseignez les données physiques et le questionnaire d'intégrité foncière pour chaque parcelle.")

    col_btn1, col_btn2 = st.columns([0.2, 0.8])
    with col_btn1:
        if st.button("➕ Ajouter une parcelle", use_container_width=True):
            st.session_state.parcelles_cultures.append(
                {
                    "Culture": "Cacao", 
                    "Nom Parcelle": f"Parcelle {len(st.session_state.parcelles_cultures)+1}", 
                    "Superficie (ha)": 1.0, 
                    "Année de création": 2021, 
                    "Précédent cultural": "Jachère", 
                    "Origine matériel végétal": "CNRA (Mercedes)", 
                    "En production": "OUI",
                    "Zone Classée": "NON (Déclaration)",
                    "Proche Aire Protégée": "NON",
                    "Litige Foncier": "NON"
                }
            )
            leila_tracker_central()
            st.rerun()
            
    with col_btn2:
        if len(st.session_state.parcelles_cultures) > 1:
            if st.button("❌ Supprimer la dernière parcelle"):
                st.session_state.parcelles_cultures.pop()
                leila_tracker_central()
                st.rerun()

    opts_cultures = ["Cacao", "Hévéa", "P. à huile", "Vivrier", "Autres cultures"]
    opts_zone = ["NON (Déclaration)", "OUI (Infiltration)"]
    opts_choix = ["NON", "OUI"]

    # --- SYSTÈME DE FORMULAIRE PERSISTANT ---
    for i, parcelle in enumerate(st.session_state.parcelles_cultures):
        label_expander = f"🌳 {parcelle['Culture']} — {parcelle['Nom Parcelle']} | Précédent: {parcelle['Précédent cultural']} ({parcelle['Année de création']})"
        
        with st.expander(label_expander, expanded=(i == len(st.session_state.parcelles_cultures)-1)):
            st.markdown("##### 📍 1. Caractéristiques Agronomiques")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                culture_actuelle = st.selectbox(
                    f"Type de Culture #{i+1}", 
                    opts_cultures,
                    index=opts_cultures.index(parcelle["Culture"]) if parcelle["Culture"] in opts_cultures else 0, 
                    key=f"p10_type_cult_{i}"
                )
                st.session_state.parcelles_cultures[i]["Culture"] = culture_actuelle
                
                st.session_state.parcelles_cultures[i]["Nom Parcelle"] = st.text_input(
                    f"Nom de la parcelle #{i+1}", 
                    value=str(parcelle["Nom Parcelle"]), 
                    key=f"p10_nom_parc_{i}"
                )
                
            with c2:
                st.session_state.parcelles_cultures[i]["Superficie (ha)"] = st.number_input(
                    f"Superficie (ha) #{i+1}", 
                    min_value=0.1, 
                    value=float(parcelle["Superficie (ha)"]), 
                    step=0.1, 
                    key=f"p10_sup_{i}"
                )
                
                st.session_state.parcelles_cultures[i]["Année de création"] = st.number_input(
                    f"Année #{i+1}", 
                    min_value=1960, 
                    max_value=2026, 
                    value=int(parcelle["Année de création"]), 
                    key=f"p10_annee_crea_{i}"
                )
                
            with c3:
                st.session_state.parcelles_cultures[i]["Précédent cultural"] = st.text_input(
                    f"Précédent cultural #{i+1} (Ex: Forêt primaire, sous bois, jachère)", 
                    value=str(parcelle["Précédent cultural"]), 
                    key=f"p10_prec_{i}"
                )
                
                liste_varietes = dict_varietes.get(culture_actuelle, ["CNRA"])
                st.session_state.parcelles_cultures[i]["Origine matériel végétal"] = st.selectbox(
                    f"Origine matériel végétal #{i+1}",
                    liste_varietes,
                    index=liste_varietes.index(parcelle["Origine matériel végétal"]) if parcelle["Origine matériel végétal"] in liste_varietes else 0,
                    key=f"p10_mat_veg_{i}"
                )
                
                st.session_state.parcelles_cultures[i]["En production"] = st.radio(
                    f"En production ? #{i+1}", 
                    opts_choix, 
                    index=opts_choix.index(parcelle["En production"]) if parcelle["En production"] in opts_choix else 0, 
                    horizontal=True, 
                    key=f"p10_prod_{i}"
                )

            st.markdown("##### ⚖️ 2. Questionnaire de Vulnérabilité (Déclaration du Producteur)")
            cq1, cq2, cq3 = st.columns(3)
            with cq1:
                st.session_state.parcelles_cultures[i]["Zone Classée"] = st.selectbox(
                    f"La parcelle est-elle située dans une Forêt Classée / Zone interdite ? #{i+1}",
                    opts_zone,
                    index=opts_zone.index(parcelle["Zone Classée"]) if parcelle["Zone Classée"] in opts_zone else 0,
                    key=f"p10_zc_{i}"
                )
            with cq2:
                st.session_state.parcelles_cultures[i]["Proche Aire Protégée"] = st.selectbox(
                    f"La parcelle est-elle limitrophe d'un Parc National / Réserve ? #{i+1}",
                    opts_choix,
                    index=opts_choix.index(parcelle["Proche Aire Protégée"]) if parcelle["Proche Aire Protégée"] in opts_choix else 0,
                    key=f"p10_ap_{i}"
                )
            with cq3:
                st.session_state.parcelles_cultures[i]["Litige Foncier"] = st.selectbox(
                    f"Existe-t-il un litige foncier ou une contestation ? #{i+1}",
                    opts_choix,
                    index=opts_choix.index(parcelle["Litige Foncier"]) if parcelle["Litige Foncier"] in opts_choix else 0,
                    key=f"p10_lf_{i}"
                )

    leila_tracker_central()

    # --- TABLEAU RECAPITULATIF ---
    st.write("---")
    st.markdown("### 📋 Récapitulatif Enregistré")
    df_cultures = pd.DataFrame(st.session_state.parcelles_cultures)
    st.dataframe(df_cultures, use_container_width=True)

    # --- MOTEUR DE DIAGNOSTIC CENTRALISÉ ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Diagnostic de Conformité Intégré par Layla IA")
    
    alertes_danger = []
    alertes_warning = []
    
    has_declared_infraction = False
    has_deforestation_risk = False
    has_hcv_suspendu = False
    has_agro_naturelle = False
    
    for index, row in df_cultures.iterrows():
        nom_complet_parcelle = f"{row['Culture']} ({row['Nom Parcelle']})"
        precedent = str(row["Précédent cultural"]).lower().strip()
        annee = int(row["Année de création"]) if row["Année de création"] else 2026
        
        # Admin / Foncier
        if row["Zone Classée"] == "OUI (Infiltration)":
            has_declared_infraction = True
            alertes_danger.append(f"🚨 **Aveu de Non-Conformité Majeure** : La parcelle **{nom_complet_parcelle}** est déclarée infiltrée en Forêt Classée par l'exploitant.")
        
        if row["Litige Foncier"] == "OUI":
            alertes_warning.append(f"⚠️ **Alerte Foncier** : Conflit ou litige en cours sur la parcelle **{nom_complet_parcelle}** (Axe Social/Légal ARS 1000).")
            
        if row["Proche Aire Protégée"] == "OUI":
            alertes_warning.append(f"⚠️ **Zone Tampon Critique** : La parcelle **{nom_complet_parcelle}** est limitrophe d'une Aire Protégée. Surveillance GPS renforcée requise.")

        # EUDR & Haute Valeur de Conservation
        if "sous ombrage" in precedent or "sous forêt" in precedent or "nettoy" in precedent:
            if annee > 2020:
                has_deforestation_risk = True
                alertes_danger.append(
                    f"🚨 **DÉGRADATION FORESTIÈRE (Règlement UE - EUDR)** : La parcelle **{nom_complet_parcelle}** "
                    f"a été établie en **{annee}** par modification du sous-bois d'une forêt primaire. L'UE interdit "
                    f"toute dégradation de forêt primaire après le 31/12/2020."
                )
            else:
                has_agro_naturelle = True
                alertes_warning.append(
                    f"⚡ **AGROFORESTERIE TRADITIONNELLE** : La parcelle **{nom_complet_parcelle}** ({annee}) "
                    f"préserve la voûte d'origine. Conformité historique validée (avant 2020)."
                )
                
        elif "primaire" in precedent:
            if annee > 2020:
                has_deforestation_risk = True
                alertes_danger.append(
                    f"🚨 **CRITIQUE - DÉFORESTATION** : La parcelle **{nom_complet_parcelle}** "
                    f"indique la destruction d'une forêt primaire en **{annee}**. Non-conformité absolue (EUDR / RA)."
                )
            else:
                has_hcv_suspendu = True
                alertes_warning.append(
                    f"⚠️ **HAUTE VALEUR DE CONSERVATION (HCV)** : La parcelle **{nom_complet_parcelle}** créée en **{annee}** "
                    f"sur forêt primaire exige un plan de remédiation conforme aux critères de l'ARS 1000."
                )

        elif "secondaire" in precedent or "forêt" in precedent:
            if annee > 2020:
                has_deforestation_risk = True
                alertes_danger.append(
                    f"🚨 **DÉFORESTATION RÉCENTE (Règlement UE - EUDR)** : La parcelle **{nom_complet_parcelle}** "
                    f"a été coupée en **{annee}** (après la date butoir du 31/12/2020). Exclusion du marché européen."
                )
            else:
                st.caption(f"ℹ️ *{nom_complet_parcelle}* : Conversion historique antérieure à 2020. Statut conforme.")

    # Synchronisation Session
    st.session_state["p10_data_verification_piège"] = df_cultures
    st.session_state["p10_has_declared_infraction"] = has_declared_infraction
    st.session_state["p10_risques_deforestation"] = has_deforestation_risk
    st.session_state["p10_alerte_hcv_suspendu"] = has_hcv_suspendu
    st.session_state["p10_agroforesterie_naturelle_active"] = has_agro_naturelle

    if not alertes_danger and not alertes_warning:
        st.markdown('<div class="alert-layla-agro-ok">✅ Déclarations valides. Layla IA est en attente des relevés polygonaux GPS pour confirmation.</div>', unsafe_allow_html=True)
    else:
        for alerte in alertes_danger:
            st.markdown(f'<div class="alert-layla-agro-danger">{alerte}</div>', unsafe_allow_html=True)
        for alerte in alertes_warning:
            st.markdown(f'<div class="alert-layla-agro-warning">{alerte}</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p10", type="primary", use_container_width=True):
        st.session_state["page_10_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 11
        st.rerun()


def dessiner_page_11_Materiel_Equipement():
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-11 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-11 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .statut-coherence-11 {
        background-color: #FFF3CD;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #FFC107;
        margin-top: 5px;
        font-size: 13px;
        font-weight: bold;
    }

    .alert-layla-agro-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-warning {
        background-color: #FFF2CC;
        color: #B25E00;
        border-left: 6px solid #FFC000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-ok {
        background-color: #E2F0D9;
        color: #385723;
        border-left: 6px solid #385723;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="diapo-slide-11">
        <div class="bullet-titre-11">• Matériel agricole et équipements de l'exploitation</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗃️ Gestion de l'Inventaire Logistique (Section Page 11)")
    st.caption("Renseignez avec précision le matériel observé sur l'exploitation pour valider la capacité opérationnelle.")

    base_materiels_cacao = {
        "": [""],
        "1. Matériel de traitement phytosanitaire": [
            "", "Pulvérisateur à pression retenue", "Atomiseur à moteur", "Équipement d'injection (Swollen Shoot)", 
            "Appareil de poudrage", "Pulvérisateur à dos mécanique", "Buses de rechange", "Dosette / Éprouvette graduée",
            "Mélangeur de produit", "Fût de préparation", "Kit de nettoyage phytosanitaire"
        ],
        "2. Matériel de taille, coupe et élagage": [
            "", "Machette (Peugette)", "Sécateur à main", "Échenilloir télescopique", "Scie arboricole circum", 
            "Hache d'abattage", "Couteau d'émondage", "Lime de affûtage", "Tronçonneuse d'élagage", "Serpe"
        ],
        "3. Matériel de récolte et post-récolte (Usinage)": [
            "", "Couteau à cacao (Goulette)", "Écabosseur (Bûchette / Masse en bois)", "Bâche de fermentation",
            "Claie de séchage en bambou", "Séchoir solaire surelevé", "Râteau de séchage (Ricle)", "Sacs en jute neufs",
            "Peseuse / Balance à aiguille", "Crible / Tamis à fèves", "Aiguille de couture pour sac"
        ],
        "4. Matériel d'entretien des parcelles (Nettoyage)": [
            "", "Houe", "Daba ivoirienne", "Pelle plate", "Pioche", "Débroussailleuse thermique", 
            "Râteau de nettoyage", "Hache-paille / Broyeur de résidus", "Cordeau de jalonnement", "Gabarit d'espacement (3m x 3m)"
        ],
        "5. Matériel de transport et logistique": [
            "", "Brouette renforcée", "Charrette à traction", "Moto de livraison", "Tricycle de charge (Moto-tri)", 
            "Cuvette plastique de ramassage", "Panier en osier traditionnel", "Pousse-pousse", "Sangle de portage", "Remorque de plantation"
        ],
        "6. Équipements de Protection Individuelle (EPI)": [
            "", "Combinaison imperméable de traitement", "Masque respiratoire à cartouche", "Lunettes de protection", 
            "Gants en nitrile / caoutchouc", "Bottes de sécurité en caoutchouc", "Visière transparente", 
            "Tablier de protection", "Chapeau à large bord", "Trousse de premiers secours", "EPI COMPLET"
        ]
    }

    if "inventaire_materiels_p11" not in st.session_state:
        st.session_state.inventaire_materiels_p11 = [
            {"Type": "", "Designation": "", "Quantite": 0, "Annee": "", "Cout": 0, "Bon": 0, "Acceptable": 0, "Mauvais": 0}
            for _ in range(4)
        ]

    col_btn1, col_btn2 = st.columns([0.25, 0.75])
    with col_btn1:
        if st.button("➕ Ajouter un équipement", use_container_width=True):
            st.session_state.inventaire_materiels_p11.append(
                {"Type": "", "Designation": "", "Quantite": 0, "Annee": "", "Cout": 0, "Bon": 0, "Acceptable": 0, "Mauvais": 0}
            )
            leila_tracker_central()
            st.rerun()
    with col_btn2:
        if len(st.session_state.inventaire_materiels_p11) > 1:
            if st.button("❌ Supprimer le dernier équipement"):
                st.session_state.inventaire_materiels_p11.pop()
                leila_tracker_central()
                st.rerun()

    inventaire_global = []
    liste_types_disponibles = list(base_materiels_cacao.keys())

    for idx, item in enumerate(st.session_state.inventaire_materiels_p11):
        num_affiche = idx + 1
        type_actuel = item["Type"] if item["Type"] != "" else "Non sélectionné"
        desig_actuelle = item["Designation"] if item["Designation"] != "" else "Outil en attente"
        label_expander = f"📦 Équipement N° {num_affiche} : {desig_actuelle} ({type_actuel.split('. ')[-1]})"

        with st.expander(label_expander, expanded=(idx == len(st.session_state.inventaire_materiels_p11) - 1)):
            c1, c2 = st.columns(2)
            with c1:
                idx_type = liste_types_disponibles.index(item["Type"]) if item["Type"] in liste_types_disponibles else 0
                type_mat = st.selectbox(
                    f"Sélectionner le Type de Matériel #{num_affiche}", 
                    liste_types_disponibles, 
                    index=idx_type,
                    key=f"p11_type_mat_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Type"] = type_mat
                
            with c2:
                liste_desig_filtree = base_materiels_cacao.get(type_mat, [""])
                idx_desig = liste_desig_filtree.index(item["Designation"]) if item["Designation"] in liste_desig_filtree else 0
                desig_mat = st.selectbox(
                    f"Désignation précise de l'outil #{num_affiche}", 
                    liste_desig_filtree, 
                    index=idx_desig,
                    key=f"p11_desig_mat_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Designation"] = desig_mat

            c3, c4, c5 = st.columns([1.5, 1.5, 2])
            with c3:
                quantite = st.number_input(
                    f"Quantité Totale constatée #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Quantite"]), 
                    key=f"p11_qty_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Quantite"] = quantite
            with c4:
                annee = st.text_input(
                    f"Année d'acquisition #{num_affiche}", 
                    value=str(item["Annee"]), 
                    placeholder="Ex: 2024", 
                    key=f"p11_annee_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Annee"] = annee
            with c5:
                cout = st.number_input(
                    f"Coût total d'achat (FCFA) #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Cout"]), 
                    step=5000, 
                    key=f"p11_cout_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Cout"] = cout

            st.markdown("**🔍 Répartition de l'état du matériel :**")
            col_b, col_a, col_m = st.columns(3)
            with col_b:
                bon = st.number_input(
                    f"Nombre en Bon état #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Bon"]), 
                    key=f"p11_bon_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Bon"] = bon
            with col_a:
                acceptable = st.number_input(
                    f"Nombre en état Acceptable #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Acceptable"]), 
                    key=f"p11_acc_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Acceptable"] = acceptable
            with col_m:
                mauvais = st.number_input(
                    f"Nombre en Mauvais état #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Mauvais"]), 
                    key=f"p11_mauv_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Mauvais"] = mauvais

            somme_etats = bon + acceptable + mauvais
            if quantite > 0 and somme_etats != quantite:
                st.markdown(f"""
                <div class="statut-coherence-11">
                    ⚠️ <b>Alerte Saisie Leila :</b> La somme des états ({bon} Bon + {acceptable} Acceptable + {mauvais} Mauvais = <b>{somme_etats}</b>) 
                    ne correspond pas à la quantité totale déclarée (<b>{quantite}</b>).
                </div>
                """, unsafe_allow_html=True)

            if type_mat != "" and desig_mat != "" and quantite > 0:
                inventaire_global.append({
                    "N°": num_affiche,
                    "Type de matériel": type_mat,
                    "Désignation de l'outil": desig_mat,
                    "Quantité totale": quantite,
                    "Année d'acquisition": annee,
                    "Coût d'achat (FCFA)": cout,
                    "Bon": bon,
                    "Acceptable": acceptable,
                    "Mauvais": mauvais
                })

    st.write("---")
    st.markdown("### 📊 Grand Tableau d'Évaluation Logistique (Page 11)")
    
    alertes_danger = []
    alertes_warning = []
    
    has_phytosanitaire = False
    has_epi_complet = False
    total_epi_masques = 0
    total_pulverisateurs = 0

    if inventaire_global:
        df_global_mat = pd.DataFrame(inventaire_global)
        st.dataframe(df_global_mat.set_index("N°"), use_container_width=True)
        
        total_outils = df_global_mat["Quantité totale"].sum()
        total_investissement = df_global_mat["Coût d'achat (FCFA)"].sum()
        total_en_panne = df_global_mat["Mauvais"].sum()
        
        for index, row in df_global_mat.iterrows():
            t_mat = row["Type de matériel"]
            d_out = row["Désignation de l'outil"]
            qty = row["Quantité totale"]
            
            if "phytosanitaire" in t_mat.lower():
                has_phytosanitaire = True
                total_pulverisateurs += qty
                
            if "protection individuelle" in t_mat.lower() or "epi" in t_mat.lower():
                if "epi complet" in d_out.lower() or "masque" in d_out.lower() or "combinaison" in d_out.lower():
                    has_epi_complet = True
                    total_epi_masques += qty

        # Règles de croisement
        if has_phytosanitaire and not has_epi_complet:
            alertes_danger.append(
                "🚨 **CRITIQUE NORMES SOCIALES (ARS 1000)** : L'exploitation dispose d'appareils phytosanitaires "
                "mais aucun Équipement de Protection Individuelle (EPI) adéquat n'est répertorié. Risque d'intoxication sévère."
            )
        elif has_phytosanitaire and has_epi_complet:
            if total_epi_masques < total_pulverisateurs:
                alertes_warning.append(
                    f"⚠️ **Alerte Risque d'Exposition** : Le nombre d'EPI ({total_epi_masques}) "
                    f"est inférieur au nombre d'appareils applicateurs utilisables simultanément ({total_pulverisateurs})."
                )
            else:
                st.caption("✨ *Sécurité Travail* : Ratios de protection individuelle validés réglementairement.")

        if total_outils > 0 and (total_en_panne / total_outils) > 0.30:
            alertes_warning.append(
                f"⚠️ **Alerte Maintenance Élevée** : Plus de 30% du parc matériel de l'exploitation est en mauvais état "
                f"({total_en_panne} outils défectueux)."
            )

        # Métriques
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric("Outils fonctionnels recensés", total_outils)
        with c_m2:
            st.metric("Capital matériel investi", f"{total_investissement:,} FCFA")
        with c_m3:
            st.metric("Outils défectueux", total_en_panne, delta=f"-{total_en_panne}" if total_en_panne > 0 else "0", delta_color="inverse")
    else:
        st.info("Aucun outil configuré dans le tableau récapitulatif.")

    # Sauvegardes d'états
    st.session_state["p11_inventaire_materiel"] = inventaire_global
    st.session_state["p11_has_phytosanitaire_sans_epi"] = (has_phytosanitaire and not has_epi_complet)
    st.session_state["p11_alertes_danger"] = alertes_danger
    st.session_state["p11_alertes_warning"] = alertes_warning
    st.session_state["p11_is_conforme"] = len(alertes_danger) == 0

    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Analyse de la Capacité Opérationnelle par Layla IA")
    if alertes_danger or alertes_warning:
        for alerte in alertes_danger:
            st.markdown(f'<div class="alert-layla-agro-danger">{alerte}</div>', unsafe_allow_html=True)
        for alerte in alertes_warning:
            st.markdown(f'<div class="alert-layla-agro-warning">{alerte}</div>', unsafe_allow_html=True)
    elif inventaire_global:
        st.markdown('<div class="alert-layla-agro-ok">✅ Analyse Layla IA : Le ratio équipement/EPI est équilibré. Les outils essentiels à la plantation sont fonctionnels.</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p11", type="primary", use_container_width=True):
        st.session_state["page_11_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 12
        st.rerun()

    # Indication stricte de la pagination
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>11</span>", unsafe_allow_html=True)



def dessiner_page_12_Situation_Arbres_Forestiers():
    # --- STYLE CSS REPRODUCTION & INTELLIGENCE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-12 {
        background-color: #C6E0B4; /* Vert clair institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-12 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-recommande { background-color: #28A745; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-tolere { background-color: #FFC107; color: black; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-deconseille { background-color: #DC3545; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-alerte { background-color: #FD7E14; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }

    .bloc-conclusion-conforme { background-color: #D4EDDA; border: 2px solid #28A745; color: #155724; padding: 15px; border-radius: 6px; font-weight: bold; margin-top: 20px; }
    .bloc-conclusion-alerte { background-color: #F8D7DA; border: 2px solid #DC3545; color: #721C24; padding: 15px; border-radius: 6px; font-weight: bold; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BASE DE DONNÉES EXPERTE DES 50 ARBRES ---
    base_arbres_experts = {
        "": ["", "Toléré"],
        "Aboudikro": ["Entandrophragma cylindricum", "Recommandé"],
        "Acajou d'Afrique": ["Khaya ivorensis", "Recommandé"],
        "Ahun (Akoua)": ["Alstonia boonei", "Toléré"],
        "Aiélé": ["Canarium schweinfurthii", "Toléré"],
        "Ako": ["Antiaris toxicaria", "Déconseillé"],
        "Akpi": ["Ricinodendron heudelotii", "Recommandé"],
        "Alové": ["Aningeria robusta", "Toléré"],
        "Assaméla": ["Pericopsis elata", "Recommandé"],
        "Avodiré": ["Turraeanthus africanus", "Toléré"],
        "Azobé": ["Lophira alata", "Toléré"],
        "Badi": ["Nauclea diderrichii", "Toléré"],
        "Bété": ["Mansonia altissima", "Toléré"],
        "Bilinga": ["Nauclea diderrichii", "Toléré"],
        "Bossé clair": ["Guarea cedrata", "Recommandé"],
        "Cèdre d'Afrique": ["Lovoa trichilioides", "Recommandé"],
        "Dabéma": ["Piptadeniastrum africanum", "Toléré"],
        "Dali": ["Tarrietia utilis", "Toléré"],
        "Dibétou": ["Lovoa trichilioides", "Recommandé"],
        "Doussié": ["Afzelia africana", "Recommandé"],
        "Ebène": ["Diospyros crassiflora", "Toléré"],
        "Framiré": ["Terminalia ivorensis", "Recommandé"],
        "Fraqué": ["Terminalia superba", "Recommandé"],
        "Fromager": ["Ceiba pentandra", "Déconseillé"],
        "Iroko": ["Milicia excelsa", "Recommandé"],
        "Kapokier": ["Bombax buonopozense", "Déconseillé"],
        "Kondroti": ["Rhodognaphalon brevicuspe", "Toléré"],
        "Kosso": ["Pterocarpus erinaceus", "Recommandé"],
        "Kotibé": ["Nesogordonia papaverifera", "Toléré"],
        "Koto": ["Pterygota bequaertii", "Toléré"],
        "Lingue": ["Afzelia bipindensis", "Recommandé"],
        "Lotofa": ["Sterculia rhinopetala", "Déconseillé"],
        "Makoré": ["Tieghemella heckelii", "Recommandé"],
        "Moabi": ["Baillonella toxisperma", "Toléré"],
        "Movingui": ["Distemonanthus benthamianus", "Toléré"],
        "Niangon": ["Heritiera utilis", "Toléré"],
        "Oboto": ["Mammea africana", "Toléré"],
        "Obié": ["Triplochiton scleroxylon", "Toléré"],
        "Okoala": ["Sacoglottis gabonensis", "Toléré"],
        "Olona": ["Adansonia digitata", "Déconseillé"],
        "Onzabili": ["Antrocaryon klaineanum", "Toléré"],
        "Ozigo": ["Dacryodes buettneri", "Toléré"],
        "Padouk": ["Pterocarpus soyauxii", "Recommandé"],
        "Rônier": ["Borassus aethiopium", "Toléré"],
        "Samba": ["Triplochiton scleroxylon", "Toléré"],
        "Sapelli": ["Entandrophragma utile", "Recommandé"],
        "Sipo": ["Entandrophragma utile", "Recommandé"],
        "Tali": ["Erythrophleum ivorense", "Toléré"],
        "Tiama": ["Entandrophragma angolense", "Recommandé"],
        "Wengé": ["Millettia laurentii" , "Recommandé"]
    }

    # --- STRUCTURE INTERFACE DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-12">
        <div class="bullet-titre-12">• Situation des arbres autres que le cacaoyer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗂️ Configuration de l'Inventaire Forestier (Section Page 12)")
    st.caption("Cette section permet de consigner l'état de l'ombrage et la diversité des essences forestières compagnes de la parcelle.")
    
    # Sélection du nombre total d'arbres
    nb_arbres_max = st.number_input("Nombre d'arbres identifiés sur la parcelle :", min_value=1, max_value=50, value=3, key="nb_arbres_p12")

    arbres_saisis = []

    # Génération dynamique des tiroirs
    for idx in range(1, int(nb_arbres_max) + 1):
        nom_session_key = f"local_p12_{idx}"
        
        # Valeurs d'exemples initiales intelligentes adaptées à la Côte d'Ivoire
        if nom_session_key not in st.session_state:
            if idx == 1: st.session_state[nom_session_key] = "Akpi"
            elif idx == 2: st.session_state[nom_session_key] = "Fraqué"
            elif idx == 3: st.session_state[nom_session_key] = "Fromager"
            else: st.session_state[nom_session_key] = ""

        arbre_titre = st.session_state[nom_session_key] if st.session_state[nom_session_key] != "" else "Non configuré"

        with st.expander(f"🌲 Emplacement & Caractéristiques - Arbre N° {idx} : {arbre_titre}"):
            
            # --- LIGNE 1 : Les Identifiants de l'arbre ---
            c1, c2, c3 = st.columns([2, 2, 1.5])
            with c1:
                liste_local = list(base_arbres_experts.keys())
                val_actuelle = st.session_state[nom_session_key]
                idx_default = liste_local.index(val_actuelle) if val_actuelle in liste_local else 0
                
                nom_local = st.selectbox(f"Nom Local #{idx}", liste_local, key=f"sel_nom_{idx}", index=idx_default)
                st.session_state[nom_session_key] = nom_local # Mise à jour de la clé maîtresse
                
            with c2:
                nom_botanique = base_arbres_experts[nom_local][0] if nom_local != "" else ""
                st.text_input(f"Nom Botanique #{idx}", value=nom_botanique, key=f"bot_p12_{idx}", disabled=True)
                
            with c3:
                def_circ = 200 if idx==1 else (70 if idx==2 else 212)
                circonference = st.number_input(f"Circonférence (cm) #{idx}", min_value=0, value=def_circ if nom_local != "" else 0, key=f"circ_p12_{idx}")

            # --- LIGNE 2 : Les Coordonnées Géographiques ---
            c_lat, c_lon, c_orig = st.columns([2, 2, 2])
            with c_lat:
                def_lat = 6.020668 if idx==1 else (6.020664 if idx==2 else 6.020614)
                latitude = st.text_input(f"Latitude #{idx}", value=str(def_lat) if nom_local != "" else "", key=f"lat_p12_{idx}", placeholder="Ex: 6.020668")
            with c_lon:
                def_lon = -4.357123 if idx==1 else (-4.356949 if idx==2 else -4.356929)
                longitude = st.text_input(f"Longitude #{idx}", value=str(def_lon) if nom_local != "" else "", key=f"lon_p12_{idx}", placeholder="Ex: -4.357123")
            with c_orig:
                origine = st.selectbox(f"Origine de l'arbre #{idx}", ["Préservé", "Planté"], key=f"orig_p12_{idx}")

            # --- LIGNE 3 : Usages, Avantages et Décisions ---
            c_av, c_us, c_dec, c_rais = st.columns([2, 2, 2, 2])
            with c_av:
                avantages = st.selectbox(f"Avantages cacaoyer #{idx}", ["Ombrage", "Fertilité du sol", "Protection érosion", "Brise-vent", "Lutte enherbement", "Aucun"], key=f"av_p12_{idx}", index=0 if idx==1 else (4 if idx==2 else 0))
            with c_us:
                usage = st.selectbox(f"Usage de l'arbre #{idx}", ["Bois d'œuvre", "Alimentaire", "Médicinale", "Bois de chauffage", "Protection"], key=f"us_p12_{idx}")
            with c_dec:
                decision = st.selectbox(f"Décision Norme #{idx}", ["A maintenir", "A éliminer"], key=f"dec_p12_{idx}", index=1 if idx==2 else 0)
            with c_rais:
                def_raison = "il y a 2 trop près" if idx==1 else ("Situé à 1,5 m d'un autre" if idx==2 else "")
                raison = st.text_input(f"Raison / Motif technique #{idx}", value=def_raison, key=f"rais_p12_{idx}")

            # --- INTERPRÉTATION INTELLIGENTE DE LEILA IA ---
            compatibilite_finale = "Toléré"
            if nom_local != "":
                statut_botanique = base_arbres_experts[nom_local][1]
                
                if decision == "A éliminer" and statut_botanique == "Recommandé":
                    st.markdown(f"**Avis de Leila :** <span class='badge-alerte'>⚠️ Arbitrage de terrain</span> — L'essence *{nom_local}* est agronomiquement excellente pour le cacao, mais votre décision d'éliminer est validée car motivée par l'espacement (*'{raison}'*). Attention à ne pas sur-éclaircir cette zone.", unsafe_allow_html=True)
                    compatibilite_finale = "Recommandé (Éliminé par contrainte d'espace)"
                
                elif decision == "A éliminer" and statut_botanique == "Déconseillé":
                    st.markdown(f"**Avis de Leila :** <span class='badge-recommande'>👍 Décision approuvée</span> — Correct. Le *{nom_local}* doit être éliminé car il présente un risque pour la plantation (hôte potentiel du Swollen Shoot ou concurrence linéaire).", unsafe_allow_html=True)
                    compatibilite_finale = "Déconseillé"
                
                elif statut_botanique == "Recommandé":
                    st.markdown(f"**Avis de Leila :** <span class='badge-recommande'>👍 Recommandé pour le cacao</span> (Excellent pour la durabilité)", unsafe_allow_html=True)
                    compatibilite_finale = "Recommandé"
                elif statut_botanique == "Toléré":
                    st.markdown(f"**Avis de Leila :** <span class='badge-tolere'>🫳 Toléré</span> (Pas d'effet négatif majeur constaté)", unsafe_allow_html=True)
                    compatibilite_finale = "Toléré"
                else:
                    st.markdown(f"**Avis de Leila :** <span class='badge-deconseille'>⚠️ Déconseillé</span> (Risque sanitaire / Réservoir potentiel Swollen Shoot)", unsafe_allow_html=True)
                    compatibilite_finale = "Déconseillé"

                arbres_saisis.append({
                    "N°": idx,
                    "Nom Local": nom_local,
                    "Nom Botanique": nom_botanique,
                    "Circonférence (cm)": circonference,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Origine": origine,
                    "Avantages": avantages,
                    "Usage": usage,
                    "Décision Norme": decision,
                    "Compatibilité Cacao": compatibilite_finale,
                    "Raison": raison
                })

    st.write("---")

    # --- AFFICHAGE DU GRAND TABLEAU RÉCAPITULATIF ---
    st.markdown("### 📊 Grand Tableau Récapitulatif de la Parcelle")
    if arbres_saisis:
        df_global = pd.DataFrame(arbres_saisis)
        colonnes_ordonnees = ["N°", "Nom Local", "Nom Botanique", "Circonférence (cm)", "Latitude", "Longitude", "Origine", "Avantages", "Usage", "Décision Norme", "Compatibilité Cacao", "Raison"]
        df_global = df_global.reindex(columns=colonnes_ordonnees)
        st.dataframe(df_global.set_index("N°"), use_container_width=True)
    else:
        st.info("Aucun arbre configuré pour le moment.")

    # Sauvegarde dans le session_state pour exploitation ultérieure
    st.session_state["p12_inventaire_forestier"] = arbres_saisis

    # --- CONCLUSION DE LEILA SUR LA CONFORMITÉ ---
    st.markdown("### ⚖️ Conclusion de l'Expert Leila sur la Conformité Agroforestière")
    st.markdown("**NOTE :** Analyse de conformité réglementaire de l'ombrage selon les critères durables.")

    if arbres_saisis:
        total_maintenus = sum(1 for a in arbres_saisis if a["Décision Norme"] == "A maintenir")

        if total_maintenus < 2:
            st.markdown(f"""
            <div class="bloc-conclusion-alerte">
                ⚠️ PARCELLE NON CONFORME (Sous-densité d'ombrage)<br>
                <span style='font-weight:normal; font-size:14px;'>
                    Leila constate un manque d'arbres d'ombrage préservés au sein de cette section (seulement {total_maintenus} maintenu(s)). Même si certaines éliminations s'expliquent par des contraintes d'espace (arbres trop serrés), le périmètre global requiert une meilleure couverture forestière pour atténuer les stress thermiques. 
                    <br>💡 <i>Conseil de Leila : Stabilisez le déboisement technique et planifiez l'introduction de nouvelles essences recommandées (comme l'Akpi ou l'Acajou) bien espacées pour atteindre l'équilibre agronomique idéal.</i>
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bloc-conclusion-conforme">
                ✅ PARCELLE CONFORME (Gestion agroforestière intelligente)<br>
                <span style='font-weight:normal; font-size:14px;'>
                    Leila valide le diagnostic ! L'équilibre entre les strates conservées pour l'ombrage protecteur ({total_maintenus} arbres) et les éliminations ciblées témoigne d'une maîtrise technique rigoureuse de la densité de l'espace agroforestier.
                </span>
            </div>
            """, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p12", type="primary", use_container_width=True):
        st.session_state["page_12_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 13
        st.rerun()

    # Numéro de page exact (12)
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>12</span>", unsafe_allow_html=True)


def dessiner_page_13_Donnees_Agronomiques():
    # --- STYLE CSS REPRODUCTION & PRESTIGE AGRONOMIQUE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-13 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-13 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .section-box-p13 { 
        background-color: #F2F4F4; 
        border-left: 5px solid #16A085; 
        padding: 18px; 
        border-radius: 4px; 
        margin-bottom: 20px; 
    }
    
    .bullet-title { font-weight: bold; color: #16A085; font-size: 16px; margin-bottom: 10px; }
    .bullet-text { font-size: 14px; color: #34495E; margin-left: 20px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-13">
        <div class="bullet-titre-13">C - Données Agronomiques (Fiche 3)</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 📐 Évaluation Expérimentale de la Densité des Cacaoyers")
    
    # --- BLOC MÉTHODOLOGIQUE ---
    st.markdown("""
    <div class="section-box-p13">
        <div class="bullet-title">🧠 Méthodologie d'évaluation de la densité (Standards Côte d'Ivoire) :</div>
        <div class="bullet-text">1. Poser <b>4 carrés de densité de 10 m × 10 m</b> sur un hectare.</div>
        <div class="bullet-text">2. Les carrés sont choisis aléatoirement par la <b>méthode des diagonales</b>.</div>
        <div class="bullet-text">3. Dans chaque carré de densité, compter scrupuleusement les arbres productifs et le nombre de tiges.</div>
        <div class="bullet-text">4. <i>Note : Multiplier par 100 le nombre moyen d'arbres par carré pour obtenir la densité moyenne automatique par hectare.</i></div>
    </div>
    """, unsafe_allow_html=True)

    # --- INITIALISATION DE LA GRILLE DANS LE SESSION STATE ---
    if "grille_densite_p13" not in st.session_state:
        st.session_state.grille_densite_p13 = [
            {"Indicateur": "Nombre cacaoyers productifs", "Carré 1": 12, "Carré 2": 11, "Carré 3": 13, "Carré 4": 12},
            {"Indicateur": "Nb moyen de tiges / pied", "Carré 1": 1.0, "Carré 2": 1.1, "Carré 3": 1.0, "Carré 4": 1.2}
        ]

    if "rendement_p13" not in st.session_state:
        st.session_state.rendement_p13 = 450

    # --- AFFICHAGE SAA (Saisie Assistée Interactive) DE LA GRILLE ---
    st.markdown("#### 📊 Grille de comptage des 4 Carrés (100m² chacun)")
    
    # Pour rendre le tableau éditable de manière persistante, on passe par un st.data_editor
    df_grille = pd.DataFrame(st.session_state.grille_densite_p13)
    edited_df = st.data_editor(df_grille, use_container_width=True, key="editor_grille_p13")
    
    # Réinjection immédiate dans la session pour conserver les modifications
    st.session_state.grille_densite_p13 = edited_df.to_dict(orient="records")

    # --- LOGIQUE DE CALCUL AUTOMATIQUE ---
    try:
        prod_row = edited_df[edited_df["Indicateur"] == "Nombre cacaoyers productifs"].iloc[0]
        moyenne_carre = (float(prod_row["Carré 1"]) + float(prod_row["Carré 2"]) + float(prod_row["Carré 3"]) + float(prod_row["Carré 4"])) / 4
        densite_calculee = int(moyenne_carre * 100)
    except Exception:
        densite_calculee = 1200 # Sécurité si mauvaise manipulation de la structure de l'indicateur

    st.metric(label="🌲 Densité Moyenne Estimée Calculée par Leila", value=f"{densite_calculee} pieds / hectare", 
              delta=f"{densite_calculee - 1333} par rapport à l'idéal (1333 pieds/ha)", delta_color="inverse")
    
    # Sauvegarde de la densité calculée
    st.session_state["p13_densite_hectare"] = densite_calculee

    # --- COLLECTE DU RENDEMENT ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("#### 📦 Suivi de la Productivité Commerciale :")
    
    st.number_input(
        "Collecter les données de commercialisation avec le producteur sur au moins la dernière campagne (kg / ha) :",
        min_value=0,
        step=50,
        key="rendement_p13"
    )

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p13", type="primary", use_container_width=True):
        st.session_state["page_13_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 14
        st.rerun()

    # --- NUMÉRO DE PAGE (13) ---
    st.write("<br><br>", unsafe_allow_html=True)
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>13</span>", unsafe_allow_html=True)



def dessiner_page_14_Determination_Densite():
    # --- STYLE CSS STANDARD REPRODUCTION & PRESTIGE LEILA ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-14 {
        background-color: #C6E0B4; /* Vert institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-14 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .formula-box { 
        background-color: #008080; 
        color: white; 
        padding: 22px; 
        border-radius: 8px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        height: 100%; 
    }
    .formula-title { font-weight: bold; font-size: 16px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .canvas-container-p14 { background-color: white; padding: 10px; border-radius: 8px; border: 2px solid #1ABC9C; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    /* Blocs d'informations clairs et scannables */
    .pouperee-level-1 { border-left: 5px solid #1ABC9C; background-color: #F8FBFB; padding: 15px; border-radius: 4px; margin-bottom: 15px; color: black; }
    .pouperee-level-2 { border-left: 5px solid #008080; background-color: #F4FBF9; padding: 15px; border-radius: 4px; margin-bottom: 15px; color: black; }
    .pouperee-level-3 { border-left: 5px solid #E0115F; background-color: #FFF5F7; padding: 15px; border-radius: 4px; color: black; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-14">
        <div class="bullet-titre-14">• Détermination de la densité</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # =========================================================================
    # PARTIE SUPÉRIEURE : RENDER SVG DIRECT & FORMULES MATHÉMATIQUES
    # =========================================================================
    col_gauche, col_droite = st.columns([0.50, 0.50])

    with col_gauche:
        st.markdown("<p style='font-weight:bold; color:#1A252F; margin-bottom:5px;'>Dispositif d'échantillonnage sur la parcelle :</p>", unsafe_allow_html=True)
        
        html_svg_securise = """
        <div class="canvas-container-p14" style="text-align: center;">
            <svg width="100%" height="260" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: auto;">
                <defs>
                    <filter id="shadow_p14" x="-5%" y="-5%" width="110%" height="110%">
                        <feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.15"/>
                    </filter>
                </defs>
                <path d="M 90,40 C 180,20 280,30 310,80 C 340,130 290,200 310,250 C 320,270 260,290 190,275 C 120,260 70,240 65,190 C 60,140 40,70 90,40 Z" fill="#F2FDFB" stroke="#4D79FF" stroke-width="3" filter="url(#shadow_p14)" />
                <line x1="85" y1="45" x2="285" y2="265" stroke="#2C3E50" stroke-width="2.5" />
                <g transform="translate(90, 50) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="-25" y="4" font-size="11" fill="#1A252F" font-weight="bold">C1</text>
                </g>
                <g transform="translate(130, 95) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="-25" y="4" font-size="11" fill="#1A252F">C2</text>
                </g>
                <g transform="translate(175, 145) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="-25" y="4" font-size="11" fill="#1A252F">C3</text>
                </g>
                <g transform="translate(225, 200) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                </g>
                <g transform="translate(265, 245) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="24" y="4" font-size="11" fill="#1A252F" font-weight="bold">Cn</text>
                </g>
                <text x="200" y="285" font-size="12" fill="#7F8C8D" font-weight="bold" text-anchor="middle">Méthode des carrés en diagonale (10m × 10m)</text>
            </svg>
        </div>
        """
        st.markdown(html_svg_securise, unsafe_allow_html=True)

    with col_droite:
        st.markdown("""
        <div class="formula-box">
            <div class="formula-title">🧮 Équations de Densité Étalon</div>
        """, unsafe_allow_html=True)
        st.write(r"$$\text{Moyenne par carré} = \frac{\sum \text{Cacaoyers Comptés}}{n \text{ (Nombre de carrés)}}$$")
        st.write(r"$$\text{Densité Moyenne Extrapolée} = \text{Moyenne} \times 100 \text{ (pieds/ha)}$$")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")

    # =========================================================================
    # CONFIGURATION & PERSISTANCE DU SESSION STATE
    # =========================================================================
    if "p14_nb_carres" not in st.session_state:
        st.session_state.p14_nb_carres = 4  # Standard recommandé en Côte d'Ivoire

    if "p14_valeurs_cacaoyers" not in st.session_state:
        st.session_state.p14_valeurs_cacaoyers = {f"cac_{i}": (12 if i % 2 == 0 else 13) for i in range(20)}
    if "p14_valeurs_tiges" not in st.session_state:
        st.session_state.p14_valeurs_tiges = {f"tig_{i}": 1.1 for i in range(20)}

    # --- ÉTAPE 1 : CONFIGURATION ---
    st.markdown("### 🎛️ ÉTAPE 1 : Configuration & Saisie des Données de Terrain")
    with st.container():
        st.markdown('<div class="pouperee-level-1">', unsafe_allow_html=True)
        
        nb_carres = st.number_input(
            "Nombre de carrés d'observation installés (n) :", 
            min_value=1, max_value=20, 
            value=int(st.session_state.p14_nb_carres), 
            key="nb_carres_p14_root"
        )
        st.session_state.p14_nb_carres = nb_carres
        
        st.markdown("##### 📏 Pieds et tiges comptés par zone carrée :")
        
        cols_saisie = st.columns(int(nb_carres))
        cacaoyers_par_carre = []
        tiges_par_carre = []
        
        for idx in range(int(nb_carres)):
            with cols_saisie[idx]:
                key_cac = f"cac_{idx}"
                key_tig = f"tig_{idx}"
                
                val_cac = st.number_input(
                    f"Cacaoyers C{idx+1}", 
                    min_value=0, 
                    value=st.session_state.p14_valeurs_cacaoyers.get(key_cac, 12),
                    key=f"p14_input_{key_cac}"
                )
                val_tig = st.number_input(
                    f"Tiges/Pied C{idx+1}", 
                    min_value=1.0, max_value=5.0, 
                    value=st.session_state.p14_valeurs_tiges.get(key_tig, 1.1), 
                    step=0.1,
                    key=f"p14_input_{key_tig}"
                )
                
                st.session_state.p14_valeurs_cacaoyers[key_cac] = val_cac
                st.session_state.p14_valeurs_tiges[key_tig] = val_tig
                
                cacaoyers_par_carre.append(val_cac)
                tiges_par_carre.append(val_tig)
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ÉTAPE 2 : RENDU VISUEL DU TABLEAU COMPILÉ ---
    st.markdown("### 📊 ÉTAPE 2 : Rendu Visuel du Tableau Récapitulatif")
    with st.container():
        st.markdown('<div class="pouperee-level-2">', unsafe_allow_html=True)
        
        dict_recap = {"Indicateur": ["Nombre cacaoyers", "Nb moyen de tiges/cacaoyer"]}
        for i in range(len(cacaoyers_par_carre)):
            dict_recap[f"Carré {i+1}"] = [cacaoyers_par_carre[i], tiges_par_carre[i]]
            
        df_recap = pd.DataFrame(dict_recap)
        # CORRECTION : use_container_width=True remplace l'ancien paramètre instable width="stretch"
        st.dataframe(df_recap.set_index("Indicateur"), use_container_width=True) 
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ÉTAPE 3 : ANALYSE & CRITÈRES DU SYSTÈME EXPERT LEILA IA ---
    st.markdown("### 🧠 ÉTAPE 3 : Analyse & Rapport d'Expert de Leila IA")
    with st.container():
        st.markdown('<div class="pouperee-level-3">', unsafe_allow_html=True)
        
        total_cacaoyers = sum(cacaoyers_par_carre)
        moyenne_pieds_carre = total_cacaoyers / nb_carres if nb_carres > 0 else 0
        densite_calculee = moyenne_pieds_carre * 100
        moyenne_tiges = sum(tiges_par_carre) / nb_carres if nb_carres > 0 else 0
        
        c_res1, c_res2, c_res3 = st.columns(3)
        with c_res1:
            st.metric("Total Cacaoyers Observés", f"{total_cacaoyers} pieds")
        with c_res2:
            st.metric("Moyenne par Carré (100m²)", f"{moyenne_pieds_carre:.2f} pieds")
        with c_res3:
            st.metric("Densité Estimée à l'Hectare", f"{int(densite_calculee)} pieds/ha")

        st.write("")
        st.markdown("**⚡ Rapport de diagnostic agronomique automatique :**")
        
        st.session_state["p14_densite_calculee"] = int(densite_calculee)
        st.session_state["p14_moyenne_tiges"] = moyenne_tiges

        # Grille réglementaire d'interprétation ARS 1000
        if densite_calculee < 1000:
            st.error(f"⚠️ **Sous-densité critique détectée ({int(densite_calculee)} pieds/ha) :** La parcelle est très peu dense par rapport aux recommandations de la norme ARS 1000 (cible : 1111 à 1333 pieds/ha). Leila recommande d'envisager un plan de recépage ou un regarnissage rigoureux des espaces vides.")
            st.session_state["p14_etat_peuplement"] = "Sous-population Critique"
        elif 1000 <= densite_calculee <= 1400:
            st.success(f"✅ **Densité Optimale ({int(densite_calculee)} pieds/ha) :** Excellente configuration spatiale conforme aux exigences techniques du Manuel du Planteur. L'ombrage et la circulation de l'air sont optimisés pour limiter le Swollen Shoot.")
            st.session_state["p14_etat_peuplement"] = "Optimale"
        else:
            st.warning(f"⚠️ **Sur-densité détectée ({int(densite_calculee)} pieds/ha) :** Compétition hydrique et nutritionnelle élevée entre les cacaoyers. Risque d'augmentation du taux d'humidité favorisant la pourriture brune. Leila suggère un élagage ciblé.")
            st.session_state["p14_etat_peuplement"] = "Sur-population / Compétition Haute"

        if moyenne_tiges > 1.2:
            st.info(f"⚠️ **Alerte Architecture ({moyenne_tiges:.2f} tiges/pied) :** Présence trop élevée d'axes multiples (gourmands verticaux). Leila préconise un planning urgent d'égourmandage pour concentrer la sève vers la fructification.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p14", type="primary", use_container_width=True):
        st.session_state["page_14_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 15
        st.rerun()

    # --- PIED DE PAGE ---
    st.write("---")
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>14</span>", unsafe_allow_html=True)


def dessiner_page_15_Degradation_Arbres():
    # 1. Configuration du Design Général Conforme à la Charte Applicative
    st.markdown("""
    <style>
    .stApp {
        background-color: white; /* Changé pour harmonisation de l'application */
    }
    .diapo-slide-15 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-15 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .content-box-p15 {
        background-color: #F8FBFB;
        padding: 30px;
        border-radius: 8px;
        border-left: 5px solid #16A085;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 10px;
        font-family: 'Arial', sans-serif;
    }
    .main-title-p15 {
        color: #1A252F;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 25px;
        line-height: 1.4;
    }
    .bullet-list-p15 {
        list-style-type: square;
        padding-left: 20px;
    }
    .bullet-item-p15 {
        color: #2C3E50;
        font-size: 15px;
        margin-bottom: 20px;
        line-height: 1.6;
    }
    .highlight-red {
        color: #DC3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE (Harmonisation des Titres Institutionnels) ---
    st.markdown("""
    <div class="diapo-slide-15">
        <div class="bullet-titre-15">• Critères de dégradation des arbres</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Structure textuelle réglementaire exacte
    st.markdown("""
    <div class="content-box-p15">
        <div class="main-title-p15">
            Les arbres considérés comme dégradés et non productifs sont ceux ayant les caractéristiques suivantes :
        </div>
        <ul class="bullet-list-p15">
            <li class="bullet-item-p15">
                La frondaison est ouverte et si dégradée qu'aucune action <span class="highlight-red">technique ne peut permettre</span> de la corriger ;
            </li>
            <li class="bullet-item-p15">
                L'attaque de loranthus (plantes parasites) est si forte qu'aucune taille ne permet de redonner de la vigueur aux arbres ;
            </li>
            <li class="bullet-item-p15">
                Le tronc est si dégradé que l'arbre n'a plus la possibilité de porter des cabosses ;
            </li>
            <li class="bullet-item-p15">
                Les arbres chétifs ne pouvant plus produire des cabosses.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p15", type="primary", use_container_width=True):
        st.session_state["page_15_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 16
        st.rerun()

    # 3. Pied de page avec le Numéro de Slide 15 exact et harmonisé
    st.write("<br>", unsafe_allow_html=True)
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>15</span>", unsafe_allow_html=True)



def dessiner_page_16_Etat_Cacaoyere_Strict():
    st.markdown("""
    <style>
    .stApp { background-color: #E8F8F5; }
    .main-title-p16 { color: #1A252F; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; margin-left: 20px; }
    .sub-title-p16 { color: #1F4E78; font-size: 18px; font-weight: bold; margin-left: 20px; margin-bottom: 15px; }
    .badge-p16 { background-color: #008080; color: white; padding: 4px 10px; font-weight: bold; border-radius: 4px; display: inline-block; font-size: 14px; }
    
    /* Structure en poupées russes */
    .pouperee-p16-l1 { border-left: 5px solid #1ABC9C; background-color: #FFFFFF; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p16-l2 { border-left: 5px solid #1F4E78; background-color: #F4FBF9; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p16-l3 { border-left: 5px solid #E0115F; background-color: #FFF5F7; padding: 15px; border-radius: 4px; }
    
    /* Cartes de diagnostic */
    .diagnostic-critique { background-color: #F8D7DA; color: #721C24; padding: 10px; border-radius: 4px; border-left: 4px solid #DC3545; margin-bottom: 8px; }
    .diagnostic-warning { background-color: #FFF3CD; color: #856404; padding: 10px; border-radius: 4px; border-left: 4px solid #FFC107; margin-bottom: 8px; }
    .diagnostic-ok { background-color: #D4EDDA; color: #155724; padding: 10px; border-radius: 4px; border-left: 4px solid #28A745; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p16">• Etat de la cacaoyère</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title-p16">⮚ Etat végétatif et sanitaire des cacaoyers (<span class="badge-p16">Fiche 3</span>)</div>', unsafe_allow_html=True)

    st.info("💡 **Questions directrices de l'évaluation :**\n"
            "* *Etat de dégradation des cacaoyers*\n"
            "* *Y a-t-il des attaques prononcées ou non de maladies ou ravageurs ?*")

    st.write("---")

    # =========================================================================
    # BANQUE DE DONNÉES DES CHOIX MULTIPLES PAR STRATE DE SÉVÉRITÉ
    # =========================================================================
    bibliotheque_layla = {
        "Mirides": {
            "1. Aucun": ["Aucune piqûre visible sur capsules ou jeunes pousses.", "Parcelle saine, absence totale de grilles de mirides.", "Feuillage et rameaux intacts, pas d'activité d'insectes.", "Structure des jeunes branches parfaitement saine.", "Aucun symptôme de dessèchement lié aux piqueurs-suceurs."],
            "2. Faible": ["Quelques grilles diffuses sur les rameaux terminaux.", "Présence isolée de piqûres sur de rares cabosses.", "Légers chancres de mirides localisés sur vieux bois.", "Attaque mineure concentrée en bordure de parcelle.", "Premiers signes de piqûres sans impact sur le rendement.", "Traces de passages anciens sans insectes actifs observés."],
            "3. Moyen": ["Dessèchement partiel de la cime (balais de sorcière).", "Chutes de feuilles significatives sur les branches hautes.", "Présence active de populations de mirides dans les zones ombragées.", "Plusieurs cabosses marquées entraînant des pertes locales.", "Chancres multiples bloquant partiellement la sève.", "Dessèchement de quelques apex terminaux."],
            "4. Fort": ["Cimes fortement calcinées, fortes pertes de sève.", "Dessèchement généralisé de la couronne des cacaoyers.", "Attaque massive destructrice sur les jeunes plantations.", "Chute totale des feuilles sur les arbres touchés.", "Parcelle sévèrement impactée, risque de perte d'arbres.", "Chancres profonds généralisés sur toute la structure."]
        },
        "Pourriture Brune": {
            "1. Aucun": ["Cabosses saines, aucune tache chocolat détectée.", "Absence complète de symptômes de Phytophthora.", "Fruits vigoureux sans nécrose sur toute la parcelle.", "Conditions saines, aucun foyer fongique repéré.", "Parcelle propre, cabosses en parfait état sanitaire."],
            "2. Faible": ["Attaque localisée sur de rares cabosses de bas-tronc.", "Petites taches bruises isolées à la pointe de quelques fruits.", "Début d'infection favorisé par une herbe légèrement haute.", "Attaque discrète n'impactant pas encore les fèves.", "Quelques fruits touchés près du sol uniquement.", "Symptômes initiaux stoppés par le retour du soleil."],
            "3. Moyen": ["Infection visible à hauteur d'homme, pertes modérées.", "Propagation du champignon sur plusieurs arbres voisins.", "Taches chocolat couvrant plus de la moitié de plusieurs cabosses.", "Pertes de récolte notables sur les branches intermédiaires.", "Feutrage blanc (spores) visible sur les fruits infectés.", "Infection active en progression due à l'humidité ambiante."],
            "4. Fort": ["Momification généralisée, forte pression fongique.", "Totalité des cabosses d'un même arbre complètement noires.", "Pourriture interne complète des fèves sur de nombreux arbres.", "Perte économique majeure imminente sur la récolte en cours.", "Infection invasive touchant toutes les strates du cacaoyer.", "Destruction massive des fruits suite à des pluies continues."]
        },
        "Épiphytes": {
            "1. Aucun": ["Troncs propres, pas de mousses parasites encombrantes.", "Absence totale de plantes épiphytes.", "Écorce saine et dégagée.", "Zéro encombrement végétal sur le tronc.", "Parcelle parfaitement entretenue au niveau du vieux bois."],
            "2. Faible": ["Légère présence de mousses ou lichens sur le vieux bois.", "Présence discrète sans étouffement des branches.", "Quelques lichens grisâtres sur les troncs ombragés.", "Mousses superficielles faciles à brosser.", "Début d'installation dans les fourches basses."],
            "3. Moyen": ["Fougères et mousses envahissant les fourches principales.", "Colonisation des axes porteurs de cabosses.", "Épiphytes denses réduisant la visibilité des fleurs.", "Humidité résiduelle élevée maintenue sur l'écorce.", "Présence de fougères de taille moyenne sur le tronc."],
            "4. Fort": ["Asphyxie végétative par surpopulation d'épiphytes.", "Troncs et branches totalement dissimulés sous la mousse.", "Poids excessif brisant les petites branches.", "Humidité permanente provoquant des nécroses cutanées.", "Prolifération invasive bloquant l'accès à la lumière."]
        },
        "Foreurs": {
            "1. Aucun": ["Aucune galerie ni rejet de sciure sur les troncs.", "Absence de perforations dues aux insectes xylophages.", "Tiges et branches vigoureuses sans dommages internes.", "Zéro activité de foreurs détectée.", "Bois sain sans perforation."],
            "2. Faible": ["Présence isolée de trous de pénétration sur vieilles branches.", "Rares rejets de sciure fine au pied d'un arbre.", "Attaque superficielle sur bois sec.", "Une à deux galeries mineures sans gravité apparente.", "Traces anciennes cicatrisées."],
            "3. Moyen": ["Galeriage actif avec présence de sciure fraîche.", "Perforations multiples sur les branches de production.", "Flétrissement de quelques rameaux terminaux minés.", "Écoulement de sève au niveau des points d'entrée.", "Activité manifeste de larves foreuses."],
            "4. Fort": ["Rameaux et axes majeurs cassants dus aux galeries internes.", "Destruction structurelle du tronc principal.", "Mort de branches charpentières entières.", "Sciure abondante accumulée aux bases des arbres.", "Risque d'effondrement ou de perte totale du cacaoyer."]
        },
        "CSSVD": {
            "1. Aucun": ["Feuillage normal, aucun symptôme suspect.", "Absence complète de signes du Swollen Shoot.", "Rameaux cylindriques et sains.", "Feuilles bien vertes, pas de décoloration atypique.", "Parcelle indemne de toute suspicion virale."],
            "2. Faible": ["Légère décoloration des nervures (feuilles en mosaïque).", "Rougeur suspecte sur les jeunes feuilles.", "Début de déformation foliaire isolée.", "Symptômes mineurs localisés sur un seul arbre.", "Suspicion à surveiller lors des prochains passages."],
            "3. Moyen": ["Gonflement visible sur quelques rameaux ou entre-nœuds.", "Mosaïque foliaire prononcée et généralisée sur un foyer.", "Ralentissement visible de la croissance de l'arbre.", "Gonflement caractéristique en forme de massue.", "Présence de cochenilles vectrices à proximité."],
            "4. Fort": ["Dépérissement progressif et mort de la structure de l'arbre.", "Défoliation massive et mort des extrémités des branches.", "Foyer d'infection étendu à plusieurs arbres adjacents.", "Perte de vigueur totale, arrêt de production.", "Destruction irréversible du squelette du cacaoyer."]
        },
        "Gourmands": {
            "1. Aucun": ["Troncs propres, entretien et regetonnage parfaits.", "Zéro gourmand sur l'axe principal.", "Toillettage rigoureux effectué récemment.", "Énergie de l'arbre concentrée sur la couronne.", "Architecture idéale du cacaoyer."],
            "2. Faible": ["Quelques jeunes gourmands fins à la base du tronc.", "Présence discrète de rejets herbacés.", "Gourmands de petite taille faciles à éliminer à la main.", "Début de repousse sans gêne pour la récolte.", "Entretien mineur à planifier."],
            "3. Moyen": ["Gourmands vigoureux entrant en compétition avec la couronne.", "Rejets lignifiés colonisant le tronc principal.", "Diminution de la pénétration de la lumière sous le couvert.", "Gourmands captant une part importante de la sève.", "Accès aux cabosses de tronc rendu difficile."],
            "4. Fort": ["Cacaoyers buissonnants, gourmands bloquant la lumière.", "Asphyxie complète de la couronne d'origine par les rejets.", "Perte drastique de rendement sur les branches principales.", "Parcelle non rejetonnée depuis de longs mois.", "Transformation du cacaoyer en buisson inextricable."]
        },
        "Cabosses momifiées": {
            "1. Aucun": ["Parcelle propre, résidus de récolte bien nettoyés.", "Absence de fruits momifiés sur les arbres.", "Aucun réservoir de spores de la saison passée.", "Hygiène de la cacaoyère impeccable.", "Zéro source d'inoculum résiduelle."],
            "2. Faible": ["Rares vieilles cabosses noires restées sur l'arbre.", "Présence isolée de fruits secs oubliés en hauteur.", "Impact négligeable à éliminer au prochain passage.", "Momies sporadiques sans contagion active.", "Quelques restes de récolte précédente."],
            "3. Moyen": ["Plusieurs cabosses sèches non récoltées, réservoirs d'inoculum.", "Fruits noirs desséchés fixés aux branches principales.", "Risque accru de propagation des maladies fongiques.", "Oubli manifeste lors des récoltes sanitaires.", "Momies servant de refuge à certains insectes."],
            "4. Fort": ["Accumulation critique de momies sur les branches.", "Arbres chargés de vieux fruits noirs desséchés.", "Source massive d'infection pour les nouvelles fleurs.", "Négligence sanitaire complète sur la parcelle.", "Pression parasitaire et fongique entretenue par les momies."]
        },
        "Loranthus": {
            "1. Aucun": ["Aucun plant de Loranthus (gui) détecté.", "Parcelle totalement exempte de plantes parasites.", "Branches saines sans fixation de Loranthus.", "Aucune concurrence sur la canopée.", "Zéro infestation."],
            "2. Faible": ["Une ou deux touffes isolées sur les branches hautes.", "Début d'installation du gui de cacaoyer.", "Parasitisme discret facile à élaguer.", "Présence localisée sur de vieux arbres.", "Impact physiologique minime pour le moment."],
            "3. Moyen": ["Parasitisme marqué provoquant le dessèchement de l'axe infesté.", "Plusieurs touffes vigoureuses installées dans la couronne.", "Perte de vigueur des branches situées au-dessus du parasite.", "Compétition sévère pour l'eau et les minéraux.", "Nécessité d'une intervention d'échenillage."],
            "4. Fort": ["Envahissement sévère, dépérissement des houppiers.", "Loranthus dominant la majorité de la canopée du cacaoyer.", "Mort programmée des branches charpentières.", "Chute drastique de la production de la parcelle.", "Infestation massive étouffant littéralement les arbres."]
        },
        "Enherbement": {
            "1. Aucun": ["Sol propre ou paillé, enherbement nul sous le couvert.", "Sous-bois totalement dégagé sous l'ombrage.", "Excellent contrôle des adventices.", "Circulation fluide sur toute la parcelle.", "Conditions idéales pour la récolte."],
            "2. Faible": ["Couvert herbeux ras, adventices sous contrôle.", "Tapis vert minime ne concurrençant pas les cacaoyers.", "Sarclage récent encore efficace.", "Légère pousse d'herbes non agressives.", "Sol bien entretenu."],
            "3. Moyen": ["Hauteur des adventices gênant la circulation sur la ligne.", "Herbes hautes entrant en concurrence pour l'azote du sol.", "Humidité stagnante favorisée au pied des arbres.", "Difficulté à repérer les cabosses tombées.", "Besoin urgent de réaliser un faucardage ou sarclage."],
            "4. Fort": ["Enherbement sauvage agressif, compétition nutritionnelle intense.", "Envahissement par des lianes ou des plantes arbustives.", "Accès à la parcelle bloqué par la végétation spontanée.", "Asphyxie des jeunes plants de cacaoyer.", "Foyer d'infestation pour les rongeurs et insectes."]
        },
        "Rien à signaler": {
            "1. Aucun": ["Aucune autre anomalie constatée sur la parcelle.", "Parcelle parfaitement conforme aux standards.", "Pas d'autres facteurs de stress identifiés."],
            "2. Faible": ["Rien à signaler d'anormal."], "3. Moyen": ["Rien à signaler d'anormal."], "4. Fort": ["Rien à signaler d'anormal."]
        },
        "Rongeurs / Écureuils": {
            "1. Aucun": ["Aucune morsure de rongeur détectée sur les cabosses.", "Faune locale en équilibre, pas de dégâts économiques.", "Cabosses de tronc intactes."],
            "2. Faible": ["Quelques rares cabosses grignotées au sol.", "Traces de dents superficielles sur une ou deux écorces.", "Pertes très isolées sans urgence de piégeage."],
            "3. Moyen": ["Attaque régulière sur les cabosses mûres à mi-hauteur.", "Pertes de fèves visibles sur plusieurs arbres du même alignement.", "Nécessité de réguler ou d'avancer la récolte."],
            "4. Fort": ["Ravages systématiques, forte proportion de cabosses vidées.", "Écureuils ou rats omniprésents détruisant la récolte utile.", "Urgence d'une stratégie de lutte ou de piégeage biologique."]
        },
        "Trachéomycose (Vascular Dieback)": {
            "1. Aucun": ["Aucun symptôme de dépérissement vasculaire repéré.", "Feuillage vigoureux, vaisseaux conducteurs sains."],
            "2. Faible": ["Jaunissement isolé de quelques feuilles sur une branche.", "Premiers signes de flétrissement sans blocage majeur de sève."],
            "3. Moyen": ["Dessèchement net d'un rameau entier avec persistance des feuilles mortes.", "Brunissement des tissus conducteurs internes après test au couteau."],
            "4. Fort": ["Dépérissement brutal et mort de branches charpentières entières.", "Blocage total des flux nutritionnels, arbre condamné à court terme."]
        },
        "Psylles / Chenilles défoliatrices": {
            "1. Aucun": ["Jeunes pousses saines, aucun insecte défoliateur actif.", "Bourgeons terminaux intacts."],
            "2. Faible": ["Quelques feuilles perforées ou enroulées sur les rejets.", "Présence discrète de chenilles sans ralentissement de croissance."],
            "3. Moyen": ["Attaque visible sur les flushes (jeunes poussées de feuilles).", "Déformation des bourgeons terminaux par les attaques de psylles."],
            "4. Fort": ["Destruction systématique des jeunes bourgeons (blocage du flush).", "Défoliation sévère des jeunes plants mettant en péril leur survie."]
        },
        "Stress Hydrique / Coup de soleil": {
            "1. Aucun": ["Ombrage optimal, humidité interne de l'arbre stable.", "Feuilles bien orientées."],
            "2. Faible": ["Léger flétrissement des pointes de feuilles aux heures chaudes.", "Ombrage un peu clairsemé par endroits."],
            "3. Moyen": ["Chute de feuilles vertes à cause de la sécheresse prolongée.", "Brûlures marginales nettes (dessèchement du limbe) dues à l'ensoleillement direct."],
            "4. Fort": ["Défoliation massive due au stress hydrique sévère.", "Dessèchement des extrémités, risque de mort par rupture de la canopée."]
        }
    }

    severites_options = ["1. Aucun", "2. Faible", "3. Moyen", "4. Fort"]
    liste_autres_anomalies = ["Rien à signaler", "Rongeurs / Écureuils", "Trachéomycose (Vascular Dieback)", "Psylles / Chenilles défoliatrices", "Stress Hydrique / Coup de soleil"]

    # =========================================================================
    # 🔐 PERSISTANCE ET INITIALISATION STRUCTURÉE DU SESSION STATE
    # =========================================================================
    cles_initialisation = {
        "p16_s_mir": "1. Aucun", "p16_o_mir": bibliotheque_layla["Mirides"]["1. Aucun"][0],
        "p16_s_pbr": "1. Aucun", "p16_o_pbr": bibliotheque_layla["Pourriture Brune"]["1. Aucun"][0],
        "p16_s_epi": "1. Aucun", "p16_o_epi": bibliotheque_layla["Épiphytes"]["1. Aucun"][0],
        "p16_s_for": "1. Aucun", "p16_o_for": bibliotheque_layla["Foreurs"]["1. Aucun"][0],
        "p16_s_css": "1. Aucun", "p16_o_css": bibliotheque_layla["CSSVD"]["1. Aucun"][0],
        "p16_type_aut": "Rien à signaler",
        "p16_s_aut": "1. Aucun", "p16_o_aut": bibliotheque_layla["Rien à signaler"]["1. Aucun"][0],
        "p16_v_gou": "1. Aucun", "p16_o_gou": bibliotheque_layla["Gourmands"]["1. Aucun"][0],
        "p16_v_mom": "1. Aucun", "p16_o_mom": bibliotheque_layla["Cabosses momifiées"]["1. Aucun"][0],
        "p16_v_lor": "1. Aucun", "p16_o_lor": bibliotheque_layla["Loranthus"]["1. Aucun"][0],
        "p16_v_enh": "1. Aucun", "p16_o_enh": bibliotheque_layla["Enherbement"]["1. Aucun"][0],
    }

    for cle, defaut in cles_initialisation.items():
        if cle not in st.session_state:
            st.session_state[cle] = defaut

    # Helper pour trouver l'index de sécurité lors du rechargement
    def obtenir_index(liste, cle_state):
        valeur = st.session_state[cle_state]
        return liste.index(valeur) if valeur in liste else 0

    # =========================================================================
    # LE SYSTÈME EXPERT EN ACTION
    # =========================================================================
    
    # 🪆 Poupée 1 : Saisie de Terrain segmentée
    with st.expander("🪆 ÉTAPE 1 : Évaluation des indicateurs phytosanitaires", expanded=True):
        st.markdown('<div class="pouperee-p16-l1">', unsafe_allow_html=True)
        
        col_tab1, col_tab2 = st.columns(2)
        
        with col_tab1:
            st.markdown("##### 🪲 Section A : Maladies & Ravageurs")
            
            # Attaque Mirides
            c1, c2 = st.columns([1.2, 2.8])
            sev_mirides = c1.selectbox("Sévérité Mirides", severites_options, index=obtenir_index(severites_options, "p16_s_mir"), key="p16_s_mir")
            # Sécurité si la sévérité change pour éviter le crash d'index hors-limite
            liste_obs_mir = bibliotheque_layla["Mirides"][sev_mirides]
            obs_mirides = c2.selectbox("Observation Mirides (Choix Layla)", liste_obs_mir, index=obtenir_index(liste_obs_mir, "p16_o_mir"), key="p16_o_mir")
            
            # Pourriture Brune
            c1, c2 = st.columns([1.2, 2.8])
            sev_pbrune = c1.selectbox("Sévérité Pourriture Brune", severites_options, index=obtenir_index(severites_options, "p16_s_pbr"), key="p16_s_pbr")
            liste_obs_pbr = bibliotheque_layla["Pourriture Brune"][sev_pbrune]
            obs_pbrune = c2.selectbox("Observation Pourriture Brune (Choix Layla)", liste_obs_pbr, index=obtenir_index(liste_obs_pbr, "p16_o_pbr"), key="p16_o_pbr")
            
            # Épiphytes
            c1, c2 = st.columns([1.2, 2.8])
            sev_epiphytes = c1.selectbox("Présence Épiphytes", severites_options, index=obtenir_index(severites_options, "p16_s_epi"), key="p16_s_epi")
            liste_obs_epi = bibliotheque_layla["Épiphytes"][sev_epiphytes]
            obs_epiphytes = c2.selectbox("Observation Épiphytes (Choix Layla)", liste_obs_epi, index=obtenir_index(liste_obs_epi, "p16_o_epi"), key="p16_o_epi")
            
            # Foreurs
            c1, c2 = st.columns([1.2, 2.8])
            sev_foreurs = c1.selectbox("Attaque Foreurs", severites_options, index=obtenir_index(severites_options, "p16_s_for"), key="p16_s_for")
            liste_obs_for = bibliotheque_layla["Foreurs"][sev_foreurs]
            obs_foreurs = c2.selectbox("Observation Foreurs (Choix Layla)", liste_obs_for, index=obtenir_index(liste_obs_for, "p16_o_for"), key="p16_o_for")
            
            # CSSVD (Swollen Shoot)
            c1, c2 = st.columns([1.2, 2.8])
            sev_cssvd = c1.selectbox("Attaque CSSVD", severites_options, index=obtenir_index(severites_options, "p16_s_css"), key="p16_s_css")
            liste_obs_css = bibliotheque_layla["CSSVD"][sev_cssvd]
            obs_cssvd = c2.selectbox("Observation CSSVD (Choix Layla)", liste_obs_css, index=obtenir_index(liste_obs_css, "p16_o_css"), key="p16_o_css")
            
            # ---- GESTION INTELLIGENTE DU PARAMÈTRE "AUTRES" ----
            st.markdown("---")
            st.caption("🔍 **Diagnostic Complémentaire sur Choix Spécifique**")
            
            type_autre = st.selectbox("Type d'anomalie détectée", liste_autres_anomalies, index=obtenir_index(liste_autres_anomalies, "p16_type_aut"), key="p16_type_aut")
            
            c1, c2 = st.columns([1.2, 2.8])
            sev_autres = c1.selectbox("Sévérité Autre", severites_options, index=obtenir_index(severites_options, "p16_s_aut"), key="p16_s_aut")
            
            liste_obs_aut = bibliotheque_layla[type_autre][sev_autres]
            obs_autres = c2.selectbox(f"Observation {type_autre} (Choix Layla)", liste_obs_aut, index=obtenir_index(liste_obs_aut, "p16_o_aut"), key="p16_o_aut")

        with col_tab2:
            st.markdown("##### 🌿 Section B : Paramètres Végétatifs")
            
            # Gourmands
            c1, c2 = st.columns([1.2, 2.8])
            val_gourmands = c1.selectbox("Présence de gourmands", severites_options, index=obtenir_index(severites_options, "p16_v_gou"), key="p16_v_gou")
            liste_obs_gou = bibliotheque_layla["Gourmands"][val_gourmands]
            obs_gourmands = c2.selectbox("Observation Gourmands (Choix Layla)", liste_obs_gou, index=obtenir_index(liste_obs_gou, "p16_o_gou"), key="p16_o_gou")
            
            # Cabosses momifiées
            c1, c2 = st.columns([1.2, 2.8])
            val_momifiees = c1.selectbox("Cabosses momifiées", severites_options, index=obtenir_index(severites_options, "p16_v_mom"), key="p16_v_mom")
            liste_obs_mom = bibliotheque_layla["Cabosses momifiées"][val_momifiees]
            obs_momifiees = c2.selectbox("Observation Momifiées (Choix Layla)", liste_obs_mom, index=obtenir_index(liste_obs_mom, "p16_o_mom"), key="p16_o_mom")
            
            # Loranthus
            c1, c2 = st.columns([1.2, 2.8])
            val_loranthus = c1.selectbox("Présence de Loranthus", severites_options, index=obtenir_index(severites_options, "p16_v_lor"), key="p16_v_lor")
            liste_obs_lor = bibliotheque_layla["Loranthus"][val_loranthus]
            obs_loranthus = c2.selectbox("Observation Loranthus (Choix Layla)", liste_obs_lor, index=obtenir_index(liste_obs_lor, "p16_o_lor"), key="p16_o_lor")
            
            # Enherbement
            c1, c2 = st.columns([1.2, 2.8])
            val_enherbement = c1.selectbox("Niveau d'enherbement", severites_options, index=obtenir_index(severites_options, "p16_v_enh"), key="p16_v_enh")
            liste_obs_enh = bibliotheque_layla["Enherbement"][val_enherbement]
            obs_enherbement = c2.selectbox("Observation Enherbement (Choix Layla)", liste_obs_enh, index=obtenir_index(liste_obs_enh, "p16_o_enh"), key="p16_o_enh")

    st.markdown('</div>', unsafe_allow_html=True)

    # 🪆 Poupée 2 : Le Grand Tableau Restructuré (Mise à jour width="stretch" pour 2026)
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Tableau de Synthèse)", expanded=True):
        st.markdown('<div class="pouperee-p16-l2">', unsafe_allow_html=True)
        
        label_autre_affichage = f"Autre : {type_autre}" if type_autre != "Rien à signaler" else "Autres anomalies"
        
        data_tableau_p16 = {
            "Maladies/ravageurs": ["Attques de mirides", "Attaques de Pourriture Brune", "Présence de plantes épiphytes", "Attaque Foreurs", "Attaque CSSVD", label_autre_affichage],
            "Sévérité": [sev_mirides, sev_pbrune, sev_epiphytes, sev_foreurs, sev_cssvd, sev_autres],
            "Observations (A)": [obs_mirides, obs_pbrune, obs_epiphytes, obs_foreurs, obs_cssvd, obs_autres],
            "Paramètres": ["Présence de gourmands", "Présence de cabosses momifiées", "Présence de loranthus", "Enherbement", "-", "-"],
            "Valeur": [val_gourmands, val_momifiees, val_loranthus, val_enherbement, "-", "-"],
            "Observations (B)": [obs_gourmands, obs_momifiees, obs_loranthus, obs_enherbement, "-", "-"]
        }
        
        df_p16 = pd.DataFrame(data_tableau_p16)
        st.dataframe(df_p16.set_index("Maladies/ravageurs"), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

        # 🪆 Poupée 3 : Moteur d'Avis Diagnostique de Layla
        with st.expander("🧠 ÉTAPE 3 : Matrice d'Arbitrage & Conseils de Layla", expanded=True):
            st.markdown('<div class="pouperee-p16-l3">', unsafe_allow_html=True)
            st.markdown("#### 💬 Alertes Décisionnelles de l'Expert")
            
            alertes_declenches = 0
            
            if "1. Aucun" not in sev_cssvd:
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-critique">
                    🚨 <strong>ALERTE CRITIQUE DE LAYLA (CSSVD / Swollen Shoot) :</strong> L'anomalie est signalée au niveau {sev_cssvd}. 
                    Conformément à la réglementation phytosanitaire en Côte d'Ivoire, l'éradication (arrachage des pieds atteints et des arbres contacts) est impérative pour freiner la progression du virus.
                </div>
                """, unsafe_allow_html=True)
            
            if "3. Moyen" in sev_autres and type_autre == "Trachéomycose (Vascular Dieback)" or "4. Fort" in sev_autres and type_autre == "Trachéomycose (Vascular Dieback)":
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-critique">
                    🍂 <strong>ALERTE PHYTOSANITAIRE DE LAYLA (Trachéomycose) :</strong> Niveau {sev_autres} détecté. 
                    Cette maladie vasculaire bloque la sève de manière irréversible. Couper et brûler immédiatement les branches atteintes en dessous de la zone brune pour protéger le reste de l'arbre.
                </div>
                """, unsafe_allow_html=True)

            if "3. Moyen" in sev_mirides or "4. Fort" in sev_mirides or "3. Moyen" in sev_foreurs or "4. Fort" in sev_foreurs:
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-warning">
                    🪲 <strong>ALERTE RAVAGEURS :</strong> Pression parasitaire trop élevée des insectes piqueurs-suceurs ou foreurs. 
                    Layla recommande de synchroniser un traitement de lutte intégrée (physique et chimique ciblée) avant la grande fuite de sève.
                </div>
                """, unsafe_allow_html=True)
                
            if ("4. Fort" in val_gourmands or "4. Fort" in val_enherbement or "3. Moyen" in val_loranthus or 
                "4. Fort" in val_loranthus or "3. Moyen" in sev_pbrune or "4. Fort" in sev_pbrune or 
                ("3. Moyen" in sev_autres or "4. Fort" in sev_autres) and type_autre in ["Rongeurs / Écureuils", "Stress Hydrique / Coup de soleil"]):
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-warning">
                    🌿 <strong>ALERTE MAINTENANCE AGRONOMIQUE & COMPLÉMENTS :</strong> L'état général montre un besoin de suivi.
                    Vérifier l'ombrage (si stress hydrique fort) ou intensifier le rythme des récoltes sanitaires (si pression des rongeurs ou Pourriture Brune).
                </div>
                """, unsafe_allow_html=True)

            if alertes_declenches == 0:
                st.markdown("""
                <div class="diagnostic-ok">
                    🟢 <strong>DIAGNOSTIC GLOBAL DE LAYLA :</strong> L'état végétatif et sanitaire général est maîtrisé. Les pressions parasitaires et fongiques restent sous le seuil d'intervention économique. Maintenir le protocole d'observation bimensuel.
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p16", type="primary", use_container_width=True):
        st.session_state["page_16_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 17
        st.rerun()

    # Numérotation réglementaire en bas à droite
    st.write("---")
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>16</span>", unsafe_allow_html=True)



def dessiner_page_17_Etat_Du_Sol_Strict():
    st.markdown("""
    <style>
    .stApp { background-color: #F4F6F6; }
    .main-title-p17 { color: #111625; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; margin-left: 20px; }
    .sub-title-p17 { color: #1F4E78; font-size: 18px; font-weight: bold; margin-left: 20px; margin-bottom: 15px; }
    .badge-p17 { background-color: #8E44AD; color: white; padding: 4px 10px; font-weight: bold; border-radius: 4px; display: inline-block; font-size: 14px; }
    
    /* Structure en poupées russes */
    .pouperee-p17-l1 { border-left: 5px solid #8E44AD; background-color: #FFFFFF; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p17-l2 { border-left: 5px solid #2980B9; background-color: #F7F9FA; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p17-l3 { border-left: 5px solid #D35400; background-color: #FFFBF2; padding: 15px; border-radius: 4px; }
    
    /* Cartes de diagnostic */
    .diagnostic-danger { background-color: #FADBD8; color: #78281F; padding: 10px; border-radius: 4px; border-left: 4px solid #C0392B; margin-bottom: 8px; }
    .diagnostic-alerte { background-color: #FCF3CF; color: #7E5109; padding: 10px; border-radius: 4px; border-left: 4px solid #F1C40F; margin-bottom: 8px; }
    .diagnostic-excellent { background-color: #D5F5E3; color: #145A32; padding: 10px; border-radius: 4px; border-left: 4px solid #27AE60; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p17">• Etat du sol</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title-p17">⮚ Caractéristiques physiques du sol (<span class="badge-p17">Fiche 3</span>)</div>', unsafe_allow_html=True)

    st.info("💡 **Orientation Toposéquence :**\n"
            "Indiquer le positionnement de la cacaoyère par rapport à la toposéquence (Plateau, haut de versant, mi-versant, bas de versant, bas-fond).")

    # =========================================================================
    # BANQUE DE DONNÉES DES CHOIX MULTIPLES POUR L'ÉTAT DU SOL (5-6 CHOIX)
    # =========================================================================
    bibliotheque_sol_layla = {
        "Couvert végétal": {
            "1. Beaucoup": [
                "Litière de feuilles très dense couvrant totalement le sol.",
                "Excellente protection du sol contre l'impact direct de la pluie.",
                "Paillage naturel épais favorisant la vie microbienne.",
                "Couverture végétale homogène retenant parfaitement l'humidité.",
                "Forte accumulation de débris organiques en surface."
            ],
            "2. Moyen": [
                "Sol partiellement visible sous une litière diffuse.",
                "Protection modérée du sol contre le lessivage.",
                "Couverture herbeuse ou de feuilles semi-homogène.",
                "Humidité du sol conservée de manière intermittente.",
                "Quelques zones nues alternent avec des zones couvertes.",
                "Niveau de décomposition de la litière correct."
            ],
            "3. Faible": [
                "Sol nu sur la majeure partie de la surface évaluée.",
                "Absence presque totale de litière protectrice.",
                "Risque d'érosion par impact des gouttes d'eau très élevé.",
                "Dessèchement rapide de la couche de surface sous le soleil.",
                "Dégradation avancée du couvert humifère.",
                "Sol exposé aux rayons directs sans litière isolante."
            ]
        },
        "Présence de Matière organique": {
            "1. Beaucoup": [
                "Horizon de surface de couleur noire ou brun foncé très net.",
                "Sol grumeleux, souple et riche en humus structuré.",
                "Abondance de débris végétaux bien décomposés en surface.",
                "Forte fertilité apparente visible à la structure du sol.",
                "Excellente rétention d'eau liée au taux d'humus."
            ],
            "2. Moyen": [
                "Teneur en humus correcte en surface.",
                "Coloration intermédiaire du sol témoignant d'un apport régulier.",
                "Structure du sol moyennement stable.",
                "Activité biologique moyenne (rares galeries de vers de terre).",
                "Apport organique à stimuler par la gestion des résidus.",
                "Présence superficielle de débris ligneux en cours de décomposition."
            ],
            "3. Faible": [
                "Sol de couleur claire (lessivé ou sableux en surface).",
                "Sol compact ou pulvérulent manquant totalement d'humus.",
                "Absence de signes d'activité biologique ou microbienne.",
                "Épuisement humifère marqué menaçant la nutrition des arbres.",
                "Structure instable sujette au compactage rapide.",
                "Taux de matière organique critique nécessitant des apports."
            ]
        },
        "Profondeur": {
            "1. Beaucoup": [
                "Sol profond sans obstacle rocheux visible sur plus d'un mètre.",
                "Excellent ancrage racinaire possible pour les pivots des arbres.",
                "Volume de sol explorable maximal pour l'alimentation en eau.",
                "Absence de dalle latéritique ou d'horizon induré.",
                "Profil de sol homogène et meuble en profondeur."
            ],
            "2. Moyen": [
                "Présence de gravillons ou d'obstacles modérés à mi-profondeur.",
                "Enracinement correct mais limité sous 60 cm.",
                "Sol de profondeur moyenne typique des flancs de collines.",
                "Ressource en eau du sol modérément disponible en saison sèche.",
                "Présence d'une couche gravillonnaire non cimentée.",
                "Pivot du cacaoyer pouvant contourner les obstacles."
            ],
            "3. Faible": [
                "Sol très superficiel, roche ou carapace latéritique proche de la surface.",
                "Horizon induré bloquant totalement le développement racinaire.",
                "Faible réserve en eau, risque de stress hydrique rapide.",
                "Arbres sensibles au déchaussement et au renversement.",
                "Couche arable de moins de 30 cm d'épaisseur.",
                "Risque d'asphyxie racinaire temporaire sur dalle imperméable."
            ]
        },
        "Texture": {
            "1. Beaucoup": [
                "Texture équilibrée de type limono-argileuse idéale.",
                "Sol malléable sans être collant, excellente porosité.",
                "Bon équilibre entre rétention d'eau et aération du système.",
                "Texture facilitant le travail racinaire et la nutrition.",
                "Sol doté d'une capacité d'échange cationique optimale."
            ],
            "2. Moyen": [
                "Texture à tendance sableuse ou argileuse lourde modérée.",
                "Sol légèrement lourd à travailler ou un peu filtrant.",
                "Proportions d'éléments fins et grossiers acceptables.",
                "Comportement physique correct face aux variations d'eau.",
                "Légère prédominance de limon provoquant une sensibilité à la battance.",
                "Porosité moyenne limitant légèrement la dynamique de l'eau."
            ],
            "3. Faible": [
                "Texture très dégradée, soit sable pur filtrant, soit argile compacte asfixiante.",
                "Sol excessivement sableux ne retenant aucun nutriment.",
                "Argile massive créant des fentes de retrait énormes en saison sèche.",
                "Contraintes physiques majeures pour la survie des radicelles.",
                "Texture squelettique dominée par les éléments grossiers.",
                "Asphyxie totale en cas de pluie ou dessèchement immédiat au soleil."
            ]
        },
        "Hydromorphie": {
            "1. Beaucoup": [
                "Engorgement permanent en eau, taches de rouille et gris bleuté dès la surface.",
                "Sol marécageux asfixiant le système racinaire du cacaoyer.",
                "Nappe phréatique affleurante bloquant toute aération du sol.",
                "Conditions anaérobies marquées provoquant la mort des radicelles.",
                "Stagnation d'eau prolongée impropre à la culture du cacao."
            ],
            "2. Moyen": [
                "Traces d'hydromorphie temporaire visibles en profondeur.",
                "Taches d'oxydoréduction (rouille) localisées sous 50 cm.",
                "Engorgement temporaire uniquement en forte saison des pluies.",
                "Ralentissement passager de l'activité racinaire sans mortalité.",
                "Drainage naturel lent nécessitant une surveillance.",
                "Zone de transition hydrique sur le bas de versant."
            ],
            "3. Faible": [
                "Sol parfaitement drainé, aucune tache de stagnation d'eau.",
                "Excellente circulation de l'eau et de l'air dans tout le profil.",
                "Absence totale de signes d'asphyxie racinaire.",
                "Profil sain maintenant une aération optimale toute l'année.",
                "Conditions idéales pour le développement des champignons mycorhiziens."
            ]
        },
        "Zones érodées": {
            "1. Oui": [
                "Ravinement marqué avec transport visible de terre arable.",
                "Présence de rigoles d'érosion dénudant les racines superficielles.",
                "Perte flagrante de la couche humifère entraînée par les eaux.",
                "Décapage de l'horizon de surface suite à une forte pente.",
                "Traces de sédimentation de boue en bas de versant.",
                "Dégradation physique active menaçant la stabilité des arbres."
            ],
            "2. Non": [
                "Aucun signe d'érosion ou de transport de matière.",
                "Surface stable, intégrité du sol préservée.",
                "Pas de rigoles ni de dénudation racinaire constatée.",
                "Topographie ou couverture empêchant le ruissellement destructeur.",
                "Horizon de surface parfaitement en place."
            ]
        },
        "Risque érosion": {
            "1. Oui": [
                "Forte pente combinée à une absence de couvert végétal au sol.",
                "Position en haut de versant sans barrière anti-érosive.",
                "Sol meuble très sensible au détachement par le ruissellement.",
                "Menace imminente de ravinement à la prochaine saison des pluies.",
                "Configuration topographique canalisant les flux d'eau de surface.",
                "Absence totale d'aménagements de rétention d'eau."
            ],
            "2. Non": [
                "Pente faible ou nulle mettant la parcelle à l'abri du ruissellement.",
                "Couvert végétal et enherbement ras fixant solidement le sol.",
                "Présence de dispositifs naturels de rétention (paillage, arbres de retenue).",
                "Caractéristiques physiques du sol limitant la susceptibilité à l'érosion.",
                "Risque nul ou négligeable dans les conditions actuelles."
            ]
        }
    }

    options_toposequence = ["Plateau", "Haut de versant", "Mi-versant", "Bas de versant", "Bas-fond"]
    valeurs_trois_niveaux = ["1. Beaucoup", "2. Moyen", "3. Faible"]
    valeurs_oui_non = ["1. Oui", "2. Non"]

    # =========================================================================
    # 🔐 PERSISTANCE ET INITIALISATION STRUCTURÉE DU SESSION STATE
    # =========================================================================
    cles_initialisation_p17 = {
        "p17_topos": "Mi-versant",
        "p17_v_cou": "2. Moyen", "p17_o_cou": bibliotheque_sol_layla["Couvert végétal"]["2. Moyen"][0],
        "p17_v_mor": "2. Moyen", "p17_o_mor": bibliotheque_sol_layla["Présence de Matière organique"]["2. Moyen"][0],
        "p17_v_pro": "1. Beaucoup", "p17_o_pro": bibliotheque_sol_layla["Profondeur"]["1. Beaucoup"][0],
        "p17_v_tex": "1. Beaucoup", "p17_o_tex": bibliotheque_sol_layla["Texture"]["1. Beaucoup"][0],
        "p17_v_hyd": "3. Faible", "p17_o_hyd": bibliotheque_sol_layla["Hydromorphie"]["3. Faible"][0],
        "p17_v_ero": "2. Non", "p17_o_ero": bibliotheque_sol_layla["Zones érodées"]["2. Non"][0],
        "p17_v_r_er": "2. Non", "p17_o_r_er": bibliotheque_sol_layla["Risque érosion"]["2. Non"][0],
    }

    for cle, defaut in cles_initialisation_p17.items():
        if cle not in st.session_state:
            st.session_state[cle] = defaut

    # Fonction assistante de synchronisation d'index
    def obtenir_index(liste, cle_state):
        valeur = st.session_state[cle_state]
        return liste.index(valeur) if valeur in liste else 0

    # Sélecteur de positionnement topographique synchro
    toposequence = st.selectbox(
        "Positionnement topographique de la cacaoyère",
        options_toposequence,
        index=obtenir_index(options_toposequence, "p17_topos"),
        key="p17_topos"
    )

    st.write("---")

    # =========================================================================
    # ENTRÉES DU TERRAIN : POUPÉE 1
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des observations physiques du sol", expanded=True):
        st.markdown('<div class="pouperee-p17-l1">', unsafe_allow_html=True)
        
        col_sol1, col_sol2 = st.columns(2)
        
        with col_sol1:
            st.markdown("##### 🧱 Profil & Propriétés du Sol")
            
            # Couvert Végétal
            c1, c2 = st.columns([1.2, 2.8])
            val_couvert = c1.selectbox("Couvert végétal", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_cou"), key="p17_v_cou")
            liste_obs_cou = bibliotheque_sol_layla["Couvert végétal"][val_couvert]
            obs_couvert = c2.selectbox("Observation Couvert (Choix Layla)", liste_obs_cou, index=obtenir_index(liste_obs_cou, "p17_o_cou"), key="p17_o_cou")
            
            # Matière Organique
            c1, c2 = st.columns([1.2, 2.8])
            val_morg = c1.selectbox("Matière organique", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_mor"), key="p17_v_mor")
            liste_obs_mor = bibliotheque_sol_layla["Présence de Matière organique"][val_morg]
            obs_morg = c2.selectbox("Observation M.O. (Choix Layla)", liste_obs_mor, index=obtenir_index(liste_obs_mor, "p17_o_mor"), key="p17_o_mor")
            
            # Profondeur
            c1, c2 = st.columns([1.2, 2.8])
            val_prof = c1.selectbox("Profondeur sol", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_pro"), key="p17_v_pro")
            liste_obs_pro = bibliotheque_sol_layla["Profondeur"][val_prof]
            obs_prof = c2.selectbox("Observation Profondeur (Choix Layla)", liste_obs_pro, index=obtenir_index(liste_obs_pro, "p17_o_pro"), key="p17_o_pro")
            
            # Texture
            c1, c2 = st.columns([1.2, 2.8])
            val_text = c1.selectbox("Texture", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_tex"), key="p17_v_tex")
            liste_obs_tex = bibliotheque_sol_layla["Texture"][val_text]
            obs_text = c2.selectbox("Observation Texture (Choix Layla)", liste_obs_tex, index=obtenir_index(liste_obs_tex, "p17_o_tex"), key="p17_o_tex")
            
            # Hydromorphie
            c1, c2 = st.columns([1.2, 2.8])
            val_hydro = c1.selectbox("Hydromorphie", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_hyd"), key="p17_v_hyd")
            liste_obs_hyd = bibliotheque_sol_layla["Hydromorphie"][val_hydro]
            obs_hydro = c2.selectbox("Observation Hydromorphie (Choix Layla)", liste_obs_hyd, index=obtenir_index(liste_obs_hyd, "p17_o_hyd"), key="p17_o_hyd")

        with col_sol2:
            st.markdown("##### 🌊 Dynamique d'Érosion (Pente & Dégradations)")
            
            # Zones Érodées
            c1, c2 = st.columns([1.2, 2.8])
            val_erodee = c1.selectbox("Zones érodées ?", valeurs_oui_non, index=obtenir_index(valeurs_oui_non, "p17_v_ero"), key="p17_v_ero")
            liste_obs_ero = bibliotheque_sol_layla["Zones érodées"][val_erodee]
            obs_erodee = c2.selectbox("Observation Érosion Active (Choix Layla)", liste_obs_ero, index=obtenir_index(liste_obs_ero, "p17_o_ero"), key="p17_o_ero")
            
            # Risque d'Érosion
            c1, c2 = st.columns([1.2, 2.8])
            val_risq_ero = c1.selectbox("Risque d'érosion ?", valeurs_oui_non, index=obtenir_index(valeurs_oui_non, "p17_v_r_er"), key="p17_v_r_er")
            liste_obs_r_er = bibliotheque_sol_layla["Risque érosion"][val_risq_ero]
            obs_risq_ero = c2.selectbox("Observation Risque Érosion (Choix Layla)", liste_obs_r_er, index=obtenir_index(liste_obs_r_er, "p17_o_r_er"), key="p17_o_r_er")

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # LE TABLEAU DE SYNTHÈSE SYNOPTIQUE : POUPÉE 2
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel du Sol", expanded=True):
        st.markdown('<div class="pouperee-p17-l2">', unsafe_allow_html=True)
        
        data_tableau_p17 = {
            "Eléments d'observation (Gauche)": ["Couvert végétal", "Présence de Matière organique", "Profondeur", "Texture", "Hydromorphie"],
            "Valeur (G)": [val_couvert, val_morg, val_prof, val_text, val_hydro],
            "Observations (Gauche)": [obs_couvert, obs_morg, obs_prof, obs_text, obs_hydro],
            "Eléments d'observation (Droite)": ["Existence de zones érodées", "Existence de zones à risque d'érosion", "-", "-", "-"],
            "Valeur (D)": [val_erodee, val_risq_ero, "-", "-", "-"],
            "Observations (Droite)": [obs_erodee, obs_risq_ero, "-", "-", "-"]
        }
        
        df_p17 = pd.DataFrame(data_tableau_p17)
        st.dataframe(df_p17.set_index("Eléments d'observation (Gauche)"), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # LE MOTEUR D'ARBITRAGE DE LAYLA : POUPÉE 3
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Matrice d'Arbitrage Pédologique de Layla", expanded=True):
        st.markdown('<div class="pouperee-p17-l3">', unsafe_allow_html=True)
        st.markdown("#### 💬 Alertes Sol & Recommandations de l'Expert")
        
        alertes_sol = 0
        
        # Alerte Hydromorphie Critique (Bas-fond ou bas de versant)
        if "1. Beaucoup" in val_hydro or (toposequence == "Bas-fond" and "3. Faible" not in val_hydro):
            alertes_sol += 1
            st.markdown(f"""
            <div class="diagnostic-danger">
                🌊 <strong>ALERTE HYDROPHYSIQUE (Asphyxie Racinaire) :</strong> Sol à forte hydromorphie ou situé en {toposequence}.
                Le cacaoyer déteste avoir les pieds dans l'eau stagnante. Layla préconise de creuser d'urgence des canaux de drainage périphériques pour abaisser le niveau de la nappe temporaire.
            </div>
            """, unsafe_allow_html=True)
            
        # Alerte Érosion Active ou Risque Élevé (Haut de versant / Pente forte)
        if "1. Oui" in val_erodee or "1. Oui" in val_risq_ero or "3. Faible" in val_couvert:
            alertes_sol += 1
            st.markdown("""
            <div class="diagnostic-alerte">
                🍂 <strong>ALERTE DÉGRADATION DU SOL (Érosion / Lessivage) :</strong> Présence de zones érodées ou risque élevé lié à la faiblesse du couvert végétal.
                Layla recommande l'interdiction du désherbage total chimique, la mise en place immédiate d'un paillage résiduel autour des arbres et l'installation de bandes enherbées perpendiculaires à la pente.
            </div>
            """, unsafe_allow_html=True)

        # Alerte Perte de Fertilité (Carence Humique)
        if "3. Faible" in val_morg:
            alertes_sol += 1
            st.markdown("""
            <div class="diagnostic-alerte">
                🧱 <strong>ALERTE APPAUVRISSEMENT EN MATIÈRE ORGANIQUE :</strong> L'horizon humifère est insuffisant ou lavé.
                Risque de blocage de l'alimentation minérale. Valoriser l'ensemble des cabosses vides après écabossage et envisager un apport de compost ou d'engrais organique bien mûr sous la projection de la couronne.
            </div>
            """, unsafe_allow_html=True)

        if alertes_sol == 0:
            st.markdown(f"""
            <div class="diagnostic-excellent">
                🟢 <strong>DIAGNOSTIC DE LAYLA (Sol Sain & Stable) :</strong> La structure physique du sol est excellente en position de {toposequence}. 
                Le couvert végétal et le taux de matière organique protègent efficacement la parcelle. Le potentiel agro-pédologique est optimal pour soutenir la productivité des cacaoyers.
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p17", type="primary", use_container_width=True):
        st.session_state["page_17_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 18
        st.rerun()

    # Numérotation réglementaire en bas à droite
    st.write("---")
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>17</span>", unsafe_allow_html=True)



def dessiner_page_18_post_recolte():
    # --- CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-18 {
        background-color: #C6E0B4; /* Vert institutionnel standardisé */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-18 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .diagnostic-container {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 8px;
        margin-top: 25px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #16A085;
    }
    .diag-title {
        color: #16A085;
        font-size: 17px;
        font-weight: bold;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-good { color: #27AE60; font-weight: bold; margin-bottom: 10px; list-style-position: inside; }
    .status-warning { color: #F39C12; font-weight: bold; margin-bottom: 10px; list-style-position: inside; }
    .status-danger { color: #C0392B; font-weight: bold; margin-bottom: 10px; list-style-position: inside; }
    
    .table-header { font-weight: bold; padding: 10px; background-color: #16A085; color: white; border-radius: 4px; text-align: left; font-size: 14px;}
    .cell-text { padding-top: 12px; font-size: 14px; color: #2C3E50; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION ---
    st.markdown("""
    <div class="diapo-slide-18">
        <div class="bullet-titre-18">• Pratiques de récolte et post-récolte</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # Banque d'options de terrain
    options_fermentation = ["1. Bâche en plastique", "2. En caisses de bois", "3. En tas sous bananiers"]
    options_sechage = ["1. Sur goudron", "2. Sur claies surélevées", "3. Sur bâche propre", "4. Sur aire cimentée"]
    options_brassage = ["1. Brassage régulier", "2. Brassage insuffisant", "3. Aucun brassage"]
    options_tri = ["1. Tri manuel à plat", "2. Tamisage / Calibrage mécanique", "3. Aucun tri"]
    options_stockage = ["1. Sacs en toile de jute sur palettes", "2. Sacs en plastique (Sisal/Synthétique)", "3. Stockage direct au sol / en vrac"]

    # =========================================================================
    # 🔐 PERSISTANCE DU SESSION STATE SÉCURISÉE
    # =========================================================================
    cles_initialisation_p18 = {
        "p18_freq_rec": "14",
        "p18_t_ecab": "2",
        "p18_t_ferm": "6",
        "p18_qualite_f": "",
        "p18_obs_comp": "",
        "p18_mode_ferm": options_fermentation[0],
        "p18_methode_sech": options_sechage[0],
        "p18_brassage": options_brassage[0],
        "p18_tri_calib": options_tri[0],
        "p18_stockage": options_stockage[0]
    }

    for cle, defaut in cles_initialisation_p18.items():
        if cle not in st.session_state:
            st.session_state[cle] = defaut

    def obtenir_index(liste, cle_state):
        valeur = st.session_state[cle_state]
        return liste.index(valeur) if valeur in liste else 0

    # --- EN-TÊTES DU TABLEAU MATRICIEL ---
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="table-header">Éléments d\'observation (Mesures)</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="table-header">Réponses</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="table-header">Éléments d\'observation (Méthodes)</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="table-header">Réponses indépendantes</div>', unsafe_allow_html=True)

    st.write("") 

    # Ligne 1
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Fréquence des récoltes (Espacement en jours)</div>', unsafe_allow_html=True)
    with c2: freq_rec_in = st.text_input("R1", value=st.session_state.p18_freq_rec, label_visibility="collapsed", key="p18_freq_rec_input")
    with c3: st.markdown('<div class="cell-text">Mode de fermentation</div>', unsafe_allow_html=True)
    with c4: mode_ferm_in = st.selectbox("D1", options=options_fermentation, index=obtenir_index(options_fermentation, "p18_mode_ferm"), label_visibility="collapsed", key="p18_mode_ferm_select")

    # Ligne 2
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Temps entre récolte et écabossage (jours)</div>', unsafe_allow_html=True)
    with c2: t_ecab_in = st.text_input("R2", value=st.session_state.p18_t_ecab, label_visibility="collapsed", key="p18_t_ecab_input")
    with c3: st.markdown('<div class="cell-text">Méthodes de Séchage</div>', unsafe_allow_html=True)
    with c4: methode_sech_in = st.selectbox("D2", options=options_sechage, index=obtenir_index(options_sechage, "p18_methode_sech"), label_visibility="collapsed", key="p18_methode_sech_select")

    # Ligne 3
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Durée de la fermentation (jours)</div>', unsafe_allow_html=True)
    with c2: t_ferm_in = st.text_input("R3", value=st.session_state.p18_t_ferm, label_visibility="collapsed", key="p18_t_ferm_input")
    with c3: st.markdown('<div class="cell-text">Technique de Brassage / Retournement</div>', unsafe_allow_html=True)
    with c4: brassage_in = st.selectbox("D3", options=options_brassage, index=obtenir_index(options_brassage, "p18_brassage"), label_visibility="collapsed", key="p18_brassage_select")

    # Ligne 4
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Qualité globale des fèves</div>', unsafe_allow_html=True)
    with c2: qualite_f_in = st.text_input("R4", value=st.session_state.p18_qualite_f, label_visibility="collapsed", key="p18_qualite_f_input")
    with c3: st.markdown('<div class="cell-text">Tri et Calibrage (Post-Séchage)</div>', unsafe_allow_html=True)
    with c4: tri_calib_in = st.selectbox("D4", options=options_tri, index=obtenir_index(options_tri, "p18_tri_calib"), label_visibility="collapsed", key="p18_tri_calib_select")

    # Ligne 5
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Observations complémentaires</div>', unsafe_allow_html=True)
    with c2: obs_comp_in = st.text_input("R5", value=st.session_state.p18_obs_comp, label_visibility="collapsed", key="p18_obs_comp_input")
    with c3: st.markdown('<div class="cell-text">Stockage / Entreposage des fèves</div>', unsafe_allow_html=True)
    with c4: stockage_in = st.selectbox("D5", options=options_stockage, index=obtenir_index(options_stockage, "p18_stockage"), label_visibility="collapsed", key="p18_stockage_select")

    # Synchronisation inverse des données saisies vers l'état
    st.session_state.p18_freq_rec = freq_rec_in
    st.session_state.p18_mode_ferm = mode_ferm_in
    st.session_state.p18_t_ecab = t_ecab_in
    st.session_state.p18_methode_sech = methode_sech_in
    st.session_state.p18_t_ferm = t_ferm_in
    st.session_state.p18_brassage = brassage_in
    st.session_state.p18_qualite_f = qualite_f_in
    st.session_state.p18_tri_calib = tri_calib_in
    st.session_state.p18_obs_comp = obs_comp_in
    st.session_state.p18_stockage = stockage_in

    # =========================================================================
    # 🧠 EXÉCUTION DIRECTE DU SYSTÈME EXPERT LEILA IA
    # =========================================================================
    try:
        freq_rec = float(freq_rec_in) if freq_rec_in else None
        t_ecab = float(t_ecab_in) if t_ecab_in else None
        t_ferm = float(t_ferm_in) if t_ferm_in else None
        
        notes_diagnostic = []
        
        # --- Analyses Chiffrées ---
        if freq_rec is not None:
            if freq_rec > 21: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Fréquence de récolte trop longue ({int(freq_rec)} jours) :</b> Risque élevé de pourriture des cabosses sur l'arbre et d'attaques de bioagresseurs.</li>")
            elif freq_rec < 10: notes_diagnostic.append(f"<li class='status-warning'>⚠️ <b>Fréquence rapprochée ({int(freq_rec)} jours) :</b> Assurez-vous que le taux de maturité des cabosses justifie économiquement le coût de la main-d'œuvre.</li>")
            else: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Fréquence de récolte optimale ({int(freq_rec)} jours) :</b> Parfait pour cueillir le cacao à maturité complète.</li>")

        if t_ecab is not None:
            if t_ecab > 5: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Écabossage très tardif ({int(t_ecab)} jours) :</b> Risque majeur de germination interne des fèves et de développement de moisissures.</li>")
            elif 3 <= t_ecab <= 5: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Pré-stockage des cabosses ({int(t_ecab)} jours) :</b> Pratique agronomique idéale pour abaisser l'acidité naturelle et améliorer le goût.</li>")
            else: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Écabossage rapide ({int(t_ecab)} jours) :</b> Pratique standard correcte préservant l'intégrité de la pulpe.</li>")

        if t_ferm is not None:
            if t_ferm < 5: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Fermentation insuffisante ({int(t_ferm)} jours) :</b> Risque d'un taux élevé de fèves violettes amères et astringentes. Lot non marchand !</li>")
            elif t_ferm > 7: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Fermentation trop longue ({int(t_ferm)} jours) :</b> Risque de sur-fermentation avec apparition d'odeurs ammoniacales et putrides.</li>")
            else: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Durée de fermentation parfaite ({int(t_ferm)} jours) :</b> Transformation biochimique et synthèse aromatique optimales.</li>")

        # --- Analyses des Méthodes Établies ---
        if "bâche" in mode_ferm_in.lower():
            notes_diagnostic.append("<li class='status-warning'>⚠️ <b>Mode fermentation (Bâche plastique) :</b> Forte rétention des jus acides. Leila conseille plutôt l'usage de caisses en bois ou de tas sous bananiers bien drainés.</li>")
        elif "caisses" in mode_ferm_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Fermentation en caisses de bois :</b> Excellente maîtrise thermique et drainage idéal de la sueur du cacao.</li>")
        elif "tas" in mode_ferm_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Fermentation en tas sous bananiers :</b> Méthode traditionnelle efficace assurant une bonne inoculation microbiologique naturelle.</li>")

        if "goudron" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Séchage sur goudron / asphalte : CRITIQUE & INTERDIT !</b> Contamination par les Hydrocarbures Aromatiques Polycycliques (HAP) causée par le bitume chaud. Risque de rejet du lot.</li>")
        elif "sol" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-danger'>❌ <b>Séchage à même le sol : DÉCONSEILLÉ.</b> Exposition directe aux souillures du sol, humidité résiduelle de la terre et développement fongique immédiat.</li>")
        elif "bâche" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-warning'>⚠️ <b>Séchage sur bâche propre : VIGILANCE REQUISE.</b> Isole du sol, mais l'absence de drainage inférieur exige un brassage fréquent pour évacuer l'eau.</li>")
        elif "aire" in methode_sech_in.lower() or "ciment" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Séchage sur aire cimentée : ACCEPTE.</b> Méthode saine si la dalle est isolée et balayée régulièrement. Nécessite des retournements précis.</li>")
        else:
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Séchage sur claies surélevées : DISPOSITIF OPTIMAL (PREMIUM).</b> Ventilation bi-directionnelle accélérant le séchage sans risque sanitaire.</li>")

        if "régulier" in brassage_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Brassage régulier :</b> Température et évaporation parfaitement homogènes sur l'ensemble du lot.</li>")
        elif "insuffisant" in brassage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Brassage insuffisant :</b> Entraîne des écarts de séchage (fèves sèches en surface, humides au cœur).</li>")
        elif "aucun" in brassage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Aucun brassage :</b> Risque critique d'agglomération des fèves en paquets et moisissures internes.</li>")

        if "manuel" in tri_calib_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Tri manuel à plat :</b> Élimination précise des débris physiques, des fèves plates, cassées ou fusionnées.</li>")
        elif "mécanique" in tri_calib_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Tamisage mécanique :</b> Garantit un grainage uniforme respectant parfaitement les standards commerciaux internationaux.</li>")
        elif "aucun" in tri_calib_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Absence complète de tri :</b> Présence d'impuretés. Risque élevé de décote ou de refus direct par la coopérative.</li>")

        if "palettes" in stockage_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Stockage réglementaire conforme :</b> Les sacs de jute sur palettes en bois isolent de l'humidité et permettent au cacao de respirer.</li>")
        elif "plastique" in stockage_in.lower() or "sisal" in stockage_in.lower() or "synthétique" in stockage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Stockage non conforme (Sacs Plastiques) :</b> Confinement de l'humidité résiduelle, altération des graisses et risque de sécrétions d'Ochratoxine A.</li>")
        elif "sol" in stockage_in.lower() or "vrac" in stockage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Stockage en vrac au sol : FORMELLEMENT INTERDIT !</b> Reprise immédiate d'humidité par capillarité et prolifération de rongeurs ou insectes.</li>")

        if notes_diagnostic:
            st.markdown(f"""
            <div class="diagnostic-container">
                <div class="diag-title">🧠 Analyse de Qualité Post-Récolte (Leila IA)</div>
                <ul style="padding-left: 5px; margin: 0;">
                    {"".join(notes_diagnostic)}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    except Exception:
        st.info("Veuillez réajuster les saisies numériques pour mettre à jour l'audit automatisé de Leila.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p18", type="primary", use_container_width=True):
        st.session_state["page_18_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 19
        st.rerun()

    # --- PIED DE PAGE STANDARDISÉ ---
    st.write("---")
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>18</span>", unsafe_allow_html=True)


def dessiner_page_19_intrants():
    # --- CONFIGURATION DU DESIGN ET STRUCTURE DE POUPÉES RUSSES ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-19 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-19 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .section-title { color: #16A085; font-size: 18px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    .cell-label { font-size: 14px; color: #34495E; font-weight: bold; padding-top: 5px; }
    
    /* Structure Box Poupées Russes */
    .pouperee-p19-l1 { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p19-l2 { border-left: 5px solid #2980B9; background-color: #F4F8FA; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p19-l3 { border-left: 5px solid #D35400; background-color: #FFFBF5; padding: 20px; border-radius: 6px; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #16A085; margin-top: 15px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION ---
    st.markdown("""
    <div class="diapo-slide-19">
        <div class="bullet-titre-19">• Suivi des Intrants et Gestion Hygiénique</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    options_engrais_t = ["Aucun", "Minéral (NPK / Boron)", "Organique (Compost/Fiente)", "Bio-stimulant"]
    options_engrais_m = ["Au sol (Couronne)", "Foliaire (Pulvérisation)", "Épandage à la volée"]
    options_applicateur = ["1. Producteur", "2. Applicateur"]
    
    options_phyto_t = ["Aucun", "Insecticide (Anti-mirides)", "Fongicide (Pourriture brune)", "Herbicide"]
    options_phyto_m = ["Atomiseur", "Pulvérisateur"]
    
    options_emballage = [
        "Sélectionner une réponse...",
        "Brûlés au champ ou jetés dans la cacaoyère / près des cours d'eau",
        "Enfouis dans le sol de la parcelle",
        "Rincés 3 fois, percés et stockés dans un bac de récupération sécurisé (Coopérative)",
        "Laissés à l'abandon sur place"
    ]

    # =========================================================================
    # 🔐 PERSISTANCE ET SÉCURISATION DES CLES SESSIONS MULTI-LIGNES
    # =========================================================================
    for i in range(1, 4):
        if f"p19_eng_t{i}" not in st.session_state: st.session_state[f"p19_eng_t{i}"] = options_engrais_t[0]
        if f"p19_eng_n{i}" not in st.session_state: st.session_state[f"p19_eng_n{i}"] = ""
        if f"p19_eng_q{i}" not in st.session_state: st.session_state[f"p19_eng_q{i}"] = ""
        if f"p19_eng_p{i}" not in st.session_state: st.session_state[f"p19_eng_p{i}"] = ""
        if f"p19_eng_m{i}" not in st.session_state: st.session_state[f"p19_eng_m{i}"] = options_engrais_m[0]
        if f"p19_eng_a{i}" not in st.session_state: st.session_state[f"p19_eng_a{i}"] = options_applicateur[0]
        
        if f"p19_phy_t{i}" not in st.session_state: st.session_state[f"p19_phy_t{i}"] = options_phyto_t[0]
        if f"p19_phy_n{i}" not in st.session_state: st.session_state[f"p19_phy_n{i}"] = ""
        if f"p19_phy_q{i}" not in st.session_state: st.session_state[f"p19_phy_q{i}"] = ""
        if f"p19_phy_p{i}" not in st.session_state: st.session_state[f"p19_phy_p{i}"] = ""
        if f"p19_phy_m{i}" not in st.session_state: st.session_state[f"p19_phy_m{i}"] = options_phyto_m[0]
        if f"p19_phy_a{i}" not in st.session_state: st.session_state[f"p19_phy_a{i}"] = options_applicateur[0]

    if "p19_emb_val" not in st.session_state:
        st.session_state.p19_emb_val = options_emballage[0]

    def idx_opt(liste, cle_state):
        val = st.session_state[cle_state]
        return liste.index(val) if val in liste else 0

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des données sur les intrants et emballages", expanded=True):
        st.markdown('<div class="pouperee-p19-l1">', unsafe_allow_html=True)
        
        # --- ENGRAIS ---
        st.markdown('<div class="section-title">❖ Application des engrais</div>', unsafe_allow_html=True)
        saisies_engrais = []
        for i in range(1, 4):
            st.markdown(f"**Ligne Engrais N°{i}**")
            c_e1, c_e2, c_e3, c_e4, c_e5, c_e6 = st.columns([2.0, 1.8, 1.0, 1.2, 1.8, 1.5])
            
            with c_e1: type_engrais = st.selectbox("Type d'engrais", options=options_engrais_t, index=idx_opt(options_engrais_t, f"p19_eng_t{i}"), key=f"p19_eng_t{i}_select")
            with c_e2: nom_engrais = st.text_input("Nom commercial / formule", value=st.session_state[f"p19_eng_n{i}"], key=f"p19_eng_n{i}_input")
            with c_e3: qte_engrais_str = st.text_input("Quantité/an (kg)", value=st.session_state[f"p19_eng_q{i}"], key=f"p19_eng_q{i}_input")
            with c_e4: per_engrais = st.text_input("Période d'apport", value=st.session_state[f"p19_eng_p{i}"], key=f"p19_eng_p{i}_input")
            with c_e5: mode_engrais = st.selectbox("Mode d'apport", options=options_engrais_m, index=idx_opt(options_engrais_m, f"p19_eng_m{i}"), key=f"p19_eng_m{i}_select")
            with c_e6: app_engrais = st.selectbox("Applicateur", options=options_applicateur, index=idx_opt(options_applicateur, f"p19_eng_a{i}"), key=f"p19_eng_a{i}_select")
            
            # Sauvegarde dynamique dans le session_state global
            st.session_state[f"p19_eng_t{i}"] = type_engrais
            st.session_state[f"p19_eng_n{i}"] = nom_engrais
            st.session_state[f"p19_eng_q{i}"] = qte_engrais_str
            st.session_state[f"p19_eng_p{i}"] = per_engrais
            st.session_state[f"p19_eng_m{i}"] = mode_engrais
            st.session_state[f"p19_eng_a{i}"] = app_engrais

            try:
                qte_engrais = float(qte_engrais_str) if qte_engrais_str.strip() != "" else 0.0
            except ValueError:
                qte_engrais = 0.0
                
            saisies_engrais.append({
                "Type d'engrais": type_engrais, "Nom commercial / formule": nom_engrais, "Quantité/an": qte_engrais,
                "Période d'apport": per_engrais, "Mode d'apport (foliaire, au sol)": mode_engrais, "Applicateur": app_engrais
            })

        st.write("---")

        # --- PHYTOSANITAIRES ---
        st.markdown('<div class="section-title">❖ Application de produits phytosanitaires</div>', unsafe_allow_html=True)
        saisies_phy = []
        for i in range(1, 4):
            st.markdown(f"**Ligne Produit Phyto N°{i}**")
            c_p1, c_p2, c_p3, c_p4, c_p5, c_p6 = st.columns([2.0, 1.8, 1.0, 1.2, 1.8, 1.5])
            
            with c_p1: type_phy = st.selectbox("Type de produits", options=options_phyto_t, index=idx_opt(options_phyto_t, f"p19_phy_t{i}"), key=f"p19_phy_t{i}_select")
            with c_p2: nom_phy = st.text_input("Nom commercial / formule", value=st.session_state[f"p19_phy_n{i}"], key=f"p19_phy_n{i}_input")
            with c_p3: qte_phy_str = st.text_input("Quantité / trait.", value=st.session_state[f"p19_phy_q{i}"], key=f"p19_phy_q{i}_input")
            with c_p4: per_phy = st.text_input("Période de traitement", value=st.session_state[f"p19_phy_p{i}"], key=f"p19_phy_p{i}_input")
            with c_p5: mode_phy = st.selectbox("Mode d'appareil", options=options_phyto_m, index=idx_opt(options_phyto_m, f"p19_phy_m{i}"), key=f"p19_phy_m{i}_select")
            with c_p6: app_phy = st.selectbox("Applicateur", options=options_applicateur, index=idx_opt(options_applicateur, f"p19_phy_a{i}"), key=f"p19_phy_a{i}_select")
            
            # Sauvegarde dynamique dans le session_state global
            st.session_state[f"p19_phy_t{i}"] = type_phy
            st.session_state[f"p19_phy_n{i}"] = nom_phy
            st.session_state[f"p19_phy_q{i}"] = qte_phy_str
            st.session_state[f"p19_phy_p{i}"] = per_phy
            st.session_state[f"p19_phy_m{i}"] = mode_phy
            st.session_state[f"p19_phy_a{i}"] = app_phy

            try:
                qte_phy = float(qte_phy_str) if qte_phy_str.strip() != "" else 0.0
            except ValueError:
                qte_phy = 0.0
                
            saisies_phy.append({
                "Type de produits (insecticide, fongicide, herbicide)": type_phy, "Nom commercial / formule": nom_phy, "Quantité / traitement": qte_phy,
                "Période de traitement": per_phy, "Mode d'apport (atomiseur, pulvérisateur)": mode_phy, "Applicateur": app_phy
            })

        st.write("---")

        # --- GESTION DES EMBALLAGES ---
        st.markdown('<div class="section-title">❖ Gestion des emballages</div>', unsafe_allow_html=True)
        c_emb1, c_emb2 = st.columns([3.0, 5.0])
        with c_emb1:
            st.markdown('<div class="cell-label">Que faites-vous des emballages après traitement/application ?</div>', unsafe_allow_html=True)
        with c_emb2:
            reponse_emballage = st.selectbox("Sélectionner une réponse...", options=options_emballage, index=idx_opt(options_emballage, "p19_emb_val"), label_visibility="collapsed", key="p19_emb_val_select")
            st.session_state.p19_emb_val = reponse_emballage

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : MATRICE SYNOPTIQUE / SORTIE DES TABLEAUX (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visuel Tableaux)", expanded=True):
        st.markdown('<div class="pouperee-p19-l2">', unsafe_allow_html=True)
        
        st.markdown("##### 🌿 Matrice de Suivi de l'Application des Engrais")
        df_engrais = pd.DataFrame(saisies_engrais)
        st.dataframe(df_engrais, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 🛡️ Matrice de Suivi des Produits Phytosanitaires")
        df_phyto = pd.DataFrame(saisies_phy)
        st.dataframe(df_phyto, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### ♻️ État de la Gestion Intégrée des Emballages")
        df_emb = pd.DataFrame({
            "Question réglementaire": ["Que faites-vous des emballages après traitement/application ?"],
            "Réponse Encodée": [reponse_emballage]
        })
        st.dataframe(df_emb, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA IA EXPERT / AVIS (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Rapport d'Analyse et Avis Experts de Leila", expanded=True):
        st.markdown('<div class="pouperee-p19-l3">', unsafe_allow_html=True)
        
        # --- NUTRITION DES SOLS ---
        st.markdown('<div class="subsection-analysis-title">🌿 Analyse Expert de la Nutrition</div>', unsafe_allow_html=True)
        compteur_engrais = 0
        for idx, row in enumerate(saisies_engrais):
            type_engrais = row["Type d'engrais"]
            quantite = row["Quantité/an"]
            periode = row["Période d'apport"]
            mode = row["Mode d'apport (foliaire, au sol)"]
            nom_comm = row["Nom commercial / formule"] if row["Nom commercial / formule"] != "" else "Non spécifié"
            
            if type_engrais != "Aucun":
                compteur_engrais += 1
                if "Minéral" in type_engrais:
                    if quantite > 250:
                        st.error(f"❌ **Ligne {idx+1} - [{nom_comm}] ({quantite} kg) :** Surdosage détecté ! Risque de toxicité racinaire accrue et de lixiviation. Leila recommande de recalibrer les doses entre 150 et 200 kg/ha.")
                    elif quantite > 0:
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_comm}] ({quantite} kg) :** Dose agronomique globale bien calibrée.")
                    else:
                        st.warning(f"⚠️ **Ligne {idx+1} - [{nom_comm}] :** Veuillez renseigner une quantité valide pour évaluer l'apport.")
                    
                    if any(m in periode.lower() for m in ["mai", "juin", "avril"]):
                        st.success(f" └─ 🟢 **Période ({periode}) :** Timing idéal. Correspond à la grande saison des pluies en Côte d'Ivoire, favorisant la solubilisation.")
                    elif periode != "":
                        st.warning(f" └─ ⚠️ **Période ({periode}) :** Risque de faible assimilation. L'engrais minéral requiert une humidité constante du sol.")
                    
                    if "couronne" in mode.lower() or "sol" in mode.lower():
                        st.success(f" └─ 🟢 **Mode d'apport ({mode}) :** Localisation validée. Engrais directement orienté vers le système racinaire absorbant.")
                    elif "volée" in mode.lower():
                        st.warning(f" └─ ⚠️ **Mode d'apport ({mode}) :** L'épandage à la volée favorise la volatilisation de l'azote et accélère la pousse des adventices.")
                        
                elif "Organique" in type_engrais:
                    st.success(f"🟢 **Ligne {idx+1} - [{nom_comm}] ({quantite} kg) :** Excellent choix technique pour restructurer durablement l'humus et stimuler la vie biologique du sol.")
                elif "Bio-stimulant" in type_engrais:
                    if "foliaire" in mode.lower():
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_comm}] :** Application foliaire validée pour limiter l'impact des stress hydriques.")
                    else:
                        st.error(f"❌ **Ligne {idx+1} - [{nom_comm}] :** L'apport au sol est inefficace pour ce type de bio-stimulant. Leila préconise une pulvérisation foliaire directe.")
        if compteur_engrais == 0:
            st.info("💡 Aucun apport de fertilisant enregistré pour le moment.")

        # --- PROTECTION DES CULTURES ---
        st.markdown('<div class="subsection-analysis-title">🛡️ Analyse Expert de la Protection des Cultures</div>', unsafe_allow_html=True)
        compteur_phyto = 0
        for idx, row in enumerate(saisies_phy):
            type_phyto = row["Type de produits (insecticide, fongicide, herbicide)"]
            nom_commercial = row["Nom commercial / formule"] if row["Nom commercial / formule"] != "" else "Non spécifié"
            mode_appareil = row["Mode d'apport (atomiseur, pulvérisateur)"]
            
            if type_phyto != "Aucun":
                compteur_phyto += 1
                if "Insecticide" in type_phyto:
                    if "atomiseur" in mode_appareil.lower():
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_commercial}] :** Matériel de traitement validé. L'atomiseur est obligatoire pour saturer la canopée et détruire efficacement les mirides (capsides).")
                    else:
                        st.error(f"❌ **Ligne {idx+1} - [{nom_commercial}] :** Pulvérisateur manuel inadapté en hauteur. La canopée ne sera pas protégée contre les attaques de ravageurs.")
                elif "Fongicide" in type_phyto:
                    if "atomiseur" in mode_appareil.lower():
                        st.warning(f"⚠️ **Ligne {idx+1} - [{nom_commercial}] :** Risque de perte par dérive aérienne. Privilégiez le pulvérisateur manuel pour bien cibler les troncs et les cabosses (Lutte contre la Pourriture brune).")
                    else:
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_commercial}] :** Application ciblée au pulvérisateur manuel validée.")
                elif "Herbicide" in type_phyto:
                    st.error(f"🚨 **Ligne {idx+1} - [{nom_commercial}] : Pratique critique fortement déconseillée !** Détruit la microfaune utile et expose les sols à l'érosion. Privilégiez un nettoyage mécanique raisonné à la machette.")
        if compteur_phyto == 0:
            st.info("💡 Aucun produit phytosanitaire appliqué sur la parcelle.")

        # --- CRITÈRES DE CERTIFICATION ET ENVIRONNEMENT ---
        st.markdown('<div class="subsection-analysis-title">♻️ Analyse Environnementale & Normes de Durabilité</div>', unsafe_allow_html=True)
        if "Sélectionner" in reponse_emballage or reponse_emballage == "":
            st.info("💡 En attente de déclaration sur la gestion des emballages vides.")
        elif "Brûlés" in reponse_emballage or "Laissés" in reponse_emballage:
            st.error(f"🚨 **Point de blocage éliminatoire :** Brûler ou abandonner les emballages pollue gravement l'écosystème et viole directement les exigences des normes durables (ex: Rainforest Alliance).")
        elif "Enfouis" in reponse_emballage:
            st.error(f"🚨 **Non-conformité environnementale majeure :** L'enfouissement accumule les résidus chimiques et les molécules toxiques dans le sous-sol et les nappes phréatiques.")
        elif "Rincés" in reponse_emballage:
            st.success("🟢 **Conformité Parfaite :** Le protocole de triple rinçage, perçage pour destruction et stockage centralisé en coopérative répond parfaitement aux exigences de durabilité.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p19", type="primary", use_container_width=True):
        st.session_state["page_19_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 20
        st.rerun()

    # --- PIED DE PAGE STANDARDISÉ ---
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>19</span>", unsafe_allow_html=True)

def dessiner_page_20_socio_economique():
    # --- CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-20 {
        background-color: #C6E0B4; /* Vert institutionnel standardisé */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 25px;
    }
    .bullet-titre-20 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .blue-fiche { color: #2980B9; font-weight: bold; }
    
    .bullet-list-p20 { font-size: 16px; color: #2C3E50; line-height: 1.8; margin-left: 10px; margin-top: 15px;}
    .bullet-item-p20 { margin-bottom: 12px; list-style-position: inside; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-20">
        <div class="bullet-titre-20">D - Données Socio-économiques <span class="blue-fiche">(Fiche 4)</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # Liste des puces textuellement conformes
    st.markdown("""
    <ul class="bullet-list-p20">
        <li class="bullet-item-p20">Caractérisation de l'unité familiale de production (rôle de chaque membre),</li>
        <li class="bullet-item-p20">Le revenu tiré du cacao et des autres activités,</li>
        <li class="bullet-item-p20">Les dépenses courantes du ménage,</li>
        <li class="bullet-item-p20">Les relations avec les partenaires financiers et commerciaux,</li>
        <li class="bullet-item-p20">Le coût de la main-d'œuvre (ressources financières et humaines pour faire face au nouvel investissement que nécessite la mise en œuvre du PDC).</li>
    </ul>
    """, unsafe_allow_html=True)

    # Espacement pour pousser le numéro de page vers le bas
    st.write("<br><br><br><br><br><br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p20", type="primary", use_container_width=True):
        st.session_state["page_20_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 21
        st.rerun()

    # --- PIED DE PAGE ET NUMÉRO DE PAGE HARMONISÉ ---
    st.write("---")
    col_space, col_num = st.columns([0.95, 0.05])
    with col_num:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>20</span>", unsafe_allow_html=True)
