import streamlit as st
import pandas as pd
import pyttsx3
import threading
import speech_recognition as sr
import os
import re
from cerveau_central import sauvegarder_donnee

# --- DICTIONNAIRE AGRONOMIQUE DE L'INGÉNIEUR LEYLA ---
DIAGNOSTIQUE = {
    "POURRITURE_BRUNE": {
        "nom": "Pourriture Brune des Cabosses (Phytophthora palmivora / megakarya)",
        "classe": "Fongique / Oomycète",
        "diagnostics": [
            {"id": "Forme classique sur fruit (Cabosse)", "symptomes": ["tache brune", "cabosse noire", "pourriture", "feutrage blanc", "moisissure veloutee"]},
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

# --- OUTILS DE TRAITEMENT TEXTE ET AUDIO ---

def nettoyer_texte(txt):
    """Nettoie le texte, retire les mots vides et normalise les plurielles."""
    mots_ig = ["des", "de", "la", "le", "les", "un", "une", "au", "aux", "du", "d", "l"]
    mots_filtres = [m for m in str(txt).lower().split() if m not in mots_ig]
    return " ".join([m[:-1] if m.endswith('s') and len(m) > 3 else m for m in mots_filtres])

def parler(texte):
    """Synthèse vocale sécurisée pour éviter de bloquer Streamlit."""
    def run_engine():
        try:
            texte_pur = re.sub(r'[---🧬🔍⚠️✅•*`]', '', texte)
            texte_pur = re.sub(r'\s+', ' ', texte_pur).strip()
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 1.0)
            engine.say(texte_pur)
            engine.runAndWait()
        except Exception:
            pass # Évite de faire planter le flux GUI
            
    threading.Thread(target=run_engine, daemon=True).start()

def ecouter_micro():
    """Capture audio via microphone avec gestion d'erreurs propre."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.toast("🎙️ Leila t'écoute... Parle maintenant !", icon="🎙️")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            texte_recu = recognizer.recognize_google(audio, language="fr-FR")
            return texte_recu
    except sr.WaitTimeoutError:
        st.warning("Temps d'écoute dépassé. Réessaie.")
    except sr.UnknownValueError:
        st.warning("Je n'ai pas bien compris ce que tu as dit.")
    excep