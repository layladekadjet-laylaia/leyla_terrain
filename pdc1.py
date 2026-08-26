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
    st.subheader("Module PDC 1")
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
