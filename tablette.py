import base64
import json
import os
import sqlite3
import time
from datetime import datetime
import numpy as np
import pandas as pd
import requests
import streamlit as st
import urllib.parse

# --- IMPORTATION DU MODULE PDC ET CROQUIS ---
import pdc
from generate_croquis import generer_croquis_parcelle

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Leyla Agri - Tablette Terrain", page_icon="📱", layout="centered"
)

# --- DECLENCHEMENT VISUEL DES BALLONS ---
if st.session_state.get("afficher_ballons_flag", False):
  st.balloons()
  st.session_state["afficher_ballons_flag"] = False

# --- INITIALISATION DES DONNÉES DU PDC EN SESSION (15 ÉTAPES) ---
if "pdc_data" not in st.session_state:
  st.session_state.pdc_data = {
      "Étape 1/15 : Localisation & Identification de la Section": {},
      "Étape 2/15 : Données Socio-démographiques & Identification Producteur": {},
      "Étape 3/15 : Données de la Parcelle & Exploitation": {},
      "Étape 4/15 : Données sur les Cultures, Équipements & Agroforesterie": {
          "🌾 Données sur les cultures et parcelles": {},
          "🛠️ Matériel agricole et équipements": {},
          "🌳 Diagnostic des arbres d'ombrage et associés": {},
      },
      "Étape 5/15 : Densité et Rendement (Fiche 3)": {},
      "Étape 6/15 : État Sanitaire, Sol, Récolte & Engrais (Fiche 3)": {},
      "Étape 7/15 : Données Socio-économiques (Fiche 4)": {
          "🏦 Compte d'épargne et Financement": {},
          "📦 Production de cacao des trois (3) dernières années": {},
          "💰 Sources de revenus autres que le cacao": {},
          "🛒 Dépenses courantes du foyer": {},
          "👥 Coût et gestion de la main d'œuvre": {},
      },
      "Étape 8/15 : Plan d'Action & Programme Annuel (Fiche 7)": {
          "📊 Grille de décision": {},
          "⚠️ Tableau d'analyse des problèmes": {},
          "📅 Plan d'Action Quinquennal (Sur 5 ans)": {},
          "🗓️ Programme Annuel d'Activités (Fiche 7)": {},
      },
      "Étape 9/15 : Détermination des moyens et des coûts (Fiche 8)": {
          "📄 Bilan global des données collectées": {}
      },
      "Étape 10/15 : Bilan & Diagnostic Qualité du PDC": {
          "🔍 Diagnostic Qualité du PDC": {},
          "📌 Récapitulatif Synthétique": {},
      },
      "Étape 11/15 : Bilan Technique Approfondi": {},
      "Étape 12/15 : Description de l'Exploitation & Croquis Parcelle": {
          "💳 Situation de l'épargne": {},
          "👥 Situation de la main-d'œuvre": {},
          "🏡 Description & Caractéristiques de l'Exploitation": {},
          "📐 Croquis & Géolocalisation": {},
      },
      "Étape 13/15 : Cultures, Agroforesterie & Matériel Agricole": {
          "🌾 Diversification & Cultures de l'Exploitation": {},
          "🌳 Inventaire des Arbres hors Cacaoyer (Normes CCC)": {},
          "🚜 Matériel Agricole & Équipements": {},
      },
      "Étape 14/15 : Planification Stratégique (5 Ans) & Programme Annuel d'Action": (
          {
              "📈 Planification Stratégique sur les Cinq (5) Prochaines Années": {},
              "🗓️ Programme Annuel d'Action (Détail Année 1)": {},
              "⚠️ Facteurs de Succès et d'Échec": {},
          }
      ),
      "Étape 15/15 : Bilan Synthétique, Faisabilité & Validation du PDC": {
          "📋 Synthèse Générale de l'Exploitation": {},
          "📊 Évaluation de la Faisabilité & Diagnostic de Réussite": {},
          "💡 Recommandations du Conseiller Agricole": {},
      },
  }


# --- FONCTIONS UTILITAIRES JSON ET CONVERSION AVANCÉE ---
class NpEncoder(json.JSONEncoder):

  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    if isinstance(obj, np.floating):
      return float(obj)
    if isinstance(obj, np.ndarray):
      return obj.tolist()
    if pd.isna(obj):
      return None
    if isinstance(obj, bytes):
      return base64.b64encode(obj).decode("utf-8")
    if isinstance(obj, (datetime, pd.Timestamp)):
      return obj.isoformat()
    return super(NpEncoder, self).default(obj)


