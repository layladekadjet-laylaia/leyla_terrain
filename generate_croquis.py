import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generer_croquis_parcelle(
    nom_producteur, code_ccc, surf_totale, surf_prod, surf_jeune, 
    waypoint_gps, nb_arbres, essences, elements, acces
):
    # Création de la figure
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.set_facecolor('#e8f5e9') # Fond vert très clair (zone agricole)

    # 1. Dessin de la parcelle principale (Polygone simulant les 5.0 ha)
    poly_coords = np.array([[1, 2], [2, 8], [8, 9], [9, 3], [5, 1]])
    parcelle = patches.Polygon(poly_coords, closed=True, edgecolor='#2e7d32', facecolor='#c8e6c9', linewidth=2.5, linestyle='--', label='Limite Parcelle')
    ax.add_patch(parcelle)

    # 2. Zone Cacao immature (Sous-zone)
    zone_jeune = patches.Polygon([[1.5, 2.5], [2.2, 5.5], [4.5, 4.5], [3.5, 2]], closed=True, edgecolor='#81c784', facecolor='#a5d6a7', hatch='//', alpha=0.7)
    ax.add_patch(zone_jeune)
    ax.text(2.5, 3.5, f"Cacao Immature\n({surf_jeune:.1f} ha)", fontsize=8, fontweight='bold', color='#1b5e20', ha='center')

    # Label Cacao productif
    ax.text(6.0, 6.0, f"Cacao Productif\n({surf_prod:.1f} ha)", fontsize=10, fontweight='bold', color='#1b5e20', ha='center')

    # 3. Positionnement aléatoire contrôlé des arbres forestiers d'ombrage
    np.random.seed(42) # Conservation du tracé fixe
    x_arbres = np.random.uniform(2.5, 7.5, min(nb_arbres, 25))
    y_arbres = np.random.uniform(2.5, 7.5, min(nb_arbres, 25))
    ax.scatter(x_arbres, y_arbres, c='#1b5e20', marker='^', s=120, zorder=4, label=f'Arbres Forestiers ({nb_arbres} pieds)')

    # 4. Infrastructures & Repères
    if "Campement / Habitation" in elements:
        ax.plot(3.0, 2.0, marker='s', markersize=12, color='#d84315', zorder=5)
        ax.text(3.0, 1.6, "Campement", fontsize=8, fontweight='bold', ha='center')

    if "Cours d'eau / Bas-fond" in elements or "Traversée par voie d'eau" in acces:
        ax.plot([0, 10], [1, 4], color='#0288d1', linewidth=3, linestyle='-', zorder=3, label="Cours d'eau")

    if "Pistes & Voies d'accès" in str(acces) or "Piste camionnière / Sommier" in acces:
        ax.plot([0, 10], [8.5, 6.5], color='#795548', linewidth=3.5, linestyle=':', zorder=3, label="Piste camionnière")

    # 5. Rose des vents (Points Cardinaux N-S-E-O)
    ax.annotate('N', xy=(0.9, 0.9), xytext=(0.9, 0.8), xycoords='axes fraction',
                arrowprops=dict(facecolor='black', width=2, headwidth=8),
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.text(0.9, 0.75, "S", transform=ax.transAxes, ha='center', fontsize=9, fontweight='bold')
    ax.text(0.95, 0.82, "E", transform=ax.transAxes, ha='center', fontsize=9, fontweight='bold')
    ax.text(0.85, 0.82, "O", transform=ax.transAxes, ha='center', fontsize=9, fontweight='bold')

    # 6. Habillage et Cartouche CCC
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off') # Masquer les axes X/Y numériques

    titre_cartouche = f"CROQUIS DE LA PARCELLE - CONSEIL CAFÉ-CACAO\nProducteur: {nom_producteur} ({code_ccc}) | Sup: {surf_totale:.1f} ha\nGPS: {waypoint_gps}"
    plt.title(titre_cartouche, fontsize=9, fontweight='bold', pad=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='#2e7d32', boxstyle='round,pad=0.5'))
    plt.legend(loc='lower right', fontsize=7, framealpha=0.9)

    # Conversion en buffer image pour Streamlit
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf
