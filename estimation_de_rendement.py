import streamlit as st
import time
import os
import json
try:
    from streamlit_geolocation import streamlit_geolocation
except ImportError:
    streamlit_geolocation = None


# --- INITIALISATIONS GLOBALES EN TOUT PREMIER ---
if 'etape_courante' not in st.session_state:
    st.session_state.etape_courante = 1
if 'sous_etape' not in st.session_state:
    st.session_state.sous_etape = 1
if 'data_rendement' not in st.session_state:
    st.session_state.data_rendement = {}
if 'nombre_carres' not in st.session_state:
    st.session_state.nombre_carres = 3
if 'index_carre_actuel' not in st.session_state:
    st.session_state.index_carre_actuel = 1
if 'donnees_carres' not in st.session_state:
    st.session_state.donnees_carres = []
if 'saisie_carres_terminee' not in st.session_state:
    st.session_state.saisie_carres_terminee = False


# --- Fonctions de Diagnostic Autonomes (Sans moteur externe) ---
def analyser_sante_locale(cssv, assainissement, elagage):
    alertes = []
    if cssv == "Présence visible":
        alertes.append("⚠️ Attaque de Swollen Shoot (CSSV) détectée")
    if assainissement == "OUI":
        alertes.append("⚠️ Risque phytosanitaire (Résidus présents)")
    if elagage == "NON":
        alertes.append("⚠️ Élégage nécessaire pour réduire l'ombrage excessif")
    
    if not alertes:
        return "✅ État sanitaire global de la parcelle : Bon"
    return " Diagnostic Santé : " + " | ".join(alertes)

def analyser_fertilite_locale(texture_sol, engrais_type):
    return f"🌱 Fertilité : Sol {texture_sol} | Apport engrais : {engrais_type}"

def analyser_productivite_locale(age, ombrage, recolte):
     status = "Optimale" if 8 <= age <= 20 else "Jeune plantation ou vieillissante"
     return f"📈 Productivité : Plantation de {age} ans ({status}) | Arbres d'ombrage : {ombrage}"


# --- Fonctions des Parties ---
def afficher_partie_1():
    st.subheader("Partie 1 : Informations du Producteur")
    zones_data = {
        "Zone A - Littoral Sud-Ouest": ["San Pedro", "Grand-Béréby", "Odidio", "Gnato", "Grabo", "Neka", "Djouroutou"],
        "Zone B - Forêt Sud-Ouest": ["Soubré", "Méagui", "Taï", "Guiglo", "Zagné", "Gabiadji", "Touih"],
        "Zone C - Centre-Ouest forestier": ["Buyo", "Duékoué", "Bangolo", "Kouibly", "Danané"],
        "Zone D - Sud forestier oriental": ["Sassandra", "Fresco", "Gbagbam", "Gueyo", "Lakota"],
        "Zone E - Transition forêt-savane": ["Vavoua"]
    }
    zone = st.selectbox("Sélectionnez la Zone", list(zones_data.keys()), key="zone_est")
    ville = st.selectbox("Localité", zones_data[zone], key="ville_est")
    nom = st.text_input("Nom et Prénoms du Producteur", key="nom_est")
    contact = st.text_input("Contact", key="contact_est")
    cooperative = st.text_input("Coopérative", key="coop_est")
    matricule = st.text_input("Matricule CCC", key="mat_est")
    section = st.text_input("Section", key="sec_est")
    superficie = st.number_input("Superficie (ha)", min_value=0.0, key="sup_est")
    annee = st.number_input("Année de création", min_value=1900, max_value=2050, key="annee_est")
    
    if st.button("Suivant", key="btn_suivant_p1_est"):
        st.session_state.data_rendement.update({
            "zone": zone, "ville": ville, "nom": nom, "contact": contact,
            "cooperative": cooperative, "matricule": matricule, 
            "section": section, "superficie": superficie, "annee": annee
        })
        st.session_state.etape_courante = 2
        st.rerun()


