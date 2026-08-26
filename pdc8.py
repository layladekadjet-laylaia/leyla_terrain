def dessiner_page_36_Mise_En_Oeuvre_Evaluation():
    # --- STYLE CSS DÉDIÉ SÉCURISÉ (PARTIE V) ---
    st.markdown("""
    <style>
    /* Conteneur central style Diapositive PowerPoint Épurée */
    .transition-container-p36 {
        background-color: #FFFFFF;
        border-left: 8px solid #2C3E50; /* Bleu sombre/gris de gestion */
        border-right: 1px solid #E0E0E0;
        border-top: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 45px 40px;
        border-radius: 4px;
        margin-top: 40px;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .partie-label-p36 {
        color: #7B1FA2; /* Violet distinctif de transition */
        font-size: 18px;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    .titre-principal-p36 {
        color: #2C3E50;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.5;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    .info-footer-p36 {
        margin-top: 40px;
        font-style: italic;
        color: #7F8C8D;
        font-size: 14px;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p36 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    # Rendu de la carte de transition de la Partie V
    st.markdown("""
    <div class="transition-container-p36">
        <div class="partie-label-p36">PARTIE V</div>
        <h1 class="titre-principal-p36">
            MISE EN ŒUVRE ET EVALUATION<br>
            DU PDC
        </h1>
        <div class="info-footer-p36">
            Module de suivi des indicateurs, de performance et de contrôle de terrain
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    
    # Message d'accompagnement pour le cadre de Suivi-Évaluation
    st.info(
        "📊 **Cadre de Suivi-Évaluation :** Cette section est destinée à accueillir les outils de pilotage, "
        "les fiches d'évaluation des performances des coopératives et le suivi des indicateurs de rendement "
        "du verger de cacao."
    )

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p36", type="primary", use_container_width=True):
        st.session_state["page_36_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 37
        st.rerun()

    # Numérotation officielle de la page (Diapo 48)
    st.markdown('<div class="footer-page-p36">48</div>', unsafe_allow_html=True)



def dessiner_page_37_Cycle_Vie_PDC():
    # --- 1. STYLE CSS EXCLUSIF ET SÉCURISÉ POUR L'INTERFACE ---
    st.markdown("""
    <style>
    /* En-tête de la page style PowerPoint */
    .header-cycle-p37 {
        background-color: #DDEBF7; 
        padding: 15px;
        border: 1.5px solid #418AB3;
        text-align: center;
        margin-bottom: 25px;
        border-radius: 4px;
    }
    .title-cycle-p37 {
        color: #1F4E79;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }

    /* Style des Jalons de la Frise (Audits) */
    .jalon-card-p37 {
        padding: 15px;
        border-radius: 6px;
        text-align: center;
        color: white !important;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    
    /* Couleurs des badges de progression */
    .badge-locked-p37 { background: #BDC3C7 !important; border: 2px solid #95A5A6 !important; color: #7F8C8D !important; }
    .badge-bronze-p37 { background: linear-gradient(135deg, #CD7F32, #A0522D) !important; border: 2px solid #8B4513 !important; color: white !important; }
    .badge-argent-p37 { background: linear-gradient(135deg, #C0C0C0, #808080) !important; border: 2px solid #A9A9A9 !important; color: white !important; }
    .badge-or-p37 { background: linear-gradient(135deg, #FFD700, #DAA520) !important; border: 2px solid #B8860B !important; color: #375623 !important; }
    .badge-enregistrement-p37 { background-color: #34495E !important; border: 2px solid #2C3E50 !important; color: white !important; }

    /* Blocs d'informations thématiques */
    .box-info-p37 {
        background-color: #F2F4F4;
        border: 2px solid #BDC3C7;
        border-radius: 8px;
        padding: 15px;
        color: black !important;
        height: 100%;
    }
    .box-info-purple-p37 { border-color: #9B59B6; background-color: #F5EEF8; }
    .box-info-blue-p37 { border-color: #2980B9; background-color: #EBF5FB; }
    .box-info-green-p37 { border-color: #27AE60; background-color: #EAF2F8; }
    
    .box-title-p37 {
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 14px;
        color: #2C3E50;
    }
    .box-title-purple-p37 { color: #8E44AD; }
    
    .box-info-p37 ul, .box-info-p37 li, .box-info-p37 p { color: black !important; }

    /* Numérotation de page en bas à droite */
    .footer-page-p37 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    # Rendu de l'En-tête officielle
    st.markdown("""
    <div class="header-cycle-p37">
        <div class="title-cycle-p37">CHRONOGRAMME ET CYCLE DE VIE DU PDC (SUIVI DES AUDITS AUTOMATIQUES)</div>
    </div>
    """, unsafe_allow_html=True)

    # --- 2. MOTEUR D'ANALYSE INTELLIGENT (SCAN CENTRAL DE LA SESSION DE LA P1 À P36) ---
    st.write("### 🧠 Analyse de Conformité Globale par Layla IA")
    
    points_details = []
    score_conformite = 0

    # ----------------------------------------------------
    # CRITÈRE 1 : VOLET SOCIAL (Données issues de la Page 8 ou équivalentes)
    # ----------------------------------------------------
    # Layla regarde si des anomalies de travail d'enfants ou de travail forcé ont été détectées
    enfants_detectes = st.session_state.get("p8_travail_enfants_detecte", False)
    travail_force_detecte = st.session_state.get("p8_travail_force_detecte", False)
    validation_p8 = st.session_state.get("page_8_validee", False)
    critere_social_officiel = st.session_state.get("ars_travail_enfants", None)

    # Mode intelligent : On valide si explicitement conforme OU si validé sans alertes bloquantes
    if critere_social_officiel == "Conforme" or (validation_p8 and not enfants_detectes and not travail_force_detecte):
        score_conformite += 25
        points_details.append("✅ **Volet Social (25%) :** Aucun cas de travail des enfants ou travail forcé détecté sur l'exploitation. Respect de la norme ARS 1000.")
    elif validation_p8 and (enfants_detectes or travail_force_detecte):
        points_details.append("🚨 **Volet Social (0%) :** Fiche soumise mais Layla a détecté des risques critiques non conformes (travail d'enfants ou vulnérabilité contractuelle).")
    else:
        points_details.append("⏳ **Volet Social (0%) :** Données socio-démographiques absentes ou en attente de validation finale.")

    # ----------------------------------------------------
    # CRITÈRE 2 : PARCELLES, GÉOLOCALISATION & AGROFORESTERIE (Page 14 & associées)
    # ----------------------------------------------------
    critere_carto = st.session_state.get("ars_mapping_gps", False) or st.session_state.get("page_14_validee", False)
    critere_agroforesterie = st.session_state.get("ars_arbres_hectare", 0)
    densite_p14 = st.session_state.get("p14_densite_calculee", 0)

    if critere_carto and (critere_agroforesterie >= 12 or densite_p14 >= 1000):
        if critere_agroforesterie >= 12:
            score_conformite += 25
            points_details.append(f"✅ **Cartographie & Densité (25%) :** Parcelles validées, densité optimale de cacaoyers et strate ombragée conforme ({critere_agroforesterie} arbres forestiers/ha).")
        else:
            score_conformite += 15
            points_details.append(f"⚠️ **Cartographie partielle (15%) :** Parcelles géolocalisées avec succès, mais le quota d'arbres d'ombrage agroforestiers est insuffisant ({critere_agroforesterie}/12 requis).")
    else:
        points_details.append("⏳ **Volet Cartographie & Écologie (0%) :** Données cartographiques ou calculs de densité de peuplement manquants.")

    # ----------------------------------------------------
    # CRITÈRE 3 : PLANIFICATION FINANCIÈRE & BUDGET (Page 34)
    # ----------------------------------------------------
    donnees_p34 = st.session_state.get("p34_donnees") or st.session_state.get("donnees_activites")
    validation_p34 = st.session_state.get("page_34_validee", False)

    if validation_p34 or (donnees_p34 and isinstance(donnees_p34, dict) and len(donnees_p34) > 0):
        score_conformite += 25
        points_details.append("✅ **Planification Financière (25%) :** Le plan budgétaire et l'itinéraire technique sur 5 ans ont été entièrement modélisés et enregistrés.")
    else:
        points_details.append("⏳ **Planification Financière (0%) :** Le tableau des coûts d'exploitation et d'investissement n'a pas encore été finalisé.")

    # ----------------------------------------------------
    # CRITÈRE 4 : ITINÉRAIRE TECHNIQUE & ENVIRONNEMENT (Pages phytosanitaires)
    # ----------------------------------------------------
    etat_sanitaire_conforme = st.session_state.get("ars_gestion_emballages", False) or st.session_state.get("page_phytosanitaire_validee", False)

    if etat_sanitaire_conforme:
        score_conformite += 25
        points_details.append("✅ **Itinéraire Technique & Environnement (25%) :** Traçabilité des intrants opérationnelle et gestion sécurisée des emballages vides phytosanitaires confirmée.")
    else:
        points_details.append("⏳ **Itinéraire Technique (0%) :** Évaluation des pratiques phytosanitaires et de la gestion des déchets environnementaux non complétée.")

    # --- 4. ATTRIBUTION DYNAMIQUE DES GRADES (LOGIQUE EXAMEN BLANC DJÈ AKADJÉ) ---
    # Le score requis pour le socle Bronze est de 30%
    SEUIL_MIN_BRONZE = 30
    
    badge_env_class = "badge-enregistrement-p37"
    badge_bronze_class = "badge-locked-p37"
    badge_argent_class = "badge-locked-p37"
    badge_or_class = "badge-locked-p37"
    
    # La frise s'allume pour montrer où on se situe sur la ligne des 5 ans
    if score_conformite >= 100:
        badge_bronze_class = "badge-bronze-p37"
        badge_argent_class = "badge-argent-p37"
        badge_or_class = "badge-or-p37"
    elif score_conformite >= 70:
        badge_bronze_class = "badge-bronze-p37"
        badge_argent_class = "badge-argent-p37"
    elif score_conformite >= 30:
        badge_bronze_class = "badge-bronze-p37"

    # Détermination de la mention à l'examen blanc pour le Niveau Bronze
    if score_conformite < SEUIL_MIN_BRONZE:
        status_text = f"📝 **Diagnostic Intermédiaire (Examen Blanc) : Niveau Insuffisant.** Votre score actuel est de {score_conformite}%. Vous êtes en dessous des {SEUIL_MIN_BRONZE}% requis pour prétendre au Niveau Bronze au terme de la trajectoire."
        alert_style = "danger" # Rouge/Orange
    elif SEUIL_MIN_BRONZE <= score_conformite <= 50:
        status_text = f"⚡ **Diagnostic Intermédiaire (Examen Blanc) : Niveau Passable ({score_conformite}%).** Vous atteignez le seuil minimal requis (>30%) pour être classé parmi les producteurs admissibles au Niveau Bronze. Maintenez et renforcez ces efforts jusqu'à la page 48 !"
        alert_style = "warning" # Jaune/Orange
    else:
        status_text = f"📈 **Diagnostic Intermédiaire (Examen Blanc) : Performance Solide ({score_conformite}%).** Vos indicateurs actuels vous positionnent favorablement pour sécuriser le Niveau Bronze pour ce PDC environnemental."
        alert_style = "success" # Vert

    # --- 5. AFFICHAGE DE LA FRISE CHRONOLOGIQUE AUTOMATISÉE ---
    st.write("### ⏱️ Positionnement sur le Cycle du PDC (Trajectoire 5 ans)")
    cols_frise = st.columns(4)
    
    with cols_frise[0]:
        st.markdown(f'<div class="jalon-card-p37 {badge_env_class}">📋 ENREGISTREMENT<br><span style="font-size:11px;">Mois 0 - Validé</span></div>', unsafe_allow_html=True)
        st.caption("<div style='text-align:center;'><b>⏱️ Horizon : Début</b></div>", unsafe_allow_html=True)
        
    with cols_frise[1]:
        st.markdown(f'<div class="jalon-card-p37 {badge_bronze_class}">🥉 AUDIT BRONZE<br><span style="font-size:11px;">Requis: >30%</span></div>', unsafe_allow_html=True)
        st.caption("<div style='text-align:center;'><b>⏱️ Horizon : 12 Mois</b></div>", unsafe_allow_html=True)
        
    with cols_frise[2]:
        st.markdown(f'<div class="jalon-card-p37 {badge_argent_class}">🥈 AUDIT ARGENT<br><span style="font-size:11px;">Requis: 70% (+40%)</span></div>', unsafe_allow_html=True)
        st.caption("<div style='text-align:center;'><b>⏱️ Horizon : 5 ans (Évolution)</b></div>", unsafe_allow_html=True)
        
    with cols_frise[3]:
        st.markdown(f'<div class="jalon-card-p37 {badge_or_class}">🥇 AUDIT OR<br><span style="font-size:11px;">Requis: 100% (+30%)</span></div>', unsafe_allow_html=True)
        st.caption("<div style='text-align:center;'><b>⏱️ Horizon : Fin de cycle</b></div>", unsafe_allow_html=True)

    # Affichage de la tendance
    st.write(f"**Tendance de performance du producteur (Pages 1 à 36) : {score_conformite}%**")
    st.progress(score_conformite / 100.0)
    
    # Rendu du message selon le niveau de l'examen blanc
    if alert_style == "danger":
        st.error(status_text)
    elif alert_style == "warning":
        st.warning(status_text)
    else:
        st.success(status_text)

    # --- 6. ONGLETS STRATÉGIQUES PHASES ---
    st.write("### 📋 Actions et Diagnostics par phase")
    tab1, tab2, tab3 = st.tabs([
        "1️⃣ Phase Initiale (0 à 12 mois)", 
        "2️⃣ Phase d'Exécution & Surveillance (5 ans)", 
        "3️⃣ Cadre d'Évaluation Globale"
    ])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="box-info-p37 box-info-purple-p37">
                <div class="box-title-p37 box-title-purple-p37">📢 Actions de Sensibilisation</div>
                <ul>
                    <li>Sensibilisation des SCOOP</li>
                    <li>Enregistrement officiel des SCOOP</li>
                    <li>Sensibilisation directe des producteurs sur le terrain</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="box-info-p37 box-info-blue-p37">
                <div class="box-title-p37">🛠️ Ingénierie & Planification</div>
                <ul>
                    <li>Recrutement d'un Agronome dédié</li>
                    <li>Formation de l'Agronome sur le diagnostic et le fonctionnement du PDC</li>
                    <li>Réalisation complète du diagnostic de terrain</li>
                    <li>Élaboration finale du document de PDC</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("""
            <div class="box-info-p37" style="border-color: #D35400; background-color: #FBEEE6;">
                <div class="box-title-p37" style="color: #D35400;">🔍 Audits de Surveillance Continu</div>
                <p>Pendant les cycles de 5 ans, mise en place de contrôles réguliers pour valider la progression :</p>
                <ul>
                    <li><b>Palier Bronze :</b> Validation du taux d'exécution minimal requis (30%)</li>
                    <li><b>Palier Argent :</b> Validation à hauteur de <b>75%</b> des critères majeurs</li>
                    <li><b>Palier Or :</b> Atteinte finale et maintien à <b>100%</b></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown("""
            <div class="box-info-p37 box-info-green-p37">
                <div class="box-title-p37" style="color: #27AE60;">🌱 Acteurs de la Mise en œuvre</div>
                <p><b>Mise en œuvre concrète du PDC :</b></p>
                <p style="background-color: #FFF2CC; padding: 8px; border-left: 4px solid #F1C40F; font-weight: bold; color: black !important;">
                    Par le producteur lui-même, accompagné pas à pas par la SCOOP.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="box-info-p37" style="border-color: #7B1FA2; background-color: #F5EEF8; text-align: center;">
            <div class="box-title-p37" style="color: #7B1FA2; font-size: 16px;">📈 Évaluation du PDC & Audits de Certification</div>
            <p style="font-size: 14px; color: black;">Le passage d'un grade à l'autre (Bronze &rarr; Argent &rarr; Or) fait l'objet d'un audit formel basé sur des indicateurs de performance stricts (Rendement du cacao, utilisation des intrants, investissements réalisés, et critères sociaux ARS 1000).</p>
        </div>
        """, unsafe_allow_html=True)

    # Sauvegarde du score pour le livrable (Page 49)
    st.session_state["score_page_37"] = score_conformite

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p37", type="primary", use_container_width=True):
        st.session_state["page_37_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 38
        st.rerun()

    # Numérotation officielle de la diapositive en bas à droite (Diapo 49)
    st.markdown('<div class="footer-page-p37">49</div>', unsafe_allow_html=True)



def dessiner_page_38_Structuration_PDC():
    # --- STYLE CSS DÉDIÉ A LA PAGE DE TRANSITION PARTIE VI ---
    st.markdown("""
    <style>
    .stApp { background-color: #F9F9F9; }
    
    /* Conteneur de transition style PowerPoint Premium */
    .transition-container-vi {
        background-color: white;
        border-left: 8px solid #D35400; /* Orange cuivré / Fève de cacao torréfiée */
        border-right: 1px solid #E0E0E0;
        border-top: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 45px 40px;
        border-radius: 4px;
        margin-top: 50px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .partie-label-vi {
        color: #8B4513; /* Brun Chocolat profond */
        font-size: 18px;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    .titre-principal-vi {
        color: #2C3E50;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.5;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    .info-footer-vi {
        margin-top: 40px;
        font-style: italic;
        color: #7F8C8D;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Rendu HTML de la carte centrale
    st.markdown("""
    <div class="transition-container-vi">
        <div class="partie-label-vi">PARTIE VI</div>
        <h1 class="titre-principal-vi">
            STRUCTURATION DU PDC
        </h1>
        <div class="info-footer-vi">
            Module d'agencement institutionnel, d'architecture et de consolidation des données de la filière
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    
    # Encadré d'information agronomique
    st.info(
        "🏗️ **Architecture du Plan :** Cette section pose le cadre structurel définitif de ton document "
        "de Plan de Développement Communal. Elle regroupe la synthèse des axes stratégiques, le squelette "
        "institutionnel et la mise en forme globale exigée pour validation."
    )
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p38", type="primary", use_container_width=True):
        st.session_state["page_38_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 39
        st.rerun()



def dessiner_page_39_Identification_Producteur():
    import time # Sécurité pour le sleep
    
    # --- STYLE CSS APPLIQUÉ AUX FORMULAIRES DU PDC ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    /* En-tête de section style cahier des charges */
    .section-header-39 {
        background-color: #F4ECE1;
        border-left: 6px solid #8B4513; /* Brun Cacao */
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .section-title {
        color: #5C3A21;
        font-size: 20px;
        font-weight: bold;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    .subsection-title {
        color: #2E86C1;
        font-size: 18px;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 15px;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    /* Encadré d'information */
    .info-box-field {
        background-color: #EBF5FB;
        border-left: 4px solid #2980B9;
        padding: 12px;
        border-radius: 4px;
        font-size: 14px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Titre de la Section principale (Reprise exacte du PowerPoint)
    st.markdown("""
    <div class="section-header-39">
        <div class="section-title">I - SITUATION DE RÉFÉRENCE DE L'EXPLOITATION</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Subtitle 1.1
    st.markdown('<div class="subsection-title">1.1 Identification du producteur</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box-field">
        📝 <b>Note de suivi :</b> Renseignez soigneusement les données d'identification du producteur. 
        Ces informations sont obligatoires pour la traçabilité et l'attribution des audits de certification du Conseil du Café-Cacao.
    </div>
    """, unsafe_allow_html=True)

    # 2. FORMULAIRE INTERACTIF D'IDENTIFICATION
    st.write("### 👤 Informations Générales")
    col1, col2 = st.columns(2)
    
    with col1:
        nom_prenoms = st.text_input(
            "Nom et prénoms :", 
            placeholder="Ex: Kouamé Koffi Jean",
            key="p39_nom_prenoms"
        )
        code_national = st.text_input(
            "Code National du producteur (Le Conseil du Café-Cacao) :", 
            placeholder="Ex: CCC-XXXXXXXX-X",
            key="p39_code_national"
        )
        
    with col2:
        contact_tel = st.text_input(
            "Contact (Tél) :", 
            placeholder="Ex: +225 07 XX XX XX XX",
            key="p39_contact_tel"
        )
        code_groupe = st.text_input(
            "Code groupe :", 
            placeholder="Ex: GRP-XXXXX",
            key="p39_code_groupe"
        )

    st.write("---")
    st.write("### 🏢 Appartenance Structurelle")
    col3, col4 = st.columns(2)
    
    with col3:
        nom_entite = st.text_input(
            "Nom Entité reconnue :", 
            placeholder="Nom de la coopérative ou structure",
            key="p39_nom_entite"
        )
    with col4:
        code_entite = st.text_input(
            "Code Entité reconnue :", 
            placeholder="Code d'identification structurelle",
            key="p39_code_entite"
        )

    st.write("---")
    st.write("### 📍 Localisation Géographique de l'Exploitation")
    
    col5, col6, col7 = st.columns(3)
    with col5:
        delegation_regionale = st.text_input(
            "Délégation Régionale du Conseil du Café-Cacao :", 
            placeholder="Ex: Daloa, Soubré, Agboville...",
            key="p39_delegation_regionale"
        )
        campement = st.text_input(
            "Campement :", 
            placeholder="Nom du campement rattaché",
            key="p39_campement"
        )
        
    with col6:
        departement = st.text_input(
            "Département :", 
            placeholder="Ex: Tiassalé",
            key="p39_departement"
        )
        village = st.text_input(
            "Village :", 
            placeholder="Nom du village principal",
            key="p39_village"
        )
        
    with col7:
        sous_prefecture = st.text_input(
            "Sous-Préfecture :", 
            placeholder="Ex: N'douci",
            key="p39_sous_prefecture"
        )

    st.write("---")
    
    # 3. INTERACTION DE SAUVEGARDE INTERMÉDIAIRE
    if st.button("💾 Enregistrer la fiche d'identification du producteur", key="p39_btn_save"):
        if nom_prenoms and code_national:
            st.success(f"✅ Fiche d'identification enregistrée localement pour **{nom_prenoms}** !")
        else:
            st.warning("⚠️ Pour valider l'enregistrement, le Nom et le Code National CCC sont requis.")

    # 4. BOUTON DE NAVIGATION ET VALIDATION CRUCIALE POUR LA PAGE 49
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p39", type="primary", use_container_width=True):
        if nom_prenoms and code_national:
            
            # === PACKAGING DES DONNÉES POUR LE STOCKAGE CENTRAL (PAGE 49) ===
            st.session_state["p39_donnees"] = {
                "nom_prenoms": nom_prenoms,
                "code_national_ccc": code_national,
                "telephone": contact_tel,
                "code_groupe": code_groupe,
                "cooperative_nom": nom_entite,
                "cooperative_code": code_entite,
                "localisation": {
                    "delegation": delegation_regionale,
                    "departement": departement,
                    "sous_prefecture": sous_prefecture,
                    "village": village,
                    "campement": campement
                },
                "statut_enregistrement": "Complet"
            }
            
            st.session_state["page_39_validee"] = True  
            
            if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
                leila_tracker_central()
                
            st.success("✅ Fiche d'identification sauvegardée dans le registre global de Layla.")
            time.sleep(0.4)
            st.session_state.page_actuelle = 40
            st.rerun()
        else:
            st.error("🚨 Bloquant : Impossible de valider le PDC sans le Nom et le Code National du producteur (Conseil du Café-Cacao).")



def dessiner_page_40_Situation_Epargne():
    import time  # Sécurité pour le sleep
    
    # --- STYLE CSS DÉDIÉ AUX TABLEAUX DE SÉLECTION ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    /* Titre de sous-section */
    .subsection-header-40 {
        background-color: #EAF2F8;
        border-left: 6px solid #2980B9;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .subsection-title-40 {
        color: #1F618D;
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    /* Style pour les cartes de chaque type d'épargne */
    .epargne-card {
        background-color: #F8F9F9;
        border: 1px solid #E5E7E9;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .epargne-label {
        font-size: 16px;
        font-weight: bold;
        color: #2C3E50;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. En-tête de la page (Reprise logique de la section I)
    st.caption("I - SITUATION DE RÉFÉRENCE DE L'EXPLOITATION")
    st.markdown("""
    <div class="subsection-header-40">
        <h2 class="subsection-title-40">1.2 Information sur le ménage : Situation de l'épargne</h2>
    </div>
    """, unsafe_allow_html=True)

    st.info("📊 **Suivi financier :** Évaluez la structure d'épargne et l'accès aux financements du ménage pour identifier leur capacité d'investissement de terrain.")

    # 2. COLLECTE DES DONNÉES PAR TYPE D'ÉPARGNE
    types_epargne = ["Mobile Money", "Microfinance", "Banque", "Autres précisez"]
    
    # Dictionnaire local temporaire pour compiler la saisie durant cette exécution du script
    donnees_epargne = {}

    st.write("### 🏦 Grille d'évaluation des comptes et financements")

    for i, epargne in enumerate(types_epargne):
        # On crée un conteneur stylisé pour chaque ligne du tableau d'origine
        st.markdown(f'<div class="epargne-card">', unsafe_allow_html=True)
        
        # Si c'est "Autres précisez", on permet de saisir le nom personnalisé
        if epargne == "Autres précisez":
            label_epargne = st.text_input("Précisez l'autre type d'épargne :", placeholder="Ex: Tontine, Association locale...", key="p40_autre_label")
            epargne_name = label_epargne if label_epargne else "Autres"
        else:
            st.markdown(f'<div class="epargne-label">📂 {epargne}</div>', unsafe_allow_html=True)
            epargne_name = epargne

        # Découpage en 3 colonnes correspondant aux entêtes du PowerPoint
        col1, col2, col3 = st.columns([1, 1, 1.2])
        
        with col1:
            a_un_compte = st.radio(
                "Avez-vous un compte ?",
                options=["Non", "Oui"],
                index=0,
                horizontal=True,
                key=f"p40_compte_{i}"
            )
            
        with col2:
            a_argent = st.radio(
                "Argent disponible sur le compte ?",
                options=["Non", "Oui"],
                index=0,
                horizontal=True,
                key=f"p40_argent_{i}"
            )
            
        with col3:
            beneficie_finance = st.radio(
                "Bénéficiez-vous de financement ?",
                options=["Non", "Oui"],
                index=0,
                horizontal=True,
                key=f"p40_finance_{i}"
            )
            
            # Gestion du montant reçu
            montant = 0
            if beneficie_finance == "Oui":
                montant = st.number_input(
                    "Montant reçu (FCFA) :",
                    min_value=0,
                    step=5000,
                    key=f"p40_montant_{i}"
                )
        
        st.markdown('</div>', unsafe_allow_html=True) # Fermeture de la carte
        
        # Stockage propre des valeurs à chaque itération de la boucle
        donnees_epargne[epargne_name] = {
            "possede_compte": a_un_compte,
            "argent_disponible": a_argent,
            "beneficie_financement": beneficie_finance,
            "montant_recu": montant
        }

    st.write("---")

    # 3. ACTIONS DE SAUVEGARDE INTERMÉDIAIRE
    if st.button("💾 Enregistrer la situation financière du ménage", key="p40_btn_save"):
        st.success("✅ Données financières de l'épargne enregistrées localement avec succès !")
        comptes_actifs = [k for k, v in donnees_epargne.items() if v["possede_compte"] == "Oui"]
        if comptes_actifs:
            st.write(f"**Comptes actifs détectés :** {', '.join(comptes_actifs)}")
        else:
            st.write("⚠️ Aucun compte d'épargne actif déclaré pour ce ménage.")

    # 4. BOUTON DE NAVIGATION ET VALIDATION GLOBALE POUR LA PAGE 49
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p40", type="primary", use_container_width=True):
        
        # === INJECTION CRUCIALE DANS LA SESSION POUR LAYLA IA ===
        # On transfère notre dictionnaire dynamique directement dans la mémoire à long terme
        st.session_state["p40_donnees"] = {
            "grille_epargne": donnees_epargne,
            "total_financements_recus": sum(info["montant_recu"] for info in donnees_epargne.values()),
            "statut_page": "Terminé"
        }
        
        st.session_state["page_40_validee"] = True  
        
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
            
        st.success("✅ Grille financière mémorisée avec succès.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 41
        st.rerun()



def dessiner_page_41_Situation_Main_Oeuvre():
    import time  # Sécurité pour le sleep
    
    # --- STYLE CSS DÉDIÉ AUX GRILLES ET FORMULAIRES DE MAIN D'ŒUVRE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    /* En-tête de la sous-section */
    .subsection-header-41 {
        background-color: #E8F8F5;
        border-left: 6px solid #117A65; /* Vert émeraude sombre */
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .subsection-title-41 {
        color: #117864;
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    /* Style pour les blocs de catégories de membres */
    .membre-box {
        background-color: #FDFEFE;
        border: 1px solid #D5DBDB;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .membre-title {
        font-size: 15px;
        font-weight: bold;
        color: #2C3E50;
        border-bottom: 2px solid #117A65;
        padding-bottom: 5px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. En-tête de la page
    st.caption("I - SITUATION DE RÉFÉRENCE DE L'EXPLOITATION")
    st.markdown("""
    <div class="subsection-header-41">
        <h2 class="subsection-title-41">1.3 Information sur le ménage : Situation de la main d'œuvre</h2>
    </div>
    """, unsafe_allow_html=True)

    st.info("👥 **Suivi de la force de travail :** Renseignez la répartition de la main d'œuvre familiale et externe. Cet indicateur permet d'évaluer la capacité opérationnelle de l'exploitation.")

    # 2. LISTE DES MEMBRES DU MÉNAGE (Reprise exacte du tableau PowerPoint)
    categories_membres = [
        "Propriétaire de l'exploitation",
        "Gérant ou représentant",
        "Conjoints",
        "Enfants 0 - 6 ans",
        "Enfant 6 - 18 ans",
        "Enfant + 18 ans",
        "Manœuvres",
        "Autres (préciser)"
    ]

    donnees_main_oeuvre = {}

    st.write("### 📝 Saisie des caractéristiques par membre / catégorie")

    # Boucle pour générer un formulaire propre par ligne du tableau d'origine
    for i, membre in enumerate(categories_membres):
        st.markdown(f'<div class="membre-box">', unsafe_allow_html=True)
        
        # Gestion dynamique du champ optionnel "Autres (préciser)"
        if "Autres" in membre:
            label_custom = st.text_input("Précisez l'autre type de membre :", placeholder="Ex: Cousin, Neveu, Journalier...", key="p41_autre_label")
            nom_categorie = label_custom if label_custom else "Autres"
        else:
            st.markdown(f'<div class="membre-title">👤 {membre}</div>', unsafe_allow_html=True)
            nom_categorie = membre

        # Organisation en colonnes pour reproduire la structure complexe du tableau
        col1, col2, col3, col4 = st.columns([1, 1, 1.5, 1.5])
        
        with col1:
            st.write("**Effectif par Sexe**")
            nb_f = st.number_input("Nombre Femmes (F)", min_value=0, step=1, key=f"p41_f_{i}")
            nb_m = st.number_input("Nombre Hommes (M)", min_value=0, step=1, key=f"p41_m_{i}")
            
        with col2:
            st.write("**Scolarité**")
            nb_ecole = st.number_input("Nombre encore à l'école", min_value=0, step=1, key=f"p41_ecole_{i}")
            
        with col3:
            st.write("**Niveau d'instruction**")
            niveau = st.selectbox(
                "Niveau majoritaire :",
                options=["Aucun", "Primaire", "Secondaire", "Universitaire"],
                key=f"p41_niveau_{i}"
            )
            
        with col4:
            st.write("**Temps de travail sur la plantation**")
            temps_travail = st.radio(
                "Régime :",
                options=["Plein temps", "Occasionnel", "Aucun"],
                index=0,
                horizontal=True,
                key=f"p41_temps_{i}"
            )
            
        st.markdown('</div>', unsafe_allow_html=True) # Fermeture de la box membre

        # Sauvegarde propre dans le dictionnaire local temporaire (Clés sécurisées)
        donnees_main_oeuvre[nom_categorie] = {
            "femmes": nb_f,
            "hommes": nb_m,
            "a_l_ecole": nb_ecole,
            "niveau_instruction": niveau,
            "temps_travail": temps_travail
        }

    st.write("---")

    # 3. BOUTON DE SAUVEGARDE INTERMÉDIAIRE
    if st.button("💾 Enregistrer la situation de la main d'œuvre", key="p41_btn_save"):
        st.success("✅ Tableau de la main d'œuvre enregistré avec succès dans l'application LAYLA IA !")
        total_actifs = sum([v["femmes"] + v["hommes"] for v in donnees_main_oeuvre.values()])
        st.metric(label="Total de la force de travail déclarée (personnes)", value=total_actifs)

    # 4. BOUTON DE NAVIGATION ET VALIDATION GLOBALE POUR LA PAGE 49
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p41", type="primary", use_container_width=True):
        
        # === INJECTION DES DONNÉES DANS LA SESSION GLOBALE (SÉCURITÉ EXPORT) ===
        total_femmes = sum(v["femmes"] for v in donnees_main_oeuvre.values())
        total_hommes = sum(v["hommes"] for v in donnees_main_oeuvre.values())
        total_scolarises = sum(v["a_l_ecole"] for v in donnees_main_oeuvre.values())
        
        st.session_state["p41_donnees"] = {
            "grille_main_oeuvre": donnees_main_oeuvre,
            "statistiques": {
                "total_femmes": total_femmes,
                "total_hommes": total_hommes,
                "force_travail_totale": total_femmes + total_hommes,
                "total_enfants_scolarises": total_scolarises
            },
            "statut_page": "Terminé"
        }
        
        st.session_state["page_41_validee"] = True  
        
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
            
        st.success("✅ Données de la main d'œuvre synchronisées avec le registre central.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 42
        st.rerun()


import streamlit as st
import numpy as np
import pandas as pd
import math
import os
import matplotlib.pyplot as plt
import pydeck as pdk
import time
import streamlit.components.v1 as components
# IMPORTATION INDISPENSABLE POUR LE CONTRÔLE DE DÉFORESTATION
from shapely.geometry import Polygon, Point 

# =========================================================================
# --- 1. RÉFÉRENTIEL DES PARCS NATIONAUX & RÉSERVES (Tolérance Zéro) ---
# =========================================================================
parcs_et_reserves = {
    "Parc National de Taï (Sud-Ouest / Cavally-Sassandra)": Polygon([
        (-7.50, 6.10), (-6.80, 6.10), (-6.75, 5.80), (-6.70, 5.15), 
        (-7.20, 5.15), (-7.55, 5.40), (-7.50, 6.10)
    ]),
    "Parc National de la Marahoué (Centre-Ouest)": Polygon([
        (-6.15, 7.15), (-5.85, 7.15), (-5.80, 6.80), (-6.10, 6.80), (-6.15, 7.15)
    ]),
    "Parc National de Comoé (Nord-Est / Zanzan)": Polygon([
        (-4.50, 9.80), (-3.10, 9.80), (-3.10, 8.50), (-4.50, 8.50), (-4.50, 9.80)
    ]),
    "Parc National d'Azagny (Sud / Littoral / Grand-Lahou)": Polygon([
        (-5.42, 5.30), (-5.15, 5.30), (-5.15, 5.10), (-5.42, 5.10), (-5.42, 5.30)
    ]),
    "Parc National du Banco (Abidjan / Sud)": Polygon([
        (-4.10, 5.43), (-4.01, 5.43), (-4.01, 5.35), (-4.10, 5.35), (-4.10, 5.43)
    ]),
    "Parc National du Mont Péko (Ouest / Guiglo)": Polygon([
        (-7.30, 7.20), (-6.95, 7.20), (-6.95, 6.90), (-7.30, 6.90), (-7.30, 7.20)
    ]),
    "Parc National du Mont Sangbé (Ouest / Tonkpi)": Polygon([
        (-7.60, 8.10), (-7.10, 8.10), (-7.10, 7.70), (-7.60, 7.70), (-7.60, 8.10)
    ]),
    "Parc National de l'Isles de Ehotilé (Sud-Est / Aboisso)": Polygon([
        (-3.30, 5.18), (-3.15, 5.18), (-3.15, 5.10), (-3.30, 5.10), (-3.30, 5.18)
    ]),
    "Réserve Scientifique de Lamto (V-Baoulé / Tiassalé-Toumodi)": Polygon([
        (-5.05, 6.25), (-4.95, 6.25), (-4.95, 6.18), (-5.05, 6.18), (-5.05, 6.25)
    ]),
    "Réserve de Faune du Haut-Bandama (Centre-Nord)": Polygon([
        (-5.70, 8.70), (-5.20, 8.70), (-5.20, 8.10), (-5.70, 8.10), (-5.70, 8.70)
    ]),
    "Réserve Naturelle Intégrale du Mont Nimba (Extrême Ouest)": Polygon([
        (-8.45, 7.70), (-8.35, 7.70), (-8.35, 7.55), (-8.45, 7.55), (-8.45, 7.70)
    ]),
    "Réserve Naturelle de Mabi-Yaya (Sud-Est / Mé / Indénié)": Polygon([
        (-3.55, 6.15), (-3.15, 6.15), (-3.15, 5.65), (-3.55, 5.65), (-3.55, 6.15)
    ]),
}

# =========================================================================
# --- 2. RÉFÉRENTIEL DES FORÊTS CLASSÉES ---
# =========================================================================
forets_classees = {
    "Forêt Classée de la Niégré (Bas-Sassandra / Soubré / San-Pédro)": Polygon([
        (-6.65, 5.40), (-6.15, 5.40), (-6.15, 4.90), (-6.65, 4.90), (-6.65, 5.40)
    ]),
    "Forêt Classée de Rapides Grah (Sassandra / San-Pédro)": Polygon([
        (-7.10, 5.20), (-6.50, 5.20), (-6.50, 4.70), (-7.10, 4.70), (-7.10, 5.20)
    ]),
    "Forêt Classée du Haut-Sassandra (Vavoua / Daloa)": Polygon([
        (-7.10, 7.45), (-6.70, 7.45), (-6.70, 6.90), (-7.10, 6.90), (-7.10, 7.45)
    ]),
    "Forêt Classée de Tai / Hana (Zone Tampon Sud-Ouest)": Polygon([
        (-7.35, 5.25), (-6.95, 5.25), (-6.95, 4.95), (-7.35, 4.95), (-7.35, 5.25)
    ]),
    "Forêt Classée de Monogaga (Littoral / San-Pédro)": Polygon([
        (-6.60, 4.90), (-6.30, 4.90), (-6.30, 4.75), (-6.60, 4.75), (-6.60, 4.90)
    ]),
    "Forêt Classée de Goin-Débé (Cavally / Guiglo / Ouest)": Polygon([
        (-7.90, 6.20), (-7.30, 6.20), (-7.30, 5.70), (-7.90, 5.70), (-7.90, 6.20)
    ]),
    "Forêt Classée de Cavally (Ouest / Zéaglo / Blolequin)": Polygon([
        (-7.95, 6.60), (-7.40, 6.60), (-7.40, 6.10), (-7.95, 6.10), (-7.95, 6.60)
    ]),
    "Forêt Classée de Scio (Guémon / Duékoué)": Polygon([
        (-7.70, 7.00), (-7.20, 7.00), (-7.20, 6.60), (-7.70, 6.60), (-7.70, 7.00)
    ]),
    "Forêt Classée de Sangouiné (Man / Ouest)": Polygon([
        (-7.75, 7.50), (-7.40, 7.50), (-7.40, 7.20), (-7.75, 7.20), (-7.75, 7.50)
    ]),
    "Forêt Classée de Klon (Zone Ouest / Danané)": Polygon([
        (-8.20, 7.30), (-7.90, 7.30), (-7.90, 7.05), (-8.20, 7.05), (-8.20, 7.30)
    ]),
    "Forêt Classée de Bossématié (Abengourou / Centre-Est)": Polygon([
        (-3.60, 6.50), (-3.30, 6.50), (-3.30, 6.20), (-3.60, 6.20), (-3.60, 6.50)
    ]),
    "Forêt Classée de Béki (Abengourou / Akoupé)": Polygon([
        (-3.85, 6.45), (-3.60, 6.45), (-3.60, 6.15), (-3.85, 6.15), (-3.85, 6.45)
    ]),
    "Forêt Classée de Brassué (Région Daoukro / Centre-Est)": Polygon([
        (-4.10, 7.35), (-3.80, 7.35), (-3.80, 7.05), (-4.10, 7.05), (-4.10, 7.35)
    ]),
    "Forêt Classée de Fetekro (Bouaké / M'Bahiakro)": Polygon([
        (-4.85, 7.80), (-4.60, 7.80), (-4.60, 7.50), (-4.85, 7.50), (-4.85, 7.80)
    ]),
    "Forêt Classée de Dogodou (Gôh / Gagnoa / Lakota)": Polygon([
        (-5.75, 5.95), (-5.45, 5.95), (-5.45, 5.70), (-5.75, 5.70), (-5.75, 5.95)
    ]),
    "Forêt Classée de Koko (Lôh-Djiboua / Divo / Tiassalé)": Polygon([
        (-5.20, 5.90), (-4.95, 5.90), (-4.95, 5.65), (-5.20, 5.65), (-5.20, 5.90)
    ]),
    "Forêt Classée de Gasso (Agnéby-Tiassa / Agboville)": Polygon([
        (-4.40, 6.00), (-4.10, 6.00), (-4.10, 5.75), (-4.40, 5.75), (-4.40, 6.00)
    ]),
    "Forêt Classée d'Irobo (Zone Grand-Lahou / Sikensi)": Polygon([
        (-4.90, 5.55), (-4.60, 5.55), (-4.60, 5.30), (-4.90, 5.30), (-4.90, 5.55)
    ]),
    "Forêt Classée de Yapo-Abbé (Agboville / Azaguié)": Polygon([
        (-4.15, 5.80), (-3.90, 5.80), (-3.90, 5.55), (-4.15, 5.55), (-4.15, 5.80)
    ]),
    "Forêt Classée de la Téné (Oumé / Toumodi)": Polygon([
        (-5.45, 6.60), (-5.15, 6.60), (-5.15, 6.25), (-5.45, 6.25), (-5.45, 6.60)
    ]),
    "Forêt Classée de Sangou (Région Oumé)": Polygon([
        (-5.60, 6.35), (-5.35, 6.35), (-5.35, 6.10), (-5.60, 6.10), (-5.60, 6.35)
    ])
}

# =========================================================================
# --- 3. RÉFÉRENTIEL DES AGRO-FORÊTS ---
# =========================================================================
agroforets = {
    "Agro-forêt Classée d'Ahua (Centre / Dimbokro)": Polygon([
        (-4.85, 6.70), (-4.65, 6.70), (-4.65, 6.50), (-4.85, 6.50), (-4.85, 6.70)
    ]),
    "Agro-forêt Classée de Port-Gauthier (Littoral / Grand-Lahou)": Polygon([
        (-5.30, 5.25), (-5.05, 5.25), (-5.05, 5.08), (-5.30, 5.08), (-5.30, 5.25)
    ]),
    "Agro-forêt Classée de Délicat (Centre-Ouest / Bouaflé / Sinfra)": Polygon([
        (-6.00, 6.70), (-5.70, 6.70), (-5.70, 6.40), (-6.00, 6.40), (-6.00, 6.70)
    ]),
    "Agro-forêt Classée de Bouaflé (Région de la Marahoué)": Polygon([
        (-5.95, 7.05), (-5.75, 7.05), (-5.75, 6.85), (-5.95, 6.85), (-5.95, 7.05)
    ]),
    "Agro-forêt Classée de Monogaga (Option Agroforestière / San-Pédro)": Polygon([
        (-6.55, 4.85), (-6.35, 4.85), (-6.35, 4.76), (-6.55, 4.76), (-6.55, 4.85)
    ]),
    "Agro-forêt Classée de Soubré (Nawa - Zone d'Intensification)": Polygon([
        (-6.75, 5.90), (-6.45, 5.90), (-6.45, 5.60), (-6.75, 5.60), (-6.75, 5.90)
    ]),
    "Agro-forêt Classée du Goin-Débé (Zone Sud-Ouest / Cavally)": Polygon([
        (-7.85, 6.00), (-7.40, 6.00), (-7.40, 5.75), (-7.85, 5.75), (-7.85, 6.00)
    ])
}

# --- FONCTIONS MATHÉMATIQUES ---
def calculer_surface_haversine(coords):
    n = len(coords)
    if n < 3: return 0.0, (0.0, 0.0)

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

    superficie_ha = abs(area) / 20000.0
    return superficie_ha, (centre_lat, centre_lon)

def chercher_lieu_excel(centre_gps, chemin="base_ivoire.xlsx"):
    lat_cible, lon_cible = centre_gps
    ville_trouvee = "Localité inconnue"
    dist_min = 999.0

    if not os.path.exists(chemin):
        return "Fichier Excel introuvable"

    try:
        df = pd.read_excel(chemin, usecols=[28, 29, 30], skiprows=1, names=["nom", "lat", "lon"])
        df = df.dropna(subset=["nom", "lat", "lon"])

        distances = np.sqrt((df["lat"].astype(float) - lat_cible)**2 + (df["lon"].astype(float) - lon_cible)**2)
        idx_min = distances.idxmin()

        if distances[idx_min] < dist_min:
            ville_trouvee = df.loc[idx_min, "nom"]

        return ville_trouvee
    except Exception as e:
        return f"Erreur Lecture Excel : {e}"

# --- MOTEUR GÉOSPATIAL DE CONTRÔLE DE CONFORMITÉ ---
def verifier_statut_environnemental(centre_gps):
    lat, lon = centre_gps
    point_test = Point(lon, lat)

    for nom_parc, polygone in parcs_et_reserves.items():
        if polygone.contains(point_test):
            return "BLOQUÉ", f"🚨 Alerte Critique : La parcelle empiète sur le {nom_parc} ! Zone protégée intégrale. Extraction requise."

    for nom_foret, polygone in forets_classees.items():
        if polygone.contains(point_test):
            return "ALERTE_FORET", f"⚠️ Blocage Marché : La parcelle est détectée dans la {nom_foret}. Risque maximal d'exclusion EUDR / Rainforest Alliance."

    for nom_agro, polygone in agroforets.items():
        if polygone.contains(point_test):
            return "AGROFORET", f"🍂 Régulation Durable : La parcelle est située dans l'{nom_agro}. Restructuration obligatoire via agroforesterie (Zonage de transition contractuel SODEFOR)."

    return "CONFORME", "✅ Conforme : La parcelle est située sur une terre agricole hors de toute zone protégée ou enregistrée."

# --- INTERFACE DE LA PAGE 42 ---
def dessiner_page_42_Description_Exploitation():
    st.title("Interface de Saisie - Page 42")
    st.header("1.3 Description de l'exploitation")
    st.caption("Système Expert Leila IA — Module d'Acquisition Foncier")
    st.write("---")

    if "mode_saisie" not in st.session_state:
        st.session_state.mode_saisie = "Aperçu"
        
    if "donnees_pdc" not in st.session_state:
        st.session_state.donnees_pdc = {}
        
    if "P42" not in st.session_state.donnees_pdc:
        st.session_state.donnees_pdc["P42"] = {
            "points_gps": [
                {'lat': 6.020668, 'lon': -4.357123, 'alt': 120},
                {'lat': 6.020900, 'lon': -4.357123, 'alt': 122},
                {'lat': 6.020900, 'lon': -4.356500, 'alt': 118},
                {'lat': 6.020614, 'lon': -4.356929, 'alt': 125}
            ],
            "rivieres": [],
            "routes": [],
            "localite": "En attente d'analyse...",
            "surface_reelle": 0.0,
            "gps_file": "Aucun",
            "statut_eco": "Non vérifié",
            "details_eco": "Faire une indexation pour lancer l'audit.",
            "arbres_inscrits": []
        }
        
    if "angle_rotation" not in st.session_state:
        st.session_state.angle_rotation = 30.0
    if "mode_auto" not in st.session_state:
        st.session_state.mode_auto = False
    if "surface_prevue" not in st.session_state:
        st.session_state.surface_prevue = "1"

    p42_data = st.session_state.donnees_pdc["P42"]

    def faire_parler_layla(message):
        st.toast(message, icon="🎙️")

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("📥 Téléverser", use_container_width=True, type="primary" if st.session_state.mode_saisie == "televerser" else "secondary"):
            st.session_state.mode_saisie = "televerser"
    with btn_col2:
        if st.button("✏️ Dessiner le croquis", use_container_width=True, type="primary" if st.session_state.mode_saisie == "croquis" else "secondary"):
            st.session_state.mode_saisie = "croquis"
    with btn_col3:
        if st.button("📍 Géolocalisation", use_container_width=True, type="primary" if st.session_state.mode_saisie == "geoloc" else "secondary"):
            st.session_state.mode_saisie = "geoloc"

    st.write("---")

    if st.session_state.mode_saisie == "televerser":
        st.subheader("📥 Importation des Tracés GPS Garmin")
        fichier_garmin = st.file_uploader("Sélectionnez le fichier de relevé (.txt, .csv, .gpx)", type=["txt", "csv", "gpx"], key="garmin_uploader")
        if fichier_garmin is not None:
            st.success(f"✅ Fichier '{fichier_garmin.name}' importé dans Leila !")

    elif st.session_state.mode_saisie == "croquis":
        st.subheader("✏️ Zone de Dessin Libre & Croquis Topographique")
        col_tool1, col_tool2, col_tool3 = st.columns([2, 2, 3])
        with col_tool1: mode_outil = st.radio("🖌️ Action", ["Crayon (Dessiner)", "Main (Gommer)"], horizontal=True)
        with col_tool2: couleur_trait = st.color_picker("🎨 Couleur", "#2E7D32")
        with col_tool3: epaisseur_trait = st.slider("📏 Épaisseur", 1, 10, 4)

        canvas_html = f"""
        <div style="background-color: #1E1E1E; border: 2px solid #4CAF50; border-radius: 8px; padding: 5px;">
            <canvas id="leilaCanvas" width="700" height="400" style="background-color: #121212; cursor: crosshair; display: block; margin: 0 auto; border-radius: 4px;"></canvas>
        </div>
        """
        components.html(canvas_html, height=420)

    elif st.session_state.mode_saisie == "geoloc":
        st.subheader("🌍 LAYLA 3D — Géolocalisation & Topographie")
        
        col_statut1, col_statut2 = st.columns(2)
        with col_statut1: st.info(f"📂 **Fichier Cartographique Actuel :** {p42_data['gps_file']}")
        with col_statut2: st.session_state.surface_prevue = st.text_input("📊 Surface prévue (Ha) :", value=st.session_state.surface_prevue)

        st.write("---")
        col_saisie, col_rendu = st.columns([1.1, 1.9])

        with col_saisie:
            tab_draw, tab_meta = st.tabs(["📝 Éditeur & Infrastructures", "🔍 Indexation & Éco-Audit"])
            
            with tab_draw:
                st.markdown("**Édition des coordonnées**")
                info_gps_header = f"# Surface prévue : {st.session_state.surface_prevue} Ha"
                coords_corps = "\n".join([f"{pt['lat']}, {pt['lon']}, {int(pt['alt'])}" for pt in p42_data["points_gps"]])
                zone_txt = st.text_area("Zone de saisie GPS (Lat, Lon, Alt)", value=f"{info_gps_header}\n{coords_corps}", height=130)
                
                if st.button("📍 AJOUTER POINT / METTRE À JOUR", use_container_width=True):
                    nouveaux_pts = []
                    for l in zone_txt.split('\n'):
                        if ',' in l and not l.startswith('#'):
                            try:
                                val = [float(v.strip()) for v in l.split(',')]
                                nouveaux_pts.append({'lat': val[0], 'lon': val[1], 'alt': val[2] if len(val) >= 3 else 120})
                            except: continue
                    if len(nouveaux_pts) >= 3:
                        p42_data["points_gps"] = nouveaux_pts
                        st.rerun()

            with tab_meta:
                st.markdown("**Indexation & Audit Éco-Environnemental**")
                st.info("Le système interroge `base_ivoire.xlsx` ET les statuts de protection SODEFOR/OIPR.")
                
                if st.button("🔍 Interroger la base matricielle Excel", use_container_width=True):
                    liste_tuples = [(p['lat'], p['lon']) for p in p42_data["points_gps"]]
                    _, centre_test = calculer_surface_haversine(liste_tuples)
                    
                    # 1. Recherche du village
                    nom_localite = chercher_lieu_excel(centre_test)
                    p42_data["localite"] = nom_localite
                    
                    # 2. Audit environnemental multi-niveaux
                    code_statut, msg_audit = verifier_statut_environnemental(centre_test)
                    p42_data["statut_eco"] = code_statut
                    p42_data["details_eco"] = msg_audit
                    
                    # 3. INTERSECTION ET FILTRAGE DES ARBRES (PAGE 45)
                    arbres_inventories = st.session_state.get("arbres_inventoriez", [])
                    arbres_dans_parcelle = []
                    
                    if len(p42_data["points_gps"]) >= 3 and arbres_inventories:
                        poly_parcelle = Polygon([(pt['lon'], pt['lat']) for pt in p42_data["points_gps"]])
                        for a in arbres_inventories:
                            try:
                                p_arbre = Point(float(a["Longitude"]), float(a["Latitude"]))
                                if poly_parcelle.contains(p_arbre):
                                    arbres_dans_parcelle.append(a)
                            except: continue
                            
                    p42_data["arbres_inscrits"] = arbres_dans_parcelle
                    
                    faire_parler_layla(f"Analyse terminée. {len(arbres_dans_parcelle)} arbre(s) d'ombrage rattaché(s) !")
                    st.rerun()
                
                st.write("---")
                st.markdown("**Résultat du diagnostic Foncier/Forêt :**")
                if "statut_eco" in p42_data:
                    if p42_data["statut_eco"] == "BLOQUÉ": st.error(p42_data["details_eco"])
                    elif p42_data["statut_eco"] == "ALERTE_FORET": st.warning(p42_data["details_eco"])
                    elif p42_data["statut_eco"] == "AGROFORET": st.info(p42_data["details_eco"])
                    else: st.success(p42_data["details_eco"])

                # Tableau léger récapitulatif des arbres inscrits
                if p42_data.get("arbres_inscrits"):
                    st.write("")
                    st.markdown(f"🌲 **{len(p42_data['arbres_inscrits'])} Arbre(s) associé(s) à Monsieur X :**")
                    df_light = pd.DataFrame(p42_data["arbres_inscrits"])
                    st.dataframe(df_light[["Nom Local", "Circonférence (cm)", "Compatibilité Cacao"]], use_container_width=True)

            st.write("---")
            if st.button("✅ SAUVEGARDER DANS LE RAPPORT", type="primary", use_container_width=True):
                liste_pts = [(p['lat'], p['lon']) for p in p42_data["points_gps"]]
                sup, _ = calculer_surface_haversine(liste_pts)
                p42_data["gps_file"] = f"{p42_data['localite']} ({sup:.4f} Ha) - {p42_data.get('statut_eco', 'Vérifié')}"
                st.success("💾 Données synchronisées !")
                st.rerun()

        # Rendu visuel cartographique (Panneau Droit)
        with col_rendu:
            liste_pts = [(p['lat'], p['lon']) for p in p42_data["points_gps"]]
            superficie_ha, centre_moyen = calculer_surface_haversine(liste_pts)
            p42_data["surface_reelle"] = superficie_ha

            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("🌳 SURFACE RÉELLE", f"{superficie_ha:.4f} Ha")
            m_col2.metric("📍 LOCALITÉ", p42_data["localite"])
            alt_moy = sum(p['alt'] for p in p42_data["points_gps"]) / len(p42_data["points_gps"]) if p42_data["points_gps"] else 0
            m_col3.metric("⛰️ ALTITUDE MOY", f"{int(alt_moy)} m")

            if p42_data.get("statut_eco") == "BLOQUÉ": st.error(f"❌ ENGAGEMENT INTERDIT : {p42_data['details_eco']}")
            elif p42_data.get("statut_eco") == "ALERTE_FORET": st.warning(p42_data["details_eco"])
            elif p42_data.get("statut_eco") == "AGROFORET": st.info(f"ℹ️ AMÉNAGEMENT SPECIFIQUE : {p42_data['details_eco']}")

            tab_map_3d, tab_map_2d = st.tabs(["🌲 Maquette Réaliste 3D", "📊 Plan Cadastral (2D)"])

            # --- PRÉPARATION DES ARBRES POUR LES CARTES ---
            arbres_inscrits = p42_data.get("arbres_inscrits", [])
            data_arbres_3d = []
            data_arbres_2d = {"lats": [], "lons": [], "colors": []}
            
            def mapping_couleur(compat):
                if "Recommandé" in compat: return [40, 167, 69, 230], '#27ae60'
                elif "Toléré" in compat: return [255, 193, 7, 230], '#f1c40f'
                return [220, 53, 69, 230], '#e74c3c'

            for arb in arbres_inscrits:
                try:
                    rgba, hex_c = mapping_couleur(arb["Compatibilité Cacao"])
                    lat_f = float(arb["Latitude"])
                    lon_f = float(arb["Longitude"])
                    circ_f = float(arb["Circonférence (cm)"])
                    
                    data_arbres_3d.append({
                        "lon": lon_f, "lat": lat_f, 
                        "nom": arb["Nom Local"], "statut": arb["Compatibilité Cacao"],
                        "circ": circ_f, "color": rgba,
                        "hauteur": circ_f * 0.12 # Hauteur proportionnelle à la taille
                    })
                    data_arbres_2d["lats"].append(lat_f)
                    data_arbres_2d["lons"].append(lon_f)
                    data_arbres_2d["colors"].append(hex_c)
                except: continue

            with tab_map_3d:
                poly_coordinates = [[p['lon'], p['lat']] for p in p42_data["points_gps"]]
                df_sol = pd.DataFrame([{"polygon": poly_coordinates, "elevation": alt_moy}])
                
                couleur_couche = "[34, 139, 34, 140]"
                if p42_data.get("statut_eco") == "BLOQUÉ": couleur_couche = "[211, 47, 47, 160]"
                elif p42_data.get("statut_eco") == "ALERTE_FORET": couleur_couche = "[245, 124, 0, 160]"
                elif p42_data.get("statut_eco") == "AGROFORET": couleur_couche = "[30, 144, 255, 140]"

                layers = [
                    pdk.Layer("PolygonLayer", df_sol, get_polygon="polygon", get_fill_color=couleur_couche, get_line_color="[255, 255, 255]", line_width_min_pixels=2)
                ]
                
                # Ajout de la couche 3D des arbres d'ombrage
                if data_arbres_3d:
                    df_arb_3d = pd.DataFrame(data_arbres_3d)
                    layers.append(pdk.Layer(
                        "ColumnLayer",
                        df_arb_3d,
                        get_position="[lon, lat]",
                        get_elevation="hauteur",
                        radius=1.8,
                        get_fill_color="color",
                        pickable=True,
                        auto_highlight=True
                    ))

                view_state = pdk.ViewState(latitude=centre_moyen[0], longitude=centre_moyen[1], zoom=17.0, pitch=50, bearing=st.session_state.angle_rotation)
                st.pydeck_chart(pdk.Deck(
                    layers=layers, 
                    initial_view_state=view_state, 
                    map_style="mapbox://styles/mapbox/satellite-v9",
                    tooltip={"text": "🌳 Essence : {nom}\nDiagnostic : {statut}\nCirconférence : {circ} cm"}
                ))

            with tab_map_2d:
                fig, ax = plt.subplots(figsize=(7, 4.5))
                fig.patch.set_facecolor('#1e1e1e')
                ax.set_facecolor('#1e1e1e')
                lats = [p[0] for p in liste_pts] + [liste_pts[0][0]]
                lons = [p[1] for p in liste_pts] + [liste_pts[0][1]]
                
                couleur_plat = '#27ae60'
                if p42_data.get("statut_eco") == "BLOQUÉ": couleur_plat = '#e74c3c'
                elif p42_data.get("statut_eco") == "ALERTE_FORET": couleur_plat = '#e67e22'
                elif p42_data.get("statut_eco") == "AGROFORET": couleur_plat = '#3498db'

                ax.fill(lons, lats, color=couleur_plat, alpha=0.4, label="Parcelle Cacao")
                ax.plot(lons, lats, color='white', linestyle='-', marker='o', linewidth=2)
                
                # Implantation des points arbres en 2D
                if data_arbres_2d["lats"]:
                    ax.scatter(data_arbres_2d["lons"], data_arbres_2d["lats"], color=data_arbres_2d["colors"], s=70, edgecolor='white', zorder=5, label="Essences compagnes")
                
                ax.set_title(f"Plan Cadastral — Statut : {p42_data.get('statut_eco', 'Non vérifié')}", color="white", fontsize=10)
                ax.tick_params(colors='white', labelsize=8)
                st.pyplot(fig)
    else:
        st.info("Sélectionnez l'un des trois boutons ci-dessus pour commencer.")
