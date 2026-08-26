# ==========================================================
# 5. MOTEURS D'AIGUILLAGE & CONTENU CENTRAL
# ==========================================================
def afficher_contenu():
    if st.session_state.page_actuelle == -1:
        st.title("🌿 Bienvenue sur LAYLA IA")
        st.subheader("Système Expert de Diagnostic Agricole")
        st.info(f"Utilisateur : Djè Akadjé | Date : {datetime.datetime.now().strftime('%d/%m/%Y')}")
        
        if st.button("Lancer le diagnostic"):
            st.session_state.page_actuelle = 0
            st.rerun()
    else:
        st.write(f"### Interface de saisie - Page {st.session_state.page_actuelle}")
        afficher_contenu_pdc()

def afficher_contenu_pdc():
    leila_tracker_central()
    n_page = st.session_state.page_actuelle
    pid = f"P{n_page}"

    # Configuration par défaut simulée pour injecter dans tes fonctions paramétrées (conf)
    mock_conf = {
        "titre": "Section Courante", "sous_titre": "Sous-section", "titre_epargne": "Suivi Épargne",
        "titre_production": "Historique Production", "titre_autres": "Autres revenus",
        "titre_depenses": "Dépenses d'Exploitation", "depenses_data": [["Entretien", "Annuel", 0]],
        "titre_main_oeuvre": "Main d'œuvre", "main_oeuvre_cols": ["Type", "Coût"],
        "decisions": ["Replantation globale", "Remplacement partiel", "Conservation"],
        "donnees": [["Exemple", "", ""]], "colonnes": ["Critère", "Statut", "Note"],
        "fiche_reference": "Ref-ARS1000", "description": "Description de section",
        "elements_requis": ["Indicateur 1", "Indicateur 2"], "etapes": ["Étape A", "Étape B"],
        "activite_label": "Détails Financiers", "champs": ["ID National", "Code Coopérative"],
        "lignes": ["Cacao", "Café", "Vivrier", "Autres"]
    }

    pages_map = {
        -1: dessiner_page_accueil,
        0:  dessiner_page_0_identification,
        1:  dessiner_page_1_Schema_Certification,
        2:  dessiner_page_2_Exigences_Suite,
        3:  dessiner_page_3_Exigences_Norme,
        4:  dessiner_page_4_Exigences_Fin,
        5:  dessiner_page_5_Etapes_Elaboration,
        6:  dessiner_page_6_Diagnostic_Initial,
        7:  dessiner_page_7_Definition_Objectifs,
        8:  dessiner_page_8_Socio_Demographiques,
        9:  dessiner_page_9_Description_exploitation,
        10: dessiner_page_10_Donnees_sur_les_cultures,
        11: dessiner_page_11_Materiel_Equipement,
        12: dessiner_page_12_Situation_Arbres_Forestiers,
        13: dessiner_page_13_Donnees_Agronomiques,
        14: dessiner_page_14_Determination_Densite,
        15: dessiner_page_15_Degradation_Arbres,
        16: dessiner_page_16_Etat_Cacaoyere_Strict,
        17: dessiner_page_17_Etat_Du_Sol_Strict,
        18: dessiner_page_18_post_recolte,
        19: dessiner_page_19_intrants,
        20: dessiner_page_20_socio_economique,
        21: dessiner_page_21_Finance_Production,
        22: dessiner_page_22_Depenses_Et_Main_Doeuvre,
        23: dessiner_page_23_Analyse_Des_Problemes,
        24: dessiner_page_24_Grille_Decision,
        25: dessiner_page_25_Analyse_Problemes,
        26: dessiner_page_26_Validation_Producteur,
        27: dessiner_page_27_Planification_Activites,
        28: dessiner_page_28_Planification_Des_Activites_Suite,
        29: dessiner_page_29_Calendrier_Activites,
        30: dessiner_page_30_Methodologie_Calendrier,
        31: dessiner_page_31_Programme_Annuel_Activites,
        32: dessiner_page_32_Determination_Moyens_Couts,
        33: dessiner_page_33_Moyens_Globaux_Couts,
        34: dessiner_page_34_Tableau_Moyens_Couts,
        35: dessiner_page_35_Orientations_Pratiques,
        36: dessiner_page_36_Mise_En_Oeuvre_Evaluation,
        37: dessiner_page_37_Cycle_Vie_PDC,
        38: dessiner_page_38_Structuration_PDC,
        39: dessiner_page_39_Identification_Producteur,
        40: dessiner_page_40_Situation_Epargne,
        41: dessiner_page_41_Situation_Main_Oeuvre,
        42: dessiner_page_42_Description_Exploitation,
        43: dessiner_page_43_Croquis_Polygone_Parcelle,
        44: dessiner_page_44_Cultures,
        45: dessiner_page_45_Situation_Arbres_Forestiers,
        46: dessiner_page_46_Verification_Materiel,
        47: dessiner_page_47_Planification_Strategique_Poupees_Russes,
        48: dessiner_page_48_Programme_Annuel_et_Facteurs,
        49: dessiner_page_49_Bilan_Global_Conformite_Decision,
    }

    dessiner_func = pages_map.get(n_page)
    if dessiner_func:
        dessiner_func()

    progression = max(0, min((n_page + 1) / 50, 1.0))
    st.sidebar.markdown("---")
    st.sidebar.write(f"Progression du PDC : {int(progression * 100)}%")
    st.sidebar.progress(progression)

