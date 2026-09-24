import streamlit as st
import sqlite3
import os
import json
import time
from datetime import datetime
import requests
import numpy as np
import pandas as pd
import urllib.parse  # Importé pour le traitement des URLs et mailto

# --- IMPORTATION DES MODULES ---
import diagnostique
import geolocalisation
import estimation_de_rendement
import pdc
from generate_croquis import generer_croquis_parcelle

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Leyla Agri - Tablette Terrain", page_icon="📱", layout="centered")

# --- ANNUAIRE DES DESTINATAIRES (COOPÉRATIVES ET CABINETS) ---
ANNUAIRE_DESTINATAIRES = {
    "Coopératives": {
        "SOCOAMO": "directionsocoamo@gmail.com",
        "COOP-CA menecentre": "directionmenecentre@gmail.com",
        "SOCAGNIPI": "directionsocagnipi",
        "ROBERTPORTE": "directionrobertporte",
        "NECAB": "directionnecab@gmail.com" 
    },
    "Cabinets de Conseil": {
        "Cabinet AgriForce": "agriforce@gmail.com",
        "Cabinet Audit & Agro": "direction@audit-agro.ci",
        "Cabinet Conseils & Developpement": "contact@ccd.ci"
    }
}

# --- INITIALISATION DES DONNÉES DU PDC EN SESSION (15 ÉTAPES) ---
if "pdc_data" not in st.session_state:
    st.session_state.pdc_data = {
        "Étape 1/15 : Localisation & Identification de la Section": {},
        "Étape 2/15 : Données de la Parcelle": {},
        "Étape 3/15 : Données Socio-démographiques (Fiche 1)": {},
        "Étape 4/15 : Données sur les Cultures, Équipements & Agroforesterie": {
            "🌾 Données sur les cultures et parcelles": {},
            "🛠️ Matériel agricole et équipements": {},
            "🌳 Diagnostic des arbres d'ombrage et associés": {}
        },
        "Étape 5/15 : Densité et Rendement (Fiche 3)": {},
        "Étape 6/15 : État Sanitaire, Sol, Récolte & Engrais (Fiche 3)": {},
        "Étape 7/15 : Données Socio-économiques (Fiche 4)": {
            "🏦 Compte d'épargne et Financement": {},
            "📦 Production de cacao des trois (3) dernières années": {},
            "💰 Sources de revenus autres que le cacao": {},
            "🛒 Dépenses courantes du foyer": {},
            "👥 Coût et gestion de la main d'œuvre": {}
        },
        "Étape 8/15 : Plan d'Action & Programme Annuel (Fiche 7)": {
            "📊 Grille de décision": {},
            "⚠️ Tableau d'analyse des problèmes": {},
            "📅 Plan d'Action Quinquennal (Sur 5 ans)": {},
            "🗓️ Programme Annuel d'Activités (Fiche 7)": {}
        },
        "Étape 9/15 : Détermination des moyens et des coûts (Fiche 8)": {
            "📄 Bilan global des données collectées": {}
        },
        "Étape 10/15 : Bilan & Diagnostic Qualité du PDC": {
            "🔍 Diagnostic Qualité du PDC": {},
            "📌 Récapitulatif Synthétique": {}
        },
        "Étape 11/15 : Identification du Producteur (Situation de Référence)": {},
        "Étape 12/15 : Informations Ménage & Description de l'Exploitation": {
            "💳 Situation de l'épargne": {},
            "👥 Situation de la main-d'œuvre": {},
            "🏡 Description & Caractéristiques de l'Exploitation": {}
        },
        "Étape 13/15 : Cultures, Agroforesterie & Matériel Agricole": {
            "🌾 Diversification & Cultures de l'Exploitation": {},
            "🌳 Inventaire des Arbres hors Cacaoyer (Normes CCC)": {},
            "🚜 Matériel Agricole & Équipements": {}
        },
        "Étape 14/15 : Planification Stratégique (5 Ans) & Programme Annuel d'Action": {
            "📈 Planification Stratégique sur les Cinq (5) Prochaines Années": {},
            "🗓️ Programme Annuel d'Action (Détail Année 1)": {},
            "⚠️ Facteurs de Succès et d'Échec": {}
        },
        "Étape 15/15 : Bilan Synthétique, Faisabilité & Validation du PDC": {
            "📋 Synthèse Générale de l'Exploitation": {},
            "📊 Évaluation de la Faisabilité & Diagnostic de Réussite": {},
            "💡 Recommandations du Conseiller Agricole": {}
        }
    }

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
    elif isinstance(d, pd.DataFrame):
        return d.to_dict(orient="records")
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
        query = "SELECT * FROM rapports_locaux WHERE module_execute = ?"
        df = pd.read_sql_query(query, conn, params=(nom_module,))
        conn.close()
        return df
    except Exception:
        try:
            conn = sqlite3.connect("leyla_terrain.db")
            query = "SELECT * FROM rapports_locaux WHERE module_type = ?"
            df = pd.read_sql_query(query, conn, params=(nom_module,))
            conn.close()
            return df
        except Exception:
            return pd.DataFrame()

