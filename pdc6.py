
def afficher():
    st.subheader("Module PDC 6")
def dessiner_page_25_Analyse_Problemes():
    # --- 1. STYLES CSS PERSONNALISÉS ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .main-title-p25 { color: #1A252F; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 5px; }
    .badge-p25 { background-color: #C0392B; color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 13px; }
    
    /* Structure en poupées russes avec bordures de sécurité */
    .pouperee-p25-l1 { border-left: 5px solid #2C3E50; background-color: #FFFFFF; padding: 15px; border-radius: 4px; margin-bottom: 15px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    .pouperee-p25-l2 { border-left: 5px solid #2980B9; background-color: #F7F9FA; padding: 15px; border-radius: 4px; margin-bottom: 15px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    .pouperee-p25-l3 { border-left: 5px solid #D35400; background-color: #FFFBF2; padding: 15px; border-radius: 4px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #C0392B; margin-top: 5px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p25">❖ Tableau d\'analyse des problèmes</div>', unsafe_allow_html=True)
    st.markdown('<div class="badge-p25">Diagnostic phytosanitaire & Contraintes du verger (Expertise Étendue 10+ Choix)</div>', unsafe_allow_html=True)

    # --- BANQUE DE DONNÉES ENRICHIE ---
    banque_diagnostics_extended = {
        "Peuplement du verger": {
            "PROBLEMES": [
                "[DENSITÉ] Forte densité (Forte concentration > 1500 pieds/ha)",
                "[DENSITÉ] Faible densité / Verger clairsemé (Sous-densité < 1000 pieds/ha)",
                "[STRUCTURE] Des plages vides en replantation sous des cacaoyers infectés",
                "[ALIGNEMENT] Mauvais piquetage et non-respect des lignes de plantation",
                "[SAUVAGE] Surpeuplement par levée spontanée et désordonnée de fèves au sol",
                "[RENDEMENT] Présence élevée de pieds totalement improductifs (arbres 'mâles')",
                "[ÂGE] Vieillissement généralisé du matériel végétal (Verger sénile > 30 ans)",
                "[INTRUS] Présence d'essences forestières concurrentes non régulées",
                "[AGRO] Taux d'échec élevé (mortalité) des jeunes plants après regarnissage",
                "[SOL] Érosion ou dégradation visible de la couche arable autour des collets"
            ],
            "CAUSES": [
                "[PRATIQUE] Non-respect du dispositif technique recommandé (ex: dispositif 3m x 3m)",
                "[PRATIQUE] Abandon ou absence de remplacement des plants morts (regarnissage non fait)",
                "[PHYTO] Mortalité directe due à la propagation du virus du Swollen Shoot",
                "[QUALITÉ] Utilisation de matériel végétal tout-venant ou de fèves non certifiées",
                "[FAUNE] Attaques sévères de rongeurs et ravageurs sur les jeunes plants installés",
                "[SUIVI] Manque drastique d'arrosage et de suivi agronomique post-replantation",
                "[PRATIQUE] Destruction accidentelle de jeunes plants lors des opérations de désherbage",
                "[CLIMAT] Stress hydrique sévère dû au prolongement de la grande saison sèche",
                "[NUTRITION] Carence nutritionnelle sévère du sol bloquant la reprise racinaire",
                "[FONCIER] Conflits de limites ou absence de sécurisation foncière"
            ],
            "CONSEQUENCES": [
                "[PHYTO] Prolifération des maladies (pourritures brunes) et insectes (mirides, foreurs)",
                "[RENDEMENT] Perte d'espace et chute brutale de la production globale à l'hectare",
                "[RENDEMENT] Chute de la production par étouffement ou compétition entre pieds",
                "[FLORE] Enherbement agressif des espaces vides compliquant les interventions",
                "[CONCURRENCE] Concurrence hydrique et nutritionnelle féroce asphyxiant le verger",
                "[PRATIQUE] Difficulté extrême de circulation pour les traitements et la récolte",
                "[ÉCONOMIE] Perte financière sèche liée à l'achat et à la main-d'œuvre des plants morts",
                "[PHYSIO] Élongation anormale des tiges (étiolement) à la recherche de lumière",
                "[SOL] Lessivage accru des nutriments du sol par manque de couverture foliaire",
                "[DÉCOURAGEMENT] Abandon progressif ou désintérêt du producteur pour les parcelles"
            ],
            "SOLUTIONS": [
                "[PRATIQUE] Régler la densité via une éclaircie sélective ou un recépage planifié",
                "[PRATIQUE] Planifier une campagne de regarnissage ciblé au début des pluies (viser 1111 pieds/ha)",
                "[AGROFORESTERIE] Planter des arbres d'ombrages temporaires (Légumineuses) et définitifs",
                "[TECHNIQUE] Adopter un piquetage rigoureux en quinconce ou en ligne droite (3m x 3m)",
                "[ENTRETIEN] Nettoyage et arrachage systématique des rejets sauvages non contrôlés",
                "[RÉGÉNÉRATION] Introduire un plan de remplacement progressif par substitution ou surgreffage",
                "[FORMATION] Sensibiliser le producteur à la sélection de clones performants (ex: Mercedes)",
                "[CONSERVATION] Pratiquer le paillage autour des jeunes plants pour maintenir l'humidité",
                "[DÉFENSE] Installer des barrières physiques ou répulsifs contre les attaques de rongeurs",
                "[PROTEC] Mettre en place des bandes enherbées pour freiner l'érosion du sol"
            ]
        },
        "Entretien du verger": {
            "PROBLEMES": [
                "[ARCHITECT] Présence de nombreux gourmands non maîtrisés",
                "[FERTILITÉ] Utilisation de fumier de mouton ou de fientes non compostés",
                "[PHYTO] Attaques récurrentes et massives de mirides (capsides)",
                "[PHYTO] Présence de galeries de foreurs de tiges (chenilles xylophages)",
                "[FLORE] Enherbement sévère, lianescent et inconsolé de la sous-cacaoyère",
                "[TAILLE] Absence totale de taille de formation, d'entretien ou de rajeunissement",
                "[LUMIÈRE] Fermeture complète de la canopée provoquant une obscurité permanente",
                "[RÉCOLTE] Maintien de cabosses momifiées ou infectées sur les arbres",
                "[OUTILLAGE] Blessures ouvertes et déchirures d'écorce lors des récoltes à la machette",
                "[SANTE] Accumulation de pourriture sur le tronc due à un mauvais drainage de la parcelle"
            ],
            "CAUSES": [
                "[ENTRETIEN] Absence ou insuffisance flagrante de l'entretien régulier du verger",
                "[FORMATION] Manque de formation technique du producteur sur les itinéraires certifiés",
                "[CALENDRIER] Retard critique dans l'exécution des opérations de calendrier culturel",
                "[INVEST] Indisponibilité locale ou coût trop élevé des intrants agricoles homologués",
                "[ÉQUIPEMENT] Carence chronique en matériel spécifique (Sécateurs, scies horticoles, émondeurs)",
                "[AGRO] Mauvaise association ou mauvaise gestion de la hauteur des arbres d'ombrage",
                "[EAU] Topographie en cuvette favorisant la stagnation prolongée des eaux de pluie",
                "[MAIN D'OEUVRE] Pénurie de main-d'œuvre qualifiée pour les travaux physiques de taille",
                "[PRODUIT] Utilisation accidentelle de produits phytosanitaires contrefaits ou mal dosés",
                "[IGNORANCE] Négligence des mesures d'hygiène phytosanitaire de base (outils non désinfectés)"
            ],
            "CONSEQUENCES": [
                "[PHYTO] Attire les mirides et réduit considérablement la vigueur du cacaoyer",
                "[PHYSIO] Intoxication des plantes et brûlures sévères des radicelles absorbantes",
                "[PRODUCTION] Perte massive de fleurs et flétrissement précoce des jeunes cherelles (Chérelle wilt)",
                "[CHAMPIGNON] Développement fulgurant du Phytophthora (Pourriture brune des cabosses)",
                "[ÉNERGIE] Consommation inutile des réserves de sève par les gourmands au détriment des fruits",
                "[STRUCT] Dessèchement et cassure des branches maîtresses charpentières",
                "[RÉCOLTE] Difficulté accrue de détection et de récolte des cabosses mûres dans les lianes",
                "[VULNÉRABILITÉ] Sensibilité accrue de la plantation aux moindres variations climatiques",
                "[PROPAGATION] Propagation rapide des maladies d'un arbre à l'autre via les outils souillés",
                "[PERTE] Chute rapide du taux de conformité aux exigences des normes de certification"
            ],
            "SOLUTIONS": [
                "[TAILLE] Réaliser rigoureusement la taille d'entretien et l'égourmandage semestriel",
                "[BIOLOGIQUE] Suivre une formation pratique sur la fabrication de compost aérobie amélioré",
                "[TRAITEMENT] Appliquer des traitements insecticides/fongicides ciblés avec des appareils calibrés",
                "[PROPRETÉ] Nettoyer la plantation au moins 3 à 4 fois par an (désherbage manuel)",
                "[HYGIÈNE] Ramasser et éliminer systématiquement les cabosses momifiées hors de la parcelle",
                "[TECHNIQUE] Désinfecter le matériel de coupe à l'alcool ou à la flamme entre chaque arbre",
                "[ÉLAGAGE] Élaguer stratégiquement les branches basses des grands arbres d'ombrage",
                "[EAU] Creuser des rigoles de drainage pour évacuer les excès d'eau stagnante",
                "[EQUIP] Acquérir un kit collectif d'outils horticoles de qualité au sein de la coopérative",
                "[SUIVI] Mettre en place un calendrier visuel de suivi des cycles de traitement et de fertilisation"
            ]
        }
    }

    # 🔐 INITIALISATION ET PERSISTANCE DE LA MEMOIRE (SESSION STATE)
    if "p25_diagnostics_sauvegardes" not in st.session_state:
        st.session_state["p25_diagnostics_sauvegardes"] = {}

    for dom in banque_diagnostics_extended.keys():
        cle_dom = dom.replace(" ", "_").lower()
        if f"p25_sel_p_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_p_{cle_dom}"] = []
        if f"p25_sel_c_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_c_{cle_dom}"] = []
        if f"p25_sel_e_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_e_{cle_dom}"] = []
        if f"p25_sel_s_{cle_dom}" not in st.session_state: st.session_state[f"p25_sel_s_{cle_dom}"] = []
        if f"p25_note_{cle_dom}" not in st.session_state: st.session_state[f"p25_note_{cle_dom}"] = ""

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN COCHÉES ET CLOISONNÉES (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Identification et Diagnostic Spécifique par Domaine", expanded=True):
        st.markdown('<div class="pouperee-p25-l1">', unsafe_allow_html=True)
        st.info("🎯 **Haute Précision :** Les listes contiennent désormais plus de 10 options ciblées. Les sélections sont enregistrées automatiquement.")
        
        diagnostics_saisis = []

        for dom, catalogues in banque_diagnostics_extended.items():
            cle_dom = dom.replace(" ", "_").lower()
            st.markdown(f"#### 📍 {dom}")
            
            sel_prob = st.multiselect(f"Problèmes constatés : {dom}", options=catalogues["PROBLEMES"], key=f"p25_sel_p_{cle_dom}")
            sel_cau = st.multiselect(f"Causes directes : {dom}", options=catalogues["CAUSES"], key=f"p25_sel_c_{cle_dom}")
            sel_cons = st.multiselect(f"Conséquences directes : {dom}", options=catalogues["CONSEQUENCES"], key=f"p25_sel_e_{cle_dom}")
            sel_sol = st.multiselect(f"Solutions préconisées : {dom}", options=catalogues["SOLUTIONS"], key=f"p25_sel_s_{cle_dom}")
            
            note_terrain = st.text_input("Précisions terrain / Notes libres", placeholder="Ex: Zone de bas-fond touchée", key=f"p25_note_{cle_dom}")
            
            if sel_prob:
                diagnostics_saisis.append({
                    "DOMAINE": dom,
                    "PROBLEMES OU CONTRAINTES": " \n• ".join(sel_prob),
                    "CAUSES": " \n• ".join(sel_cau) if sel_cau else "Non spécifié",
                    "CONSEQUENCES": " \n• ".join(sel_cons) if sel_cons else "Non spécifié",
                    "SOLUTIONS": " \n• ".join(sel_sol) if sel_sol else "Non spécifié",
                    "OBSERVATIONS": note_terrain if note_terrain.strip() != "" else "Confirmé sur site"
                })
            st.write("---")
            
        st.session_state["p25_diagnostics_sauvegardes"] = diagnostics_saisis
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : RENDU SYNOPTIQUE MATRICIEL DYNAMIQUE (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visualisation du Tableau)", expanded=True):
        st.markdown('<div class="pouperee-p25-l2">', unsafe_allow_html=True)
        
        donnees_affichees = st.session_state["p25_diagnostics_sauvegardes"]
        
        if len(donnees_affichees) > 0:
            st.markdown("##### 📋 Matrice d'Analyse des Problèmes Enrichie (Format Terrain)")
            df_diagnostics = pd.DataFrame(donnees_affichees)
            
            st.dataframe(
                df_diagnostics[["DOMAINE", "PROBLEMES OU CONTRAINTES", "CAUSES", "CONSEQUENCES", "SOLUTIONS", "OBSERVATIONS"]], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.warning("💡 En attente de saisie à l'Étape 1 pour l'affichage de la matrice synoptique.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA EXPERT / ALERTES DISCRIMINANTES (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Analyse des Vulnérabilités & Moteur décisionnel de Leila", expanded=True):
        st.markdown('<div class="pouperee-p25-l3">', unsafe_allow_html=True)
        
        if len(donnees_affichees) == 0:
            st.success("🟢 **Statut Verger :** Aucun dysfonctionnement n'a été répertorié. Continuer le suivi standard.")
        else:
            st.markdown('<div class="subsection-analysis-title">🔍 Alertes Automatiques Déclenchées par Leila</div>', unsafe_allow_html=True)
            
            texte_diagnostics = " ".join([d["PROBLEMES OU CONTRAINTES"] for d in donnees_affichees]).lower()
            
            if "swollen shoot" in texte_diagnostics or "plages vides" in texte_diagnostics:
                st.error("🚨 **CRITIQUE - Sécurité Sanitaire Nationale (Swollen Shoot) :**\n\n"
                         "*Le diagnostic mentionne des pertes de pieds suspectes ou des plages vides induites. "
                         "Attention, toute replantation à l'aveugle sans respect du cordon sanitaire ou de la période "
                         "de jachère intermédiaire provoquera une ré-infestation par les cochenilles. Alerte prioritaire à remonter à la coopérative.*")
                
            if "forte densité" in texte_diagnostics:
                st.warning("⚠️ **ALERTE AGRO - Excès de Densité (>1500 pieds/ha) :**\n\n"
                           "*Une densité excessive couplée à un manque d'égourmandage engendre un confinement humide sous la canopée. "
                           "C'est l'incubateur parfait pour le Phytophthora (pourriture brune des cabosses). Une éclaircie sélective est hautement recommandée.*")
                
            if "faible densité" in texte_diagnostics:
                st.warning("📉 **ALERTE RENDEMENT - Sous-occupation de l'Espace (<1000 pieds/ha) :**\n\n"
                           "*La sous-densité laisse filtrer trop de lumière, ce qui déclenche un enherbement agressif et épuise les nutriments. "
                           "Le rendement à l'hectare chute drastiquement. Leila préconise de planifier un regarnissage au début de la saison des pluies "
                           "pour viser la cible optimale de 1111 pieds/ha.*")

            if "fumier" in texte_diagnostics or "non composté" in texte_diagnostics:
                st.error("❌ **ALERTE TECHNIQUE - Risque de Phytotoxicité Racinaire :**\n\n"
                         "*L'épandage de matières organiques non stabilisées entraîne une faim d'azote temporaire et dégage une chaleur interne "
                         "susceptible de détruire les radicelles superficielles de l'arbre. Interdire la pratique immédiate tant que le compostage n'est pas maîtrisé.*")
                
            if "sénile" in texte_diagnostics or "vieillissement" in texte_diagnostics:
                st.info("⏳ **STRATÉGIE - Plan de Replantation / Reconversion Obligatoire :**\n\n"
                        "*Le verger a dépassé son seuil optimal de productivité économique. Leila recommande d'intégrer ce producteur "
                        "dans les programmes d'appui aux parcelles agroforestières de nouvelle génération (matériel clonal Mercedes).*")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p25", type="primary", use_container_width=True):
        st.session_state["page_25_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 26
        st.rerun()

    # --- PIED DE PAGE ET PAGINATION RÉGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>25</span>", unsafe_allow_html=True)


def dessiner_page_26_Validation_Producteur():
    # --- 1. INITIALISATION DE LA MÉMOIRE DE SESSION ---
    if "p26_nom_producteur" not in st.session_state:
        st.session_state.p26_nom_producteur = ""
    if "p26_statut_discussion" not in st.session_state:
        st.session_state.p26_statut_discussion = False
    if "p26_accord_producteur" not in st.session_state:
        st.session_state.p26_accord_producteur = False
    if "p26_enregistre" not in st.session_state:
        st.session_state.p26_enregistre = False

    # --- 2. STYLE CSS DÉDIÉ ET OPTIMISÉ ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .title-p26 { color: #113f67; font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    .subtitle-p26 { color: #4A5568; font-size: 14px; margin-bottom: 25px; font-style: italic; }
    
    /* Encadré de la Note institutionnelle */
    .note-box-p26 {
        background-color: #1e3d2f; 
        color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.6;
        text-align: justify;
        margin-bottom: 30px;
    }
    .note-box-p26 strong {
        color: #ffeb3b; 
        font-size: 18px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 3. EN-TÊTE ---
    st.markdown('<div class="title-p26">📢 Restitutions et Engagements des Constats</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-p26">Phase de concertation, de validation et de prise de décision finale</div>', unsafe_allow_html=True)

    # --- 4. AFFICHAGE DE LA NOTE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="note-box-p26">
        <strong>NOTE :</strong> Les constats et recommandations de l'équipe de diagnostic 
        dovent être portés à la connaissance du producteur (et de ses travailleurs si possible). 
        Ces constats et recommandations sont discutés et validés avec le producteur ; 
        ce qui permettra, au regard des objectifs à court et moyen terme du producteur, 
        de prendre la décision finale et de dégager les principales actions à mener.
    </div>
    """, unsafe_allow_html=True)

    # --- 5. MODULE INTERACTIF DE LEILA IA ---
    st.markdown("### 📝 Validation du Rapport de Restitution")
    
    st.write(
        "Avant de générer le plan d'action définitif, confirmez que la séance de "
        "restitution et d'échange a bien eu lieu avec le producteur sur la parcelle."
    )
    
    nom_producteur = st.text_input(
        "Nom du Producteur / Exploitant :", 
        value=st.session_state.p26_nom_producteur,
        placeholder="Ex: M. Kouamé",
        key="input_nom_producteur"
    )
    st.session_state.p26_nom_producteur = nom_producteur
    
    col1, col2 = st.columns(2)
    with col1:
        statut_discussion = st.checkbox(
            "Les constats et recommandations ont été discutés", 
            value=st.session_state.p26_statut_discussion,
            key="chk_statut_discussion"
        )
        st.session_state.p26_statut_discussion = statut_discussion
        
    with col2:
        accord_producteur = st.checkbox(
            "Le producteur valide les décisions proposées", 
            value=st.session_state.p26_accord_producteur,
            key="chk_accord_producteur"
        )
        st.session_state.p26_accord_producteur = accord_producteur

    # --- 6. ZONE D'ENGAGEMENT ET ENREGISTREMENT ---
    st.write("<br>", unsafe_allow_html=True)
    
    if statut_discussion and accord_producteur and nom_producteur.strip() != "":
        st.success(f"✅ Diagnostic validé d'un commun accord avec le producteur **{nom_producteur}**. Prêt pour le déploiement des actions à court et moyen terme !")
        
        if st.button("💾 Enregistrer la validation et générer le Plan de Développement"):
            st.session_state.p26_enregistre = True
            
        if st.session_state.p26_enregistre:
            st.toast("🎉 Données de validation enregistrées avec succès !", icon="💾")
    else:
        st.session_state.p26_enregistre = False
        st.warning("⚠️ En attente de la confirmation des échanges et du nom du producteur pour valider officiellement cette étape.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p26", type="primary", use_container_width=True):
        st.session_state["page_26_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 27
        st.rerun()

    # --- 7. PIED DE PAGE ET NUMÉROTATION RÉGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    _, col_p = st.columns([0.95, 0.05])
    with col_p:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>26</span>", unsafe_allow_html=True)



def dessiner_page_27_Planification_Activites():
    # --- 1. STYLES CSS PERSONNALISÉS ---
    st.markdown("""
    <style>
    /* Le bandeau vert du haut */
    .header-bar-p27 {
        background-color: #C6EFCE; /* Vert clair institutionnel */
        border: 1.5px solid #2E7D32; /* Bordure verte marquée */
        padding: 10px 20px;
        margin-bottom: 30px;
        border-radius: 4px;
    }

    .header-title-p27 {
        color: #006100; /* Vert foncé */
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Le sous-titre avec le diamant */
    .subtitle-container-p27 {
        display: flex;
        align-items: center;
        margin-left: 20px;
        margin-bottom: 25px;
    }

    .diamond-icon-p27 {
        color: #008080; /* Teal / Bleu pétrole */
        font-size: 24px;
        margin-right: 15px;
    }

    .subtitle-text-p27 {
        color: #008080;
        font-size: 22px;
        font-weight: bold;
        text-decoration: underline;
        font-family: 'Arial', sans-serif;
    }

    /* Texte principal et liste */
    .content-container-p27 {
        margin-left: 40px;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        color: #2D3748;
        line-height: 1.6;
    }

    .list-p27 {
        list-style-type: none;
        padding-left: 20px;
        margin-top: 15px;
    }

    .list-item-p27 {
        position: relative;
        margin-bottom: 12px;
    }

    .list-item-p27::before {
        content: "o"; /* Reproduction du marqueur circulaire */
        position: absolute;
        left: -25px;
        color: #4A5568;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. RENDU DE L'INTERFACE ---
    st.markdown('''
        <div class="header-bar-p27">
            <h1 class="header-title-p27">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div class="subtitle-container-p27">
            <span class="diamond-icon-p27">❖</span>
            <span class="subtitle-text-p27">Élaboration du plan d'action sur 5 ans</span>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div class="content-container-p27">
            <p>À l'issue du diagnostic, un plan d'action est élaboré pour une période de 5 ans. La matrice du plan d'action précise :</p>
            <ul class="list-p27">
                <li class="list-item-p27">les axes stratégiques,</li>
                <li class="list-item-p27">les objectifs visés par chaque axe stratégique,</li>
                <li class="list-item-p27">les principales activités par axe et leurs coûts.</li>
            </ul>
        </div>
    ''', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p27", type="primary", use_container_width=True):
        st.session_state["page_27_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 28
        st.rerun()

    # --- PIED DE PAGE ET NUMÉROTATION RÉGLEMENTAIRE ---
    st.write("<br><br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>27</span>", unsafe_allow_html=True)

def analyser_activite_layla(nom_activite, periode_saisie):
    """
    Analyse agronomique prédictive basée sur le calendrier culturel ivoirien.
    """
    act = nom_activite.lower()
    per = periode_saisie.lower()
    
    # 1. ANALYSE ACTIVITÉ : RÉGLER LA DENSITÉ
    if "densité" in act or "densite" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Régler la densité ({periode_saisie}) - Idéal :** Parfait pour repérer les surpeuplements. Le bois est sec et l'enherbement est bas, ce qui facilite la circulation et l'abattage sélectif."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Régler la densité ({periode_saisie}) - Recommandé :** Il faut impérativement finir d'ajuster le piquetage et l'éclaircie avant la reprise forte de la végétation."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "error",
                "msg": f"❌ **Régler la densité ({periode_saisie}) - À éviter :** Le sol est boueux et glissant. Abattre des arbres en cette période de grandes pluies risque de détruire les racines gorgées d'eau des cacaoyers voisins."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Régler la densité ({periode_saisie}) - Possible :** Petite saison sèche, observation recommandée du comportement du verger face à la baisse momentanée des pluies."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "error",
                "msg": f"❌ **Régler la densité ({periode_saisie}) - À proscrire :** Les arbres sont chargés de cabosses pour la grande récolte. Risque majeur de faire tomber les fruits et de blesser les coussinets floraux."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Régler la densité ({periode_saisie}) - Fin de cycle :** Nettoyage sanitaire et réajustement de la parcelle opportun juste après les grands passages de récolte."
            }

    # 2. ANALYSE ACTIVITÉ : RÉALISER LA TAILLE DES CACAOYERS
    elif "taille" in act or "élagage" in act or "elagage" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "warning",
                "msg": f"⚠️ **Taille des cacaoyers ({periode_saisie}) - Prudence :** Taille légère uniquement (gourmands). Évitez les tailles sévères car l'arbre cicatrise mal sans eau et le soleil direct brûlerait l'intérieur du verger mis à nu."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "success",
                "msg": f"🔥 **Taille des cacaoyers ({periode_saisie}) - Période Cruciale :** Grande taille d'entretien. Aérer la canopée juste avant les pluies détruit l'habitat favori des mirides (capsides) et stimule la floraison."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "warning",
                "msg": f"⚠️ **Taille des cacaoyers ({periode_saisie}) - Trop tard :** Évitez les gros travaux de restructuration. Le verger non taillé devient un incubateur à humidité, favorisant la pourriture brune (*Phytophthora*)."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Taille des cacaoyers ({periode_saisie}) - Deuxième passage :** Idéal pour un égourmandage ciblé. On élimine les rejets anarchiques qui ont profité des pluies de juin."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "error",
                "msg": f"❌ **Taille des cacaoyers ({periode_saisie}) - À proscrire :** Entrer avec des machettes ou des scies blesse les coussinets floraux de la récolte future et provoque la chute des cabosses mûres."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Taille des cacaoyers ({periode_saisie}) - Fin de cycle :** Nettoyage de fin de récolte, élimination des branches cassées ou malades avant l'intensité du vent sec de l'Harmattan."
            }

    # 3. ANALYSE ACTIVITÉ : PLANTER LES ARBRES D'OMBRAGE TEMPORAIRES
    elif "plant" in act or "ombrage" in act or "regarnissage" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "error",
                "msg": f"❌ **Arbres d'ombrage ({periode_saisie}) - Interdiction absolue :** Installer de jeunes plants ou des boutures en pleine grande saison sèche conduit inévitablement à un dessèchement racinaire immédiat."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "info",
                "msg": f"⏳ **Arbres d'ombrage ({periode_saisie}) - En attente :** Bon moment pour la préparation des trous (piquetage/potquetage) et la sécurisation en pépinière, mais il faut attendre les vraies pluies pour planter."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "success",
                "msg": f"🏆 **Arbres d'ombrage ({periode_saisie}) - Top Priorité :** Le sommet de l'année. Le sol est meuble et gorgé d'eau, assurant un taux de reprise racinaire proche de 100%."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "error",
                "msg": f"❌ **Arbres d'ombrage ({periode_saisie}) - Risqué :** La petite saison sèche (août) peut être traître. Si le système racinaire n'est pas encore profond, le jeune plant ne survivra pas au stress hydrique."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Arbres d'ombrage ({periode_saisie}) - Dernière chance :** Possible uniquement au tout début du mois de septembre si les pluies reprennent bien."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "error",
                "msg": f"❌ **Arbres d'ombrage ({periode_saisie}) - Interdit :** L'arrivée imminente de l'Harmattan va griller immédiatement les jeunes plants."
            }

    # 4. ANALYSE ACTIVITÉ : FORMATION DU PRODUCTEUR SUR LE COMPOST
    elif "compost" in act or "fertilisation" in act or "engrais" in act:
        if any(m in per for m in ["jan", "fév", "fev"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Excellent :** Période creuse, les producteurs ont du temps. Idéal pour collecter la matière sèche disponible."
            }
        elif any(m in per for m in ["mar", "avr"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Formation Compost ({periode_saisie}) - Neutre :** Les premières pluies activeront les bactéries du tas."
            }
        elif any(m in per for m in ["mai", "jui", "jun"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Pratique terrain :** Matière verte abondante et l'eau de pluie maintient l'humidité requise sans effort d'arrosage."
            }
        elif any(m in per for m in ["jul", "aoû", "aou"]):
            return {
                "statut": "info",
                "msg": f"🟡 **Formation Compost ({periode_saisie}) - Neutre :** Période dédiée principalement au suivi et retournement."
            }
        elif any(m in per for m in ["sep", "oct"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Stratégique :** Le décabossage génère des coques vides riches en potasse. Les composter évite la propagation de la pourriture brune."
            }
        elif any(m in per for m in ["nov", "déc", "dec"]):
            return {
                "statut": "success",
                "msg": f"🟢 **Formation Compost ({periode_saisie}) - Application :** Valorisation des derniers résidus de la récolte avant le climat sec."
            }
            
    return {"statut": "neutre", "msg": f"⚠️ **{nom_activite} ({periode_saisie}) :** Planification enregistrée sans directive technique spécifique."}


def dessiner_page_28_Planification_Des_Activites_Suite():
    # --- 1. MEMOIRE DE SESSION ET VALEURS PAR DÉFAUT ---
    defaults_p28 = {
        "p28_axe_1": "Axe 1 : Réhabilitation du verger",
        "p28_objectif_1": "Remettre la parcelle en bon état de production",
        # Ligne 1
        "p28_act1": "Régler la densité", "p28_co1": "200 000",
        "p28_a1_1": "Jan-Mar", "p28_a2_1": "Jan", "p28_a3_1": "-", "p28_a4_1": "-", "p28_a5_1": "-",
        "p28_re1": "producteur", "p28_pa1": "Coopérative, ANADER",
        # Ligne 2
        "p28_act2": "Réaliser la taille des cacaoyers", "p28_co2": "25 000",
        "p28_a1_2": "Avr", "p28_a2_2": "Avr", "p28_a3_2": "Avr", "p28_a4_2": "Avr", "p28_a5_2": "Avr",
        "p28_re2": "producteur", "p28_pa2": "ANADER",
        # Ligne 3
        "p28_act3": "Planter les arbres d'ombrage temporaires", "p28_co3": "-",
        "p28_a1_3": "Mai-Jui", "p28_a2_3": "Mai", "p28_a3_3": "-", "p28_a4_3": "-", "p28_a5_3": "-",
        "p28_re3": "producteur", "p28_pa3": "Cabinet",
        # Ligne 4
        "p28_act4": "Formation du producteur sur le composte", "p28_co4": "-",
        "p28_a1_4": "Oct", "p28_a2_4": "-", "p28_a3_4": "-", "p28_a4_4": "-", "p28_a5_4": "-",
        "p28_re4": "producteur", "p28_pa4": "Coopérative, Cabinet"
    }

    for key, value in defaults_p28.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --- 2. STYLE CSS SÉCURISÉ ---
    st.markdown("""
    <style>
    .header-plan {
        background-color: #C6E0B4; 
        padding: 15px;
        border: 1px solid #70AD47;
        text-align: left;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .header-title {
        color: #375623;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
        font-family: 'Arial', sans-serif;
    }
    .table-pdc {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Arial', sans-serif;
        font-size: 13px;
        margin-bottom: 20px;
    }
    .table-pdc th {
        background-color: #4472C4; 
        color: white;
        border: 1px solid #A0AEC0;
        padding: 8px;
        text-align: center;
    }
    .table-pdc td {
        border: 1px solid #A0AEC0;
        padding: 8px;
        vertical-align: middle;
        text-align: center;
        background-color: white;
        color: #2D3748;
    }
    .text-left { text-align: left !important; }
    
    div.stTextInput > div > div > input {
        padding: 6px !important;
        text-align: center !important;
        font-size: 13px !important;
    }
    div.stTextArea > div > div > textarea {
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header-plan"><h1 class="header-title">PLAN D\'ACTION SUR LES CINQ PROCHAINES ANNÉES (MODE SAISIE)</h1></div>', unsafe_allow_html=True)
    
    # --- 3. ENTRÉES SYNCHRONISÉES (CORRECTION DU RE-RENDU BUG) ---
    st.session_state.p28_axe_1 = st.text_input("Axe stratégique :", value=st.session_state.p28_axe_1, key="axe_strat_input_unique")
    st.session_state.p28_objectif_1 = st.text_area("Objectif global :", value=st.session_state.p28_objectif_1, height=70, key="obj_global_input_unique")
    
    st.write("### 📝 Remplissez les lignes du plan d'action :")

    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with col1: st.markdown("**Activité**")
    with col2: st.markdown("**Coût (FCFA)**")
    with col3: st.markdown("**Mois A1**")
    with col4: st.markdown("**Mois A2**")
    with col5: st.markdown("**Mois A3**")
    with col6: st.markdown("**Mois A4**")
    with col7: st.markdown("**Mois A5**")
    with col8: st.markdown("**Responsable**")
    with col9: st.markdown("**Partenaires**")
    st.markdown("---")
    
    # --- FORMULAIRE DE LIGNE 1 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act1 = st.text_input("Act 1", value=st.session_state.p28_act1, key="input_act1", label_visibility="collapsed")
    with c2: st.session_state.p28_co1 = st.text_input("Co 1", value=st.session_state.p28_co1, key="input_co1", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_1 = st.text_input("A1_1", value=st.session_state.p28_a1_1, key="input_a1_1", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_1 = st.text_input("A2_1", value=st.session_state.p28_a2_1, key="input_a2_1", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_1 = st.text_input("A3_1", value=st.session_state.p28_a3_1, key="input_a3_1", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_1 = st.text_input("A4_1", value=st.session_state.p28_a4_1, key="input_a4_1", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_1 = st.text_input("A5_1", value=st.session_state.p28_a5_1, key="input_a5_1", label_visibility="collapsed")
    with c8: st.session_state.p28_re1 = st.text_input("Re 1", value=st.session_state.p28_re1, key="input_re1", label_visibility="collapsed")
    with c9: st.session_state.p28_pa1 = st.text_input("Pa 1", value=st.session_state.p28_pa1, key="input_pa1", label_visibility="collapsed")

    # --- FORMULAIRE DE LIGNE 2 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act2 = st.text_input("Act 2", value=st.session_state.p28_act2, key="input_act2", label_visibility="collapsed")
    with c2: st.session_state.p28_co2 = st.text_input("Co 2", value=st.session_state.p28_co2, key="input_co2", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_2 = st.text_input("A1_2", value=st.session_state.p28_a1_2, key="input_a1_2", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_2 = st.text_input("A2_2", value=st.session_state.p28_a2_2, key="input_a2_2", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_2 = st.text_input("A3_2", value=st.session_state.p28_a3_2, key="input_a3_2", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_2 = st.text_input("A4_2", value=st.session_state.p28_a4_2, key="input_a4_2", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_2 = st.text_input("A5_2", value=st.session_state.p28_a5_2, key="input_a5_2", label_visibility="collapsed")
    with c8: st.session_state.p28_re2 = st.text_input("Re 2", value=st.session_state.p28_re2, key="input_re2", label_visibility="collapsed")
    with c9: st.session_state.p28_pa2 = st.text_input("Pa 2", value=st.session_state.p28_pa2, key="input_pa2", label_visibility="collapsed")

    # --- FORMULAIRE DE LIGNE 3 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act3 = st.text_input("Act 3", value=st.session_state.p28_act3, key="input_act3", label_visibility="collapsed")
    with c2: st.session_state.p28_co3 = st.text_input("Co 3", value=st.session_state.p28_co3, key="input_co3", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_3 = st.text_input("A1_3", value=st.session_state.p28_a1_3, key="input_a1_3", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_3 = st.text_input("A2_3", value=st.session_state.p28_a2_3, key="input_a2_3", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_3 = st.text_input("A3_3", value=st.session_state.p28_a3_3, key="input_a3_3", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_3 = st.text_input("A4_3", value=st.session_state.p28_a4_3, key="input_a4_3", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_3 = st.text_input("A5_3", value=st.session_state.p28_a5_3, key="input_a5_3", label_visibility="collapsed")
    with c8: st.session_state.p28_re3 = st.text_input("Re 3", value=st.session_state.p28_re3, key="input_re3", label_visibility="collapsed")
    with c9: st.session_state.p28_pa3 = st.text_input("Pa 3", value=st.session_state.p28_pa3, key="input_pa3", label_visibility="collapsed")

    # --- FORMULAIRE DE LIGNE 4 ---
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([2, 1.2, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2, 1.5])
    with c1: st.session_state.p28_act4 = st.text_input("Act 4", value=st.session_state.p28_act4, key="input_act4", label_visibility="collapsed")
    with c2: st.session_state.p28_co4 = st.text_input("Co 4", value=st.session_state.p28_co4, key="input_co4", label_visibility="collapsed")
    with c3: st.session_state.p28_a1_4 = st.text_input("A1_4", value=st.session_state.p28_a1_4, key="input_a1_4", label_visibility="collapsed")
    with c4: st.session_state.p28_a2_4 = st.text_input("A2_4", value=st.session_state.p28_a2_4, key="input_a2_4", label_visibility="collapsed")
    with c5: st.session_state.p28_a3_4 = st.text_input("A3_4", value=st.session_state.p28_a3_4, key="input_a3_4", label_visibility="collapsed")
    with c6: st.session_state.p28_a4_4 = st.text_input("A4_4", value=st.session_state.p28_a4_4, key="input_a4_4", label_visibility="collapsed")
    with c7: st.session_state.p28_a5_4 = st.text_input("A5_4", value=st.session_state.p28_a5_4, key="input_a5_4", label_visibility="collapsed")
    with c8: st.session_state.p28_re4 = st.text_input("Re 4", value=st.session_state.p28_re4, key="input_re4", label_visibility="collapsed")
    with c9: st.session_state.p28_pa4 = st.text_input("Pa 4", value=st.session_state.p28_pa4, key="input_pa4", label_visibility="collapsed")

    st.markdown("---")
    st.write("### 👁️ Rendu Visuel Officiel de la Page 28 :")

    # --- 4. CRÉATION DU TABLEAU MATRICIEL DYNAMIQUE ---
    html_table = f"""
    <table class="table-pdc">
        <thead>
            <tr>
                <th rowspan="2">Axes stratégiques</th>
                <th rowspan="2">Objectifs</th>
                <th rowspan="2">Activités</th>
                <th rowspan="2">Coût (F CFA)</th>
                <th colspan="5">Période (Mois d'exécution)</th>
                <th rowspan="2">Responsable</th>
                <th rowspan="2">Partenaires</th>
            </tr>
            <tr>
                <th style="background-color:#4472C4;">A1</th>
                <th style="background-color:#4472C4;">A2</th>
                <th style="background-color:#4472C4;">A3</th>
                <th style="background-color:#4472C4;">A4</th>
                <th style="background-color:#4472C4;">A5</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td rowspan="4" style="background-color:#F2F2F2; font-weight:bold; color:black;">{st.session_state.p28_axe_1}</td>
                <td rowspan="4" class="text-left" style="color:black;">{st.session_state.p28_objectif_1}</td>
                <td class="text-left">{st.session_state.p28_act1}</td>
                <td>{st.session_state.p28_co1}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_1}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a2_1}</td>
                <td>{st.session_state.p28_a3_1}</td><td>{st.session_state.p28_a4_1}</td><td>{st.session_state.p28_a5_1}</td>
                <td>{st.session_state.p28_re1}</td>
                <td rowspan="4" class="text-left" style="font-size: 12px;">{st.session_state.p28_pa1}<br><br>{st.session_state.p28_pa2}<br><br>{st.session_state.p28_pa3}</td>
            </tr>
            <tr>
                <td class="text-left">{st.session_state.p28_act2}</td>
                <td>{st.session_state.p28_co2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a2_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a3_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a4_2}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a5_2}</td>
                <td>{st.session_state.p28_re2}</td>
            </tr>
            <tr>
                <td class="text-left">{st.session_state.p28_act3}</td>
                <td>{st.session_state.p28_co3}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_3}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a2_3}</td>
                <td>{st.session_state.p28_a3_3}</td><td>{st.session_state.p28_a4_3}</td><td>{st.session_state.p28_a5_3}</td>
                <td>{st.session_state.p28_re3}</td>
            </tr>
            <tr>
                <td class="text-left">{st.session_state.p28_act4}</td>
                <td>{st.session_state.p28_co4}</td>
                <td style="background-color:#FCF3CF; font-weight:bold;">{st.session_state.p28_a1_4}</td>
                <td>{st.session_state.p28_a2_4}</td><td>{st.session_state.p28_a3_4}</td><td>{st.session_state.p28_a4_4}</td><td>{st.session_state.p28_a5_4}</td>
                <td>{st.session_state.p28_re4}</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    # --- 5. ANALYSE CHRONOLOGIQUE DE LEILA IA ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Le Diagnostic Chronologique de Leila :")

    plan_saisi = [
        {"nom": st.session_state.p28_act1, "periodes": [st.session_state.p28_a1_1, st.session_state.p28_a2_1, st.session_state.p28_a3_1, st.session_state.p28_a4_1, st.session_state.p28_a5_1]},
        {"nom": st.session_state.p28_act2, "periodes": [st.session_state.p28_a1_2, st.session_state.p28_a2_2, st.session_state.p28_a3_2, st.session_state.p28_a4_2, st.session_state.p28_a5_2]},
        {"nom": st.session_state.p28_act3, "periodes": [st.session_state.p28_a1_3, st.session_state.p28_a2_3, st.session_state.p28_a3_3, st.session_state.p28_a4_3, st.session_state.p28_a5_3]},
        {"nom": st.session_state.p28_act4, "periodes": [st.session_state.p28_a1_4, st.session_state.p28_a2_4, st.session_state.p28_a3_4, st.session_state.p28_a4_4, st.session_state.p28_a5_4]}
    ]

    with st.container():
        alertes_affichees = 0
        
        for item in plan_saisi:
            periodes_valides = [p for p in item["periodes"] if p and p.strip() != "-"]
            # Extraction propre des mois si format étendu (ex: "Jan-Mar" -> ["Jan", "Mar"])
            periodes_uniques = []
            for pv in periodes_valides:
                if "-" in pv:
                    periodes_uniques.extend([m.strip() for m in pv.split("-")])
                else:
                    periodes_uniques.append(pv.strip())
            
            periodes_uniques = list(set(periodes_uniques))
            
            for per in periodes_uniques:
                analyse = analyser_activite_layla(item["nom"], per)
                
                if analyse["statut"] == "success":
                    st.success(analyse["msg"])
                    alertes_affichees += 1
                elif analyse["statut"] == "warning":
                    st.warning(analyse["msg"])
                    alertes_affichees += 1
                elif analyse["statut"] == "error":
                    st.error(analyse["msg"])
                    alertes_affichees += 1
                elif analyse["statut"] == "info":
                    st.info(analyse["msg"])
                    alertes_affichees += 1

        if alertes_affichees == 0:
            st.info("🟢 **Leila :** Aucune anomalie chronologique détectée. Le plan d'action suit parfaitement le calendrier cultural ivoirien.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p28", type="primary", use_container_width=True):
        st.session_state["page_28_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 29
        st.rerun()

    # --- PIED DE PAGE ET NUMÉROTATION RÉGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_empty, col_page = st.columns([0.95, 0.05])
    with col_page:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>28</span>", unsafe_allow_html=True)


def dessiner_page_29_Calendrier_Activites():
    # --- STYLE CSS POUR REPRODUCTION MIROIR ---
    st.markdown("""
    <style>
    /* Fond de page blanc */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Bandeau d'en-tête vert */
    .header-bar-p29 {
        background-color: #C6EFCE; 
        border: 1.5px solid #2E7D32;
        padding: 15px 25px;
        margin-bottom: 40px;
    }

    .header-title-p29 {
        color: #006100;
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Style du titre avec le losange (❖) */
    .main-title-container-p29 {
        display: flex;
        align-items: flex-start;
        margin-left: 40px;
        margin-bottom: 30px;
    }

    .diamond-icon-p29 {
        color: #008080;
        font-size: 26px;
        margin-right: 12px;
        line-height: 1;
    }

    .main-title-text-p29 {
        color: #008080;
        font-size: 22px;
        font-weight: bold;
        text-decoration: underline;
        font-family: 'Arial', sans-serif;
    }

    /* Texte descriptif et conteneur global */
    .content-area-p29 {
        margin-left: 90px;
        font-family: 'Arial', sans-serif;
        font-size: 19px;
        color: #000000;
        line-height: 1.5;
    }

    /* Style pour la liste principale avec les cercles (o) */
    .main-list-p29 {
        list-style-type: none;
        padding-left: 0;
        margin-top: 20px;
    }

    .list-item-p29 {
        position: relative;
        padding-left: 25px;
    }

    /* Reproduction exacte du petit cercle 'o' */
    .list-item-p29::before {
        content: "o";
        position: absolute;
        left: 0;
        top: -2px;
        font-weight: bold;
        color: #000000;
    }

    /* Sous-liste imbriquée */
    .nested-list-p29 {
        list-style-type: none;
        padding-left: 30px;
        margin-top: 10px;
    }

    .nested-item-p29 {
        position: relative;
        margin-bottom: 8px;
    }

    /* Tirets d'énumération clairs */
    .nested-item-p29::before {
        content: "-";
        position: absolute;
        left: -20px;
        color: #000000;
        font-weight: bold;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p29 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- CONTENU DE LA PAGE ---

    # 1. Bandeau de titre supérieur
    st.markdown('<div class="header-bar-p29"><h1 class="header-title-p29">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1></div>', unsafe_allow_html=True)

    # 2. Titre principal de la fiche avec icône ❖
    st.markdown('<div class="main-title-container-p29"><span class="diamond-icon-p29">❖</span><span class="main-title-text-p29">Elaboration du calendrier annuel des activités</span></div>', unsafe_allow_html=True)

    # 3. Bloc de texte descriptif et listes (Tout écrit en une seule ligne continue pour bloquer le bug de rendu Streamlit)
    html_liste_strict = '<div class="content-area-p29"><p>Les activités à réaliser doivent être décrites en détail, programmées et <br> intégrées dans une matrice de calendrier annuel d\'activités.</p><ul class="main-list-p29"><li class="list-item-p29">Préciser pour chaque axe stratégique :<ul class="nested-list-p29"><li class="nested-item-p29">les activités,</li><li class="nested-item-p29">les indicateurs opérationnels de suivi,</li><li class="nested-item-p29">les échéances,</li><li class="nested-item-p29">les coûts, ainsi que</li><li class="nested-item-p29">les responsabilités de chacun des acteurs.</li></ul></li></ul></div>'
    st.markdown(html_liste_strict, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p29", type="primary", use_container_width=True):
        st.session_state["page_29_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 30
        st.rerun()

    # 4. Numéro de page officiel (Page 29)
    st.markdown('<div class="footer-page-p29">29</div>', unsafe_allow_html=True)


def dessiner_page_30_Methodologie_Calendrier():
    # --- STYLE CSS APPLIQUÉ DE MANIÈRE SÉCURISÉE ---
    st.markdown("""
    <style>
    /* Fond de page blanc */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Bandeau d'en-tête vert */
    .header-bar-p30 {
        background-color: #C6EFCE; 
        border: 1.5px solid #2E7D32;
        padding: 15px 25px;
        margin-bottom: 40px;
    }

    .header-title-p30 {
        color: #006100;
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Conteneur principal pour le texte */
    .content-area-p30 {
        margin-left: 60px;
        font-family: 'Arial', sans-serif;
        color: #000000;
    }

    /* Style du titre d'introduction */
    .intro-text-p30 {
        font-size: 21px;
        font-weight: bold;
        margin-bottom: 30px;
        line-height: 1.4;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p30 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- CONTENU DE LA PAGE ---

    # 1. Bandeau de titre supérieur
    st.markdown('<div class="header-bar-p30"><h1 class="header-title-p30">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1></div>', unsafe_allow_html=True)

    # 2. Zone de contenu principal
    st.markdown('<div class="content-area-p30"><p class="intro-text-p30">L’élaboration du calendrier annuel d’activités se fait de la manière suivante :</p></div>', unsafe_allow_html=True)

    # 3. Utilisation des composants natifs Streamlit
    col_space, col_content = st.columns([0.1, 0.9])
    
    with col_content:
        st.markdown("**• Dresser la liste des principales activités :** Ce sont les activités retenues à l'issue du diagnostic de l'exploitation.")
        st.write("") # Espace de respiration
        
        st.markdown("**• Répartir les principales activités en tâches opérationnelles :** identifier pour chaque activité, les sous-activités, diviser les sous-activités en tâches.")
        st.write("")
        
        st.markdown("**• Estimer la date de démarrage, la durée et la date de finalisation** de chaque activité.")
        st.write("")
        
        st.markdown("**• Définir les compétences requises :**")
        st.write("")
        
        st.markdown("**• Répartir les tâches au sein de l'équipe :**")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p30", type="primary", use_container_width=True):
        st.session_state["page_30_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 31
        st.rerun()

    # 4. Numéro de page officiel corrigé (Page 30 au lieu de 42)
    st.markdown('<div class="footer-page-p30">30</div>', unsafe_allow_html=True)


def analyser_trimestre_layla(activite, sous_act, trimestre):
    """
    Moteur agronomique de Leila pour la Côte d'Ivoire.
    Analyse la cohérence entre la sous-activité choisie et le trimestre coché.
    """
    act = activite.lower()
    sa = sous_act.lower()
    t = trimestre.upper()
    
    # --- 1. RÉGLER LA DENSITÉ ---
    if "densité" in act or "densite" in act:
        if "diagnostic" in sa or "marquage" in sa or "identifier" in sa:
            if t in ["T1", "T4"]:
                return "success", f"🟢 **[Régler la densité] Idéal en {t} :** La saison sèche et la fin des récoltes offrent une excellente visibilité au sol pour repérer et marquer les arbres en surpeuplement."
            return "info", f"🟡 **[Régler la densité] Possible en {t} :** Attention, l'enherbement et la végétation dense réduisent la visibilité pour un bon diagnostic."
        
        elif "abattage" in sa or "supprimer" in sa or "essartage" in sa:
            if t == "T1":
                return "success", f"🔥 **[Régler la densité] Recommandé en T1 (Grande saison sèche) :** Le bois est sec, le sol est stable. Abattre un arbre maintenant limite les dégâts racinaires sur les cacaoyers voisins."
            elif t == "T2":
                return "warning", f"⚠️ **[Régler la densité] Prudence en T2 (Grandes pluies) :** Sol glissant et boueux. Risque de déraciner ou de blesser les coussinets floraux."
            return "error", f"❌ **[Régler la densité] À proscrire en {t} (Période critique) :** Les arbres sont en pleine floraison ou chargés de cabosses. Risque de pertes économiques directes."

    # --- 2. ENTRETIEN ---
    elif "entretenir" in act or "entretien" in act:
        if "loranthacées" in sa or "gui" in sa:
            if t in ["T1", "T2"]:
                return "success", f"🟢 **[Entretenir] Crucial en {t} :** Éliminer le gui (loranthus) avant la poussée de sève permet au cacaoyer de maximiser ses nutriments."
            return "warning", f"⚠️ **[Entretenir] Moins efficace en {t} :** Le parasite s'est déjà propagé. Nettoyage tardif."
        
        elif "taille d'entretien" in sa or "élagage" in sa:
            if t == "T2":
                return "success", f"🏆 **[Entretenir] Période maîtresse (T2) :** Aérer la canopée juste avant les grandes pluies réduit l'humidité stagnante, freinant la pourriture brune."
            elif t == "T1":
                return "error", f"❌ **[Entretenir] Danger en T1 :** Une taille trop sévère expose le tronc nu au soleil direct de la saison sèche, risquant de brûler l'écorce."
            return "info", f"🟡 **[Entretenir] Passage léger en {t} :** Égourmandage ciblé uniquement."
            
        elif "sanitaire" in sa:
            if t in ["T2", "T3"]:
                return "success", f"🟢 **[Entretenir] Urgence Sanitaire ({t}) :** En pleine saison des pluies, retirer les cabosses momifiées stoppe la progression du Phytophthora."
            return "info", f"🟢 **[Entretenir] Routine ({t}) :** La récolte sanitaire doit s'effectuer de manière continue."

    return "neutre", f"📋 **Planification enregistrée ({t}) :** Activité programmée sans contre-indication majeure."