def moteur_de_navigation(n_page_externe=None):
    pages_disponibles = {
        "Accueil": -1, "P0 - Identification": 0, "P1 - Schéma Certification": 1,
        "P2 - Exigences Suite": 2, "P3 - Exigences Norme": 3, "P4 - Titre Partie 2": 4,
        "P5 - Définition PDC": 5, "P6 - Caractéristiques": 6, "P7 - Introduction Collecte": 7,
        "P8 - Socio_Demographiques": 8, "P9 - Description Exploitation": 9, "P10 - Données Cultures": 10,
        "P11 - Materiel_Equipement": 11, "P12 - Situation_Arbres_Forestiers": 12, "P13 - Donnees_Agronomiques": 13,
        "P14 - Determination_Densite": 14, "P15 - Degradation_Arbres": 15, "P16 - Etat_Cacaoyere_Strict": 16,
        "P17 - Etat_Du_Sol_Strict": 17, "P18 - Post-Récolte": 18, "P19 - Intrants & Emballages": 19,
        "P20 - socio_economique": 20, "P21 - Finance Production": 21, "P22 - Charges Exploitation": 22,
        "P23 - Analyse Problèmes": 23, "P24 - Grille de Décision": 24, "P25 - Analyse Approfondie": 25,
        "P26 - Validation_Producteur": 26, "P27 - Planification_Activites": 27, "P28 - Planification_Activites_Suite": 28,
        "P29 - Calendrier_Activites": 29, "P30 - Méthode Calendrier": 30, "P31 - Programme Annuel": 31,
        "P32 - Détermination Moyens": 32, "P33 - Moyens_Globaux_Couts": 33, "P34 - Tableau Coûts Détails": 34,
        "P35 - Orientations_Pratiques": 35, "P36 - Mise_En_Oeuvre_Evaluation": 36, "P37 - Cycle_Vie_PDC": 37,
        "P38 - Structuration_PDC": 38, "P39 - Identification Producteur": 39, "P40 - Situation Épargne": 40,
        "P41 - Main d'Œuvre": 41, "P42 - Description_Exploitation": 42, "P43 - Croquis_Polygone_Parcelle": 43,
        "P44 - Inventaire Cultures": 44, "P45 - Situation_Arbres_Forestiers": 45, "P46 - Verification_Materiel": 46,
        "P47 - Planification 5 Ans": 47, "P48 - Programme Annuel (PDC)": 48, "P49 - Bilan_Global_Conformite_Decision": 49
    }

    st.sidebar.title("🌿 Navigation Layla")
    liste_noms = list(pages_disponibles.keys())
    liste_valeurs = list(pages_disponibles.values())
    index_actuel = liste_valeurs.index(st.session_state.page_actuelle) if st.session_state.page_actuelle in liste_valeurs else 0
    
    selection = st.sidebar.selectbox("Aller à la page :", liste_noms, index=index_actuel)
    n_page = pages_disponibles[selection]
    
    if n_page != st.session_state.page_actuelle:
        st.session_state.page_actuelle = n_page
        st.rerun()

