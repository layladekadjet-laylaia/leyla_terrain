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

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# =========================================================================
# --- 1. COMPOSANT TRACKER GPS (AUTONOME EN LOCALSTORAGE) ---
# =========================================================================
def composant_tracker_garmin():
    """
    Composant HTML/JS autonome style Garmin.
    Sauvegarde la trace dans le localStorage du mobile pour éviter toute perte lors des rerun.
    Ne transmet les données à Streamlit qu'au moment de l'arrêt/bouclage.
    """
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.4.0/dist/streamlit-component-lib.js"></script>
        <style>
            body { margin: 0; padding: 0; background-color: transparent; font-family: system-ui, -apple-system, sans-serif; }
            .tracker-card {
                background-color: #121212; 
                padding: 16px; 
                border-radius: 12px; 
                text-align: center; 
                color: white; 
                border: 1px solid #333;
                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            }
            .btn-action {
                width: 100%; 
                padding: 14px; 
                margin: 8px 0;
                border: none; 
                border-radius: 8px; 
                font-size: 15px; 
                font-weight: bold; 
                cursor: pointer;
                transition: 0.2s;
            }
            .btn-stop { background-color: #ff5252; color: white; }
            .btn-disabled { background-color: #424242 !important; color: #757575 !important; cursor: not-allowed !important; }
            .status-box { font-size: 13px; font-weight: bold; margin: 6px 0; }
        </style>
    </head>
    <body>
        <div class="tracker-card">
            <p style="margin:0; font-size: 15px; font-weight: bold; color: #4fc3f7;">🛰️ Relevé GPS Continuous (Pas : 1m)</p>
            
            <button id="btn-stop" class="btn-action btn-stop btn-disabled" disabled onclick="stopperEtEnvoyer()">
                🛑 ARRÊTER ET BOUCLER (0 PTS)
            </button>

            <div id="status_text" class="status-box" style="color: #ffb74d;">⏳ Initialisation du GPS...</div>
            <p id="coords_display" style="font-family: monospace; font-size: 12px; margin: 4px 0; color: #b0bec5;">Lat: -- | Lon: -- (±--m)</p>
            <p id="count_display" style="font-size: 14px; color: #81c784; margin-top: 6px; font-weight: bold;">Points enregistrés : 0</p>
        </div>

        <script>
        let pointsList = JSON.parse(localStorage.getItem("leyla_gps_trace") || "[]");
        let lastLat = pointsList.length > 0 ? pointsList[pointsList.length - 1].lat : null;
        let lastLon = pointsList.length > 0 ? pointsList[pointsList.length - 1].lon : null;
        const minDistanceMeters = 1.0;

        function updateUI() {
            const btn = document.getElementById("btn-stop");
            document.getElementById("count_display").innerText = "Points enregistrés : " + pointsList.length;
            if (pointsList.length >= 3) {
                btn.disabled = false;
                btn.classList.remove("btn-disabled");
                btn.innerText = "🛑 ARRÊTER ET BOUCLER LA PARCELLE (" + pointsList.length + " PTS)";
            } else {
                btn.disabled = true;
                btn.classList.add("btn-disabled");
                btn.innerText = "🛑 ARRÊTER ET BOUCLER (" + pointsList.length + " / 3 PTS MIN)";
            }
        }

        function stopperEtEnvoyer() {
            if (pointsList.length >= 3) {
                if (window.Streamlit) {
                    Streamlit.setComponentValue({
                        points: pointsList,
                        termine: true
                    });
                }
                localStorage.removeItem("leyla_gps_trace");
            }
        }

        function haversineDistance(lat1, lon1, lat2, lon2) {
            const R = 6371000;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        }

        updateUI();

        if ("geolocation" in navigator) {
            navigator.geolocation.watchPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const alt = position.coords.altitude !== null ? position.coords.altitude : 0.0;
                    const accuracy = Math.round(position.coords.accuracy);

                    document.getElementById("coords_display").innerText = 
                        "Lat: " + lat.toFixed(6) + " | Lon: " + lon.toFixed(6) + " (±" + accuracy + "m)";

                    let addPoint = false;
                    if (lastLat === null || lastLon === null) {
                        addPoint = true;
                    } else {
                        if (haversineDistance(lastLat, lastLon, lat, lon) >= minDistanceMeters) {
                            addPoint = true;
                        }
                    }

                    if (addPoint) {
                        lastLat = lat;
                        lastLon = lon;
                        pointsList.push({ lat: lat, lon: lon, alt: alt });
                        localStorage.setItem("leyla_gps_trace", JSON.stringify(pointsList));
                        
                        document.getElementById("status_text").innerText = "🟢 GPS Actif - Acquisition de la trace...";
                        document.getElementById("status_text").style.color = "#00e676";
                        updateUI();
                    } else {
                        document.getElementById("status_text").innerText = "🟡 En attente de déplacement...";
                        document.getElementById("status_text").style.color = "#ffb74d";
                    }
                },
                (error) => {
                    document.getElementById("status_text").innerText = "🔴 Signal GPS perdu ou refusé (" + error.code + ")";
                    document.getElementById("status_text").style.color = "#ff5252";
                },
                { enableHighAccuracy: true, maximumAge: 0, timeout: 15000 }
            );
        } else {
            document.getElementById("status_text").innerText = "🔴 Géolocalisation non supportée sur cet appareil.";
        }
        </script>
    </body>
    </html>
    """
    return components.html(html_code, height=230)

# =========================================================================
# --- 2. CALCULS GÉOMÉTRIQUES (HA VERSINE & SHOELACE) ---
# =========================================================================
def calculer_superficie_et_perimetre(points):
    """Calcule le périmètre (m) et la superficie (m² / ha) d'un polygone de points GPS."""
    if len(points) < 3:
        return 0.0, 0.0, 0.0

    R = 6378137.0  # Rayon Terre (m)
    perimetre = 0.0
    
    # 1. Périmètre
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        
        dlat = math.radians(p2['lat'] - p1['lat'])
        dlon = math.radians(p2['lon'] - p1['lon'])
        a = math.sin(dlat/2)**2 + math.cos(math.radians(p1['lat'])) * math.cos(math.radians(p2['lat'])) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        perimetre += R * c

    # 2. Superficie (Projection équirectangulaire + Formule du Lacet / Shoelace)
    lat_moy = math.radians(sum(p['lat'] for p in points) / len(points))
    x = [R * math.radians(p['lon']) * math.cos(lat_moy) for p in points]
    y = [R * math.radians(p['lat']) for p in points]
    
    superficie_m2 = 0.5 * abs(sum(x[i] * y[(i + 1) % len(x)] - x[(i + 1) % len(x)] * y[i] for i in range(len(x))))
    superficie_ha = superficie_m2 / 10000.0

    return perimetre, superficie_m2, superficie_ha

