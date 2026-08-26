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



def dessiner_page_21_Finance_Production():
    # --- CONFIGURATION DU DESIGN ET STRUCTURES EN POUPÉES RUSSES ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-21 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-21 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-p21 { background-color: #1F4E78; color: white; padding: 6px 14px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 14px; }
    .section-title-p21 { color: #16A085; font-size: 18px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    
    /* Structure Box Poupées Russes */
    .pouperee-p21-l1 { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p21-l2 { border-left: 5px solid #2980B9; background-color: #F4F8FA; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p21-l3 { border-left: 5px solid #D35400; background-color: #FFFBF5; padding: 20px; border-radius: 6px; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #16A085; margin-top: 15px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-21">
        <div class="bullet-titre-21">❖ D - Données Socio-économiques (Fiche 4)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="badge-p21">💳 Compte d\'épargne, Financement & Revenus</div>', unsafe_allow_html=True)

    types_epargne = ["Mobile Money", "Microfinance", "Banque", "Autres"]
    annees_cacao = ["Année N-1", "Année N-2", "Année N-3"]

    # =========================================================================
    # 🔐 PERSISTANCE ET SÉCURISATION DES CLÉS MULTI-LIGNES DU SESSION STATE
    # =========================================================================
    for ep in types_epargne:
        cle_ep = ep.replace(" ", "_").lower()
        if f"p21_hc_{cle_ep}" not in st.session_state: st.session_state[f"p21_hc_{cle_ep}"] = "Non"
        if f"p21_ha_{cle_ep}" not in st.session_state: st.session_state[f"p21_ha_{cle_ep}"] = "Non"
        if f"p21_hf_{cle_ep}" not in st.session_state: st.session_state[f"p21_hf_{cle_ep}"] = "Non"
        if f"p21_mt_{cle_ep}" not in st.session_state: st.session_state[f"p21_mt_{cle_ep}"] = 0

    for an in annees_cacao:
        cle_an = an.replace(" ", "_").replace("-", "_").lower()
        if f"p21_prod_{cle_an}" not in st.session_state: st.session_state[f"p21_prod_{cle_an}"] = 0
        if f"p21_rev_{cle_an}" not in st.session_state: st.session_state[f"p21_rev_{cle_an}"] = 0

    for i in range(1, 3):
        if f"p21_act_n_{i}" not in st.session_state: st.session_state[f"p21_act_n_{i}"] = ""
        if f"p21_act_p_{i}" not in st.session_state: st.session_state[f"p21_act_p_{i}"] = ""
        if f"p21_act_r_{i}" not in st.session_state: st.session_state[f"p21_act_r_{i}"] = 0

    def obtenir_idx_radio(options, valeur_actuelle):
        return options.index(valeur_actuelle) if valeur_actuelle in options else 0

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des données financières et de production", expanded=True):
        st.markdown('<div class="pouperee-p21-l1">', unsafe_allow_html=True)
        
        # --- SOUS-SECTION 1 : COMPTE D'ÉPARGNE ET FINANCEMENT ---
        st.markdown('<div class="section-title-p21">❖ 1. Compte d\'épargne et Financement</div>', unsafe_allow_html=True)
        saisies_epargne = []
        options_radio = ["Non", "Oui"]
        
        for ep in types_epargne:
            cle_ep = ep.replace(" ", "_").lower()
            st.markdown(f"**Option d'Épargne : {ep}**")
            c_ep1, c_ep2, c_ep3, c_ep4 = st.columns([2.5, 2.5, 2.5, 2.5])
            
            with c_ep1: 
                has_compte = st.radio("Avez-vous un compte ?", options_radio, index=obtenir_idx_radio(options_radio, st.session_state[f"p21_hc_{cle_ep}"]), horizontal=True, key=f"p21_hc_{cle_ep}_input")
            
            with c_ep2: 
                if has_compte == "Oui":
                    has_argent = st.radio("Argent sur le compte ?", options_radio, index=obtenir_idx_radio(options_radio, st.session_state[f"p21_ha_{cle_ep}"]), horizontal=True, key=f"p21_ha_{cle_ep}_input")
                else:
                    st.text_input("Argent sur le compte ?", value="N/A", disabled=True, key=f"p21_ha_dis_{cle_ep}")
                    has_argent = "Non"
            
            with c_ep3: 
                has_finance = st.radio("Bénéficié de financement ?", options_radio, index=obtenir_idx_radio(options_radio, st.session_state[f"p21_hf_{cle_ep}"]), horizontal=True, key=f"p21_hf_{cle_ep}_input")
            
            with c_ep4: 
                if has_finance == "Oui":
                    montant_fin = st.number_input("Montant (FCFA)", min_value=0, step=5000, value=st.session_state[f"p21_mt_{cle_ep}"], key=f"p21_mt_{cle_ep}_input")
                else:
                    st.text_input("Montant (FCFA)", value="0", disabled=True, key=f"p21_mt_dis_{cle_ep}")
                    montant_fin = 0
            
            # Synchro Session State
            st.session_state[f"p21_hc_{cle_ep}"] = has_compte
            st.session_state[f"p21_ha_{cle_ep}"] = has_argent
            st.session_state[f"p21_hf_{cle_ep}"] = has_finance
            st.session_state[f"p21_mt_{cle_ep}"] = montant_fin

            saisies_epargne.append({
                "Type d'Épargne": ep,
                "Possède un compte": has_compte,
                "Solde positif (Argent disponible)": has_argent,
                "Financement obtenu": has_finance,
                "Montant du financement (FCFA)": montant_fin
            })
            
        st.write("---")

        # --- SOUS-SECTION 2 : PRODUCTION DE CACAO ---
        st.markdown('<div class="section-title-p21">❖ 2. Production de cacao des trois (3) dernières années</div>', unsafe_allow_html=True)
        saisies_production = []
        
        c_h1, c_h2, c_h3 = st.columns([3, 3, 4])
        with c_h2: st.markdown("<span style='font-size:13px; font-weight:bold; color:#7F8C8D;'>Production (kg)</span>", unsafe_allow_html=True)
        with c_h3: st.markdown("<span style='font-size:13px; font-weight:bold; color:#7F8C8D;'>Revenu brut (FCFA)</span>", unsafe_allow_html=True)

        for an in annees_cacao:
            cle_an = an.replace(" ", "_").replace("-", "_").lower()
            c_p1, c_p2, c_p3 = st.columns([3, 3, 4])
            with c_p1: 
                st.markdown(f"<div style='padding-top:10px; font-weight:bold; color:#2C3E50;'>{an} :</div>", unsafe_allow_html=True)
            with c_p2: 
                prod_kg = st.number_input(f"Production (kg) - {an}", min_value=0, step=50, value=st.session_state[f"p21_prod_{cle_an}"], label_visibility="collapsed", key=f"p21_prod_{cle_an}_input")
            with c_p3: 
                rev_brut = st.number_input(f"Revenu brut (FCFA) - {an}", min_value=0, step=25000, value=st.session_state[f"p21_rev_{cle_an}"], label_visibility="collapsed", key=f"p21_rev_{cle_an}_input")
            
            st.session_state[f"p21_prod_{cle_an}"] = prod_kg
            st.session_state[f"p21_rev_{cle_an}"] = rev_brut

            saisies_production.append({
                "ANNÉE": an,
                "Production (kg)": prod_kg,
                "Revenu brut (FCFA)": rev_brut
            })

        st.write("---")

        # --- SOUS-SECTION 3 : SOURCES DE REVENUS ALTERNATIVES ---
        st.markdown('<div class="section-title-p21">❖ 3. Sources de revenus autres que le cacao</div>', unsafe_allow_html=True)
        saisies_autres = []
        
        for i in range(1, 3):
            st.markdown(f"**Activité alternative N°{i}**")
            c_a1, c_a2, c_a3 = st.columns([4, 3, 3])
            with c_a1: 
                nom_act = st.text_input(f"Nom / Type de l'activité {i}", value=st.session_state[f"p21_act_n_{i}"], key=f"p21_act_n_{i}_input")
            with c_a2: 
                prod_act = st.text_input(f"Production moyenne annuelle {i}", placeholder="Ex: 500 régimes", value=st.session_state[f"p21_act_p_{i}"], key=f"p21_act_p_{i}_input")
            with c_a3: 
                rev_act = st.number_input(f"Revenu brut moyen/an (FCFA) {i}", min_value=0, step=10000, value=st.session_state[f"p21_act_r_{i}"], key=f"p21_act_r_{i}_input")
            
            st.session_state[f"p21_act_n_{i}"] = nom_act
            st.session_state[f"p21_act_p_{i}"] = prod_act
            st.session_state[f"p21_act_r_{i}"] = rev_act

            saisies_autres.append({
                "ACTIVITÉ": nom_act if nom_act.strip() != "" else f"Activité {i}",
                "Production moyenne annuelle": prod_act if prod_act.strip() != "" else "Non spécifiée",
                "Revenu brut moyen/an (FCFA)": rev_act
            })

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : MATRICE SYNOPTIQUE / SORTIE DES TABLEAUX (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visuel Tableaux)", expanded=True):
        st.markdown('<div class="pouperee-p21-l2">', unsafe_allow_html=True)
        
        st.markdown("##### 💳 Matrice de Suivi de l'Épargne et du Financement Agricole")
        df_epargne = pd.DataFrame(saisies_epargne)
        st.dataframe(df_epargne, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 📉 Évolution Triennale de la Production Cacaoyère")
        df_production = pd.DataFrame(saisies_production)
        st.dataframe(df_production, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 🌾 État des Flux de Revenus de Diversification")
        df_autres = pd.DataFrame(saisies_autres)
        st.dataframe(df_autres, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA IA EXPERT / AVIS (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Rapport d'Analyse et Avis Experts de Leila IA", expanded=True):
        st.markdown('<div class="pouperee-p21-l3">', unsafe_allow_html=True)
        
        # --- LEILA : ANALYSE FINANCIÈRE & BANCARISATION ---
        st.markdown('<div class="subsection-analysis-title">💳 Bancarisation & Capacité de Financement (Leila IA)</div>', unsafe_allow_html=True)
        comptes_actifs = [r["Type d'Épargne"] for r in saisies_epargne if r["Possède un compte"] == "Oui"]
        financements_recus = sum(r["Montant du financement (FCFA)"] for r in saisies_epargne)
        
        if len(comptes_actifs) == 0:
            st.error("🚨 **Alerte exclusion financière :** Le producteur ne possède aucun compte d'épargne (ni Mobile Money, ni banque). Cela bloque toute éligibilité au versement électronique des primes de durabilité et limite l'accès aux crédits de campagne.")
        else:
            comptes_str = ", ".join(comptes_actifs)
            st.success(f"🟢 **Profil d'inclusion validé :** Producteur connecté au réseau financier via : **{comptes_str}**.")
            
        if financements_recus > 0:
            st.info(f"💰 **Levier de crédit :** Un financement externe total de **{financements_recus:,.0f} FCFA** a été mobilisé. Assurez-vous que le calendrier de remboursement coïncide avec les pics des récoltes de la grande campagne.")
        else:
            st.warning("⚠️ **Absence de soutien financier :** Aucun financement externe enregistré. L'autofinancement total ralentit les capacités de régénération ou d'achat d'intrants homologués.")

        # --- LEILA : ANALYSE DES PERFORMANCES CACAO ---
        st.markdown('<div class="subsection-analysis-title">📉 Diagnostic de Productivité Cacaoyère (Leila IA)</div>', unsafe_allow_html=True)
        
        p_n1 = saisies_production[0]["Production (kg)"]
        p_n2 = saisies_production[1]["Production (kg)"]
        p_n3 = saisies_production[2]["Production (kg)"]
        
        r_n1 = saisies_production[0]["Revenu brut (FCFA)"]
        r_n2 = saisies_production[1]["Revenu brut (FCFA)"]
        r_n3 = saisies_production[2]["Revenu brut (FCFA)"]
        
        tous_revenus_cacao = [r_n1, r_n2, r_n3]
        revenus_valides = [r for r in tous_revenus_cacao if r > 0]
        
        if len(revenus_valides) > 0:
            revenu_moyen_cacao = sum(revenus_valides) / len(revenus_valides)
            st.success(f"💰 **Revenu annuel moyen (Cacao) :** {revenu_moyen_cacao:,.0f} FCFA.")
            
            # Analyse des tendances de rendement triennal (N-3 -> N-2 -> N-1)
            if p_n3 > p_n2 > p_n1 and p_n1 > 0:
                st.error("🚨 **Alerte de baisse continue de rendement :** La production chute d'année en d'année ! Leila IA conseille d'auditer d'urgence le taux de sénescence (vieillissement) du verger ou l'extension latente de foyers du Swollen Shoot.")
            elif p_n1 > p_n2 and p_n2 > 0:
                st.success("📈 **Dynamique de production positive :** Hausse des rendements constatée sur la dernière campagne. Maintenir l'itinéraire technique actuel.")
        else:
            st.info("💡 Complétez les données de production des campagnes pour activer les graphiques de performance de Leila IA.")

        # --- LEILA : ANALYSE DE LA DIVERSIFICATION DES REVENUS ---
        st.markdown('<div class="subsection-analysis-title">🌾 Résilience Économique et Diversification (Leila IA)</div>', unsafe_allow_html=True)
        revenu_annexe_total = sum(r["Revenu brut moyen/an (FCFA)"] for r in saisies_autres)
        
        if revenu_annexe_total == 0:
            st.warning("⚠️ **Dépendance exclusive (Monoculture) :** 100% du budget repose sur le cacao. Le ménage est hautement vulnérable aux fluctuations des cours mondiaux ou aux aléas climatiques locaux. Leila IA préconise vivement de développer des cultures vivrières de contre-saison (piment, gombo) ou du petit élevage.")
        else:
            st.success(f"🍏 **Diversification validée :** Les sources annexes génèrent **{revenu_annexe_total:,.0f} FCFA / an**. Cette stratégie sécurise les dépenses courantes en période de soudure cacaoyère.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p21", type="primary", use_container_width=True):
        st.session_state["page_21_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 22
        st.rerun()

    # --- PIED DE PAGE ET PAGINATION REGLEMENTAIRE HARMONISÉE A 21 ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>21</span>", unsafe_allow_html=True)



def dessiner_page_22_Depenses_Et_Main_Doeuvre():
    # --- 1. CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-22 {
        background-color: #C6E0B4; /* Vert institutionnel standardisé */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .main-title-p22 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-p22 { background-color: #1F4E78; color: white; padding: 6px 14px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 14px; }
    .section-title-p22 { color: #16A085; font-size: 18px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    
    /* Structure Box Poupées Russes */
    .pouperee-p22-l1 { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p22-l2 { border-left: 5px solid #2980B9; background-color: #F4F8FA; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p22-l3 { border-left: 5px solid #D35400; background-color: #FFFBF5; padding: 20px; border-radius: 6px; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #16A085; margin-top: 15px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-22">
        <div class="main-title-p22">❖ D - Données Socio-économiques (Suite)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="badge-p22">🏠 Dépenses du foyer & 👥 Coût de la main d\'œuvre</div>', unsafe_allow_html=True)

    # Définition des structures de données fixes
    postes_depenses = [
        {"label": "Scolarité", "perio": "année"},
        {"label": "Nourriture", "perio": "mois"},
        {"label": "Santé", "perio": "année"},
        {"label": "Électricité", "perio": "2 mois"},
        {"label": "Eau courante", "perio": "mois"},
        {"label": "Charges sociales (Funérailles, mariage, baptême...)", "perio": "année"}
    ]
    categories_mo = ["Travailleur 1", "Travailleur 2", "Travailleur n", "Groupe de travail"]
    options_statut_mo = ["Non spécifié", "Mo permanente", "Mo occasionnelle", "Non rémunérée (familiale)"]
    options_sexe = ["M", "F"]

    # =========================================================================
    # 🔐 PERSISTANCE ET SÉCURISATION DES CLÉS DU SESSION STATE
    # =========================================================================
    for dp in postes_depenses:
        cle_dp = dp['label'].replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").replace(".", "").lower()
        if f"p22_mt_{cle_dp}" not in st.session_state: 
            st.session_state[f"p22_mt_{cle_dp}"] = 0

    for mo in categories_mo:
        cle_mo = mo.replace(" ", "_").lower()
        if f"p22_statut_{cle_mo}" not in st.session_state: st.session_state[f"p22_statut_{cle_mo}"] = "Non spécifié"
        if f"p22_sexe_{cle_mo}" not in st.session_state: st.session_state[f"p22_sexe_{cle_mo}"] = "M"
        if f"p22_temps_{cle_mo}" not in st.session_state: st.session_state[f"p22_temps_{cle_mo}"] = 0
        if f"p22_cout_{cle_mo}" not in st.session_state: st.session_state[f"p22_cout_{cle_mo}"] = 0

    def obtenir_idx_selection(options, valeur_actuelle):
        return options.index(valeur_actuelle) if valeur_actuelle in options else 0

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des dépenses domestiques et charges de main d'œuvre", expanded=True):
        st.markdown('<div class="pouperee-p22-l1">', unsafe_allow_html=True)
        
        # --- SOUS-SECTION 1 : DÉPENSES COURANTES DU FOYER ---
        st.markdown('<div class="section-title-p22">❖ 1. Dépenses courantes du foyer</div>', unsafe_allow_html=True)
        saisies_depenses = []
        
        for dp in postes_depenses:
            cle_dp = dp['label'].replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").replace(".", "").lower()
            c_dp1, c_dp2, c_dp3 = st.columns([4, 2, 4])
            
            with c_dp1:
                st.markdown(f"<div style='padding-top:10px; font-weight:bold; color:#2C3E50;'>{dp['label']}</div>", unsafe_allow_html=True)
            with c_dp2:
                st.markdown(f"<div style='padding-top:10px; color:#7F8C8D; font-style:italic;'>par {dp['perio']}</div>", unsafe_allow_html=True)
            with c_dp3:
                montant_base = st.number_input(f"Montant ({dp['label']})", min_value=0, step=5000, value=st.session_state[f"p22_mt_{cle_dp}"], label_visibility="collapsed", key=f"p22_mt_{cle_dp}_input")
            
            st.session_state[f"p22_mt_{cle_dp}"] = montant_base

            # Normalisation annuelle
            if dp['perio'] == "année":
                montant_annuel = montant_base
            elif dp['perio'] == "mois":
                montant_annuel = montant_base * 12
            elif dp['perio'] == "2 mois":
                montant_annuel = montant_base * 6
                
            saisies_depenses.append({
                "Poste de Dépenses": dp['label'],
                "Périodicité d'origine": dp['perio'],
                "Montant saisi (FCFA)": montant_base,
                "Montant calculé / an (FCFA)": montant_annuel
            })
            
        st.write("---")

        # --- SOUS-SECTION 2 : COÛT DE LA MAIN D'ŒUVRE ---
        st.markdown('<div class="section-title-p22">❖ 2. Coût de la main d\'œuvre</div>', unsafe_allow_html=True)
        saisies_mo = []
        
        for mo in categories_mo:
            cle_mo = mo.replace(" ", "_").lower()
            st.markdown(f"**Profil de main d'œuvre : {mo}**")
            c_mo1, c_mo2, c_mo3, c_mo4 = st.columns([3, 2, 2, 3])
            
            with c_mo1:
                statut_mo = st.selectbox(f"Statut ({mo})", options_statut_mo, index=obtenir_idx_selection(options_statut_mo, st.session_state[f"p22_statut_{cle_mo}"]), key=f"p22_statut_{cle_mo}_input")
            with c_mo2:
                sexe_mo = st.selectbox(f"Sexe ({mo})", options_sexe, index=obtenir_idx_selection(options_sexe, st.session_state[f"p22_sexe_{cle_mo}"]), key=f"p22_sexe_{cle_mo}_input")
            with c_mo3:
                temps_j = st.number_input(f"Temps ({mo} jours/an)", min_value=0, step=5, value=st.session_state[f"p22_temps_{cle_mo}"], key=f"p22_temps_{cle_mo}_input")
            with c_mo4:
                if statut_mo == "Non rémunérée (familiale)":
                    st.text_input(f"Coût ({mo} FCFA/an)", value="0 (Familial)", disabled=True, key=f"p22_cout_dis_{cle_mo}")
                    cout_annuel = 0
                else:
                    cout_annuel = st.number_input(f"Coût ({mo} FCFA/an)", min_value=0, step=10000, value=st.session_state[f"p22_cout_{cle_mo}"], key=f"p22_cout_{cle_mo}_input")
            
            # Synchronisation Session State
            st.session_state[f"p22_statut_{cle_mo}"] = statut_mo
            st.session_state[f"p22_sexe_{cle_mo}"] = sexe_mo
            st.session_state[f"p22_temps_{cle_mo}"] = temps_j
            st.session_state[f"p22_cout_{cle_mo}"] = cout_annuel

            saisies_mo.append({
                "Travailleur": mo,
                "Mo permanente": "X" if statut_mo == "Mo permanente" else "",
                "Mo occasionnelle": "X" if statut_mo == "Mo occasionnelle" else "",
                "Non rémunérée (familiale)": "X" if statut_mo == "Non rémunérée (familiale)" else "",
                "Sexe": sexe_mo,
                "Coût annuel (FCFA)": cout_annuel,
                "Temps de travail (jours)": temps_j
            })
                
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : MATRICE SYNOPTIQUE / SORTIE DES TABLEAUX (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visuel Tableaux)", expanded=True):
        st.markdown('<div class="pouperee-p22-l2">', unsafe_allow_html=True)
        
        st.markdown("##### 🛒 Matrice Analytique des Dépenses Courantes du Foyer")
        df_depenses = pd.DataFrame(saisies_depenses)
        st.dataframe(df_depenses, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 👥 Grille Structurelle et Coûts de la Main d'Œuvre")
        df_mo = pd.DataFrame(saisies_mo)
        cols_ordre = ["Travailleur", "Mo permanente", "Mo occasionnelle", "Non rémunérée (familiale)", "Sexe", "Coût annuel (FCFA)", "Temps de travail (jours)"]
        st.dataframe(df_mo[cols_ordre], use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA IA / DIAGNOSTIC (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Rapport d'Analyse et Avis Experts de Leila IA", expanded=True):
        st.markdown('<div class="pouperee-p22-l3">', unsafe_allow_html=True)
        
        total_depenses_foyer = sum(r["Montant calculé / an (FCFA)"] for r in saisies_depenses)
        total_charges_mo = sum(r["Coût annuel (FCFA)"] for r in saisies_mo)
        total_jours_mo = sum(r["Temps de travail (jours)"] for r in saisies_mo)
        
        # --- LEILA : DIAGNOSTIC DES CHARGES DOMESTIQUES ---
        st.markdown('<div class="subsection-analysis-title">🛒 Structure du Budget Logistique Familial (Leila IA)</div>', unsafe_allow_html=True)
        if total_depenses_foyer > 0:
            st.info(f"📊 **Charges domestiques :** Les charges de vie incompressibles estimées pour le maintien du foyer s'élèvent à **{total_depenses_foyer:,.0f} FCFA / an**.")
            
            scolarite_row = next((r for r in saisies_depenses if r["Poste de Dépenses"] == "Scolarité"), None)
            if scolarite_row and scolarite_row["Montant saisi (FCFA)"] == 0:
                st.warning("⚠️ **Vigilance Éthique & Sociale :** La ligne de dépense 'Scolarité' est nulle. S'il y a présence d'enfants en âge scolaire au sein du ménage, veillez à auditer l'absence de travail des enfants sur les parcelles (Critère de tolérance zéro de la norme Rainforest Alliance).")
        else:
            st.info("💡 En attente des données budgétaires domestiques pour amorcer l'évaluation du niveau de vie.")

        # --- LEILA : BILAN IMPACT MAIN D'ŒUVRE ---
        st.markdown('<div class="subsection-analysis-title">👥 Évaluation Opérationnelle de la Main d\'œuvre (Leila IA)</div>', unsafe_allow_html=True)
        if total_jours_mo > 0:
            st.success(f"⚡ **Volume de travail absorbé :** La conduite des parcelles requiert **{total_jours_mo} hommes-jours / an** pour matérialiser le calendrier technique.")
            if total_charges_mo > 0:
                cout_moyen_jour = total_charges_mo / total_jours_mo
                st.info(f"💵 **Valeur moyenne de la tâche :** Le coût unitaire journalier de la force de travail externe équivaut à **{cout_moyen_jour:,.0f} FCFA / jour**.")
            
            fam_unites = sum(1 for r in saisies_mo if r["Non rémunérée (familiale)"] == "X")
            if fam_unites > 0:
                st.warning(f"💡 **Indice d'implication endogène :** L'exploitation intègre {fam_unites} ligne(s) de main d'œuvre familiale d'entraide. Utile pour la trésorerie de campagne, cette configuration demande un suivi rigoureux de la charge globale imposée aux proches.")
        else:
            st.warning("⚠️ **Indicateurs manquants :** Aucun volume temporel (jours/an) n'est consigné. Calcul de l'efficience économique suspendu.")

        # --- LEILA : SYNTHÈSE DES CHARGES OUT ---
        st.markdown('<div class="subsection-analysis-title">📉 Balance Consolide des Sorties (Leila IA)</div>', unsafe_allow_html=True)
        sorties_totales = total_depenses_foyer + total_charges_mo
        if sorties_totales > 0:
            st.markdown(f"**Cumul annuel des sorties financières (Foyer + Exploitation) :** <span style='color:#C0392B; font-weight:bold;'>{sorties_totales:,.0f} FCFA / an</span>", unsafe_allow_html=True)
            st.caption("Leila IA croisera automatiquement cette matrice de flux sortants avec le revenu brut calculé en page 21 afin de déterminer le solde net disponible de l'unité de production.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p22", type="primary", use_container_width=True):
        st.session_state["page_22_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 23
        st.rerun()

    # --- PIED DE PAGE ET PAGINATION HARMONISÉE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>22</span>", unsafe_allow_html=True)


def dessiner_page_23_Analyse_Des_Problemes():
    # --- 1. CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-23 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 25px;
    }
    .main-title-p23 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-p23 { background-color: #1F4E78; color: white; padding: 6px 14px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 14px; }
    
    /* Structure d'encadrement institutionnel standardisé */
    .pouperee-p23-cadre { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 25px; border-radius: 6px; margin-bottom: 15px; }
    
    .bullet-list-p23 { font-size: 16px; color: #2C3E50; line-height: 1.8; margin-left: 10px; }
    .bullet-item-p23 { margin-bottom: 12px; list-style-position: inside; font-weight: 500; }
    .bullet-item-p23 strong { color: #1F4E78; }
    
    .sub-section-title-p23 { color: #16A085; font-size: 19px; font-weight: bold; margin-top: 25px; margin-bottom: 15px; border-bottom: 2px solid #16A085; padding-bottom: 6px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-23">
        <div class="main-title-p23">❖ 2.4.2 ANALYSE DES PROBLÈMES</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="badge-p23">📋 Cadre Méthodologique du Diagnostic de l\'Exploitation</div>', unsafe_allow_html=True)

    # --- CONTENU PRINCIPAL ENCADRÉ ---
    st.markdown('<div class="pouperee-p23-cadre">', unsafe_allow_html=True)
    
    st.markdown("""
    <ul class="bullet-list-p23">
        <li class="bullet-item-p23">Ressortir les principales contraintes, les causes et les conséquences sur la cacaoyère.</li>
        <li class="bullet-item-p23">Classer les contraintes par domaine (Technique, Socio-économique, Environnemental).</li>
        <li class="bullet-item-p23">Déterminer les solutions à mettre en œuvre, en vue de rendre l'exploitation économiquement, socialement et environnementalement viable et de se conformer aux exigences de la norme de certification.</li>
    </ul>
    """, unsafe_allow_html=True)
    
    # --- SOUS-SECTION DIAGNOSTIC (Nettoyage structurel complet) ---
    st.markdown('<div class="sub-section-title-p23">Le diagnostic de la cacaoyère conduit à la prise de décision sur :</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <ul class="bullet-list-p23" style="margin-top: 10px;">
        <li class="bullet-item-p23"><strong>La réhabilitation :</strong> Recépage, taille de restructuration, densification.</li>
        <li class="bullet-item-p23"><strong>La replantation :</strong> Renouvellement total de la parcelle fatiguée ou sénescente.</li>
        <li class="bullet-item-p23"><strong>La reconversion :</strong> Changement de culture si le sol ou les contraintes climatiques ne répondent plus aux exigences du cacao.</li>
        <li class="bullet-item-p23"><strong>La poursuite des BPA :</strong> Application continue des Bonnes Pratiques Agricoles sur plantation saine.</li>
        <li class="bullet-item-p23"><strong>La diversification :</strong> Introduction structurée d'arbres d'ombrage utiles et intégration de cultures vivrières intermédiaires.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p23", type="primary", use_container_width=True):
        st.session_state["page_23_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 24
        st.rerun()

    # --- PIED DE PAGE ET NUMÉRO DE PAGE HARMONISÉ ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    _, col_p = st.columns([0.95, 0.05])
    with col_p:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>23</span>", unsafe_allow_html=True)



def dessiner_page_24_Grille_Decision():
    # --- 1. INITIALISATION DE LA MÉMOIRE DE SESSION (PERSISTANCE ATOMIQUE) ---
    cles_checkbox = [
        "age_plus_30", "age_moins_30", 
        "densite_inf_800", "densite_800_1000", 
        "rendement_inf_400", "rendement_sup_400",
        "swollen_shoot_present", "swollen_shoot_absent", 
        "sol_favorable", "sol_hydromorphe", 
        "sol_grossier", "sol_sn_cuirasse", 
        "pluvio_inf_1200"
    ]
    
    for cle in cles_checkbox:
        if cle not in st.session_state:
            st.session_state[cle] = False

    # --- 2. INJECTION DES STYLES CSS NATIFS ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .main-title-p24 { color: #113f67; font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    .badge-p24 { background-color: #2e86de; color: white; padding: 5px 10px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
    .box-decision { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 15px; margin-bottom: 20px; border: 1px solid #E2E8F0; }
    .critere-header { background-color: #34495e; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-bottom: 15px; }
    
    /* Styles de la structure FAQ & Tableaux Natifs (Évite le bug de l'Iframe) */
    .title-faq { color: #113f67; font-size: 22px; font-weight: bold; margin-top: 25px; margin-bottom: 15px; }
    .box-question { background-color: #ffffff; padding: 15px 20px; border-radius: 8px; border-left: 5px solid #2e86de; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    .sub-title-leila { color: #1e3d2f; font-size: 17px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
    .badge-accent { background-color: #e8f4f8; color: #2e86de; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; }
    .badge-danger { background-color: #fff5f5; color: #c53030; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; }
    .triptyque-box { background-color: #f8f9fa; border: 1px dashed #cbd5e0; padding: 15px; border-radius: 6px; font-family: monospace; text-align: center; color: #2d3748; margin: 15px 0; line-height: 1.4; font-size: 13px; }
    
    /* Tableau épuré sans scrollbars externes */
    .edu-table-native { width: 100%; border-collapse: collapse; margin-top: 15px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .edu-table-native th { background-color: #113f67; color: white; padding: 12px; text-align: left; font-size: 14px; border: 1px solid #E2E8F0; }
    .edu-table-native td { padding: 12px; border: 1px solid #E2E8F0; font-size: 13.5px; vertical-align: top; text-align: justify; color: #2D3748; line-height: 1.5; }
    .edu-table-native tr:hover { background-color: #F8FAFC; }
    .td-critere { font-weight: bold; color: #113f67; }
    
    /* --- NOUVEAUX BADGES INTERNES AU TABLEAU --- */
    .badge-adv { background-color: #E8F4F8; color: #1F4E78; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; margin-bottom: 4px; }
    .badge-inc { background-color: #FFF5F5; color: #C53030; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; margin-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p24">• Grille de décision du PDC</div>', unsafe_allow_html=True)
    st.markdown('<div class="badge-p24">Orientation Technique de la Parcelle</div>', unsafe_allow_html=True)

    st.write("### 🛠️ Cochez les critères observés sur la parcelle :")
    
    # --- 3. INTERFACE DE COCHAGE AVEC PERSISTANCE ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="critere-header">📈 Âge, Densité & Rendement</div>', unsafe_allow_html=True)
        age_plus_30 = st.checkbox("Plantation âgée de plus de 30 ans", key="age_plus_30")
        age_moins_30 = st.checkbox("Plantation âgée de moins de 30 ans", key="age_moins_30")
        st.divider()
        densite_inf_800 = st.checkbox("Densité inférieure à 800 arbres productifs / ha", key="densite_inf_800")
        densite_800_1000 = st.checkbox("Densité comprise entre 800 et 1 000 arbres productifs / ha", key="densite_800_1000")
        st.divider()
        rendement_inf_400 = st.checkbox("Rendement inférieur à 400 kg / ha", key="rendement_inf_400")
        rendement_sup_400 = st.checkbox("Rendement égal ou supérieur à 400 kg / ha", key="rendement_sup_400")

    with col2:
        st.markdown('<div class="critere-header">🌍 Sol, Climat & État Sanitaire</div>', unsafe_allow_html=True)
        swollen_shoot_present = st.checkbox("Présence de foyers de Swollen Shoot", key="swollen_shoot_present")
        swollen_shoot_absent = st.checkbox("Absence de foyers de Swollen Shoot", key="swollen_shoot_absent")
        st.divider()
        sol_favorable = st.checkbox("Sol favorable à la culture de cacao", key="sol_favorable")
        sol_hydromorphe = st.checkbox("Sol hydromorphe (engorgé d'eau)", key="sol_hydromorphe")
        sol_grossier = st.checkbox("Sol contenant plus de 50 % d'éléments grossiers", key="sol_grossier")
        cuirasse_proche = st.checkbox("Présence de cuirasse à moins d'un mètre de profondeur", key="sol_sn_cuirasse")
        st.divider()
        pluvio_inf_1200 = st.checkbox("Pluviométrie < 1200 mm avec plus de 4 mois de saison sèche", key="pluvio_inf_1200")

    # --- 4. BASE DE DONNÉES ENRICHIE ---
    dictionnaire_pedagogique = {
        "age_plus_30": {
            "nom": "Plantation âgée de plus de 30 ans",
            "avantage": "L'analyse de ce critère permet de caractériser le stade de sénescence physiologique terminale du verger cacaoyer. Sur le plan scientifique, il sert d'indicateur historique pour évaluer l'épuisement du potentiel de renouvellement cellulaire des arbres. Il permet aux chercheurs de planifier la transition variétale vers des générations de matériel végétal plus performantes. Enfin, cet indicateur valide l'arrêt immédiat des investissements en intrants chimiques complexes devenus inefficaces sur un système racinaire âgé.",
            "inconvenient": "À cet âge, les cacaoyers présentent une dégradation structurelle irréversible des vaisseaux conducteurs de sève (xylème et phloème), limitant la nutrition des cabosses. Le taux de mortalité naturelle des arbres s'accélère de façon exponentielle, créant des vides structurels dans la parcelle qui effondrent la rentabilité à l'hectare. La faible vigueur immunitaire des vieux arbres en fait des réservoirs épidémiologiques parfaits pour la multiplication des parasites. Pour le planteur, maintenir ce verger représente un gouffre financier en main-d'œuvre pour un retour sur investissement nul."
        },
        "age_moins_30": {
            "nom": "Plantation âgée de moins de 30 ans",
            "avantage": "Ce critère confirme la présence d'un appareil végétatif en pleine capacité métabolique, hormonal et structurelle. Les arbres possèdent encore la plasticité biologique nécessaire pour réagir positivement et rapidement aux techniques de régénération intensive. Il justifie scientifiquement l'application de programmes de fertilisation minérale raisonnée car l'absorption racinaire demeure optimale à ce stade. C'est un excellent feu vert technique pour rentabiliser des opérations de taille de restructuration ou de sur-greffage en clones améliorés.",
            "inconvenient": "Si le rendement de la parcelle est anormalement bas malgré cet âge théoriquement productif, cela indique un blocage agronomique majeur sous-jacent. Le risque est d'investir à perte dans la réhabilitation si l'échec initial est dû à un mauvais choix de matériel végétal non certifié à la plantation. De plus, un verger vigoureux de cet âge non entretenu développe une canopée anarchique qui séquestre la lumière solaire. Cela peut masquer une dégradation physico-chimique invisible des sols que le producteur ne détectera qu'après l'apparition des premiers symptômes de dépérissement."
        },
        "densite_inf_800": {
            "nom": "Densité inférieure à 800 arbres productifs / ha",
            "avantage": "Cet indicateur met scientifiquement en évidence une sous-utilisation critique de l'espace cultural et de l'énergie photonique disponible. Il permet de quantifier précisément le manque à gagner spatial pour optimiser l'indice de surface foliaire globale (LAI) de la parcelle. L'analyse de cette faible densité aide à planifier des stratégies précises de replantation intercalaire ciblée ou de densification. Elle offre également une opportunité agroforestière unique pour introduire des arbres d'ombrage sans étouffer les cacaoyers existants.",
            "inconvenient": "La rupture de la canopée causée par ce vide thermique provoque une forte insolation directe du sol, accélérant la minéralisation de la matière organique. Cette ouverture lumineuse favorise la germination agressive des adventices héliophiles, augmentant drastiquement la pénibilité et les coûts liés au désherbage. Le microclimat interne de la parcelle devient hautement instable, exposant le tronc des cacaoyers à des stress thermiques et aux attaques de foreurs de tiges. Sur le plan social, cette sous-population condamne le paysan à la pauvreté par l'impossibilité d'atteindre des rendements d'échelle."
        },
        "densite_800_1000": {
            "nom": "Densité comprise entre 800 et 1 000 arbres / ha",
            "avantage": "Ce critère valide la conformité rigoureuse de la structure spatiale du verger vis-à-vis des normes agronomiques recommandées en Côte d'Ivoire. Il garantit un équilibre optimal entre l'interception de la lumière solaire pour la photosynthèse et l'occupation du volume racinaire souterrain. Cette configuration stabilise le microclimat sous la canopée, protégeant naturellement la litière du sol contre le dessèchement direct. Pour l'expert, c'est la base idéale pour évaluer le potentiel réel des formules de fertilisation sans biais de surpeuplement.",
            "inconvenient": "Si cette densité théorique s'accompagne d'un manque de taille d'entretien, elle engendre un confinement de l'air sous le feuillage. Cette humidité relative stagnante devient le principal vecteur d'explosion des attaques de pourriture brune dues à Phytophthora palmivora. La compétition pour les nutriments du sol devient féroce si le producteur n'apporte pas de fumure de compensation régulière. Enfin, la récolte et la circulation sanitaire dans la parcelle peuvent devenir complexes si l'architecture des branches n'est pas canalisée."
        },
        "rendement_inf_400": {
            "nom": "Rendement inférieur à 400 kg / ha",
            "avantage": "L'analyse de ce seuil critique permet de matérialiser la faillite économique objective de la parcelle en l'état actuel du système. Scientifiquement, il prouve l'existence d'un facteur limitant absolu (sanitaire, pédologique ou génétique) qui bloque l'expression du métabolisme de la plante. Cet indicateur sert de levier d'aide à la décision pour orienter de force le producteur vers une reconversion culturale ou une replantation totale. Il permet aux coopératives d'identifier les zones de détresse agricole nécessitant une intervention d'urgence des projets de développement.",
            "inconvenient": "Un niveau de production aussi bas ne couvre même pas les charges de main-d'œuvre familiale ou salariée requises pour la récolte. Sur le plan social, cette situation entraîne un phénomène d'abandon psychologique du champ, transformant la parcelle en friche non entretenue. Ces parcelles abandonnées deviennent instantanément des foyers d'incubation géants pour les maladies qui contaminent les vergers sains voisins. Le producteur se retrouve prisonnier d'un cycle de précarité économique, l'empêchant d'investir dans l'éducation ou la santé de sa famille."
        },
        "rendement_sup_400": {
            "nom": "Rendement égal ou supérieur à 400 kg / ha",
            "avantage": "Ce critère garantit une base de productivité résiduelle permettant de rentabiliser rapidement des investissements de réhabilitation à faible coût. Il confirme que l'interaction entre le sol, le climat et le matériel végétal maintient une efficacité métabolique minimale stable. Pour le chercheur, c'est un indicateur de résilience agro-écosystémique qui valide la conservation temporaire du verger. Il sécurise un flux de trésorerie minimum pour le producteur pendant la mise en œuvre des réformes techniques.",
            "inconvenient": "Ce rendement peut dissimuler un épuisement silencieux et progressif des réserves minérales du sol si la production est maintenue sans compensation. Le producteur peut développer un faux sentiment de satisfaction économique, l'incitant à négliger les signes avant-coureurs de vieillissement des arbres. À long terme, l'absence de restructuration sur ces parcelles mène à un effondrement brutal et imprévisible de la production. Cela retarde l'adoption nécessaire des innovations agronomiques et des nouvelles variétés tolérantes."
        },
        "swollen_shoot_present": {
            "nom": "Présence de foyers de Swollen Shoot",
            "avantage": "La détection de ce critère permet de poser une alerte épidémiologique absolue, critique et prioritaire sur l'ensemble de l'exploitation. Sur le plan virologique, cet indicateur stoppe immédiatement l'application inutile de fertilisants ou de fongicides qui ne peuvent guérir ce phytovirus. Il permet de déclencher l'application stricte du protocole de quarantaine et d'arrachage pour sauver le bassin cacaoyer environnant. C'est l'argument scientifique incontestable pour mobiliser les fonds d'indemnisation et d'appui auprès des autorités nationales.",
            "inconvenient": "Ce virus complexe attaque le système vasculaire de l'arbre, provoquant des gonflements nodaux et un dépérissement fatal à court terme. L'inconvénient majeur est l'obligation de détruire non seulement les arbres infectés, mais aussi une ceinture de sécurité d'arbres sains autour du foyer. Cela impose au planteur un traumatisme social lié à la perte immédiate de son outil de travail et de sa seule source de revenus durables. Le sol exige un vide sanitaire rigoureux et l'éradication des plantes hôtes avant toute replantation certifiée."
        },
        "swollen_shoot_absent": {
            "nom": "Absence de foyers de Swollen Shoot",
            "avantage": "Ce critère apporte une garantie de sécurité et de sérénité phytosanitaire maximale pour planifier des investissements structurels lourds et durables. Il confirme que la parcelle est exempte du principal fléau virologique d'Afrique de l'Ouest, sécurisant les projections de rendement des bailleurs. Pour l'agronome, c'est le feu vert absolu pour déployer des programmes de fertilisation intensive ou de régénération par taille. Il valorise la position géographique et technique de l'exploitation au sein des réseaux de coopératives.",
            "inconvenient": "L'absence de symptômes visibles peut générer un excès de confiance dangereux et une baisse de vigilance face aux insectes vecteurs (cochenilles). Le producteur peut omettre d'inspecter régulièrement les parcelles limitrophes, s'exposant à une introduction surprise du virus par contamination aérienne. En outre, cela peut inciter à négliger l'éradication des barrières de plantes hôtes sauvages en bordure de champ. Le risque est de voir survenir une épidémie foudroyante dès que les conditions environnementales stressantes affaiblissent le verger."
        },
        "sol_favorable": {
            "nom": "Sol favorable à la culture de cacao",
            "avantage": "Ce paramètre assure un ancrage racinaire profond, une excellente porosité et une valorisation maximale de chaque unité de fertilisant apportée. Il garantit que les horizons pédologiques disposent d'un équilibre physico-chimique idéal pour nourrir durablement l'appareil végétatif. Scientifiquement, il maximise l'efficience de l'utilisation de l'eau (WUE) et protège les arbres contre les stress physiologiques mineurs. C'est le socle fondamental pour optimiser l'expression du potentiel génétique des variétés sélectionnées.",
            "inconvenient": "Un excellent sol incite malheureusement et très souvent à des pratiques de monoculture intensive destructrices, sans arbres d'ombrage associés. À terme, cette exploitation continue accélère la minéralisation de l'humus et provoque un déclin rapide de la biodiversité microbienne du sol. Le producteur tend à surestimer la résilience naturelle de sa terre, omettant d'apporter des amendements organiques de restitution. À long terme, cela conduit à une fatigue du sol difficile et coûteuse à corriger agronomiquement."
        },
        "sol_hydromorphe": {
            "nom": "Sol hydromorphe (engorgé d'eau)",
            "avantage": "L'analyse de ce critère permet de diagnostiquer un blocage physique majeur lié à l'anoxie (absence d'oxygène) dans les horizons racinaires. D'un point de vue scientifique, cet indicateur isole la cause mécanique de la mortalité des arbres, évitant les erreurs de traitement phytosanitaire. Il sert de base technique indiscutable pour recommander des travaux lourds de drainage ou pour réorienter la parcelle vers des cultures de bas-fonds. Il explique scientifiquement pourquoi les arbres sur-greffés s'effondrent subitement après une phase de surproduction factice.",
            "inconvenient": "L'excès d'eau permanent provoque l'asphyxie et le pourrissement biologique du pivot central et des radicelles absorbantes du cacaoyer. Ce milieu anaérobie stimule la prolifération de champignons racinaires destructeurs comme le genre Phytophthora, entraînant l'apoplexie de l'arbre. Le cacaoyer ne peut pas développer de racines d'ancrage stables, ce qui provoque des vagues de mortalité dès que les horizons supérieurs s'asphyxient. C'est une barrière environnementale éliminatoire : y investir dans le cacao garantit la perte totale du capital en moins de 6 ans."
        },
        "sol_grossier": {
            "nom": "Sol contenant plus de 50 % d'éléments grossiers",
            "avantage": "Ce paramètre met en évidence un déficit structural sévère de la texture du sol affectant directement sa Capacité d'Échange Cationique (CEC). Scientifiquement, il permet d'anticiper la faible rétention des nutriments et d'expliquer la faim minérale chronique constatée sur les arbres. Il permet aux agronomes de concevoir des plans de fertilisation fractionnée très spécifiques pour limiter le gaspillage économique des intrants. Cet indicateur justifie scientifiquement l'apport massif et impératif de compost pour recréer du complexe argilo-humique.",
            "inconvenient": "Ces sols gravillonneurs souffrent d'une porosité macro-texturale excessive qui accélère le lessivage des éléments nutritifs vers les nappes phréatiques. Pendant la saison sèche, la réserve en eau utile (RU) du sol s'épuise de manière fulgurante, plongeant les cacaoyers dans un stress hydrique létal. Le système racinaire superficiel s'use mécaniquement contre la fraction pierreuse, créant des micro-blessures propices aux infections bactériennes du bois. Pour le paysan, c'est un sol ingrat qui engendre de lourdes charges financières pour des rendements médiocres."
        },
        "sol_sn_cuirasse": {
            "nom": "Présence de cuirasse à moins d'un mètre de profondeur",
            "avantage": "L'identification de la cuirasse ferrugineuse permet de cartographier une barrière géologique verticale infranchissable pour le système racinaire. Sur le plan de la physique des sols, cet indicateur démontre une réduction drastique du volume de terre utile exploré par la plante. Il permet de stopper immédiatement les projets de replantation de cacaoyers sur des dalles rocheuses souterraines invisibles à l'œil nu. C'est une donnée spatiale précieuse pour réorienter le foncier vers des aménagements pastoraux ou des cultures superficielles.",
            "inconvenient": "La cuirasse indurée bloque mécaniquement la descente de la racine pivotante, élément vital pour l'accès à l'eau en période de stress climatique. Les cacaoyers développent un système racinaire anormalement plat et traçant, ce qui les rend extrêmement vulnérables au déracinement par les tornades. Dès que les premiers horizons supérieurs subissent la sécheresse, les arbres entrent en flétrissement et meurent massivement. Cette contrainte physique majeure condamne le verger à un nanisme végétatif irréversible."
        },
        "pluvio_inf_1200": {
            "nom": "Pluviométrie < 1200 mm avec longue saison sèche",
            "avantage": "Ce critère macroclimatique permet de poser les limites strictes de la viabilité géographique de la cacaoculture face au changement climatique global. Scientifiquement, il modélise le déficit hydrique cumulé qui bloque l'activité photosynthétique et perturbe la physiologie de la floraison. Il permet d'anticiper les baisses de récoltes régionales et d'orienter les politiques agricoles vers l'agroforesterie de substitution. C'est l'indicateur clé pour valider l'installation de systèmes d'irrigation ou de techniques de paillage lourd.",
            "inconvenient": "Le manque d'eau prolongé provoque l'avortement en série des coussinets floraux et le dessèchement précoce des jeunes cabosses (cherelles). Les arbres entrent en flétrissement permanent, perdent leur indice foliaire et deviennent incapables d'assimiler les éléments minéraux du sol. Ce stress hydrique chronique effondre le système immunitaire du cacaoyer, déclenchant des invasions massives et destructrices de mirides. Pour les communautés rurales, ce climat instable transforme la cacaoculture en une activité précaire qui menace la survie économique des ménages."
        }
    }

    # --- 5. MOTEUR DE DÉCISION ET TRAITEMENT DES INCOHÉRENCES ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Diagnostic de Cohérence et Croisement par Leila IA")

    choix = {
        "age_plus_30": age_plus_30, "age_moins_30": age_moins_30,
        "densite_inf_800": densite_inf_800, "densite_800_1000": densite_800_1000,
        "rendement_inf_400": rendement_inf_400, "rendement_sup_400": rendement_sup_400,
        "swollen_shoot_present": swollen_shoot_present, "swollen_shoot_absent": swollen_shoot_absent,
        "sol_favorable": sol_favorable, "sol_hydromorphe": sol_hydromorphe,
        "sol_grossier": sol_grossier, "sol_sn_cuirasse": cuirasse_proche,
        "pluvio_inf_1200": pluvio_inf_1200
    }
    
    criteres_coches = [k for k, v in choix.items() if v]
    nb_coches = len(criteres_coches)

    incoherence = False
    if age_plus_30 and age_moins_30:
        st.error("❌ **Incohérence :** Une plantation ne peut pas avoir plus de 30 ans et moins de 30 ans simultanément.")
        incoherence = True
    if densite_inf_800 and densite_800_1000:
        st.error("❌ **Incohérence :** Deux intervalles de densité différents ne peuvent pas être sélectionnés en même temps.")
        incoherence = True
    if rendement_inf_400 and rendement_sup_400:
        st.error("❌ **Incohérence :** Le rendement ne peut pas être à la fois inférieur et supérieur à 400 kg/ha.")
        incoherence = True
    if swollen_shoot_present and swollen_shoot_absent:
        st.error("❌ **Incohérence :** Statut contradictoire pour le Swollen Shoot.")
        incoherence = True

    if incoherence:
        st.stop()

    force_reconversion = sol_hydromorphe or cuirasse_proche or sol_grossier or pluvio_inf_1200
    force_replantation_economique = age_plus_30 or (densite_inf_800 and rendement_inf_400) or densite_inf_800

    if nb_coches > 0:
        if force_reconversion:
            st.error("🚨 **DÉCISION FINALE : RECONVERSION / DIVERSIFICATION**")
            msg_global = "Les barrières physiques du milieu (sol ou climat) sont éliminatoires pour le cacaoyer. Même si d'autres indicateurs semblent favorables à court terme, la parcelle subira un dépérissement irrémédiable."
            color_border = "#e74c3c"
            reco_pdc = "<li><strong>Arrêt définitif du cacao</strong> sur les zones à contraintes lourdes.</li><li>S'orienter vers une <strong>diversification culturale</strong> adaptée.</li>"
        elif swollen_shoot_present:
            st.warning("⚠️ **DÉCISION FINALE : REPLANTATION TOTALE (URGENCE SANITAIRE)**")
            msg_global = "La présence confirmée du virus du Swollen Shoot annule tout espoir de réhabilitation simple. L'arrachage de sécurité est inévitable pour stopper la contagion géographique."
            color_border = "#e67e22"
            reco_pdc = "<li>Arrachage complet des plants atteints selon le protocole national.</li><li>Mise en place d'un vide sanitaire strict avant replantation avec du matériel certifié tolérant.</li>"
        elif force_replantation_economique:
            st.warning("⚠️ **DÉCISION FINALE : REPLANTATION ÉCONOMIQUE**")
            msg_global = "Les indicateurs d'épuisement physiologique ou de sous-population critique dominent. Une restructuration totale par blocs s'impose pour retrouver un niveau de productivité viable."
            color_border = "#f39c12"
            reco_pdc = "<li>Planifier un remplacement complet et ordonné de la parcelle.</li><li>Régénérer le sol avec des apports organiques avant la replantation de matériel végétal sélectionné.</li>"
        elif age_moins_30 and densite_inf_800 and rendement_sup_400:
            st.success("🟢 **DÉCISION FINALE : RÉHABILITATION PAR REGARNISSAGE**")
            msg_global = "La plantation est jeune et garde une productivité encourageante sur un sol propice, mais elle souffre d'un manque cruel de pieds à l'hectare qu'il faut combler au plus vite."
            color_border = "#2ecc71"
            reco_pdc = "<li>Conserver la charpente des arbres existants toujours productifs.</li><li>Procéder à un <strong>regarnissage systématique</strong> en début de saison des pluies.</li>"
        else:
            st.success("🟢 **DÉCISION FINALE : RÉHABILITATION ET ENTRETIEN CLASSIQUE**")
            msg_global = "Les voyants agronomiques fondamentaux sont au vert (plantation saine, jeune, sol de qualité). Le potentiel de production doit juste être maintenu par de bonnes pratiques culturales."
            color_border = "#27ae60"
            reco_pdc = "<li>Poursuivre le calendrier de taille d'aération et la maîtrise de l'ombrage.</li><li>Optimiser la nutrition par un plan d'apport d'engrais équilibré.</li>"

        st.markdown(f"""
        <div class="box-decision" style="border-left: 5px solid {color_border};">
            <p style="margin: 0 0 10px 0; font-size: 15px; text-align: justify;">{msg_global}</p>
            <p style="margin: 5px 0 0 0; font-weight: bold; color: #333;">📋 Recommandations du PDC :</p>
            <ul style="margin: 5px 0 0 0; padding-left: 20px; font-size: 14px;">{reco_pdc}</ul>
        </div>
        """, unsafe_allow_html=True)

        # --- 6. TABLEAU PÉDAGOGIQUE EN RENDU STRIPÉ NATIF STYLES (PAS D'IFRAME) ---
        st.write("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 Décorticage Éducatif des Éléments Sélectionnés")
        st.info("Leila détaille ci-dessous les forces et les vulnérabilités propres à chaque facteur coché pour guider votre intervention :")

        lignes_html = ""
        for c in criteres_coches:
            if c in dictionnaire_pedagogique:
                infos = dictionnaire_pedagogique[c]
                lignes_html += f"""
                <tr>
                    <td class="td-critere">{infos['nom']}</td>
                    <td><span class="badge-adv">Avantage / Intérêt pédagogique</span><br>{infos['avantage']}</td>
                    <td><span class="badge-inc">Inconvénient / Risque terrain</span><br>{infos['inconvenient']}</td>
                </tr>
                """

        tableau_final_html = f"""
        <table class="edu-table-native">
            <thead>
                <tr>
                    <th style="width: 25%;">Critère Observé</th>
                    <th style="width: 37.5%;">Pourquoi Leila l'analyse (Avantages)</th>
                    <th style="width: 37.5%;">Ce que le terrain subit (Inconvénients)</th>
                </tr>
            </thead>
            <tbody>
                {lignes_html}
            </tbody>
        </table>
        """
        st.markdown(tableau_final_html, unsafe_allow_html=True)

# --- 7. SÉQUENCE INTERACTIVE : LEILA & SWOLLEN SHOOT ---
        if swollen_shoot_present:
            st.write("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="title-faq">💡 Guide Interactif & Savoir Agronomique Approfondi</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="box-question">
                <span style="color: #1F4E78; font-weight: bold; font-size: 13px; text-transform: uppercase;">Question Additionnelle du Planteur / Chercheur :</span><br>
                <p style="font-size: 15px; font-weight: 500; color: #2C3E50; margin-top: 5px; margin-bottom: 0;">
                    Est-ce qu'on peut replanter un nouveau champ de cacao après une attaque de Swollen Shoot ?
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🧠 Analyse de Cohérence et Stratégie Évolutive par Leila IA")
            
            st.info(
                "**Réponse de Leila :** C'est une excellente question de stratégie agronomique et de gestion des sols. "
                "La réponse courte est **oui, absolument**, et c'est même l'une des meilleures approches recommandées "
                "par la recherche (notamment le CNRA en Côte d'Ivoire) pour rompre le cycle du virus.\n\n"
                "Cependant, il y a des conditions biologiques strictes à respecter pendant ces 2 ou 3 cycles de cultures vivrières.\n\n"
                "Voici l'analyse agronomique détaillée de ce processus :"
            )
            
            st.markdown("""<div class="sub-title-leila">1. Pourquoi la rotation avec le vivrier fonctionne (L'effet "Vide Sanitaire")</div>""", unsafe_allow_html=True)
            st.markdown(
                "Le virus du Swollen Shoot (**CSSV** - *Cocoa Swollen Shoot Virus*) a une faiblesse majeure : "
                "il ne peut pas survivre directement dans le sol, ni dans les débris de bois morts une fois qu'ils "
                "sont totalement secs et décomposés. Le virus a impérativement besoin d'un hôte vivant (les cellules d'un arbre malade) "
                "et d'un vecteur mobile (les cochenilles) pour passer d'une plante à une autre.\n\n"
                "En éliminant complètement le verger infecté et en cultivant du vivrier pendant plusieurs cycles "
                "(ce qui prend généralement entre **2 et 3 ans**), tu crées un **vide sanitaire biologique** :"
            )
            
            st.markdown("""
            * 🪰 **Mortalité des vecteurs :** Les cochenilles infectées qui restent sur le site meurent ou perdent le virus (le virus n'est pas persistant indéfiniment chez le vecteur).
            * 🪵 **Destruction de la source :** Les racines résiduelles des vieux cacaoyers malades enfouies dans le sol meurent définitivement, coupant toute source de nourriture au virus.
            """)

            st.markdown('<div class="sub-title-leila">2. Le choix crucial des cultures vivrières (Les pièges à éviter)</div>', unsafe_allow_html=True)
            st.markdown(
                "Tous les vivriers ne se valent pas. Certains arbres ou plantes présents dans les champs en Côte d'Ivoire "
                "sont des **hôtes intermédiaires** (des réservoirs cachés) du Swollen Shoot. Si le planteur les laisse ou les cultive, "
                "le virus restera sur la parcelle."
            )
            
            col_ok, col_ban = st.columns(2)
            with col_ok:
                st.markdown('🟢 **Cultures vivrières excellentes (Sans danger) :**')
                st.markdown("""
                * **Le Maïs et le Riz :** Les graminées sont parfaites. Elles n'hébergent pas le virus et leur système racinaire de surface nettoie la structure supérieure du sol.
                * **L'Arachide et le Niébé :** <span class="badge-accent">Le choix d'expert</span>. En plus de rompre le cycle du virus, ces légumineuses fixent l'azote de l'air et enrichissent naturellement le sol pour les futurs cacaoyers.
                * **Le Manioc :** Utilisable, mais à condition de nettoyer drastiquement la parcelle à la récolte.
                """, unsafe_allow_html=True)
                
            with col_ban:
                st.markdown('⚠️ **Plantes à exclure absolument (Réservoirs) :**')
                st.markdown("""
                * **Le Colatier (*Cola nitida*) :** C'est le cousin germain du cacaoyer, il abrite le virus en mode asymptomatique (sans toujours de symptômes apparents).
                * **Le Baobab (*Adansonia digitata*) & Le Fromager (*Ceiba pentandra*) :** <span class="badge-danger">Hôtels 5 étoiles</span>. Ces grands arbres forestiers hébergent massivement les colonies de cochenilles. Ils doivent être abattus ou annelés si la parcelle a été détruite.
                """, unsafe_allow_html=True)

            st.markdown('<div class="sub-title-leila">3. Les 3 étapes indispensables avant le retour du cacao</div>', unsafe_allow_html=True)
            st.markdown(
                "Pour garantir que le nouveau verger ne retombe pas malade après les 3 cycles de vivriers, "
                "Leila conseille d'appliquer ce triptyque technique :"
            )
            
            st.markdown("""
            <div class="triptyque-box">
                [Éradication Totale & Incinération]<br>
                │<br>
                ▼<br>
                [2 à 3 Cycles de Vivriers (Azote / Rupture)]<br>
                │<br>
                ▼<br>
                [Replantation : Matériel Tolérant + Barrière Végétale]
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            * 🛡️ **La Ceinture de Sécurité Végétale :** Lors de la replantation, il est fortement recommandé de planter une barrière protectrice tout autour de l'espace (ex: 2 ou 3 rangées serrées de bananiers ou de *Prestige*) pour empêcher les cochenilles des plantations voisines de migrer par le vent vers la nouvelle parcelle saine.
            * 🧪 **Le choix de la variété :** Après un passif de Swollen Shoot, il est interdit de replanter du tout-venant. L'utilisation de semences certifiées tolérantes (comme le **Cacao Mercedes** distribué par le CNRA) est obligatoire pour assurer la résilience immunitaire du verger.
            * 🪱 **La restauration humique :** Les cycles de vivriers successifs épuisent la couche superficielle du sol. Avant de remettre les jeunes plants de cacao, un apport de compost ou de biomasse végétale est nécessaire pour redonner de la force à la structure de la terre.
            """)

            st.write("<br>", unsafe_allow_html=True)
            st.success(
                "🍀 **En résumé :** L'idée de transition par le vivrier est la **clé de voûte de la durabilité**. "
                "Elle résout un problème social immense : elle permet au planteur de continuer à nourrir sa famille et de "
                "générer des revenus à court terme avec le maïs ou l'arachide, tout en soignant scientifiquement sa terre "
                "pour relancer l'or brun sur des bases saines."
            )

    else:
        st.info("💡 **En attente de critères...** Cochez au moins un paramètre pour obtenir le diagnostic et le décorticage éducatif de Leila.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p24", type="primary", use_container_width=True):
        st.session_state["page_24_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 25
        st.rerun()

    # --- 8. PIED DE PAGE ET NUMÉROTATION REGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    _, col_p = st.columns([0.95, 0.05])
    with col_p:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>24</span>", unsafe_allow_html=True)



def dessiner_page_25_Analyse_Problemes():
    # --- 1. STYLES CSS PERSONNALISÉS ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .main-title-p25 { color: #1A252F; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 5px; }
    .badge-p25 { background-color: #C0392B; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 13px; }
    
    /* Structure en poupées russes avec bordures de sécurité */
    .pouperee-p25-l1 { border-left: 5px solid #2C3E50; background-color: #FFFFFF; padding: 15px; border-radius: 4px; margin-bottom: 15px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    .pouperee-p25-l2 { border-left: 5px solid #2980B9; background-color: #F7F9FA; padding: 15px; border-radius: 4px; margin-bottom: 15px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    .pouperee-p25-l3 { border-left: 5px solid #D35400; background-color: #FFFBF2; padding: 15px; border-radius: 4px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #C0392B; margin-top: 5px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p25">❖ Tableau d\'analyse des problèmes</div>', unsafe_allow_html=True)
    st.markdown('<div class="badge-p25">Diagnostic phytosanitaire & Contraintes du verger (Expertise Étendue 10+ Choix)</div>', unsafe_allow_html=True)

    # --- BANQUE DE DONNÉES ENRICHIE ---
    banque_diagnostics_extended = {
        "Peuplement du verger": {
            "PROBLEMES": [
                "[DENSITÉ] Forte densité (Forte concentration > 1500 pieds/ha)",
                "[DENSITÉ] Faible densité / Verger clairsemé (Sous-densité < 1000 pieds/ha)",
                "[STRUCTURE] Des plages vides en replantation sous des cacaoyers infectés",
                "[ALIGNEMENT] Mauvais piquetage et non-respect des lignes de plantation",
                "[SAUVAGE] Surpeuplement par levée spontanée et désordonnée de fèves au sol",
                "[RENDEMENT] Présence élevée de pieds totalement improductifs (arbres 'mâles')",
                "[ÂGE] Vieillissement généralisé du matériel végétal (Verger sénile > 30 ans)",
                "[INTRUS] Présence d'essences forestières concurrentes non régulées",
                "[AGRO] Taux d'échec élevé (mortalité) des jeunes plants après regarnissage",
                "[SOL] Érosion ou dégradation visible de la couche arable autour des collets"
            ],
            "CAUSES": [
                "[PRATIQUE] Non-respect du dispositif technique recommandé (ex: dispositif 3m x 3m)",
                "[PRATIQUE] Abandon ou absence de remplacement des plants morts (regarnissage non fait)",
                "[PHYTO] Mortalité directe due à la propagation du virus du Swollen Shoot",
                "[QUALITÉ] Utilisation de matériel végétal tout-venant ou de fèves non certifiées",
                "[FAUNE] Attaques sévères de rongeurs et ravageurs sur les jeunes plants installés",
                "[SUIVI] Manque drastique d'arrosage et de suivi agronomique post-replantation",
                "[PRATIQUE] Destruction accidentelle de jeunes plants lors des opérations de désherbage",
                "[CLIMAT] Stress hydrique sévère dû au prolongement de la grande saison sèche",
                "[NUTRITION] Carence nutritionnelle sévère du sol bloquant la reprise racinaire",
                "[FONCIER] Conflits de limites ou absence de sécurisation foncière"
            ],
            "CONSEQUENCES": [
                "[PHYTO] Prolifération des maladies (pourritures brunes) et insectes (mirides, foreurs)",
                "[RENDEMENT] Perte d'espace et chute brutale de la production globale à l'hectare",
                "[RENDEMENT] Chute de la production par étouffement ou compétition entre pieds",
                "[FLORE] Enherbement agressif des espaces vides compliquant les interventions",
                "[CONCURRENCE] Concurrence hydrique et nutritionnelle féroce asphyxiant le verger",
                "[PRATIQUE] Difficulté extrême de circulation pour les traitements et la récolte",
                "[ÉCONOMIE] Perte financière sèche liée à l'achat et à la main-d'œuvre des plants morts",
                "[PHYSIO] Élongation anormale des tiges (étiolement) à la recherche de lumière",
                "[SOL] Lessivage accru des nutriments du sol par manque de couverture foliaire",
                "[DÉCOURAGEMENT] Abandon progressif ou désintérêt du producteur pour les parcelles"
            ],
            "SOLUTIONS": [
                "[PRATIQUE] Régler la densité via une éclaircie sélective ou un recépage planifié",
                "[PRATIQUE] Planifier une campagne de regarnissage ciblé au début des pluies (viser 1111 pieds/ha)",
                "[AGROFORESTERIE] Planter des arbres d'ombrages temporaires (Légumineuses) et définitifs",
                "[TECHNIQUE] Adopter un piquetage rigoureux en quinconce ou en ligne droite (3m x 3m)",
                "[ENTRETIEN] Nettoyage et arrachage systématique des rejets sauvages non contrôlés",
                "[RÉGÉNÉRATION] Introduire un plan de remplacement progressif par substitution ou surgreffage",
                "[FORMATION] Sensibiliser le producteur à la sélection de clones performants (ex: Mercedes)",
                "[CONSERVATION] Pratiquer le paillage autour des jeunes plants pour maintenir l'humidité",
                "[DÉFENSE] Installer des barrières physiques ou répulsifs contre les attaques de rongeurs",
                "[PROTEC] Mettre en place des bandes enherbées pour freiner l'érosion du sol"
            ]
        },
        "Entretien du verger": {
            "PROBLEMES": [
                "[ARCHITECT] Présence de nombreux gourmands non maîtrisés",
                "[FERTILITÉ] Utilisation de fumier de mouton ou de fientes non compostés",
                "[PHYTO] Attaques récurrentes et massives de mirides (capsides)",
                "[PHYTO] Présence de galeries de foreurs de tiges (chenilles xylophages)",
                "[FLORE] Enherbement sévère, lianescent et inconsolé de la sous-cacaoyère",
                "[TAILLE] Absence totale de taille de formation, d'entretien ou de rajeunissement",
                "[LUMIÈRE] Fermeture complète de la canopée provoquant une obscurité permanente",
                "[RÉCOLTE] Maintien de cabosses momifiées ou infectées sur les arbres",
                "[OUTILLAGE] Blessures ouvertes et déchirures d'écorce lors des récoltes à la machette",
                "[SANTE] Accumulation de pourriture sur le tronc due à un mauvais drainage de la parcelle"
            ],
            "CAUSES": [
                "[ENTRETIEN] Absence ou insuffisance flagrante de l'entretien régulier du verger",
                "[FORMATION] Manque de formation technique du producteur sur les itinéraires certifiés",
                "[CALENDRIER] Retard critique dans l'exécution des opérations de calendrier culturel",
                "[INVEST] Indisponibilité locale ou coût trop élevé des intrants agricoles homologués",
                "[ÉQUIPEMENT] Carence chronique en matériel spécifique (Sécateurs, scies horticoles, émondeurs)",
                "[AGRO] Mauvaise association ou mauvaise gestion de la hauteur des arbres d'ombrage",
                "[EAU] Topographie en cuvette favorisant la stagnation prolongée des eaux de pluie",
                "[MAIN D'OEUVRE] Pénurie de main-d'œuvre qualifiée pour les travaux physiques de taille",
                "[PRODUIT] Utilisation accidentelle de produits phytosanitaires contrefaits ou mal dosés",
                "[IGNORANCE] Négligence des mesures d'hygiène phytosanitaire de base (outils non désinfectés)"
            ],
            "CONSEQUENCES": [
                "[PHYTO] Attire les mirides et réduit considérablement la vigueur du cacaoyer",
                "[PHYSIO] Intoxication des plantes et brûlures sévères des radicelles absorbantes",
                "[PRODUCTION] Perte massive de fleurs et flétrissement précoce des jeunes cherelles (Chérelle wilt)",
                "[CHAMPIGNON] Développement fulgurant du Phytophthora (Pourriture brune des cabosses)",
                "[ÉNERGIE] Consommation inutile des réserves de sève par les gourmands au détriment des fruits",
                "[STRUCT] Dessèchement et cassure des branches maîtresses charpentières",
                "[RÉCOLTE] Difficulté accrue de détection et de récolte des cabosses mûres dans les lianes",
                "[VULNÉRABILITÉ] Sensibilité accrue de la plantation aux moindres variations climatiques",
                "[PROPAGATION] Propagation rapide des maladies d'un arbre à l'autre via les outils souillés",
                "[PERTE] Chute rapide du taux de conformité aux exigences des normes de certification"
            ],
            "SOLUTIONS": [
                "[TAILLE] Réaliser rigoureusement la taille d'entretien et l'égourmandage semestriel",
                "[BIOLOGIQUE] Suivre une formation pratique sur la fabrication de compost aérobie amélioré",
                "[TRAITEMENT] Appliquer des traitements insecticides/fongicides ciblés avec des appareils calibrés",
                "[PROPRETÉ] Nettoyer la plantation au moins 3 à 4 fois par an (désherbage manuel)",
                "[HYGIÈNE] Ramasser et éliminer systématiquement les cabosses momifiées hors de la parcelle",
                "[TECHNIQUE] Désinfecter le matériel de coupe à l'alcool ou à la flamme entre chaque arbre",
                "[ÉLAGAGE] Élaguer stratégiquement les branches basses des grands arbres d'ombrage",
                "[EAU] Creuser des rigoles de drainage pour évacuer les excès d'eau stagnante",
                "[EQUIP] Acquérir un kit collectif d'outils horticoles de qualité au sein de la coopérative",
                "[SUIVI] Mettre en place un calendrier visuel de suivi des cycles de traitement et de fertilisation"
            ]
        }
    }

    # 🔐 INITIALISATION ET PERSISTANCE DE LA MEMOIRE (SESSION STATE)
    if "p25_diagnostics_sauvegardes" not in st.session_state:
        st.session_state["p25_diagnostics_sauvegardes"] = {}

    for dom in banque_diagnostics_extended.keys():
        cle_dom = dom.replace(" ", "_").lower()
        if f"p25_sel_p_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_p_{cle_dom}"] = []
        if f"p25_sel_c_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_c_{cle_dom}"] = []
        if f"p25_sel_e_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_e_{cle_dom}"] = []
        if f"p25_sel_s_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_s_{cle_dom}"] = []
        if f"p25_note_{cle_dom}" not in st.session_state: st.session_state[f"p25_note_{cle_dom}"] = ""

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN COCHÉES ET CLOISONNÉES (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Identification et Diagnostic Spécifique par Domaine", expanded=True):
        st.markdown('<div class="pouperee-p25-l1">', unsafe_allow_html=True)
        st.info("🎯 **Haute Précision :** Les listes contiennent désormais plus de 10 options ciblées. Les sélections sont enregistrées automatiquement.")
        
        diagnostics_saisis = []

        for dom, catalogues in banque_diagnostics_extended.items():
            cle_dom = dom.replace(" ", "_").lower()
            st.markdown(f"#### 📍 {dom}")
            
            sel_prob = st.multiselect(f"Problèmes constatés : {dom}", options=catalogues["PROBLEMES"], key=f"p25_sel_p_{cle_dom}")
            sel_cau = st.multiselect(f"Causes directes : {dom}", options=catalogues["CAUSES"], key=f"p25_sel_c_{cle_dom}")
            sel_cons = st.multiselect(f"Conséquences directes : {dom}", options=catalogues["CONSEQUENCES"], key=f"p25_sel_e_{cle_dom}")
            sel_sol = st.multiselect(f"Solutions préconisées : {dom}", options=catalogues["SOLUTIONS"], key=f"p25_sel_s_{cle_dom}")
            
            note_terrain = st.text_input("Précisions terrain / Notes libres", placeholder="Ex: Zone de bas-fond touchée", key=f"p25_note_{cle_dom}")
            
            if sel_prob:
                diagnostics_saisis.append({
                    "DOMAINE": dom,
                    "PROBLEMES OU CONTRAINTES": " \n• ".join(sel_prob),
                    "CAUSES": " \n• ".join(sel_cau) if sel_cau else "Non spécifié",
                    "CONSEQUENCES": " \n• ".join(sel_cons) if sel_cons else "Non spécifié",
                    "SOLUTIONS": " \n• ".join(sel_sol) if sel_sol else "Non spécifié",
                    "OBSERVATIONS": note_terrain if note_terrain.strip() != "" else "Confirmé sur site"
                })
            st.write("---")
            
        st.session_state["p25_diagnostics_sauvegardes"] = diagnostics_saisis
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : RENDU SYNOPTIQUE MATRICIEL DYNAMIQUE (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visualisation du Tableau)", expanded=True):
        st.markdown('<div class="pouperee-p25-l2">', unsafe_allow_html=True)
        
        donnees_affichees = st.session_state["p25_diagnostics_sauvegardes"]
        
        if len(donnees_affichees) > 0:
            st.markdown("##### 📋 Matrice d'Analyse des Problèmes Enrichie (Format Terrain)")
            df_diagnostics = pd.DataFrame(donnees_affichees)
            
            st.dataframe(
                df_diagnostics[["DOMAINE", "PROBLEMES OU CONTRAINTES", "CAUSES", "CONSEQUENCES", "SOLUTIONS", "OBSERVATIONS"]], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.warning("💡 En attente de saisie à l'Étape 1 pour l'affichage de la matrice synoptique.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA EXPERT / ALERTES DISCRIMINANTES (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Analyse des Vulnérabilités & Moteur décisionnel de Leila", expanded=True):
        st.markdown('<div class="pouperee-p25-l3">', unsafe_allow_html=True)
        
        if len(donnees_affichees) == 0:
            st.success("🟢 **Statut Verger :** Aucun dysfonctionnement n'a été répertorié. Continuer le suivi standard.")
        else:
            st.markdown('<div class="subsection-analysis-title">🔍 Alertes Automatiques Déclenchées par Leila</div>', unsafe_allow_html=True)
            
            texte_diagnostics = " ".join([d["PROBLEMES OU CONTRAINTES"] for d in donnees_affichees]).lower()
            
            if "swollen shoot" in texte_diagnostics or "plages vides" in texte_diagnostics:
                st.error("🚨 **CRITIQUE - Sécurité Sanitaire Nationale (Swollen Shoot) :**\n\n"
                         "*Le diagnostic mentionne des pertes de pieds suspectes ou des plages vides induites. "
                         "Attention, toute replantation à l'aveugle sans respect du cordon sanitaire ou de la période "
                         "de jachère intermédiaire provoquera une ré-infestation par les cochenilles. Alerte prioritaire à remonter à la coopérative.*")
                
            if "forte densité" in texte_diagnostics:
                st.warning("⚠️ **ALERTE AGRO - Excès de Densité (>1500 pieds/ha) :**\n\n"
                           "*Une densité excessive couplée à un manque d'égourmandage engendre un confinement humide sous la canopée. "
                           "C'est l'incubateur parfait pour le Phytophthora (pourriture brune des cabosses). Une éclaircie sélective est hautement recommandée.*")
                
            if "faible densité" in texte_diagnostics:
                st.warning("📉 **ALERTE RENDEMENT - Sous-occupation de l'Espace (<1000 pieds/ha) :**\n\n"
                           "*La sous-densité laisse filtrer trop de lumière, ce qui déclenche un enherbement agressif et épuise les nutriments. "
                           "Le rendement à l'hectare chute drastiquement. Leila préconise de planifier un regarnissage au début de la saison des pluies "
                           "pour viser la cible optimale de 1111 pieds/ha.*")

            if "fumier" in texte_diagnostics or "non composté" in texte_diagnostics:
                st.error("❌ **ALERTE TECHNIQUE - Risque de Phytotoxicité Racinaire :**\n\n"
                         "*L'épandage de matières organiques non stabilisées entraîne une faim d'azote temporaire et dégage une chaleur interne "
                         "susceptible de détruire les radicelles superficielles de l'arbre. Interdire la pratique immédiate tant que le compostage n'est pas maîtrisé.*")
                
            if "sénile" in texte_diagnostics or "vieillissement" in texte_diagnostics:
                st.info("⏳ **STRATÉGIE - Plan de Replantation / Reconversion Obligatoire :**\n\n"
                        "*Le verger a dépassé son seuil optimal de productivité économique. Leila recommande d'intégrer ce producteur "
                        "dans les programmes d'appui aux parcelles agroforestières de nouvelle génération (matériel clonal Mercedes).*")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p25", type="primary", use_container_width=True):
        st.session_state["page_25_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 26
        st.rerun()

    # --- PIED DE PAGE ET PAGINATION RÉGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>25</span>", unsafe_allow_html=True)


def dessiner_page_26_Validation_Producteur():
    # --- 1. INITIALISATION DE LA MÉMOIRE DE SESSION ---
    if "p26_nom_producteur" not in st.session_state:
        st.session_state.p26_nom_producteur = ""
    if "p26_statut_discussion" not in st.session_state:
        st.session_state.p26_statut_discussion = False
    if "p26_accord_producteur" not in st.session_state:
        st.session_state.p26_accord_producteur = False
    if "p26_enregistre" not in st.session_state:
        st.session_state.p26_enregistre = False

    # --- 2. STYLE CSS DÉDIÉ ET OPTIMISÉ ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .title-p26 { color: #113f67; font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    .subtitle-p26 { color: #4A5568; font-size: 14px; margin-bottom: 25px; font-style: italic; }
    
    /* Encadré de la Note institutionnelle */
    .note-box-p26 {
        background-color: #1e3d2f; 
        color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.6;
        text-align: justify;
        margin-bottom: 30px;
    }
    .note-box-p26 strong {
        color: #ffeb3b; 
        font-size: 18px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 3. EN-TÊTE ---
    st.markdown('<div class="title-p26">📢 Restitutions et Engagements des Constats</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-p26">Phase de concertation, de validation et de prise de décision finale</div>', unsafe_allow_html=True)

    # --- 4. AFFICHAGE DE LA NOTE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="note-box-p26">
        <strong>NOTE :</strong> Les constats et recommandations de l'équipe de diagnostic 
        dovent être portés à la connaissance du producteur (et de ses travailleurs si possible). 
        Ces constats et recommandations sont discutés et validés avec le producteur ; 
        ce qui permettra, au regard des objectifs à court et moyen terme du producteur, 
        de prendre la décision finale et de dégager les principales actions à mener.
    </div>
    """, unsafe_allow_html=True)

    # --- 5. MODULE INTERACTIF DE LEILA IA ---
    st.markdown("### 📝 Validation du Rapport de Restitution")
    
    st.write(
        "Avant de générer le plan d'action définitif, confirmez que la séance de "
        "restitution et d'échange a bien eu lieu avec le producteur sur la parcelle."
    )
    
    nom_producteur = st.text_input(
        "Nom du Producteur / Exploitant :", 
        value=st.session_state.p26_nom_producteur,
        placeholder="Ex: M. Kouamé",
        key="input_nom_producteur"
    )
    st.session_state.p26_nom_producteur = nom_producteur
    
    col1, col2 = st.columns(2)
    with col1:
        statut_discussion = st.checkbox(
            "Les constats et recommandations ont été discutés", 
            value=st.session_state.p26_statut_discussion,
            key="chk_statut_discussion"
        )
        st.session_state.p26_statut_discussion = statut_discussion
        
    with col2:
        accord_producteur = st.checkbox(
            "Le producteur valide les décisions proposées", 
            value=st.session_state.p26_accord_producteur,
            key="chk_accord_producteur"
        )
        st.session_state.p26_accord_producteur = accord_producteur

    # --- 6. ZONE D'ENGAGEMENT ET ENREGISTREMENT ---
    st.write("<br>", unsafe_allow_html=True)
    
    if statut_discussion and accord_producteur and nom_producteur.strip() != "":
        st.success(f"✅ Diagnostic validé d'un commun accord avec le producteur **{nom_producteur}**. Prêt pour le déploiement des actions à court et moyen terme !")
        
        if st.button("💾 Enregistrer la validation et générer le Plan de Développement"):
            st.session_state.p26_enregistre = True
            
        if st.session_state.p26_enregistre:
            st.toast("🎉 Données de validation enregistrées avec succès !", icon="💾")
    else:
        st.session_state.p26_enregistre = False
        st.warning("⚠️ En attente de la confirmation des échanges et du nom du producteur pour valider officiellement cette étape.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p26", type="primary", use_container_width=True):
        st.session_state["page_26_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 27
        st.rerun()

    # --- 7. PIED DE PAGE ET NUMÉROTATION RÉGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    _, col_p = st.columns([0.95, 0.05])
    with col_p:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>26</span>", unsafe_allow_html=True)



def dessiner_page_27_Planification_Activites():
    # --- 1. STYLES CSS PERSONNALISÉS ---
    st.markdown("""
    <style>
    /* Le bandeau vert du haut */
    .header-bar-p27 {
        background-color: #C6EFCE; /* Vert clair institutionnel */
        border: 1.5px solid #2E7D32; /* Bordure verte marquée */
        padding: 10px 20px;
        margin-bottom: 30px;
        border-radius: 4px;
    }

    .header-title-p27 {
        color: #006100; /* Vert foncé */
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Le sous-titre avec le diamant */
    .subtitle-container-p27 {
        display: flex;
        align-items: center;
        margin-left: 20px;
        margin-bottom: 25px;
    }

    .diamond-icon-p27 {
        color: #008080; /* Teal / Bleu pétrole */
        font-size: 24px;
        margin-right: 15px;
    }

    .subtitle-text-p27 {
        color: #008080;
        font-size: 22px;
        font-weight: bold;
        text-decoration: underline;
        font-family: 'Arial', sans-serif;
    }

    /* Texte principal et liste */
    .content-container-p27 {
        margin-left: 40px;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        color: #2D3748;
        line-height: 1.6;
    }

    .list-p27 {
        list-style-type: none;
        padding-left: 20px;
        margin-top: 15px;
    }

    .list-item-p27 {
        position: relative;
        margin-bottom: 12px;
    }

    .list-item-p27::before {
        content: "o"; /* Reproduction du marqueur circulaire */
        position: absolute;
        left: -25px;
        color: #4A5568;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. RENDU DE L'INTERFACE ---
    st.markdown('''
        <div class="header-bar-p27">
            <h1 class="header-title-p27">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div class="subtitle-container-p27">
            <span class="diamond-icon-p27">❖</span>
            <span class="subtitle-text-p27">Élaboration du plan d'action sur 5 ans</span>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div class="content-container-p27">
            <p>À l'issue du diagnostic, un plan d'action est élaboré pour une période de 5 ans. La matrice du plan d'action précise :</p>
            <ul class="list-p27">
                <li class="list-item-p27">les axes stratégiques,</li>
                <li class="list-item-p27">les objectifs visés par chaque axe stratégique,</li>
                <li class="list-item-p27">les principales activités par axe et leurs coûts.</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p27", type="primary", use_container_width=True):
        st.session_state["page_27_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 28
        st.rerun()

    # --- PIED DE PAGE ET NUMÉROTATION RÉGLEMENTAIRE ---
    st.write("<br><br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>27</span>", unsafe_allow_html=True)

def analyser_activite_layla(nom_activite, periode_saisie):
    """
    Analyse agronomique prédictive basée sur le calendrier culturel ivoirien.
    """
    act = nom_activite.lower()
    per = periode_saisie.lower()
    
    # 1. ANALYSE ACTIVITÉ : RÉGLER LA DENSITÉ
    if "densité" in act or "densite" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Régler la densité ({periode_saisie}) - Idéal :** Parfait pour repérer les surpeuplements. Le bois est sec et l'enherbement est bas, ce qui facilite la circulation et l'abattage sélectif."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Régler la densité ({periode_saisie}) - Recommandé :** Il faut impérativement finir d'ajuster le piquetage et l'éclaircie avant la reprise forte de la végétation."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "error",
                "msg": f"❌ **Régler la densité ({periode_saisie}) - À éviter :** Le sol est boueux et glissant. Abattre des arbres en cette période de grandes pluies risque de détruire les racines gorgées d'eau des cacaoyers voisins."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Régler la densité ({periode_saisie}) - Possible :** Petite saison sèche, observation recommandée du comportement du verger face à la baisse momentanée des pluies."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "error",
                "msg": f"❌ **Régler la densité ({periode_saisie}) - À proscrire :** Les arbres sont chargés de cabosses pour la grande récolte. Risque majeur de faire tomber les fruits et de blesser les coussinets floraux."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Régler la densité ({periode_saisie}) - Fin de cycle :** Nettoyage sanitaire et réajustement de la parcelle opportun juste après les grands passages de récolte."
            }

    # 2. ANALYSE ACTIVITÉ : RÉALISER LA TAILLE DES CACAOYERS
    elif "taille" in act or "élagage" in act or "elagage" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "warning",
                "msg": f"⚠️ **Taille des cacaoyers ({periode_saisie}) - Prudence :** Taille légère uniquement (gourmands). Évitez les tailles sévères car l'arbre cicatrise mal sans eau et le soleil direct brûlerait l'intérieur du verger mis à nu."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "success",
                "msg": f"🔥 **Taille des cacaoyers ({periode_saisie}) - Période Cruciale :** Grande taille d'entretien. Aérer la canopée juste avant les pluies détruit l'habitat favori des mirides (capsides) et stimule la floraison."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "warning",
                "msg": f"⚠️ **Taille des cacaoyers ({periode_saisie}) - Trop tard :** Évitez les gros travaux de restructuration. Le verger non taillé devient un incubateur à humidité, favorisant la pourriture brune (*Phytophthora*)."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Taille des cacaoyers ({periode_saisie}) - Deuxième passage :** Idéal pour un égourmandage ciblé. On élimine les rejets anarchiques qui ont profité des pluies de juin."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "error",
                "msg": f"❌ **Taille des cacaoyers ({periode_saisie}) - À proscrire :** Entrer avec des machettes ou des scies blesse les coussinets floraux de la récolte future et provoque la chute des cabosses mûres."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Taille des cacaoyers ({periode_saisie}) - Fin de cycle :** Nettoyage de fin de récolte, élimination des branches cassées ou malades avant l'intensité du vent sec de l'Harmattan."
            }

    # 3. ANALYSE ACTIVITÉ : PLANTER LES ARBRES D'OMBRAGE TEMPORAIRES
    elif "plant" in act or "ombrage" in act or "regarnissage" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "error",
                "msg": f"❌ **Arbres d'ombrage ({periode_saisie}) - Interdiction absolue :** Installer de jeunes plants ou des boutures en pleine grande saison sèche conduit inévitablement à un dessèchement racinaire immédiat."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "info",
                "msg": f"⏳ **Arbres d'ombrage ({periode_saisie}) - En attente :** Bon moment pour la préparation des trous (piquetage/potquetage) et la sécurisation en pépinière, mais il faut attendre les vraies pluies pour planter."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "success",
                "msg": f"🏆 **Arbres d'ombrage ({periode_saisie}) - Top Priorité :** Le sommet de l'année. Le sol est meuble et gorgé d'eau, assurant un taux de reprise racinaire proche de 100%."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "error",
                "msg": f"❌ **Arbres d'ombrage ({periode_saisie}) - Risqué :** La petite saison sèche (août) peut être traître. Si le système racinaire n'est pas encore profond, le jeune plant ne survivra pas au stress hydrique."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Arbres d'ombrage ({periode_saisie}) - Dernière chance :** Possible uniquement au tout début du mois de septembre si les pluies reprennent bien."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "error",
                "msg": f"❌ **Arbres d'ombrage ({periode_saisie}) - Interdit :** L'arrivée imminente de l'Harmattan va griller immédiatement les jeunes plants."
            }

    # 4. ANALYSE ACTIVITÉ : FORMATION DU PRODUCTEUR SUR LE COMPOST
    elif "compost" in act or "fertilisation" in act or "engrais" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Excellent :** Période creuse, les producteurs ont du temps. Idéal pour collecter la matière sèche disponible."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Formation Compost ({periode_saisie}) - Neutre :** Les premières pluies activeront les bactéries du tas."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Pratique terrain :** Matière verte abondante et l'eau de pluie maintient l'humidité requise sans effort d'arrosage."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Formation Compost ({periode_saisie}) - Neutre :** Période dédiée principalement au suivi et retournement."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Stratégique :** Le décabossage génère des coques vides riches en potasse. Les composter évite la propagation de la pourriture brune."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Application :** Valorisation des derniers résidus de la récolte avant le climat sec."
            }
            
    return {"statut": "neutre", "msg": f"⚠️ **{nom_activite} ({periode_saisie}) :** Planification enregistrée sans directive technique spécifique."}


def dessiner_page_28_Planification_Des_Activites_Suite():
    # --- 1. MEMOIRE DE SESSION ET VALEURS PAR DÉFAUT ---
    defaults_p28 = {
        "p28_axe_1": "Axe 1 : Réhabilitation du verger",
        "p28_objectif_1": "Remettre la parcelle en bon état de production",
        # Ligne 1
        "p28_act1": "Régler la densité", "p28_co1": "200 000",
        "p28_a1_1": "Jan-Mar", "p28_a2_1": "Jan", "p28_a3_1": "-", "p28_a4_1": "-", "p28_a5_1": "-",
        "p28_re1": "producteur", "p28_pa1": "Coopérative, ANADER",
        # Ligne 2
        "p28_act2": "Réaliser la taille des cacaoyers", "p28_co2": "25 000",
        "p28_a1_2": "Avr", "p28_a2_2": "Avr", "p28_a3_2": "Avr", "p28_a4_2": "Avr", "p28_a5_2": "Avr",
        "p28_re2": "producteur", "p28_pa2": "ANADER",
        # Ligne 3
        "p28_act3": "Planter les arbres d'ombrage temporaires", "p28_co3": "-",
        "p28_a1_3": "Mai-Jui", "p28_a2_3": "Mai", "p28_a3_3": "-", "p28_a4_3": "-", "p28_a5_3": "-",
        "p28_re3": "producteur", "p28_pa3": "Cabinet",
        # Ligne 4
        "p28_act4": "Formation du producteur sur le composte", "p28_co4": "-",
        "p28_a1_4": "Oct", "p28_a2_4": "-", "p28_a3_4": "-", "p28_a4_4": "-", "p28_a5_4": "-",
        "p28_re4": "producteur", "p28_pa4": "Coopérative, Cabinet"
    }

    for key, value in defaults_p28.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- 2. STYLE CSS SÉCURISÉ ---
    st.markdown("""
    <style>
    .header-plan {
        background-color: #C6E0B4; 
        padding: 15px;
        border: 1px solid #70AD47;
        text-align: left;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .header-title {
        color: #375623;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
        font-family: 'Arial', sans-serif;
    }
    .table-pdc {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Arial', sans-serif;
        font-size: 13px;
        margin-bottom: 20px;
    }
    .table-pdc th {
        background-color: #4472C4; 
        color: white;
        border: 1px solid #A0AEC0;
        padding: 8px;
        text-align: center;
    }
    .table-pdc td {
        border: 1px solid #A0AEC0;
        padding: 8px;
        vertical-align: middle;
        text-align: center;
        background-color: white;
        color: #2D3748;
    }
    .text-left { text-align: left !important; }
    
    div.stTextInput > div > div > input {
        padding: 6px !important;
        text-align: center !important;
        font-size: 13px !important;
    }
    div.stTextArea > div > div > textarea {
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header-plan"><h1 class="header-title">PLAN D\'ACTION SUR LES CINQ PROCHAINES ANNÉES (MODE SAISIE)</h1></div>', unsafe_allow_html=True)
    
    # --- 3. ENTRÉES SYNCHRONISÉES (CORRECTION DU RE-RENDU BUG) ---
    st.session_state.p28_axe_1 = st.text_input("Axe stratégique :", value=st.session_state.p28_axe_1, key="axe_strat_input_unique")
    st.session_state.p28_objectif_1 = st.text_area("Objectif global :", value=st.session_state.p28_objectif_1, height=70, key="obj_global_input_unique")
    
    st.write("### 📝 Remplissez les lignes du plan d'action :")

    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with col1: st.markdown("**Activité**")
    with col2: st.markdown("**Coût (FCFA)**")
    with col3: st.markdown("**Mois A1**")
    with col4: st.markdown("**Mois A2**")
    with col5: st.markdown("**Mois A3**")
    with col6: st.markdown("**Mois A4**")
    with col7: st.markdown("**Mois A5**")
    with col8: st.markdown("**Responsable**")
    with col9: st.markdown("**Partenaires**")
    st.markdown("---")
    
    # --- FORMULAIRE DE LIGNE 1 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act1 = st.text_input("Act 1", value=st.session_state.p28_act1, key="input_act1", label_visibility="collapsed")
    with c2: st.session_state.p28_co1 = st.text_input("Co 1", value=st.session_state.p28_co1, key="input_co1", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_1 = st.text_input("A1_1", value=st.session_state.p28_a1_1, key="input_a1_1", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_1 = st.text_input("A2_1", value=st.session_state.p28_a2_1, key="input_a2_1", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_1 = st.text_input("A3_1", value=st.session_state.p28_a3_1, key="input_a3_1", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_1 = st.text_input("A4_1", value=st.session_state.p28_a4_1, key="input_a4_1", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_1 = st.text_input("A5_1", value=st.session_state.p28_a5_1, key="input_a5_1", label_visibility="collapsed")
    with c8: st.session_state.p28_re1 = st.text_input("Re 1", value=st.session_state.p28_re1, key="input_re1", label_visibility="collapsed")
    with c9: st.session_state.p28_pa1 = st.text_input("Pa 1", value=st.session_state.p28_pa1, key="input_pa1", label_visibility="collapsed")

    # --- FORMULAIRE DE LIGNE 2 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act2 = st.text_input("Act 2", value=st.session_state.p28_act2, key="input_act2", label_visibility="collapsed")
    with c2: st.session_state.p28_co2 = st.text_input("Co 2", value=st.session_state.p28_co2, key="input_co2", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_2 = st.text_input("A1_2", value=st.session_state.p28_a1_2, key="input_a1_2", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_2 = st.text_input("A2_2", value=st.session_state.p28_a2_2, key="input_a2_2", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_2 = st.text_input("A3_2", value=st.session_state.p28_a3_2, key="input_a3_2", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_2 = st.text_input("A4_2", value=st.session_state.p28_a4_2, key="input_a4_2", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_2 = st.text_input("A5_2", value=st.session_state.p28_a5_2, key="input_a5_2", label_visibility="collapsed")
    with c8: st.session_state.p28_re2 = st.text_input("Re 2", value=st.session_state.p28_re2, key="input_re2", label_visibility="collapsed")
    with c9: st.session_state.p28_pa2 = st.text_input("Pa 2", value=st.session_state.p28_pa2, key="input_pa2", label_visibility="collapsed")

    # --- FORMULAIRE DE LIGNE 3 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act3 = st.text_input("Act 3", value=st.session_state.p28_act3, key="input_act3", label_visibility="collapsed")
    with c2: st.session_state.p28_co3 = st.text_input("Co 3", value=st.session_state.p28_co3, key="input_co3", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_3 = st.text_input("A1_3", value=st.session_state.p28_a1_3, key="input_a1_3", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_3 = st.text_input("A2_3", value=st.session_state.p28_a2_3, key="input_a2_3", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_3 = st.text_input("A3_3", value=st.session_state.p28_a3_3, key="input_a3_3", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_3 = st.text_input("A4_3", value=st.session_state.p28_a4_3, key="input_a4_3", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_3 = st.text_input("A5_3", value=st.session_state.p28_a5_3, key="input_a5_3", label_visibility="collapsed")
    with c8: st.session_state.p28_re3 = st.text_input("Re 3", value=st.session_state.p28_re3, key="input_re3", label_visibility="collapsed")
    with c9: st.session_state.p28_pa3 = st.text_input("Pa 3", value=st.session_state.p28_pa3, key="input_pa3", label_visibility="collapsed")

    # --- FORMULAIRE DE LIGNE 4 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act4 = st.text_input("Act 4", value=st.session_state.p28_act4, key="input_act4", label_visibility="collapsed")
    with c2: st.session_state.p28_co4 = st.text_input("Co 4", value=st.session_state.p28_co4, key="input_co4", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_4 = st.text_input("A1_4", value=st.session_state.p28_a1_4, key="input_a1_4", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_4 = st.text_input("A2_4", value=st.session_state.p28_a2_4, key="input_a2_4", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_4 = st.text_input("A3_4", value=st.session_state.p28_a3_4, key="input_a3_4", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_4 = st.text_input("A4_4", value=st.session_state.p28_a4_4, key="input_a4_4", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_4 = st.text_input("A5_4", value=st.session_state.p28_a5_4, key="input_a5_4", label_visibility="collapsed")
    with c8: st.session_state.p28_re4 = st.text_input("Re 4", value=st.session_state.p28_re4, key="input_re4", label_visibility="collapsed")
    with c9: st.session_state.p28_pa4 = st.text_input("Pa 4", value=st.session_state.p28_pa4, key="input_pa4", label_visibility="collapsed")

    st.markdown("---")
    st.write("### 👁️ Rendu Visuel Officiel de la Page 28 :")

    # --- 4. CRÉATION DU TABLEAU MATRICIEL DYNAMIQUE ---
    html_table = f"""
    <table class="table-pdc">
        <thead>
            <tr>
                <th rowspan="2">Axes stratégiques</th>
                <th rowspan="2">Objectifs</th>
                <th rowspan="2">Activités</th>
                <th rowspan="2">Coût (F CFA)</th>
                <th colspan="5">Période (Mois d'exécution)</th>
                <th rowspan="2">Responsable</th>
                <th rowspan="2">Partenaires</th>
            </tr>
            <tr>
                <th style="background-color:#4472C4;">A1</th>
                <th style="background-color:#4472C4;">A2</th>
                <th style="background-color:#4472C4;">A3</th>
                <th style="background-color:#4472C4;">A4</th>
                <th style="background-color:#4472C4;">A5</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td rowspan="4" style="background-color:#F2F2F2; font-weight:bold; color:black;">{st.session_state.p28_axe_1}</td>
                <td rowspan="4" class="text-left" style="color:black;">{st.session_state.p28_objectif_1}</td>
                <td class="text-left">{st.session_state.p28_act1}</td>
                <td>{st.session_state.p28_co1}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_1}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a2_1}</td>
                <td>{st.session_state.p28_a3_1}</td><td>{st.session_state.p28_a4_1}</td><td>{st.session_state.p28_a5_1}</td>
                <td>{st.session_state.p28_re1}</td>
                <td rowspan="4" class="text-left" style="font-size: 12px;">{st.session_state.p28_pa1}<br><br>{st.session_state.p28_pa2}<br><br>{st.session_state.p28_pa3}</td>
            </tr>
            <tr>
                <td class="text-left">{st.session_state.p28_act2}</td>
                <td>{st.session_state.p28_co2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a2_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a3_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a4_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a5_2}</td>
                <td>{st.session_state.p28_re2}</td>
            </tr>
            <tr>
                <td class="text-left">{st.session_state.p28_act3}</td>
                <td>{st.session_state.p28_co3}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_3}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a2_3}</td>
                <td>{st.session_state.p28_a3_3}</td><td>{st.session_state.p28_a4_3}</td><td>{st.session_state.p28_a5_3}</td>
                <td>{st.session_state.p28_re3}</td>
            </tr>
            <tr>
                <td class="text-left">{st.session_state.p28_act4}</td>
                <td>{st.session_state.p28_co4}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_4}</td>
                <td>{st.session_state.p28_a2_4}</td><td>{st.session_state.p28_a3_4}</td><td>{st.session_state.p28_a4_4}</td><td>{st.session_state.p28_a5_4}</td>
                <td>{st.session_state.p28_re4}</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    # --- 5. ANALYSE CHRONOLOGIQUE DE LEILA IA ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Le Diagnostic Chronologique de Leila :")

    plan_saisi = [
        {"nom": st.session_state.p28_act1, "periodes": [st.session_state.p28_a1_1, st.session_state.p28_a2_1, st.session_state.p28_a3_1, st.session_state.p28_a4_1, st.session_state.p28_a5_1]},
        {"nom": st.session_state.p28_act2, "periodes": [st.session_state.p28_a1_2, st.session_state.p28_a2_2, st.session_state.p28_a3_2, st.session_state.p28_a4_2, st.session_state.p28_a5_2]},
        {"nom": st.session_state.p28_act3, "periodes": [st.session_state.p28_a1_3, st.session_state.p28_a2_3, st.session_state.p28_a3_3, st.session_state.p28_a4_3, st.session_state.p28_a5_3]},
        {"nom": st.session_state.p28_act4, "periodes": [st.session_state.p28_a1_4, st.session_state.p28_a2_4, st.session_state.p28_a3_4, st.session_state.p28_a4_4, st.session_state.p28_a5_4]}
    ]

    with st.container():
        alertes_affichees = 0
        
        for item in plan_saisi:
            periodes_valides = [p for p in item["periodes"] if p and p.strip() != "-"]
            # Extraction propre des mois si format étendu (ex: "Jan-Mar" -> ["Jan", "Mar"])
            periodes_uniques = []
            for pv in periodes_valides:
                if "-" in pv:
                    periodes_uniques.extend([m.strip() for m in pv.split("-")])
                else:
                    periodes_uniques.append(pv.strip())
            
            periodes_uniques = list(set(periodes_uniques))
            
            for per in periodes_uniques:
                analyse = analyser_activite_layla(item["nom"], per)
                
                if analyse["statut"] == "success":
                    st.success(analyse["msg"])
                    alertes_affichees += 1
                elif analyse["statut"] == "warning":
                    st.warning(analyse["msg"])
                    alertes_affichees += 1
                elif analyse["statut"] == "error":
                    st.error(analyse["msg"])
                    alertes_affichees += 1
                elif analyse["statut"] == "info":
                    st.info(analyse["msg"])
                    alertes_affichees += 1

        if alertes_affichees == 0:
            st.info("🟢 **Leila :** Aucune anomalie chronologique détectée. Le plan d'action suit parfaitement le calendrier cultural ivoirien.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p28", type="primary", use_container_width=True):
        st.session_state["page_28_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 29
        st.rerun()

    # --- PIED DE PAGE ET NUMÉROTATION RÉGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_empty, col_page = st.columns([0.95, 0.05])
    with col_page:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>28</span>", unsafe_allow_html=True)


def dessiner_page_29_Calendrier_Activites():
    # --- STYLE CSS POUR REPRODUCTION MIROIR ---
    st.markdown("""
    <style>
    /* Fond de page blanc */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Bandeau d'en-tête vert */
    .header-bar-p29 {
        background-color: #C6EFCE; 
        border: 1.5px solid #2E7D32;
        padding: 15px 25px;
        margin-bottom: 40px;
    }

    .header-title-p29 {
        color: #006100;
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Style du titre avec le losange (❖) */
    .main-title-container-p29 {
        display: flex;
        align-items: flex-start;
        margin-left: 40px;
        margin-bottom: 30px;
    }

    .diamond-icon-p29 {
        color: #008080;
        font-size: 26px;
        margin-right: 12px;
        line-height: 1;
    }

    .main-title-text-p29 {
        color: #008080;
        font-size: 22px;
        font-weight: bold;
        text-decoration: underline;
        font-family: 'Arial', sans-serif;
    }

    /* Texte descriptif et conteneur global */
    .content-area-p29 {
        margin-left: 90px;
        font-family: 'Arial', sans-serif;
        font-size: 19px;
        color: #000000;
        line-height: 1.5;
    }

    /* Style pour la liste principale avec les cercles (o) */
    .main-list-p29 {
        list-style-type: none;
        padding-left: 0;
        margin-top: 20px;
    }

    .list-item-p29 {
        position: relative;
        padding-left: 25px;
    }

    /* Reproduction exacte du petit cercle 'o' */
    .list-item-p29::before {
        content: "o";
        position: absolute;
        left: 0;
        top: -2px;
        font-weight: bold;
        color: #000000;
    }

    /* Sous-liste imbriquée */
    .nested-list-p29 {
        list-style-type: none;
        padding-left: 30px;
        margin-top: 10px;
    }

    .nested-item-p29 {
        position: relative;
        margin-bottom: 8px;
    }

    /* Tirets d'énumération clairs */
    .nested-item-p29::before {
        content: "-";
        position: absolute;
        left: -20px;
        color: #000000;
        font-weight: bold;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p29 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- CONTENU DE LA PAGE ---

    # 1. Bandeau de titre supérieur
    st.markdown('<div class="header-bar-p29"><h1 class="header-title-p29">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1></div>', unsafe_allow_html=True)

    # 2. Titre principal de la fiche avec icône ❖
    st.markdown('<div class="main-title-container-p29"><span class="diamond-icon-p29">❖</span><span class="main-title-text-p29">Elaboration du calendrier annuel des activités</span></div>', unsafe_allow_html=True)

    # 3. Bloc de texte descriptif et listes (Tout écrit en une seule ligne continue pour bloquer le bug de rendu Streamlit)
    html_liste_strict = '<div class="content-area-p29"><p>Les activités à réaliser doivent être décrites en détail, programmées et <br> intégrées dans une matrice de calendrier annuel d\'activités.</p><ul class="main-list-p29"><li class="list-item-p29">Préciser pour chaque axe stratégique :<ul class="nested-list-p29"><li class="nested-item-p29">les activités,</li><li class="nested-item-p29">les indicateurs opérationnels de suivi,</li><li class="nested-item-p29">les échéances,</li><li class="nested-item-p29">les coûts, ainsi que</li><li class="nested-item-p29">les responsabilités de chacun des acteurs.</li></ul></li></ul></div>'
    st.markdown(html_liste_strict, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p29", type="primary", use_container_width=True):
        st.session_state["page_29_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 30
        st.rerun()

    # 4. Numéro de page officiel (Page 29)
    st.markdown('<div class="footer-page-p29">29</div>', unsafe_allow_html=True)


def dessiner_page_30_Methodologie_Calendrier():
    # --- STYLE CSS APPLIQUÉ DE MANIÈRE SÉCURISÉE ---
    st.markdown("""
    <style>
    /* Fond de page blanc */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Bandeau d'en-tête vert */
    .header-bar-p30 {
        background-color: #C6EFCE; 
        border: 1.5px solid #2E7D32;
        padding: 15px 25px;
        margin-bottom: 40px;
    }

    .header-title-p30 {
        color: #006100;
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Conteneur principal pour le texte */
    .content-area-p30 {
        margin-left: 60px;
        font-family: 'Arial', sans-serif;
        color: #000000;
    }

    /* Style du titre d'introduction */
    .intro-text-p30 {
        font-size: 21px;
        font-weight: bold;
        margin-bottom: 30px;
        line-height: 1.4;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p30 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- CONTENU DE LA PAGE ---

    # 1. Bandeau de titre supérieur
    st.markdown('<div class="header-bar-p30"><h1 class="header-title-p30">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1></div>', unsafe_allow_html=True)

    # 2. Zone de contenu principal
    st.markdown('<div class="content-area-p30"><p class="intro-text-p30">L’élaboration du calendrier annuel d’activités se fait de la manière suivante :</p></div>', unsafe_allow_html=True)

    # 3. Utilisation des composants natifs Streamlit
    col_space, col_content = st.columns([0.1, 0.9])
    
    with col_content:
        st.markdown("**• Dresser la liste des principales activités :** Ce sont les activités retenues à l'issue du diagnostic de l'exploitation.")
        st.write("") # Espace de respiration
        
        st.markdown("**• Répartir les principales activités en tâches opérationnelles :** identifier pour chaque activité, les sous-activités, diviser les sous-activités en tâches.")
        st.write("")
        
        st.markdown("**• Estimer la date de démarrage, la durée et la date de finalisation** de chaque activité.")
        st.write("")
        
        st.markdown("**• Définir les compétences requises :**")
        st.write("")
        
        st.markdown("**• Répartir les tâches au sein de l'équipe :**")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p30", type="primary", use_container_width=True):
        st.session_state["page_30_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 31
        st.rerun()

    # 4. Numéro de page officiel corrigé (Page 30 au lieu de 42)
    st.markdown('<div class="footer-page-p30">30</div>', unsafe_allow_html=True)


def analyser_trimestre_layla(activite, sous_act, trimestre):
    """
    Moteur agronomique de Leila pour la Côte d'Ivoire.
    Analyse la cohérence entre la sous-activité choisie et le trimestre coché.
    """
    act = activite.lower()
    sa = sous_act.lower()
    t = trimestre.upper()
    
    # --- 1. RÉGLER LA DENSITÉ ---
    if "densité" in act or "densite" in act:
        if "diagnostic" in sa or "marquage" in sa or "identifier" in sa:
            if t in ["T1", "T4"]:
                return "success", f"🟢 **[Régler la densité] Idéal en {t} :** La saison sèche et la fin des récoltes offrent une excellente visibilité au sol pour repérer et marquer les arbres en surpeuplement."
            return "info", f"🟡 **[Régler la densité] Possible en {t} :** Attention, l'enherbement et la végétation dense réduisent la visibilité pour un bon diagnostic."
        
        elif "abattage" in sa or "supprimer" in sa or "essartage" in sa:
            if t == "T1":
                return "success", f"🔥 **[Régler la densité] Recommandé en T1 (Grande saison sèche) :** Le bois est sec, le sol est stable. Abattre un arbre maintenant limite les dégâts racinaires sur les cacaoyers voisins."
            elif t == "T2":
                return "warning", f"⚠️ **[Régler la densité] Prudence en T2 (Grandes pluies) :** Sol glissant et boueux. Risque de déraciner ou de blesser les coussinets floraux."
            return "error", f"❌ **[Régler la densité] À proscrire en {t} (Période critique) :** Les arbres sont en pleine floraison ou chargés de cabosses. Risque de pertes économiques directes."

    # --- 2. ENTRETIEN ---
    elif "entretenir" in act or "entretien" in act:
        if "loranthacées" in sa or "gui" in sa:
            if t in ["T1", "T2"]:
                return "success", f"🟢 **[Entretenir] Crucial en {t} :** Éliminer le gui (loranthus) avant la poussée de sève permet au cacaoyer de maximiser ses nutriments."
            return "warning", f"⚠️ **[Entretenir] Moins efficace en {t} :** Le parasite s'est déjà propagé. Nettoyage tardif."
        
        elif "taille d'entretien" in sa or "élagage" in sa:
            if t == "T2":
                return "success", f"🏆 **[Entretenir] Période maîtresse (T2) :** Aérer la canopée juste avant les grandes pluies réduit l'humidité stagnante, freinant la pourriture brune."
            elif t == "T1":
                return "error", f"❌ **[Entretenir] Danger en T1 :** Une taille trop sévère expose le tronc nu au soleil direct de la saison sèche, risquant de brûler l'écorce."
            return "info", f"🟡 **[Entretenir] Passage léger en {t} :** Égourmandage ciblé uniquement."
            
        elif "sanitaire" in sa:
            if t in ["T2", "T3"]:
                return "success", f"🟢 **[Entretenir] Urgence Sanitaire ({t}) :** En pleine saison des pluies, retirer les cabosses momifiées stoppe la progression du Phytophthora."
            return "info", f"🟢 **[Entretenir] Routine ({t}) :** La récolte sanitaire doit s'effectuer de manière continue."

    return "neutre", f"📋 **Planification enregistrée ({t}) :** Activité programmée sans contre-indication majeure."
