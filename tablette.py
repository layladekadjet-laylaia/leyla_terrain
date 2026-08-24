import streamlit as st
import sqlite3
import os
from datetime import datetime
import requests

# --- IMPORTATION DE TES MODULES ---
import diagnostique
import estimation_de_rendement
import geolocalisation

# --- CONFIGURATION DE LA TABLETTE ---
st.set_page_config(page_title="Leyla Agri - Tablette Terrain", page_icon="📱", layout="centered")

# --- INITIALISATION DE LA BASE DE DONNÉES LOCALE (SQLite) ---
def init_local_db():
    conn = sqlite3.connect("leyla_terrain.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rapports_locaux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cooperative TEXT,
            section TEXT,
            technicien TEXT,
            producteur TEXT,
            code_producteur TEXT,
            superficie REAL,
            age_parcelle TEXT,
            module_type TEXT,
            donnees_module TEXT,
            date_saisie TEXT,
            statut TEXT DEFAULT 'En attente'
        )
    """)
    conn.commit()
    conn.close()

init_local_db()

# --- 1. PROFIL D'IDENTIFICATION (VERROUILLÉ AU DÉMARRAGE) ---
st.title("📱 Leyla Agri - Mode Terrain")
st.markdown("---")

if "identifie" not in st.session_state:
    st.session_state.identifie = False

if not st.session_state.identifie:
    st.subheader("🔒 Profil d'identification du Technicien")
    with st.form("form_identification"):
        cooperative = st.text_input("Identification de la Coopérative", value="SCACO")
        section = st.text_input("Identification de la Section", value="Section Divo-Sud")
        technicien = st.text_input("Nom, Prénom & Identifiant", value="Agent Kouamé Konan - ID 0001")
        
        btn_valider_profil = st.form_submit_button("Enregistrer et Verrouiller le Profil")
        if btn_valider_profil:
            if cooperative and section and technicien:
                st.session_state.cooperative = cooperative
                st.session_state.section = section
                st.session_state.technicien = technicien
                st.session_state.identifie = True
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs d'identification.")
    st.stop()

with st.sidebar:
    st.markdown("### 👤 Session Active")
    st.write(f"**Coop :** {st.session_state.cooperative}")
    st.write(f"**Section :** {st.session_state.section}")
    st.write(f"**Agent :** {st.session_state.technicien}")
    if st.button("🔓 Modifier le profil"):
        st.session_state.identifie = False
        st.rerun()

# --- 2. FICHE DE SAISIE DU PRODUCTEUR & DE LA PARCELLE ---
st.header("📋 Fiche Producteur & Parcelle")
col1, col2 = st.columns(2)
with col1:
    nom_producteur = st.text_input("Nom du Producteur", key="nom_prod_tab")
    code_producteur = st.text_input("Code du Producteur (optionnel)", key="code_prod_tab")
with col2:
    superficie = st.number_input("Superficie (Hectares)", min_value=0.1, step=0.1, value=1.0, key="sup_prod_tab")
    age_parcelle = st.text_input("Âge de la cacaoyère (ex: 12 ans)", key="age_prod_tab")

# Stockage dans le session_state pour accès global par les modules si besoin
st.session_state.info_producteur = {
    "nom": nom_producteur,
    "code": code_producteur,
    "superficie": superficie,
    "age": age_parcelle
}

st.markdown("---")

# --- 3. SÉLECTION ET EXÉCUTION DES MODULES TERRAIN ---
st.header("🛠️ Modules de Saisie")
choix_module = st.selectbox(
    "Sélectionnez le module à exécuter :",
    ["-- Choisir un module --", "1. Diagnostic Phytosanitaire", "2. Géo-intelligence & RDUE", "3. Estimation de Rendement"]
)

st.markdown("---")

# --- APPEL DES VRAIS MODULES ---
if choix_module == "1. Diagnostic Phytosanitaire":
    diagnostique.afficher()

elif choix_module == "2. Géo-intelligence & RDUE":
    geolocalisation.afficher()

elif choix_module == "3. Estimation de Rendement":
    estimation_de_rendement.afficher()

# --- 4. SYNCHRONISATION / ENVOI AU SERVEUR CENTRAL ---
st.markdown("---")
st.header("🔄 Synchronisation / Envoi au Serveur Central")
st.info("Lorsque vous disposez d'une connexion Internet, cliquez ci-dessous pour envoyer les données vers le serveur central Supabase.")

conn = sqlite3.connect("leyla_terrain.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM rapports_locaux WHERE statut='En attente'")
nombre_attente = cursor.fetchone()[0]
conn.close()

st.write(f"📦 Rapports en attente d'envoi dans la tablette : **{nombre_attente}**")

if st.button("🚀 SYNCHRONISER / ENVOYER AU SERVEUR CENTRAL", use_container_width=True):
    if nombre_attente > 0:
        try:
            url_supabase = st.secrets["supabase"]["url"]
            key_supabase = st.secrets["supabase"]["key"]
            
            headers = {
                "apikey": key_supabase,
                "Authorization": f"Bearer {key_supabase}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            }
            endpoint = f"{url_supabase}/rest/v1/producteurs_parcelles"

            conn = sqlite3.connect("leyla_terrain.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, cooperative, section, technicien, producteur, code_producteur, superficie, age_parcelle, module_type, donnees_module FROM rapports_locaux WHERE statut='En attente'")
            lignes = cursor.fetchall()
            
            for ligne in lignes:
                row_id, coop, sec, tech, prod, code_p, sup, age_p, mod_t, donnees_m = ligne
                
                age_int = 0
                try:
                    age_int = int(''.join(filter(str.isdigit, str(age_p))))
                except:
                    age_int = 0

                payload = {
                    "cooperative_id": coop,
                    "section_id": sec,
                    "agent_id": tech,
                    "nom_producteur": prod,
                    "code_producteur": str(code_p) if code_p else "",
                    "superficie": float(sup),
                    "age_cacaoyere": age_int,
                    "module_execute": mod_t,
                    "observations_diagnostic": donnees_m,
                    "rdue_conforme": True
                }
                
                response = requests.post(endpoint, json=payload, headers=headers)
                
                if response.status_code in [200, 201, 204]:
                    cursor.execute("UPDATE rapports_locaux SET statut='Envoyé' WHERE id=?", (row_id,))
                else:
                    st.error(f"Erreur HTTP {response.status_code}: {response.text}")
                    break
            
            conn.commit()
            conn.close()
            st.success("Synchronisation réussie ! Toutes les données ont été transmises à Supabase.")
            st.rerun()
            
        except Exception as e:
            st.error(f"Erreur lors de la transmission : {e}")
    else:
        st.warning("Aucune nouvelle donnée en attente de synchronisation.")
