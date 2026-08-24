import streamlit as st
import os
import sqlite3
import time
import math
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from shapely.geometry import Polygon, Point
from datetime import datetime

# =========================================================================
# --- 1. RÉFÉRENTIELS (EUDR, PARCS, FORÊTS & AGRO-FORÊTS) ---
# =========================================================================
parcs_et_reserves = {
    "Parc National de Taï (Sud-Ouest / Cavally-Sassandra)": Polygon([(-7.50, 6.10), (-6.80, 6.10), (-6.75, 5.80), (-6.70, 5.15), (-7.20, 5.15), (-7.55, 5.40), (-7.50, 6.10)]),
    "Parc National de la Marahoué (Centre-Ouest)": Polygon([(-6.15, 7.15), (-5.85, 7.15), (-5.80, 6.80), (-6.10, 6.80), (-6.15, 7.15)]),
    "Parc National de Comoé (Nord-Est / Zanzan)": Polygon([(-4.50, 9.80), (-3.10, 9.80), (-3.10, 8.50), (-4.50, 8.50), (-4.50, 9.80)]),
    "Parc National d'Azagny (Sud / Littoral / Grand-Lahou)": Polygon([(-5.42, 5.30), (-5.15, 5.30), (-5.15, 5.10), (-5.42, 5.10), (-5.42, 5.30)]),
    "Parc National du Banco (Abidjan / Sud)": Polygon([(-4.10, 5.43), (-4.01, 5.43), (-4.01, 5.35), (-4.10, 5.35), (-4.10, 5.43)]),
    "Parc National du Mont Péko (Ouest / Guiglo)": Polygon([(-7.30, 7.20), (-6.95, 7.20), (-6.95, 6.90), (-7.30, 6.90), (-7.30, 7.20)]),
    "Parc National du Mont Sangbé (Ouest / Tonkpi)": Polygon([(-7.60, 8.10), (-7.10, 8.10), (-7.10, 7.70), (-7.60, 7.70), (-7.60, 8.10)]),
    "Parc National de l'Isles de Ehotilé (Sud-Est / Aboisso)": Polygon([(-3.30, 5.18), (-3.15, 5.18), (-3.15, 5.10), (-3.30, 5.10), (-3.30, 5.18)]),
    "Réserve Scientifique de Lamto (V-Baoulé / Tiassalé-Toumodi)": Polygon([(-5.05, 6.25), (-4.95, 6.25), (-4.95, 6.18), (-5.05, 6.18), (-5.05, 6.25)]),
    "Réserve de Faune du Haut-Bandama (Centre-Nord)": Polygon([(-5.70, 8.70), (-5.20, 8.70), (-5.20, 8.10), (-5.70, 8.10), (-5.70, 8.70)]),
    "Réserve Naturelle Intégrale du Mont Nimba (Extrême Ouest)": Polygon([(-8.45, 7.70), (-8.35, 7.70), (-8.35, 7.55), (-8.45, 7.55), (-8.45, 7.70)]),
    "Réserve Naturelle de Mabi-Yaya (Sud-Est / Mé / Indénié)": Polygon([(-3.55, 6.15), (-3.15, 6.15), (-3.15, 5.65), (-3.55, 5.65), (-3.55, 6.15)]),
}

