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
from generate_croquis import generer_croquis_parcelle
from streamlit_drawable_canvas import st_canvas
import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def evaluer_pdc(data):
    score = 100
    points_forts = []
    avertissements = []
    alertes_critiques = []

    # =========================================================
    # 1. IDENTIFICATION, MÉNAGE & LOCALISATION (5 critères)
    # =========================================================
    zone = data.get("zone", "")
    if zone:
        points_forts.append(f"Zone d'intervention identifiée : Zone {zone}.")
    else:
        avertissements.append("Zone géographique non spécifiée.")
        score -= 2

    ville = data.get("ville", "")
    if ville:
        points_forts.append(f"Localisation renseignée : {ville}.")
    else:
        avertissements.append("Localité/Ville non renseignée.")
        score -= 2

    lat = data.get("lat", 0)
    lon = data.get("lon", 0)
    if lat != 0 and lon != 0:
        points_forts.append(f"Géolocalisation valide ({lat}, {lon}).")
    else:
        avertissements.append("Coordonnées GPS absentes ou nulles.")
        score -= 3

    statut_fam = data.get("statut_famille", "")
    annee_naiss = data.get("annee_naissance", 0)
    if statut_fam and annee_naiss > 0:
        points_forts.append(f"Profil membre renseigné ({statut_fam}, Né(e) en {annee_naiss}).")
    else:
        avertissements.append("Profil du membre/ménage incomplet.")
        score -= 2

    niveau_inst = data.get("niveau_instruction", "")
    if niveau_inst:
        points_forts.append(f"Niveau d'instruction caractérisé : {niveau_inst}.")
    else:
        avertissements.append("Niveau d'instruction non renseigné.")
        score -= 1

    # =========================================================
    # 2. STRUCTURE FONCIÈRE & DIVERSIFICATION (4 critères)
    # =========================================================
    parcelles = data.get("parcelles_cacaoyer", [])
    superficie_totale = sum([p.get("Superficie (ha)", 0) for p in parcelles])
    if superficie_totale > 0:
        points_forts.append(f"Superficie cacaoyère caractérisée : {superficie_totale} ha sur {len(parcelles)} parcelle(s).")
    else:
        alertes_critiques.append("Superficie cacaoyère totale nulle ou non renseignée.")
        score -= 15

    parcelles_sans_origen = [p for p in parcelles if not p.get("Origine matériel végétal") or p.get("Origine matériel végétal") == "Tout venant"]
    if parcelles_sans_origen:
        avertissements.append(f"{len(parcelles_sans_origen)} parcelle(s) avec matériel végétal 'Tout venant' ou non certifié.")
        score -= 3

    autres_cultures = data.get("autres_cultures", [])
    if len(autres_cultures) > 0:
        points_forts.append(f"Diversification agricole effective : {len(autres_cultures)} autre(s) culture(s) déclarée(s).")
    else:
        avertissements.append("Aucune culture de diversification enregistrée (Mono-culture cacaoyère).")

    terres_disp = data.get("terres_disponibles", 0)
    if terres_disp > 0:
        points_forts.append(f"Réserve foncière disponible pour extension : {terres_disp} ha.")

    # =========================================================
    # 3. DENSITÉ & AGROFORESTERIE (3 critères)
    # =========================================================
    donnees_densite = data.get("donnees_densite", [])
    if len(donnees_densite) >= 4:
        points_forts.append(f"Comptage de densité conforme ({len(donnees_densite)} carrés renseignés).")
    else:
        avertissements.append("Comptage de densité partiel (moins de 4 carrés).")
        score -= 3

    densite = data.get("densite_calculee_ha", 0)
    if 1100 <= densite <= 1400:
        points_forts.append(f"Densité conforme aux normes agronomiques ({densite} pieds/ha).")
    elif 0 < densite < 1100:
        avertissements.append(f"Sous-densité détectée ({densite} pieds/ha). Risque de sous-rendement.")
        score -= 5
    elif densite > 1400:
        avertissements.append(f"Sur-densité détectée ({densite} pieds/ha). Risque d'étiolement et compétition.")
        score -= 5
    else:
        alertes_critiques.append("Densité globale nulle ou invalide.")
        score -= 10

    arbres = data.get("arbres_ombrage", [])
    total_arbres = sum([a.get("Nombre", 0) for a in arbres])
    if total_arbres > 0:
        points_forts.append(f"Agroforesterie active : {total_arbres} arbre(s) d'ombrage répertorié(s).")
    else:
        avertissements.append("Absence totale d'arbres d'ombrage (Stress thermique/hydrique élevé).")
        score -= 5

    # =========================================================
    # 4. DIAGNOSTICS PÉDOLOGIQUE & SANITAIRE (Critères de notation)
    # =========================================================
    sante_data = data.get("sante_cacaoyere", [])
    attaques_graves = [s for s in sante_data if "3." in str(s.get("Sévérité", "")) or "Élevé" in str(s.get("Sévérité", ""))]
    if len(attaques_graves) > 0:
        alertes_critiques.append(f"Pression sanitaire élevée : {len(attaques_graves)} problème(s) sévère(s) détecté(s).")
        score -= 10

    toposequence = data.get("toposequence", "")
    if toposequence in ["Bas de pente", "Bas-fond"]:
        avertissements.append(f"Risque d'hydromorphie lié à la toposéquence ({toposequence}).")
        score -= 3

    sols_data = data.get("caracteristiques_sol", [])
    if len(sols_data) < 3:
        avertissements.append("Profil pédologique renseigné incomplet (< 3 caractéristiques).")
        score -= 3

    # =========================================================
    # 5. ITINÉRAIRE TECHNIQUE & QUALITÉ POST-RÉCOLTE (5 critères)
    # =========================================================
    freq_recolte = data.get("frequence_recolte_jours", 0)
    if 10 <= freq_recolte <= 15:
        points_forts.append(f"Fréquence de récolte optimale ({freq_recolte} jours).")
    elif freq_recolte > 15:
        avertissements.append(f"Fréquence de récolte espacée ({freq_recolte} jours) : Risque de sur-maturation/germination.")
        score -= 3

    temps_ecab = data.get("temps_ecabossage_jours", 0)
    if 1 <= temps_ecab <= 3:
        points_forts.append(f"Délai d'écabossage conforme ({temps_ecab} jour(s)).")
    elif temps_ecab > 3:
        avertissements.append(f"Délai d'écabossage trop long ({temps_ecab} jours) : Risque de moisissures.")
        score -= 3

    duree_ferm = data.get("duree_fermentation_jours", 0)
    if 5 <= duree_ferm <= 6:
        points_forts.append(f"Durée de fermentation conforme ({duree_ferm} jours).")
    else:
        avertissements.append(f"Durée de fermentation atypique ({duree_ferm} jours).")
        score -= 3

    mode_ferm = data.get("mode_fermentation", "")
    if mode_ferm:
        points_forts.append(f"Mode de fermentation spécifié ({mode_ferm}).")

    sechage = data.get("methode_sechage", "")
    if "goudron" in sechage.lower():
        alertes_critiques.append("NON-CONFORMITÉ QUALITÉ : Le séchage sur goudron est strictement interdit (risques HAP).")
        score -= 25
    elif sechage:
        points_forts.append("Méthode de séchage conforme aux exigences de qualité.")

    # =========================================================
    # 6. INTRANTS, ÉQUIPEMENTS & MAIN-D'ŒUVRE (4 critères)
    # =========================================================
    engrais = data.get("utilisation_engrais", [])
    if len(engrais) > 0:
        points_forts.append(f"Programme de fertilisation renseigné ({len(engrais)} type(s) d'engrais).")

    phyto = data.get("produits_phytosanitaires", [])
    if len(phyto) > 0:
        points_forts.append(f"Protection phytosanitaire renseignée ({len(phyto)} produit(s)).")

    emb = data.get("gestion_emballages", "")
    if emb:
        points_forts.append("Mode de gestion des emballages de produits renseigné.")
    else:
        avertissements.append("Gestion des emballages vides non renseignée (Risque environnemental).")
        score -= 2

    equipements = data.get("equipements", [])
    if len(equipements) > 0:
        points_forts.append(f"Équipements et matériels répertoriés ({len(equipements)} équipement(s)).")
    elif superficie_totale > 2:
        avertissements.append("Aucun équipement enregistré pour la superficie exploitée.")
        score -= 3

    # =========================================================
    # 7. BILAN ÉCONOMIQUE, FINANCIER & FOYER (14 critères)
    # =========================================================
    financements = data.get("financement", [])
    comptes_epargne = [f for f in financements if f.get("Compte d'épargne (Oui/Non)") == "Oui"]
    if comptes_epargne:
        points_forts.append(f"Inclusion financière effective : Compte d'épargne actif ({len(comptes_epargne)} service(s)).")
    else:
        avertissements.append("Absence de compte d'épargne formel déclaré.")
        score -= 2

    demandes_credit = [f for f in financements if f.get("Demande de crédit (Oui/Non)") == "Oui"]
    if demandes_credit:
        points_forts.append("Accès au crédit sollicité/obtenu auprès des institutions.")

    prod_historique = data.get("prod_historique", [])
    total_prod = sum([p.get("Production (kg)", 0) for p in prod_historique])
    if total_prod > 0:
        points_forts.append(f"Historique de production renseigné ({total_prod} kg enregistrés au total).")
    else:
        avertissements.append("Historique de production nul ou non renseigné (0 kg).")
        score -= 5

    if (len(engrais) > 0 or len(phyto) > 0) and total_prod == 0:
        avertissements.append("Incohérence : Intrants/Engrais déclarés alors que la production historique affichée est 0 kg.")
        score -= 5

    autres_rev = data.get("autres_revenus", [])
    total_rev_annexes = sum([r.get("Montant estimé/an (FCFA)", 0) for r in autres_rev])
    if total_rev_annexes > 0:
        points_forts.append(f"Revenus complémentaires du foyer enregistrés ({total_rev_annexes:,} FCFA/an).".replace(",", " "))

    depenses = data.get("depenses_foyer", [])
    total_depenses = sum([d.get("Montant moyen (FCFA)", 0) for d in depenses])
    if total_depenses > 0:
        points_forts.append(f"Charges du foyer chiffrées : {total_depenses:,} FCFA.".replace(",", " "))
    else:
        avertissements.append("Bilan financier du foyer incomplet : Dépenses non chiffrées (0 FCFA).")
        score -= 5

    main_oeuvre = data.get("main_oeuvre", [])
    if len(main_oeuvre) > 0:
        points_forts.append(f"Main-d'œuvre identifiée ({len(main_oeuvre)} intervenant(s)/groupe(s)).")
    else:
        avertissements.append("Aucun détail renseigné sur la main-d'œuvre.")
        score -= 3

    score = max(0, score)
    return score, points_forts, avertissements, alertes_critiques



import hashlib
import io
import matplotlib.pyplot as plt
import numpy as np


def generer_croquis_parcelle(
    nom_producteur="Inconnu",
    code_ccc="CCC-001",
    surf_totale=1.0,
    surf_prod=0.0,
    surf_jeune=0.0,
    waypoint_gps="0.0 N, 0.0 W",
    nb_arbres=0,
    essences=None,
    acces=None,
    liste_arbres=None,
    liste_reperes=None,  # <-- Transmis depuis l'Étape 12.3
    liste_sommets=None,  # <-- Transmis depuis l'Étape 12.3
    **kwargs,
):
  """Génère un schéma cartographique de la parcelle cacaoyère au format In-Memory BytesIO.

  Intègre la géolocalisation des sommets (polygone), des infrastructures et des
  arbres d'ombrage.
  """
  if essences is None:
    essences = []
  if acces is None:
    acces = []
  if liste_arbres is None:
    liste_arbres = []
  if liste_reperes is None:
    liste_reperes = []
  if liste_sommets is None:
    liste_sommets = []

  # Configuration du canevas
  fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
  ax.set_facecolor("#f4f9f4")

  # --- 1. COLLECTE ET CALCUL DES BORNES GPS GLOBALES ---
  lats_all = []
  lons_all = []

  # Extraction de toutes les coordonnées valides (sommets, arbres, repères)
  for groupe in [liste_sommets, liste_arbres, liste_reperes]:
    for item in groupe:
      if isinstance(item, dict):
        lat = item.get("Latitude")
        lon = item.get("Longitude")
        if lat is not None and lon is not None:
          try:
            lats_all.append(float(lat))
            lons_all.append(float(lon))
          except ValueError:
            continue

  lat_min = min(lats_all) if lats_all else 6.0
  lat_max = max(lats_all) if lats_all else 7.0
  lon_min = min(lons_all) if lons_all else -6.0
  lon_max = max(lons_all) if lons_all else -5.0

  def projeter_xy(lat, lon):
    """Projette une coordonnée GPS sur l'espace graphique de [1.5, 8.5]."""
    if lat_max == lat_min or lon_max == lon_min:
      return 5.0, 5.0
    x = 1.5 + (float(lon) - lon_min) / (lon_max - lon_min) * 7.0
    y = 1.5 + (float(lat) - lat_min) / (lat_max - lat_min) * 7.0
    return x, y

  # --- 2. TRACÉ DU POLYGONE DE LA PARCELLE (OPTION A & B) ---
  sommets_valides = [
      s
      for s in liste_sommets
      if isinstance(s, dict)
      and s.get("Latitude") is not None
      and s.get("Longitude") is not None
  ]

  if len(sommets_valides) >= 3:
    # OPTION A : Tracé exact sur la base des waypoints contours réels
    poly_x, poly_y = [], []
    for s in sommets_valides:
      try:
        px, py = projeter_xy(s["Latitude"], s["Longitude"])
        poly_x.append(px)
        poly_y.append(py)
      except ValueError:
        continue

    if poly_x:
      poly_x.append(poly_x[0])
      poly_y.append(poly_y[0])
      ax.fill(
          poly_x,
          poly_y,
          color="#2e7d32",
          alpha=0.18,
          label="Parcelle (Polygone GPS)",
      )
      ax.plot(poly_x, poly_y, color="#1b5e20", linewidth=2.5, linestyle="--")
      ax.scatter(poly_x[:-1], poly_y[:-1], color="#1b5e20", s=40, zorder=4)
  else:
    # OPTION B : Contour pseudo-aléatoire unique basé sur le code du producteur
    seed_val = int(hashlib.md5(code_ccc.encode()).hexdigest(), 16) % (10**8)
    np.random.seed(seed_val)

    nb_cotes = np.random.randint(5, 8)
    angles = np.sort(np.random.uniform(0, 2 * np.pi, nb_cotes))
    rayons = np.random.uniform(2.8, 3.8, nb_cotes)

    poly_x = 5 + rayons * np.cos(angles)
    poly_y = 5 + rayons * np.sin(angles)
    poly_x = np.append(poly_x, poly_x[0])
    poly_y = np.append(poly_y, poly_y[0])

    ax.fill(
        poly_x,
        poly_y,
        color="#2e7d32",
        alpha=0.18,
        label="Parcelle (Tracé estimé)",
    )
    ax.plot(poly_x, poly_y, color="#1b5e20", linewidth=2.5, linestyle="--")

  # --- 3. REPRÉSENTATION DU WAYPOINT CENTRAL ---
  ax.plot(
      5,
      5,
      marker="*",
      markersize=14,
      color="#d32f2f",
      label=f"Waypoint Central ({waypoint_gps})",
  )

  # --- 4. TRACÉ DES INFRASTRUCTURES & REPÈRES GÉOLOCALISÉS ---
  dict_symboles = {
      "Campement / Habitation": {"marker": "s", "color": "#e65100", "lbl": "🏠"},
      "Cours d'eau / Bas-fond": {"marker": "o", "color": "#0288d1", "lbl": "💧"},
      "Puits / Source d'eau": {"marker": "p", "color": "#0097a7", "lbl": "🚰"},
      "Zone rocheuse non cultivable": {
          "marker": "h",
          "color": "#616161",
          "lbl": "🪨",
      },
      "Magasin de stockage": {"marker": "D", "color": "#795548", "lbl": "🏚️"},
  }

  reperes_affiches = 0
  for item in liste_reperes:
    if isinstance(item, dict):
      lat, lon = item.get("Latitude"), item.get("Longitude")
      elem = item.get("Élément", "Repère")
      if lat is not None and lon is not None:
        try:
          rx, ry = projeter_xy(lat, lon)
          cfg = dict_symboles.get(
              elem, {"marker": "X", "color": "#9c27b0", "lbl": "📍"}
          )
          ax.plot(
              rx,
              ry,
              marker=cfg["marker"],
              markersize=10,
              color=cfg["color"],
              markeredgecolor="#000000",
              zorder=5,
          )
          ax.text(
              rx + 0.12,
              ry - 0.15,
              f"{cfg['lbl']} {elem.split('/')[0]}",
              fontsize=7,
              fontweight="bold",
              color=cfg["color"],
          )
          reperes_affiches += 1
        except ValueError:
          continue

  if reperes_affiches > 0:
    ax.plot(
        [],
        [],
        marker="s",
        color="#e65100",
        linestyle="None",
        label=f"Infrastructures ({reperes_affiches} GPS)",
    )

  # --- 5. TRACÉ DES ARBRES GÉOLOCALISÉS (ÉTAPES 4 & 12.3) ---
  arbres_affiches = 0
  if liste_arbres:
    for item in liste_arbres:
      if isinstance(item, dict):
        lat, lon = item.get("Latitude"), item.get("Longitude")
        espece = item.get("Espèce", "Arbre")
        if lat is not None and lon is not None:
          try:
            ax_x, ax_y = projeter_xy(lat, lon)
            ax.plot(
                ax_x,
                ax_y,
                marker="^",
                markersize=9,
                color="#388e3c",
                markeredgecolor="#1b5e20",
                zorder=4,
            )
            ax.text(
                ax_x + 0.1,
                ax_y + 0.1,
                str(espece),
                fontsize=7,
                fontweight="bold",
                color="#1b5e20",
                bbox=dict(
                    boxstyle="round,pad=0.15",
                    facecolor="#ffffff",
                    edgecolor="none",
                    alpha=0.65,
                ),
            )
            arbres_affiches += 1
          except ValueError:
            continue

    if arbres_affiches > 0:
      ax.plot(
          [],
          [],
          marker="^",
          color="#388e3c",
          linestyle="None",
          label=f"Arbres conservés ({arbres_affiches} GPS)",
      )
  else:
    np.random.seed(42)
    for _ in range(min(nb_arbres, 25)):
      rx = np.random.uniform(2.5, 7.5)
      ry = np.random.uniform(2.5, 7.5)
      ax.plot(rx, ry, marker="^", markersize=9, color="#4caf50", alpha=0.8)

  # --- 6. HABILLAGE ET INFORMATIONS STATISTIQUES ---
  ax.set_title(
      f"CROQUIS TECHNIQUE DE LA PARCELLE — CCC / RDUE\nProducteur :"
      f" {nom_producteur} | Code : {code_ccc}",
      fontsize=11,
      fontweight="bold",
      pad=15,
  )

  info_text = (
      f"Superficie Totale : {surf_totale:.2f} ha\n"
      f"Cacao Productif : {surf_prod:.2f} ha\n"
      f"Cacao Immature : {surf_jeune:.2f} ha\n"
      f"Arbres d'ombrage conservés : {nb_arbres} pieds\n"
      f"Accès : {', '.join(acces[:2]) if acces else 'Standard'}"
  )
  ax.text(
      0.02,
      0.02,
      info_text,
      transform=ax.transAxes,
      fontsize=8.5,
      bbox=dict(
          boxstyle="round,pad=0.5",
          facecolor="#ffffff",
          edgecolor="#cccccc",
          alpha=0.9,
      ),
  )

  ax.set_xlim(0, 10)
  ax.set_ylim(0, 10)
  ax.grid(True, linestyle=":", alpha=0.5)
  ax.legend(loc="upper right", fontsize=8.5)
  ax.set_xlabel("Orientation Est-Ouest (Relatif)")
  ax.set_ylabel("Orientation Nord-Sud (Relatif)")

  buf = io.BytesIO()
  plt.tight_layout()
  plt.savefig(buf, format="png", dpi=200)
  plt.close(fig)
  buf.seek(0)

  return buf




import json
import numpy as np
import pandas as pd

class NpEncoder(json.JSONEncoder):
    """Convertit tous les types d'objets non-JSON (int64, float64, arrays, etc.) en types natifs Python."""
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
    """Nettoie récursivement un dictionnaire ou une liste pour la sérialisation JSON."""
    if isinstance(d, dict):
        # Filtre les clés Streamlit internes non sérialisables
        return {
            str(k): nettoyer_pour_json(v) 
            for k, v in d.items() 
            if not str(k).startswith("FormSubmitter") and not str(k).startswith("btn_")
        }
    elif isinstance(d, list):
        return [nettoyer_pour_json(v) for v in d]
    elif isinstance(d, (np.integer, int)):
        return int(d)
    elif isinstance(d, (np.floating, float)):
        return float(d)
    elif isinstance(d, bytes):
        return None  # On évite d'inclure des octets bruts (comme les images/pdf) directement dans le JSON textuel
    else:
        return d


import sqlite3
import json
import numpy as np
import pandas as pd

def convert_types(obj):
    """Convertit récursivement les int64/float64 Pandas/NumPy en types Python natifs."""
    if isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    return obj