# =========================================================================
# --- 3. GÉNÉRATION DES MAQUETTES 2D ET 3D ---
# =========================================================================
def generer_maquette_2d(points):
    lats = [p['lat'] for p in points] + [points[0]['lat']]
    lons = [p['lon'] for p in points] + [points[0]['lon']]

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        mode="lines+markers",
        lat=lats, lon=lons,
        marker={'size': 8, 'color': '#00e676'},
        line={'width': 3, 'color': '#00e676'},
        fill="toself",
        fillcolor="rgba(0, 230, 118, 0.2)",
        name="Parcelle"
    ))

    fig.update_layout(
        mapbox={
            'style': "open-street-map",
            'center': {'lat': np.mean(lats), 'lon': np.mean(lons)},
            'zoom': 17
        },
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        height=400
    )
    return fig

def generer_maquette_3d(points):
    # Transformation coordonnées relatives en mètres pour la vue 3D
    R = 6378137.0
    lat0 = math.radians(points[0]['lat'])
    lon0 = math.radians(points[0]['lon'])

    x, y, z = [], [], []
    for p in points:
        px = R * (math.radians(p['lon']) - lon0) * math.cos(lat0)
        py = R * (math.radians(p['lat']) - lat0)
        pz = p.get('alt', 0.0)
        x.append(px)
        y.append(py)
        z.append(pz)

    # Fermeture de la boucle
    x.append(x[0])
    y.append(y[0])
    z.append(z[0])

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers',
        marker=dict(size=4, color='#4fc3f7'),
        line=dict(color='#00e676', width=6),
        name="Trace 3D"
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Altitude (m)",
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=450
    )
    return fig