# --- FONCTION D'UPLOAD DU PDF VERS SUPABASE STORAGE ---
def uploader_pdf_supabase(pdf_bytes, nom_fichier):
    """Téléverse le fichier PDF vers le bucket Supabase Storage et retourne son URL publique."""
    try:
        url_supabase = st.secrets["supabase"]["url"]
        key_supabase = st.secrets["supabase"]["key"]
        bucket_name = "pdc-rapports"
        
        storage_url = f"{url_supabase}/storage/v1/object/{bucket_name}/{nom_fichier}"
        
        headers = {
            "apikey": key_supabase,
            "Authorization": f"Bearer {key_supabase}",
            "Content-Type": "application/pdf",
            "x-upsert": "true"
        }
        
        response = requests.post(storage_url, data=pdf_bytes, headers=headers, timeout=20)
        
        if response.status_code in [200, 201]:
            pdf_public_url = f"{url_supabase}/storage/v1/object/public/{bucket_name}/{nom_fichier}"
            return pdf_public_url
        else:
            st.sidebar.error(f"⚠️ Erreur Storage Supabase ({response.status_code}) : {response.text}")
            return None
            
    except Exception as e:
        st.sidebar.error(f"❌ Erreur lors de l'envoi du PDF vers Supabase : {e}")
        return None

# --- FONCTION D'AFFICHAGE POUR IMPRESSION (MODE GLOBAL) ---
def afficher_vue_impression_dynamique():
    st.markdown("""
        <style>
        @media print {
            [data-testid="stSidebar"], .stButton, header, footer { 
                display: none !important; 
            }
            .main .block-container { 
                max-width: 100% !important; 
                padding: 0 !important; 
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📋 Plan de Développement de Conseil (PDC) - Rapport Complet")
    st.caption("Aperçu global récapitulatif pour impression PDF")
    st.divider()

    reponses = st.session_state.get("reponses_pdc", {})

    if not reponses:
        cles_a_ignorer = [
            "appareil_deverrouille", "identifie", "code_agent_connecte", 
            "pdf_bytes_pdc", "etape_pdc", "pdc_data", "cooperative", "section", "technicien"
        ]
        reponses = {
            k: v for k, v in st.session_state.items() 
            if not str(k).startswith("btn_") and not str(k).startswith("sb_") 
            and not str(k).startswith("FormSubmitter") and k not in cles_a_ignorer
        }

    if reponses:
        st.subheader("📌 Données collectées durant la session")
        for cle, valeur in reponses.items():
            nom_champ = str(cle).replace("_", " ").capitalize()
            
            if isinstance(valeur, dict):
                st.markdown(f"### {nom_champ}")
                for sub_k, sub_v in valeur.items():
                    st.write(f"- **{sub_k} :** {sub_v}")
            elif isinstance(valeur, pd.DataFrame):
                if not valeur.empty:
                    st.markdown(f"### {nom_champ}")
                    st.dataframe(valeur, use_container_width=True)
            elif isinstance(valeur, list):
                if len(valeur) > 0:
                    st.markdown(f"### {nom_champ}")
                    if isinstance(valeur[0], dict):
                        st.table(valeur)
                    else:
                        for item in valeur:
                            st.write(f"- {item}")
            else:
                if valeur != "" and valeur is not None:
                    st.write(f"**{nom_champ} :** {valeur}")
            st.divider()
    else:
        st.warning("⚠️ Aucune donnée n'a été détectée dans la session active. Assure-toi d'avoir validé les formulaires des étapes.")

# --- INITIALISATION DE LA SESSION ET SÉCURITÉ ---
if "appareil_deverrouille" not in st.session_state:
    st.session_state.appareil_deverrouille = False

if "identifie" not in st.session_state:
    st.session_state.identifie = False

if "pdf_bytes_pdc" not in st.session_state:
    st.session_state["pdf_bytes_pdc"] = None

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
            module_execute TEXT,
            donnees_module TEXT,
            pdf_blob BLOB,
            date_saisie TEXT,
            statut TEXT DEFAULT 'En attente'
        )
    """)
    try:
        cursor.execute("ALTER TABLE rapports_locaux ADD COLUMN module_execute TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE rapports_locaux ADD COLUMN pdf_blob BLOB")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()