def afficher_partie_2():
    if 'sous_etape' not in st.session_state:
        st.session_state.sous_etape = 1
        
    st.subheader("Partie 2 : Diagnostic de la Plantation")
    st.progress(st.session_state.sous_etape / 14)
    s = st.session_state.sous_etape
    
    if s == 1:
        st.write("### 1. Coordonnées GPS")
        if st.button("📍 Capturer la position", key="btn_gps_capture_final"):
            if streamlit_geolocation:
                st.session_state.gps = streamlit_geolocation()
            else:
                st.warning("Module GPS Web indisponible.")
        if 'gps' in st.session_state and st.session_state.gps:
            st.write("Position capturée :", st.session_state.gps)
        
    elif s == 2:
        st.session_state.data_rendement['pluvio'] = st.radio("2. Appréciation de la pluviométrie", ["BON", "MOYEN", "MAUVAIS"], key="r_pluvio")
    elif s == 3:
        st.session_state.data_rendement['recolte'] = st.number_input("3. Récolte de l'année dernière (kg)", min_value=0, key="n_recolte")
    elif s == 4:
        st.session_state.data_rendement['materiel'] = st.radio("4. Matériel végétal utilisé", ["cnra", "Tout Venant"], key="r_materiel")
    elif s == 5:
        st.session_state.data_rendement['prod_max'] = st.number_input("5. Production annuelle la plus élevée (kg)", min_value=0, key="n_prod_max")
    elif s == 6:
        st.session_state.data_rendement['age_arbres'] = st.number_input("6. Âge des arbres (années)", min_value=0, key="n_age")
    elif s == 7:
        st.session_state.data_rendement['cssv'] = st.radio("7. Maladies incurables (CSSV)", ["Aucune présence", "Présence visible"], key="r_cssv")
    elif s == 8:
        st.session_state.data_rendement['assainissement'] = st.radio("8. Présence résidus (cabosses/emballages)", ["OUI", "NON"], key="r_assainissement")
    elif s == 9:
        st.session_state.data_rendement['mauvaises_herbes'] = st.radio("9. Mauvaises herbes (> 0.5m)", ["Moins de 20%", "Plus de 20%"], key="r_herbes")
    elif s == 10:
        st.session_state.data_rendement['ombrage'] = st.number_input("10. Nombre d'arbres d'ombrage", min_value=0, key="n_ombrage")
    elif s == 11:
        st.session_state.data_rendement['texture_sol'] = st.radio("11. État du sol", ["Argileux", "Sableux", "Argilo-sableux", "Sablo-argileux", "Gravionnaire"], key="r_sol")
    elif s == 12:
        st.session_state.data_rendement['microbienne'] = st.radio("12. Présence microbienne", ["OUI", "NON"], key="r_micro")
    elif s == 13:
        st.session_state.data_rendement['engrais_type'] = st.radio("13. Formulation d'engrais", ["NPK-0-23-19", "Compost/Organique", "Autres"], key="r_engrais")
    elif s == 14:
        st.session_state.data_rendement['elagage'] = st.radio("14. Plantation bien taillée ?", ["OUI", "NON"], key="r_elagage")

    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Retour", key=f"btn_retour_p2_{s}"):
            if st.session_state.sous_etape > 1:
                st.session_state.sous_etape -= 1
                st.rerun()
            else:
                st.session_state.etape_courante = 1
                st.rerun()

    with col2:
        if st.button("Suivant ➡️", key=f"btn_suivant_p2_{s}"):
            if st.session_state.sous_etape < 14:
                st.session_state.sous_etape += 1
                st.rerun()
            else:
                st.session_state.etape_courante = 3
                st.rerun()