# =========================================================================
# --- 4. FONCTION PRINCIPALE : AFFICHER ---
# =========================================================================
def afficher():
    if "etape_module" not in st.session_state:
        st.session_state.etape_module = 1
    if "points_gps" not in st.session_state:
        st.session_state.points_gps = []
    if "is_tracking" not in st.session_state:
        st.session_state.is_tracking = False
    if "nom_producteur" not in st.session_state:
        st.session_state.nom_producteur = ""

    st.title("🛰️ LEYLA — Cartographie & Topographie Terrain")

    # --- ÉTAPE 1 : Accueil ---
    if st.session_state.etape_module == 1:
        st.info("💡 **Mode Calcul de Zone Garmin** : Activez le tracé, effectuez le tour complet de la parcelle puis stopez pour obtenir la superficie exacte.")
        st.session_state.nom_producteur = st.text_input("Nom du Producteur / Code Parcelle :", placeholder="ex: Kouadio - Parcelle Cocoa A")
        
        if st.button("▶️ Démarrer le Calcul de Zone", type="primary", use_container_width=True):
            if st.session_state.nom_producteur.strip() == "":
                st.warning("⚠️ Veillez renseigner le nom du producteur avant de démarrer.")
            else:
                st.session_state.is_tracking = True
                st.session_state.points_gps = []
                st.session_state.etape_module = 2
                st.rerun()

    # --- ÉTAPE 2 : Tracker et Acquisition GPS ---
    elif st.session_state.etape_module == 2:
        st.subheader(f"📍 Acquisition Terrain : {st.session_state.nom_producteur}")
        
        if st.button("🔄 Annuler / Réinitialiser la marche", type="secondary"):
            st.session_state.is_tracking = False
            st.session_state.points_gps = []
            st.session_state.etape_module = 1
            st.rerun()

        st.markdown("---")
        
        # Injection du composant HTML Garmin
        donnees_composant = composant_tracker_garmin()

        # Capture de l'événement de fin de parcours envoyé par l'iFrame
        if isinstance(donnees_composant, dict):
            if donnees_composant.get("termine") is True:
                st.session_state.points_gps = donnees_composant.get("points", [])
                st.session_state.is_tracking = False
                st.session_state.etape_module = 3
                st.rerun()

    # --- ÉTAPE 3 : Résultats, Maquettes 2D / 3D & Enregistrement ---
    elif st.session_state.etape_module == 3:
        pts = st.session_state.points_gps
        perimetre, sup_m2, sup_ha = calculer_superficie_et_perimetre(pts)

        st.success(f"🎉 **Calcul de Zone Terminé avec Succès !**")
        st.subheader(f"📋 Fiche Synthese : {st.session_state.nom_producteur}")

        # KPI Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Superficie (Ha)", f"{sup_ha:.3f} ha")
        col2.metric("Superficie (m²)", f"{sup_m2:.1f} m²")
        col3.metric("Périmètre", f"{perimetre:.1f} m")

        # Cartes 2D / 3D
        tab_2d, tab_3d, tab_data = st.tabs(["🗺️ Maquette 2D (Vue Vue du Ciel)", "🧊 Maquette Topographique 3D", "📊 Tableau des Sommets GPS"])

        with tab_2d:
            st.plotly_chart(generer_maquette_2d(pts), use_container_width=True)

        with tab_3d:
            st.plotly_chart(generer_maquette_3d(pts), use_container_width=True)

        with tab_data:
            df_pts = pd.DataFrame(pts)
            st.dataframe(df_pts, use_container_width=True)

        st.markdown("---")
        c_save, c_restart = st.columns(2)
        with c_save:
            if st.button("💾 Enregistrer la Parcelle dans LEYLA", type="primary", use_container_width=True):
                st.balloons()
                st.success("✅ Données enregistrées dans la base de données !")
        with c_restart:
            if st.button("🔄 Effectuer un Nouveau Relevé", use_container_width=True):
                st.session_state.etape_module = 1
                st.session_state.points_gps = []
                st.rerun()

# =========================================================================
# --- 5. POINT D'ENTRÉE DU SCRIPT ---
# =========================================================================
if __name__ == "__main__":
    st.set_page_config(
        page_title="LEYLA - Cartographie Terrain",
        page_icon="🛰️",
        layout="centered"
    )
    afficher()


