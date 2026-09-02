import streamlit as st
import sqlite3
import os
from datetime import datetime
import requests

# --- IMPORTATION DES MODULES ---
import diagnostique
import geolocalisation
import estimation_de_rendement
import pdc
from generate_croquis import generer_croquis_parcelle

# --- CONFIGURATION DE LA TABLETTE ---
st.set_page_config(page_title="Leyla Agri - Tablette Terrain", page_icon="📱", layout="centered")

# --- INITIALISATION DE LA SESSION ---
if "appareil_deverrouille" not in st.session_state:
    st.session_state.appareil_deverrouille = False

if "identifie" not in st.session_state:
    st.session_state.identifie = False

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

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.markdown("### 👤 Session Active")
    st.write(f"**Coop :** {st.session_state.cooperative}")
    st.write(f"**Section :** {st.session_state.section}")
    st.write(f"**Agent :** {st.session_state.technicien}")
    
    if st.button("🔓 Modifier le profil"):
        st.session_state.identifie = False
        st.rerun()

    st.markdown("---")
    if st.session_state.appareil_deverrouille:
        if st.button("🔒 Verrouiller la tablette", use_container_width=True):
            st.session_state.appareil_deverrouille = False
            st.rerun()

# --- 2. ÉCRAN DE DÉVERROUILLAGE TECHNICIEN ---
MOT_DE_PASSE_VALIDE = "leyla2.6" 

if not st.session_state.appareil_deverrouille:
    st.header("🔒 Accès Sécurisé Technicien")
    st.caption("Veuillez saisir votre mot de passe pour déverrouiller l'application Leyla et accéder aux modules.")

    with st.form("form_login_technicien"):
        code_agent = st.text_input("Code Agent / Technicien", placeholder="Ex: Agent Kouame", key="input_code_agent")
        mot_de_passe = st.text_input("Mot de passe *", type="password", key="input_mdp_technicien")
        btn_valider = st.form_submit_button("🔓 Déverrouiller la tablette", type="primary", use_container_width=True)

    if btn_valider:
        if mot_de_passe == MOT_DE_PASSE_VALIDE:
            st.session_state.appareil_deverrouille = True
            st.session_state.code_agent_connecte = code_agent
            st.success(f"✅ Déverrouillage réussi. Bienvenue Agent {code_agent} !")
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect. Accès refusé.")

    st.warning("⚠️ L'application est verrouillée. Entrez le mot de passe pour continuer.")
    st.stop()

# --- 3. ACCÈS AUX MODULES (UNISSONS UNE FOIS DÉVERROUILLÉ) ---
st.header("🛠️ Modules de Saisie")
st.caption(f"👤 Session Agent : **{st.session_state.get('code_agent_connecte', 'Inconnu')}**")

choix_module = st.selectbox(
    "Sélectionnez le module à exécuter :",
    [
        "-- Choisir un module --",
        "1. Diagnostic Phytosanitaire",
        "2. Géo-intelligence & RDUE",
        "3. Estimation de Rendement",
        "4. PDC",            
    ]
)

import streamlit as st
import time

# =========================================================
# BARRE LATÉRALE (SIDEBAR) : ACTIONS FINALES (PDF & SAUVEGARDE)
# =========================================================
with st.sidebar:
    st.markdown("## 📄 Actions PDC")
    
    # 1. BOUTON : VALIDER & GÉNÉRER LE PDF
    if st.button("🎓 Générer le PDF Final", key="sb_btn_generer_pdf", type="primary", use_container_width=True):
        # Récupération sécurisée du score et des identifiants
        score_final = st.session_state.get("score_pdc", 0)
        code_prod = st.session_state.get("code_producteur", "CCC-001")
        nom_prod = st.session_state.get("nom_producteur", "Inconnu")
        section_zone = st.session_state.get("section", "Zone Centre")

        payload_pdf = {
            "nom_producteur": nom_prod,
            "code_ccc": code_prod,
            "zone": section_zone,
            "score_faisabilite": score_final,
            "reponses": st.session_state.get("reponses_pdc", {})
        }
        
        try:
            # Génération du PDF
            pdf_bytes = generer_pdf_pdc_fonction(payload_pdf)
            st.session_state["pdf_bytes_pdc"] = pdf_bytes
            st.success("✅ PDF généré avec succès !")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Erreur PDF : {e}")

    # 2. BOUTON : TÉLÉCHARGER LE PDF (Affiche le bouton de téléchargement si le PDF a été généré)
    if st.session_state.get("pdf_bytes_pdc"):
        code_prod = st.session_state.get("code_producteur", "CCC-001")
        nom_prod = st.session_state.get("nom_producteur", "Inconnu")
        
        st.download_button(
            label="📥 Télécharger le PDF",
            data=st.session_state["pdf_bytes_pdc"],
            file_name=f"PDC_{code_prod}_{nom_prod}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="sb_btn_download_pdf"
        )

    st.markdown("---")

    # 3. BOUTON : ENREGISTRER SUR LA TABLETTE (SQLITE)
    if st.button("💾 Enregistrer dans la tablette", type="secondary", key="sb_btn_sauvegarder_sqlite", use_container_width=True):
        code_prod = st.session_state.get("code_producteur", "CCC-001")
        nom_prod = st.session_state.get("nom_producteur", "Inconnu")
        section_zone = st.session_state.get("section", "Zone Centre")
        score_final = st.session_state.get("score_pdc", 0)

        # Extraction propre du session_state complet
        session_complete = {}
        for key, val in st.session_state.items():
            if key not in ["pdf_bytes_pdc"] and not key.startswith("btn_") and not key.startswith("sb_"):
                session_complete[key] = val

        donnees_dossier_pdc = {
            "type_document": "PDC_COMPLET",
            "code_ccc": code_prod,
            "nom_producteur": nom_prod,
            "zone": section_zone,
            "score_faisabilite": score_final,
            "reponses_pdc": st.session_state.get("reponses_pdc", {}),
            "etat_session_integral": nettoyer_pour_json(session_complete),
            "croquis_base64": st.session_state.get("croquis_genere", None),
            "facteurs_succes": st.session_state.get("facteurs_succes_pdc", ""),
            "statut_synchro": "En attente de synchro"
        }

        try:
            sauvegarder_en_local_sqlite(donnees_dossier_pdc)
            st.success(f"💾 Dossier sauvegardé en local !")
            st.balloons()
            
            time.sleep(1.5)

            # Réinitialisation propre
            st.session_state.etape_pdc = 1
            st.session_state.reponses_pdc = {}
            st.session_state.pop("croquis_genere", None)
            st.session_state.pop("facteurs_succes_pdc", None)
            st.session_state.pop("pdf_bytes_pdc", None)

            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur SQLite : {e}")


st.markdown("---")

# --- APPEL DES MODULES ---
if choix_module == "1. Diagnostic Phytosanitaire":
    diagnostique.afficher()

elif choix_module == "2. Géo-intelligence & RDUE":
    geolocalisation.afficher()

elif choix_module == "3. Estimation de Rendement":
    estimation_de_rendement.afficher()

elif choix_module == "4. PDC":
    pdc.afficher()

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
