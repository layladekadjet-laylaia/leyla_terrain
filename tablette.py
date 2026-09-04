import streamlit as st
import sqlite3
import os
import json
import time
from datetime import datetime
import requests
import numpy as np
import pandas as pd

# --- IMPORTATION DES MODULES ---
import diagnostique
import geolocalisation
import estimation_de_rendement
import pdc
from generate_croquis import generer_croquis_parcelle

# --- CONFIGURATION DE LA PAGE (UNE SEULE FOIS AU DÉBUT) ---
st.set_page_config(page_title="Leyla Agri - Tablette Terrain", page_icon="📱", layout="centered")

# --- FONCTIONS UTILITAIRES POUR JSON ET SQLITE ---
class NpEncoder(json.JSONEncoder):
    """Convertit les types NumPy / Pandas en types natifs Python."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if pd.isna(obj):
            return None
        return super(NpEncoder, self).default(obj)

def nettoyer_pour_json(d):
    """Nettoie récursivement un dictionnaire pour la sérialisation JSON."""
    if isinstance(d, dict):
        return {
            str(k): nettoyer_pour_json(v) 
            for k, v in d.items() 
            if not str(k).startswith("FormSubmitter") and not str(k).startswith("btn_") and not str(k).startswith("sb_")
        }
    elif isinstance(d, list):
        return [nettoyer_pour_json(v) for v in d]
    elif isinstance(d, (np.integer, int)):
        return int(d)
    elif isinstance(d, (np.floating, float)):
        return float(d)
    elif isinstance(d, bytes):
        return None
    else:
        return d


def charger_donnees_par_module(nom_module):
    """Charge et filtre uniquement les enregistrements du module actif."""
    try:
        conn = sqlite3.connect("leyla_terrain.db")
        query = "SELECT * FROM rapports_locaux WHERE module_type = ?"
        df = pd.read_sql_query(query, conn, params=(nom_module,))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur lors de la lecture : {e}")
        return pd.DataFrame()


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

# --- TITRE PRINCIPAL ---
st.title("📱 Leyla Agri - Mode Terrain")
st.markdown("---")

# --- 1. PROFIL D'IDENTIFICATION (VERROUILLÉ AU DÉMARRAGE) ---
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

# --- BARRE LATÉRALE (UNIQUE) ---
with st.sidebar:
    st.markdown("### 👤 Session Active")
    st.write(f"**Coop :** {st.session_state.get('cooperative', 'N/A')}")
    st.write(f"**Section :** {st.session_state.get('section', 'N/A')}")
    st.write(f"**Agent :** {st.session_state.get('technicien', 'N/A')}")
    
    if st.button("🔓 Modifier le profil", key="sb_btn_modifier_profil"):
        st.session_state.identifie = False
        st.rerun()

    st.markdown("---")
    if st.session_state.appareil_deverrouille:
        if st.button("🔒 Verrouiller la tablette", use_container_width=True, key="sb_btn_verrouiller"):
            st.session_state.appareil_deverrouille = False
            st.rerun()

    st.markdown("---")
    st.markdown("## 📄 Actions PDC")
    
    # 1. BOUTON : GENERER LE PDF FINAL
    if st.button("🎓 Générer le PDF Final", key="sb_btn_generer_pdf", type="primary", use_container_width=True):
        reponses_completes = {}
        
        if "reponses_pdc" in st.session_state and isinstance(st.session_state.reponses_pdc, dict):
            reponses_completes.update(st.session_state.reponses_pdc)
        
        cles_a_ignorer = [
            "appareil_deverrouille", "identifie", "code_agent_connecte", 
            "pdf_bytes_pdc", "etape_pdc", "reponses_pdc"
        ]
        
        for k, v in st.session_state.items():
            if not str(k).startswith("btn_") and not str(k).startswith("sb_") and not str(k).startswith("FormSubmitter") and k not in cles_a_ignorer:
                if isinstance(v, (str, int, float, bool, list, dict)):
                    reponses_completes[k] = v

        nom_prod = st.session_state.get("nom_producteur") or st.session_state.get("producteur") or st.session_state.get("nom_prod", "Inconnu")
        code_prod = st.session_state.get("code_producteur") or st.session_state.get("code_ccc", "CCC-001")
        section_zone = st.session_state.get("section") or st.session_state.get("zone", "Section Divo-Sud")
        score_final = st.session_state.get("score_pdc") or st.session_state.get("score_faisabilite") or st.session_state.get("score", 0)

        payload_pdf = {
            "nom_producteur": nom_prod,
            "code_ccc": code_prod,
            "zone": section_zone,
            "score_faisabilite": score_final,
            "reponses": reponses_completes
        }
        
        try:
            pdf_bytes = pdc.generer_pdf_pdc_fonction(payload_pdf)
            st.session_state["pdf_bytes_pdc"] = pdf_bytes
            st.success("✅ PDF généré avec succès !")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Erreur PDF : {e}")

    # 2. BOUTON : TÉLÉCHARGER LE PDF
    if st.session_state.get("pdf_bytes_pdc"):
        code_p = st.session_state.get("code_producteur", "CCC-001")
        nom_p = st.session_state.get("nom_producteur", "Inconnu")
        
        st.download_button(
            label="📥 Télécharger le PDF",
            data=st.session_state["pdf_bytes_pdc"],
            file_name=f"PDC_{code_p}_{nom_p}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="sb_btn_download_pdf"
        )

    st.markdown("---")

    # 3. BOUTON : ENREGISTRER SUR LA TABLETTE (SQLITE)
    if st.button("💾 Enregistrer dans la tablette", type="secondary", key="sb_btn_sauvegarder_sqlite", use_container_width=True):
        # Identification du profil
        coop = st.session_state.get("cooperative", "SCACO")
        sec = st.session_state.get("section", "Section Divo-Sud")
        tech = st.session_state.get("technicien", "Agent Kouamé")
        
        # Récupération depuis les étapes du PDC
        reponses = st.session_state.get("reponses_pdc", {})
        
        # 1. Extraction du nom (Priorité à l'Étape 11)
        nom_prod = (
            reponses.get("nom_prenoms_producteur") 
            or st.session_state.get("nom_prenoms_producteur")
            or reponses.get("nom_membre")
            or st.session_state.get("nom_producteur")
            or "Producteur Inconnu"
        )
        
        # 2. Extraction du code (Priorité à l'Étape 11)
        code_prod = (
            reponses.get("code_national_producteur") 
            or st.session_state.get("code_national_producteur")
            or reponses.get("code_groupe")
            or st.session_state.get("code_producteur")
            or "CCC-000"
        )
        
        superficie = st.session_state.get("superficie") or st.session_state.get("superficie_ha") or 0.0
        age_p = str(st.session_state.get("age_parcelle") or st.session_state.get("age_cacaoyere") or "0")

        # Mise à jour globale dans la session
        st.session_state["nom_producteur"] = nom_prod
        st.session_state["code_producteur"] = code_prod

        # Rassemblement complet des réponses
        session_complete = {}
        if isinstance(reponses, dict):
            session_complete.update(reponses)
            
        cles_a_ignorer = ["appareil_deverrouille", "identifie", "code_agent_connecte", "pdf_bytes_pdc"]
        for k, v in st.session_state.items():
            if not str(k).startswith("btn_") and not str(k).startswith("sb_") and not str(k).startswith("FormSubmitter") and k not in cles_a_ignorer:
                if isinstance(v, (str, int, float, bool, list, dict)):
                    session_complete[k] = v

        donnees_json_str = json.dumps(nettoyer_pour_json(session_complete), cls=NpEncoder, ensure_ascii=False)
        date_saisie = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect("leyla_terrain.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rapports_locaux (
                    cooperative, section, technicien, producteur, code_producteur, 
                    superficie, age_parcelle, module_type, donnees_module, date_saisie, statut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'En attente')
            """, (coop, sec, tech, nom_prod, code_prod, float(superficie), age_p, "PDC", donnees_json_str, date_saisie))
            
            conn.commit()
            conn.close()

            st.success(f"💾 Fiche PDC enregistrée pour : **{nom_prod}** ({code_prod})")
            st.balloons()
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur lors de la sauvegarde SQLite : {e}")

    # ==============================================================================
    # SYNCHRONISATION EN BARRE LATÉRALE (SIDEBAR)
    # ==============================================================================
    st.markdown("---")
    st.subheader("🔄 Synchronisation Supabase")

    # 1. Compter les rapports en attente
    try:
        conn = sqlite3.connect("leyla_terrain.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rapports_locaux WHERE statut='En attente'")
        nombre_attente = cursor.fetchone()[0]
        conn.close()
    except Exception:
        nombre_attente = 0

    st.write(f"📦 Rapports en attente : **{nombre_attente}**")

    # 2. Bouton de synchronisation
    if st.button("🚀 SYNCHRONISER AHORA", use_container_width=True, key="sb_btn_synchro_supabase"):
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
                cursor.execute("""
                    SELECT id, cooperative, section, technicien, producteur, code_producteur, 
                           superficie, age_parcelle, module_type, donnees_module 
                    FROM rapports_locaux 
                    WHERE statut='En attente'
                """)
                lignes = cursor.fetchall()
                
                nb_succes = 0
                
                for ligne in lignes:
                    row_id, coop, sec, tech, prod, code_p, sup, age_p, mod_t, donnees_m = ligne
                    
                    # Extraire uniquement les chiffres de l'âge
                    try:
                        age_int = int(''.join(filter(str.isdigit, str(age_p))))
                    except ValueError:
                        age_int = 0

                    # Formater le contenu sous forme de chaîne JSON propre
                    if isinstance(donnees_m, (dict, list)):
                        donnees_str = json.dumps(donnees_m)
                    else:
                        donnees_str = str(donnees_m) if donnees_m else "{}"

                    # Payload nettoyé pour éviter tout rejet HTTP 400
                    payload = {
                        "cooperative_id": str(coop) if coop else "",
                        "section_id": str(sec) if sec else "",
                        "agent_id": str(tech) if tech else "",
                        "nom_producteur": str(prod) if prod else "",
                        "code_producteur": str(code_p) if code_p else "",
                        "superficie": float(sup) if sup else 0.0,
                        "age_cacaoyere": age_int,
                        "module_execute": str(mod_t) if mod_t else "",
                        "observations_diagnostic": donnees_str,
                        "rdue_conforme": True
                    }
                    
                    try:
                        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                        
                        if response.status_code in [200, 201, 204]:
                            cursor.execute("UPDATE rapports_locaux SET statut='Envoyé' WHERE id=?", (row_id,))
                            nb_succes += 1
                        else:
                            st.sidebar.error(f"⚠️ Erreur HTTP {response.status_code} : {response.text}")
                            break
                            
                    except requests.exceptions.ConnectionError:
                        st.sidebar.warning("📡 Connexion réseau indisponible.")
                        break
                    except requests.exceptions.Timeout:
                        st.sidebar.warning("⏱️ Délai d'attente dépassé.")
                        break
                
                conn.commit()
                conn.close()
                
                if nb_succes > 0:
                    st.sidebar.success(f"✅ {nb_succes} rapport(s) synchronisé(s) !")
                    st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"❌ Erreur de transmission : {e}")
        else:
            st.sidebar.info("Aucun rapport en attente.")

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

# --- 3. ACCÈS AUX MODULES (UNE FOIS DÉVERROUILLÉ) ---
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
    ],
    key="sb_choix_module_principal"
)

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