# ==========================================================
# 6. CONFIGURATION VISUELLE & SIDEBAR
# ==========================================================
appliquer_style_layla()

with st.sidebar:
    try:
        st.image("logo_layla.png", width=150)
    except:
        st.header("LAYLA IA")
    
    st.write("📍 **ZONE : Soubré**")
    st.divider()
    
    page_mode = st.radio(
        "NAVIGATION",
        ["🏠 Accueil", "📄 GESTION PDC (ARS 1000)", "📊 STATISTIQUES", "⚙️ CONFIGURATION"]
    )
    st.info("Ingénieur Djè Akadjé")

# Appel du moteur de navigation unique pour synchroniser proprement la barre latérale
# On le place ICI pour que le selectbox ne vienne pas écraser les changements des boutons inférieurs
moteur_de_navigation(st.session_state.page_actuelle)

if page_mode == "📄 GESTION PDC (ARS 1000)":
    st.title("📄 Système de Gestion PDC (ARS 1000)")
    
    # Rendu du tableau et des données spécifiques à la page actuelle
    st.subheader(f"DOCUMENT ARS 1000 - PAGE {st.session_state.page_actuelle}")

    if f"table_p{st.session_state.page_actuelle}" not in st.session_state.donnees_pdc:
        df_init = pd.DataFrame([["", ""]], columns=["Description", "Valeur"])
        st.session_state.donnees_pdc[f"table_p{st.session_state.page_actuelle}"] = df_init

    edited_df = st.data_editor(
        st.session_state.donnees_pdc[f"table_p{st.session_state.page_actuelle}"],
        num_rows="dynamic",
        width="stretch",
        key=f"editor_p{st.session_state.page_actuelle}"
    )
    st.session_state.donnees_pdc[f"table_p{st.session_state.page_actuelle}"] = edited_df

    if st.button("💾 Synchroniser et Préparer PDF"):
        st.success("Données synchronisées. Prêt pour l'export.")
        parler("Données synchronisées. Je prépare le document officiel.")

# NOTE: Suppression du doublon "LAYLA MASTER" qui recréait un second number_input 
# dans la sidebar et provoquait des conflits de variables avec le reste.

# ==========================================================
# 8. EXÉCUTION DU CORPS DE PAGE (Placé avant la barre pour cohérence visuelle)
# ==========================================================
afficher_contenu()

# ==========================================================
# 7. BARRE DE NAVIGATION INFÉRIEURE (En bas de page)
# ==========================================================
st.divider()
col_prev, col_page, col_next = st.columns([1, 2, 1])

with col_prev:
    # Changement direct via le clic du bouton principal
    if st.button("⬅️ Précédent", width="stretch", disabled=(st.session_state.page_actuelle <= -1), key="nav_prev_main"): 
        st.session_state.page_actuelle -= 1
        st.rerun()

with col_page:
    st.markdown(f"<h3 style='text-align: center; color: #2E7D32;'>📄 PAGE {st.session_state.page_actuelle} / 49</h3>", unsafe_allow_html=True)

with col_next:
    if st.button("Suivant ➡️", width="stretch", key="btn_navigation_next", disabled=(st.session_state.page_actuelle >= 49)):
        st.session_state.page_actuelle += 1
        st.rerun()