init_local_db()



import streamlit as st
import sqlite3
import os
import json
import time
from datetime import datetime
import requests
import numpy as np
import pandas as pd
import urllib.parse

# --- TITRE PRINCIPAL ---
st.title("📱 Leyla Agri - Mode Terrain")
st.markdown("---")

# --- 1. PROFIL D'IDENTIFICATION ---
if not st.session_state.get("identifie", False):
    st.subheader("🔒 Profil d'identification du Technicien")
    with st.form("form_identification"):
        cooperative = st.text_input(
            "Identification de la Coopérative", 
            value="", 
            placeholder="Ex: SCACO, SOCABA, COOP-CA..."
        )
        section = st.text_input(
            "Identification de la Section", 
            value="", 
            placeholder="Ex: Section Divo-Sud, Lakota, Soubré..."
        )
        technicien = st.text_input(
            "Nom, Prénom & Identifiant", 
            value="", 
            placeholder="Ex: Agent Kouamé Konan - ID 0001"
        )
        
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
    
    # Interrompt immédiatement l'exécution pour éviter le double rendu du sidebar
    st.stop()


# --- BARRE LATÉRALE (EXÉCUTÉE UNIQUEMENT SI IDENTIFIÉ) ---
with st.sidebar:
    st.markdown("### 👤 Session Active")
    st.write(f"**Coop :** {st.session_state.get('cooperative', 'N/A')}")
    st.write(f"**Section :** {st.session_state.get('section', 'N/A')}")
    st.write(f"**Agent :** {st.session_state.get('technicien', 'N/A')}")
    
    if st.button("🔓 Modifier le profil", key="sb_btn_modifier_profil"):
        st.session_state.identifie = False
        st.rerun()

    st.markdown("---")
    if st.session_state.get("appareil_deverrouille", False):
        if st.button("🔒 Verrouiller la tablette", use_container_width=True, key="sb_btn_verrouiller"):
            st.session_state.appareil_deverrouille = False
            st.rerun()

    st.markdown("---")
    st.markdown("## 🖨️ Mode Impression")
    mode_impression = st.checkbox("🖨️ Activer le Mode Vue Impression", key="sb_mode_impression")

    st.markdown("---")
    st.markdown("## 📄 Actions PDC")
    
    # GÉNÉRATION DU PDF FINAL
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

        rapports_sqlite = []
        try:
            conn = sqlite3.connect("leyla_terrain.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT module_execute, donnees_module, date_saisie 
                FROM rapports_locaux 
                ORDER BY id DESC
            """)
            lignes = cursor.fetchall()
            conn.close()
            
            for mod_exe, d_json, d_saisie in lignes:
                try:
                    data_parsed = json.loads(d_json) if isinstance(d_json, str) else d_json
                except Exception:
                    data_parsed = str(d_json)
                rapports_sqlite.append({
                    "module": mod_exe,
                    "date": d_saisie,
                    "details": data_parsed
                })
        except Exception as e:
            st.warning(f"Note SQLite : {e}")

        payload_pdf = {
            "nom_producteur": nom_prod,
            "code_ccc": code_prod,
            "zone": section_zone,
            "score_faisabilite": score_final,
            "reponses": reponses_completes,
            "historique_modules": rapports_sqlite
        }
        
        try:
            pdf_data = pdc.generer_pdf_pdc_fonction(payload_pdf)
            st.session_state["pdf_bytes_pdc"] = pdf_data
            st.success("✅ PDF complet généré !")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erreur PDF : {e}")

    # TÉLÉCHARGER LE PDF
    if st.session_state.get("pdf_bytes_pdc") is not None:
        code_p = str(st.session_state.get("code_producteur", "CCC-001")).replace(" ", "_")
        nom_p = str(st.session_state.get("nom_producteur", "Inconnu")).replace(" ", "_")
        
        st.download_button(
            label="📥 Télécharger le PDF",
            data=st.session_state["pdf_bytes_pdc"],
            file_name=f"PDC_{code_p}_{nom_p}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="sb_btn_download_pdf"
        )

        # --- MODULE INTEGRÉ : TRANSMISSION VIA GMAIL ---
        st.markdown("---")
        st.markdown("### ✉️ Partage par E-mail")
        
        type_dest = st.radio(
            "Type de structure :", 
            ["Coopératives", "Cabinets de Conseil"], 
            key="sb_radio_type_dest"
        )
        
        entreprises_dispos = list(ANNUAIRE_DESTINATAIRES[type_dest].keys())
        entite_choisie = st.selectbox(
            "Sélectionner la structure :", 
            entreprises_dispos, 
            key="sb_select_entite"
        )
        
        email_cible = ANNUAIRE_DESTINATAIRES[type_dest][entite_choisie]
        
        nom_prod_mail = st.session_state.get("nom_producteur") or st.session_state.get("producteur") or "Inconnu"
        code_prod_mail = st.session_state.get("code_producteur") or st.session_state.get("code_ccc") or "CCC-001"
        
        sujet_mail = urllib.parse.quote(f"Rapport PDC - {nom_prod_mail} ({code_prod_mail}) - {entite_choisie}")
        corps_mail = urllib.parse.quote(
            f"Bonjour,\n\n"
            f"Veuillez trouver ci-joint le rapport Plan de Développement de Conseil (PDC) pour le producteur {nom_prod_mail} (Code: {code_prod_mail}).\n\n"
            f"Ce document a été généré via l'application Leyla Agri (Mode Terrain).\n\n"
            f"N'oubliez pas d'attacher le fichier PDF téléchargé (PDC_{code_p}_{nom_p}.pdf) avant de cliquer sur Envoyer.\n\n"
            f"Cordialement,\n"
            f"{st.session_state.get('technicien', 'L\'Agent de Terrain')}"
        )
        
        lien_mailto = f"mailto:{email_cible}?subject={sujet_mail}&body={corps_mail}"
        
        st.caption(f"📩 Destinataire : `{email_cible}`")
        st.link_button(
            label=f"📧 Ouvrir Gmail pour {entite_choisie}",
            url=lien_mailto,
            use_container_width=True
        )

    # CENTRE D'ENREGISTREMENT MULTI-MODULES (SQLITE)
    st.markdown("---")
    st.markdown("## 💾 Sauvegarde Terrain")
    
    module_a_enregistrer = st.selectbox(
        "Module à enregistrer :",
        [
            "PDC",
            "Diagnostic Phytosanitaire",
            "Géo-intelligence & RDUE",
            "Estimation de Rendement"
        ],
        key="sb_select_module_enregistrement"
    )

    if st.button("💾 Enregistrer dans la tablette", type="secondary", key="sb_btn_sauvegarder_sqlite", use_container_width=True):
        coop = st.session_state.get("cooperative", "SCACO")
        sec = st.session_state.get("section", "Section Divo-Sud")
        tech = st.session_state.get("technicien", "Agent Kouamé")
        
        reponses = st.session_state.get("reponses_pdc", {})
        
        nom_prod = (
            reponses.get("nom_prenoms_producteur") 
            or st.session_state.get("nom_prenoms_producteur")
            or reponses.get("nom_membre")
            or st.session_state.get("nom_producteur")
            or "Producteur Inconnu"
        )
        
        code_prod = (
            reponses.get("code_national_producteur") 
            or st.session_state.get("code_national_producteur")
            or reponses.get("code_groupe")
            or st.session_state.get("code_producteur")
            or "CCC-000"
        )
        
        superficie = st.session_state.get("superficie") or st.session_state.get("superficie_ha") or 0.0
        age_p = str(st.session_state.get("age_parcelle") or st.session_state.get("age_cacaoyere") or "0")

        st.session_state["nom_producteur"] = nom_prod
        st.session_state["code_producteur"] = code_prod

        session_complete = {}
        if isinstance(reponses, dict):
            session_complete.update(reponses)
            
        cles_a_ignorer = ["appareil_deverrouille", "identifie", "code_agent_connecte", "pdf_bytes_pdc"]
        for k, v in st.session_state.items():
            if not str(k).startswith("btn_") and not str(k).startswith("sb_") and not str(k).startswith("FormSubmitter") and k not in cles_a_ignorer:
                if isinstance(v, (str, int, float, bool, list, dict)):
                    session_complete[k] = v

        # Génération auto du PDF s'il manque
        if st.session_state.get("pdf_bytes_pdc") is None:
            try:
                payload_auto_pdf = {
                    "nom_producteur": nom_prod,
                    "code_ccc": code_prod,
                    "zone": sec,
                    "score_faisabilite": st.session_state.get("score_pdc", 0),
                    "reponses": session_complete,
                    "historique_modules": []
                }
                st.session_state["pdf_bytes_pdc"] = pdc.generer_pdf_pdc_fonction(payload_auto_pdf)
            except Exception:
                pass

        donnees_json_str = json.dumps(nettoyer_pour_json(session_complete), cls=NpEncoder, ensure_ascii=False)
        pdf_blob = st.session_state.get("pdf_bytes_pdc")
        date_saisie = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect("leyla_terrain.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO rapports_locaux (
                    cooperative, section, technicien, producteur, code_producteur, 
                    superficie, age_parcelle, module_execute, donnees_module, pdf_blob, date_saisie, statut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'En attente')
            """, (coop, sec, tech, nom_prod, code_prod, float(superficie), age_p, module_a_enregistrer, donnees_json_str, pdf_blob, date_saisie))
            
            conn.commit()
            conn.close()

            st.success(f"💾 Fiche enregistrée pour [{module_a_enregistrer}] : **{nom_prod}** ({code_prod})")
            st.balloons()
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur lors de la sauvegarde SQLite : {e}")

    # SYNCHRONISATION SUPABASE
    st.markdown("---")
    st.subheader("🔄 Synchronisation Supabase")

    try:
        conn = sqlite3.connect("leyla_terrain.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rapports_locaux WHERE statut='En attente'")
        nombre_attente = cursor.fetchone()[0]
        conn.close()
    except Exception:
        nombre_attente = 0

    st.write(f"📦 Rapports en attente : **{nombre_attente}**")

    if st.button("🚀 SYNCHRONISER MAINTENANT", use_container_width=True, key="sb_btn_synchro_supabase"):
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
                           superficie, age_parcelle, module_execute, donnees_module, pdf_blob 
                    FROM rapports_locaux 
                    WHERE statut='En attente'
                """)
                lignes = cursor.fetchall()
                
                nb_succes = 0
                
                for ligne in lignes:
                    row_id, coop, sec, tech, prod, code_p, sup, age_p, mod_t, donnees_m, pdf_b = ligne
                    
                    try:
                        age_int = int(''.join(filter(str.isdigit, str(age_p))))
                    except ValueError:
                        age_int = 0

                    if isinstance(donnees_m, (dict, list)):
                        donnees_str = json.dumps(nettoyer_pour_json(donnees_m), cls=NpEncoder, ensure_ascii=False)
                    else:
                        donnees_str = str(donnees_m) if donnees_m else "{}"

                    url_pdf_public = None
                    if pdf_b is not None:
                        code_clean = str(code_p).replace(" ", "_").replace("/", "_")
                        nom_f = f"PDC_{code_clean}_{row_id}.pdf"
                        url_pdf_public = uploader_pdf_supabase(pdf_b, nom_f)

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
                        "url_pdf_pdc": url_pdf_public,
                        "rdue_conforme": True
                    }
                    
                    try:
                        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
                        
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

if not st.session_state.get("appareil_deverrouille", False):
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

# --- 3. ACCÈS AUX MODULES OU MODE IMPRESSION ---
if st.session_state.get("sb_mode_impression", False):
    afficher_vue_impression_dynamique()
else:
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

    # APPEL DES MODULES
    if choix_module == "1. Diagnostic Phytosanitaire":
        diagnostique.afficher()

    elif choix_module == "2. Géo-intelligence & RDUE":
        geolocalisation.afficher()

    elif choix_module == "3. Estimation de Rendement":
        estimation_de_rendement.afficher()

    elif choix_module == "4. PDC":
        pdc.afficher()