forets_classees = {
    "Forêt Classée de la Niégré (Bas-Sassandra / Soubré / San-Pédro)": Polygon([(-6.65, 5.40), (-6.15, 5.40), (-6.15, 4.90), (-6.65, 4.90), (-6.65, 5.40)]),
    "Forêt Classée de Rapides Grah (Sassandra / San-Pédro)": Polygon([(-7.10, 5.20), (-6.50, 5.20), (-6.50, 4.70), (-7.10, 4.70), (-7.10, 5.20)]),
    "Forêt Classée du Haut-Sassandra (Vavoua / Daloa)": Polygon([(-7.10, 7.45), (-6.70, 7.45), (-6.70, 6.90), (-7.10, 6.90), (-7.10, 7.45)]),
    "Forêt Classée de Tai / Hana (Zone Tampon Sud-Ouest)": Polygon([(-7.35, 5.25), (-6.95, 5.25), (-6.95, 4.95), (-7.35, 4.95), (-7.35, 5.25)]),
    "Forêt Classée de Monogaga (Littoral / San-Pédro)": Polygon([(-6.60, 4.90), (-6.30, 4.90), (-6.30, 4.75), (-6.60, 4.75), (-6.60, 4.90)]),
    "Forêt Classée de Goin-Débé (Cavally / Guiglo / Ouest)": Polygon([(-7.90, 6.20), (-7.30, 6.20), (-7.30, 5.70), (-7.90, 5.70), (-7.90, 6.20)]),
    "Forêt Classée de Cavally (Ouest / Zéaglo / Blolequin)": Polygon([(-7.95, 6.60), (-7.40, 6.60), (-7.40, 6.10), (-7.95, 6.10), (-7.95, 6.60)]),
    "Forêt Classée de Scio (Guémon / Duékoué)": Polygon([(-7.70, 7.00), (-7.20, 7.00), (-7.20, 6.60), (-7.70, 6.60), (-7.70, 7.00)]),
    "Forêt Classée de Sangouiné (Man / Ouest)": Polygon([(-7.75, 7.50), (-7.40, 7.50), (-7.40, 7.20), (-7.75, 7.20), (-7.75, 7.50)]),
    "Forêt Classée de Klon (Zone Ouest / Danané)": Polygon([(-8.20, 7.30), (-7.90, 7.30), (-7.90, 7.05), (-8.20, 7.05), (-8.20, 7.30)]),
    "Forêt Classée de Bossématié (Abengourou / Centre-Est)": Polygon([(-3.60, 6.50), (-3.30, 6.50), (-3.30, 6.20), (-3.60, 6.20), (-3.60, 6.50)]),
    "Forêt Classée de Béki (Abengourou / Akoupé)": Polygon([(-3.85, 6.45), (-3.60, 6.45), (-3.60, 6.15), (-3.85, 6.15), (-3.85, 6.45)]),
    "Forêt Classée de Brassué (Région Daoukro / Centre-Est)": Polygon([(-4.10, 7.35), (-3.80, 7.35), (-3.80, 7.05), (-4.10, 7.05), (-4.10, 7.35)]),
    "Forêt Classée de Fetekro (Bouaké / M'Bahiakro)": Polygon([(-4.85, 7.80), (-4.60, 7.80), (-4.60, 7.50), (-4.85, 7.50), (-4.85, 7.80)]),
    "Forêt Classée de Dogodou (Gôh / Gagnoa / Lakota)": Polygon([(-5.75, 5.95), (-5.45, 5.95), (-5.45, 5.70), (-5.75, 5.70), (-5.75, 5.95)]),
    "Forêt Classée de Koko (Lôh-Djiboua / Divo / Tiassalé)": Polygon([(-5.20, 5.90), (-4.95, 5.90), (-4.95, 5.65), (-5.20, 5.65), (-5.20, 5.90)]),
    "Forêt Classée de Gasso (Agnéby-Tiassa / Agboville)": Polygon([(-4.40, 6.00), (-4.10, 6.00), (-4.10, 5.75), (-4.40, 5.75), (-4.40, 6.00)]),
    "Forêt Classée d'Irobo (Zone Grand-Lahou / Sikensi)": Polygon([(-4.90, 5.55), (-4.60, 5.55), (-4.60, 5.30), (-4.90, 5.30), (-4.90, 5.55)]),
    "Forêt Classée de Yapo-Abbé (Agboville / Azaguié)": Polygon([(-4.15, 5.80), (-3.90, 5.80), (-3.90, 5.55), (-4.15, 5.55), (-4.15, 5.80)]),
    "Forêt Classée de la Téné (Oumé / Toumodi)": Polygon([(-5.45, 6.60), (-5.15, 6.60), (-5.15, 6.25), (-5.45, 6.25), (-5.45, 6.60)]),
    "Forêt Classée de Sangou (Région Oumé)": Polygon([(-5.60, 6.35), (-5.35, 6.35), (-5.35, 6.10), (-5.60, 6.10), (-5.60, 6.35)])
}