def nettoyer_pour_json(d):
  if isinstance(d, dict):
    return {
        str(k): nettoyer_pour_json(v)
        for k, v in d.items()
        if not str(k).startswith("FormSubmitter")
        and not str(k).startswith("btn_")
        and not str(k).startswith("sb_")
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
    return f"data:image/png;base64,{base64.b64encode(d).decode('utf-8')}"
  elif pd.isna(d):
    return None
  else:
    return d


# --- UPLOAD SUPABASE STORAGE ---
def uploader_pdf_supabase(pdf_bytes, nom_fichier):
  try:
    url_supabase = st.secrets["supabase"]["url"]
    key_supabase = st.secrets["supabase"]["key"]
    bucket_name = "pdc-rapports"

    storage_url = f"{url_supabase}/storage/v1/object/{bucket_name}/{nom_fichier}"

    headers = {
        "apikey": key_supabase,
        "Authorization": f"Bearer {key_supabase}",
        "Content-Type": "application/pdf",
        "x-upsert": "true",
    }

    response = requests.post(
        storage_url, data=pdf_bytes, headers=headers, timeout=20
    )

    if response.status_code in [200, 201]:
      return (
          f"{url_supabase}/storage/v1/object/public/{bucket_name}/{nom_fichier}"
      )
    else:
      st.sidebar.error(
          f"⚠️ Erreur Storage Supabase ({response.status_code}) :"
          f" {response.text}"
      )
      return None

  except Exception as e:
    st.sidebar.error(f"❌ Erreur lors de l'envoi du PDF vers Supabase : {e}")
    return None


# --- VUE IMPRESSION ---
def afficher_vue_impression_dynamique():
  st.markdown(
      """
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
    """,
      unsafe_allow_html=True,
  )

  st.title("📋 Plan de Développement de Conseil (PDC) - Rapport Complet")
  st.caption("Aperçu global récapitulatif pour impression PDF")
  st.divider()

  reponses = st.session_state.get("reponses_pdc", {})

  if not reponses:
    cles_a_ignorer = [
        "appareil_deverrouille",
        "identifie",
        "code_agent_connecte",
        "pdf_bytes_pdc",
        "etape_pdc",
        "pdc_data",
        "cooperative",
        "section",
        "technicien",
    ]
    reponses = {
        k: v
        for k, v in st.session_state.items()
        if not str(k).startswith("btn_")
        and not str(k).startswith("sb_")
        and not str(k).startswith("FormSubmitter")
        and k not in cles_a_ignorer
    }

  if reponses:
    st.subheader("📌 Données collectées durant la session")
    for cle, valeur in reponses.items():
      nom_champ = str(cle).replace("_", " ").capitalize()

      if isinstance(valeur, dict):
        st.markdown(f"### {nom_champ}")
        for sub_k, sub_v in valeur.items():
          st.markdown(f"- **{sub_k} :** {sub_v}")
      elif isinstance(valeur, pd.DataFrame):
        if not valeur.empty:
          st.markdown(f"### {nom_champ}")
          st.dataframe(valeur, use_container_width=True)
      elif isinstance(valeur, list):
        if len(valeur) > 0:
          st.markdown(f"### {nom_champ}")
          for idx, item in enumerate(valeur, 1):
            if isinstance(item, dict):
              st.markdown(f"**Élément {idx} :**")
              for sub_k, sub_v in item.items():
                st.markdown(f"- *{sub_k}* : {sub_v}")
            else:
              st.markdown(f"- {item}")
      else:
        if valeur != "" and valeur is not None:
          st.markdown(f"**{nom_champ} :** {valeur}")
      st.divider()
  else:
    st.warning("⚠️ Aucune donnée n'a été détectée dans la session active.")


# --- SÉCURITÉ ET SESSION ---
if "appareil_deverrouille" not in st.session_state:
  st.session_state.appareil_deverrouille = False

if "identifie" not in st.session_state:
  st.session_state.identifie = False

if "pdf_bytes_pdc" not in st.session_state:
  st.session_state["pdf_bytes_pdc"] = None


# --- INITIALISATION SQLITE LOCALE ---
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

# --- ENTÊTE PRINCIPAL ---
st.title("📱 Leyla Agri - Mode Terrain")
st.markdown("---")

# --- 1. PROFIL D'IDENTIFICATION ---
if not st.session_state.get("identifie", False):
  st.subheader("🔒 Profil d'identification du Technicien")
  with st.form("form_identification"):
    cooperative = st.text_input(
        "Identification de la Coopérative", placeholder="Ex: SCACO, SOCABA..."
    )
    section = st.text_input(
        "Identification de la Section", placeholder="Ex: Section Divo-Sud..."
    )
    technicien = st.text_input(
        "Nom, Prénom & Identifiant", placeholder="Ex: Agent Kouamé - ID 0001"
    )

    btn_valider_profil = st.form_submit_button(
        "Enregistrer et Verrouiller le Profil"
    )
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
  st.write(f"**Coop :** {st.session_state.get('cooperative', 'N/A')}")
  st.write(f"**Section :** {st.session_state.get('section', 'N/A')}")
  st.write(f"**Agent :** {st.session_state.get('technicien', 'N/A')}")

  if st.button("🔓 Modifier le profil", key="sb_btn_modifier_profil"):
    st.session_state.identifie = False
    st.rerun()

  st.markdown("---")
  if st.session_state.get("appareil_deverrouille", False):
    if st.button(
        "🔒 Verrouiller la tablette",
        use_container_width=True,
        key="sb_btn_verrouiller",
    ):
      st.session_state.appareil_deverrouille = False
      st.rerun()

  st.markdown("---")
  st.markdown("## 🖨️ Mode Impression")
  mode_impression = st.checkbox(
      "🖨️ Activer le Mode Vue Impression", key="sb_mode_impression"
  )

  st.markdown("---")
  st.markdown("## 📄 Actions PDC")

  if st.button(
      "🎓 Générer le PDF Final",
      key="sb_btn_generer_pdf",
      type="primary",
      use_container_width=True,
  ):
    reponses_completes = {}
    if isinstance(st.session_state.get("pdc_data"), dict):
      reponses_completes["pdc_data_15_etapes"] = st.session_state.pdc_data

    if isinstance(st.session_state.get("reponses_pdc"), dict):
      reponses_completes.update(st.session_state.reponses_pdc)

    cles_a_ignorer = [
        "appareil_deverrouille",
        "identifie",
        "code_agent_connecte",
        "pdf_bytes_pdc",
        "etape_pdc",
        "reponses_pdc",
    ]
    for k, v in st.session_state.items():
      if (
          not str(k).startswith("btn_")
          and not str(k).startswith("sb_")
          and not str(k).startswith("FormSubmitter")
          and k not in cles_a_ignorer
      ):
        reponses_completes[k] = v

    page_2_data = st.session_state.get("pdc_data", {}).get(
        "Étape 2/15 : Données Socio-démographiques & Identification Producteur",
        {},
    )
    nom_prod = (
        page_2_data.get("nom_prenoms_producteur")
        or st.session_state.get("nom_producteur")
        or "Inconnu"
    )
    code_prod = (
        page_2_data.get("code_national_producteur")
        or st.session_state.get("code_producteur")
        or "CCC-001"
    )
    section_zone = st.session_state.get("section", "Section Divo-Sud")
    score_final = st.session_state.get("score_pdc", 0)

    payload_pdf = {
        "nom_producteur": nom_prod,
        "code_ccc": code_prod,
        "zone": section_zone,
        "score_faisabilite": score_final,
        "reponses": reponses_completes,
        "mode_impression": mode_impression,
    }

    try:
      pdf_data = pdc.generer_pdf_pdc_fonction(payload_pdf)
      st.session_state["pdf_bytes_pdc"] = pdf_data
      st.session_state["afficher_ballons_flag"] = True
      st.success("✅ PDF complet généré avec succès !")
      st.rerun()
    except Exception as e:
      st.error(f"❌ Erreur PDF : {e}")

  if st.session_state.get("pdf_bytes_pdc") is not None:
    code_p = str(st.session_state.get("code_producteur", "CCC-001")).replace(
        " ", "_"
    )
    nom_p = str(st.session_state.get("nom_producteur", "Inconnu")).replace(
        " ", "_"
    )
    st.download_button(
        label="📥 Télécharger le PDF",
        data=st.session_state["pdf_bytes_pdc"],
        file_name=f"PDC_{code_p}_{nom_p}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="sb_btn_download_pdf",
    )

  st.markdown("---")
  st.markdown("## 💾 Sauvegarde Terrain")
  module_a_enregistrer = st.selectbox(
      "Module à enregistrer :", ["PDC_INTEGRAL"], key="sb_select_module"
  )

  if st.button(
      "💾 Enregistrer dans la tablette",
      type="secondary",
      key="sb_btn_sauvegarder",
      use_container_width=True,
  ):
    coop = st.session_state.get("cooperative", "SCACO")
    sec = st.session_state.get("section", "Section Divo-Sud")
    tech = st.session_state.get("technicien", "Agent Kouamé")
    reponses = st.session_state.get("reponses_pdc", {})
    page_2_data = st.session_state.get("pdc_data", {}).get(
        "Étape 2/15 : Données Socio-démographiques & Identification Producteur",
        {},
    )

    nom_prod = (
        page_2_data.get("nom_prenoms_producteur")
        or st.session_state.get("nom_producteur")
        or "Producteur Inconnu"
    )
    code_prod = (
        page_2_data.get("code_national_producteur")
        or st.session_state.get("code_producteur")
        or "CCC-000"
    )
    superficie = st.session_state.get("superficie", 0.0)
    age_p = str(st.session_state.get("age_parcelle", "0"))

    session_complete = {
        "metadata_agent": {
            "cooperative": coop,
            "section": sec,
            "technicien": tech,
            "date_capture": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "pdc_data_15_etapes": st.session_state.get("pdc_data", {}),
        "reponses_pdc": reponses if isinstance(reponses, dict) else {},
    }

    donnees_json_str = json.dumps(
        nettoyer_pour_json(session_complete), cls=NpEncoder, ensure_ascii=False
    )
    pdf_blob = st.session_state.get("pdf_bytes_pdc")
    date_saisie = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
      conn = sqlite3.connect("leyla_terrain.db")
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO rapports_locaux (
                    cooperative, section, technicien, producteur, code_producteur, 
                    superficie, age_parcelle, module_execute, donnees_module, pdf_blob, date_saisie, statut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'En attente')
            """,
          (
              coop,
              sec,
              tech,
              nom_prod,
              code_prod,
              float(superficie) if superficie else 0.0,
              age_p,
              module_a_enregistrer,
              donnees_json_str,
              pdf_blob,
              date_saisie,
          ),
      )
      conn.commit()
      conn.close()
      st.session_state["afficher_ballons_flag"] = True
      st.success(f"💾 Fiche enregistrée avec succès pour **{nom_prod}**")
      time.sleep(0.5)
      st.rerun()
    except Exception as e:
      st.error(f"❌ Erreur SQLite : {e}")

# --- 2. ACCÈS SÉCURISÉ TECHNICIEN ---
MOT_DE_PASSE_VALIDE = "leyla2.6"

if not st.session_state.get("appareil_deverrouille", False):
  st.header("🔒 Accès Sécurisé Technicien")
  with st.form("form_login_technicien"):
    code_agent = st.text_input(
        "Code Agent / Technicien", key="input_code_agent"
    )
    mot_de_passe = st.text_input(
        "Mot de passe *", type="password", key="input_mdp_technicien"
    )
    btn_valider = st.form_submit_button(
        "🔓 Déverrouiller la tablette", type="primary", use_container_width=True
    )

  if btn_valider:
    if mot_de_passe == MOT_DE_PASSE_VALIDE:
      st.session_state.appareil_deverrouille = True
      st.session_state.code_agent_connecte = code_agent
      st.success(f"✅ Déverrouillage réussi !")
      st.rerun()
    else:
      st.error("❌ Mot de passe incorrect.")
  st.stop()

# --- 3. EXÉCUTION DU MODULE UNIQUE PDC / IMPRESSION ---
if st.session_state.get("sb_mode_impression", False):
  afficher_vue_impression_dynamique()
else:
  st.header("🛠️ Module de Saisie - PDC")
  st.caption(
      "👤 Session Agent :"
      f" **{st.session_state.get('code_agent_connecte', 'Inconnu')}**"
  )
  pdc.afficher()