def sauvegarder_en_local_sqlite(donnees_dossier: dict, db_path: str = "leyla_local.db"):
    """
    Sauvegarde TOUT le dossier PDC (avec session intégrale et données nettoyées) dans la base SQLite locale.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pdc_locaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_ccc TEXT,
                nom_producteur TEXT,
                zone TEXT,
                score_faisabilite REAL,
                donnees_pdc TEXT,
                croquis_base64 TEXT,
                facteurs_succes TEXT,
                statut_synchro TEXT DEFAULT 'En attente de synchro',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 1. Nettoyage et conversion exhaustive de TOUT le dictionnaire
        donnees_completes_nettoyees = nettoyer_pour_json(donnees_dossier)
        
        # 2. Sérialisation JSON de TOUTES les données (donnees_pdc + etat_session_integral)
        donnees_pdc_json = json.dumps(donnees_completes_nettoyees, cls=NpEncoder, ensure_ascii=False)

        cursor.execute("""
            INSERT INTO pdc_locaux (
                code_ccc, 
                nom_producteur, 
                zone, 
                score_faisabilite, 
                donnees_pdc, 
                croquis_base64, 
                facteurs_succes, 
                statut_synchro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            donnees_dossier.get("code_ccc", ""),
            donnees_dossier.get("nom_producteur", ""),
            donnees_dossier.get("zone", ""),
            donnees_dossier.get("score_faisabilite", 0),
            donnees_pdc_json,  # Contient désormais tout l'état de session et le dossier complet
            donnees_dossier.get("croquis_base64", ""),
            donnees_dossier.get("facteurs_succes", ""),
            donnees_dossier.get("statut_synchro", "En attente de synchro")
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde SQLite locale : {e}")
        raise e


import os
import tempfile
import json
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from fpdf import FPDF

# =========================================================================
# 1. UTILS ET NETTOYAGE DU TEXTE POUR FPDF (LATIN-1)
# =========================================================================

def nettoyer_texte_pdf(chaine: str) -> str:
    """
    Nettoie les caractères UTF-8 non pris en charge par l'encodage latin-1 de FPDF.
    Remplace les puces complexes et les emojis par des équivalents ASCII.
    """
    if chaine is None:
        return ""
    s = str(chaine)
    replacements = {
        "•": "-", "–": "-", "—": "-", "’": "'",
        "“": '"', "”": '"', "…": "...", "\u200b": "",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s.encode("latin-1", "replace").decode("latin-1")


# =========================================================================
# 2. FONCTIONS DE GESTION DES SIGNATURES TACTILES
# =========================================================================

def extraire_image_signature(canvas_obj):
    """
    Extrait en toute sécurité le tableau d'image NumPy depuis le composant canvas.
    """
    if canvas_obj is None:
        return None
    
    # 1. Vérification si un tracé (dessin) existe dans le canvas
    has_drawing = False
    try:
        if hasattr(canvas_obj, "json_data") and canvas_obj.json_data is not None:
            objects = canvas_obj.json_data.get("objects", [])
            if len(objects) > 0:
                has_drawing = True
    except Exception:
        pass

    if not has_drawing:
        return None

    # 2. Récupération directe du tableau image_data
    try:
        img_array = canvas_obj.image_data
        if img_array is not None and isinstance(img_array, np.ndarray):
            if img_array.size > 0:
                return img_array
    except Exception:
        pass

    # 3. Secours : si l'attribut image_data lève une exception lors du clic
    return "SIGNATURE_PRESENTE"


def traiter_signature_pour_pdf(sig_data):
    """
    Convertit la matrice d'image (NumPy Array) ou l'objet signature en un fichier 
    temporaire PNG réutilisable par FPDF.
    """
    if sig_data is None:
        return None

    # CAS 1 : C'est une matrice d'image NumPy (issue de canvas_obj.image_data)
    if isinstance(sig_data, np.ndarray):
        try:
            # Vérifier que le tableau n'est pas vide et contient du tracé
            if sig_data.size > 0:
                # Si RGBA, vérifier la transparence sur le canal Alpha (index 3)
                if sig_data.ndim == 3 and sig_data.shape[2] == 4:
                    if not np.any(sig_data[:, :, 3] > 0):
                        return None
                
                img_pil = Image.fromarray(sig_data.astype('uint8'))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                img_pil.save(temp_file.name, format="PNG")
                temp_file.close()
                return temp_file.name
        except Exception:
            return None

    # CAS 2 : C'est un chemin vers un fichier image existant
    elif isinstance(sig_data, str) and os.path.exists(sig_data):
        return sig_data

    return None


# =========================================================================
# 3. GÉNÉRATEUR DU RAPPORT PDF (PDC)
# =========================================================================

def generer_pdf_pdc_fonction(data: dict) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # En-tête principal
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, nettoyer_texte_pdf("PLAN DE DÉVELOPPEMENT DE CONSEIL (PDC)"), ln=True, align="C")
    pdf.ln(3)
    
    # Bloc Identité
    pdf.set_font("Arial", "B", 10)
    nom_prod = data.get('nom_producteur') or data.get('producteur') or 'Inconnu'
    code_ccc = data.get('code_ccc') or data.get('code_producteur') or 'N/A'
    zone = data.get('zone') or data.get('section') or 'N/A'
    score = data.get('score_faisabilite', 'N/A')
    
    pdf.cell(0, 6, nettoyer_texte_pdf(f"Producteur : {nom_prod}"), ln=True)
    pdf.cell(0, 6, nettoyer_texte_pdf(f"Code CCC : {code_ccc}"), ln=True)
    pdf.cell(0, 6, nettoyer_texte_pdf(f"Zone d'intervention : {zone}"), ln=True)
    pdf.cell(0, 6, nettoyer_texte_pdf(f"Score de Faisabilité : {score} / 100"), ln=True)
    pdf.ln(3)
    
    # Séparateur visuel
    pdf.set_draw_color(180, 180, 180)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # --- SECTION 1 : SYNTHÈSE DES DONNÉES EN SESSION ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, nettoyer_texte_pdf("1. SYNTHÈSE DES DONNÉES DU FORMULAIRE EN SESSION :"), ln=True)
    pdf.ln(2)
    
    reponses = data.get("reponses", {})
    if isinstance(reponses, dict) and reponses:
        for cle, val in reponses.items():
            # Exclure le dictionnaire signataires du listing brut (traité à la fin)
            if cle == "signataires":
                continue

            nom_cle = nettoyer_texte_pdf(str(cle).replace("_", " ").capitalize())
            
            if isinstance(val, list):
                if len(val) > 0:
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 6, nettoyer_texte_pdf(f"- {nom_cle} ({len(val)} élément(s)) :"), ln=True)
                    pdf.set_font("Arial", size=9)
                    for i, item in enumerate(val, 1):
                        details = ", ".join([f"{k}: {v}" for k, v in item.items()]) if isinstance(item, dict) else str(item)
                        pdf.write(5, nettoyer_texte_pdf(f"   * [{i}] {details}\n"))
            elif isinstance(val, dict):
                if len(val) > 0:
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 6, nettoyer_texte_pdf(f"- {nom_cle} :"), ln=True)
                    pdf.set_font("Arial", size=9)
                    for k_sub, v_sub in val.items():
                        pdf.write(5, nettoyer_texte_pdf(f"   * {k_sub}: {v_sub}\n"))
            else:
                str_val = str(val).strip()
                if str_val != "":
                    pdf.set_font("Arial", size=9)
                    pdf.write(5, nettoyer_texte_pdf(f"- {nom_cle} : {str_val}\n"))
    else:
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, nettoyer_texte_pdf("Aucune donnée de formulaire directe."), ln=True)

    pdf.ln(5)

    # --- SECTION 2 : RAPPORTS SQLITE LOCAUX ---
    historique = data.get("historique_modules", [])
    if historique:
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, nettoyer_texte_pdf("2. RAPPORTS TERRAIN & DIAGNOSTICS ENREGISTRÉS :"), ln=True)
        pdf.ln(2)

        for idx, rap in enumerate(historique, 1):
            mod_nom = rap.get("module", "Module")
            d_date = rap.get("date", "")
            details = rap.get("details", {})

            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, nettoyer_texte_pdf(f"Fiche #{idx} - {mod_nom} ({d_date}) :"), ln=True)
            pdf.set_font("Arial", size=9)

            if isinstance(details, dict):
                for k_d, v_d in details.items():
                    k_clean = str(k_d).replace("_", " ").capitalize()
                    if isinstance(v_d, (dict, list)):
                        v_str = json.dumps(v_d, ensure_ascii=False)
                    else:
                        v_str = str(v_d)
                    pdf.write(5, nettoyer_texte_pdf(f"   * {k_clean} : {v_str}\n"))
            else:
                pdf.write(5, nettoyer_texte_pdf(f"   * Contenu : {details}\n"))
            pdf.ln(2)

    # --- SECTION 3 : VALIDATION ET SIGNATURES ---
    signataires = reponses.get("signataires", {}) if isinstance(reponses, dict) else {}
    if signataires:
        pdf.ln(5)
        pdf.set_draw_color(180, 180, 180)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, nettoyer_texte_pdf("3. VALIDATION ET SIGNATURES :"), ln=True)
        pdf.ln(2)

        date_val = signataires.get("date_validation", "")
        if date_val:
            pdf.set_font("Arial", "I", 9)
            pdf.cell(0, 5, nettoyer_texte_pdf(f"Document validé le : {date_val}"), ln=True)
            pdf.ln(3)

        # Repères de position pour double colonne
        y_start_signatures = pdf.get_y()

        # --- Colonne Gauche : Producteur ---
        pdf.set_xy(10, y_start_signatures)
        pdf.set_font("Arial", "B", 10)
        prod_nom = signataires.get("producteur_nom", "Producteur")
        pdf.cell(90, 6, nettoyer_texte_pdf(f"Producteur : {prod_nom}"), ln=True)

        path_sig_prod = traiter_signature_pour_pdf(signataires.get("producteur_signature"))
        if path_sig_prod:
            pdf.image(path_sig_prod, x=10, y=pdf.get_y() + 2, w=55)
            if os.path.exists(path_sig_prod) and path_sig_prod.endswith(".png"):
                try:
                    os.remove(path_sig_prod)
                except Exception:
                    pass
        elif signataires.get("producteur_signature") == "SIGNATURE_PRESENTE":
            pdf.set_font("Arial", "I", 8)
            pdf.cell(90, 5, nettoyer_texte_pdf("[Signature validée sur tablette]"), ln=True)

        # --- Colonne Droite : Technicien ---
        pdf.set_xy(110, y_start_signatures)
        pdf.set_font("Arial", "B", 10)
        tech_nom = signataires.get("technicien_nom", "Technicien")
        pdf.cell(90, 6, nettoyer_texte_pdf(f"Technicien : {tech_nom}"), ln=True)

        path_sig_tech = traiter_signature_pour_pdf(signataires.get("technicien_signature"))
        if path_sig_tech:
            pdf.image(path_sig_tech, x=110, y=pdf.get_y() + 2, w=55)
            if os.path.exists(path_sig_tech) and path_sig_tech.endswith(".png"):
                try:
                    os.remove(path_sig_tech)
                except Exception:
                    pass
        elif signataires.get("technicien_signature") == "SIGNATURE_PRESENTE":
            pdf.set_font("Arial", "I", 8)
            pdf.cell(90, 5, nettoyer_texte_pdf("[Signature validée sur tablette]"), ln=True)

    pdf_buffer = pdf.output(dest='S')
    if isinstance(pdf_buffer, str):
        return pdf_buffer.encode('latin-1', 'replace')
    return bytes(pdf_buffer)



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


import streamlit as st
import pandas as pd

# Import de la fonction d'accès à la BDD locale si définie dans tablette/utilitaires
try:
    from tablette import charger_donnees_par_module
except ImportError:
    def charger_donnees_par_module(nom_module):
        return pd.DataFrame()

# =========================================================================
# INTERFACE STREAMLIT DU PDC
# =========================================================================