agroforets = {
    "Agro-forêt Classée d'Ahua (Centre / Dimbokro)": Polygon([(-4.85, 6.70), (-4.65, 6.70), (-4.65, 6.50), (-4.85, 6.50), (-4.85, 6.70)]),
    "Agro-forêt Classée de Port-Gauthier (Littoral / Grand-Lahou)": Polygon([(-5.30, 5.25), (-5.05, 5.25), (-5.05, 5.08), (-5.30, 5.08), (-5.30, 5.25)]),
    "Agro-forêt Classée de Délicat (Centre-Ouest / Bouaflé / Sinfra)": Polygon([(-6.00, 6.70), (-5.70, 6.70), (-5.70, 6.40), (-6.00, 6.40), (-6.00, 6.70)]),
    "Agro-forêt Classée de Bouaflé (Région de la Marahoué)": Polygon([(-5.95, 7.05), (-5.75, 7.05), (-5.75, 6.85), (-5.95, 6.85), (-5.95, 7.05)]),
    "Agro-forêt Classée de Monogaga (Option Agroforestière / San-Pédro)": Polygon([(-6.55, 4.85), (-6.35, 4.85), (-6.35, 4.76), (-6.55, 4.76), (-6.55, 4.85)]),
    "Agro-forêt Classée de Soubré (Nawa - Zone d'Intensification)": Polygon([(-6.75, 5.90), (-6.45, 5.90), (-6.45, 5.60), (-6.75, 5.60), (-6.75, 5.90)]),
    "Agro-forêt Classée du Goin-Débé (Zone Sud-Ouest / Cavally)": Polygon([(-7.85, 6.00), (-7.40, 6.00), (-7.40, 5.75), (-7.85, 5.75), (-7.85, 6.00)])
}

# =========================================================================
# --- 2. FONCTIONS DE CALCULS, BDD & ANALYSES ---
# =========================================================================
def init_db():
    """Initialise la table des relevés géographiques dans SQLite."""
    conn = sqlite3.connect("leyla_terrain.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geolocalisations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_creation TEXT,
            producteur TEXT,
            localite TEXT,
            superficie_ha REAL,
            altitude_m INTEGER,
            statut_eudr TEXT,
            conforme INTEGER,
            points_json TEXT,
            statut_envoi TEXT DEFAULT 'En attente'
        )
    """)
    conn.commit()
    conn.close()

def enregistrer_geolocalisation(producteur, localite, superficie, altitude, statut_eudr, conforme, points):
    """Insère un levé cadastral dans la base locale."""
    init_db()
    conn = sqlite3.connect("leyla_terrain.db")
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO geolocalisations 
        (date_creation, producteur, localite, superficie_ha, altitude_m, statut_eudr, conforme, points_json, statut_envoi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'En attente')
    """, (now, producteur, localite, superficie, altitude, statut_eudr, 1 if conforme else 0, json.dumps(points)))
    conn.commit()
    conn.close()

def calculer_surface_haversine(coords):
    n = len(coords)
    if n < 3: 
        return 0.0, (0.0, 0.0)
    centre_lat = sum(p[0] for p in coords) / n
    centre_lon = sum(p[1] for p in coords) / n
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        x1 = coords[i][1] * 111320 * math.cos(math.radians(coords[i][0]))
        y1 = coords[i][0] * 111132
        x2 = coords[j][1] * 111320 * math.cos(math.radians(coords[j][0]))
        y2 = coords[j][0] * 111132
        area += (x1 * y2) - (x2 * y1)
    return abs(area) / 20000.0, (centre_lat, centre_lon)

