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
