

def dessiner_page_17_Etat_Du_Sol_Strict():
    st.markdown("""
    <style>
    .stApp { background-color: #F4F6F6; }
    .main-title-p17 { color: #111625; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; margin-left: 20px; }
    .sub-title-p17 { color: #1F4E78; font-size: 18px; font-weight: bold; margin-left: 20px; margin-bottom: 15px; }
    .badge-p17 { background-color: #8E44AD; color: white; padding: 4px 10px; font-weight: bold; border-radius: 4px; display: inline-block; font-size: 14px; }
    
    /* Structure en poupées russes */
    .pouperee-p17-l1 { border-left: 5px solid #8E44AD; background-color: #FFFFFF; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p17-l2 { border-left: 5px solid #2980B9; background-color: #F7F9FA; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p17-l3 { border-left: 5px solid #D35400; background-color: #FFFBF2; padding: 15px; border-radius: 4px; }
    
    /* Cartes de diagnostic */
    .diagnostic-danger { background-color: #FADBD8; color: #78281F; padding: 10px; border-radius: 4px; border-left: 4px solid #C0392B; margin-bottom: 8px; }
    .diagnostic-alerte { background-color: #FCF3CF; color: #7E5109; padding: 10px; border-radius: 4px; border-left: 4px solid #F1C40F; margin-bottom: 8px; }
    .diagnostic-excellent { background-color: #D5F5E3; color: #145A32; padding: 10px; border-radius: 4px; border-left: 4px solid #27AE60; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p17">• Etat du sol</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title-p17">⮚ Caractéristiques physiques du sol (<span class="badge-p17">Fiche 3</span>)</div>', unsafe_allow_html=True)

    st.info("💡 **Orientation Toposéquence :**\n"
            "Indiquer le positionnement de la cacaoyère par rapport à la toposéquence (Plateau, haut de versant, mi-versant, bas de versant, bas-fond).")

    # =========================================================================
    # BANQUE DE DONNÉES DES CHOIX MULTIPLES POUR L'ÉTAT DU SOL (5-6 CHOIX)
    # =========================================================================
    bibliotheque_sol_layla = {
        "Couvert végétal": {
            "1. Beaucoup": [
                "Litière de feuilles très dense couvrant totalement le sol.",
                "Excellente protection du sol contre l'impact direct de la pluie.",
                "Paillage naturel épais favorisant la vie microbienne.",
                "Couverture végétale homogène retenant parfaitement l'humidité.",
                "Forte accumulation de débris organiques en surface."
            ],
            "2. Moyen": [
                "Sol partiellement visible sous une litière diffuse.",
                "Protection modérée du sol contre le lessivage.",
                "Couverture herbeuse ou de feuilles semi-homogène.",
                "Humidité du sol conservée de manière intermittente.",
                "Quelques zones nues alternent avec des zones couvertes.",
                "Niveau de décomposition de la litière correct."
            ],
            "3. Faible": [
                "Sol nu sur la majeure partie de la surface évaluée.",
                "Absence presque totale de litière protectrice.",
                "Risque d'érosion par impact des gouttes d'eau très élevé.",
                "Dessèchement rapide de la couche de surface sous le soleil.",
                "Dégradation avancée du couvert humifère.",
                "Sol exposé aux rayons directs sans litière isolante."
            ]
        },
        "Présence de Matière organique": {
            "1. Beaucoup": [
                "Horizon de surface de couleur noire ou brun foncé très net.",
                "Sol grumeleux, souple et riche en humus structuré.",
                "Abondance de débris végétaux bien décomposés en surface.",
                "Forte fertilité apparente visible à la structure du sol.",
                "Excellente rétention d'eau liée au taux d'humus."
            ],
            "2. Moyen": [
                "Teneur en humus correcte en surface.",
                "Coloration intermédiaire du sol témoignant d'un apport régulier.",
                "Structure du sol moyennement stable.",
                "Activité biologique moyenne (rares galeries de vers de terre).",
                "Apport organique à stimuler par la gestion des résidus.",
                "Présence superficielle de débris ligneux en cours de décomposition."
            ],
            "3. Faible": [
                "Sol de couleur claire (lessivé ou sableux en surface).",
                "Sol compact ou pulvérulent manquant totalement d'humus.",
                "Absence de signes d'activité biologique ou microbienne.",
                "Épuisement humifère marqué menaçant la nutrition des arbres.",
                "Structure instable sujette au compactage rapide.",
                "Taux de matière organique critique nécessitant des apports."
            ]
        },
        "Profondeur": {
            "1. Beaucoup": [
                "Sol profond sans obstacle rocheux visible sur plus d'un mètre.",
                "Excellent ancrage racinaire possible pour les pivots des arbres.",
                "Volume de sol explorable maximal pour l'alimentation en eau.",
                "Absence de dalle latéritique ou d'horizon induré.",
                "Profil de sol homogène et meuble en profondeur."
            ],
            "2. Moyen": [
                "Présence de gravillons ou d'obstacles modérés à mi-profondeur.",
                "Enracinement correct mais limité sous 60 cm.",
                "Sol de profondeur moyenne typique des flancs de collines.",
                "Ressource en eau du sol modérément disponible en saison sèche.",
                "Présence d'une couche gravillonnaire non cimentée.",
                "Pivot du cacaoyer pouvant contourner les obstacles."
            ],
            "3. Faible": [
                "Sol très superficiel, roche ou carapace latéritique proche de la surface.",
                "Horizon induré bloquant totalement le développement racinaire.",
                "Faible réserve en eau, risque de stress hydrique rapide.",
                "Arbres sensibles au déchaussement et au renversement.",
                "Couche arable de moins de 30 cm d'épaisseur.",
                "Risque d'asphyxie racinaire temporaire sur dalle imperméable."
            ]
        },
        "Texture": {
            "1. Beaucoup": [
                "Texture équilibrée de type limono-argileuse idéale.",
                "Sol malléable sans être collant, excellente porosité.",
                "Bon équilibre entre rétention d'eau et aération du système.",
                "Texture facilitant le travail racinaire et la nutrition.",
                "Sol doté d'une capacité d'échange cationique optimale."
            ],
            "2. Moyen": [
                "Texture à tendance sableuse ou argileuse lourde modérée.",
                "Sol légèrement lourd à travailler ou un peu filtrant.",
                "Proportions d'éléments fins et grossiers acceptables.",
                "Comportement physique correct face aux variations d'eau.",
                "Légère prédominance de limon provoquant une sensibilité à la battance.",
                "Porosité moyenne limitant légèrement la dynamique de l'eau."
            ],
            "3. Faible": [
                "Texture très dégradée, soit sable pur filtrant, soit argile compacte asfixiante.",
                "Sol excessivement sableux ne retenant aucun nutriment.",
                "Argile massive créant des fentes de retrait énormes en saison sèche.",
                "Contraintes physiques majeures pour la survie des radicelles.",
                "Texture squelettique dominée par les éléments grossiers.",
                "Asphyxie totale en cas de pluie ou dessèchement immédiat au soleil."
            ]
        },
        "Hydromorphie": {
            "1. Beaucoup": [
                "Engorgement permanent en eau, taches de rouille et gris bleuté dès la surface.",
                "Sol marécageux asfixiant le système racinaire du cacaoyer.",
                "Nappe phréatique affleurante bloquant toute aération du sol.",
                "Conditions anaérobies marquées provoquant la mort des radicelles.",
                "Stagnation d'eau prolongée impropre à la culture du cacao."
            ],
            "2. Moyen": [
                "Traces d'hydromorphie temporaire visibles en profondeur.",
                "Taches d'oxydoréduction (rouille) localisées sous 50 cm.",
                "Engorgement temporaire uniquement en forte saison des pluies.",
                "Ralentissement passager de l'activité racinaire sans mortalité.",
                "Drainage naturel lent nécessitant une surveillance.",
                "Zone de transition hydrique sur le bas de versant."
            ],
            "3. Faible": [
                "Sol parfaitement drainé, aucune tache de stagnation d'eau.",
                "Excellente circulation de l'eau et de l'air dans tout le profil.",
                "Absence totale de signes d'asphyxie racinaire.",
                "Profil sain maintenant une aération optimale toute l'année.",
                "Conditions idéales pour le développement des champignons mycorhiziens."
            ]
        },
        "Zones érodées": {
            "1. Oui": [
                "Ravinement marqué avec transport visible de terre arable.",
                "Présence de rigoles d'érosion dénudant les racines superficielles.",
                "Perte flagrante de la couche humifère entraînée par les eaux.",
                "Décapage de l'horizon de surface suite à une forte pente.",
                "Traces de sédimentation de boue en bas de versant.",
                "Dégradation physique active menaçant la stabilité des arbres."
            ],
            "2. Non": [
                "Aucun signe d'érosion ou de transport de matière.",
                "Surface stable, intégrité du sol préservée.",
                "Pas de rigoles ni de dénudation racinaire constatée.",
                "Topographie ou couverture empêchant le ruissellement destructeur.",
                "Horizon de surface parfaitement en place."
            ]
        },
        "Risque érosion": {
            "1. Oui": [
                "Forte pente combinée à une absence de couvert végétal au sol.",
                "Position en haut de versant sans barrière anti-érosive.",
                "Sol meuble très sensible au détachement par le ruissellement.",
                "Menace imminente de ravinement à la prochaine saison des pluies.",
                "Configuration topographique canalisant les flux d'eau de surface.",
                "Absence totale d'aménagements de rétention d'eau."
            ],
            "2. Non": [
                "Pente faible ou nulle mettant la parcelle à l'abri du ruissellement.",
                "Couvert végétal et enherbement ras fixant solidement le sol.",
                "Présence de dispositifs naturels de rétention (paillage, arbres de retenue).",
                "Caractéristiques physiques du sol limitant la susceptibilité à l'érosion.",
                "Risque nul ou négligeable dans les conditions actuelles."
            ]
        }
    }

    options_toposequence = ["Plateau", "Haut de versant", "Mi-versant", "Bas de versant", "Bas-fond"]
    valeurs_trois_niveaux = ["1. Beaucoup", "2. Moyen", "3. Faible"]
    valeurs_oui_non = ["1. Oui", "2. Non"]

    # =========================================================================
    # 🔐 PERSISTANCE ET INITIALISATION STRUCTURÉE DU SESSION STATE
    # =========================================================================
    cles_initialisation_p17 = {
        "p17_topos": "Mi-versant",
        "p17_v_cou": "2. Moyen", "p17_o_cou": bibliotheque_sol_layla["Couvert végétal"]["2. Moyen"][0],
        "p17_v_mor": "2. Moyen", "p17_o_mor": bibliotheque_sol_layla["Présence de Matière organique"]["2. Moyen"][0],
        "p17_v_pro": "1. Beaucoup", "p17_o_pro": bibliotheque_sol_layla["Profondeur"]["1. Beaucoup"][0],
        "p17_v_tex": "1. Beaucoup", "p17_o_tex": bibliotheque_sol_layla["Texture"]["1. Beaucoup"][0],
        "p17_v_hyd": "3. Faible", "p17_o_hyd": bibliotheque_sol_layla["Hydromorphie"]["3. Faible"][0],
        "p17_v_ero": "2. Non", "p17_o_ero": bibliotheque_sol_layla["Zones érodées"]["2. Non"][0],
        "p17_v_r_er": "2. Non", "p17_o_r_er": bibliotheque_sol_layla["Risque érosion"]["2. Non"][0],
    }

    for cle, defaut in cles_initialisation_p17.items():
        if cle not in st.session_state:
            st.session_state[cle] = defaut

    # Fonction assistante de synchronisation d'index
    def obtenir_index(liste, cle_state):
        valeur = st.session_state[cle_state]
        return liste.index(valeur) if valeur in liste else 0

    # Sélecteur de positionnement topographique synchro
    toposequence = st.selectbox(
        "Positionnement topographique de la cacaoyère",
        options_toposequence,
        index=obtenir_index(options_toposequence, "p17_topos"),
        key="p17_topos"
    )

    st.write("---")

    # =========================================================================
    # ENTRÉES DU TERRAIN : POUPÉE 1
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des observations physiques du sol", expanded=True):
        st.markdown('<div class="pouperee-p17-l1">', unsafe_allow_html=True)
        
        col_sol1, col_sol2 = st.columns(2)
        
        with col_sol1:
            st.markdown("##### 🧱 Profil & Propriétés du Sol")
            
            # Couvert Végétal
            c1, c2 = st.columns([1.2, 2.8])
            val_couvert = c1.selectbox("Couvert végétal", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_cou"), key="p17_v_cou")
            liste_obs_cou = bibliotheque_sol_layla["Couvert végétal"][val_couvert]
            obs_couvert = c2.selectbox("Observation Couvert (Choix Layla)", liste_obs_cou, index=obtenir_index(liste_obs_cou, "p17_o_cou"), key="p17_o_cou")
            
            # Matière Organique
            c1, c2 = st.columns([1.2, 2.8])
            val_morg = c1.selectbox("Matière organique", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_mor"), key="p17_v_mor")
            liste_obs_mor = bibliotheque_sol_layla["Présence de Matière organique"][val_morg]
            obs_morg = c2.selectbox("Observation M.O. (Choix Layla)", liste_obs_mor, index=obtenir_index(liste_obs_mor, "p17_o_mor"), key="p17_o_mor")
            
            # Profondeur
            c1, c2 = st.columns([1.2, 2.8])
            val_prof = c1.selectbox("Profondeur sol", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_pro"), key="p17_v_pro")
            liste_obs_pro = bibliotheque_sol_layla["Profondeur"][val_prof]
            obs_prof = c2.selectbox("Observation Profondeur (Choix Layla)", liste_obs_pro, index=obtenir_index(liste_obs_pro, "p17_o_pro"), key="p17_o_pro")
            
            # Texture
            c1, c2 = st.columns([1.2, 2.8])
            val_text = c1.selectbox("Texture", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_tex"), key="p17_v_tex")
            liste_obs_tex = bibliotheque_sol_layla["Texture"][val_text]
            obs_text = c2.selectbox("Observation Texture (Choix Layla)", liste_obs_tex, index=obtenir_index(liste_obs_tex, "p17_o_tex"), key="p17_o_tex")
            
            # Hydromorphie
            c1, c2 = st.columns([1.2, 2.8])
            val_hydro = c1.selectbox("Hydromorphie", valeurs_trois_niveaux, index=obtenir_index(valeurs_trois_niveaux, "p17_v_hyd"), key="p17_v_hyd")
            liste_obs_hyd = bibliotheque_sol_layla["Hydromorphie"][val_hydro]
            obs_hydro = c2.selectbox("Observation Hydromorphie (Choix Layla)", liste_obs_hyd, index=obtenir_index(liste_obs_hyd, "p17_o_hyd"), key="p17_o_hyd")

        with col_sol2:
            st.markdown("##### 🌊 Dynamique d'Érosion (Pente & Dégradations)")
            
            # Zones Érodées
            c1, c2 = st.columns([1.2, 2.8])
            val_erodee = c1.selectbox("Zones érodées ?", valeurs_oui_non, index=obtenir_index(valeurs_oui_non, "p17_v_ero"), key="p17_v_ero")
            liste_obs_ero = bibliotheque_sol_layla["Zones érodées"][val_erodee]
            obs_erodee = c2.selectbox("Observation Érosion Active (Choix Layla)", liste_obs_ero, index=obtenir_index(liste_obs_ero, "p17_o_ero"), key="p17_o_ero")
            
            # Risque d'Érosion
            c1, c2 = st.columns([1.2, 2.8])
            val_risq_ero = c1.selectbox("Risque d'érosion ?", valeurs_oui_non, index=obtenir_index(valeurs_oui_non, "p17_v_r_er"), key="p17_v_r_er")
            liste_obs_r_er = bibliotheque_sol_layla["Risque érosion"][val_risq_ero]
            obs_risq_ero = c2.selectbox("Observation Risque Érosion (Choix Layla)", liste_obs_r_er, index=obtenir_index(liste_obs_r_er, "p17_o_r_er"), key="p17_o_r_er")

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # LE TABLEAU DE SYNTHÈSE SYNOPTIQUE : POUPÉE 2
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel du Sol", expanded=True):
        st.markdown('<div class="pouperee-p17-l2">', unsafe_allow_html=True)
        
        data_tableau_p17 = {
            "Eléments d'observation (Gauche)": ["Couvert végétal", "Présence de Matière organique", "Profondeur", "Texture", "Hydromorphie"],
            "Valeur (G)": [val_couvert, val_morg, val_prof, val_text, val_hydro],
            "Observations (Gauche)": [obs_couvert, obs_morg, obs_prof, obs_text, obs_hydro],
            "Eléments d'observation (Droite)": ["Existence de zones érodées", "Existence de zones à risque d'érosion", "-", "-", "-"],
            "Valeur (D)": [val_erodee, val_risq_ero, "-", "-", "-"],
            "Observations (Droite)": [obs_erodee, obs_risq_ero, "-", "-", "-"]
        }
        
        df_p17 = pd.DataFrame(data_tableau_p17)
        st.dataframe(df_p17.set_index("Eléments d'observation (Gauche)"), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # LE MOTEUR D'ARBITRAGE DE LAYLA : POUPÉE 3
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Matrice d'Arbitrage Pédologique de Layla", expanded=True):
        st.markdown('<div class="pouperee-p17-l3">', unsafe_allow_html=True)
        st.markdown("#### 💬 Alertes Sol & Recommandations de l'Expert")
        
        alertes_sol = 0
        
        # Alerte Hydromorphie Critique (Bas-fond ou bas de versant)
        if "1. Beaucoup" in val_hydro or (toposequence == "Bas-fond" and "3. Faible" not in val_hydro):
            alertes_sol += 1
            st.markdown(f"""
            <div class="diagnostic-danger">
                🌊 <strong>ALERTE HYDROPHYSIQUE (Asphyxie Racinaire) :</strong> Sol à forte hydromorphie ou situé en {toposequence}.
                Le cacaoyer déteste avoir les pieds dans l'eau stagnante. Layla préconise de creuser d'urgence des canaux de drainage périphériques pour abaisser le niveau de la nappe temporaire.
            </div>
            """, unsafe_allow_html=True)
            
        # Alerte Érosion Active ou Risque Élevé (Haut de versant / Pente forte)
        if "1. Oui" in val_erodee or "1. Oui" in val_risq_ero or "3. Faible" in val_couvert:
            alertes_sol += 1
            st.markdown("""
            <div class="diagnostic-alerte">
                🍂 <strong>ALERTE DÉGRADATION DU SOL (Érosion / Lessivage) :</strong> Présence de zones érodées ou risque élevé lié à la faiblesse du couvert végétal.
                Layla recommande l'interdiction du désherbage total chimique, la mise en place immédiate d'un paillage résiduel autour des arbres et l'installation de bandes enherbées perpendiculaires à la pente.
            </div>
            """, unsafe_allow_html=True)

        # Alerte Perte de Fertilité (Carence Humique)
        if "3. Faible" in val_morg:
            alertes_sol += 1
            st.markdown("""
            <div class="diagnostic-alerte">
                🧱 <strong>ALERTE APPAUVRISSEMENT EN MATIÈRE ORGANIQUE :</strong> L'horizon humifère est insuffisant ou lavé.
                Risque de blocage de l'alimentation minérale. Valoriser l'ensemble des cabosses vides après écabossage et envisager un apport de compost ou d'engrais organique bien mûr sous la projection de la couronne.
            </div>
            """, unsafe_allow_html=True)

        if alertes_sol == 0:
            st.markdown(f"""
            <div class="diagnostic-excellent">
                🟢 <strong>DIAGNOSTIC DE LAYLA (Sol Sain & Stable) :</strong> La structure physique du sol est excellente en position de {toposequence}. 
                Le couvert végétal et le taux de matière organique protègent efficacement la parcelle. Le potentiel agro-pédologique est optimal pour soutenir la productivité des cacaoyers.
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p17", type="primary", use_container_width=True):
        st.session_state["page_17_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 18
        st.rerun()

    # Numérotation réglementaire en bas à droite
    st.write("---")
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>17</span>", unsafe_allow_html=True)



def dessiner_page_18_post_recolte():
    # --- CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-18 {
        background-color: #C6E0B4; /* Vert institutionnel standardisé */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-18 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .diagnostic-container {
        background-color: #FFFFFF;
        padding: 22px;
        border-radius: 8px;
        margin-top: 25px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #16A085;
    }
    .diag-title {
        color: #16A085;
        font-size: 17px;
        font-weight: bold;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-good { color: #27AE60; font-weight: bold; margin-bottom: 10px; list-style-position: inside; }
    .status-warning { color: #F39C12; font-weight: bold; margin-bottom: 10px; list-style-position: inside; }
    .status-danger { color: #C0392B; font-weight: bold; margin-bottom: 10px; list-style-position: inside; }
    
    .table-header { font-weight: bold; padding: 10px; background-color: #16A085; color: white; border-radius: 4px; text-align: left; font-size: 14px;}
    .cell-text { padding-top: 12px; font-size: 14px; color: #2C3E50; font-weight: 500;}
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION ---
    st.markdown("""
    <div class="diapo-slide-18">
        <div class="bullet-titre-18">• Pratiques de récolte et post-récolte</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # Banque d'options de terrain
    options_fermentation = ["1. Bâche en plastique", "2. En caisses de bois", "3. En tas sous bananiers"]
    options_sechage = ["1. Sur goudron", "2. Sur claies surélevées", "3. Sur bâche propre", "4. Sur aire cimentée"]
    options_brassage = ["1. Brassage régulier", "2. Brassage insuffisant", "3. Aucun brassage"]
    options_tri = ["1. Tri manuel à plat", "2. Tamisage / Calibrage mécanique", "3. Aucun tri"]
    options_stockage = ["1. Sacs en toile de jute sur palettes", "2. Sacs en plastique (Sisal/Synthétique)", "3. Stockage direct au sol / en vrac"]

    # =========================================================================
    # 🔐 PERSISTANCE DU SESSION STATE SÉCURISÉE
    # =========================================================================
    cles_initialisation_p18 = {
        "p18_freq_rec": "14",
        "p18_t_ecab": "2",
        "p18_t_ferm": "6",
        "p18_qualite_f": "",
        "p18_obs_comp": "",
        "p18_mode_ferm": options_fermentation[0],
        "p18_methode_sech": options_sechage[0],
        "p18_brassage": options_brassage[0],
        "p18_tri_calib": options_tri[0],
        "p18_stockage": options_stockage[0]
    }

    for cle, defaut in cles_initialisation_p18.items():
        if cle not in st.session_state:
            st.session_state[cle] = defaut

    def obtenir_index(liste, cle_state):
        valeur = st.session_state[cle_state]
        return liste.index(valeur) if valeur in liste else 0

    # --- EN-TÊTES DU TABLEAU MATRICIEL ---
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="table-header">Éléments d\'observation (Mesures)</div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="table-header">Réponses</div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="table-header">Éléments d\'observation (Méthodes)</div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="table-header">Réponses indépendantes</div>', unsafe_allow_html=True)

    st.write("") 

    # Ligne 1
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Fréquence des récoltes (Espacement en jours)</div>', unsafe_allow_html=True)
    with c2: freq_rec_in = st.text_input("R1", value=st.session_state.p18_freq_rec, label_visibility="collapsed", key="p18_freq_rec_input")
    with c3: st.markdown('<div class="cell-text">Mode de fermentation</div>', unsafe_allow_html=True)
    with c4: mode_ferm_in = st.selectbox("D1", options=options_fermentation, index=obtenir_index(options_fermentation, "p18_mode_ferm"), label_visibility="collapsed", key="p18_mode_ferm_select")

    # Ligne 2
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Temps entre récolte et écabossage (jours)</div>', unsafe_allow_html=True)
    with c2: t_ecab_in = st.text_input("R2", value=st.session_state.p18_t_ecab, label_visibility="collapsed", key="p18_t_ecab_input")
    with c3: st.markdown('<div class="cell-text">Méthodes de Séchage</div>', unsafe_allow_html=True)
    with c4: methode_sech_in = st.selectbox("D2", options=options_sechage, index=obtenir_index(options_sechage, "p18_methode_sech"), label_visibility="collapsed", key="p18_methode_sech_select")

    # Ligne 3
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Durée de la fermentation (jours)</div>', unsafe_allow_html=True)
    with c2: t_ferm_in = st.text_input("R3", value=st.session_state.p18_t_ferm, label_visibility="collapsed", key="p18_t_ferm_input")
    with c3: st.markdown('<div class="cell-text">Technique de Brassage / Retournement</div>', unsafe_allow_html=True)
    with c4: brassage_in = st.selectbox("D3", options=options_brassage, index=obtenir_index(options_brassage, "p18_brassage"), label_visibility="collapsed", key="p18_brassage_select")

    # Ligne 4
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Qualité globale des fèves</div>', unsafe_allow_html=True)
    with c2: qualite_f_in = st.text_input("R4", value=st.session_state.p18_qualite_f, label_visibility="collapsed", key="p18_qualite_f_input")
    with c3: st.markdown('<div class="cell-text">Tri et Calibrage (Post-Séchage)</div>', unsafe_allow_html=True)
    with c4: tri_calib_in = st.selectbox("D4", options=options_tri, index=obtenir_index(options_tri, "p18_tri_calib"), label_visibility="collapsed", key="p18_tri_calib_select")

    # Ligne 5
    c1, c2, c3, c4 = st.columns([2.5, 1.2, 2.5, 1.8])
    with c1: st.markdown('<div class="cell-text">Observations complémentaires</div>', unsafe_allow_html=True)
    with c2: obs_comp_in = st.text_input("R5", value=st.session_state.p18_obs_comp, label_visibility="collapsed", key="p18_obs_comp_input")
    with c3: st.markdown('<div class="cell-text">Stockage / Entreposage des fèves</div>', unsafe_allow_html=True)
    with c4: stockage_in = st.selectbox("D5", options=options_stockage, index=obtenir_index(options_stockage, "p18_stockage"), label_visibility="collapsed", key="p18_stockage_select")

    # Synchronisation inverse des données saisies vers l'état
    st.session_state.p18_freq_rec = freq_rec_in
    st.session_state.p18_mode_ferm = mode_ferm_in
    st.session_state.p18_t_ecab = t_ecab_in
    st.session_state.p18_methode_sech = methode_sech_in
    st.session_state.p18_t_ferm = t_ferm_in
    st.session_state.p18_brassage = brassage_in
    st.session_state.p18_qualite_f = qualite_f_in
    st.session_state.p18_tri_calib = tri_calib_in
    st.session_state.p18_obs_comp = obs_comp_in
    st.session_state.p18_stockage = stockage_in

    # =========================================================================
    # 🧠 EXÉCUTION DIRECTE DU SYSTÈME EXPERT LEILA IA
    # =========================================================================
    try:
        freq_rec = float(freq_rec_in) if freq_rec_in else None
        t_ecab = float(t_ecab_in) if t_ecab_in else None
        t_ferm = float(t_ferm_in) if t_ferm_in else None
        
        notes_diagnostic = []
        
        # --- Analyses Chiffrées ---
        if freq_rec is not None:
            if freq_rec > 21: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Fréquence de récolte trop longue ({int(freq_rec)} jours) :</b> Risque élevé de pourriture des cabosses sur l'arbre et d'attaques de bioagresseurs.</li>")
            elif freq_rec < 10: notes_diagnostic.append(f"<li class='status-warning'>⚠️ <b>Fréquence rapprochée ({int(freq_rec)} jours) :</b> Assurez-vous que le taux de maturité des cabosses justifie économiquement le coût de la main-d'œuvre.</li>")
            else: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Fréquence de récolte optimale ({int(freq_rec)} jours) :</b> Parfait pour cueillir le cacao à maturité complète.</li>")

        if t_ecab is not None:
            if t_ecab > 5: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Écabossage très tardif ({int(t_ecab)} jours) :</b> Risque majeur de germination interne des fèves et de développement de moisissures.</li>")
            elif 3 <= t_ecab <= 5: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Pré-stockage des cabosses ({int(t_ecab)} jours) :</b> Pratique agronomique idéale pour abaisser l'acidité naturelle et améliorer le goût.</li>")
            else: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Écabossage rapide ({int(t_ecab)} jours) :</b> Pratique standard correcte préservant l'intégrité de la pulpe.</li>")

        if t_ferm is not None:
            if t_ferm < 5: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Fermentation insuffisante ({int(t_ferm)} jours) :</b> Risque d'un taux élevé de fèves violettes amères et astringentes. Lot non marchand !</li>")
            elif t_ferm > 7: notes_diagnostic.append(f"<li class='status-danger'>🚨 <b>Fermentation trop longue ({int(t_ferm)} jours) :</b> Risque de sur-fermentation avec apparition d'odeurs ammoniacales et putrides.</li>")
            else: notes_diagnostic.append(f"<li class='status-good'>🟢 <b>Durée de fermentation parfaite ({int(t_ferm)} jours) :</b> Transformation biochimique et synthèse aromatique optimales.</li>")

        # --- Analyses des Méthodes Établies ---
        if "bâche" in mode_ferm_in.lower():
            notes_diagnostic.append("<li class='status-warning'>⚠️ <b>Mode fermentation (Bâche plastique) :</b> Forte rétention des jus acides. Leila conseille plutôt l'usage de caisses en bois ou de tas sous bananiers bien drainés.</li>")
        elif "caisses" in mode_ferm_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Fermentation en caisses de bois :</b> Excellente maîtrise thermique et drainage idéal de la sueur du cacao.</li>")
        elif "tas" in mode_ferm_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Fermentation en tas sous bananiers :</b> Méthode traditionnelle efficace assurant une bonne inoculation microbiologique naturelle.</li>")

        if "goudron" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Séchage sur goudron / asphalte : CRITIQUE & INTERDIT !</b> Contamination par les Hydrocarbures Aromatiques Polycycliques (HAP) causée par le bitume chaud. Risque de rejet du lot.</li>")
        elif "sol" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-danger'>❌ <b>Séchage à même le sol : DÉCONSEILLÉ.</b> Exposition directe aux souillures du sol, humidité résiduelle de la terre et développement fongique immédiat.</li>")
        elif "bâche" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-warning'>⚠️ <b>Séchage sur bâche propre : VIGILANCE REQUISE.</b> Isole du sol, mais l'absence de drainage inférieur exige un brassage fréquent pour évacuer l'eau.</li>")
        elif "aire" in methode_sech_in.lower() or "ciment" in methode_sech_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Séchage sur aire cimentée : ACCEPTE.</b> Méthode saine si la dalle est isolée et balayée régulièrement. Nécessite des retournements précis.</li>")
        else:
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Séchage sur claies surélevées : DISPOSITIF OPTIMAL (PREMIUM).</b> Ventilation bi-directionnelle accélérant le séchage sans risque sanitaire.</li>")

        if "régulier" in brassage_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Brassage régulier :</b> Température et évaporation parfaitement homogènes sur l'ensemble du lot.</li>")
        elif "insuffisant" in brassage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Brassage insuffisant :</b> Entraîne des écarts de séchage (fèves sèches en surface, humides au cœur).</li>")
        elif "aucun" in brassage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Aucun brassage :</b> Risque critique d'agglomération des fèves en paquets et moisissures internes.</li>")

        if "manuel" in tri_calib_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Tri manuel à plat :</b> Élimination précise des débris physiques, des fèves plates, cassées ou fusionnées.</li>")
        elif "mécanique" in tri_calib_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Tamisage mécanique :</b> Garantit un grainage uniforme respectant parfaitement les standards commerciaux internationaux.</li>")
        elif "aucun" in tri_calib_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Absence complète de tri :</b> Présence d'impuretés. Risque élevé de décote ou de refus direct par la coopérative.</li>")

        if "palettes" in stockage_in.lower():
            notes_diagnostic.append("<li class='status-good'>🟢 <b>Stockage réglementaire conforme :</b> Les sacs de jute sur palettes en bois isolent de l'humidité et permettent au cacao de respirer.</li>")
        elif "plastique" in stockage_in.lower() or "sisal" in stockage_in.lower() or "synthétique" in stockage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Stockage non conforme (Sacs Plastiques) :</b> Confinement de l'humidité résiduelle, altération des graisses et risque de sécrétions d'Ochratoxine A.</li>")
        elif "sol" in stockage_in.lower() or "vrac" in stockage_in.lower():
            notes_diagnostic.append("<li class='status-danger'>🚨 <b>Stockage en vrac au sol : FORMELLEMENT INTERDIT !</b> Reprise immédiate d'humidité par capillarité et prolifération de rongeurs ou insectes.</li>")

        if notes_diagnostic:
            st.markdown(f"""
            <div class="diagnostic-container">
                <div class="diag-title">🧠 Analyse de Qualité Post-Récolte (Leila IA)</div>
                <ul style="padding-left: 5px; margin: 0;">
                    {"".join(notes_diagnostic)}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    except Exception:
        st.info("Veuillez réajuster les saisies numériques pour mettre à jour l'audit automatisé de Leila.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p18", type="primary", use_container_width=True):
        st.session_state["page_18_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 19
        st.rerun()

    # --- PIED DE PAGE STANDARDISÉ ---
    st.write("---")
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>18</span>", unsafe_allow_html=True)


def dessiner_page_19_intrants():
    # --- CONFIGURATION DU DESIGN ET STRUCTURE DE POUPÉES RUSSES ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-19 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-19 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .section-title { color: #16A085; font-size: 18px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    .cell-label { font-size: 14px; color: #34495E; font-weight: bold; padding-top: 5px; }
    
    /* Structure Box Poupées Russes */
    .pouperee-p19-l1 { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p19-l2 { border-left: 5px solid #2980B9; background-color: #F4F8FA; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p19-l3 { border-left: 5px solid #D35400; background-color: #FFFBF5; padding: 20px; border-radius: 6px; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #16A085; margin-top: 15px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION ---
    st.markdown("""
    <div class="diapo-slide-19">
        <div class="bullet-titre-19">• Suivi des Intrants et Gestion Hygiénique</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    options_engrais_t = ["Aucun", "Minéral (NPK / Boron)", "Organique (Compost/Fiente)", "Bio-stimulant"]
    options_engrais_m = ["Au sol (Couronne)", "Foliaire (Pulvérisation)", "Épandage à la volée"]
    options_applicateur = ["1. Producteur", "2. Applicateur"]
    
    options_phyto_t = ["Aucun", "Insecticide (Anti-mirides)", "Fongicide (Pourriture brune)", "Herbicide"]
    options_phyto_m = ["Atomiseur", "Pulvérisateur"]
    
    options_emballage = [
        "Sélectionner une réponse...",
        "Brûlés au champ ou jetés dans la cacaoyère / près des cours d'eau",
        "Enfouis dans le sol de la parcelle",
        "Rincés 3 fois, percés et stockés dans un bac de récupération sécurisé (Coopérative)",
        "Laissés à l'abandon sur place"
    ]

    # =========================================================================
    # 🔐 PERSISTANCE ET SÉCURISATION DES CLES SESSIONS MULTI-LIGNES
    # =========================================================================
    for i in range(1, 4):
        if f"p19_eng_t{i}" not in st.session_state: st.session_state[f"p19_eng_t{i}"] = options_engrais_t[0]
        if f"p19_eng_n{i}" not in st.session_state: st.session_state[f"p19_eng_n{i}"] = ""
        if f"p19_eng_q{i}" not in st.session_state: st.session_state[f"p19_eng_q{i}"] = ""
        if f"p19_eng_p{i}" not in st.session_state: st.session_state[f"p19_eng_p{i}"] = ""
        if f"p19_eng_m{i}" not in st.session_state: st.session_state[f"p19_eng_m{i}"] = options_engrais_m[0]
        if f"p19_eng_a{i}" not in st.session_state: st.session_state[f"p19_eng_a{i}"] = options_applicateur[0]
        
        if f"p19_phy_t{i}" not in st.session_state: st.session_state[f"p19_phy_t{i}"] = options_phyto_t[0]
        if f"p19_phy_n{i}" not in st.session_state: st.session_state[f"p19_phy_n{i}"] = ""
        if f"p19_phy_q{i}" not in st.session_state: st.session_state[f"p19_phy_q{i}"] = ""
        if f"p19_phy_p{i}" not in st.session_state: st.session_state[f"p19_phy_p{i}"] = ""
        if f"p19_phy_m{i}" not in st.session_state: st.session_state[f"p19_phy_m{i}"] = options_phyto_m[0]
        if f"p19_phy_a{i}" not in st.session_state: st.session_state[f"p19_phy_a{i}"] = options_applicateur[0]

    if "p19_emb_val" not in st.session_state:
        st.session_state.p19_emb_val = options_emballage[0]

    def idx_opt(liste, cle_state):
        val = st.session_state[cle_state]
        return liste.index(val) if val in liste else 0

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des données sur les intrants et emballages", expanded=True):
        st.markdown('<div class="pouperee-p19-l1">', unsafe_allow_html=True)
        
        # --- ENGRAIS ---
        st.markdown('<div class="section-title">❖ Application des engrais</div>', unsafe_allow_html=True)
        saisies_engrais = []
        for i in range(1, 4):
            st.markdown(f"**Ligne Engrais N°{i}**")
            c_e1, c_e2, c_e3, c_e4, c_e5, c_e6 = st.columns([2.0, 1.8, 1.0, 1.2, 1.8, 1.5])
            
            with c_e1: type_engrais = st.selectbox("Type d'engrais", options=options_engrais_t, index=idx_opt(options_engrais_t, f"p19_eng_t{i}"), key=f"p19_eng_t{i}_select")
            with c_e2: nom_engrais = st.text_input("Nom commercial / formule", value=st.session_state[f"p19_eng_n{i}"], key=f"p19_eng_n{i}_input")
            with c_e3: qte_engrais_str = st.text_input("Quantité/an (kg)", value=st.session_state[f"p19_eng_q{i}"], key=f"p19_eng_q{i}_input")
            with c_e4: per_engrais = st.text_input("Période d'apport", value=st.session_state[f"p19_eng_p{i}"], key=f"p19_eng_p{i}_input")
            with c_e5: mode_engrais = st.selectbox("Mode d'apport", options=options_engrais_m, index=idx_opt(options_engrais_m, f"p19_eng_m{i}"), key=f"p19_eng_m{i}_select")
            with c_e6: app_engrais = st.selectbox("Applicateur", options=options_applicateur, index=idx_opt(options_applicateur, f"p19_eng_a{i}"), key=f"p19_eng_a{i}_select")
            
            # Sauvegarde dynamique dans le session_state global
            st.session_state[f"p19_eng_t{i}"] = type_engrais
            st.session_state[f"p19_eng_n{i}"] = nom_engrais
            st.session_state[f"p19_eng_q{i}"] = qte_engrais_str
            st.session_state[f"p19_eng_p{i}"] = per_engrais
            st.session_state[f"p19_eng_m{i}"] = mode_engrais
            st.session_state[f"p19_eng_a{i}"] = app_engrais

            try:
                qte_engrais = float(qte_engrais_str) if qte_engrais_str.strip() != "" else 0.0
            except ValueError:
                qte_engrais = 0.0
                
            saisies_engrais.append({
                "Type d'engrais": type_engrais, "Nom commercial / formule": nom_engrais, "Quantité/an": qte_engrais,
                "Période d'apport": per_engrais, "Mode d'apport (foliaire, au sol)": mode_engrais, "Applicateur": app_engrais
            })

        st.write("---")

        # --- PHYTOSANITAIRES ---
        st.markdown('<div class="section-title">❖ Application de produits phytosanitaires</div>', unsafe_allow_html=True)
        saisies_phy = []
        for i in range(1, 4):
            st.markdown(f"**Ligne Produit Phyto N°{i}**")
            c_p1, c_p2, c_p3, c_p4, c_p5, c_p6 = st.columns([2.0, 1.8, 1.0, 1.2, 1.8, 1.5])
            
            with c_p1: type_phy = st.selectbox("Type de produits", options=options_phyto_t, index=idx_opt(options_phyto_t, f"p19_phy_t{i}"), key=f"p19_phy_t{i}_select")
            with c_p2: nom_phy = st.text_input("Nom commercial / formule", value=st.session_state[f"p19_phy_n{i}"], key=f"p19_phy_n{i}_input")
            with c_p3: qte_phy_str = st.text_input("Quantité / trait.", value=st.session_state[f"p19_phy_q{i}"], key=f"p19_phy_q{i}_input")
            with c_p4: per_phy = st.text_input("Période de traitement", value=st.session_state[f"p19_phy_p{i}"], key=f"p19_phy_p{i}_input")
            with c_p5: mode_phy = st.selectbox("Mode d'appareil", options=options_phyto_m, index=idx_opt(options_phyto_m, f"p19_phy_m{i}"), key=f"p19_phy_m{i}_select")
            with c_p6: app_phy = st.selectbox("Applicateur", options=options_applicateur, index=idx_opt(options_applicateur, f"p19_phy_a{i}"), key=f"p19_phy_a{i}_select")
            
            # Sauvegarde dynamique dans le session_state global
            st.session_state[f"p19_phy_t{i}"] = type_phy
            st.session_state[f"p19_phy_n{i}"] = nom_phy
            st.session_state[f"p19_phy_q{i}"] = qte_phy_str
            st.session_state[f"p19_phy_p{i}"] = per_phy
            st.session_state[f"p19_phy_m{i}"] = mode_phy
            st.session_state[f"p19_phy_a{i}"] = app_phy

            try:
                qte_phy = float(qte_phy_str) if qte_phy_str.strip() != "" else 0.0
            except ValueError:
                qte_phy = 0.0
                
            saisies_phy.append({
                "Type de produits (insecticide, fongicide, herbicide)": type_phy, "Nom commercial / formule": nom_phy, "Quantité / traitement": qte_phy,
                "Période de traitement": per_phy, "Mode d'apport (atomiseur, pulvérisateur)": mode_phy, "Applicateur": app_phy
            })

        st.write("---")

        # --- GESTION DES EMBALLAGES ---
        st.markdown('<div class="section-title">❖ Gestion des emballages</div>', unsafe_allow_html=True)
        c_emb1, c_emb2 = st.columns([3.0, 5.0])
        with c_emb1:
            st.markdown('<div class="cell-label">Que faites-vous des emballages après traitement/application ?</div>', unsafe_allow_html=True)
        with c_emb2:
            reponse_emballage = st.selectbox("Sélectionner une réponse...", options=options_emballage, index=idx_opt(options_emballage, "p19_emb_val"), label_visibility="collapsed", key="p19_emb_val_select")
            st.session_state.p19_emb_val = reponse_emballage

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : MATRICE SYNOPTIQUE / SORTIE DES TABLEAUX (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visuel Tableaux)", expanded=True):
        st.markdown('<div class="pouperee-p19-l2">', unsafe_allow_html=True)
        
        st.markdown("##### 🌿 Matrice de Suivi de l'Application des Engrais")
        df_engrais = pd.DataFrame(saisies_engrais)
        st.dataframe(df_engrais, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 🛡️ Matrice de Suivi des Produits Phytosanitaires")
        df_phyto = pd.DataFrame(saisies_phy)
        st.dataframe(df_phyto, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### ♻️ État de la Gestion Intégrée des Emballages")
        df_emb = pd.DataFrame({
            "Question réglementaire": ["Que faites-vous des emballages après traitement/application ?"],
            "Réponse Encodée": [reponse_emballage]
        })
        st.dataframe(df_emb, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA IA EXPERT / AVIS (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Rapport d'Analyse et Avis Experts de Leila", expanded=True):
        st.markdown('<div class="pouperee-p19-l3">', unsafe_allow_html=True)
        
        # --- NUTRITION DES SOLS ---
        st.markdown('<div class="subsection-analysis-title">🌿 Analyse Expert de la Nutrition</div>', unsafe_allow_html=True)
        compteur_engrais = 0
        for idx, row in enumerate(saisies_engrais):
            type_engrais = row["Type d'engrais"]
            quantite = row["Quantité/an"]
            periode = row["Période d'apport"]
            mode = row["Mode d'apport (foliaire, au sol)"]
            nom_comm = row["Nom commercial / formule"] if row["Nom commercial / formule"] != "" else "Non spécifié"
            
            if type_engrais != "Aucun":
                compteur_engrais += 1
                if "Minéral" in type_engrais:
                    if quantite > 250:
                        st.error(f"❌ **Ligne {idx+1} - [{nom_comm}] ({quantite} kg) :** Surdosage détecté ! Risque de toxicité racinaire accrue et de lixiviation. Leila recommande de recalibrer les doses entre 150 et 200 kg/ha.")
                    elif quantite > 0:
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_comm}] ({quantite} kg) :** Dose agronomique globale bien calibrée.")
                    else:
                        st.warning(f"⚠️ **Ligne {idx+1} - [{nom_comm}] :** Veuillez renseigner une quantité valide pour évaluer l'apport.")
                    
                    if any(m in periode.lower() for m in ["mai", "juin", "avril"]):
                        st.success(f" └─ 🟢 **Période ({periode}) :** Timing idéal. Correspond à la grande saison des pluies en Côte d'Ivoire, favorisant la solubilisation.")
                    elif periode != "":
                        st.warning(f" └─ ⚠️ **Période ({periode}) :** Risque de faible assimilation. L'engrais minéral requiert une humidité constante du sol.")
                    
                    if "couronne" in mode.lower() or "sol" in mode.lower():
                        st.success(f" └─ 🟢 **Mode d'apport ({mode}) :** Localisation validée. Engrais directement orienté vers le système racinaire absorbant.")
                    elif "volée" in mode.lower():
                        st.warning(f" └─ ⚠️ **Mode d'apport ({mode}) :** L'épandage à la volée favorise la volatilisation de l'azote et accélère la pousse des adventices.")
                        
                elif "Organique" in type_engrais:
                    st.success(f"🟢 **Ligne {idx+1} - [{nom_comm}] ({quantite} kg) :** Excellent choix technique pour restructurer durablement l'humus et stimuler la vie biologique du sol.")
                elif "Bio-stimulant" in type_engrais:
                    if "foliaire" in mode.lower():
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_comm}] :** Application foliaire validée pour limiter l'impact des stress hydriques.")
                    else:
                        st.error(f"❌ **Ligne {idx+1} - [{nom_comm}] :** L'apport au sol est inefficace pour ce type de bio-stimulant. Leila préconise une pulvérisation foliaire directe.")
        if compteur_engrais == 0:
            st.info("💡 Aucun apport de fertilisant enregistré pour le moment.")

        # --- PROTECTION DES CULTURES ---
        st.markdown('<div class="subsection-analysis-title">🛡️ Analyse Expert de la Protection des Cultures</div>', unsafe_allow_html=True)
        compteur_phyto = 0
        for idx, row in enumerate(saisies_phy):
            type_phyto = row["Type de produits (insecticide, fongicide, herbicide)"]
            nom_commercial = row["Nom commercial / formule"] if row["Nom commercial / formule"] != "" else "Non spécifié"
            mode_appareil = row["Mode d'apport (atomiseur, pulvérisateur)"]
            
            if type_phyto != "Aucun":
                compteur_phyto += 1
                if "Insecticide" in type_phyto:
                    if "atomiseur" in mode_appareil.lower():
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_commercial}] :** Matériel de traitement validé. L'atomiseur est obligatoire pour saturer la canopée et détruire efficacement les mirides (capsides).")
                    else:
                        st.error(f"❌ **Ligne {idx+1} - [{nom_commercial}] :** Pulvérisateur manuel inadapté en hauteur. La canopée ne sera pas protégée contre les attaques de ravageurs.")
                elif "Fongicide" in type_phyto:
                    if "atomiseur" in mode_appareil.lower():
                        st.warning(f"⚠️ **Ligne {idx+1} - [{nom_commercial}] :** Risque de perte par dérive aérienne. Privilégiez le pulvérisateur manuel pour bien cibler les troncs et les cabosses (Lutte contre la Pourriture brune).")
                    else:
                        st.success(f"🟢 **Ligne {idx+1} - [{nom_commercial}] :** Application ciblée au pulvérisateur manuel validée.")
                elif "Herbicide" in type_phyto:
                    st.error(f"🚨 **Ligne {idx+1} - [{nom_commercial}] : Pratique critique fortement déconseillée !** Détruit la microfaune utile et expose les sols à l'érosion. Privilégiez un nettoyage mécanique raisonné à la machette.")
        if compteur_phyto == 0:
            st.info("💡 Aucun produit phytosanitaire appliqué sur la parcelle.")

        # --- CRITÈRES DE CERTIFICATION ET ENVIRONNEMENT ---
        st.markdown('<div class="subsection-analysis-title">♻️ Analyse Environnementale & Normes de Durabilité</div>', unsafe_allow_html=True)
        if "Sélectionner" in reponse_emballage or reponse_emballage == "":
            st.info("💡 En attente de déclaration sur la gestion des emballages vides.")
        elif "Brûlés" in reponse_emballage or "Laissés" in reponse_emballage:
            st.error(f"🚨 **Point de blocage éliminatoire :** Brûler ou abandonner les emballages pollue gravement l'écosystème et viole directement les exigences des normes durables (ex: Rainforest Alliance).")
        elif "Enfouis" in reponse_emballage:
            st.error(f"🚨 **Non-conformité environnementale majeure :** L'enfouissement accumule les résidus chimiques et les molécules toxiques dans le sous-sol et les nappes phréatiques.")
        elif "Rincés" in reponse_emballage:
            st.success("🟢 **Conformité Parfaite :** Le protocole de triple rinçage, perçage pour destruction et stockage centralisé en coopérative répond parfaitement aux exigences de durabilité.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p19", type="primary", use_container_width=True):
        st.session_state["page_19_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 20
        st.rerun()

    # --- PIED DE PAGE STANDARDISÉ ---
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>19</span>", unsafe_allow_html=True)

def dessiner_page_20_socio_economique():
    # --- CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-20 {
        background-color: #C6E0B4; /* Vert institutionnel standardisé */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 25px;
    }
    .bullet-titre-20 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .blue-fiche { color: #2980B9; font-weight: bold; }
    
    .bullet-list-p20 { font-size: 16px; color: #2C3E50; line-height: 1.8; margin-left: 10px; margin-top: 15px;}
    .bullet-item-p20 { margin-bottom: 12px; list-style-position: inside; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-20">
        <div class="bullet-titre-20">D - Données Socio-économiques <span class="blue-fiche">(Fiche 4)</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # Liste des puces textuellement conformes
    st.markdown("""
    <ul class="bullet-list-p20">
        <li class="bullet-item-p20">Caractérisation de l'unité familiale de production (rôle de chaque membre),</li>
        <li class="bullet-item-p20">Le revenu tiré du cacao et des autres activités,</li>
        <li class="bullet-item-p20">Les dépenses courantes du ménage,</li>
        <li class="bullet-item-p20">Les relations avec les partenaires financiers et commerciaux,</li>
        <li class="bullet-item-p20">Le coût de la main-d'œuvre (ressources financières et humaines pour faire face au nouvel investissement que nécessite la mise en œuvre du PDC).</li>
    </ul>
    """, unsafe_allow_html=True)

    # Espacement pour pousser le numéro de page vers le bas
    st.write("<br><br><br><br><br><br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p20", type="primary", use_container_width=True):
        st.session_state["page_20_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 21
        st.rerun()

    # --- PIED DE PAGE ET NUMÉRO DE PAGE HARMONISÉ ---
    st.write("---")
    col_space, col_num = st.columns([0.95, 0.05])
    with col_num:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>20</span>", unsafe_allow_html=True)