def analyser_domaines_etat(coords_lat_lon):
    if not coords_lat_lon:
        return "Aucune coordonnée", True
    moyen_lat = sum(c[0] for c in coords_lat_lon) / len(coords_lat_lon)
    moyen_lon = sum(c[1] for c in coords_lat_lon) / len(coords_lat_lon)
    pt = Point(moyen_lon, moyen_lat)
    poly_parcelle = Polygon([(c[1], c[0]) for c in coords_lat_lon])

    for nom, poly in parcs_et_reserves.items():
        if poly.contains(pt) or poly.intersects(poly_parcelle):
            return f"Appartient au domaine protégé de l'État : {nom} (Non conforme EUDR)", False

    for nom, poly in forets_classees.items():
        if poly.contains(pt) or poly.intersects(poly_parcelle):
            return f"Appartient au domaine forestier classé de l'État : {nom} (Strictement réglementé)", False

    for nom, poly in agroforets.items():
        if poly.contains(pt) or poly.intersects(poly_parcelle):
            return f"Situé dans la {nom} (Statut agroforestier autorisé sous conditions)", True

    return "Situé hors des domaines protégés (Conforme aux directives EUDR)", True

def chercher_lieu_excel(centre_gps, chemin="base_ivoire.xlsx"):
    lat_cible, lon_cible = centre_gps
    if not os.path.exists(chemin):
        return "Localité non référencée (Fichier absent)"
    try:
        df = pd.read_excel(chemin, usecols=[28, 29, 30], skiprows=1, names=["nom", "lat", "lon"])
        df = df.dropna(subset=["nom", "lat", "lon"])
        distances = np.sqrt((df["lat"].astype(float) - lat_cible)**2 + (df["lon"].astype(float) - lon_cible)**2)
        idx_min = distances.idxmin()
        return str(df.loc[idx_min, "nom"])
    except Exception as e:
        return f"Localité estimée"

