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


# --- FONCTIONS UTILITAIRES JSON ET CONVERSION ---
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
    return super(NpEncoder, self).default(obj)


def nettoyer_pour_json(d):
  """Nettoie et convertit dynamiquement toutes les données pour la sérialisation JSON sans pertes."""
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
    return None
  else:
    return str(d) if d is not None else None


def uploader_pdf_supabase(pdf_bytes, nom_fichier):
  """Téléverse le PDF complet vers Supabase Storage."""
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
    return None
  except Exception as e:
    st.sidebar.error(f"❌ Erreur Storage Supabase : {e}")
    return None


# --- INITIALISATION BASE SQLITE LOCALE ---
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
  conn.commit()
  conn.close()


init_local_db()

# --- SÉCURITÉ ET SESSION ---
if "appareil_deverrouille" not in st.session_state:
  st.session_state.appareil_deverrouille = False
if "identifie" not in st.session_state:
  st.session_state.identifie = False
if "pdf_bytes_pdc" not in st.session_state:
  st.session_state["pdf_bytes_pdc"] = None

# --- ENTÊTE & IDENTIFICATION ---
st.title("📱 Leyla Agri - Mode Terrain")
st.markdown("---")

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
        "Nom & Identifiant Agent", placeholder="Ex: Agent Kouamé - ID 0001"
    )
    if st.form_submit_button("Enregistrer et Verrouiller le Profil"):
      if cooperative and section and technicien:
        st.session_state.cooperative = cooperative
        st.session_state.section = section
        st.session_state.technicien = technicien
        st.session_state.identifie = True
        st.rerun()
      else:
        st.error("Veuillez remplir tous les champs.")
  st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
  st.markdown("### 👤 Session Active")
  st.write(f"**Coop :** {st.session_state.get('cooperative', 'N/A')}")
  st.write(f"**Section :** {st.session_state.get('section', 'N/A')}")
  st.write(f"**Agent :** {st.session_state.get('technicien', 'N/A')}")

  if st.button("🔓 Modifier le profil"):
    st.session_state.identifie = False
    st.rerun()

  st.markdown("---")
  st.markdown("## 📄 Gestion & Vue PDF")

  # --- BOUTON DE GÉNÉRATION MANUELLE DU PDF ---
  if st.button(
      "⚙️ Générer le PDF du PDC", type="secondary", use_container_width=True
  ):
    page_2_data = st.session_state.pdc_data.get(
        "Étape 2/15 : Données Socio-démographiques & Identification Producteur",
        {},
    )
    nom_prod = (
        page_2_data.get("nom_prenoms_producteur")
        or st.session_state.get("nom_producteur")
        or st.session_state.get("nom_prenoms_producteur")
        or "Producteur Inconnu"
    )
    code_prod = (
        page_2_data.get("code_national_producteur")
        or st.session_state.get("code_producteur")
        or st.session_state.get("code_national_producteur")
        or "CCC-000"
    )

    capture_complete_tablette = {
        "metadata_agent": {
            "cooperative": st.session_state.get("cooperative"),
            "section": st.session_state.get("section"),
            "technicien": st.session_state.get("technicien"),
            "date_capture": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "page_2_identification_reference": page_2_data,
        "donnees_15_etapes_pdc": st.session_state.get("pdc_data", {}),
        "variables_globales_session": {
            k: v
            for k, v in st.session_state.items()
            if not str(k).startswith("btn_")
            and not str(k).startswith("sb_")
            and not str(k).startswith("FormSubmitter")
            and k not in ["pdf_bytes_pdc", "pdc_data"]
        },
    }

    try:
      payload_pdf = {
          "nom_producteur": nom_prod,
          "code_ccc": code_prod,
          "zone": st.session_state.get("section"),
          "score_faisabilite": st.session_state.get("score_pdc", 0),
          "reponses": capture_complete_tablette,
          "historique_modules": [],
      }
      st.session_state["pdf_bytes_pdc"] = pdc.generer_pdf_pdc_fonction(
          payload_pdf
      )
      st.success("✅ PDF généré avec succès !")
    except Exception as e:
      st.error(f"❌ Erreur lors de la génération du PDF : {e}")

  # --- BOUTON DE TÉLÉCHARGEMENT PDF (AMÉLIORÉ & SÉCURISÉ) ---
  if st.session_state.get("pdf_bytes_pdc") is not None:
    st.download_button(
        label="📥 Télécharger le PDF",
        data=st.session_state["pdf_bytes_pdc"],
        file_name=f"PDC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="btn_download_pdf",
    )

    # --- MODE VUE IMPRESSION / PREVISUALISATION ---
    with st.expander("🖨️ Mode Vue Impression / Aperçu PDF"):
      base64_pdf = base64.b64encode(st.session_state["pdf_bytes_pdc"]).decode(
          "utf-8"
      )
      pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
      st.markdown(pdf_display, unsafe_allow_html=True)

  st.markdown("---")
  st.markdown("## 💾 Sauvegarde Intégrale Tablette")

  # --- ENREGISTREMENT TOTAL DANS LA TABLETTE ---
  if st.button(
      "💾 Enregistrer TOUTE la tablette",
      type="primary",
      use_container_width=True,
  ):
    page_2_data = st.session_state.pdc_data.get(
        "Étape 2/15 : Données Socio-démographiques & Identification Producteur",
        {},
    )

    nom_prod = (
        page_2_data.get("nom_prenoms_producteur")
        or st.session_state.get("nom_producteur")
        or st.session_state.get("nom_prenoms_producteur")
        or "Producteur Inconnu"
    )
    code_prod = (
        page_2_data.get("code_national_producteur")
        or st.session_state.get("code_producteur")
        or st.session_state.get("code_national_producteur")
        or "CCC-000"
    )

    superficie = (
        st.session_state.get("superficie")
        or page_2_data.get("superficie_ha")
        or 0.0
    )
    age_p = str(
        st.session_state.get("age_parcelle")
        or page_2_data.get("age_cacaoyere")
        or "0"
    )

    capture_complete_tablette = {
        "metadata_agent": {
            "cooperative": st.session_state.get("cooperative"),
            "section": st.session_state.get("section"),
            "technicien": st.session_state.get("technicien"),
            "date_capture": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "page_2_identification_reference": page_2_data,
        "donnees_15_etapes_pdc": st.session_state.get("pdc_data", {}),
        "variables_globales_session": {
            k: v
            for k, v in st.session_state.items()
            if not str(k).startswith("btn_")
            and not str(k).startswith("sb_")
            and not str(k).startswith("FormSubmitter")
            and k not in ["pdf_bytes_pdc", "pdc_data"]
        },
    }

    if st.session_state.get("pdf_bytes_pdc") is None:
      try:
        payload_pdf = {
            "nom_producteur": nom_prod,
            "code_ccc": code_prod,
            "zone": st.session_state.get("section"),
            "score_faisabilite": st.session_state.get("score_pdc", 0),
            "reponses": capture_complete_tablette,
            "historique_modules": [],
        }
        st.session_state["pdf_bytes_pdc"] = pdc.generer_pdf_pdc_fonction(
            payload_pdf
        )
      except Exception as e:
        st.warning(f"Note PDF : {e}")

    donnees_json_str = json.dumps(
        nettoyer_pour_json(capture_complete_tablette),
        cls=NpEncoder,
        ensure_ascii=False,
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'PDC_COMPLET_TOUTES_PAGES', ?, ?, ?, 'En attente')
            """,
          (
              st.session_state.get("cooperative"),
              st.session_state.get("section"),
              st.session_state.get("technicien"),
              nom_prod,
              code_prod,
              float(superficie),
              age_p,
              donnees_json_str,
              pdf_blob,
              date_saisie,
          ),
      )
      conn.commit()
      conn.close()

      st.session_state["afficher_ballons_flag"] = True
      st.success(
          f"✅ Capture intégrale enregistrée ! Producteur (Page 2) :"
          f" **{nom_prod}** ({code_prod})"
      )
      time.sleep(0.5)
      st.rerun()
    except Exception as e:
      st.error(f"❌ Erreur sauvegarde locale : {e}")

  # --- SYNCHRONISATION SERVEUR CENTRAL (SUPABASE CORRIGÉE) ---
  st.markdown("---")
  st.subheader("🔄 Synchronisation Supabase")

  try:
    conn = sqlite3.connect("leyla_terrain.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM rapports_locaux WHERE statut='En attente'"
    )
    nombre_attente = cursor.fetchone()[0]
    conn.close()
  except Exception:
    nombre_attente = 0

  st.write(f"📦 Rapports complets prêts à envoyer : **{nombre_attente}**")

  if st.button(
      "🚀 SYNCHRONISER MAINTENANT",
      use_container_width=True,
      type="primary",
      key="sb_synchro",
  ):
    if nombre_attente > 0:
      try:
        url_supabase = st.secrets["supabase"]["url"]
        key_supabase = st.secrets["supabase"]["key"]

        headers = {
            "apikey": key_supabase,
            "Authorization": f"Bearer {key_supabase}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
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
          (
              row_id,
              coop,
              sec,
              tech,
              prod,
              code_p,
              sup,
              age_p,
              mod_t,
              donnees_m,
              pdf_b,
          ) = ligne

          url_pdf_public = None
          if pdf_b is not None:
            code_clean = str(code_p).replace(" ", "_").replace("/", "_")
            nom_f = f"PDC_INTEGRAL_{code_clean}_{row_id}.pdf"
            url_pdf_public = uploader_pdf_supabase(pdf_b, nom_f)

          try:
            age_int = int(float(age_p)) if age_p else 0
          except ValueError:
            age_int = 0

          payload = {
              "cooperative_id": str(coop) if coop else "",
              "section_id": str(sec) if sec else "",
              "agent_id": str(tech) if tech else "",
              "nom_producteur": str(prod) if prod else "",
              "code_producteur": str(code_p) if code_p else "",
              "superficie": float(sup) if sup else 0.0,
              "age_cacaoyere": age_int,
              "module_execute": str(mod_t) if mod_t else "PDC_INTEGRAL",
              "observations_diagnostic": donnees_m,
              "url_pdf_pdc": url_pdf_public,
              "rdue_conforme": True,
          }

          response = requests.post(
              endpoint, json=payload, headers=headers, timeout=20
          )

          if response.status_code in [200, 201, 204]:
            cursor.execute(
                "UPDATE rapports_locaux SET statut='Envoyé' WHERE id=?",
                (row_id,),
            )
            nb_succes += 1
          else:
            st.sidebar.error(
                f"⚠ Échec envoi ID {row_id} (Code {response.status_code}) :"
                f" {response.text}"
            )
            # Arrêt de la boucle si une erreur survient pour ne pas effacer localement sans validation Supabase
            break

        conn.commit()
        conn.close()

        if nb_succes > 0:
          st.sidebar.success(f"✅ {nb_succes} rapport(s) intégraux synchronisés !")
          time.sleep(0.5)
          st.rerun()

      except Exception as e:
        st.sidebar.error(f"❌ Erreur lors de l'envoi : {e}")
    else:
      st.sidebar.info("Aucun rapport en attente.")

# --- DÉVERROUILLAGE ACCÈS TERRAIN ---
MOT_DE_PASSE_VALIDE = "leyla2.6"
if not st.session_state.get("appareil_deverrouille", False):
  st.header("🔒 Accès Sécurisé Technicien")
  with st.form("form_login"):
    code_agent = st.text_input("Code Agent / Technicien")
    mot_de_passe = st.text_input("Mot de passe *", type="password")
    if st.form_submit_button("🔓 Déverrouiller la tablette"):
      if mot_de_passe == MOT_DE_PASSE_VALIDE:
        st.session_state.appareil_deverrouille = True
        st.session_state.code_agent_connecte = code_agent
        st.rerun()
      else:
        st.error("Mot de passe incorrect.")
  st.stop()

# --- MODULE D'AFFICHAGE DU PDC ---
st.header("🛠️ Saisie Terrain - Plan de Développement de la Cacaoyère")
pdc.afficher()
