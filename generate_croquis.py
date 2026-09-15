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
    elements=None,
    acces=None,
    liste_arbres=None,
    **kwargs,
):
  """Génère un schéma graphique de la parcelle cacaoyère au format In-Memory BytesIO

  en intégrant les coordonnées GPS des arbres répertoriés à l'Étape 4.
  """
  if essences is None:
    essences = []
  if elements is None:
    elements = []
  if acces is None:
    acces = []
  if liste_arbres is None:
    liste_arbres = []

  # Configuration du canevas
  fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
  ax.set_facecolor("#f4f9f4")

  # Simulation des limites du polygone de la parcelle
  polygone_x = [1, 2, 8, 9, 7, 3, 1]
  polygone_y = [2, 8, 9, 6, 1, 1, 2]
  ax.fill(polygone_x, polygone_y, color="#2e7d32", alpha=0.15, label="Parcelle")
  ax.plot(polygone_x, polygone_y, color="#1b5e20", linewidth=2.5, linestyle="--")

  # Représentation du Waypoint Central (Centre de gravité de la parcelle)
  ax.plot(
      5,
      5,
      marker="*",
      markersize=15,
      color="#d32f2f",
      label=f"Waypoint Central ({waypoint_gps})",
  )

  # Trace des arbres géolocalisés (issus de l'Étape 4)
  if liste_arbres:
    lats = []
    lons = []
    labels = []

    for item in liste_arbres:
      if isinstance(item, dict):
        lat = item.get("Latitude")
        lon = item.get("Longitude")
        espece = item.get("Espèce", "Arbre")
        if lat is not None and lon is not None:
          try:
            lats.append(float(lat))
            lons.append(float(lon))
            labels.append(str(espece))
          except ValueError:
            continue

    # Projection orthogonale simplifiée sur le schéma si des coordonnées valides existent
    if lats and lons:
      lat_min, lat_max = min(lats), max(lats)
      lon_min, lon_max = min(lons), max(lons)

      for lat, lon, esp in zip(lats, lons, labels):
        # Normalisation dans l'espace [2, 8] du plot
        x_proj = (
            5
            if lon_max == lon_min
            else 2 + (lon - lon_min) / (lon_max - lon_min) * 6
        )
        y_proj = (
            5
            if lat_max == lat_min
            else 2 + (lat - lat_min) / (lat_max - lat_min) * 6
        )

        ax.plot(
            x_proj,
            y_proj,
            marker="^",
            markersize=10,
            color="#388e3c",
            markeredgecolor="#1b5e20",
        )
        ax.text(
            x_proj + 0.1,
            y_proj + 0.1,
            esp,
            fontsize=8,
            fontweight="bold",
            color="#1b5e20",
        )

      # Légende fictive unique pour le groupe d'arbres
      ax.plot(
          [],
          [],
          marker="^",
          color="#388e3c",
          linestyle="None",
          label=f"Arbres relevés ({len(lats)} GPS)",
      )
  else:
    # Si pas de coordonnées précises, représentation symbolique basée sur le nombre
    np.random.seed(42)
    for _ in range(min(nb_arbres, 25)):
      rx = np.random.uniform(2.5, 7.5)
      ry = np.random.uniform(2.5, 7.5)
      ax.plot(
          rx,
          ry,
          marker="^",
          markersize=9,
          color="#4caf50",
          alpha=0.8,
      )

  # Habillage de la carte
  ax.set_title(
      f"CROQUIS TECHNIQUE DE LA PARCELLE — CCC / RDUE\nProducteur : {nom_producteur} | Code : {code_ccc}",
      fontsize=12,
      fontweight="bold",
      pad=15,
  )

  # Boîte d'informations statistiques
  info_text = (
      f"Superficie Totale : {surf_totale:.2f} ha\n"
      f"Cacao Productif : {surf_prod:.2f} ha\n"
      f"Cacao Immature : {surf_jeune:.2f} ha\n"
      f"Effectif Arbres d'ombrage : {nb_arbres} pieds\n"
      f"Accès : {', '.join(acces[:2]) if acces else 'Standard'}"
  )
  ax.text(
      0.02,
      0.02,
      info_text,
      transform=ax.transAxes,
      fontsize=9,
      bbox=dict(
          boxstyle="round,pad=0.5",
          facecolor="#ffffff",
          edgecolor="#cccccc",
          alpha=0.9,
      ),
  )

  # Style des axes et grilles
  ax.set_xlim(0, 10)
  ax.set_ylim(0, 10)
  ax.grid(True, linestyle=":", alpha=0.5)
  ax.legend(loc="upper right", fontsize=9)
  ax.set_xlabel("Orientation Est-Ouest (Relatif)")
  ax.set_ylabel("Orientation Nord-Sud (Relatif)")

  # Sauvegarde mémoire dans un tampon BytesIO pour Streamlit
  buf = io.BytesIO()
  plt.tight_layout()
  plt.savefig(buf, format="png", dpi=200)
  plt.close(fig)
  buf.seek(0)

  return buf