# =========================================================================
# --- 3. MODULE PRINCIPAL STREAMLIT ---
# =========================================================================
def afficher():
    if "etape_module" not in st.session_state:
        st.session_state.etape_module = 1
    if "besoin_maquette" not in st.session_state:
        st.session_state.besoin_maquette = None
    if "points_gps" not in st.session_state:
        st.session_state.points_gps = []

    st.title("🛰️ LEYLA — Cartographie & GPS Terrain")
    st.markdown("---")

    # --- ÉTAPE 1 : Choix du Mode ---
    if st.session_state.etape_module == 1:
        st.subheader("📋 Étape 1 : Sélection du Mode de Relevé")
        st.info("Choisissez le type d'analyse géographique à effectuer pour cette parcelle.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗺️ Mode Parcelle Complète (2D/3D & Polygons)", type="primary", use_container_width=True):
                st.session_state.besoin_maquette = True
                st.session_state.etape_module = 2
                st.rerun()
        with col2:
            if st.button("📍 Mode Point Unique (Localisation Simple)", use_container_width=True):
                st.session_state.besoin_maquette = False
                st.session_state.etape_module = 2
                st.rerun()

    # --- ÉTAPE 2 : Capture GPS Pas à Pas (Garmin Style) ou Import ---
    elif st.session_state.etape_module == 2:
        st.subheader("📍 Étape 2 : Acquisition des Coordonnées GPS")

        if st.session_state.besoin_maquette:
            tab_garmin, tab_saisie_libre, tab_fichier = st.tabs([
                "📱 GPS Pas à Pas (Mode Garmin)", 
                "✍️ Saisie Texte Bloc", 
                "📁 Importer GPX / CSV"
            ])

            # --- TAB 1 : Mode Garmin Smartphone ---
            with tab_garmin:
                st.write("🚶‍♂️ **Parcourez le périmètre et relevez chaque borne/sommet :**")
                
                # HTML5 Geolocation API injection
                html_gps = """
                <script>
                function getGPS() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(
                            (position) => {
                                document.getElementById("lat_out").value = position.coords.latitude;
                                document.getElementById("lon_out").value = position.coords.longitude;
                                document.getElementById("alt_out").value = position.coords.altitude || 120;
                                document.getElementById("gps_status").innerText = "✅ Position GPS capturée avec succès !";
                            },
                            (error) => {
                                document.getElementById("gps_status").innerText = "⚠️ Erreur GPS : " + error.message;
                            },
                            { enableHighAccuracy: true, timeout: 10000 }
                        );
                    } else {
                        document.getElementById("gps_status").innerText = "⚠️ La géolocalisation n'est pas supportée.";
                    }
                }
                </script>
                <div style="padding:10px; background-color:#262730; border-radius:8px; margin-bottom:10px;">
                    <button onclick="getGPS()" style="width:100%; padding:10px; background-color:#ff4b4b; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                        📡 Capturer le Point GPS du Smartphone
                    </button>
                    <p id="gps_status" style="color:#00ffcc; font-size:12px; margin-top:5px; text-align:center;">Cliquez pour géolocaliser l'appareil.</p>
                </div>
                """
                st.components.v1.html(html_gps, height=110)

                col_lat, col_lon, col_alt = st.columns(3)
                with col_lat:
                    g_lat = st.number_input("Latitude", value=5.942100, format="%.6f", key="g_lat")
                with col_lon:
                    g_lon = st.number_input("Longitude", value=-4.215400, format="%.6f", key="g_lon")
                with col_alt:
                    g_alt = st.number_input("Altitude (m)", value=120.0, step=1.0, key="g_alt")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📍 Ajouter ce point GPS", type="primary", use_container_width=True):
                        st.session_state.points_gps.append({'lat': g_lat, 'lon': g_lon, 'alt': g_alt})
                        st.success(f"Point {len(st.session_state.points_gps)} ajouté !")
                        st.rerun()

                with col_btn2:
                    if st.button("↩️ Effacer le dernier point", use_container_width=True):
                        if st.session_state.points_gps:
                            st.session_state.points_gps.pop()
                            st.rerun()

                # Affichage des bornes déjà capturées
                if st.session_state.points_gps:
                    st.markdown("#### 📐 Bornes enregistrées :")
                    df_pts = pd.DataFrame(st.session_state.points_gps)
                    st.dataframe(df_pts, use_container_width=True)

            # --- TAB 2 : Saisie Libre ---
            with tab_saisie_libre:
                saisie_defaut = "\n".join([f"{p['lat']}, {p['lon']}, {p['alt']}" for p in st.session_state.points_gps])
                saisie_texte = st.text_area(
                    "Entrez la liste des points (Latitude, Longitude, Altitude)", 
                    value=saisie_defaut, 
                    placeholder="5.9421, -4.2154, 120\n5.9430, -4.2150, 122\n5.9415, -4.2140, 118",
                    height=150
                )
                if st.button("🔄 Mettre à jour depuis le texte", use_container_width=True):
                    pts = []
                    for ligne in saisie_texte.split('\n'):
                        if ',' in ligne:
                            morceaux = ligne.split(',')
                            try:
                                lat = float(morceaux[0].strip())
                                lon = float(morceaux[1].strip())
                                alt = float(morceaux[2].strip()) if len(morceaux) > 2 else 120.0
                                pts.append({'lat': lat, 'lon': lon, 'alt': alt})
                            except ValueError:
                                continue
                    st.session_state.points_gps = pts
                    st.success(f"{len(pts)} points pris en compte.")
                    st.rerun()

            # --- TAB 3 : Fichier ---
            with tab_fichier:
                croquis_file = st.file_uploader("Téléversez un fichier (GPX, CSV, TXT)", type=["gpx", "csv", "txt"])
                if croquis_file is not None:
                    try:
                        nom_fichier = croquis_file.name.lower()
                        pts_charges = []
                        if nom_fichier.endswith('.gpx'):
                            import xml.etree.ElementTree as ET
                            tree = ET.parse(croquis_file)
                            root = tree.getroot()
                            namespace = {'gpx': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                            elements = root.findall('.//gpx:trkpt', namespace) or root.findall('.//trkpt', namespace)
                            if not elements:
                                elements = root.findall('.//gpx:wpt', namespace) or root.findall('.//wpt', namespace)
                            for pt in elements:
                                lat = float(pt.get('lat'))
                                lon = float(pt.get('lon'))
                                ele_elem = pt.find('gpx:ele', namespace) if namespace else pt.find('ele')
                                alt = float(ele_elem.text) if ele_elem is not None else 120.0
                                pts_charges.append({'lat': lat, 'lon': lon, 'alt': alt})
                        else:
                            df_croquis = pd.read_csv(croquis_file)
                            if 'lat' in df_croquis.columns and 'lon' in df_croquis.columns:
                                for _, row in df_croquis.iterrows():
                                    pts_charges.append({'lat': row['lat'], 'lon': row['lon'], 'alt': row.get('alt', 120.0)})

                        if pts_charges:
                            st.session_state.points_gps = pts_charges
                            st.success(f"✅ {len(pts_charges)} points chargés depuis le fichier !")
                    except Exception as e:
                        st.error(f"Erreur de lecture du fichier : {e}")

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Retour", use_container_width=True):
                    st.session_state.etape_module = 1
                    st.rerun()
            with c2:
                if st.button("🚀 Valider et calculer la parcelle", type="primary", use_container_width=True):
                    if len(st.session_state.points_gps) >= 3:
                        st.session_state.etape_module = 3
                        st.rerun()
                    else:
                        st.error("⚠️ Il faut au moins 3 points GPS pour fermer le polygone de la parcelle.")

        else:
            # Mode Simple
            st.write("🎯 **Saisie du centre de la parcelle :**")
            lat_simple = st.text_input("Latitude", value="5.9421")
            lon_simple = st.text_input("Longitude", value="-4.2154")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Retour", use_container_width=True):
                    st.session_state.etape_module = 1
                    st.rerun()
            with c2:
                if st.button("🚀 Valider l'emplacement", type="primary", use_container_width=True):
                    try:
                        lat_f = float(lat_simple)
                        lon_f = float(lon_simple)
                        st.session_state.points_gps = [
                            {'lat': lat_f + 0.0005, 'lon': lon_f - 0.0005, 'alt': 120},
                            {'lat': lat_f + 0.0005, 'lon': lon_f + 0.0005, 'alt': 120},
                            {'lat': lat_f - 0.0005, 'lon': lon_f + 0.0005, 'alt': 120},
                            {'lat': lat_f - 0.0005, 'lon': lon_f - 0.0005, 'alt': 120}
                        ]
                        st.session_state.etape_module = 3
                        st.rerun()
                    except ValueError:
                        st.error("⚠️ Coordonnées invalides.")

    # --- ÉTAPE 3 : Résultats & Maquettes ---
    elif st.session_state.etape_module == 3:
        st.subheader("📊 Étape 3 : Résultats de l'Analyse Cadastrale")

        tuples_coords = [(p['lat'], p['lon']) for p in st.session_state.points_gps]
        superficie_ha, centre_gps = calculer_surface_haversine(tuples_coords)
        statut_texte, est_conforme = analyser_domaines_etat(tuples_coords)
        nom_localite = chercher_lieu_excel(centre_gps)
        alt_moyenne = sum(p['alt'] for p in st.session_state.points_gps) / len(st.session_state.points_gps)

        m1, m2, m3 = st.columns(3)
        m1.metric("🌳 SUPERFICIE", f"{superficie_ha:.4f} Ha")
        m2.metric("📍 LOCALITÉ", nom_localite)
        m3.metric("⛰️ ALTITUDE MOYENNE", f"{int(alt_moyenne)} m")

        if est_conforme:
            st.success(f"✅ **Statut Réglementaire :** {statut_texte}")
        else:
            st.warning(f"⚠️ **Statut Réglementaire :** {statut_texte}")

        nom_producteur = st.text_input("Nom & Prénoms du Producteur", value="Producteur Non Renseigné")

        if st.session_state.besoin_maquette:
            st.markdown("### 🗺️ Visualisation Cartographique")
            tab_3d, tab_2d = st.tabs(["🌲 Maquette Réaliste 3D", "📊 Plan Cadastral 2D"])

            with tab_3d:
                col_rot1, col_rot2 = st.columns(2)
                with col_rot1:
                    angle_horizontal = st.slider("Rotation azimut (0-360°)", 0, 360, 40, step=10)
                with col_rot2:
                    angle_vertical = st.slider("Inclinaison pitch (0-85°)", 0, 85, 50, step=5)

                poly_coords_3d = [[p['lon'], p['lat']] for p in st.session_state.points_gps]
                df_sol = pd.DataFrame([{"polygon": poly_coords_3d, "elevation": alt_moyenne}])
                df_surface = pd.DataFrame([{"polygon": poly_coords_3d, "elevation": alt_moyenne + 1}])

                layers = [
                    pdk.Layer("PolygonLayer", df_sol, get_polygon="polygon", get_fill_color="[110, 60, 20, 230]", extruded=True, get_elevation="elevation", elevation_scale=0.05),
                    pdk.Layer("PolygonLayer", df_surface, get_polygon="polygon", get_fill_color="[46, 125, 50, 210]", extruded=True, get_elevation="elevation", elevation_scale=0.1)
                ]

                view_state = pdk.ViewState(
                    latitude=centre_gps[0], longitude=centre_gps[1], zoom=16.5,
                    pitch=angle_vertical, bearing=angle_horizontal
                )

                st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, map_style="mapbox://styles/mapbox/satellite-streets-v11"))

            with tab_2d:
                fig, ax = plt.subplots(figsize=(7, 4))
                fig.patch.set_facecolor('#1e1e1e')
                ax.set_facecolor('#1e1e1e')
                lats = [p['lat'] for p in st.session_state.points_gps] + [st.session_state.points_gps[0]['lat']]
                lons = [p['lon'] for p in st.session_state.points_gps] + [st.session_state.points_gps[0]['lon']]
                ax.fill(lons, lats, color='#27ae60', alpha=0.5)
                ax.plot(lons, lats, color='#2ecc71', marker='o', linewidth=2)
                ax.tick_params(colors='white', labelsize=8)
                ax.grid(True, color='#333333', linestyle=':')
                ax.set_title(f"Plan Cadastral — {nom_localite}", color="white", fontsize=10)
                st.pyplot(fig)

        st.markdown("---")
        if st.button("💾 Enregistrer la parcelle dans la base SQLite", type="primary", use_container_width=True):
            enregistrer_geolocalisation(
                producteur=nom_producteur,
                localite=nom_localite,
                superficie=superficie_ha,
                altitude=int(alt_moyenne),
                statut_eudr=statut_texte,
                conforme=est_conforme,
                points=st.session_state.points_gps
            )

            st.success("✅ Levé cadastral enregistré avec succès dans SQLite (Statut : En attente) !")
            st.balloons()

            # Réinitialisation
            st.session_state.points_gps = []
            st.session_state.etape_module = 1
            st.session_state.besoin_maquette = None
            
            time.sleep(1.5)
            st.rerun()

if __name__ == "__main__":
    afficher()