def afficher_estimation():
    st.subheader("Partie 3 : Diagnostic et Comptage par Carré")
    
    if 'nombre_carres' not in st.session_state:
        st.session_state.nombre_carres = 3
    if 'index_carre_actuel' not in st.session_state:
        st.session_state.index_carre_actuel = 1
    if 'donnees_carres' not in st.session_state:
        st.session_state.donnees_carres = []
    if 'saisie_carres_terminee' not in st.session_state:
        st.session_state.saisie_carres_terminee = False

    if not st.session_state.saisie_carres_terminee and len(st.session_state.donnees_carres) == 0 and st.session_state.index_carre_actuel == 1:
        st.session_state.nombre_carres = st.number_input(
            "Combien de carrés d'échantillonnage (10m x 10m) souhaitez-vous analyser ?", 
            min_value=1, max_value=10, value=st.session_state.nombre_carres, step=1, key="input_choix_n_carres"
        )

    total_carres = st.session_state.nombre_carres
    i_carre = st.session_state.index_carre_actuel

    if not st.session_state.saisie_carres_terminee:
        st.write(f"### Carré {i_carre} sur {total_carres} (10m x 10m)")
        
        nb_pieds = st.number_input(f"Nbre de pieds de cacaoyers (Carré {i_carre})", min_value=0, value=15, key=f"c_pieds_{i_carre}")
        nb_productifs = st.number_input(f"Nbre d'arbres productifs (Carré {i_carre})", min_value=0, value=12, key=f"c_prod_{i_carre}")
        
        st.write("#### Comptage phénologique par arbre moyen / échantillon :")
        cabosses_mures = st.number_input("Nbre de cabosses mûres (Récolte immédiate)", min_value=0, value=10, key=f"c_mures_{i_carre}")
        cabosses_jeunes = st.number_input("Nbre de cabosses jeunes (1 à 2 mois)", min_value=0, value=15, key=f"c_jeunes_{i_carre}")
        chereles = st.number_input("Nbre de chérèles (4 à 5 mois)", min_value=0, value=25, key=f"c_chereles_{i_carre}")
        fleurs = st.number_input("Estimation du nbre de fleurs (Long terme)", min_value=0, value=40, key=f"c_fleurs_{i_carre}")

        col1, col2 = st.columns(2)
        with col1:
            if i_carre > 1:
                if st.button("⬅️ Carré Précédent", key=f"btn_prec_carre_{i_carre}"):
                    st.session_state.index_carre_actuel -= 1
                    st.rerun()
        with col2:
            if st.button("Carré Suivant ➡️" if i_carre < total_carres else "Terminer les Carrés 🏁", key=f"btn_suiv_carre_{i_carre}"):
                donnees_c = {
                    "carre": i_carre, "nb_pieds": nb_pieds, "nb_productifs": nb_productifs,
                    "cabosses_mures": cabosses_mures, "cabosses_jeunes": cabosses_jeunes,
                    "chereles": chereles, "fleurs": fleurs
                }
                
                if len(st.session_state.donnees_carres) >= i_carre:
                    st.session_state.donnees_carres[i_carre - 1] = donnees_c
                else:
                    st.session_state.donnees_carres.append(donnees_c)

                if i_carre < total_carres:
                    st.session_state.index_carre_actuel += 1
                    st.rerun()
                else:
                    st.session_state.saisie_carres_terminee = True
                    st.session_state.data_rendement["details_carres"] = st.session_state.donnees_carres
                    st.session_state.data_rendement["horodatage"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Exécution du diagnostic local
                    data = st.session_state.data_rendement
                    diag_sante = analyser_sante_locale(data.get('cssv'), data.get('assainissement'), data.get('elagage'))
                    diag_fert = analyser_fertilite_locale(data.get('texture_sol'), data.get('engrais_type'))
                    diag_prod = analyser_productivite_locale(data.get('age_arbres'), data.get('ombrage'), data.get('recolte', 0))
                    
                    st.session_state.diag_sante = diag_sante
                    st.session_state.diag_fert = diag_fert
                    st.session_state.diag_prod = diag_prod
                    st.session_state.data_rendement["diagnostic"] = f"{diag_sante} | {diag_fert} | {diag_prod}"

                    superficie_ha = st.session_state.data_rendement.get("superficie", 1.0)
                    if superficie_ha <= 0: 
                        superficie_ha = 1.0

                    total_mures = sum(c["cabosses_mures"] for c in st.session_state.donnees_carres)
                    total_jeunes = sum(c["cabosses_jeunes"] for c in st.session_state.donnees_carres)
                    total_chereles = sum(c["chereles"] for c in st.session_state.donnees_carres)
                    moy_prod = sum(c["nb_productifs"] for c in st.session_state.donnees_carres) / total_carres
                    pieds_totaux_estimes = moy_prod * 100 * superficie_ha
                    
                    st.session_state.resultats_previsionnels = {
                        "immediat": round((total_mures / total_carres * pieds_totaux_estimes) / 22000, 2),
                        "court_terme": round((total_jeunes / total_carres * pieds_totaux_estimes * 0.85) / 22000, 2),
                        "moyen_terme": round((total_chereles / total_carres * pieds_totaux_estimes * 0.20) / 22000, 2)
                    }
                    st.session_state.data_rendement["previsions"] = st.session_state.resultats_previsionnels
                    st.rerun()
    else:
        st.write("### 🔍 Diagnostic Terrain")
        st.success(st.session_state.diag_sante)
        st.info(st.session_state.diag_fert)
        st.warning(st.session_state.diag_prod)
        
        st.write("---")
        st.write("### 📊 Calendrier Prévisionnel de Récolte")
        res = st.session_state.resultats_previsionnels
        st.success(f"🟢 **Récolte Immédiate (Cabosses mûres) :** ~{res['immediat']} Tonnes")
        st.info(f"🔵 **Court Terme / 1-2 mois (Cabosses jeunes) :** ~{res['court_terme']} Tonnes")
        st.warning(f"🟠 **Moyen Terme / 4-5 mois (Chérèles ajustées) :** ~{res['moyen_terme']} Tonnes")
        
        st.write("---")
        if st.button("🏁 Enregistrer et sauvegarder localement", type="primary", key="btn_sortir_p3_fin"):
            fichier_json = "base_de_donnees_layla.json"
            if os.path.exists(fichier_json):
                with open(fichier_json, "r", encoding="utf-8") as f:
                    try:
                        data_file = json.load(f)
                    except:
                        data_file = {}
            else:
                data_file = {}

            if "Estimation_Rendement" not in data_file:
                data_file["Estimation_Rendement"] = []

            data_file["Estimation_Rendement"].append(st.session_state.data_rendement)

            with open(fichier_json, "w", encoding="utf-8") as f:
                json.dump(data_file, f, indent=4, ensure_ascii=False)

            st.success("✅ Rapport enregistré avec succès dans la base locale !")
            st.balloons()
            
            # Réinitialisation des états
            st.session_state.data_rendement = {}
            st.session_state.gps = None  
            st.session_state.etape_courante = 1
            st.session_state.sous_etape = 1
            st.session_state.donnees_carres = []
            st.session_state.index_carre_actuel = 1
            st.session_state.saisie_carres_terminee = False
            st.session_state.nombre_carres = 3
            
            if 'module_actif' in st.session_state:
                st.session_state.module_actif = "accueil"
            
            time.sleep(1.5)
            st.rerun()


import sqlite3
import pandas as pd
import streamlit as st

# --- FONCTION UTILITAIRE DE CHARGEMENT SQLITE ---
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

# =========================================================================
# --- FLUX PRINCIPAL DU MODULE ---
# =========================================================================
def afficher():
    # 1. Chargement des données filtrées UNIQUEMENT pour l'Estimation de Rendement
    df = charger_donnees_par_module("Estimation de Rendement")

    st.title("📊 Estimation de Rendement")

    # 2. Section de consultation des enregistrements de rendement
    with st.expander(f"📁 Afficher / Masquer les données brutes ({len(df)} enregistrement(s))"):
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun enregistrement disponible pour l'estimation de rendement.")

    st.markdown("---")

    # 3. Initialisation de la gestion des étapes
    if "etape_courante" not in st.session_state:
        st.session_state.etape_courante = 1

    # 4. Navigation dans les étapes du module
    if st.session_state.etape_courante == 1:
        afficher_partie_1()
    elif st.session_state.etape_courante == 2:
        afficher_partie_2()
    elif st.session_state.etape_courante == 3:
        afficher_estimation()

if __name__ == "__main__":
    afficher()