def afficher():
    # 1. Chargement des données
    df = charger_donnees_par_module("PDC")

    st.title("📋 PDC - Diagnostic & Plan de Développement")

    # 2. Section de consultation des PDC enregistrés
    with st.expander(
        f"📁 Afficher / Masquer les données brutes ({len(df)} enregistrement(s))"
    ):
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun enregistrement PDC disponible.")

    st.markdown("---")

    # =========================================================
    # INITIALISATION SÉCURISÉE DES ÉTATS DE SESSION (SESSION STATE)
    # =========================================================
    if "etape_pdc" not in st.session_state:
        st.session_state.etape_pdc = 1

    if "reponses_pdc" not in st.session_state:
        st.session_state.reponses_pdc = {}

    if "temp_tableau_arbres" not in st.session_state:
        st.session_state.temp_tableau_arbres = []

    if "temp_tableau_cultures" not in st.session_state:
        st.session_state.temp_tableau_cultures = []

    if "temp_tableau_equipements" not in st.session_state:
        st.session_state.temp_tableau_equipements = []

    # --- INITIALISATION DES VARIABLES RACINES POUR SYNC SQLITE / SUPABASE ---
    if "nom_producteur" not in st.session_state:
        st.session_state.nom_producteur = ""
    if "code_producteur" not in st.session_state:
        st.session_state.code_producteur = ""
    if "superficie" not in st.session_state:
        st.session_state.superficie = 0.0

    # Initialisation du dictionnaire maître pour les 15 étapes
    if "pdc_data" not in st.session_state:
        st.session_state.pdc_data = {
            "Étape 1/15 : Localisation & Identification de la Section": {},
            "Étape 2/15 : Identification du Producteur & Données de la Parcelle": {
                "👤 Identification du Producteur": {},
                "📍 Données de la Parcelle": {}
            },
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


    # --- AJOUT DES INITIALISATIONS POUR L'ÉTAPE 13 ---
    if "df_cultures_pdc" not in st.session_state:
        st.session_state.df_cultures_pdc = [
            {
                "Culture": "Cacao - Parcelle 1",
                "Superficie (ha)": 3.5,
                "Année de création": 2012,
                "Source matériel végétal": "SATMACI / ANADER / CNRA",
                "Production campagne préc. (kg)": 2100,
                "Revenu (FCFA)": 3150000,
            },
            {
                "Culture": "Cacao - Parcelle 2",
                "Superficie (ha)": 1.0,
                "Année de création": 2023,
                "Source matériel végétal": "Pépiniériste privé",
                "Production campagne préc. (kg)": 0,
                "Revenu (FCFA)": 0,
            },
            {
                "Culture": "Hévéa",
                "Superficie (ha)": 0.0,
                "Année de création": 2020,
                "Source matériel végétal": "Tout venant",
                "Production campagne préc. (kg)": 0,
                "Revenu (FCFA)": 0,
            },
            {
                "Culture": "Palmier à huile",
                "Superficie (ha)": 0.0,
                "Année de création": 2020,
                "Source matériel végétal": "SATMACI / ANADER / CNRA",
                "Production campagne préc. (kg)": 0,
                "Revenu (FCFA)": 0,
            },
            {
                "Culture": "Vivriers (Banane/Maïs/Cassava)",
                "Superficie (ha)": 0.5,
                "Année de création": 2024,
                "Source matériel végétal": "Tout venant",
                "Production campagne préc. (kg)": 1200,
                "Revenu (FCFA)": 450000,
            },
            {
                "Culture": "Autres activités / Verger",
                "Superficie (ha)": 0.0,
                "Année de création": 2020,
                "Source matériel végétal": "Tout venant",
                "Production campagne préc. (kg)": 0,
                "Revenu (FCFA)": 0,
            },
        ]

    if "df_arbres_pdc" not in st.session_state:
        st.session_state.df_arbres_pdc = [
            {
                "Nom de l'arbre": "Akpi",
                "Nombre": 1,
                "Latitude (N)": 6.020668,
                "Longitude (W)": -4.3571323,
                "Statut actuel": "Préservé",
                "Rôle / Avantage": "Bois d'œuvre / Ombrage",
                "Décision": "À maintenir",
                "Remarque / Distance": "Bonne association",
            },
            {
                "Nom de l'arbre": "Fraké",
                "Nombre": 1,
                "Latitude (N)": 6.020664,
                "Longitude (W)": -4.3569498,
                "Statut actuel": "Préservé",
                "Rôle / Avantage": "Bois d'œuvre",
                "Décision": "À éliminer",
                "Remarque / Distance": "Situé à 1,5m d'un cacaoyer",
            },
            {
                "Nom de l'arbre": "Fromager",
                "Nombre": 1,
                "Latitude (N)": 6.020614,
                "Longitude (W)": -4.3561020,
                "Statut actuel": "Préservé",
                "Rôle / Avantage": "Ombrage haut",
                "Décision": "À maintenir",
                "Remarque / Distance": "En bordure de parcelle",
            },
        ]

    if "df_materiel_pdc" not in st.session_state:
        st.session_state.df_materiel_pdc = [
            {
                "Type": "Matériel de traitement",
                "Désignation": "Pulvérisateur à dos",
                "Quantité": 1,
                "Année acquisition": 2022,
                "Coût (FCFA)": 25000,
                "État": "Bon",
            },
            {
                "Type": "Matériel de traitement",
                "Désignation": "Atomiseur à moteur",
                "Quantité": 1,
                "Année acquisition": 2021,
                "Coût (FCFA)": 130000,
                "État": "Acceptable",
            },
            {
                "Type": "Matériel de transport",
                "Désignation": "Brouette",
                "Quantité": 2,
                "Année acquisition": 2023,
                "Coût (FCFA)": 30000,
                "État": "Bon",
            },
            {
                "Type": "Moyen de déplacement",
                "Désignation": "MOTO Tricycle / Moto 2 roues",
                "Quantité": 1,
                "Année acquisition": 2020,
                "Coût (FCFA)": 650000,
                "État": "Mauvais",
            },
        ]

    # Barre de progression globale (15 étapes)
    total_etapes = 15
    st.progress(st.session_state.etape_pdc / total_etapes)

    # ---------------------------------------------------------
    # ÉTAPE 1 : INFORMATIONS GÉNÉRALES & LOCALISATION
    # ---------------------------------------------------------
    if st.session_state.etape_pdc == 1:
        st.subheader("Étape 1/15 : Localisation & Identification de la Section")
       
        REGIONS_CACAO = {
            "Nawa (Soubré)": [
                "Soubré",
                "Grand-Zattry",
                "Méagui",
                "Buyo",
                "Gueyo",
                "Okrouyo",
                "Liliyo",
                "Yabayo",
                "Oupoyo",
                "Autre (Saisir)",
            ],
            "Lôh-Djiboua (Divo)": [
                "Divo",
                "Lakota",
                "Guitry",
                "Hiré",
                "Zikisso",
                "Ogoudou",
                "Gagny",
                "Didoko",
                "Nebo",
                "Goudouko",
                "Autre (Saisir)",
            ],
            "Haut-Sassandra (Daloa)": [
                "Daloa",
                "Issia",
                "Vavoua",
                "Zoukougbeu",
                "Saioua",
                "Bediala",
                "Boguhé",
                "Namanane",
                "Iboguhé",
                "Dania",
                "Autre (Saisir)",
            ],
            "San-Pédro": [
                "San-Pédro",
                "Sassandra",
                "Fresco",
                "Gbagbam",
                "Grabo",
                "Grand-Béréby",
                "Dakpadou",
                "Sago",
                "Dassioko",
                "Autre (Saisir)",
            ],
            "Gôh (Gagnoa)": [
                "Gagnoa",
                "Oumé",
                "Diégonéfla",
                "Ouragahio",
                "Bayota",
                "Guibéroua",
                "Sériho",
                "Dignago",
                "Gnagbodougnoa",
                "Tonela",
                "Autre (Saisir)",
            ],
            "Agnéby-Tiassa (Agboville)": [
                "Agboville",
                "Sikensi",
                "Tiassalé",
                "Taabo",
                "Rubino",
                "Azaguié",
                "Grand-Morié",
                "N'Douci",
                "Gbolouville",
                "Autre (Saisir)",
            ],
            "Indénié-Djuablin (Abengourou)": [
                "Abengourou",
                "Agnibilékrou",
                "Bettie",
                "Zaranou",
                "Ebilassokro",
                "Yakassé-Feyassé",
                "Daffoukro",
                "Autre (Saisir)",
            ],
            "Sud-Comoé (Aboisso)": [
                "Aboisso",
                "Adiaké",
                "Grand-Bassam",
                "Ayamé",
                "Maféré",
                "Aboisso-Comoé",
                "Bianouan",
                "Etuéboué",
                "Autre (Saisir)",
            ],
            "Cavally (Guiglo)": [
                "Guiglo",
                "Blolequin",
                "Taï",
                "Toulepleu",
                "Zagne",
                "Nizahon",
                "Doké",
                "Zéo",
                "Kaade",
                "Autre (Saisir)",
            ],
            "Guémon (Duékoué)": [
                "Duékoué",
                "Bangolo",
                "Kouibly",
                "Fakobly",
                "Bagohouo",
                "Guezon",
                "Tieny-Siably",
                "Nidrou",
                "Autre (Saisir)",
            ],
            "Mé (Adzopé)": [
                "Adzopé",
                "Akoupé",
                "Yakassé-Attobrou",
                "Afféry",
                "Agou",
                "Bécédi-Brignan",
                "Assikoi",
                "Autre (Saisir)",
            ],
            "Iffou (Daoukro)": [
                "Daoukro",
                "M'Bahiakro",
                "Prikro",
                "Ettrokro",
                "Samanza",
                "Ananda",
                "Koffi-Amonkro",
                "Autre (Saisir)",
            ],
            "N'Zi (Dimbokro)": [
                "Dimbokro",
                "Bocanda",
                "Kouassi-Kouassikro",
                "N'Douffoukro",
                "Abigui",
                "Bengassou",
                "Autre (Saisir)",
            ],
        }

        # 1. Sélection de la Région
        region = st.selectbox(
            "Région cacaoyère *",
            options=list(REGIONS_CACAO.keys()),
            key="region_input",
        )

        # 2. Choix de la localité
        villes_disponibles = REGIONS_CACAO.get(region, [])
        ville_choisie = st.selectbox(
            "Sous-préfecture / Localité *",
            options=villes_disponibles,
            key="ville_input",
        )

        # 3. Saisie dynamique si 'Autre (Saisir)' est sélectionné
        if ville_choisie == "Autre (Saisir)":
            ville = st.text_input(
                "Saisir la localité / Sous-préfecture *",
                placeholder="Ex: Grand-Zattry, Okrouyo, Hiré...",
                key="ville_custom_input",
            )
        else:
            ville = ville_choisie

        # 4. Saisie optionnelle du Village / Campement
        village_campement = st.text_input(
            "Village / Campement (Optionnel)",
            placeholder="Ex: Kouamékro, Village Zattry 2...",
            key="village_input",
        )

        # 5. Identification de la Section
        section = st.text_input(
            "Section *",
            placeholder="Ex: Section Grand-Zattry 1, Section Divo-Sud...",
            key="section_input",
        )

        # Boutons de navigation
        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button(
                "Suivant ➡️", use_container_width=True, type="primary"
            ):
                if section.strip() and ville.strip():
                    st.session_state.reponses_pdc.update(
                        {
                            "region": region,
                            "ville": ville.strip(),
                            "village_campement": village_campement.strip(),
                            "section": section.strip(),
                        }
                    )
                    st.session_state.etape_pdc = 2
                    st.rerun()
                else:
                    st.error(
                        "⚠️ Veuillez renseigner la Localité et la Section avant"
                        " de continuer."
                    )


    # ---------------------------------------------------------
    # ÉTAPE 2 : IDENTIFICATION DU PRODUCTEUR & DONNÉES DE LA PARCELLE
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 2:
        st.subheader("Étape 2/15 : Identification du Producteur & Données de la Parcelle")
        st.info("Saisie des informations d'identification officielles selon le modèle Conseil Café-Cacao et caractéristiques de la parcelle. Les champs marqués d'un (*) sont obligatoires.")

        # --- PARTIE 1 : IDENTIFICATION DU PRODUCTEUR ---
        st.markdown("### 👤 Identification du Producteur (Situation de Référence)")
        
        col_id1, col_id2 = st.columns(2)
        
        with col_id1:
            nom_prenoms = st.text_input(
                "Nom et prénoms du producteur *", 
                placeholder="Ex: Kouamé Konan Jean", 
                key="input_nom_prenoms_e2"
            )
            contact_tel = st.text_input(
                "Contact (Tél) *", 
                placeholder="Ex: 0708091011", 
                key="input_contact_tel_e2"
            )
            code_national = st.text_input(
                "Code National du producteur (Le Conseil du Café-Cacao) *", 
                placeholder="Ex: CCC-12345678", 
                key="input_code_national_e2"
            )
            code_groupe = st.text_input(
                "Code groupe", 
                placeholder="Ex: GRP-01", 
                key="input_code_groupe_e2"
            )
            nom_entite = st.text_input(
                "Nom Entité reconnue", 
                placeholder="Ex: COOP-CA SCACO", 
                key="input_nom_entite_e2"
            )
            code_entite = st.text_input(
                "Code Entité reconnue", 
                placeholder="Ex: COOP-001", 
                key="input_code_entite_e2"
            )

        with col_id2:
            delegation_regionale = st.text_input(
                "Délégation Régionale du Conseil du Café-Cacao", 
                placeholder="Ex: Divo", 
                key="input_delegation_e2"
            )
            departement = st.text_input(
                "Département", 
                placeholder="Ex: Divo", 
                key="input_departement_e2"
            )
            sous_prefecture = st.text_input(
                "Sous-Préfecture", 
                placeholder="Ex: Divo-Sud", 
                key="input_sprefecture_e2"
            )
            village = st.text_input(
                "Village", 
                placeholder="Ex: Hermankono", 
                key="input_village_e2"
            )
            campement = st.text_input(
                "Campement", 
                placeholder="Ex: Campement Kouamé", 
                key="input_campement_e2"
            )

        st.markdown("---")

        # --- PARTIE 2 : DONNÉES DE LA PARCELLE ---
        st.markdown("### 📍 Données de la Parcelle")

        superficie = st.number_input(
            "Superficie de la plantation (ha) *", 
            min_value=0.0, 
            step=0.5, 
            key="input_superficie_e2"
        )
        annee_creation = st.number_input(
            "Année de création", 
            min_value=1950, 
            max_value=2026, 
            value=2010, 
            key="input_annee_creation_e2"
        )
        lat = st.number_input(
            "Latitude GPS", 
            format="%.6f", 
            value=5.7881, 
            key="input_lat_e2"
        )
        lon = st.number_input(
            "Longitude GPS", 
            format="%.6f", 
            value=-6.5918, 
            key="input_lon_e2"
        )

        st.markdown("---")

        # --- BOUTONS DE NAVIGATION ---
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("⬅️ Retour", key="btn_retour_pdc_etape2", use_container_width=True):
                st.session_state.etape_pdc = 1
                st.rerun()

        with col2:
            if st.button("Suivant ➡️", key="btn_suivant_pdc_etape2", type="primary", use_container_width=True):
                # Vérification de la présence des champs obligatoires
                champs_manquants = []
                if not nom_prenoms.strip():
                    champs_manquants.append("Nom et prénoms du producteur")
                if not contact_tel.strip():
                    champs_manquants.append("Contact (Tél)")
                if not code_national.strip():
                    champs_manquants.append("Code National du producteur")
                if superficie <= 0.0:
                    champs_manquants.append("Superficie de la plantation (doit être > 0)")

                if champs_manquants:
                    for champ in champs_manquants:
                        st.error(f"⚠️ Le champ obligatoire **{champ}** n'est pas renseigné.")
                else:
                    if "reponses_pdc" not in st.session_state:
                        st.session_state.reponses_pdc = {}

                    # Mise à jour globale des réponses (Identification + Parcelle)
                    st.session_state.reponses_pdc.update({
                        # Identification Producteur
                        "nom_prenoms_producteur": nom_prenoms.strip(),
                        "contact_tel": contact_tel.strip(),
                        "code_national_producteur": code_national.strip(),
                        "code_groupe": code_groupe.strip(),
                        "nom_entite_reconnue": nom_entite.strip(),
                        "code_entite_reconnue": code_entite.strip(),
                        "delegation_regionale": delegation_regionale.strip(),
                        "departement": departement.strip(),
                        "sous_prefecture": sous_prefecture.strip(),
                        "village": village.strip(),
                        "campement": campement.strip(),
                        # Caractéristiques Parcelle
                        "superficie": superficie,
                        "annee_creation": annee_creation,
                        "lat": lat,
                        "lon": lon
                    })
                    
                    # Inscription directe dans la session racine pour SQLite / Supabase
                    st.session_state["nom_producteur"] = nom_prenoms.strip()
                    st.session_state["code_producteur"] = code_national.strip()
                    st.session_state["superficie"] = superficie
                    
                    st.session_state.etape_pdc = 3
                    st.rerun()



    # ---------------------------------------------------------
    # ÉTAPE 3 : DONNÉES SOCIO-DÉMOGRAPHIQUES (FICHE 1)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 3:
        st.subheader("Étape 3/15 : Données Socio-démographiques (Fiche 1)")
        st.info("Informations sur les membres du ménage et les actifs familiaux/travailleurs")

        nom_membre = st.text_input("Nom et Prénoms du membre du ménage")
        statut_famille = st.selectbox("Statut/Famille (Lien de parenté)", ["1. Chef de ménage", "2. Conjoint", "3. Enfant", "4. Autre"])
        statut_plantation = st.selectbox("Statut/Plantation", ["1. Aucun", "2. Propriétaire", "3. Gérant", "4. MO permanent", "5. MO Temporaire"])
        statut_scolaire = st.selectbox("Statut Scolaire", ["1. Scolarisé", "2. Déscolarisé"])
        contact_membre = st.text_input("Contact (Téléphone)")
        annee_naissance = st.number_input("Année de naissance", min_value=1930, max_value=2026, value=1990)
        sexe = st.radio("Sexe", ["M", "F"], horizontal=True)
        niveau_instruction = st.selectbox("Niveau d'instruction", ["1. Aucun", "2. Préscolaire", "3. Primaire", "4. Secondaire", "5. Supérieur", "6. Autres"])
        categorie_ethnique = st.selectbox("Catégorie ethnique", ["1. Autochtone", "2. Allochtone", "3. Allogène"])

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 2
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True):
                st.session_state.reponses_pdc.update({
                    "nom_membre": nom_membre, "statut_famille": statut_famille,
                    "statut_plantation": statut_plantation, "statut_scolaire": statut_scolaire,
                    "contact_membre": contact_membre, "annee_naissance": annee_naissance,
                    "sexe": sexe, "niveau_instruction": niveau_instruction,
                    "categorie_ethnique": categorie_ethnique
                })
                st.session_state.etape_pdc = 4
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 4 : DIAGNOSTIC DES CULTURES, ÉQUIPEMENTS & ARBRES D'OMBRAGE
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 4:
        st.subheader("Étape 4/15 : Données sur les Cultures, Équipements & Agroforesterie")

        # =========================================================
        # 1. DEFINITION DES CALLBACKS D'EDITION SECURISEE
        # =========================================================
        
        def apply_editor_changes(key_editor, key_state_df):
            """Applique proprement les deltas de st.data_editor au DataFrame en session_state."""
            changes = st.session_state.get(key_editor, {})
            df = st.session_state[key_state_df].copy()

            # 1. Modifications de cellules
            for row_idx_str, row_changes in changes.get("edited_rows", {}).items():
                row_idx = int(row_idx_str)
                for col_name, new_val in row_changes.items():
                    if col_name in df.columns:
                        df.iat[row_idx, df.columns.get_loc(col_name)] = new_val

            # 2. Ajouts de lignes
            for new_row in changes.get("added_rows", {}):
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # 3. Suppressions de lignes
            deleted_indices = changes.get("deleted_rows", [])
            if deleted_indices:
                df = df.drop(index=deleted_indices).reset_index(drop=True)

            st.session_state[key_state_df] = df

        def update_cultures():
            apply_editor_changes("editor_cultures", "df_cultures_data")

        def update_equipements():
            apply_editor_changes("editor_equipements", "df_equipements_data")

        def update_arbres():
            apply_editor_changes("editor_arbres", "df_arbres_data")

        # =========================================================
        # 2. INITIALISATION DES DATAFRAMES (SESSION STATE)
        # =========================================================

        if "df_cultures_data" not in st.session_state:
            init_cult = st.session_state.reponses_pdc.get("tableau_cultures", [
                {"Culture": "Cacao - Parcelle 1", "Superficie (ha)": 1.5, "Année création": 2012, "Précédent cultural": "Forêt", "Origine matériel": "CNRA / Certifié", "En production": "OUI"},
                {"Culture": "Cacao - Parcelle 2", "Superficie (ha)": 1.0, "Année création": 2018, "Précédent cultural": "Friche", "Origine matériel": "Tout-venant", "En production": "OUI"},
                {"Culture": "Hévéa", "Superficie (ha)": 0.0, "Année création": 2020, "Précédent cultural": "Savane", "Origine matériel": "Privé", "En production": "NON"},
                {"Culture": "Palmier à huile", "Superficie (ha)": 0.0, "Année création": 2021, "Précédent cultural": "Friche", "Origine matériel": "Privé", "En production": "NON"},
                {"Culture": "Vivrier (Manioc/Maïs)", "Superficie (ha)": 0.5, "Année création": 2023, "Précédent cultural": "Friche", "Origine matériel": "Local", "En production": "OUI"},
            ])
            st.session_state.df_cultures_data = pd.DataFrame(init_cult)

        if "df_equipements_data" not in st.session_state:
            init_eq = st.session_state.reponses_pdc.get("tableau_equipements", [
                {"Type": "Matériel de traitement", "Désignation": "Pulvérisateur", "Quantité": 1, "Année d'acquisition": 2021, "Coût (FCFA)": 35000, "État": "Bon"},
                {"Type": "Matériel de traitement", "Désignation": "Atomiseur", "Quantité": 0, "Année d'acquisition": 2020, "Coût (FCFA)": 0, "État": "Mauvais"},
                {"Type": "Matériel de transport", "Désignation": "Brouette / Charette", "Quantité": 2, "Année d'acquisition": 2022, "Coût (FCFA)": 45000, "État": "Acceptable"},
                {"Type": "Moyen de déplacement", "Désignation": "Moto terrain", "Quantité": 1, "Année d'acquisition": 2019, "Coût (FCFA)": 450000, "État": "Acceptable"},
            ])
            st.session_state.df_equipements_data = pd.DataFrame(init_eq)

        if "df_arbres_data" not in st.session_state:
            init_arb = st.session_state.reponses_pdc.get("tableau_arbres", [
                {"Espèce": "Akpi", "Nombre": 1, "Latitude": 6.020668, "Longitude": -4.357132, "Statut": "Préservé", "Avantages Cacaoyère": "1. Ombrage / 2. Fertilité sol", "Usage": "Alimentaire / Bois", "Décision": "A maintenir", "Remarque": ""},
                {"Espèce": "Fraqué", "Nombre": 1, "Latitude": 6.020664, "Longitude": -4.356949, "Statut": "Préservé", "Avantages Cacaoyère": "1. Ombrage / 3. Protection érosion", "Usage": "Bois d'œuvre", "Décision": "A éliminer", "Remarque": "Situé à 1,5m d'un autre arbre"},
                {"Espèce": "Fromager", "Nombre": 1, "Latitude": 6.020614, "Longitude": -4.356902, "Statut": "Préservé", "Avantages Cacaoyère": "1. Ombrage", "Usage": "Bois d'œuvre", "Décision": "A maintenir", "Remarque": ""},
            ])
            st.session_state.df_arbres_data = pd.DataFrame(init_arb)

        # =========================================================
        # 3. TABLEAU : DONNÉES SUR LES CULTURES
        # =========================================================
        st.markdown("### 🌾 1. Données sur les cultures et parcelles")
        st.caption("Renseignez l'ensemble des parcelles cacaoyères et des autres spéculations sur l'exploitation.")

        st.data_editor(
            st.session_state.df_cultures_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Culture": st.column_config.SelectboxColumn("Culture / Parcelle", options=["Cacao - Parcelle 1", "Cacao - Parcelle 2", "Cacao - Parcelle 3", "Hévéa", "Palmier à huile", "Vivrier (Manioc/Maïs)", "Banane / Plantain", "Autre"], required=True),
                "Superficie (ha)": st.column_config.NumberColumn("Superficie (ha)", min_value=0.0, step=0.1, format="%.2f ha"),
                "Année création": st.column_config.NumberColumn("Année de création", min_value=1950, max_value=2026, step=1),
                "Précédent cultural": st.column_config.SelectboxColumn("Précédent cultural", options=["Forêt", "Friche", "Savane", "Replantation Cacao", "Culture vivrière"]),
                "Origine matériel": st.column_config.SelectboxColumn("Origine matériel végétal", options=["CNRA / Certifié", "Tout-venant", "Champ voisin", "Privé"]),
                "En production": st.column_config.SelectboxColumn("En production ?", options=["OUI", "NON"]),
            },
            key="editor_cultures",
            on_change=update_cultures
        )

        # Calculs automatiques
        df_cult_current = st.session_state.df_cultures_data
        superficie_totale_cacao = 0.0
        superficie_autres = 0.0

        if not df_cult_current.empty and "Culture" in df_cult_current.columns:
            sup_series = pd.to_numeric(df_cult_current.get("Superficie (ha)"), errors="coerce").fillna(0.0)
            mask_cacao = df_cult_current["Culture"].astype(str).str.contains("Cacao", case=False, na=False)
            superficie_totale_cacao = float(sup_series[mask_cacao].sum())
            superficie_autres = float(sup_series[~mask_cacao].sum())

        col_c1, col_c2, col_c3 = st.columns(3)
        col_c1.metric("Superficie Cacao Totale", f"{superficie_totale_cacao:.2f} ha")
        col_c2.metric("Autres Spéculations", f"{superficie_autres:.2f} ha")
        col_c3.metric("Diversification Spéculative", "Élevée" if superficie_autres > 0 else "Nulle")

        st.markdown("---")

        # =========================================================
        # 4. TABLEAU : MATÉRIEL AGRICOLE ET ÉQUIPEMENTS
        # =========================================================
        st.markdown("### 🛠️ 2. Matériel agricole et équipements")
        st.caption("Inventaire des équipements de pulvérisation, transport et déplacement.")

        st.data_editor(
            st.session_state.df_equipements_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Type": st.column_config.SelectboxColumn("Type", options=["Matériel de traitement", "Matériel de transport", "Moyen de déplacement", "Petit outillage"]),
                "Désignation": st.column_config.TextColumn("Désignation"),
                "Quantité": st.column_config.NumberColumn("Quantité", min_value=0, step=1),
                "Année d'acquisition": st.column_config.NumberColumn("Année d'acquisition", min_value=1980, max_value=2026, step=1),
                "Coût (FCFA)": st.column_config.NumberColumn("Coût d'achat (FCFA)", min_value=0, step=5000, format="%d FCFA"),
                "État": st.column_config.SelectboxColumn("État fonctionnel", options=["Bon", "Acceptable", "Mauvais"]),
            },
            key="editor_equipements",
            on_change=update_equipements
        )

        # Calculs équipements
        df_eq_current = st.session_state.df_equipements_data
        valeur_equipements = 0.0
        nb_pulverisateurs = 0

        if not df_eq_current.empty:
            qte_series = pd.to_numeric(df_eq_current.get("Quantité"), errors="coerce").fillna(0)
            cout_series = pd.to_numeric(df_eq_current.get("Coût (FCFA)"), errors="coerce").fillna(0)
            valeur_equipements = float((qte_series * cout_series).sum())

            if "Désignation" in df_eq_current.columns and "État" in df_eq_current.columns:
                mask_pulve = (
                    df_eq_current["Désignation"].astype(str).str.contains("Pulvérisateur|Atomiseur", case=False, na=False)
                ) & (df_eq_current["État"].astype(str) != "Mauvais")
                nb_pulverisateurs = int(qte_series[mask_pulve].sum())

        col_eq1, col_eq2 = st.columns(2)
        col_eq1.metric("Valeur estimée du parc (FCFA)", f"{valeur_equipements:,.0f} FCFA")
        col_eq2.metric("Matériel de traitement opérationnel", f"{nb_pulverisateurs} unité(s)", delta="Insuffisant" if nb_pulverisateurs == 0 else "Opérationnel")

        st.markdown("---")

        # =========================================================
        # 5. TABLEAU : DIAGNOSTIC DES ARBRES D'OMBRAGE
        # =========================================================
        st.markdown("### 🌳 3. Diagnostic des arbres d'ombrage et associés")
        st.caption("Relevé de la composante agroforestière (Nombre, localisation, avantages et décision d'aménagement).")

        st.data_editor(
            st.session_state.df_arbres_data,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Espèce": st.column_config.TextColumn("Espèce / Nom d'arbre", required=True),
                "Nombre": st.column_config.NumberColumn("Nombre de pieds", min_value=1, step=1, required=True),
                "Latitude": st.column_config.NumberColumn("Latitude GPS", format="%.6f"),
                "Longitude": st.column_config.NumberColumn("Longitude GPS", format="%.6f"),
                "Statut": st.column_config.SelectboxColumn("Statut", options=["Préservé", "Introduit / Planté", "Spontané"]),
                "Avantages Cacaoyère": st.column_config.SelectboxColumn(
                    "Avantages pour la cacaoyère",
                    options=[
                        "1. Ombrage",
                        "2. Fertilité du sol",
                        "3. Protection contre l'érosion",
                        "4. Maintien de l'humidité",
                        "5. Lutte contre l'enherbement",
                    ],
                ),
                "Usage": st.column_config.SelectboxColumn("Usage principal", options=["Alimentaire", "Médicinale", "Protection des cacaoyers", "Bois d'œuvre", "Bois de chauffage"]),
                "Décision": st.column_config.SelectboxColumn("Action recommandée", options=["A maintenir", "A éliminer", "A élaguer"], required=True),
                "Remarque": st.column_config.TextColumn("Remarques / Distances"),
            },
            key="editor_arbres",
            on_change=update_arbres
        )

        # Calculs agroforestiers
        df_arb_current = st.session_state.df_arbres_data
        total_arbres = 0
        arbres_conserves = 0

        if not df_arb_current.empty:
            nb_arb_series = pd.to_numeric(df_arb_current.get("Nombre"), errors="coerce").fillna(0)
            total_arbres = int(nb_arb_series.sum())

            if "Décision" in df_arb_current.columns:
                mask_conserves = df_arb_current["Décision"].isin(["A maintenir", "A élaguer"])
                arbres_conserves = int(nb_arb_series[mask_conserves].sum())

        arbres_par_ha = (total_arbres / superficie_totale_cacao) if superficie_totale_cacao > 0 else 0.0
        densite_conservee_ha = (arbres_conserves / superficie_totale_cacao) if superficie_totale_cacao > 0 else 0.0

        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        col_a1.metric("Total arbres répertoriés", f"{total_arbres} pieds")
        col_a2.metric("Arbres conservés/élagués", f"{arbres_conserves} pieds")
        col_a3.metric("Densité brute", f"{arbres_par_ha:.1f} arb/ha")
        col_a4.metric("Densité conservée", f"{densite_conservee_ha:.1f} arb/ha")

        # Conformité agroforestière / RDUE
        if 18 <= densite_conservee_ha <= 40:
            st.success(f"✅ **Densité agroforestière conforme (RDUE/CCC)** : {densite_conservee_ha:.1f} arbres/ha conservés (Cible : 18-40 arbres/ha).")
        elif densite_conservee_ha < 18:
            st.warning(f"⚠️ **Ombrage déficitaire pour la norme RDUE** : {densite_conservee_ha:.1f} arbres/ha conservés. Un reboisement complémentaire est requis.")
        else:
            st.error(f"⚠️ **Ombrage excessif** : {densite_conservee_ha:.1f} arbres/ha conservés. Risque d'humidité excessive et de développement de la Pourriture brune. Élagage recommandé.")

        # =========================================================
        # SAUVEGARDE ET NAVIGATION
        # =========================================================
        def sauvegarder_etape_4():
            st.session_state.reponses_pdc.update({
                "tableau_cultures": st.session_state.df_cultures_data.to_dict("records"),
                "superficie_totale_cacao": superficie_totale_cacao,
                "superficie_autres_cultures": superficie_autres,
                "tableau_equipements": st.session_state.df_equipements_data.to_dict("records"),
                "valeur_total_equipements": valeur_equipements,
                "nb_pulverisateurs_operationnels": nb_pulverisateurs,
                "tableau_arbres": st.session_state.df_arbres_data.to_dict("records"),
                "total_arbres_ombrage": total_arbres,
                "arbres_conserves": arbres_conserves,
                "densite_arbres_ha": arbres_par_ha,
                "densite_conservee_ha": densite_conservee_ha,
            })

        st.markdown("---")
        col_nav1, col_nav2 = st.columns([1, 1])

        with col_nav1:
            if st.button("⬅️ Précédent", use_container_width=True):
                sauvegarder_etape_4()
                st.session_state.etape_pdc = 3
                st.rerun()

        with col_nav2:
            if st.button("Suivant ➡️", use_container_width=True, type="primary"):
                sauvegarder_etape_4()
                st.session_state.etape_pdc = 5
                st.rerun()



        # ---------------------------------------------------------
    # ÉTAPE 5 : DENSITÉ ET RENDEMENT (FICHE 3 - PARTIE 1)
    # ---------------------------------------------------------
    if st.session_state.etape_pdc == 5:
        st.subheader("Étape 5/15 : Densité et Rendement (Fiche 3)")

        st.markdown("### 📐 1. Densité des cacaoyers")
        if 'df_densite_cacao' not in st.session_state:
            st.session_state.df_densite_cacao = [
                {"Carré": "Carré 1", "Nombre cacaoyers": 12, "Nb moyen de tiges/cacaoyer": 1.0},
                {"Carré": "Carré 2", "Nombre cacaoyers": 11, "Nb moyen de tiges/cacaoyer": 1.2},
                {"Carré": "Carré 3", "Nombre cacaoyers": 13, "Nb moyen de tiges/cacaoyer": 1.0},
                {"Carré": "Carré 4", "Nombre cacaoyers": 10, "Nb moyen de tiges/cacaoyer": 1.1}
            ]

        densite_df = st.data_editor(st.session_state.df_densite_cacao, num_rows="dynamic", key="editor_densite", use_container_width=True)

        if len(densite_df) > 0:
            df_temp = pd.DataFrame(densite_df)
            moyenne_arbres_carre = df_temp["Nombre cacaoyers"].mean() if "Nombre cacaoyers" in df_temp else 0
            densite_estimee = moyenne_arbres_carre * 100
            st.success(f"📊 **Densité estimée :** `{densite_estimee:.0f} cacaoyers / ha`")
        else:
            densite_estimee = 0

        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.etape_pdc = 4
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True, type="primary"):
                st.session_state.reponses_pdc.update({
                    "donnees_densite": densite_df, 
                    "densite_calculee_ha": densite_estimee
                })
                st.session_state.etape_pdc = 6
                st.rerun()


    # ---------------------------------------------------------
    # ÉTAPE 6 : ÉTAT SANITAIRE, SOL, RÉCOLTE & ENGRAIS (FICHE 3)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 6:
        st.subheader("Étape 6/15 : État Sanitaire, Sol, Récolte & Engrais (Fiche 3)")

        # =========================================================
        # 1. FONCTION DE CALLBACK GÉNÉRIQUE POUR LES ÉDITEURS
        # =========================================================
        def apply_editor_changes(key_editor, key_state_df):
            """Applique proprement les deltas de st.data_editor au DataFrame en session_state."""
            changes = st.session_state.get(key_editor, {})
            df = st.session_state[key_state_df].copy()

            # 1. Modifications de cellules
            for row_idx_str, row_changes in changes.get("edited_rows", {}).items():
                row_idx = int(row_idx_str)
                for col_name, new_val in row_changes.items():
                    if col_name in df.columns:
                        df.iat[row_idx, df.columns.get_loc(col_name)] = new_val

            # 2. Ajouts de lignes
            for new_row in changes.get("added_rows", {}):
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # 3. Suppressions de lignes
            deleted_indices = changes.get("deleted_rows", [])
            if deleted_indices:
                df = df.drop(index=deleted_indices).reset_index(drop=True)

            st.session_state[key_state_df] = df

        # Callbacks dédiés
        def update_sante():
            apply_editor_changes("editor_sante", "df_sante_cacao")

        def update_sol():
            apply_editor_changes("editor_sol", "df_sol_caract")

        def update_engrais():
            apply_editor_changes("editor_engrais", "df_engrais")

        def update_phyto():
            apply_editor_changes("editor_phyto", "df_phyto")

        # =========================================================
        # 2. INITIALISATION ET GARANTIE DES DATAFRAMES DANS SESSION STATE
        # =========================================================
        # S'assure que les variables de session sont TOUJOURS des DataFrames
        if "df_sante_cacao" not in st.session_state or not isinstance(st.session_state.df_sante_cacao, pd.DataFrame):
            init_sante = st.session_state.reponses_pdc.get("sante_cacaoyere", [
                {"Maladies / Ravageurs": "Attaques de mirides", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "Présence de gourmands", "Valeur": "1. Aucun", "Observations P.": ""},
                {"Maladies / Ravageurs": "Attaques de Pourriture Brune", "Sévérité": "2. Faible", "Observations": "", "Paramètres": "Présence de cabosses momifiées", "Valeur": "2. Faible", "Observations P.": ""},
                {"Maladies / Ravageurs": "Présence de plantes épiphytes", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "Présence de loranthus", "Valeur": "1. Aucun", "Observations P.": ""},
                {"Maladies / Ravageurs": "Attaque Foreurs", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "Enherbedement", "Valeur": "3. moyen", "Observations P.": ""},
                {"Maladies / Ravageurs": "Attaque CSSVD", "Sévérité": "1. Aucun", "Observations": "", "Paramètres": "", "Valeur": "", "Observations P.": ""}
            ])
            st.session_state.df_sante_cacao = pd.DataFrame(init_sante)

        if "df_sol_caract" not in st.session_state or not isinstance(st.session_state.df_sol_caract, pd.DataFrame):
            init_sol = st.session_state.reponses_pdc.get("caracteristiques_sol", [
                {"Éléments d'observation (A)": "Couvert végétal", "Valeur A": "2. moyen", "Obs A": "", "Éléments d'observation (B)": "Existence de zones érodées", "Valeur B": "2. Non", "Obs B": "Ravinements..."},
                {"Éléments d'observation (A)": "Présence de Matière organique", "Valeur A": "1. beaucoup", "Obs A": "", "Éléments d'observation (B)": "Existence de zones à risque d'érosion", "Valeur B": "2. Non", "Obs B": "Pente..."},
                {"Éléments d'observation (A)": "Profondeur", "Valeur A": "2. moyen", "Obs A": "", "Éléments d'observation (B)": "", "Valeur B": "", "Obs B": ""},
                {"Éléments d'observation (A)": "Texture", "Valeur A": "2. moyen", "Obs A": "", "Éléments d'observation (B)": "", "Valeur B": "", "Obs B": ""}
            ])
            st.session_state.df_sol_caract = pd.DataFrame(init_sol)

        if "df_engrais" not in st.session_state or not isinstance(st.session_state.df_engrais, pd.DataFrame):
            init_engrais = st.session_state.reponses_pdc.get("utilisation_engrais", [
                {
                    "Type d'engrais": "Minéraux",
                    "Nom commercial / Formule": "NPK 0-23-19",
                    "Quantité/an": "200 kg",
                    "Période d'apport": "Mai",
                    "Mode d'apport": "Au sol",
                    "Applicateur": "1. Producteur"
                }
            ])
            st.session_state.df_engrais = pd.DataFrame(init_engrais)

        if "df_phyto" not in st.session_state or not isinstance(st.session_state.df_phyto, pd.DataFrame):
            init_phyto = st.session_state.reponses_pdc.get("produits_phytosanitaires", [
                {
                    "Type de produits": "Fongicide",
                    "Nom commercial / Formule": "Ridomil Gold",
                    "Quantité / traitement": "50g/15L",
                    "Période de traitement": "Juin-Juillet",
                    "Mode d'apport": "Pulvérisateur",
                    "Applicateur": "2. Applicateur"
                }
            ])
            st.session_state.df_phyto = pd.DataFrame(init_phyto)

        # =========================================================
        # 6.1 ÉTAT VÉGÉTATIF ET SANITAIRE DES CACAOYERS
        # =========================================================
        st.markdown("### 🐛 1. État végétatif et sanitaire")

        st.data_editor(
            st.session_state.df_sante_cacao,
            num_rows="dynamic",
            key="editor_sante",
            column_config={
                "Sévérité": st.column_config.SelectboxColumn("Sévérité", options=["1. Aucun", "2. Faible", "3. Moyen", "4. Fort"]),
                "Valeur": st.column_config.SelectboxColumn("Valeur", options=["1. Aucun", "2. Faible", "3. moyen", "4. Fort"])
            },
            use_container_width=True,
            on_change=update_sante
        )

        # --- DIAGNOSTIC AUTOMATIQUE 6.1 (SANTE & VEGETATIF) ---
        df_sante = st.session_state.df_sante_cacao
        sev_map = {"1. Aucun": 0, "2. Faible": 1, "3. Moyen": 2, "3. moyen": 2, "4. Fort": 3}

        # Extraction sécurisée des colonnes
        severites = df_sante["Sévérité"] if "Sévérité" in df_sante.columns else []
        valeurs = df_sante["Valeur"] if "Valeur" in df_sante.columns else []

        score_maladies = sum([sev_map.get(str(x), 0) for x in severites if pd.notna(x)])
        score_entretien = sum([sev_map.get(str(x), 0) for x in valeurs if pd.notna(x)])
        score_total_sante = score_maladies + score_entretien

        cssvd_detecte = any("CSSVD" in str(row.get("Maladies / Ravageurs", "")) and row.get("Sévérité") != "1. Aucun" for _, row in df_sante.iterrows())
        gourmands_forts = any("gourmands" in str(row.get("Paramètres", "")).lower() and row.get("Valeur") in ["3. Moyen", "3. moyen", "4. Fort"] for _, row in df_sante.iterrows())
        loranthus_present = any("loranthus" in str(row.get("Paramètres", "")).lower() and row.get("Valeur") != "1. Aucun" for _, row in df_sante.iterrows())

        st.markdown("#### 🩺 Diagnostic Phytosanitaire & Entretien")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Pression Sanitaire", f"{score_maladies} pts / 15")
        col_s2.metric("Niveau d'Enherbement / Gourmands", f"{score_entretien} pts / 12")
        
        if score_total_sante <= 3:
            col_s3.success("🟢 État sanitaire global : EXCELLENT")
        elif score_total_sante <= 7:
            col_s3.warning("🟡 État sanitaire global : MODÉRÉ")
        else:
            col_s3.error("🔴 État sanitaire global : CRITIQUE")

        if cssvd_detecte:
            st.error("🚨 **ALERTE CSSVD (Swollen Shoot)** : Présence suspectée ! Isolement immédiat et arrachage des pieds infectés préconisés selon le protocole national.")
        if gourmands_forts or loranthus_present:
            st.warning("⚠️ **Recommandation Taille** : Présence importante de gourmands ou Loranthus. Prévoir une séance d'égourmandage et de déparasitage pour réduire la compétition nutritive.")

        st.markdown("---")

        # =========================================================
        # 6.2 CARACTÉRISTIQUES PHYSIQUES DU SOL
        # =========================================================
        st.markdown("### 🏔️ 2. État et caractéristiques du sol")
        
        default_topos = st.session_state.reponses_pdc.get("toposequence", "Plateau")
        topos_options = ["Plateau", "Haut de versant", "Mi-versant", "Bas de versant", "Bas-fond"]
        topos_index = topos_options.index(default_topos) if default_topos in topos_options else 0
        
        toposequence = st.selectbox("Positionnement dans la toposéquence", topos_options, index=topos_index)

        st.data_editor(
            st.session_state.df_sol_caract,
            num_rows="dynamic",
            key="editor_sol",
            column_config={
                "Valeur A": st.column_config.SelectboxColumn("Valeur (A)", options=["1. beaucoup", "2. moyen", "3. Faible"]),
                "Valeur B": st.column_config.SelectboxColumn("Valeur (B)", options=["1. Oui", "2. Non"])
            },
            use_container_width=True,
            on_change=update_sol
        )

        # --- DIAGNOSTIC AUTOMATIQUE 6.2 (SOL ET TOPOSEQUENCE) ---
        df_sol = st.session_state.df_sol_caract
        
        zone_erodee = any(row.get("Valeur B") == "1. Oui" for _, row in df_sol.iterrows() if "zones érodées" in str(row.get("Éléments d'observation (B)", "")))
        risque_erosion = any(row.get("Valeur B") == "1. Oui" for _, row in df_sol.iterrows() if "risque d'érosion" in str(row.get("Éléments d'observation (B)", "")))
        faible_mo = any(row.get("Valeur A") == "3. Faible" for _, row in df_sol.iterrows() if "Matière organique" in str(row.get("Éléments d'observation (A)", "")))

        st.markdown("#### 🌱 Diagnostic d'Aptitude du Sol")
        col_sol1, col_sol2 = st.columns(2)
        
        if toposequence in ["Bas-fond", "Bas de versant"]:
            col_sol1.warning(f"📍 Toposéquence ({toposequence}) : Risque d'hydromorphie / Asphyxie racinaire en saison des pluies. Drainages à prévoir.")
        else:
            col_sol1.success(f"📍 Toposéquence ({toposequence}) : Sol bien drainé a priori.")

        if zone_erodee or risque_erosion:
            col_sol2.error("⚠️ Risque d'érosion ÉLEVÉ : Aménagement en courbes de niveau ou enherbement contrôlé recommandé.")
        elif faible_mo:
            col_sol2.warning("⚠️ Matière organique FAIBLE : Prévoir un apport de compost ou maintien des résidus de taille au sol.")
        else:
            col_sol2.success("✅ Conservation du sol & fertilité satisfaisantes.")

        st.markdown("---")

        # =========================================================
        # 6.3 PRATIQUES DE RÉCOLTE ET POST-RÉCOLTE
        # =========================================================
        st.markdown("### 🧺 3. Pratiques de récolte et post-récolte")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            freq_recolte = st.number_input("Fréquence des récoltes (jours entre 2 récoltes)", min_value=1, max_value=60, value=int(st.session_state.reponses_pdc.get("frequence_recolte_jours", 14)))
            temps_ecabossage = st.number_input("Temps entre récolte et écabossage (jours)", min_value=0, max_value=15, value=int(st.session_state.reponses_pdc.get("temps_ecabossage_jours", 2)))
            duree_fermentation = st.number_input("Durée de la fermentation (jours)", min_value=1, max_value=10, value=int(st.session_state.reponses_pdc.get("duree_fermentation_jours", 6)))
        
        with col_p2:
            mode_options = ["1. Bâche en plastique", "2. Feuilles de bananier", "3. Bac de fermentation", "4. Autre (à préciser)"]
            default_mode = st.session_state.reponses_pdc.get("mode_fermentation", mode_options[0])
            mode_idx = mode_options.index(default_mode) if default_mode in mode_options else 0
            mode_fermentation = st.selectbox("Mode de fermentation", mode_options, index=mode_idx)

            sechage_options = ["1. Sur goudron", "2. Sur aire cimentée", "3. Sur bâche en plastique à terre", "4. Sur claie", "5. Autre (à préciser)"]
            default_sechage = st.session_state.reponses_pdc.get("methode_sechage", sechage_options[3])
            sechage_idx = sechage_options.index(default_sechage) if default_sechage in sechage_options else 3
            methode_sechage = st.selectbox("Méthodes de séchage", sechage_options, index=sechage_idx)

        # Diagnostic qualité post-récolte
        st.markdown("#### 🍫 Diagnostic Qualité Post-Récolte")
        if duree_fermentation < 5:
            st.warning("⚠️ Fermentation courte (< 5 jours) : Risque de fèves violettes, d'amertume et d'acidité élevée.")
        elif duree_fermentation > 7:
            st.warning("⚠️ Fermentation longue (> 7 jours) : Risque de moisissures internes et d'arômes défectueux.")
        else:
            st.success("✅ Durée de fermentation optimale (5 à 7 jours).")

        if "goudron" in methode_sechage.lower() or "bâche en plastique à terre" in methode_sechage.lower():
            st.error("🚫 Séchage non conforme : Le séchage à terre ou sur goudron altère la qualité des fèves et entraîne un risque de contamination PAH/HAP.")
        elif "claie" in methode_sechage.lower():
            st.success("✅ Séchage sur claie : Conforme aux standards d'exportation de qualité supérieure.")

        st.markdown("---")

        # =========================================================
        # 6.4 UTILISATION DES ENGRAIS ET AMENDEMENTS
        # =========================================================
        st.markdown("### 🧪 4. Utilisation des engrais / amendements")

        st.data_editor(
            st.session_state.df_engrais,
            num_rows="dynamic",
            key="editor_engrais",
            column_config={
                "Type d'engrais": st.column_config.SelectboxColumn("Type d'engrais", options=["Minéraux", "Organiques", "Autres"]),
                "Mode d'apport": st.column_config.SelectboxColumn("Mode d'apport", options=["Foliaire", "Au sol"]),
                "Applicateur": st.column_config.SelectboxColumn("Applicateur", options=["1. Producteur", "2. Applicateur"])
            },
            use_container_width=True,
            on_change=update_engrais
        )

        st.markdown("---")

        # =========================================================
        # 6.5 UTILISATION DES PRODUITS PHYTOSANITAIRES
        # =========================================================
        st.markdown("### 🛡️ 5. Produits phytosanitaires utilisés")

        st.data_editor(
            st.session_state.df_phyto,
            num_rows="dynamic",
            key="editor_phyto",
            column_config={
                "Type de produits": st.column_config.SelectboxColumn("Type de produits", options=["Insecticide", "Fongicide", "Herbicide", "Nematicide"]),
                "Mode d'apport": st.column_config.SelectboxColumn("Mode d'apport", options=["Atomiseur", "Pulvérisateur"]),
                "Applicateur": st.column_config.SelectboxColumn("Applicateur", options=["1. Producteur", "2. Applicateur"])
            },
            use_container_width=True,
            on_change=update_phyto
        )

        st.markdown("---")

        # =========================================================
        # 6.6 GESTION DES EMBALLAGES VIDES
        # =========================================================
        st.markdown("### 🗑️ 6. Gestion des emballages vides")
        gestion_emballages = st.text_area(
            "Que faites-vous des emballages après traitement/application ?",
            value=st.session_state.reponses_pdc.get("gestion_emballages", ""),
            placeholder="Exemple : Rincés 3 fois, percés et ramassés par le programme de collecte de la coopérative...",
            height=100
        )

        # =========================================================
        # NAVIGATION ENTRE ÉTAPES ET SAUVEGARDE
        # =========================================================
        def sauvegarder_etape_6():
            st.session_state.reponses_pdc.update({
                "sante_cacaoyere": st.session_state.df_sante_cacao.to_dict("records"),
                "toposequence": toposequence,
                "caracteristiques_sol": st.session_state.df_sol_caract.to_dict("records"),
                "frequence_recolte_jours": freq_recolte,
                "temps_ecabossage_jours": temps_ecabossage,
                "duree_fermentation_jours": duree_fermentation,
                "mode_fermentation": mode_fermentation,
                "methode_sechage": methode_sechage,
                "utilisation_engrais": st.session_state.df_engrais.to_dict("records"),
                "produits_phytosanitaires": st.session_state.df_phyto.to_dict("records"),
                "gestion_emballages": gestion_emballages,
                "score_pression_sanitaire": score_maladies,
                "score_entretien_parcelle": score_entretien
            })

        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                sauvegarder_etape_6()
                st.session_state.etape_pdc = 5
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True, type="primary"):
                sauvegarder_etape_6()
                st.session_state.etape_pdc = 7
                st.rerun()


    # ---------------------------------------------------------
    # ÉTAPE 7 : PARTIE D - DONNÉES SOCIO-ÉCONOMIQUES (FICHE 4)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 7:
        st.subheader("Étape 7/15 : Données Socio-économiques (Fiche 4)")

        # =========================================================
        # 1. FONCTION DE CALLBACK GÉNÉRIQUE ET FONCTIONS DÉDIÉES
        # =========================================================
        def apply_editor_changes(key_editor, key_state_df):
            """Applique proprement les deltas de st.data_editor au DataFrame en session_state."""
            changes = st.session_state.get(key_editor, {})
            df = st.session_state[key_state_df].copy()

            # 1. Modifications de cellules
            for row_idx_str, row_changes in changes.get("edited_rows", {}).items():
                row_idx = int(row_idx_str)
                for col_name, new_val in row_changes.items():
                    if col_name in df.columns:
                        df.iat[row_idx, df.columns.get_loc(col_name)] = new_val

            # 2. Ajouts de lignes
            for new_row in changes.get("added_rows", {}):
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # 3. Suppressions de lignes
            deleted_indices = changes.get("deleted_rows", [])
            if deleted_indices:
                df = df.drop(index=deleted_indices).reset_index(drop=True)

            st.session_state[key_state_df] = df

        def update_financement():
            apply_editor_changes("editor_financement", "df_financement")

        def update_prod_historique():
            apply_editor_changes("editor_prod_historique", "df_prod_historique")

        def update_autres_revenus():
            apply_editor_changes("editor_autres_revenus", "df_autres_revenus")

        def update_depenses():
            apply_editor_changes("editor_depenses", "df_depenses")

        def update_main_oeuvre():
            apply_editor_changes("editor_main_oeuvre", "df_main_oeuvre")

        # =========================================================
        # 2. INITIALISATION ET GARANTIE DES DATAFRAMES DANS SESSION STATE
        # =========================================================
        if "df_financement" not in st.session_state or not isinstance(st.session_state.df_financement, pd.DataFrame):
            init_financement = st.session_state.reponses_pdc.get("financement", [
                {"Service": "Mobile Money", "Compte d'épargne (Oui/Non)": "Oui", "Demande de crédit (Oui/Non)": "Non", "Crédit obtenu (Oui/Non)": "Non", "Montant (FCFA)": 0},
                {"Service": "Microfinance", "Compte d'épargne (Oui/Non)": "Non", "Demande de crédit (Oui/Non)": "Non", "Crédit obtenu (Oui/Non)": "Non", "Montant (FCFA)": 0},
                {"Service": "Banque", "Compte d'épargne (Oui/Non)": "Non", "Demande de crédit (Oui/Non)": "Non", "Crédit obtenu (Oui/Non)": "Non", "Montant (FCFA)": 0}
            ])
            st.session_state.df_financement = pd.DataFrame(init_financement)

        if "df_prod_historique" not in st.session_state or not isinstance(st.session_state.df_prod_historique, pd.DataFrame):
            init_prod_hist = st.session_state.reponses_pdc.get("prod_historique", [
                {"Campagne": "Année N-1", "Production (kg)": 1500, "Prix moyen (FCFA/kg)": 1500},
                {"Campagne": "Année N-2", "Production (kg)": 1200, "Prix moyen (FCFA/kg)": 1000},
                {"Campagne": "Année N-3", "Production (kg)": 1000, "Prix moyen (FCFA/kg)": 900}
            ])
            st.session_state.df_prod_historique = pd.DataFrame(init_prod_hist)

        if "df_autres_revenus" not in st.session_state or not isinstance(st.session_state.df_autres_revenus, pd.DataFrame):
            init_autres_rev = st.session_state.reponses_pdc.get("autres_revenus", [
                {"Source de revenu / Activité": "Vente de vivriers", "Montant estimé/an (FCFA)": 250000, "Observations": ""},
                {"Source de revenu / Activité": "Élevage", "Montant estimé/an (FCFA)": 100000, "Observations": ""}
            ])
            st.session_state.df_autres_revenus = pd.DataFrame(init_autres_rev)

        if "df_depenses" not in st.session_state or not isinstance(st.session_state.df_depenses, pd.DataFrame):
            init_depenses = st.session_state.reponses_pdc.get("depenses_foyer", [
                {"Dépenses": "Scolarité", "Périodicité": "Année", "Montant moyen (FCFA)": 150000},
                {"Dépenses": "Nourriture", "Périodicité": "Mois", "Montant moyen (FCFA)": 50000},
                {"Dépenses": "Santé", "Périodicité": "Année", "Montant moyen (FCFA)": 80000},
                {"Dépenses": "Électricité", "Périodicité": "2 mois", "Montant moyen (FCFA)": 15000},
                {"Dépenses": "Eau courante", "Périodicité": "Mois", "Montant moyen (FCFA)": 5000},
                {"Dépenses": "Charges sociales (Funérailles, fêtes...)", "Périodicité": "Année", "Montant moyen (FCFA)": 100000}
            ])
            st.session_state.df_depenses = pd.DataFrame(init_depenses)

        if "df_main_oeuvre" not in st.session_state or not isinstance(st.session_state.df_main_oeuvre, pd.DataFrame):
            init_mo = st.session_state.reponses_pdc.get("main_oeuvre", [
                {"Travailleur": "Travailleur 1", "Statut": "MO permanente", "Sexe": "M", "Coût annuel (FCFA)": 300000, "Temps de travail / an (jours)": 250},
                {"Travailleur": "Groupe de travail (Entraide)", "Statut": "Non rémunérée (familiale)", "Sexe": "M", "Coût annuel (FCFA)": 0, "Temps de travail / an (jours)": 30}
            ])
            st.session_state.df_main_oeuvre = pd.DataFrame(init_mo)

        # =========================================================
        # 1. COMPTE D'ÉPARGNE ET FINANCEMENT
        # =========================================================
        st.markdown("### 🏦 1. Compte d'épargne et Financement")

        st.data_editor(
            st.session_state.df_financement,
            num_rows="dynamic",
            key="editor_financement",
            column_config={
                "Compte d'épargne (Oui/Non)": st.column_config.SelectboxColumn("Compte d'épargne", options=["Oui", "Non"]),
                "Demande de crédit (Oui/Non)": st.column_config.SelectboxColumn("Demande de crédit", options=["Oui", "Non"]),
                "Crédit obtenu (Oui/Non)": st.column_config.SelectboxColumn("Crédit obtenu", options=["Oui", "Non"]),
                "Montant (FCFA)": st.column_config.NumberColumn("Montant (FCFA)", min_value=0, step=10000, format="%d FCFA")
            },
            use_container_width=True,
            on_change=update_financement
        )

        # --- DIAGNOSTIC AUTOMATIQUE 7.1 (INCLUSION FINANCIÈRE) ---
        df_fin = st.session_state.df_financement
        has_epargne = any(row.get("Compte d'épargne (Oui/Non)") == "Oui" for _, row in df_fin.iterrows())
        credit_obtenu = any(row.get("Crédit obtenu (Oui/Non)") == "Oui" for _, row in df_fin.iterrows())
        montant_total_credit = df_fin["Montant (FCFA)"].sum() if "Montant (FCFA)" in df_fin.columns else 0

        st.markdown("#### 💳 Diagnostic d'Inclusion Financière")
        col_f1, col_f2 = st.columns(2)
        if has_epargne:
            col_f1.success("✅ Accès aux services d'épargne confirmé.")
        else:
            col_f1.warning("⚠️ Absence de compte d'épargne formel : Vulnérabilité accrue aux chocs de trésorerie.")

        if credit_obtenu:
            col_f2.info(f"ℹ️ Crédit obtenu : Total de {montant_total_credit:,.0f} FCFA engagé.")
        else:
            col_f2.write("ℹ️ Aucun crédit bancaire ou microfinance contracté.")

        st.markdown("---")

        # =========================================================
        # 2. PRODUCTION DE CACAO DES 3 DERNIÈRES ANNÉES
        # =========================================================
        st.markdown("### 📦 2. Production de cacao des trois (3) dernières années")

        st.data_editor(
            st.session_state.df_prod_historique,
            num_rows="dynamic",
            key="editor_prod_historique",
            column_config={
                "Production (kg)": st.column_config.NumberColumn("Production (kg)", min_value=0, step=50, format="%d kg"),
                "Prix moyen (FCFA/kg)": st.column_config.NumberColumn("Prix moyen (FCFA/kg)", min_value=0, step=50, format="%d FCFA")
            },
            use_container_width=True,
            on_change=update_prod_historique
        )

        # --- DIAGNOSTIC MULTI-ANNÉES COMPLET (7.2) ---
        df_prod_calc = st.session_state.df_prod_historique.copy()
        
        # S'assurer des colonnes numériques
        prod_col = df_prod_calc["Production (kg)"] if "Production (kg)" in df_prod_calc.columns else pd.Series([0])
        prix_col = df_prod_calc["Prix moyen (FCFA/kg)"] if "Prix moyen (FCFA/kg)" in df_prod_calc.columns else pd.Series([0])
        
        df_prod_calc["Revenu Brut (FCFA)"] = prod_col * prix_col
        
        prod_n1 = prod_col.iloc[0] if len(prod_col) > 0 else 0
        prod_n2 = prod_col.iloc[1] if len(prod_col) > 1 else 0
        prod_n3 = prod_col.iloc[2] if len(prod_col) > 2 else 0

        rev_n1 = df_prod_calc["Revenu Brut (FCFA)"].iloc[0] if len(df_prod_calc) > 0 else 0

        revenu_cacao_dernire_annee = rev_n1
        moyenne_prod_3ans = prod_col.mean() if not prod_col.empty else 0

        # Calcul de la tendance de production (N-3 à N-1)
        evo_prod_pct = ((prod_n1 - prod_n3) / prod_n3 * 100) if prod_n3 > 0 else 0

        st.markdown("#### 📊 Analyse Dynamique de la Production (Historique 3 Ans)")
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        col_h1.metric("Production Année N-1", f"{prod_n1:,.0f} kg", delta=f"{((prod_n1 - prod_n2)/prod_n2*100):+.1f}% vs N-2" if prod_n2 > 0 else None)
        col_h2.metric("Production Année N-2", f"{prod_n2:,.0f} kg", delta=f"{((prod_n2 - prod_n3)/prod_n3*100):+.1f}% vs N-3" if prod_n3 > 0 else None)
        col_h3.metric("Production Année N-3", f"{prod_n3:,.0f} kg")
        col_h4.metric("Moyenne Production (3 ans)", f"{moyenne_prod_3ans:,.0f} kg")

        if evo_prod_pct > 5:
            st.success(f"📈 **Tendance de production positive** : Progression de +{evo_prod_pct:.1f}% sur les 3 dernières campagnes.")
        elif evo_prod_pct < -5:
            st.error(f"📉 **Baisse de production détectée** : Chute de {evo_prod_pct:.1f}% entre N-3 et N-1. Nécessite une analyse du vieillissement des arbres ou des attaques sanitaires.")
        else:
            st.info("➡️ **Production stable** sur les trois dernières années.")

        st.markdown("---")

        # =========================================================
        # 3. SOURCES DE REVENUS AUTRES QUE LE CACAO
        # =========================================================
        st.markdown("### 💰 3. Sources de revenus autres que le cacao")

        st.data_editor(
            st.session_state.df_autres_revenus,
            num_rows="dynamic",
            key="editor_autres_revenus",
            column_config={
                "Montant estimé/an (FCFA)": st.column_config.NumberColumn("Montant estimé/an (FCFA)", min_value=0, step=10000, format="%d FCFA")
            },
            use_container_width=True,
            on_change=update_autres_revenus
        )

        df_autres = st.session_state.df_autres_revenus
        total_autres_revenus = df_autres["Montant estimé/an (FCFA)"].sum() if "Montant estimé/an (FCFA)" in df_autres.columns else 0
        revenu_total_global = revenu_cacao_dernire_annee + total_autres_revenus
        part_cacao = (revenu_cacao_dernire_annee / revenu_total_global * 100) if revenu_total_global > 0 else 0

        st.markdown("#### 🌾 Analyse de Diversification du Revenu")
        col_d1, col_d2 = st.columns(2)
        col_d1.metric("Revenus Hors-Cacao / an", f"{total_autres_revenus:,.0f} FCFA")
        col_d2.metric("Part du Cacao dans le Revenu Total", f"{part_cacao:.1f}%")

        if part_cacao > 85:
            st.warning("⚠️ **Forte dépendance à la monoculture de cacao** (> 85%). Vulnérabilité élevée face aux fluctuations des cours mondiaux.")
        else:
            st.success("✅ **Bonne diversification des revenus** (cultures vivrières, élevage ou services).")

        st.markdown("---")

        # =========================================================
        # 4. DÉPENSES COURANTES DU FOYER
        # =========================================================
        st.markdown("### 🛒 4. Dépenses courantes du foyer")

        st.data_editor(
            st.session_state.df_depenses,
            num_rows="dynamic",
            key="editor_depenses",
            column_config={
                "Périodicité": st.column_config.SelectboxColumn("Périodicité", options=["Mois", "2 mois", "Trimestre", "Semestre", "Année"]),
                "Montant moyen (FCFA)": st.column_config.NumberColumn("Montant (FCFA)", min_value=0, step=5000, format="%d FCFA")
            },
            use_container_width=True,
            on_change=update_depenses
        )

        # Calcul annualisé des dépenses ménagères
        df_dep = st.session_state.df_depenses
        def aux_annualiser(row):
            m = row.get("Montant moyen (FCFA)", 0)
            p = row.get("Périodicité", "Année")
            if p == "Mois": return m * 12
            elif p == "2 mois": return m * 6
            elif p == "Trimestre": return m * 4
            elif p == "Semestre": return m * 2
            return m

        total_depenses_an = df_dep.apply(aux_annualiser, axis=1).sum() if not df_dep.empty else 0
        st.metric("Total Dépenses Foyer Estimées / an", f"{total_depenses_an:,.0f} FCFA")

        st.markdown("---")

        # =========================================================
        # 5. COÛT DE LA MAIN D'ŒUVRE
        # =========================================================
        st.markdown("### 👥 5. Coût et gestion de la main d'œuvre")

        st.data_editor(
            st.session_state.df_main_oeuvre,
            num_rows="dynamic",
            key="editor_main_oeuvre",
            column_config={
                "Statut": st.column_config.SelectboxColumn("Statut de la main d'œuvre", options=["MO permanente", "MO occasionnelle", "Non rémunérée (familiale)"]),
                "Sexe": st.column_config.SelectboxColumn("Sexe", options=["M", "F"]),
                "Coût annuel (FCFA)": st.column_config.NumberColumn("Coût annuel (FCFA)", min_value=0, step=10000, format="%d FCFA"),
                "Temps de travail / an (jours)": st.column_config.NumberColumn("Temps (jours/an)", min_value=0, step=5)
            },
            use_container_width=True,
            on_change=update_main_oeuvre
        )

        df_mo = st.session_state.df_main_oeuvre
        total_cout_mo = df_mo["Coût annuel (FCFA)"].sum() if "Coût annuel (FCFA)" in df_mo.columns else 0
        total_jours_mo = df_mo["Temps de travail / an (jours)"].sum() if "Temps de travail / an (jours)" in df_mo.columns else 0

        st.markdown("#### 👷 Diagnostic de la Main d'Œuvre")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Coût Total Main d'Œuvre / an", f"{total_cout_mo:,.0f} FCFA")
        col_m2.metric("Volume de Travail Annuel", f"{total_jours_mo:,.0f} homme-jours")

        st.markdown("---")

        # =========================================================
        # BILAN FINANCIER GLOBAL CONSOLIDÉ & SAUVEGARDE
        # =========================================================
        st.markdown("### ⚖️ Bilan Financier Consolidé & Capacité d'Investissement")
        revenu_total_estime = revenu_cacao_dernire_annee + total_autres_revenus
        charges_totales = total_depenses_an + total_cout_mo
        solde_net_estime = revenu_total_estime - charges_totales

        col_b1, col_b2, col_b3 = st.columns(3)
        col_b1.metric("Revenus Totaux (N-1)", f"{revenu_total_estime:,.0f} FCFA")
        col_b2.metric("Charges Totales (Foyer + MO)", f"{charges_totales:,.0f} FCFA")
        col_b3.metric("Solde Net Estimé", f"{solde_net_estime:,.0f} FCFA", delta_color="normal" if solde_net_estime >= 0 else "inverse")

        # Évaluation de la soutenabilité économique
        if solde_net_estime < 0:
            st.error("🚨 **Déficit financier annuel** : Les charges du ménage et de la main-d'œuvre dépassent les revenus générés. Risque de surendettement.")
        elif solde_net_estime < 200000:
            st.warning("⚠️ **Capacité d'épargne limitée** (< 200 000 FCFA/an). Capacité d'investissement restreinte pour la fertilisation et la réhabilitation.")
        else:
            st.success("🟢 **Solde financier positif** : Le ménage dispose d'une marge budgétaire pour investir dans les intrants et les aménagements de la parcelle.")

        def sauvegarder_etape_7():
            st.session_state.reponses_pdc.update({
                "financement": st.session_state.df_financement.to_dict("records"),
                "prod_historique": st.session_state.df_prod_historique.to_dict("records"),
                "autres_revenus": st.session_state.df_autres_revenus.to_dict("records"),
                "depenses_foyer": st.session_state.df_depenses.to_dict("records"),
                "main_oeuvre": st.session_state.df_main_oeuvre.to_dict("records"),
                "revenu_total_estime": revenu_total_estime,
                "charges_totales_estimees": charges_totales,
                "solde_net_estime": solde_net_estime,
                "tendance_production_3ans_pct": evo_prod_pct,
                "part_revenu_cacao_pct": part_cacao
            })

        # NAVIGATION ENTRE ÉTAPES
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Retour", use_container_width=True):
                sauvegarder_etape_7()
                st.session_state.etape_pdc = 6
                st.rerun()
        with col2:
            if st.button("Suivant ➡️", use_container_width=True, type="primary"):
                sauvegarder_etape_7()
                st.session_state.etape_pdc = 8
                st.rerun()



    # ---------------------------------------------------------
    # ÉTAPE 8 : PLANIFICATION COMPLÈTE (PLAN 5 ANS & FICHE 7)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 8:
        st.subheader("Étape 8/15 : Plan d'Action & Programme Annuel (Fiche 7)")
        st.caption("Planification globale, matrice quinquennale, calendrier d'exécution")

        # =========================================================
        # 1. FONCTIONS DE CALLBACKS POUR PERSISTANCE DES DATAFRAMES
        # =========================================================
        def apply_editor_changes(key_editor, key_state_df):
            """Applique les deltas de st.data_editor au DataFrame st.session_state."""
            changes = st.session_state.get(key_editor, {})
            df = st.session_state[key_state_df].copy()

            # Modifications
            for row_idx_str, row_changes in changes.get("edited_rows", {}).items():
                row_idx = int(row_idx_str)
                for col_name, new_val in row_changes.items():
                    if col_name in df.columns:
                        df.iat[row_idx, df.columns.get_loc(col_name)] = new_val

            # Ajouts
            for new_row in changes.get("added_rows", {}):
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Suppressions
            deleted_indices = changes.get("deleted_rows", [])
            if deleted_indices:
                df = df.drop(index=deleted_indices).reset_index(drop=True)

            st.session_state[key_state_df] = df

        def update_analyse_problemes():
            apply_editor_changes("editor_analyse_prob", "df_analyse_problemes")

        def update_plan_action_5ans():
            apply_editor_changes("editor_plan_action_5ans", "df_plan_action_5ans")

        def update_programme_annuel():
            apply_editor_changes("editor_prog_annuel", "df_programme_annuel")

        # =========================================================
        # 2. INITIALISATION ET GARANTIE DES DATAFRAMES EN SESSION STATE
        # =========================================================
        if "df_analyse_problemes" not in st.session_state or not isinstance(st.session_state.df_analyse_problemes, pd.DataFrame):
            init_analyse = st.session_state.reponses_pdc.get("analyse_problemes", [
                {
                    "Domaine": "Peuplement du verger",
                    "Problèmes ou Contraintes": "Forte densité (1500 pieds/ha)",
                    "Causes": "Non-respect du dispositif de plantation",
                    "Conséquences": "Prolifération des maladies et insectes",
                    "Solutions": "Régler la densité"
                },
                {
                    "Domaine": "Entretien du verger",
                    "Problèmes ou Contraintes": "Présence de nombreux gourmands",
                    "Causes": "Absence d'entretien",
                    "Conséquences": "Attire les mirides / Réduit la vigueur",
                    "Solutions": "Réaliser la taille d'entretien"
                }
            ])
            st.session_state.df_analyse_problemes = pd.DataFrame(init_analyse)

        if "df_plan_action_5ans" not in st.session_state or not isinstance(st.session_state.df_plan_action_5ans, pd.DataFrame):
            init_plan_5ans = st.session_state.reponses_pdc.get("plan_action_5ans", [
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Objectifs": "Remettre la parcelle en bon état de production",
                    "Activités": "Régler la densité",
                    "Coût (FCFA)": 200000,
                    "A1": True, "A2": False, "A3": False, "A4": False, "A5": False,
                    "Responsable": "Producteur",
                    "Partenaires": "Coopérative"
                }
            ])
            st.session_state.df_plan_action_5ans = pd.DataFrame(init_plan_5ans)

        if "df_programme_annuel" not in st.session_state or not isinstance(st.session_state.df_programme_annuel, pd.DataFrame):
            init_prog_annuel = st.session_state.reponses_pdc.get("programme_annuel", [
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Activités": "Régler la densité",
                    "Sous-activités": "Identifier les pieds à supprimer",
                    "Indicateurs": "80% des pieds à supprimer identifiés",
                    "T1": True, "T2": False, "T3": False, "T4": False,
                    "Responsable d'exécution": "Producteur",
                    "Responsable suivi": "Coopérative",
                    "Coût FCFA": 0
                }
            ])
            st.session_state.df_programme_annuel = pd.DataFrame(init_prog_annuel)

        # =========================================================
        # 8.1 GRILLE DE DÉCISION DYNAMIQUE
        # =========================================================
        st.markdown("### 📊 1. Grille de décision")
        st.caption("Cochez les critères constatés sur la parcelle pour déterminer le type de décision.")

        criteres_replantation = [
            "Plantation âgée de plus de 30 ans",
            "Densité inférieure à 800 arbres productifs / ha",
            "Rendement inférieur à 400 kg / ha",
            "Sol favorable à la culture de cacao",
            "Présence de foyers de Swollen Shoot"
        ]

        criteres_rehabilitation = [
            "Plantation âgée de moins de 30 ans",
            "Densité : 800 à 1 000 arbres productifs / ha",
            "Rendement : au moins 400 kg / ha",
            "Absence de foyers de Swollen Shoot"
        ]

        criteres_reconversion = [
            "Pluviométrie inférieure à 1200 mm avec plus de 4 mois de saison sèche",
            "Présence de cuirasse à moins d'un mètre de profondeur"
        ]

        coche_replantation = []
        coche_rehabilitation = []
        coche_reconversion = []

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Critères Replantation / Réhabilitation**")
            for crit in criteres_replantation:
                if st.checkbox(crit, key=f"crit_{crit}"):
                    coche_replantation.append(crit)

            for crit in criteres_rehabilitation:
                if st.checkbox(crit, key=f"crit_{crit}"):
                    coche_rehabilitation.append(crit)

        with col_b:
            st.markdown("**Critères Reconversion**")
            for crit in criteres_reconversion:
                if st.checkbox(crit, key=f"crit_{crit}"):
                    coche_reconversion.append(crit)

        decision_calculee = "Non déterminée"
        if len(coche_reconversion) > 0:
            decision_calculee = "Reconversion"
        elif len(coche_replantation) > 0:
            decision_calculee = "Replantation"
        elif len(coche_rehabilitation) > 0:
            decision_calculee = "Réhabilitation"

        if decision_calculee == "Replantation":
            st.error(f"**Type de décision : {decision_calculee}**")
        elif decision_calculee == "Reconversion":
            st.warning(f"**Type de décision : {decision_calculee}**")
        elif decision_calculee == "Réhabilitation":
            st.success(f"**Type de décision : {decision_calculee}**")
        else:
            st.info("Veuillez cocher au moins un critère pour déterminer la décision.")

        st.markdown("---")

        # =========================================================
        # 8.2 TABLEAU D'ANALYSE DES PROBLÈMES
        # =========================================================
        st.markdown("### ⚠️ 2. Tableau d'analyse des problèmes")

        st.data_editor(
            st.session_state.df_analyse_problemes,
            num_rows="dynamic",
            key="editor_analyse_prob",
            column_config={
                "Domaine": st.column_config.SelectboxColumn(
                    "Domaine",
                    options=["Peuplement du verger", "Entretien du verger", "Protection phytosanitaire", "Gestion du sol / Ombrage"],
                    required=True
                ),
                "Problèmes ou Contraintes": st.column_config.TextColumn("Problèmes / Contraintes", width="medium"),
                "Causes": st.column_config.TextColumn("Causes", width="medium"),
                "Conséquences": st.column_config.TextColumn("Conséquences", width="medium"),
                "Solutions": st.column_config.TextColumn("Solutions préconisées", width="medium")
            },
            use_container_width=True,
            on_change=update_analyse_problemes
        )

        st.markdown("---")

        # =========================================================
        # 8.3 PLAN D'ACTION SUR 5 ANS
        # =========================================================
        st.markdown("### 📅 3. Plan d'Action Quinquennal (Sur 5 ans)")

        st.data_editor(
            st.session_state.df_plan_action_5ans,
            num_rows="dynamic",
            key="editor_plan_action_5ans",
            column_config={
                "Axes stratégiques": st.column_config.SelectboxColumn(
                    "Axes stratégiques",
                    options=[
                        "Axe 1 : Réhabilitation du verger",
                        "Axe 2 : Replantation du verger",
                        "Axe 3 : Amélioration de la fertilité des sols",
                        "Axe 4 : Protection phytosanitaire intégrée"
                    ],
                    required=True,
                    width="medium"
                ),
                "Objectifs": st.column_config.TextColumn("Objectifs", width="medium"),
                "Activités": st.column_config.TextColumn("Activités à réaliser", width="large"),
                "Coût (FCFA)": st.column_config.NumberColumn("Coût (FCFA)", min_value=0, step=5000, format="%d FCFA"),
                "A1": st.column_config.CheckboxColumn("A1"),
                "A2": st.column_config.CheckboxColumn("A2"),
                "A3": st.column_config.CheckboxColumn("A3"),
                "A4": st.column_config.CheckboxColumn("A4"),
                "A5": st.column_config.CheckboxColumn("A5"),
                "Responsable": st.column_config.SelectboxColumn("Responsable", options=["Producteur", "Manœuvre", "Équipe spécialisée"], default="Producteur"),
                "Partenaires": st.column_config.TextColumn("Partenaires", width="medium")
            },
            use_container_width=True,
            on_change=update_plan_action_5ans
        )

        df_plan = st.session_state.df_plan_action_5ans
        total_budget_5ans = df_plan["Coût (FCFA)"].sum() if "Coût (FCFA)" in df_plan.columns else 0
        st.info(f"💰 **Budget total estimé du plan d'action sur 5 ans :** `{total_budget_5ans:,.0f} FCFA`".replace(",", " "))

        st.markdown("---")

        # =========================================================
        # 8.4 PROGRAMME ANNUEL D'ACTIVITÉS (FICHE 7)
        # =========================================================
        st.markdown("### 🗓️ 4. Programme Annuel d'Activités (Fiche 7)")

        st.data_editor(
            st.session_state.df_programme_annuel,
            num_rows="dynamic",
            key="editor_prog_annuel",
            column_config={
                "Axes stratégiques": st.column_config.SelectboxColumn("Axe stratégique", options=["Axe 1 : Réhabilitation du verger", "Axe 2 : Replantation du verger"], width="medium"),
                "Activités": st.column_config.TextColumn("Activité", width="medium"),
                "Sous-activités": st.column_config.TextColumn("Sous-activité", width="large"),
                "Indicateurs": st.column_config.TextColumn("Indicateur de suivi", width="large"),
                "T1": st.column_config.CheckboxColumn("T1"),
                "T2": st.column_config.CheckboxColumn("T2"),
                "T3": st.column_config.CheckboxColumn("T3"),
                "T4": st.column_config.CheckboxColumn("T4"),
                "Responsable d'exécution": st.column_config.SelectboxColumn("Exécution", options=["Producteur", "Manœuvre", "Équipe spécialisée"], default="Producteur"),
                "Responsable suivi": st.column_config.SelectboxColumn("Suivi", options=["Coopérative", "ANADER", "Agent terrain"], default="Coopérative"),
                "Coût FCFA": st.column_config.NumberColumn("Coût (FCFA)", min_value=0, step=2500, format="%d FCFA")
            },
            use_container_width=True,
            on_change=update_programme_annuel
        )

        df_prog = st.session_state.df_programme_annuel
        total_annuel = df_prog["Coût FCFA"].sum() if "Coût FCFA" in df_prog.columns else 0
        st.info(f"💰 **Budget total du programme annuel :** `{total_annuel:,.0f} FCFA`".replace(",", " "))

        st.markdown("---")

        # =========================================================
        # FONCTION DE SAUVEGARDE ET BOUTONS DE NAVIGATION ÉTAPE 8
        # =========================================================
        def sauvegarder_etape_8():
            if "reponses_pdc" not in st.session_state:
                st.session_state.reponses_pdc = {}

            st.session_state.reponses_pdc.update({
                "decision_retenue": decision_calculee,
                "analyse_problemes": st.session_state.df_analyse_problemes.to_dict("records"),
                "plan_action_5ans": st.session_state.df_plan_action_5ans.to_dict("records"),
                "programme_annuel": st.session_state.df_programme_annuel.to_dict("records"),
                "budget_total_5ans": total_budget_5ans,
                "budget_annuel_total": total_annuel
            })

        col_e8_1, col_e8_2 = st.columns([1, 1])
        with col_e8_1:
            if st.button("⬅️ Retour", key="btn_retour_etape8", use_container_width=True):
                sauvegarder_etape_8()
                st.session_state.etape_pdc = 7
                st.rerun()

        with col_e8_2:
            if st.button("Suivant ➡️", key="btn_suivant_etape8", type="primary", use_container_width=True):
                sauvegarder_etape_8()
                st.session_state.etape_pdc = 9
                st.rerun()


    # ---------------------------------------------------------
    # ÉTAPE 9 : DÉTERMINATION DES MOYENS ET COÛTS (FICHE 8)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 9:
        st.subheader("Étape 9/15 : Détermination des moyens et des coûts (Fiche 8)")
        st.caption("Évaluation détaillée des coûts d'investissement, intrants et main d'œuvre par activité sur 5 ans.")

        # 1. Callback de mise à jour des modifications st.data_editor
        def update_moyens_cou_fiche8():
            changes = st.session_state.get("editor_fiche8_moyens_couts", {})
            df = st.session_state.df_moyens_cou_fiche8.copy()

            # Modifications de cellules
            for row_idx_str, row_changes in changes.get("edited_rows", {}).items():
                row_idx = int(row_idx_str)
                for col_name, new_val in row_changes.items():
                    if col_name in df.columns:
                        df.iat[row_idx, df.columns.get_loc(col_name)] = new_val

            # Ajouts de lignes
            for new_row in changes.get("added_rows", {}):
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Suppressions de lignes
            deleted_indices = changes.get("deleted_rows", [])
            if deleted_indices:
                df = df.drop(index=deleted_indices).reset_index(drop=True)

            st.session_state.df_moyens_cou_fiche8 = df

        # 2. Champs de saisie de l'activité concernée
        activite_selectionnee = st.text_input(
            "Activité concernée :",
            value=st.session_state.reponses_pdc.get("activite_fiche8", "Activité 1 : Traitement phytosanitaire et fertilisation"),
            placeholder="Entrez le nom de l'activité...",
            key="input_activite_fiche8"
        )

        # 3. Initialisation du DataFrame dans session state
        if "df_moyens_cou_fiche8" not in st.session_state or not isinstance(st.session_state.df_moyens_cou_fiche8, pd.DataFrame):
            init_fiche8 = st.session_state.reponses_pdc.get("moyens_fiche8_details", [
                {"Catégorie": "Investissement", "Moyens spécifiques": "Atomiseur", "Unités": "Nombre", "Qté A1": 1, "Coût A1": 150000, "Qté A2": 0, "Coût A2": 0, "Qté A3": 0, "Coût A3": 0, "Qté A4": 0, "Coût A4": 0, "Qté A5": 0, "Coût A5": 0},
                {"Catégorie": "Intrants", "Moyens spécifiques": "Engrais", "Unités": "kg", "Qté A1": 200, "Coût A1": 70000, "Qté A2": 200, "Coût A2": 70000, "Qté A3": 250, "Coût A3": 87500, "Qté A4": 250, "Coût A4": 87500, "Qté A5": 300, "Coût A5": 105000}
            ])
            st.session_state.df_moyens_cou_fiche8 = pd.DataFrame(init_fiche8)

        # 4. Éditeur de données
        st.data_editor(
            st.session_state.df_moyens_cou_fiche8,
            num_rows="dynamic",
            key="editor_fiche8_moyens_couts",
            column_config={
                "Catégorie": st.column_config.SelectboxColumn("Catégorie", options=["Investissement", "Intrants", "Main d'œuvre", "Activités d'appui/gestion"], required=True, width="medium"),
                "Moyens spécifiques": st.column_config.TextColumn("Moyens spécifiques", width="medium"),
                "Unités": st.column_config.TextColumn("Unités", width="small"),
                "Qté A1": st.column_config.NumberColumn("Qté A1", min_value=0, step=1),
                "Coût A1": st.column_config.NumberColumn("Coût A1 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A2": st.column_config.NumberColumn("Qté A2", min_value=0, step=1),
                "Coût A2": st.column_config.NumberColumn("Coût A2 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A3": st.column_config.NumberColumn("Qté A3", min_value=0, step=1),
                "Coût A3": st.column_config.NumberColumn("Coût A3 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A4": st.column_config.NumberColumn("Qté A4", min_value=0, step=1),
                "Coût A4": st.column_config.NumberColumn("Coût A4 (FCFA)", min_value=0, step=1000, format="%d FCFA"),
                "Qté A5": st.column_config.NumberColumn("Qté A5", min_value=0, step=1),
                "Coût A5": st.column_config.NumberColumn("Coût A5 (FCFA)", min_value=0, step=1000, format="%d FCFA")
            },
            use_container_width=True,
            on_change=update_moyens_cou_fiche8
        )

        # 5. Calcul du coût global sur 5 ans
        df_f8 = st.session_state.df_moyens_cou_fiche8
        cols_couts = [f"Coût A{i}" for i in range(1, 6) if f"Coût A{i}" in df_f8.columns]
        total_fiche8 = df_f8[cols_couts].sum().sum() if not df_f8.empty and cols_couts else 0

        st.info(f"💵 **Coût global estimé des moyens (Fiche 8) sur 5 ans :** `{total_fiche8:,.0f} FCFA`".replace(",", " "))

        st.markdown("---")

        # Sauvegarde Étape 9
        def sauvegarder_etape_9():
            if "reponses_pdc" not in st.session_state:
                st.session_state.reponses_pdc = {}

            st.session_state.reponses_pdc.update({
                "activite_fiche8": activite_selectionnee,
                "moyens_fiche8_details": st.session_state.df_moyens_cou_fiche8.to_dict("records"),
                "budget_fiche8_total": total_fiche8
            })

        # Navigation Étape 9
        col_e9_1, col_e9_2 = st.columns([1, 1])
        with col_e9_1:
            if st.button("⬅️ Retour", key="btn_retour_etape9", use_container_width=True):
                sauvegarder_etape_9()
                st.session_state.etape_pdc = 8
                st.rerun()

        with col_e9_2:
            if st.button("Suivant ➡️", key="btn_suivant_etape9", type="primary", use_container_width=True):
                sauvegarder_etape_9()
                st.session_state.etape_pdc = 10
                st.rerun()


    # ---------------------------------------------------------
    # ÉTAPE 10 : AUDIT & DIAGNOSTIC DE CONFORMITÉ (BILAN FINAL PARTIE 1)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 10:
        st.subheader("Étape 10/15 : Bilan & Diagnostic Qualité du PDC")
        st.caption("Synthèse globale du plan de développement et évaluation de conformité.")

        donnees = st.session_state.get("reponses_pdc", {})

        # --- 10.1 DIAGNOSTIC & AUDIT DE CONFORMITÉ ---
        st.markdown("### 🔍 Diagnostic Qualité du PDC")
        
        # Diagnostic via evaluer_pdc
        score_global, pts_forts, avert, alertes = evaluer_pdc(donnees)

        st.metric(label="Score de Conformité Global (Étapes 1 à 9)", value=f"{score_global} / 100")

        if alertes:
            st.error("🚨 **Alertes Critiques / Non-Conformités Majeures :**")
            for alerte in alertes:
                st.write(f"- {alerte}")

        if avert:
            st.warning("⚠️ **Avertissements & Points d'attention :**")
            for av in avert:
                st.write(f"- {av}")

        with st.expander("✅ Voir les Points Forts validés"):
            if pts_forts:
                for pf in pts_forts:
                    st.write(f"- {pf}")
            else:
                st.write("Aucun point fort enregistré pour le moment.")

        st.markdown("---")

        # --- 10.2 RÉCAPITULATIF ET BUDGETS ---
        st.markdown("### 📌 Récapitulatif Synthétique")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.metric("Producteur", donnees.get("nom", "Non renseigné"))
        col_s2.metric("Localité / Ville", donnees.get("ville", "Non renseigné"))
        col_s3.metric("Zone d'intervention", f"Zone {donnees.get('zone', '-')}")

        col_b1, col_b2, col_b3 = st.columns(3)
        col_b1.metric("Budget Plan 5 ans", f"{donnees.get('budget_total_5ans', 0):,.0f} FCFA".replace(",", " "))
        col_b2.metric("Programme Annuel (A1)", f"{donnees.get('budget_annuel_total', 0):,.0f} FCFA".replace(",", " "))
        col_b3.metric("Moyens & Intrants (F8)", f"{donnees.get('budget_fiche8_total', 0):,.0f} FCFA".replace(",", " "))

        st.markdown("---")

        # --- 10.3 BILAN JSON COMPLET ---
        with st.expander("📄 Voir le bilan des données brutes collectées (JSON)"):
            st.json(donnees)

        st.markdown("---")

        # --- 10.4 NAVIGATION ---
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour", key="btn_retour_etape10", use_container_width=True):
                st.session_state.etape_pdc = 9
                st.rerun()
                
        with col_btn2:
            if st.button("Suivant  ➡️", key="btn_suivant_etape10", type="primary", use_container_width=True):
                st.session_state.reponses_pdc["score_conformite_etape1_9"] = score_global
                st.session_state.etape_pdc = 11
                st.rerun()

       # ---------------------------------------------------------
    # ÉTAPE 11 : IDENTIFICATION DU PRODUCTEUR & LOCALISATION (PARTIE 2)
    # (PARTIE VI : STRUCTURATION DU PDC - 1.1 Identification)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 11:
        st.subheader("Étape 11/15 : Identification du Producteur (Situation de Référence)")
        st.info("Saisie des informations d'identification officielles selon le modèle Conseil Café-Cacao.")

        col_id1, col_id2 = st.columns(2)
        
        with col_id1:
            nom_prenoms = st.text_input("Nom et prénoms du producteur", key="input_nom_prenoms")
            contact_tel = st.text_input("Contact (Tél)", key="input_contact_tel")
            code_national = st.text_input("Code National du producteur (Le Conseil du Café-Cacao)", key="input_code_national")
            code_groupe = st.text_input("Code groupe", key="input_code_groupe")
            nom_entite = st.text_input("Nom Entité reconnue", key="input_nom_entite")
            code_entite = st.text_input("Code Entité reconnue", key="input_code_entite")

        with col_id2:
            delegation_regionale = st.text_input("Délégation Régionale du Conseil du Café-Cacao", key="input_delegation")
            departement = st.text_input("Département", key="input_departement")
            sous_prefecture = st.text_input("Sous-Préfecture", key="input_sprefecture")
            village = st.text_input("Village", key="input_village")
            campement = st.text_input("Campement", key="input_campement")

        st.markdown("---")

        # Layout unique pour la navigation (1 seule déclaration pour col1 et col2)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("⬅️ Retour", key="btn_retour_pdc_etape11", use_container_width=True):
                st.session_state.etape_pdc = 10
                st.rerun()

        with col2:
            if st.button("Suivant ➡️", key="btn_suivant_pdc_etape11", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}
                    
                st.session_state.reponses_pdc.update({
                    "nom_prenoms_producteur": nom_prenoms,
                    "contact_tel": contact_tel,
                    "code_national_producteur": code_national,
                    "code_groupe": code_groupe,
                    "nom_entite_reconnue": nom_entite,
                    "code_entite_reconnue": code_entite,
                    "delegation_regionale": delegation_regionale,
                    "departement": departement,
                    "sous_prefecture": sous_prefecture,
                    "village": village,
                    "campement": campement
                })
                
                # Inscription directe dans la session racine pour SQLite/Supabase
                st.session_state["nom_producteur"] = nom_prenoms
                st.session_state["code_producteur"] = code_national
                
                st.session_state.etape_pdc = 12
                st.rerun()

    # ---------------------------------------------------------
    # ÉTAPE 12 : MÉNAGE & DESCRIPTION DE L'EXPLOITATION (NORMES CCC)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 12:
        st.subheader("Étape 12/15 : Informations Ménage & Description de l'Exploitation")
        st.caption("Données financières, main-d'œuvre et croquis/caractérisation spatiale de la parcelle selon le barème du Conseil Café-Cacao.")

        # =========================================================
        # 12.1 SITUATION DE L'ÉPARGNE
        # =========================================================
        st.markdown("### 💳 1.2.1 Situation de l'épargne")

        if 'df_epargne_pdc' not in st.session_state or not isinstance(st.session_state.df_epargne_pdc, pd.DataFrame):
            epargne_init = [
                {"Épargne": "Mobile Money", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
                {"Épargne": "Microfinance", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
                {"Épargne": "Banque", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
                {"Épargne": "Autres (à préciser)", "Avez-vous un compte ?": "Non", "Avez-vous de l'argent sur le compte ?": "Non", "Avez-vous bénéficié de financement ?": "Non", "Montant (FCFA)": 0},
            ]
            st.session_state.df_epargne_pdc = pd.DataFrame(epargne_init)

        df_epargne_edite = st.data_editor(
            st.session_state.df_epargne_pdc,
            key="editor_epargne_pdc",
            column_config={
                "Épargne": st.column_config.TextColumn("Type d'épargne", disabled=True),
                "Avez-vous un compte ?": st.column_config.SelectboxColumn("Compte ?", options=["Oui", "Non"], default="Non"),
                "Avez-vous de l'argent sur le compte ?": st.column_config.SelectboxColumn("Argent disponible ?", options=["Oui", "Non"], default="Non"),
                "Avez-vous bénéficié de financement ?": st.column_config.SelectboxColumn("Financement reçu ?", options=["Oui", "Non"], default="Non"),
                "Montant (FCFA)": st.column_config.NumberColumn("Montant du financement", min_value=0, step=5000, format="%d FCFA")
            },
            use_container_width=True,
            num_rows="dynamic"
        )

        st.markdown("---")

        # =========================================================
        # 12.2 SITUATION DE LA MAIN-D'ŒUVRE
        # =========================================================
        st.markdown("### 👥 1.2.2 Situation de la main-d'œuvre")

        if "df_main_oeuvre_pdc" not in st.session_state or not isinstance(st.session_state.df_main_oeuvre_pdc, pd.DataFrame):
            mo_init = [
                {"Membre du ménage": "Propriétaire de l'exploitation", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Plein temps"},
                {"Membre du ménage": "Gérant ou représentant", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Plein temps"},
                {"Membre du ménage": "Conjoints", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Occasionnel"},
                {"Membre du ménage": "Enfants 0 - 6 ans", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Aucun", "Temps de travail": "Occasionnel"},
                {"Membre du ménage": "Enfant 6 - 18 ans", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Primaire", "Temps de travail": "Occasionnel"},
                {"Membre du ménage": "Enfant + 18 ans", "Nb Femmes": 0, "Nb Hommes": 0, "Nb à l'école": 0, "Instruction": "Secondaire", "Temps de travail": "Plein temps"},
            ]
            st.session_state.df_main_oeuvre_pdc = pd.DataFrame(mo_init)

        df_mo_edite = st.data_editor(
            st.session_state.df_main_oeuvre_pdc,
            key="editor_main_oeuvre_pdc",
            column_config={
                "Membre du ménage": st.column_config.TextColumn("Catégorie membre", disabled=True),
                "Nb Femmes": st.column_config.NumberColumn("F", min_value=0, step=1, help="Nombre de femmes"),
                "Nb Hommes": st.column_config.NumberColumn("M", min_value=0, step=1, help="Nombre d'hommes"),
                "Nb à l'école": st.column_config.NumberColumn("Encore à l'école", min_value=0, step=1),
                "Instruction": st.column_config.SelectboxColumn("Niveau d'instruction", options=["Aucun", "Primaire", "Secondaire", "Universitaire"], default="Aucun"),
                "Temps de travail": st.column_config.SelectboxColumn("Temps de travail sur plantation", options=["Plein temps", "Occasionnel", "Aucun"], default="Occasionnel"),
            },
            use_container_width=True,
            num_rows="dynamic",
        )

        st.markdown("---")

        # =========================================================
        # 12.3 DESCRIPTION & CARACTÉRISTIQUES DE L'EXPLOITATION
        # =========================================================
        st.markdown("### 🏡 1.3 Description & Caractéristiques de l'Exploitation")

        # Extraction sécurisée des données de l'étape 4
        reponses = st.session_state.get("reponses_pdc", {})

        try:
            surf_cacao_defaut = float(reponses.get("superficie_totale_cacao", 3.5))
        except (ValueError, TypeError):
            surf_cacao_defaut = 3.5

        try:
            surf_autres_defaut = float(reponses.get("superficie_autres_cultures", 0.5))
        except (ValueError, TypeError):
            surf_autres_defaut = 0.5

        surf_totale_defaut = surf_cacao_defaut + surf_autres_defaut

        tableau_arbres = reponses.get("tableau_arbres", st.session_state.get("temp_tableau_arbres", []))

        try:
            nb_arbres_defaut = int(reponses.get("arbres_conserves", len(tableau_arbres)))
        except (ValueError, TypeError):
            nb_arbres_defaut = len(tableau_arbres)

        try:
            densite_ha_defaut = float(reponses.get("densite_conservee_ha", 0.0))
        except (ValueError, TypeError):
            densite_ha_defaut = 0.0

        essences_extraites = list({
            str(row.get("Espèce", "")).strip()
            for row in tableau_arbres
            if isinstance(row, dict) and row.get("Espèce")
        })

        if densite_ha_defaut < 10:
            ombrage_defaut = "Faible (< 10 arbres/ha)"
        elif 10 <= densite_ha_defaut <= 25:
            ombrage_defaut = "Adéquat (10-25 arbres/ha)"
        else:
            ombrage_defaut = "Excessif (> 25 arbres/ha)"

        # --- EXPANDER 1 : FORMULAIRE AGRONOMIQUE & FONCIER ---
        with st.expander("📋 **1. Formulaire AGRONOMIQUE & FONCIER**", expanded=True):
            col1, col2 = st.columns(2)

            with col1:
                statut_foncier = st.selectbox(
                    "📜 Statut foncier de la parcelle",
                    [
                        "Propriétaire coutumier",
                        "Titre foncier / Certificat foncier",
                        "Métayage (Abougnon / Planteur-Partage)",
                        "Location / Fermage",
                    ],
                    key="statut_foncier",
                )
                surf_totale = st.number_input(
                    "📐 Superficie totale de l'exploitation (ha)",
                    min_value=0.1,
                    value=max(0.1, surf_totale_defaut),
                    step=0.5,
                    key="surf_totale",
                    help="Prend automatiquement la somme des superficies renseignées à l'Étape 4",
                )
                surf_cacao_prod = st.number_input(
                    "🍫 Superficie en cacao productif (ha)",
                    min_value=0.0,
                    value=surf_cacao_defaut,
                    step=0.5,
                    key="surf_cacao_prod",
                    help="Total du cacao productif calculé à l'Étape 4",
                )
                surf_cacao_jeune = st.number_input(
                    "🌱 Superficie cacao immature / immaturité (ha)",
                    min_value=0.0,
                    value=0.0,
                    step=0.5,
                    key="surf_cacao_jeune",
                )

            with col2:
                age_moyen_plan = st.select_slider(
                    "🌳 Âge moyen du verger (années)",
                    options=[
                        "0-3 ans (Jeune)",
                        "4-15 ans (Plein rendement)",
                        "16-25 ans (Vieillissant)",
                        "+25 ans (Vétuste)",
                    ],
                    value="4-15 ans (Plein rendement)",
                    key="age_moyen",
                )
                relief_sol = st.multiselect(
                    "⛰️ Relief & Type de sol prédominant",
                    [
                        "Bas-fond / Hydromorphe",
                        "Plat / Sol Ferrallitique",
                        "Pente légère / Sol Gravillonnaire",
                        "Zone Rocheuse / Latéritique",
                    ],
                    default=["Plat / Sol Ferrallitique"],
                    key="relief_sol",
                )
                contraintes = st.multiselect(
                    "⚠️ Contraintes & Risques observés sur la parcelle",
                    [
                        "Attaque de Swollen Shoot",
                        "Pression Foreurs de tiges / Punaise",
                        "Pourriture brune des cabosses",
                        "Ombrage excessif",
                        "Manque d'eau / Sécheresse",
                        "Inaccessibilité en saison de pluies",
                    ],
                    default=["Pression Foreurs de tiges / Punaise"],
                    key="contraintes_parcelle",
                )

        # --- EXPANDER 2 : CARTOGRAPHIE, ARBRES & INFRASTRUCTURES GÉOLOCALISÉES ---
        with st.expander("🗺️ **2. Cartographie, Infrastructures & Repères Géolocalisés (Normes CCC & RDUE)**", expanded=True):
            st.caption("Données relatives au croquis/polygone, aux waypoints du contour, aux infrastructures et aux arbres d'ombrage géolocalisés.")

            col_geo1, col_geo2 = st.columns(2)

            with col_geo1:
                voies_acces = st.multiselect(
                    "🛣️ Pistes & Voies d'accès",
                    [
                        "Piste cyclable / Piétonne",
                        "Piste camionnière / Sommier",
                        "Route bitumée à proximité",
                        "Traversée par voie d'eau",
                    ],
                    default=["Piste camionnière / Sommier"],
                    key="voies_acces",
                )

            with col_geo2:
                lat_ref = (
                    tableau_arbres[0].get("Latitude")
                    if (tableau_arbres and isinstance(tableau_arbres[0], dict) and "Latitude" in tableau_arbres[0])
                    else 6.67262
                )
                lon_ref = (
                    tableau_arbres[0].get("Longitude")
                    if (tableau_arbres and isinstance(tableau_arbres[0], dict) and "Longitude" in tableau_arbres[0])
                    else -5.28095
                )
                gps_defaut_str = f"{lat_ref:.6f} N, {lon_ref:.6f} W"

                waypoint_gps = st.text_input(
                    "📍 Coordonnées GPS centrales / Waypoint Central",
                    value=gps_defaut_str,
                    key="waypoint_gps",
                )

            st.markdown("---")

            # --- SOMMETS DU POLYGONE ---
            st.markdown("##### 📐 Sommets / Coins de la Parcelle (Polygone GPS)")
            st.caption("Renseignez les waypoints des coins de la parcelle.")

            if "temp_tableau_sommets" not in st.session_state:
                st.session_state.temp_tableau_sommets = []

            df_sommets_in = pd.DataFrame(st.session_state.temp_tableau_sommets)
            for col in ["Sommet", "Latitude", "Longitude"]:
                if col not in df_sommets_in.columns:
                    df_sommets_in[col] = None

            df_sommets_out = st.data_editor(
                df_sommets_in,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Sommet": st.column_config.TextColumn("Nom du point / Sommet", required=True),
                    "Latitude": st.column_config.NumberColumn("Latitude (ex: 6.67262)", format="%.6f"),
                    "Longitude": st.column_config.NumberColumn("Longitude (ex: -5.28095)", format="%.6f"),
                },
                key="editor_sommets_pdc",
            )
            liste_sommets = df_sommets_out.to_dict("records")
            st.session_state.temp_tableau_sommets = liste_sommets

            st.markdown("---")

            # --- INFRASTRUCTURES & REPÈRES ---
            st.markdown("##### 📍 Infrastructures & Éléments Remarquables Géolocalisés")

            cols_reperes = ["Élément", "Latitude", "Longitude", "Remarque"]
            if "temp_tableau_reperes" not in st.session_state:
                st.session_state.temp_tableau_reperes = [
                    {
                        "Élément": "Campement / Habitation",
                        "Latitude": lat_ref + 0.0005,
                        "Longitude": lon_ref - 0.0005,
                        "Remarque": "Campement principal",
                    }
                ]

            df_rep_in = pd.DataFrame(st.session_state.temp_tableau_reperes)
            for col in cols_reperes:
                if col not in df_rep_in.columns:
                    df_rep_in[col] = None

            df_reperes_out = st.data_editor(
                df_rep_in,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Élément": st.column_config.SelectboxColumn(
                        "Type d'infrastructure / Repère",
                        options=[
                            "Campement / Habitation",
                            "Cours d'eau / Bas-fond",
                            "Puits / Source d'eau",
                            "Zone rocheuse non cultivable",
                            "Magasin de stockage",
                        ],
                        required=True,
                    ),
                    "Latitude": st.column_config.NumberColumn("Latitude", format="%.6f"),
                    "Longitude": st.column_config.NumberColumn("Longitude", format="%.6f"),
                    "Remarque": st.column_config.TextColumn("Remarque / Description"),
                },
                key="editor_reperes_pdc",
            )
            liste_reperes = df_reperes_out.to_dict("records")
            st.session_state.temp_tableau_reperes = liste_reperes

            st.markdown("---")

            # --- SYNTHÈSE AGROFORESTIÈRE ---
            st.markdown("##### 🌳 Inventaire Agroforestier (🔒 Récupéré de l'Étape 4)")
            essences_str_label = ", ".join(essences_extraites) if essences_extraites else "Aucune essence spécifiée"

            col_syn1, col_syn2 = st.columns(2)
            with col_syn1:
                st.metric(label="Nombre d'arbres conservés géolocalisés", value=f"{nb_arbres_defaut} pieds")
            with col_syn2:
                st.info(f"• **Essences recensées :** {essences_str_label}\n\n• **Densité / Ombrage :** {ombrage_defaut}")

            nb_arbres_forestiers = nb_arbres_defaut
            essences_arbres = essences_extraites if essences_extraites else ["Akpi", "Iroko", "Framiré"]
            densite_ombrage = ombrage_defaut

            st.markdown("---")

            # --- RENDU DU CROQUIS ---
            st.markdown("##### 🎨 Rendu du Croquis de la Parcelle")
            col_gen1, col_gen2 = st.columns([1, 1])
            with col_gen1:
                btn_generer_croquis = st.button("🖌️ Générer le croquis automatique (CCC)", use_container_width=True)

            with col_gen2:
                fichier_croquis = st.file_uploader("Ou importer un croquis manuel (PNG/JPG)", type=["png", "jpg", "jpeg"], key="fichier_croquis_parcelle")

            if btn_generer_croquis:
                if "generer_croquis_parcelle" in globals():
                    img_buf = generer_croquis_parcelle(
                        nom_producteur=st.session_state.get("nom_producteur", "Inconnu"),
                        code_ccc=st.session_state.get("code_producteur", "CCC-001"),
                        surf_totale=surf_totale,
                        surf_prod=surf_cacao_prod,
                        surf_jeune=surf_cacao_jeune,
                        waypoint_gps=waypoint_gps,
                        nb_arbres=nb_arbres_forestiers,
                        essences=essences_arbres,
                        acces=voies_acces,
                        liste_arbres=tableau_arbres,
                        liste_reperes=liste_reperes,
                        liste_sommets=liste_sommets,
                    )
                    st.session_state["croquis_genere"] = img_buf.getvalue()
                else:
                    st.warning("La fonction `generer_croquis_parcelle` n'est pas encore définie dans le script.")

            if fichier_croquis is not None:
                st.image(fichier_croquis, caption="Croquis manuel importé pour le dossier CCC", use_container_width=True)
            elif "croquis_genere" in st.session_state:
                st.image(st.session_state["croquis_genere"], caption="Croquis automatique géolocalisé généré (Normes CCC & RDUE)", use_container_width=True)

        # --- CALCULS & TABLEAU DE BORD SYNTHÉTIQUE ---
        surf_autre = max(0.0, surf_totale - (surf_cacao_prod + surf_cacao_jeune))
        pct_cacao = ((surf_cacao_prod + surf_cacao_jeune) / surf_totale * 100) if surf_totale > 0 else 0.0

        relief_str = ", ".join(relief_sol) if relief_sol else "Non précisé"
        contraintes_str = ", ".join(contraintes) if contraintes else "Aucune contrainte majeure"

        elements_reperes_liste = list({
            r.get("Élément", "")
            for r in st.session_state.get("temp_tableau_reperes", [])
            if isinstance(r, dict) and r.get("Élément")
        })
        elements_str = ", ".join(elements_reperes_liste) if elements_reperes_liste else "Aucun élément spécifique"
        voies_str = ", ".join(voies_acces) if voies_acces else "Non précisé"
        essences_str = ", ".join(essences_arbres) if essences_arbres else "Aucune essence spécifiée"

        if "Vétuste" in age_moyen_plan:
            diagnostic_age = "🚨 **Régénération urgente requise** (Verger en fin de cycle productif)."
            niveau_alerte = "error"
        elif "Vieillissant" in age_moyen_plan:
            diagnostic_age = "⚠️ **Replantation progressive à prévoir**."
            niveau_alerte = "warning"
        else:
            diagnostic_age = "✅ **Potentiel de production optimal**."
            niveau_alerte = "success"

        st.markdown("---")
        st.markdown("#### 📊 Tableau de Bord Synthétique de l'Exploitation")

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Superficie Totale", f"{surf_totale:.1f} ha")
        kpi2.metric("Cacao Productif", f"{surf_cacao_prod:.1f} ha", f"{pct_cacao:.0f}% du total")
        kpi3.metric("Arbres Forestiers", f"{nb_arbres_forestiers} pieds", f"{densite_ombrage}")
        kpi4.metric("Autre / Jachère", f"{surf_autre:.1f} ha")

        if niveau_alerte == "error":
            st.error(diagnostic_age)
        elif niveau_alerte == "warning":
            st.warning(diagnostic_age)
        else:
            st.success(diagnostic_age)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("##### 🏞️ Occupation du Sol, Foncier & GPS")
            st.info(
                f"• **Régime foncier :** {statut_foncier}\n\n"
                f"• **Taux d'occupation cacaoyère :** {pct_cacao:.1f}%\n\n"
                f"• **Relief/Sol :** {relief_str}\n\n"
                f"• **Waypoint Central :** `{waypoint_gps}`"
            )

        with col_c2:
            st.markdown("##### 🛡️ Éléments du Croquis & Agroforesterie")
            st.info(
                f"• **Infrastructures/Repères :** {elements_str}\n\n"
                f"• **Accès :** {voies_str}\n\n"
                f"• **Arbres d'ombrage :** {nb_arbres_forestiers} pieds ({essences_str})\n\n"
                f"• **Niveau d'ombrage :** {densite_ombrage}"
            )

        # --- RAPPORT SYNTHÉTIQUE AUTOMATISÉ ---
        st.markdown("#### 📝 Description Officielle (Générée automatiquement pour le Dossier CCC)")

        texte_description = (
            f"L'exploitation sous le statut foncier **{statut_foncier}** couvre une superficie totale mesurée de "
            f"**{surf_totale:.1f} hectares** (Waypoint GPS central : {waypoint_gps}). La spéculation principale est la "
            f"cacaoculture qui occupe **{surf_cacao_prod + surf_cacao_jeune:.1f} ha** (soit **{surf_cacao_prod:.1f} ha** "
            f"en verger productif et **{surf_cacao_jeune:.1f} ha** en phase d'immaturité), représentant **{pct_cacao:.1f}%** "
            f"de la surface globale. Le verger présente un profil d'âge **{age_moyen_plan}**, installé sur un relief "
            f"de type **{relief_str}**. Le croquis cartographique géolocalisé identifie les voies d'accès (**{voies_str}**) "
            f"ainsi que les infrastructures/repères physiques sur la parcelle (**{elements_str}**). Sur le plan agroforestier, "
            f"l'exploitation compte **{nb_arbres_forestiers} arbres forestiers d'ombrage** (principalement : {essences_str}), "
            f"garantissant un niveau d'ombrage évalué comme **{densite_ombrage}**. "
        )

        if contraintes:
            texte_description += f"Sur le plan phytosanitaire et pédo-climatique, la parcelle subit les contraintes suivantes : **{contraintes_str}**."
        else:
            texte_description += "Aucune contrainte phytosanitaire critique n'a été répertoriée lors de la visite terrain."

        st.markdown(texte_description)
        st.markdown("---")

        # =========================================================
        # NAVIGATION DE L'ÉTAPE 12
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour", key="btn_retour_etape12", use_container_width=True):
                st.session_state.etape_pdc = 11
                st.rerun()

        with col_btn2:
            if st.button("Suivant ➡️", key="btn_suivant_etape12", type="primary", use_container_width=True):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Conversion explicite des DataFrames en dictionnaires pour sérialisation
                st.session_state.reponses_pdc["situation_epargne"] = df_epargne_edite.to_dict("records") if isinstance(df_epargne_edite, pd.DataFrame) else df_epargne_edite
                st.session_state.reponses_pdc["situation_main_oeuvre"] = df_mo_edite.to_dict("records") if isinstance(df_mo_edite, pd.DataFrame) else df_mo_edite

                st.session_state.reponses_pdc["description_exploitation"] = {
                    "statut_foncier": statut_foncier,
                    "superficie_totale": surf_totale,
                    "superficie_cacao_productif": surf_cacao_prod,
                    "superficie_cacao_immature": surf_cacao_jeune,
                    "age_moyen": age_moyen_plan,
                    "relief_sol": relief_sol,
                    "contraintes": contraintes,
                    "waypoint_gps": waypoint_gps,
                    "voies_acces": voies_acces,
                    "elements_parcelle": elements_str,
                    "nb_arbres_forestiers": nb_arbres_forestiers,
                    "essences_arbres": essences_arbres,
                    "densite_ombrage": densite_ombrage,
                    "sommets_polygon": liste_sommets,
                    "reperes_geolocalises": liste_reperes,
                    "texte_synthese_auto": texte_description,
                }

                st.session_state.etape_pdc = 13
                st.rerun()


    # =========================================================
    # ÉTAPE 13 : CULTURES, AGROFORESTERIE & MATÉRIEL AGRICOLE
    # =========================================================
    elif st.session_state.etape_pdc == 13:
        st.subheader("Étape 13/15 : Cultures, Agroforesterie & Matériel Agricole")

        st.caption(
            "Caractérisation des spéculations, inventaire des arbres d'ombrage et"
            " bilan des équipements de l'exploitation."
        )

        # --- Initialisation Sécurisée du Session State (DataFrames) ---
        if "df_cultures_pdc" not in st.session_state or not isinstance(st.session_state.df_cultures_pdc, pd.DataFrame):
            init_cultures = [
                {
                    "Culture": "Cacao",
                    "Superficie (ha)": 3.5,
                    "Année de création": 2010,
                    "Source matériel végétal": "SATMACI / ANADER / CNRA",
                    "Production campagne préc. (kg)": 1800,
                    "Revenu (FCFA)": 2700000,
                }
            ]
            st.session_state.df_cultures_pdc = pd.DataFrame(init_cultures)

        if "df_arbres_pdc" not in st.session_state or not isinstance(st.session_state.df_arbres_pdc, pd.DataFrame):
            init_arbres = [
                {
                    "Nom de l'arbre": "Akpi",
                    "Nombre": 1,
                    "Latitude (N)": 0.0,
                    "Longitude (W)": 0.0,
                    "Statut actuel": "Préservé",
                    "Rôle / Avantage": "Produit secondaire (PNFL)",
                    "Décision": "À maintenir",
                    "Remarque / Distance": "Bon état",
                }
            ]
            st.session_state.df_arbres_pdc = pd.DataFrame(init_arbres)

        if "df_materiel_pdc" not in st.session_state or not isinstance(st.session_state.df_materiel_pdc, pd.DataFrame):
            init_materiel = [
                {
                    "Type": "Matériel de traitement",
                    "Désignation": "Pulvérisateur à dos",
                    "Quantité": 1,
                    "Année acquisition": 2022,
                    "Coût (FCFA)": 35000,
                    "État": "Bon",
                }
            ]
            st.session_state.df_materiel_pdc = pd.DataFrame(init_materiel)

        # ---------------------------------------------------------
        # 13.1 SYSTÈME DE CULTURES & REVENUS
        # ---------------------------------------------------------
        st.markdown("### 🌾 1.3.1 Diversification & Cultures de l'Exploitation")

        df_cultures_edite = st.data_editor(
            st.session_state.df_cultures_pdc,
            key="editor_cultures_pdc",
            column_config={
                "Culture": st.column_config.TextColumn(
                    "Culture / Parcelle", disabled=False
                ),
                "Superficie (ha)": st.column_config.NumberColumn(
                    "Superficie (ha)", min_value=0.0, step=0.1, format="%.2f ha"
                ),
                "Année de création": st.column_config.NumberColumn(
                    "Année", min_value=1960, max_value=2030, step=1
                ),
                "Source matériel végétal": st.column_config.SelectboxColumn(
                    "Source plants/semences",
                    options=[
                        "SATMACI / ANADER / CNRA",
                        "Tout venant",
                        "Pépiniériste privé",
                    ],
                    default="SATMACI / ANADER / CNRA",
                ),
                "Production campagne préc. (kg)": st.column_config.NumberColumn(
                    "Prod. Précédente (kg)", min_value=0, step=50, format="%d kg"
                ),
                "Revenu (FCFA)": st.column_config.NumberColumn(
                    "Revenu estimé (FCFA)",
                    min_value=0,
                    step=25000,
                    format="%d FCFA",
                ),
            },
            use_container_width=True,
            num_rows="dynamic",
        )

        st.markdown("---")

        # ---------------------------------------------------------
        # 13.2 ARBRES ASSOCIÉS & INVENTAIRE AGROFORESTIER
        # ---------------------------------------------------------
        st.markdown(
            "### 🌳 1.3.2 Inventaire des Arbres hors Cacaoyer (Normes CCC)"
        )
        st.caption(
            "Renseignez les arbres d'ombrage ou forestiers présents dans la"
            " cacaoyère et la décision d'aménagement."
        )

        df_arbres_edite = st.data_editor(
            st.session_state.df_arbres_pdc,
            key="editor_arbres_pdc",
            column_config={
                "Nom de l'arbre": st.column_config.TextColumn(
                    "Essence / Nom", required=True
                ),
                "Nombre": st.column_config.NumberColumn(
                    "Pieds", min_value=1, step=1
                ),
                "Latitude (N)": st.column_config.NumberColumn(
                    "Lat (N)", format="%.6f"
                ),
                "Longitude (W)": st.column_config.NumberColumn(
                    "Long (W)", format="%.6f"
                ),
                "Statut actuel": st.column_config.SelectboxColumn(
                    "Statut",
                    options=["Préservé", "Planté", "Régénération naturelle"],
                    default="Préservé",
                ),
                "Rôle / Avantage": st.column_config.SelectboxColumn(
                    "Rôle pour cacaoyer",
                    options=[
                        "Bois d'œuvre",
                        "Fertilité du sol",
                        "Produit secondaire (PNFL)",
                        "Ombrage excessif / Hôte pucerons",
                    ],
                    default="Bois d'œuvre",
                ),
                "Décision": st.column_config.SelectboxColumn(
                    "Action préconisée",
                    options=["À maintenir", "À éliminer", "À élaguer"],
                    default="À maintenir",
                ),
                "Remarque / Distance": st.column_config.TextColumn(
                    "Remarques terrain"
                ),
            },
            use_container_width=True,
            num_rows="dynamic",
        )

        st.markdown("---")

        # ---------------------------------------------------------
        # 13.3 MATÉRIEL ET ÉQUIPEMENTS AGRICOLES
        # ---------------------------------------------------------
        st.markdown("### 🚜 1.3.3 Matériel Agricole & Équipements")

        df_mat_edite = st.data_editor(
            st.session_state.df_materiel_pdc,
            key="editor_materiel_pdc",
            column_config={
                "Type": st.column_config.SelectboxColumn(
                    "Type d'équipement",
                    options=[
                        "Matériel de traitement",
                        "Matériel de récolte / Entretien",
                        "Matériel de transport",
                        "Moyen de déplacement",
                    ],
                    default="Matériel de traitement",
                ),
                "Désignation": st.column_config.TextColumn(
                    "Désignation du matériel", required=True
                ),
                "Quantité": st.column_config.NumberColumn(
                    "Qté", min_value=0, step=1
                ),
                "Année acquisition": st.column_config.NumberColumn(
                    "Année", min_value=1990, max_value=2030, step=1
                ),
                "Coût (FCFA)": st.column_config.NumberColumn(
                    "Valeur / Coût", min_value=0, step=5000, format="%d FCFA"
                ),
                "État": st.column_config.SelectboxColumn(
                    "État d'usure",
                    options=["Bon", "Acceptable", "Mauvais"],
                    default="Bon",
                ),
            },
            use_container_width=True,
            num_rows="dynamic",
        )

        # ---------------------------------------------------------
        # SYNTHÈSE AUTOMATIQUE DE L'ÉTAPE 13 (SÉCURISÉE)
        # ---------------------------------------------------------
        df_cult_calc = pd.DataFrame(df_cultures_edite)
        df_arb_calc = pd.DataFrame(df_arbres_edite)

        tot_revenu_agri = 0
        tot_prod_cacao = 0

        if not df_cult_calc.empty:
            if "Revenu (FCFA)" in df_cult_calc.columns:
                tot_revenu_agri = int(
                    pd.to_numeric(
                        df_cult_calc["Revenu (FCFA)"], errors="coerce"
                    ).fillna(0).sum()
                )

            if (
                "Culture" in df_cult_calc.columns
                and "Production campagne préc. (kg)" in df_cult_calc.columns
            ):
                cacao_mask = df_cult_calc["Culture"].astype(str).str.contains(
                    "Cacao", case=False, na=False
                )
                tot_prod_cacao = int(
                    pd.to_numeric(
                        df_cult_calc.loc[
                            cacao_mask, "Production campagne préc. (kg)"
                        ],
                        errors="coerce",
                    ).fillna(0).sum()
                )

        tot_arbres_maintenir = 0
        tot_arbres_eliminer = 0

        if not df_arb_calc.empty and "Nombre" in df_arb_calc.columns and "Décision" in df_arb_calc.columns:
            df_arb_calc["Nombre_clean"] = pd.to_numeric(
                df_arb_calc["Nombre"], errors="coerce"
            ).fillna(1)
            
            tot_arbres_maintenir = int(
                df_arb_calc[df_arb_calc["Décision"] == "À maintenir"][
                    "Nombre_clean"
                ].sum()
            )
            tot_arbres_eliminer = int(
                df_arb_calc[
                    df_arb_calc["Décision"].isin(["À éliminer", "À élaguer"])
                ]["Nombre_clean"].sum()
            )

        st.markdown("#### 📊 Bilan Synthétique de l'Étape 13")
        kpi_e1, kpi_e2, kpi_e3 = st.columns(3)
        kpi_e1.metric("Production Cacao Totale", f"{tot_prod_cacao:,} kg".replace(",", " "))
        kpi_e2.metric("Revenu Agricole Global", f"{tot_revenu_agri:,} FCFA".replace(",", " "))
        kpi_e3.metric(
            "Bilan Agroforesterie",
            f"{tot_arbres_maintenir} à maintenir",
            f"{tot_arbres_eliminer} à éliminer/élaguer",
        )

        st.markdown("---")

        # =========================================================
        # NAVIGATION DE L'ÉTAPE 13
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button(
                "⬅️ Retour",
                key="btn_retour_etape13",
                use_container_width=True,
            ):
                st.session_state.df_cultures_pdc = pd.DataFrame(df_cultures_edite)
                st.session_state.df_arbres_pdc = pd.DataFrame(df_arbres_edite)
                st.session_state.df_materiel_pdc = pd.DataFrame(df_mat_edite)
                st.session_state.etape_pdc = 12
                st.rerun()

        with col_btn2:
            if st.button(
                "Suivant ➡️",
                key="btn_suivant_etape13",
                type="primary",
                use_container_width=True,
            ):
                # Mise à jour des DataFrames dans session_state
                st.session_state.df_cultures_pdc = pd.DataFrame(df_cultures_edite)
                st.session_state.df_arbres_pdc = pd.DataFrame(df_arbres_edite)
                st.session_state.df_materiel_pdc = pd.DataFrame(df_mat_edite)

                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Conversion sérialisable en dictionnaires
                st.session_state.reponses_pdc["cultures_et_revenus"] = (
                    df_cultures_edite.to_dict("records") if isinstance(df_cultures_edite, pd.DataFrame) else df_cultures_edite
                )
                st.session_state.reponses_pdc["inventaire_arbres"] = (
                    df_arbres_edite.to_dict("records") if isinstance(df_arbres_edite, pd.DataFrame) else df_arbres_edite
                )
                st.session_state.reponses_pdc["materiel_agricole"] = (
                    df_mat_edite.to_dict("records") if isinstance(df_mat_edite, pd.DataFrame) else df_mat_edite
                )

                st.session_state.etape_pdc = 14
                st.rerun()


    # =========================================================
    # ÉTAPE 14 : PLANIFICATION STRATÉGIQUE & PROGRAMME ANNUEL
    # =========================================================
    elif st.session_state.etape_pdc == 14:
        st.subheader(
            "Étape 14/15 : Planification Stratégique (5 Ans) & Programme Annuel"
            " d'Action"
        )
        st.caption(
            "Définition du plan quinquennal, du chronogramme opérationnel"
            " trimestriel et des facteurs clés de succès du PDC."
        )

        # --- Initialisation Sécurisée du Session State (DataFrames) ---
        if "df_plan_quinquennal" not in st.session_state or not isinstance(st.session_state.df_plan_quinquennal, pd.DataFrame):
            init_quinquennal = [
                {
                    "Stratégie / Axe": "Axe 1 : Réhabilitation du verger",
                    "Objectifs": "Restaurer la productivité des parcelles anciennes",
                    "Activités": "Régler la densité (égourmandage, égrapillage)",
                    "Coût (FCFA)": 150000,
                    "A1": True,
                    "A2": True,
                    "A3": False,
                    "A4": False,
                    "A5": False,
                    "Exécutant": "Producteur + M.O.",
                    "Partenaires": "Coopérative / ANADER",
                },
                {
                    "Stratégie / Axe": "Axe 1 : Réhabilitation du verger",
                    "Objectifs": "Réduire la pression parasitaire et parasitaire",
                    "Activités": "Taille des loranthacées (guis) et sanitation",
                    "Coût (FCFA)": 100000,
                    "A1": True,
                    "A2": True,
                    "A3": True,
                    "A4": False,
                    "A5": False,
                    "Exécutant": "Producteur",
                    "Partenaires": "ANADER",
                },
                {
                    "Stratégie / Axe": "Axe 2 : Plantation / Replantation",
                    "Objectifs": "Renouveler 2 ha en agroforesterie",
                    "Activités": "Replanter 2 ha avec espèces d'ombrage (Akpi/Iroko)",
                    "Coût (FCFA)": 600000,
                    "A1": False,
                    "A2": True,
                    "A3": True,
                    "A4": False,
                    "A5": False,
                    "Exécutant": "Producteur",
                    "Partenaires": "Conseil Café-Cacao",
                },
                {
                    "Stratégie / Axe": "Axe 3 : Diversification",
                    "Objectifs": "Sécuriser les revenus hors saison cacao",
                    "Activités": "Mise en place d'une parcelle vivrière (Banane/Piment)",
                    "Coût (FCFA)": 200000,
                    "A1": True,
                    "A2": False,
                    "A3": False,
                    "A4": False,
                    "A5": False,
                    "Exécutant": "Famille / Ménage",
                    "Partenaires": "Coopérative",
                },
            ]
            st.session_state.df_plan_quinquennal = pd.DataFrame(init_quinquennal)

        if "df_programme_annuel" not in st.session_state or not isinstance(st.session_state.df_programme_annuel, pd.DataFrame):
            init_programme = [
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Activités / Sous-activités": "Régler la densité (égourmandage, échenillonnage)",
                    "Indicateur": "Nombre d'hectares traités (ex: 3.5 ha)",
                    "T1": True,
                    "T2": True,
                    "T3": False,
                    "T4": False,
                    "Coût (FCFA)": 75000,
                },
                {
                    "Axes stratégiques": "Axe 1 : Réhabilitation du verger",
                    "Activités / Sous-activités": "Réaliser la taille des loranthacées",
                    "Indicateur": "Taux d'arbres nettoyés (%)",
                    "T1": False,
                    "T2": True,
                    "T3": True,
                    "T4": False,
                    "Coût (FCFA)": 50000,
                },
                {
                    "Axes stratégiques": "Axe 3 : Diversification",
                    "Activités / Sous-activités": "Préparation terrain & planting banane/piment",
                    "Indicateur": "Superficie installée (ha)",
                    "T1": True,
                    "T2": False,
                    "T3": False,
                    "T4": False,
                    "Coût (FCFA)": 150000,
                },
            ]
            st.session_state.df_programme_annuel = pd.DataFrame(init_programme)

        # ---------------------------------------------------------
        # 14.1 PLANIFICATION STRATÉGIQUE SUR 5 ANS
        # ---------------------------------------------------------
        st.markdown(
            "### 📈 II - Planification Stratégique sur les Cinq (5) Prochaines"
            " Années"
        )
        st.caption(
            "Précisez les axes, objectifs, activités, budgets et responsables sur"
            " l'horizon 5 ans (A1 à A5)."
        )

        df_quinquennal_edite = st.data_editor(
            st.session_state.df_plan_quinquennal,
            key="editor_plan_quinquennal",
            column_config={
                "Stratégie / Axe": st.column_config.SelectboxColumn(
                    "Axe Stratégique",
                    options=[
                        "Axe 1 : Réhabilitation du verger",
                        "Axe 2 : Plantation / Replantation",
                        "Axe 3 : Diversification",
                    ],
                    required=True,
                ),
                "Objectifs": st.column_config.TextColumn("Objectifs visés"),
                "Activités": st.column_config.TextColumn(
                    "Activités à mener", required=True
                ),
                "Coût (FCFA)": st.column_config.NumberColumn(
                    "Coût estimé (FCFA)",
                    min_value=0,
                    step=25000,
                    format="%d FCFA",
                ),
                "A1": st.column_config.CheckboxColumn("Année 1"),
                "A2": st.column_config.CheckboxColumn("Année 2"),
                "A3": st.column_config.CheckboxColumn("Année 3"),
                "A4": st.column_config.CheckboxColumn("Année 4"),
                "A5": st.column_config.CheckboxColumn("Année 5"),
                "Exécutant": st.column_config.TextColumn("Exécutant principal"),
                "Partenaires": st.column_config.TextColumn("Partenaires appui"),
            },
            use_container_width=True,
            num_rows="dynamic",
        )

        st.markdown("---")

        # =========================================================
        # 14.2 PROGRAMME ANNUEL D'ACTION (CHRONOGRAMME A1)
        # =========================================================
        st.markdown("### 🗓️ III - Programme Annuel d'Action (Détail Année 1)")
        st.caption(
            "Planification opérationnelle par trimestre (T1 à T4) pour la première"
            " année de mise en œuvre."
        )

        df_annuel_edite = st.data_editor(
            st.session_state.df_programme_annuel,
            key="editor_programme_annuel",
            column_config={
                "Axes stratégiques": st.column_config.TextColumn(
                    "Axe Stratégique", required=True
                ),
                "Activités / Sous-activités": st.column_config.TextColumn(
                    "Activités / Sous-activités", required=True
                ),
                "Indicateur": st.column_config.TextColumn("Indicateur de suivi"),
                "T1": st.column_config.CheckboxColumn("T1 (Jan-Mar)"),
                "T2": st.column_config.CheckboxColumn("T2 (Avr-Juin)"),
                "T3": st.column_config.CheckboxColumn("T3 (Juil-Sept)"),
                "T4": st.column_config.CheckboxColumn("T4 (Oct-Déc)"),
                "Coût (FCFA)": st.column_config.NumberColumn(
                    "Coût Trimestriel (FCFA)",
                    min_value=0,
                    step=10000,
                    format="%d FCFA",
                ),
            },
            use_container_width=True,
            num_rows="dynamic",
        )

        st.markdown("---")

        # =========================================================
        # 14.3 FACTEURS DE SUCCÈS ET D'ÉCHEC
        # =========================================================
        st.markdown("### ⚠️ IV - Facteurs de Succès et d'Échec")
        st.caption(
            "Décrivez les conditions indispensables pour une mise en œuvre efficace"
            " du plan de développement."
        )

        def_facteurs = (
            "1. Accès à temps aux intrants homologués (engrais/fongicides) et plants"
            " d'arbres d'ombrage.\n2. Disponibilité de la main-d'œuvre familiale et"
            " occasionnelle qualifiée pour la taille.\n3. Accompagnement technique"
            " régulier par le conseiller agricole de la coopérative / ANADER.\n4."
            " Maîtrise de la trésorerie et accès au crédit / préfinancement des"
            " activités de réhabilitation.\n5. Conditions climatiques favorables"
            " (pluviométrie régulière et absence de sécheresse sévère)."
        )

        facteurs_succes = st.text_area(
            "Conditions indispensables & risques identifiés",
            value=st.session_state.get("facteurs_succes_pdc", def_facteurs),
            height=150,
            key="input_facteurs_succes",
        )

        # ---------------------------------------------------------
        # SYNTHÈSE FINANCIÈRE DE LA PLANIFICATION (SÉCURISÉE)
        # ---------------------------------------------------------
        df_quinq_calc = pd.DataFrame(df_quinquennal_edite)
        df_ann_calc = pd.DataFrame(df_annuel_edite)

        cout_total_5ans = 0
        if not df_quinq_calc.empty and "Coût (FCFA)" in df_quinq_calc.columns:
            cout_total_5ans = int(
                pd.to_numeric(
                    df_quinq_calc["Coût (FCFA)"], errors="coerce"
                ).fillna(0).sum()
            )

        cout_total_a1 = 0
        if not df_ann_calc.empty and "Coût (FCFA)" in df_ann_calc.columns:
            cout_total_a1 = int(
                pd.to_numeric(
                    df_ann_calc["Coût (FCFA)"], errors="coerce"
                ).fillna(0).sum()
            )

        st.markdown("#### 📊 Synthèse Budgétaire de la Planification")
        kpi_p1, kpi_p2 = st.columns(2)
        kpi_p1.metric(
            "Budget Plan Quinquennal (5 Ans)",
            f"{cout_total_5ans:,} FCFA".replace(",", " ")
        )
        kpi_p2.metric(
            "Budget Année 1 (Programme d'Action)",
            f"{cout_total_a1:,} FCFA".replace(",", " ")
        )

        st.markdown("---")

        # =========================================================
        # NAVIGATION DE L'ÉTAPE 14
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button(
                "⬅️ Retour",
                key="btn_retour_etape14",
                use_container_width=True,
            ):
                st.session_state.df_plan_quinquennal = pd.DataFrame(df_quinquennal_edite)
                st.session_state.df_programme_annuel = pd.DataFrame(df_annuel_edite)
                st.session_state["facteurs_succes_pdc"] = facteurs_succes
                st.session_state.etape_pdc = 13
                st.rerun()

        with col_btn2:
            if st.button(
                "Suivant ➡️",
                key="btn_suivant_etape14",
                type="primary",
                use_container_width=True,
            ):
                # Mise à jour des objets DataFrames dans session_state
                st.session_state.df_plan_quinquennal = pd.DataFrame(df_quinquennal_edite)
                st.session_state.df_programme_annuel = pd.DataFrame(df_annuel_edite)
                st.session_state["facteurs_succes_pdc"] = facteurs_succes

                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Conversion sérialisable en dictionnaires
                st.session_state.reponses_pdc["plan_quinquennal"] = (
                    df_quinquennal_edite.to_dict("records")
                    if isinstance(df_quinquennal_edite, pd.DataFrame)
                    else df_quinquennal_edite
                )
                st.session_state.reponses_pdc["programme_annuel"] = (
                    df_annuel_edite.to_dict("records")
                    if isinstance(df_annuel_edite, pd.DataFrame)
                    else df_annuel_edite
                )
                st.session_state.reponses_pdc["facteurs_succes"] = facteurs_succes

                st.session_state.etape_pdc = 15
                st.rerun()


    # ---------------------------------------------------------
    # ÉTAPE 15 : RÉSUMÉ GLOBAL, ÉVALUATION DU SUCCÈS & GÉNÉRATION DU PDC FINAL
    # (SYNTHÈSE DU PLAN DE DÉVELOPPEMENT DE CONSEIL)
    # ---------------------------------------------------------
    elif st.session_state.etape_pdc == 15:
        st.subheader(
            "Étape 15/15 : Bilan Synthétique, Faisabilité & Validation du PDC"
        )
        st.caption(
            "Évaluation de la viabilité du plan, score de réussite prévisionnel et"
            " impression du document final."
        )

        # Récupération sécurisée des données
        reponses = st.session_state.get("reponses_pdc", {})

        # =========================================================
        # 15.1 SYNTHÈSE & RÉSUMÉ DES MODULES
        # =========================================================
        st.markdown("### 📋 1. Synthèse Générale de l'Exploitation")

        # Calculs de synthèse sécurisés
        df_cult = pd.DataFrame(reponses.get("cultures_et_revenus", []))
        df_quinq = pd.DataFrame(reponses.get("plan_quinquennal", []))
        df_ann = pd.DataFrame(reponses.get("programme_annuel", []))
        df_arb = pd.DataFrame(reponses.get("inventaire_arbres", []))

        tot_revenu_actuel = 0
        if not df_cult.empty and "Revenu (FCFA)" in df_cult.columns:
            tot_revenu_actuel = int(
                pd.to_numeric(df_cult["Revenu (FCFA)"], errors="coerce").fillna(0).sum()
            )

        tot_cout_quinq = 0
        if not df_quinq.empty and "Coût (FCFA)" in df_quinq.columns:
            tot_cout_quinq = int(
                pd.to_numeric(df_quinq["Coût (FCFA)"], errors="coerce").fillna(0).sum()
            )

        tot_cout_a1 = 0
        if not df_ann.empty and "Coût (FCFA)" in df_ann.columns:
            tot_cout_a1 = int(
                pd.to_numeric(df_ann["Coût (FCFA)"], errors="coerce").fillna(0).sum()
            )

        nb_arbres_maintenus = 0
        if not df_arb.empty and "Décision" in df_arb.columns:
            mask_maint = df_arb["Décision"] == "À maintenir"
            if "Nombre" in df_arb.columns:
                nb_arbres_maintenus = int(
                    pd.to_numeric(df_arb.loc[mask_maint, "Nombre"], errors="coerce").fillna(1).sum()
                )
            else:
                nb_arbres_maintenus = int(mask_maint.sum())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Revenu Actuel", f"{tot_revenu_actuel:,} FCFA".replace(",", " "))
        c2.metric("Budget Quinquennal", f"{tot_cout_quinq:,} FCFA".replace(",", " "))
        c3.metric("Investissement A1", f"{tot_cout_a1:,} FCFA".replace(",", " "))
        c4.metric("Arbres Conservés", f"{nb_arbres_maintenus} pieds")

        st.markdown("---")

        # =========================================================
        # 15.2 ÉVALUATION DE LA RÉUSSITE ET DE LA VIABILITÉ DU PDC
        # =========================================================
        st.markdown(
            "### 📊 2. Évaluation de la Faisabilité & Diagnostic de Réussite"
        )
        st.caption(
            "Analyse des critères de viabilité financière, technique et sociale du"
            " producteur."
        )

        # Calcul automatique d'un score de faisabilité (Base 100)
        score = 0
        criteres = []

        # Critère 1 : Capacité financière
        ratio_invest = (
            (tot_cout_a1 / tot_revenu_actuel) if tot_revenu_actuel > 0 else 1.0
        )
        if ratio_invest <= 0.4:
            score += 35
            criteres.append(
                "✅ **Capacité financière solide** : Le coût de l'Année 1 représente"
                " moins de 40% des revenus actuels."
            )
        elif ratio_invest <= 0.7:
            score += 20
            criteres.append(
                "⚠️ **Capacité financière moyenne** : L'investissement A1 nécessite"
                " un préfinancement ou un crédit léger."
            )
        else:
            score += 10
            criteres.append(
                "❌ **Tension de trésorerie** : L'investissement A1 dépasse 70% du"
                " revenu actuel (Besoin urgent d'appui/subvention)."
            )

        # Critère 2 : Agroforesterie & Normes Durables
        if nb_arbres_maintenus >= 10:
            score += 35
            criteres.append(
                "✅ **Norme Agroforesterie respectée** : Densité d'ombrage conforme"
                " aux directives CCC (>10 pieds/ha)."
            )
        else:
            score += 15
            criteres.append(
                "⚠️ **Agroforesterie à renforcer** : Prévoir l'introduction d'arbres"
                " d'ombrage supplémentaires."
            )

        # Critère 3 : Planification et Clarté des Objectifs
        if len(df_quinq) >= 3 and len(df_ann) >= 2:
            score += 30
            criteres.append(
                "✅ **Plan d'Action Complet** : Les axes de réhabilitation,"
                " replantation et diversification sont structurés."
            )
        else:
            score += 15
            criteres.append(
                "⚠️ **Plan d'Action partiel** : Compléter les activités"
                " trimestrielles pour garantir le suivi."
            )

        # Affichage du Score et du Statut de Réussite
        st.markdown(f"#### Score de Faisabilité Global : **{score} / 100**")
        st.progress(score / 100)

        if score >= 85:
            st.success(
                "🎉 **PDC Très Viable (Très Forte Chance de Réussite)** : Le"
                " producteur dispose de toutes les conditions pour exécuter son"
                " plan avec succès et améliorer durablement ses conditions de vie."
            )
        elif score >= 60:
            st.info(
                "👍 **PDC Viable sous conditions** : Le plan est réalisable, mais"
                " nécessite un accompagnement technique soutenu et un suivi de la"
                " trésorerie."
            )
        else:
            st.warning(
                "⚠️ **Risque Élevé d'Échec** : Ajuster les ambitions financières ou"
                " rechercher des partenaires/coopératives pour cofinancer l'Année"
                " 1."
            )

        st.markdown("**Détails du Diagnostic :**")
        for crit in criteres:
            st.markdown(f"- {crit}")

        st.markdown("---")

        # =========================================================
        # 15.3 RECOMMANDATIONS ET CONCLUSION
        # =========================================================
        st.markdown("### 💡 3. Recommandations du Conseiller Agricole")
        recom_def = (
            "1. Prioriser les travaux d'assainissement sanitaire (taille des"
            " loranthacées) dès le T1.\n2. Sécuriser les plants d'arbres d'ombrage"
            " auprès des pépinières agréées par le Conseil Café-Cacao.\n3. Veiller à"
            " la scolarisation effective des enfants du ménage conformément aux"
            " engagements sociaux du PDC.\n4. Faire un point trimestriel avec le"
            " conseiller de la coopérative pour valider le chronogramme T1 à T4."
        )
        recommandations_finales = st.text_area(
            "Recommandations stratégiques à l'attention du producteur",
            value=st.session_state.get("recommandations_finales_pdc", recom_def),
            height=120,
            key="txt_recom_finales",
        )

        st.markdown("---")

        # =========================================================
        # 15.4 SIGNATURES TACTILES DES PARTIES
        # =========================================================
        st.markdown("### ✍️ 4. Validation & Signatures Tactiles")
        st.caption("Signez directement avec le doigt ou un stylet sur les cadres ci-dessous.")

        st.info(
            "📜 **Engagement :** Je soussigné(e) confirme avoir pris connaissance "
            "du diagnostic de mon exploitation et valide le plan d'action quinquennal établi."
        )

        col_sig_prod, col_sig_cons = st.columns(2)

        # Zone 1 : Signature du Producteur
        with col_sig_prod:
            st.markdown("#### 🖊️ Signature du Producteur")
            nom_producteur = st.text_input(
                "Nom du Producteur",
                value=st.session_state.get("nom_producteur_pdc", "Nom et Prénom"),
                key="input_nom_producteur_sig"
            )
            st.caption("Tracez la signature du producteur ci-dessous :")
            canvas_producteur = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=2,
                stroke_color="#000000",
                background_color="#f0f2f6",
                height=150,
                width=300,
                drawing_mode="freedraw",
                key="canvas_prod",
            )

        # Zone 2 : Signature du Technicien 
        with col_sig_cons:
            st.markdown("#### 🖊️ Signature du Technicien")
            nom_technicien = st.text_input(
                "Nom du Technicien",
                value=st.session_state.get("nom_conseiller_pdc", ""),
                placeholder="Ex: Kouassi Yao",
                key="input_nom_technicien_sig"
            )
            st.caption("Tracez la signature du technicien ci-dessous :")
            canvas_technicien = st_canvas(
                fill_color="rgba(255, 255, 255, 0)",
                stroke_width=2,
                stroke_color="#084081",
                background_color="#f0f2f6",
                height=150,
                width=300,
                drawing_mode="freedraw",
                key="canvas_cons",
            )

        st.markdown("---")


        # =========================================================
        # NAVIGATION ET ENREGISTREMENT DE L'ÉTAPE 15
        # =========================================================
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("⬅️ Retour", key="btn_retour_etape15", use_container_width=True):
                st.session_state["recommandations_finales_pdc"] = recommandations_finales
                st.session_state.etape_pdc = 14
                st.rerun()

        with col_btn2:
            if st.button(
                "💾 Valider & Finaliser le PDC",
                key="btn_valider_pdc_final",
                type="primary",
                use_container_width=True,
            ):
                if "reponses_pdc" not in st.session_state:
                    st.session_state.reponses_pdc = {}

                # Sauvegarde globale des textes
                st.session_state["recommandations_finales_pdc"] = recommandations_finales
                st.session_state.reponses_pdc["recommandations_finales"] = recommandations_finales
                st.session_state.reponses_pdc["score_faisabilite"] = score
                st.session_state.reponses_pdc["criteres_faisabilite"] = criteres

                # Fonction de récupération sécurisée
                def extraire_image_signature(canvas_obj):
                    if canvas_obj is None:
                        return None
                    
                    has_drawing = False
                    try:
                        if hasattr(canvas_obj, "json_data") and canvas_obj.json_data is not None:
                            objects = canvas_obj.json_data.get("objects", [])
                            if len(objects) > 0:
                                has_drawing = True
                    except Exception:
                        pass

                    if not has_drawing:
                        return None

                    try:
                        img_array = canvas_obj.image_data
                        if img_array is not None and isinstance(img_array, np.ndarray):
                            if img_array.size > 0:
                                return img_array
                    except Exception:
                        pass

                    return "SIGNATURE_PRESENTE"

                # Extractions sécurisées
                img_sig_prod = extraire_image_signature(canvas_producteur)
                img_sig_tech = extraire_image_signature(canvas_technicien)

                # Enregistrement des données des signataires
                st.session_state.reponses_pdc["signataires"] = {
                    "producteur_nom": nom_producteur,
                    "producteur_signature": img_sig_prod,
                    "technicien_nom": nom_technicien,
                    "technicien_signature": img_sig_tech,
                    "date_validation": pd.Timestamp.now().strftime("%d/%m/%Y à %H:%M")
                }

                st.session_state["pdc_finalise"] = True
                st.success("✅ PDC finalisé avec succès ! Les signatures tactiles ont été enregistrées.")
