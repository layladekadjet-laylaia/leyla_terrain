import streamlit as st
import pandas as pd
import sqlite3
import json
import time

# --- GESTION DE LA BASE DE DONNÉES LOCALE (SQLITE TERRAIN) ---
DB_LOCAL_PATH = "leyla_terrain.db"

def sauvegarder_en_local_sqlite(donnees):
    """Insère le rapport directement dans la base leyla_terrain.db de la tablette avec le statut 'En attente'."""
    conn = sqlite3.connect(DB_LOCAL_PATH)
    cursor = conn.cursor()
    
    # Récupération des infos producteur stockées dans la session principale
    info_p = st.session_state.get("info_producteur", {})
    nom_prod = donnees.get("nom") or info_p.get("nom") or "Inconnu"
    code_prod = info_p.get("code", "")
    sup_prod = info_p.get("superficie", 1.0)
    age_prod = info_p.get("age", "")

    cursor.execute("""
        INSERT INTO rapports_locaux 
        (cooperative, section, technicien, producteur, code_producteur, superficie, age_parcelle, module_type, donnees_module, date_saisie, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'En attente')
    """, (
        st.session_state.get("cooperative", "N/A"),
        st.session_state.get("section", "N/A"),
        st.session_state.get("technicien", "N/A"),
        nom_prod,
        code_prod,
        float(sup_prod),
        str(age_prod),
        "Diagnostic Phytosanitaire",
        donnees["diagnostic"],
        time.strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# --- DICTIONNAIRE AGRONOMIQUE DE L'INGÉNIEUR LEYLA ---
DIAGNOSTIQUE = {
    "POURRITURE_BRUNE": {
        "nom": "Pourriture Brune des Cabosses (Phytophthora palmivora / megakarya)",
        "classe": "Fongique / Oomycète",
        "diagnostics": [
            {"id": "Forme classique sur fruit (Cabosse)", "symptomes": ["tache brune","tâches brunes", "tâche brune", "tache brune", "cabosse noire", "pourriture", "feutrage blanc", "moisissure veloutee"]},
            {"id": "Forme foliaire et vasculaire", "symptomes": ["taches marron sur les feuilles", "dessechement pointes vegetatives", "necrose bourgeons", "chute feuilles vertes"]},
            {"id": "Forme chancres", "symptomes": ["ecorce brunie", "suintement gélatineux", "liquide rougeatre", "liquide violace", "dessechement charpentiere"]}
        ],
        "remede": (
            "• Récolte sanitaire stricte toutes les 2 semaines pour retirer toutes les cabosses atteintes (les enterrer ou les brûler hors du champ).\n"
            "• Élagage intensif des cacaoyers et élimination des mauvaises herbes pour casser l'humidité ambiante sous la canopée.\n"
            "• Pulvérisation de fongicides cupriques (hydroxyde de cuivre ou oxyde cuivreux) au début des grandes pluies, à renouveler toutes les 3 semaines."
        )
    },
    "BALAI_DE_SORCIERE": {
        "nom": "Balai de Sorcière (Moniliophthora perniciosa)",
        "classe": "Fongique / Cryptogamique",
        "diagnostics": [
            {"id": "Attaque végétative (Rameaux)", "symptomes": ["balai de sorciere", "proliferation rameaux", "branches en touffe", "bourgeons hypertrophies"]},
            {"id": "Attaque sur fleurs", "symptomes": ["floraison massive", "coussin floral geant", "fleurs deformees", "fleurs steriles"]},
            {"id": "Attaque sur fruits", "symptomes": ["cabosse poire", "cabosse fraise", "durcissement precoce", "feves agglutinees"]}
        ],
        "remede": (
            "• Taille chirurgicale systématique : couper les balais végétatifs 20 cm en dessous de leur point d'insertion avant qu'ils ne sèchent et ne libèrent leurs spores.\n"
            "• Brûler immédiatement tous les débris de taille.\n"
            "• Désinfection obligatoire des outils de coupe (machettes, sécateurs) à l'alcool ou à l'eau de javel diluée entre chaque arbre."
        )
    },
    "MONILIOSE": {
        "nom": "Moniliose des Cabosses (Moniliophthora roreri)",
        "classe": "Fongique / Cryptogamique",
        "diagnostics": [
            {"id": "Attaque sur jeunes fruits", "symptomes": ["bosse cabosse", "gonflement asymetrique", "jaunissement premature"]},
            {"id": "Stade avancé (Sporulation)", "symptomes": ["tache brune irreguliere", "poudre blanche", "poudre creme", "cabosse lourde", "coque seche"]}
        ],
        "remede": (
            "• Inspection hebdomadaire fine de la plantation.\n"
            "• Retrait délicat des cabosses suspectes AVANT que la poudre blanche n'apparaisse pour éviter la dispersion par le vent.\n"
            "• Enterrer les cabosses infectées sous une couche de terre de minimum 20 cm."
        )
    },
    "POURRIDIE_BLANC": {
        "nom": "Pourridié Blanc des Racines (Rigidoporus lignosus)",
        "classe": "Fongique / Racinaire",
        "diagnostics": [
            {"id": "Symptômes souterrains (Racines)", "symptomes": ["mycelium blanc", "filaments jaunatres", "ecorce racine decollee", "racine pourrie"]},
            {"id": "Symptômes extérieurs au collet", "symptomes": ["champignon console", "champignon jaune orange", "champignon au pied du tronc"]},
            {"id": "Impact foliaire global", "symptomes": ["jaunissement soudain feuillage", "fletrissement rapide", "mort de l'arbre debout"]}
        ],
        "remede": (
            "• Creuser des tranchées d'isolement de 60 cm de profondeur autour de la zone infectée pour couper les contacts racinaires avec les arbres sains.\n"
            "• Arrachage complet, extraction des racines et incinération de la souche morte.\n"
            "• Épandage massif de chaux agricole (dolomie) dans le trou pour alcaliniser le sol et bloquer le champignon."
        )
    },
    "POURRIDIE_ROUGE": {
        "nom": "Pourridié Rouge (Ganoderma philippii)",
        "classe": "Fongique / Racinaire",
        "diagnostics": [
            {"id": "Attaque racinaire", "symptomes": ["filaments rouges", "mycelium brun rouge", "sable piege racines"]},
            {"id": "Destruction du tronc", "symptomes": ["pourriture seche pivot", "bois spongieux", "bois friable", "rupture du tronc", "arbre casse"]}
        ],
        "remede": (
            "• Protocole identique au pourridié blanc : isolement par tranchée et destruction de la souche.\n"
            "• Éviter d'installer une nouvelle plantation immédiatement sur des parcelles récemment défrichées pleines de vieilles souches forestières sans nettoyage préalable."
        )
    },
    "FIL_BLANC": {
        "nom": "Maladie du Fil Blanc (Marasmiellus scandens)",
        "classe": "Fongique / Cryptogamique",
        "diagnostics": [
            {"id": "Présence de cordons mycéliens", "symptomes": ["fils blancs rameaux", "cordons myceliens", "fils blancs sous feuilles"]},
            {"id": "Rétention des feuilles mortes", "symptomes": ["feuilles fixées branches", "grappes feuilles seches", "feuilles suspendues"]}
        ],
        "remede": (
            "• Élagage des branches basses et des rameaux touchés.\n"
            "• Amélioration de l'aération de la parcelle pour baisser l'humidité relative."
        )
    },
    "MALADIE_ROSE": {
        "nom": "Maladie Rose (Erythricium salmonicolor)",
        "classe": "Fongique / Cryptogamique",
        "diagnostics": [
            {"id": "Infection de l'écorce", "symptomes": ["croûte rose", "enduit soyeux rose", "rose saumon fourche"]},
            {"id": "Nécrose de la branche", "symptomes": ["fissuration ecorce", "dessechement branche", "mort section branche"]}
        ],
        "remede": (
            "• Tailler la branche atteinte 30 cm en dessous de la zone rose.\n"
            "• Application locale d'une pâte fongicide à base de cuivre sur la plaie de coupe."
        )
    },
    "ANTHRACNOSE": {
        "nom": "Anthracnose du Cacaoyer (Colletotrichum gloeosporioides)",
        "classe": "Fongique / Cryptogamique",
        "diagnostics": [
            {"id": "Manifestation foliaire", "symptomes": ["taches circulaires claires", "feuilles perforees", "feuilles criblees de balles"]},
            {"id": "Manifestation sur fruits", "symptomes": ["taches noires enfoncees", "taches seches cabosse", "lesion superficielle"]}
        ],
        "remede": (
            "• Souvent lié à une faiblesse générale de l'arbre. Apport d'engrais équilibré.\n"
            "• Pulvérisation cuprique combinée lors des traitements contre la pourriture brune."
        )
    },
    "MORT_SUBITE": {
        "nom": "Mort Subite / Dépérissement à Lasiodiplodia (Lasiodiplodia theobromae)",
        "classe": "Fongique / Vasculaire",
        "diagnostics": [
            {"id": "Dépérissement foliaire fulgurant", "symptomes": ["dessechement brutal feuilles", "feuilles marron attachees"]},
            {"id": "Atteinte du système vasculaire", "symptomes": ["stries noires bois", "stries grises coupe", "blocage seve"]}
        ],
        "remede": (
            "• Éliminer l'arbre mort pour éviter que l'insecte vecteur (souche de scolyte) ne propage le champignon.\n"
            "• Réduire les stress hydriques par un paillage épais au sol."
        )
    },
    "SWOLLEN_SHOOT_VASCULAIRE": {
        "nom": "Virus du Swollen Shoot - Forme Vasculaire (CSSV)",
        "classe": "Virale",
        "diagnostics": [
            {"id": "Hypertrophie des rameaux", "symptomes": ["gonflement des rameaux", "rameaux gonfles", "noeuds canne a sucre", "tiges en massue"]},
            {"id": "Hypertrophie racinaire", "symptomes": ["gonflement racines", "racines pivotantes gonflees"]}
        ],
        "remede": (
            "⚠️ AUCUN TRAITEMENT CHIMIQUE CURATIF.\n"
            "• Arrachage complet de l'arbre malade ainsi que de tous les arbres voisins dans un rayon de 5 à 10 mètres (ceinture de sécurité).\n"
            "• Incinération sur place des résidus arrachés."
        )
    },
    "SWOLLEN_SHOOT_FOLIAIRE": {
        "nom": "Virus du Swollen Shoot - Forme Foliaire Chlorotique (CSSV)",
        "classe": "Virale",
        "diagnostics": [
            {"id": "Symptômes de mosaïque foliaire", "symptomes": ["decoloration nervures", "mosaique rouge", "mosaique jaune", "feuilles miniatures", "feuilles en faux"]},
            {"id": "Atrophie des cabosses", "symptomes": ["cabosses petites", "cabosses rondes", "cabosses spheriques", "feves trophiees", "changement couleur precoce"]}
        ],
        "remede": (
            "• Application stricte du protocole d'éradication nationale (arrachage et barrière sanitaire).\n"
            "• Replantation exclusive avec des semences certifiées tolérantes (matériel végétal fourni par le CNRA / FIRCA).\n"
            "• Élimination des plantes hôtes alternatives du virus en bordure de parcelle (ex: Cola chlamydantha)."
        )
    },
    "MOSAIQUE_CMV": {
        "nom": "Virus de la Mosaïque du Cacaoyer (CMV)",
        "classe": "Virale",
        "diagnostics": [
            {"id": "Forme marbrée classique", "symptomes": ["marbrures vert clair", "feuilles adultes alternees", "perte lente rendement"]}
        ],
        "remede": (
            "• Surveillance et contrôle biologique des insectes vecteurs (pucerons).\n"
            "• Maintien de la vigueur de l'arbre par fertilisation organique soutenue."
        )
    },
    "CAPSIDES_MIRIDES": {
        "nom": "Attaque de Capsides / Mirides (Sahlbergella / Distantiella)",
        "classe": "Parasitaire / Insecte",
        "diagnostics": [
            {"id": "Dégâts sur cabosses", "symptomes": ["piqures sur cabosses", "taches noires circulaires", "cratères coque", "suintement seve"]},
            {"id": "Dégâts sur pousses et branches", "symptomes": ["dessechement rameaux", "grillage jeunes feuilles", "chancres liégeux", "cortex noir"]}
        ],
        "remede": (
            "• Traitement insecticide ciblé (néonicotinoïdes ou pyréthrinoïdes homologués) localisé uniquement sur les poches de capsides (généralement en août/septembre et janvier/février).\n"
            "• Réduction de l'ombrage excessif qui favorise leur prolifération."
        )
    },
    "FOREUR_DE_TIGES": {
        "nom": "Foreur de Tiges et de Troncs (Eulophonotus myrmeleon)",
        "classe": "Parasitaire / Insecte",
        "diagnostics": [
            {"id": "Signes de perforation active", "symptomes": ["trous tronc", "trous branches", "sciure de bois au sol", "excrements larvaires"]},
            {"id": "Impact sur la charpente", "symptomes": ["fletrissement branche maitresse", "mort au-dessus perforation", "casse branche"]}
        ],
        "remede": (
            "• Insérer un fil de fer flexible et cranté dans la galerie pour transpercer et tuer la larve.\n"
            "• Injecter une solution répulsive ou huileuse dans le trou, puis boucher immédiatement la galerie avec de l'argile ou du mastic."
        )
    },
    "COCHENILLES_VECTRICES": {
        "nom": "Cochenilles Vectrices (Pseudococcidae)",
        "classe": "Parasitaire / Insecte",
        "diagnostics": [
            {"id": "Amas cotonneux visibles", "symptomes": ["amas cotonneux", "poudre blanche pedoncules", "cochenilles bourgeons"]},
            {"id": "Symbiose avec les fourmis", "symptomes": ["fourmis noires tronc", "circulation fourmis", "presence fourmiliere"]}
        ],
        "remede": (
            "• Destructuration des nids de fourmis à la base du tronc.\n"
            "• Application d'huiles blanches végétales ou de savon noir pulvérisé pour étouffer les cochenilles."
        )
    },
    "THRIPS": {
        "nom": "Thrips du Cacaoyer (Selenothrips rubrocinctus)",
        "classe": "Parasitaire / Insecte",
        "diagnostics": [
            {"id": "Infection foliaire inférieure", "symptomes": ["larves jaunes bande rouge", "excrements noirs goudron", "insectes noirs sous feuilles"]},
            {"id": "Changement de couleur et défoliation", "symptomes": ["teinte bronzee", "feuilles argentées", "aspect metallique", "chute de feuilles masse"]}
        ],
        "remede": (
            "• Augmenter l'ombrage si la parcelle est trop exposée au soleil direct (les thrips adorent la lumière forte).\n"
            "• Pulvérisation d'extraits de neem (biopesticide) en cas de forte infestation."
        )
    },
    "PUCERONS": {
        "nom": "Pucerons du Cacaoyer (Toxoptera aurantii)",
        "classe": "Parasitaire / Insecte",
        "diagnostics": [
            {"id": "Colonies sur axes tendres", "symptomes": ["pucerons noirs", "colonies tiges florales", "pucerons cherelles"]},
            {"id": "Déformation végétative", "symptomes": ["enroulement jeunes feuilles", "avortement fleurs", "epuisement seve"]}
        ],
        "remede": (
            "• Généralement régulé naturellement par les larves de syrphes et de coccinelles.\n"
            "• En cas d'attaque bloquant la floraison : douche foliaire à l'eau savonneuse."
        )
    },
    "TEIGNE_FOREUR_CABOSSE": {
        "nom": "Teigne / Foreur de Cabosses (Conopomorpha cramerella)",
        "classe": "Parasitaire / Insecte",
        "diagnostics": [
            {"id": "Murissement anormal externe", "symptomes": ["murissement zebre", "zones vertes jaunes", "galeries placenta"]},
            {"id": "Altération des fèves", "symptomes": ["feves collees", "feves dures", "ecabossage impossible"]}
        ],
        "remede": (
            "• Ensachage des jeunes cabosses avec du plastique perforé (pratique intensive).\n"
            "• Récolte complète et absolue sans laisser aucun fruit mûrir au-delà de la date limite pour casser le cycle de ponte du papillon."
        )
    },
    "DESTRUCTION_ECUREUILS": {
        "nom": "Destruction par Écureuils (Sciuridae)",
        "classe": "Animalière / Rongeur",
        "diagnostics": [
            {"id": "Attaque latérale nette", "symptomes": ["trou beant lateral", "bords biseautés", "marques incisives", "cabosse vide"]},
            {"id": "Résidus au sol", "symptomes": ["coques vides au sol", "mucilage suce", "cabosses grignotees"]}
        ],
        "remede": (
            "• Désherbage total sous les arbres pour supprimer le tapis de progression des rongeurs.\n"
            "• Pose de colliers métalliques lisses (manchons anti-rongeurs) autour du tronc à 1 m du sol pour empêcher l'ascension."
        )
    },
    "ATTAQUE_RATS": {
        "nom": "Attaque de Rats des Champs (Rattus spp.)",
        "classe": "Animalière / Rongeur",
        "diagnostics": [
            {"id": "Perforation basse désordonnée", "symptomes": ["perforations irregulieres", "coque dechiquetee", "feves eparpillees", "attaque pres du sol"]}
        ],
        "remede": (
            "• Hygiène stricte de la plantation : ne pas laisser de tas de cabosses écabossées pourrir au milieu de la parcelle.\n"
            "• Utilisation de pièges mécaniques locaux disposés le long des pistes de passage."
        )
    },
    "CHERELLE_WILT": {
        "nom": "Cherelle Wilt (Flétrissement Physiologique)",
        "classe": "Physiologique / Cellulaire",
        "diagnostics": [
            {"id": "Momification nutritionnelle", "symptomes": ["cherelles jaunes", "petits fruits noirs", "fruits rides", "fruits momifies", "cabosses suspendues seches"]}
        ],
        "remede": (
            "⚠️ FAILLITE CELLULAIRE / AUTO-RÉGULATION (NON INFECTIEUX).\n"
            "• Apport de fumure organique (compost de fèves ou fientes) riche en Potassium et en Bore.\n"
            "• Paillage massif du sol sur un rayon d'un mètre autour du tronc pour conserver l'eau en saison sèche."
        )
    },
    "CARENCE_AZOTE": {
        "nom": "Carence Critique en Azote (N)",
        "classe": "Carence Minérale",
        "diagnostics": [
            {"id": "Chlorose générale uniforme", "symptomes": ["jaunissement uniforme feuillage", "nervures jaunes", "feuilles reduites", "croissance stoppee"]}
        ],
        "remede": (
            "• Épandage d'urée ou apport massif de compost riche en matières azotées avant le cycle des pluies.\n"
            "• Intégration de légumineuses d'ombrage (Albizia, Gliricidia) qui fixent l'azote de l'air."
        )
    },
    "CARENCE_PHOSPHORE": {
        "nom": "Carence Critique en Phosphore (P)",
        "classe": "Carence Minérale",
        "diagnostics": [
            {"id": "Forme pourpre périphérique", "symptomes": ["coloration vert fonce feuilles", "bords violaces", "bords pourpres", "chute feuilles inferieures", "racines fragiles"]}
        ],
        "remede": (
            "• Apport de phosphate naturel ou de superphosphate triple au niveau de la couronne racinaire pour stimuler le système souterrain."
        )
    },
    "CARENCE_POTASSIUM": {
        "nom": "Carence Critique en Potassium (K)",
        "classe": "Carence Minérale",
        "diagnostics": [
            {"id": "Brûlure marginale du limbe", "symptomes": ["necrose marginale", "bord feuille sec", "feuille brulee par le feu", "pointe marron clair"]}
        ],
        "remede": (
            "• Épandage de sulfate de potasse ou de cendres de coques de cacao bien réparties sous la projection du feuillage."
        )
    },
    "CARENCE_BORE": {
        "nom": "Carence en Bore (B)",
        "classe": "Carence Minérale",
        "diagnostics": [
            {"id": "Déformation des fruits", "symptomes": ["cabosses deformees", "cabosses bosselees", "cabosses tordues", "coque dure epaisse", "cabosses vides"]},
            {"id": "Perte de dominance apicale", "symptomes": ["mort bourgeons terminaux", "ramification excessive", "branches desordonnees"]}
        ],
        "remede": (
            "• Application au sol ou pulvérisation foliaire fine de borax (solubor) à très faible dose en respectant scrupuleusement les prescriptions agronomiques."
        )
    }
}

import sqlite3
import time

# --- DICTIONNAIRE TERRAIN DE LEYLA (25 PATHOLOGIES & RAVAGEURS) ---
DICTIONNAIRE_DIAGNOSTIC = {
    "1. Pourriture brune des cabosses (Phytophthora)": [
        "tache noire", "taches noires", "cabosse noire", "pourri", "pourriture", 
        "jus noir", "odeur forte", "moulue noire", "cabosse marron", "chocolat noir"
    ],
    "2. Attaque de Mirides / Punaises (Sahlbergella / Distantiella)": [
        "tache brune", "taches brunes", "piqûre", "piqure", "desséché", 
        "cabosse grillée", "trous sur cabosse", "cratère", "dessèchement", "brûlure"
    ],
    "3. Cochenilles (Vecteurs du Swollen Shoot)": [
        "point blanc", "points blancs", "poudre blanche", "coton", 
        "substance collante", "pucerons blancs", "amas blanc", "fourmis"
    ],
    "4. Virus du Swollen Shoot (CSSV)": [
        "gonflement", "rameau gonflé", "mosaïque", "feuille rouge", 
        "strie rouge", "jaunissement des veines", "baisse de rendement", "tiges déformées"
    ],
    "5. Chancre du tronc (Phytophthora palmivora)": [
        "liquide rouge", "liquide brun", "tronc qui coule", "blessure rouge", 
        "écorce fendue", "saignement", "écorce craquelée", "gomme"
    ],
    "6. Chenilles & Foreurs de tiges (Eulophonotus)": [
        "trous dans le bois", "sciure", "chenille", "tige cassée", 
        "galerie", "feuilles mangées", "trous de foreur"
    ],
    "7. Anthracnose (Colletotrichum gloeosporioides)": [
        "taches nécrotiques", "bords desséchés", "feuilles perforées", 
        "taches avec aureole", "dessèchement des jeunes feuilles"
    ],
    "8. Maladie du balai de sorcière (Moniliophthora perniciosa)": [
        "branches en balai", "ramification excessive", "mousse de rameaux", 
        "cabosse en forme de fraise", "déformation des bourgeons"
    ],
    "9. Moniliose (Moniliophthora roreri)": [
        "poussière blanche", "cabosse lourde", "poudre grise", "cabosse bosseuse", 
        "tache marron avec poudre"
    ],
    "10. Trachéomycose / Flétrissement vasculaire (Fusarium)": [
        "flétrissement rapide", "feuilles sèches restées accrochées", 
        "jaunissement brutal", "dessèchement d'un côté de l'arbre"
    ],
    "11. Pourridié racinaire (Rosellinia / Armillaria)": [
        "racines pourries", "filaments blancs sous l'écorce", "champignon au pied", 
        "arbre qui tombe", "déchaussement"
    ],
    "12. Termites / Mutilation des racines et troncs": [
        "galeries de terre", "tunnels de terre", "bois mangé", "termites", 
        "tronc creux", "terre sur le tronc"
    ],
    "13. Thrips du cacaoyer (Selenothrips rubrocinctus)": [
        "feuilles argentées", "aspect plombé", "gouttes noires sous feuilles", 
        "feuilles bronzées", "chute des feuilles"
    ],
    "14. Pucerons du cacaoyer (Toxoptera aurantii)": [
        "petits insectes noirs", "pucerons noirs", "jeunes pousses crispées", 
        "feuilles enroulées", "jabon"
    ],
    "15. Charançons / Borer des cabosses": [
        "petits trous sur cabosse", "sciure sur cabosse", "larve dans cabosse", 
        "cabosse trouée"
    ],
    "16. Rats et Écureuils (Rongeurs)": [
        "cabosse rongée", "trous de dents", "coque ouverte", "fèves mangées", 
        "reste de cabosse par terre"
    ],
    "17. Carence en Azote (N)": [
        "jaunissement général", "anciennes feuilles jaunes", "petite taille", 
        "arbre pâle", "manque de vigueur"
    ],
    "18. Carence en Potassion (K)": [
        "bord des feuilles brûlé", "brûlure marginale", "dessèchement de la pointe", 
        "feuilles enroulées vers le bas"
    ],
    "19. Carence en Phosphore (P)": [
        "feuilles violettes", "teinte pourpre", "feuilles vert foncé rigides", 
        "retard de croissance"
    ],
    "20. Carence en Zinc (Zn) / Feuille en faucille": [
        "feuilles étroites", "feuilles déformées en faux", "petite feuille", 
        "feuille ondulée"
    ],
    "21. Grillure du feuillage / Coup de soleil (Stress hydrique)": [
        "feuilles grilées", "brûlure du soleil", "feuilles cassantes", 
        "chute massive en saison sèche"
    ],
    "22. Mousse et Epiphytes (Lichen / Guppy)": [
        "mousse verte", "lichen blanc", "tronc couvert de plante", 
        "liane étrangleuse", "barbe sur branches"
    ],
    "23. Cherelle Wilt (Avortement naturel des jeunes cabosses)": [
        "petite cabosse jaune", "cherelle noire sèche", "petite cabosse flétrie", 
        "avortement sans attaque"
    ],
    "24. Attaque de Loranthus (Plante parasite / Mistletoe)": [
        "plante incrustée", "grosse boule verte sur branche", "parasite sur branche", 
        "fleurs rouges parasites"
    ],
    "25. Dégâts de Rongeurs et Pigeons (Oiseaux / Piqueurs)": [
        "coups de bec", "trous d'oiseaux", "cabosse piquée"
    ]
}

def analyser_description_terrain(texte_saisi):
    """Analyse le texte saisi par le technicien et retourne la liste des maladies correspondantes."""
    if not texte_saisi:
        return []
        
    texte = texte_saisi.lower()
    maladies_detectees = []
    
    for maladie, mots_cles in DICTIONNAIRE_DIAGNOSTIC.items():
        for mot in mots_cles:
            if mot in texte:
                if maladie not in maladies_detectees:
                    maladies_detectees.append(maladie)
                break
                
    return maladies_detectees

# --- OUTILS DE TRAITEMENT TEXTE ---

def nettoyer_texte(txt):
    """Nettoie le texte, retire les mots vides et normalise les pluriels."""
    mots_ig = ["des", "de", "la", "le", "les", "un", "une", "au", "aux", "du", "d", "l"]
    mots_filtres = [m for m in str(txt).lower().split() if m not in mots_ig]
    return " ".join([m[:-1] if m.endswith('s') and len(m) > 3 else m for m in mots_filtres])

def moteur_cognitif_leyla(liste_symptomes_bruts, texte_integral=""):
    """Moteur d'analyse croisée des symptômes."""
    historique_nettoye = nettoyer_texte(texte_integral)
    pistes_identifiees = []

    for nom_cle, data in DIAGNOSTIQUE.items():
        tous_symptomes_maladie = []
        if "diagnostics" in data:
            for diag in data["diagnostics"]:
                if isinstance(diag, dict) and "symptomes" in diag:
                    tous_symptomes_maladie.extend(diag["symptomes"])
                elif isinstance(diag, list):
                    tous_symptomes_maladie.extend(diag)
        elif "symptomes" in data:
            tous_symptomes_maladie.extend(data["symptomes"])

        preuves_reelles = []
        for s in tous_symptomes_maladie:
            s_clean = nettoyer_texte(s)
            if s_clean in historique_nettoye:
                if s not in preuves_reelles:
                    preuves_reelles.append(s)

        if preuves_reelles:
            score = len(preuves_reelles) * 30
            pistes_identifiees.append({
                "cle": nom_cle,
                "nom": data.get("nom", nom_cle),
                "classe": data.get("classe", "Inconnue"),
                "score": score,
                "preuves": preuves_reelles,
                "remede": data.get("remede", "Aucun remède spécifié.")
            })

    pistes_identifiees = sorted(pistes_identifiees, key=lambda x: x["score"], reverse=True)

    if not pistes_identifiees:
        return "Dis donc, je n'ai repéré aucun symptôme clair dans ce que tu m'as partagé. On reprend calmement ?", []

    rapport = "--- 🧬 RAPPORT D'EXPERTISE INTER-FAMILLE DE LEYLA ---\n\n"
    classes_presentes = set(p['classe'] for p in pistes_identifiees)
    
    if len(classes_presentes) > 1:
        rapport += "⚠️ **Attention l'ami : J'ai détecté une synergie pathologique ou des attaques multiples croisées sur ta parcelle !**\n\n"
    else:
        rapport += "✅ **Analyse monopathologique ciblée.**\n\n"

    maladies_retenues = []
    for p in pistes_identifiees:
        taux_confiance = min(99, 70 + (p['score'] * 5))
        rapport += f"• **Maladie détectée : {p['nom']}**\n"
        rapport += f"  - *Classe :* {p['classe']}\n"
        rapport += f"  - *Indice de certitude :* {taux_confiance}%\n"
        rapport += f"  - *Symptômes retenus :* `{', '.join(p['preuves'])}`\n"
        rapport += f"\n  - *Mon conseil d'ingénieur / Protocole :*\n{p['remede']}\n\n"
        maladies_retenues.append(p['nom'])

    return rapport, maladies_retenues

# --- INTERFACE UTILISATEUR (STREAMLIT) ---

def afficher():
    if st.button("⬅️ Retour à l'accueil Leyla"):
        st.session_state.module_actif = "accueil"
        st.rerun()

    st.title("🩺 Leyla - Ingénieur Agronome")
    st.write("Salut ! C'est Leyla. Écris-moi ce que tu observes sur tes cacaoyers. Quand tu as terminé, tape **« c'est terminé »**.")

    # Session states
    if "messages_diag_leyla" not in st.session_state:
        msg_accueil = "Salut à toi l'ami ! Dis-moi, qu'est-ce que tu observes d'anormal sur tes cacaoyers ?"
        st.session_state.messages_diag_leyla = [{"role": "assistant", "content": msg_accueil}]

    if "symptomes_detectes_leyla" not in st.session_state:
        st.session_state.symptomes_detectes_leila = []
    if "diagnostic_final_cache_leyla" not in st.session_state:
        st.session_state.diagnostic_final_cache_leyla = None

    # Historique de discussion
    for msg in st.session_state.messages_diag_leyla:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Zone de Saisie Utilisateur par texte
    saisie_utilisateur = st.text_input(
        "Saisissez vos symptômes ou vos observations :",
        key="input_leyla_unique"
    )

    btn_envoyer = st.button("Envoyer 💬", key="btn_send_diag")

    if btn_envoyer and saisie_utilisateur:
        texte_traitement = saisie_utilisateur
        st.session_state.messages_diag_leyla.append({"role": "user", "content": texte_traitement})

        texte_lower = texte_traitement.lower()

        if any(mot in texte_lower for mot in ["c'est terminé", "c'est fini", "fini", "terminé"]):
            texte_complet_discussion = " ".join([m["content"] for m in st.session_state.messages_diag_leyla if m["role"] == "user"])
            
            resultat_diag, noms_maladies = moteur_cognitif_leyla(st.session_state.symptomes_detectes_leila, texte_complet_discussion)
            
            st.session_state.diagnostic_final_cache_leyla = {
                "diagnostic": resultat_diag,
                "maladies": noms_maladies,
                "symptomes": st.session_state.symptomes_detectes_leila.copy()
            }
            reponse_leyla = f"🔍 **Entretien clos, chef !** J'ai bouclé l'analyse. Voici mon rapport complet :\n\n{resultat_diag}"
        else:
            mots_trouves = []
            texte_compare = nettoyer_texte(texte_lower)

            for nom_cle, data in DIAGNOSTIQUE.items():
                tous_symptomes = []
                if "diagnostics" in data:
                    for diag in data["diagnostics"]:
                        if isinstance(diag, dict) and "symptomes" in diag:
                            tous_symptomes.extend(diag["symptomes"])
                        elif isinstance(diag, list):
                            tous_symptomes.extend(diag)
                elif "symptomes" in data:
                    tous_symptomes.extend(data["symptomes"])

                for s in tous_symptomes:
                    s_clean = nettoyer_texte(s)
                    if s_clean in texte_compare:
                        if s not in st.session_state.symptomes_detectes_leila:
                            st.session_state.symptomes_detectes_leila.append(s)
                        if s not in mots_trouves:
                            mots_trouves.append(s)

            if mots_trouves:
                reponse_leyla = f"J'ai bien noté ça l'ami : `{', '.join(mots_trouves)}`. Tu vois autre chose d'anormal ? (Sinon, tape **« c'est terminé »**)."
            else:
                reponse_leyla = "Hmm, je ne retrouve pas ce symptôme précis. Peux-tu préciser un peu plus (ex: cabosses noires, fleurs déformées, feuilles jaunies...) ?"

        st.session_state.messages_diag_leyla.append({"role": "assistant", "content": reponse_leyla})
        st.rerun()

    # --- ENREGISTREMENT EN BASE LOCALE (SQLITE) ---
    if st.session_state.diagnostic_final_cache_leyla:
        st.markdown("---")
        st.info("📌 **Enregistrement local** (Le rapport sera stocké sur la tablette en attente de synchronisation).")
        
        info_prod = st.session_state.get("info_producteur", {})
        col_n, col_z = st.columns(2)
        nom_prod = col_n.text_input("Nom du Producteur", value=info_prod.get("nom", "Producteur Local"), key="input_nom_prod_diag")
        zone_prod = col_z.text_input("Zone / Localité", value=st.session_state.get("section", "Zone Centre"), key="input_zone_prod_diag")

        if st.button("💾 Sauvegarder localement (En attente de synchro)", type="primary", key="btn_envoi_chef_diag"):
            nouveau_rapport = {
                "nom": nom_prod,
                "zone": zone_prod,
                "diagnostic": st.session_state.diagnostic_final_cache_leyla["diagnostic"],
                "symptomes_observes": st.session_state.diagnostic_final_cache_leyla["symptomes"],
                "statut_eudr": "Conforme / Diagnostiqué par Leyla"
            }

            # Sauvegarde dans leyla_terrain.db pour la synchronisation
            sauvegarder_en_local_sqlite(nouveau_rapport)

            st.success("💾 Rapport phytosanitaire sauvegardé dans la tablette ! Prêt pour la synchronisation.")
            
            # Réinitialisation
            st.session_state.diagnostic_final_cache_leyla = None
            st.session_state.symptomes_detectes_leila = []
            st.session_state.messages_diag_leyla = [
                {"role": "assistant", "content": "Nouveau diagnostic initialisé. Qu'est-ce qui cloche sur la parcelle ?"}
            ]
            time.sleep(1.5)
            st.rerun()

if __name__ == "__main__":
    afficher()
