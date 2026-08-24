import streamlit as st
import streamlit.components.v1 as components
import pyttsx3
import threading
import os
import json
import time
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
from shapely.geometry import Polygon, Point

# Initialisation COM pour éviter les crashs pyttsx3 sous Windows/EXE
def parler(texte):
    def run_engine():
        try:
            import platform
            if platform.system() == "Windows":
                import pythoncom
                pythoncom.CoInitialize()
            engine = pyttsx3.init()
            engine.setProperty('rate', 175)
            engine.setProperty('volume', 1.0)
            engine.say(texte)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=run_engine, daemon=True).start()

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
# --- 2. FONCTIONS DE CALCULS & ANALYSES ---
# =========================================================================
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

@st.cache_data(show_spinner=False)
def charger_base_localites(chemin="base_ivoire.xlsx"):
    if not os.path.exists(chemin):
        return None
    try:
        df = pd.read_excel(chemin, usecols=[28, 29, 30], skiprows=1, names=["nom", "lat", "lon"])
        return df.dropna(subset=["nom", "lat", "lon"])
    except Exception:
        return None

def chercher_lieu_excel(centre_gps, chemin="base_ivoire.xlsx"):
    lat_cible, lon_cible = centre_gps
    df = charger_base_localites(chemin)
    if df is None:
        return "Localité non référencée (Base locale indisponible)"
    try:
        distances = np.sqrt((df["lat"].astype(float) - lat_cible)**2 + (df["lon"].astype(float) - lon_cible)**2)
        idx_min = distances.idxmin()
        return str(df.loc[idx_min, "nom"])
    except Exception as e:
        return f"Localité estimée ({e})"

# =========================================================================
# --- COMPOSANT TRACKER GPS AUTOMATIQUE (STYLE GARMIN) ---
# =========================================================================
def composant_tracker_garmin():
    html_code = """
    <div style="background-color: #1e1e1e; padding: 12px; border-radius: 8px; text-align: center; color: white;">
        <p style="margin:0; font-size: 14px;">🛰️ <b>Relevé GPS automatique (Pas : 1 Mètre)</b></p>
        <p id="status_text" style="color: #f1c40f; margin: 4px 0; font-size: 12px;">Initialisation du composant...</p>
        <p id="coords_display" style="font-family: monospace; font-size: 12px; margin: 0; color: #bdc3c7;">Lat: -- | Lon: -- | Alt: --</p>
        <p id="count_display" style="font-size: 11px; color: #2ecc71; margin-top: 4px;">Points capturés : 0</p>
    </div>

    <script>
    let lastLat = null;
    let lastLon = null;
    let pointCount = 0;
    const minDistanceMeters = 1.0; // Capturation fixée à 1 mètre

    function haversineDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000; // Rayon de la Terre en mètres
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    if ("geolocation" in navigator) {
        navigator.geolocation.watchPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const alt = position.coords.altitude !== null ? position.coords.altitude : 120.0;
                const accuracy = position.coords.accuracy;

                document.getElementById("coords_display").innerText = 
                    "Lat: " + lat.toFixed(6) + " | Lon: " + lon.toFixed(6) + " (±" + Math.round(accuracy) + "m)";

                let addPoint = false;
                let dist = 0;

                if (lastLat === null || lastLon === null) {
                    addPoint = true;
                } else {
                    dist = haversineDistance(lastLat, lastLon, lat, lon);
                    if (dist >= minDistanceMeters) {
                        addPoint = true;
                    }
                }

                if (addPoint) {
                    lastLat = lat;
                    lastLon = lon;
                    pointCount++;
                    document.getElementById("count_display").innerText = "Points capturés localement : " + pointCount + " (Dernier déplacement: " + dist.toFixed(1) + "m)";
                    document.getElementById("status_text").innerText = "🟢 GPS Actif - Point enregistré à 1m";
                    document.getElementById("status_text").style.color = "#2ecc71";

                    const pointData = { lat: lat, lon: lon, alt: alt };
                    window.parent.postMessage({ type: 'streamlit:setComponentValue', value: pointData }, '*');
                } else {
                    document.getElementById("status_text").innerText = "🟡 En attente d'un déplacement de 1m (Actuel: " + dist.toFixed(1) + "m)";
                    document.getElementById("status_text").style.color = "#f1c40f";
                }
            },
            (error) => {
                document.getElementById("status_text").innerText = "🔴 Erreur GPS (" + error.code + ") : " + error.message;
                document.getElementById("status_text").style.color = "#e74c3c";
            },
            {
                enableHighAccuracy: true,
                maximumAge: 0,         // Force la lecture en temps réel sans utiliser le cache
                timeout: 5000
            }
        );
    } else {
        document.getElementById("status_text").innerText = "🔴 La géolocalisation n'est pas supportée par ce navigateur.";
    }
    </script>
    """
    return components.html(html_code, height=120)

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
    if "is_tracking" not in st.session_state:
        st.session_state.is_tracking = False

    st.title("🛰️ LEYLA — Module de Localisation de Parcelle")
    st.markdown("---")

    # --- ÉTAPE 1 : Accueil ---
    if st.session_state.etape_module == 1:
        st.subheader("🤖 Étape 1 : Accueil par Leila")
        texte_accueil = "En plus de la localisation, voulez-vous voir la maquette 2D ou 3D de la parcelle ?"
        st.info(f"**Leila :** *« {texte_accueil} »*")
        
        if "voix_initiale_fait" not in st.session_state:
            parler(texte_accueil)
            st.session_state.voix_initiale_fait = True

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 Oui (Je veux les maquettes 2D/3D)", type="primary", use_container_width=True):
                st.session_state.besoin_maquette = True
                st.session_state.etape_module = 2
                st.rerun()
        with col2:
            if st.button("🔴 Non (Seulement l'emplacement exact)", use_container_width=True):
                st.session_state.besoin_maquette = False
                st.session_state.etape_module = 2
                st.rerun()

    # --- ÉTAPE 2 : Saisie des données ---
    elif st.session_state.etape_module == 2:
        st.subheader("📍 Étape 2 : Acquisition des Coordonnées Géographiques")

        if st.session_state.besoin_maquette:
            st.write("✨ **Mode Maquettes activé :** Leila a besoin d'un polygone complet.")
            
            tab_gps, tab_fichiers, tab_manuel = st.tabs([
                "📡 Suivi GPS Direct (Walk & Track)", 
                "📁 Téléversement de Croquis/Fichiers", 
                "✏️ Saisie Manuelle des Bornes"
            ])

            # --- ONGLET 1: TRACKING GPS CONTINU EN DIRECT (MODE GARMIN AUTOMATIQUE) ---
            with tab_gps:
                st.markdown("#### 🚶 Mode Marche Terrain (Relevé Continu Automatique)")
                st.info("💡 **Instructions :** Activez le tracé et marchez autour de la parcelle. Les points sont enregistrés automatiquement au fur et à mesure de vos pas. Cliquez sur **Boucler la parcelle** lorsque vous êtes revenu au point de départ.")

                c_start, c_stop = st.columns(2)
                with c_start:
                    if st.button("▶️ Démarrer le tracé GPS", use_container_width=True, type="primary"):
                        st.session_state.is_tracking = True
                        parler("Suivi automatique activé. Avancez le long des limites de la parcelle.")
                        st.rerun()

                with c_stop:
                    if st.button("🛑 Arrêter le suivi", use_container_width=True):
                        st.session_state.is_tracking = False
                        st.rerun()

                if st.session_state.is_tracking:
                    st.success("🟢 **Acquisition GPS active :** Enregistrement de la trace en cours...")
                    
                    # Composant JS d'écoute GPS continu
                    point_recu = composant_tracker_garmin()
                    
                    if point_recu:
                        lat_r = round(point_recu['lat'], 6)
                        lon_r = round(point_recu['lon'], 6)
                        alt_r = round(point_recu['alt'], 1)

                        # Évite d'ajouter le même point si la position n'a pas varié
                        if not st.session_state.points_gps or (
                            st.session_state.points_gps[-1]['lat'] != lat_r or 
                            st.session_state.points_gps[-1]['lon'] != lon_r
                        ):
                            st.session_state.points_gps.append({'lat': lat_r, 'lon': lon_r, 'alt': alt_r})
                            parler(f"Point {len(st.session_state.points_gps)} capturé")
                            st.rerun()

                if st.session_state.points_gps:
                    st.write(f"🚩 **Points de trace capturés ({len(st.session_state.points_gps)}) :**")
                    df_pts = pd.DataFrame(st.session_state.points_gps)
                    st.dataframe(df_pts, use_container_width=True)

                    c_reset, c_valid = st.columns(2)
                    with c_reset:
                        if st.button("🗑️ Effacer tous les points", use_container_width=True):
                            st.session_state.points_gps = []
                            st.rerun()
                    with c_valid:
                        if st.button("🎯 Boucler la parcelle et analyser", type="primary", use_container_width=True):
                            if len(st.session_state.points_gps) >= 3:
                                st.session_state.is_tracking = False
                                st.session_state.etape_module = 3
                                st.rerun()
                            else:
                                st.error("⚠️ Il faut au moins 3 points GPS pour fermer le polygone de la parcelle.")

            # --- ONGLET 2: TÉLÉVERSEMENT DE FICHIERS ---
            with tab_fichiers:
                st.markdown("#### 📁 Charger un fichier de terrain (GPX, CSV, TXT)")
                croquis_file = st.file_uploader("Choisissez un fichier", type=["gpx", "csv", "txt"], key="file_upload_tab")
                
                if croquis_file is not None:
                    try:
                        pts_charges = []
                        nom_fichier = croquis_file.name.lower()
                        if nom_fichier.endswith('.gpx'):
                            import xml.etree.ElementTree as ET
                            tree = ET.parse(croquis_file)
                            root = tree.getroot()
                            namespace = {'gpx': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                            elements = root.findall('.//gpx:trkpt', namespace) or root.findall('.//trkpt', namespace) or root.findall('.//gpx:wpt', namespace) or root.findall('.//wpt', namespace)
                            
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
                                    pts_charges.append({'lat': float(row['lat']), 'lon': float(row['lon']), 'alt': float(row.get('alt', 120))})

                        if len(pts_charges) >= 3:
                            st.session_state.points_gps = pts_charges
                            st.success(f"✅ {len(pts_charges)} points chargés depuis le fichier !")
                            if st.button("🚀 Analyser ce fichier", type="primary"):
                                st.session_state.etape_module = 3
                                st.rerun()
                        else:
                            st.error("⚠️ Moins de 3 points valides trouvés.")
                    except Exception as e:
                        st.error(f"Erreur de lecture du fichier : {e}")

            # --- ONGLET 3: SAISIE MANUELLE ---
            with tab_manuel:
                st.markdown("#### ✏️ Saisie textuelle des coordonnées")
                saisie_texte = st.text_area(
                    "Coordonnées GPS (Format : Latitude, Longitude, Altitude)", 
                    placeholder="5.9421, -4.2154, 120\n5.9430, -4.2150, 122\n5.9415, -4.2140, 118",
                    key="manual_text_area"
                )

                if st.button("🚀 Valider la saisie manuelle", type="primary"):
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
                    if len(pts) >= 3:
                        st.session_state.points_gps = pts
                        st.session_state.etape_module = 3
                        st.rerun()
                    else:
                        st.error("⚠️ Veuillez fournir au moins 3 points GPS valides.")

            st.markdown("---")
            if st.button("⬅️ Retour au choix initial"):
                st.session_state.etape_module = 1
                st.rerun()

        else:
            st.write("🎯 **Mode Localisation Simple activé :**")
            instruction = "Entrez la latitude et la longitude de la parcelle."
            st.info(f"**Leila :** *« {instruction} »*")
            
            if "voix_etape2_non" not in st.session_state:
                parler(instruction)
                st.session_state.voix_etape2_non = True

            lat_simple = st.text_input("Latitude", value="5.9421")
            lon_simple = st.text_input("Longitude", value="-4.2154")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ Retour", use_container_width=True):
                    st.session_state.etape_module = 1
                    st.rerun()
            with c2:
                if st.button("🚀 Obtenir l'emplacement", type="primary", use_container_width=True):
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

    # --- ÉTAPE 3 : Résultats ---
    elif st.session_state.etape_module == 3:
        st.subheader("📊 Étape 3 : Résultats de l'Analyse par Leila")

        tuples_coords = [(p['lat'], p['lon']) for p in st.session_state.points_gps]
        superficie_ha, centre_gps = calculer_surface_haversine(tuples_coords)
        statut_texte, est_conforme = analyser_domaines_etat(tuples_coords)
        nom_localite = chercher_lieu_excel(centre_gps)
        alt_moyenne = sum(p['alt'] for p in st.session_state.points_gps) / len(st.session_state.points_gps)

        m1, m2, m3 = st.columns(3)
        m1.metric("🌳 SUPERFICIE", f"{superficie_ha:.4f} Ha")
        m2.metric("📍 LOCALITÉ", nom_localite)
        m3.metric("⛰️ ALTITUDE", f"{int(alt_moyenne)} m")

        if est_conforme:
            st.success(f"✅ **Domaine de l'État :** {statut_texte}")
        else:
            st.warning(f"⚠️ **Domaine de l'État :** {statut_texte}")

        cle_vocal_final = f"{superficie_ha:.2f}-{nom_localite}-{st.session_state.besoin_maquette}"
        if "dernier_vocal_module3" not in st.session_state or st.session_state.dernier_vocal_module3 != cle_vocal_final:
            discours = f"La parcelle est située à {nom_localite}. Superficie : {superficie_ha:.2f} hectares. {statut_texte}."
            parler(discours)
            st.session_state.dernier_vocal_module3 = cle_vocal_final

        if st.session_state.besoin_maquette:
            st.markdown("### 🗺️ Maquettes de la Parcelle (2D & 3D)")
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
        if st.button("🏁 Enregistrer et envoyer au Chef", type="primary", key="btn_sortir_p3_fin", use_container_width=True):
            fichier_json = "base_de_donnees_layla.json"
            data_file = {}
            if os.path.exists(fichier_json):
                try:
                    with open(fichier_json, "r", encoding="utf-8") as f:
                        data_file = json.load(f)
                except Exception:
                    data_file = {}

            if "file_attente_locale" not in data_file:
                data_file["file_attente_locale"] = []

            rapport_parcelle = {
                "horodatage": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nom": "Producteur Localisation",
                "zone": "Zone Agricole",
                "ville": nom_localite,
                "superficie": superficie_ha,
                "diagnostic": statut_texte,
                "altitude_moyenne": int(alt_moyenne),
                "est_conforme": est_conforme,
                "besoin_maquette": st.session_state.besoin_maquette,
                "gps": {"latitude": centre_gps[0], "longitude": centre_gps[1]},
                "points_gps_bruts": st.session_state.points_gps
            }

            data_file["file_attente_locale"].append(rapport_parcelle)

            with open(fichier_json, "w", encoding="utf-8") as f:
                json.dump(data_file, f, indent=4, ensure_ascii=False)

            parler("OK, c'est parti pour une nouvelle localisation.")
            st.success("✅ Rapport enregistré et transmis avec succès !")
            st.balloons()
            
            # Réinitialisation
            st.session_state.points_gps = []
            st.session_state.etape_module = 1
            st.session_state.besoin_maquette = None
            for cle_voix in ["voix_initiale_fait", "voix_etape2_oui", "voix_etape2_non", "dernier_vocal_module3"]:
                st.session_state.pop(cle_voix, None)
            
            time.sleep(1.5)
            st.rerun()

if __name__ == "__main__":
    afficher()
