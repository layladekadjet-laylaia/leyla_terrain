def dessiner_page_10_Donnees_sur_les_cultures():
    # --- STYLE CSS REPRODUCTION PRESTIGE DIAPO ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-10 {
        background-color: #E2F0D9; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .titre-10 {
        color: #1F4E78; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .alert-layla-agro-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-warning {
        background-color: #FFF2CC;
        color: #B25E00;
        border-left: 6px solid #FFC000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-ok {
        background-color: #E2F0D9;
        color: #385723;
        border-left: 6px solid #385723;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-10">
        <div class="titre-10">• Données sur les cultures & Statut Réglementaire</div>
    </div>
    """, unsafe_allow_html=True)

    # --- DICTIONNAIRE DES VARIÉTÉS (Triées par ordre de couleur, des meilleures aux moins bonnes) ---
    dict_varietes = {
        "Cacao": ["CNRA (Mercedes)", "Tout-Venant"],
        "Hévéa": ["IRCA 41", "IRCA 18", "GT 1"],
        "P. à huile": ["Tenera", "Dura", "Pisifera"],
        "Vivrier": ["Banane Corne", "Manioc Sika", "Maïs Blanc"],
        "Autres cultures": ["Café Robustat", "Anacarde Recrut"]
    }

    # --- INITIALISATION DE LA MÉMOIRE GLOBALE ---
    if "parcelles_cultures" not in st.session_state:
        st.session_state.parcelles_cultures = [
            {
                "Culture": "Cacao", 
                "Nom Parcelle": "Parcelle 1", 
                "Superficie (ha)": 2.5, 
                "Année de création": 2015, 
                "Précédent cultural": "Forêt secondaire", 
                "Origine matériel végétal": "CNRA (Mercedes)", 
                "En production": "OUI",
                "Zone Classée": "NON (Déclaration)",
                "Proche Aire Protégée": "NON",
                "Litige Foncier": "NON"
            }
        ]

    # Initialisation des flags de session pour la page 49
    st.session_state["p10_has_declared_infraction"] = False
    st.session_state["p10_risques_deforestation"] = False
    st.session_state["p10_alerte_hcv_suspendu"] = False
    st.session_state["p10_agroforesterie_naturelle_active"] = False

    # --- GESTION DYNAMIQUE DES PARCELLES ---
    st.markdown("### 🗺️ Recensement et Intégrité des Parcelles")
    st.caption("Renseignez les données physiques et le questionnaire d'intégrité foncière pour chaque parcelle.")

    col_btn1, col_btn2 = st.columns([0.2, 0.8])
    with col_btn1:
        if st.button("➕ Ajouter une parcelle", use_container_width=True):
            st.session_state.parcelles_cultures.append(
                {
                    "Culture": "Cacao", 
                    "Nom Parcelle": f"Parcelle {len(st.session_state.parcelles_cultures)+1}", 
                    "Superficie (ha)": 1.0, 
                    "Année de création": 2021, 
                    "Précédent cultural": "Jachère", 
                    "Origine matériel végétal": "CNRA (Mercedes)", 
                    "En production": "OUI",
                    "Zone Classée": "NON (Déclaration)",
                    "Proche Aire Protégée": "NON",
                    "Litige Foncier": "NON"
                }
            )
            leila_tracker_central()
            st.rerun()
            
    with col_btn2:
        if len(st.session_state.parcelles_cultures) > 1:
            if st.button("❌ Supprimer la dernière parcelle"):
                st.session_state.parcelles_cultures.pop()
                leila_tracker_central()
                st.rerun()

    opts_cultures = ["Cacao", "Hévéa", "P. à huile", "Vivrier", "Autres cultures"]
    opts_zone = ["NON (Déclaration)", "OUI (Infiltration)"]
    opts_choix = ["NON", "OUI"]

    # --- SYSTÈME DE FORMULAIRE PERSISTANT ---
    for i, parcelle in enumerate(st.session_state.parcelles_cultures):
        label_expander = f"🌳 {parcelle['Culture']} — {parcelle['Nom Parcelle']} | Précédent: {parcelle['Précédent cultural']} ({parcelle['Année de création']})"
        
        with st.expander(label_expander, expanded=(i == len(st.session_state.parcelles_cultures)-1)):
            st.markdown("##### 📍 1. Caractéristiques Agronomiques")
            c1, c2, c3 = st.columns(3)
            
            with c1:
                culture_actuelle = st.selectbox(
                    f"Type de Culture #{i+1}", 
                    opts_cultures,
                    index=opts_cultures.index(parcelle["Culture"]) if parcelle["Culture"] in opts_cultures else 0, 
                    key=f"p10_type_cult_{i}"
                )
                st.session_state.parcelles_cultures[i]["Culture"] = culture_actuelle
                
                st.session_state.parcelles_cultures[i]["Nom Parcelle"] = st.text_input(
                    f"Nom de la parcelle #{i+1}", 
                    value=str(parcelle["Nom Parcelle"]), 
                    key=f"p10_nom_parc_{i}"
                )
                
            with c2:
                st.session_state.parcelles_cultures[i]["Superficie (ha)"] = st.number_input(
                    f"Superficie (ha) #{i+1}", 
                    min_value=0.1, 
                    value=float(parcelle["Superficie (ha)"]), 
                    step=0.1, 
                    key=f"p10_sup_{i}"
                )
                
                st.session_state.parcelles_cultures[i]["Année de création"] = st.number_input(
                    f"Année #{i+1}", 
                    min_value=1960, 
                    max_value=2026, 
                    value=int(parcelle["Année de création"]), 
                    key=f"p10_annee_crea_{i}"
                )
                
            with c3:
                st.session_state.parcelles_cultures[i]["Précédent cultural"] = st.text_input(
                    f"Précédent cultural #{i+1} (Ex: Forêt primaire, sous bois, jachère)", 
                    value=str(parcelle["Précédent cultural"]), 
                    key=f"p10_prec_{i}"
                )
                
                liste_varietes = dict_varietes.get(culture_actuelle, ["CNRA"])
                st.session_state.parcelles_cultures[i]["Origine matériel végétal"] = st.selectbox(
                    f"Origine matériel végétal #{i+1}",
                    liste_varietes,
                    index=liste_varietes.index(parcelle["Origine matériel végétal"]) if parcelle["Origine matériel végétal"] in liste_varietes else 0,
                    key=f"p10_mat_veg_{i}"
                )
                
                st.session_state.parcelles_cultures[i]["En production"] = st.radio(
                    f"En production ? #{i+1}", 
                    opts_choix, 
                    index=opts_choix.index(parcelle["En production"]) if parcelle["En production"] in opts_choix else 0, 
                    horizontal=True, 
                    key=f"p10_prod_{i}"
                )

            st.markdown("##### ⚖️ 2. Questionnaire de Vulnérabilité (Déclaration du Producteur)")
            cq1, cq2, cq3 = st.columns(3)
            with cq1:
                st.session_state.parcelles_cultures[i]["Zone Classée"] = st.selectbox(
                    f"La parcelle est-elle située dans une Forêt Classée / Zone interdite ? #{i+1}",
                    opts_zone,
                    index=opts_zone.index(parcelle["Zone Classée"]) if parcelle["Zone Classée"] in opts_zone else 0,
                    key=f"p10_zc_{i}"
                )
            with cq2:
                st.session_state.parcelles_cultures[i]["Proche Aire Protégée"] = st.selectbox(
                    f"La parcelle est-elle limitrophe d'un Parc National / Réserve ? #{i+1}",
                    opts_choix,
                    index=opts_choix.index(parcelle["Proche Aire Protégée"]) if parcelle["Proche Aire Protégée"] in opts_choix else 0,
                    key=f"p10_ap_{i}"
                )
            with cq3:
                st.session_state.parcelles_cultures[i]["Litige Foncier"] = st.selectbox(
                    f"Existe-t-il un litige foncier ou une contestation ? #{i+1}",
                    opts_choix,
                    index=opts_choix.index(parcelle["Litige Foncier"]) if parcelle["Litige Foncier"] in opts_choix else 0,
                    key=f"p10_lf_{i}"
                )

    leila_tracker_central()

    # --- TABLEAU RECAPITULATIF ---
    st.write("---")
    st.markdown("### 📋 Récapitulatif Enregistré")
    df_cultures = pd.DataFrame(st.session_state.parcelles_cultures)
    st.dataframe(df_cultures, use_container_width=True)

    # --- MOTEUR DE DIAGNOSTIC CENTRALISÉ ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Diagnostic de Conformité Intégré par Layla IA")
    
    alertes_danger = []
    alertes_warning = []
    
    has_declared_infraction = False
    has_deforestation_risk = False
    has_hcv_suspendu = False
    has_agro_naturelle = False
    
    for index, row in df_cultures.iterrows():
        nom_complet_parcelle = f"{row['Culture']} ({row['Nom Parcelle']})"
        precedent = str(row["Précédent cultural"]).lower().strip()
        annee = int(row["Année de création"]) if row["Année de création"] else 2026
        
        # Admin / Foncier
        if row["Zone Classée"] == "OUI (Infiltration)":
            has_declared_infraction = True
            alertes_danger.append(f"🚨 **Aveu de Non-Conformité Majeure** : La parcelle **{nom_complet_parcelle}** est déclarée infiltrée en Forêt Classée par l'exploitant.")
        
        if row["Litige Foncier"] == "OUI":
            alertes_warning.append(f"⚠️ **Alerte Foncier** : Conflit ou litige en cours sur la parcelle **{nom_complet_parcelle}** (Axe Social/Légal ARS 1000).")
            
        if row["Proche Aire Protégée"] == "OUI":
            alertes_warning.append(f"⚠️ **Zone Tampon Critique** : La parcelle **{nom_complet_parcelle}** est limitrophe d'une Aire Protégée. Surveillance GPS renforcée requise.")

        # EUDR & Haute Valeur de Conservation
        if "sous ombrage" in precedent or "sous forêt" in precedent or "nettoy" in precedent:
            if annee > 2020:
                has_deforestation_risk = True
                alertes_danger.append(
                    f"🚨 **DÉGRADATION FORESTIÈRE (Règlement UE - EUDR)** : La parcelle **{nom_complet_parcelle}** "
                    f"a été établie en **{annee}** par modification du sous-bois d'une forêt primaire. L'UE interdit "
                    f"toute dégradation de forêt primaire après le 31/12/2020."
                )
            else:
                has_agro_naturelle = True
                alertes_warning.append(
                    f"⚡ **AGROFORESTERIE TRADITIONNELLE** : La parcelle **{nom_complet_parcelle}** ({annee}) "
                    f"préserve la voûte d'origine. Conformité historique validée (avant 2020)."
                )
                
        elif "primaire" in precedent:
            if annee > 2020:
                has_deforestation_risk = True
                alertes_danger.append(
                    f"🚨 **CRITIQUE - DÉFORESTATION** : La parcelle **{nom_complet_parcelle}** "
                    f"indique la destruction d'une forêt primaire en **{annee}**. Non-conformité absolue (EUDR / RA)."
                )
            else:
                has_hcv_suspendu = True
                alertes_warning.append(
                    f"⚠️ **HAUTE VALEUR DE CONSERVATION (HCV)** : La parcelle **{nom_complet_parcelle}** créée en **{annee}** "
                    f"sur forêt primaire exige un plan de remédiation conforme aux critères de l'ARS 1000."
                )

        elif "secondaire" in precedent or "forêt" in precedent:
            if annee > 2020:
                has_deforestation_risk = True
                alertes_danger.append(
                    f"🚨 **DÉFORESTATION RÉCENTE (Règlement UE - EUDR)** : La parcelle **{nom_complet_parcelle}** "
                    f"a été coupée en **{annee}** (après la date butoir du 31/12/2020). Exclusion du marché européen."
                )
            else:
                st.caption(f"ℹ️ *{nom_complet_parcelle}* : Conversion historique antérieure à 2020. Statut conforme.")

    # Synchronisation Session
    st.session_state["p10_data_verification_piège"] = df_cultures
    st.session_state["p10_has_declared_infraction"] = has_declared_infraction
    st.session_state["p10_risques_deforestation"] = has_deforestation_risk
    st.session_state["p10_alerte_hcv_suspendu"] = has_hcv_suspendu
    st.session_state["p10_agroforesterie_naturelle_active"] = has_agro_naturelle

    if not alertes_danger and not alertes_warning:
        st.markdown('<div class="alert-layla-agro-ok">✅ Déclarations valides. Layla IA est en attente des relevés polygonaux GPS pour confirmation.</div>', unsafe_allow_html=True)
    else:
        for alerte in alertes_danger:
            st.markdown(f'<div class="alert-layla-agro-danger">{alerte}</div>', unsafe_allow_html=True)
        for alerte in alertes_warning:
            st.markdown(f'<div class="alert-layla-agro-warning">{alerte}</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p10", type="primary", use_container_width=True):
        st.session_state["page_10_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 11
        st.rerun()


def dessiner_page_11_Materiel_Equipement():
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-11 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-11 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .statut-coherence-11 {
        background-color: #FFF3CD;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #FFC107;
        margin-top: 5px;
        font-size: 13px;
        font-weight: bold;
    }

    .alert-layla-agro-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-warning {
        background-color: #FFF2CC;
        color: #B25E00;
        border-left: 6px solid #FFC000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-agro-ok {
        background-color: #E2F0D9;
        color: #385723;
        border-left: 6px solid #385723;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="diapo-slide-11">
        <div class="bullet-titre-11">• Matériel agricole et équipements de l'exploitation</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗃️ Gestion de l'Inventaire Logistique (Section Page 11)")
    st.caption("Renseignez avec précision le matériel observé sur l'exploitation pour valider la capacité opérationnelle.")

    base_materiels_cacao = {
        "": [""],
        "1. Matériel de traitement phytosanitaire": [
            "", "Pulvérisateur à pression retenue", "Atomiseur à moteur", "Équipement d'injection (Swollen Shoot)", 
            "Appareil de poudrage", "Pulvérisateur à dos mécanique", "Buses de rechange", "Dosette / Éprouvette graduée",
            "Mélangeur de produit", "Fût de préparation", "Kit de nettoyage phytosanitaire"
        ],
        "2. Matériel de taille, coupe et élagage": [
            "", "Machette (Peugette)", "Sécateur à main", "Échenilloir télescopique", "Scie arboricole circum", 
            "Hache d'abattage", "Couteau d'émondage", "Lime de affûtage", "Tronçonneuse d'élagage", "Serpe"
        ],
        "3. Matériel de récolte et post-récolte (Usinage)": [
            "", "Couteau à cacao (Goulette)", "Écabosseur (Bûchette / Masse en bois)", "Bâche de fermentation",
            "Claie de séchage en bambou", "Séchoir solaire surelevé", "Râteau de séchage (Ricle)", "Sacs en jute neufs",
            "Peseuse / Balance à aiguille", "Crible / Tamis à fèves", "Aiguille de couture pour sac"
        ],
        "4. Matériel d'entretien des parcelles (Nettoyage)": [
            "", "Houe", "Daba ivoirienne", "Pelle plate", "Pioche", "Débroussailleuse thermique", 
            "Râteau de nettoyage", "Hache-paille / Broyeur de résidus", "Cordeau de jalonnement", "Gabarit d'espacement (3m x 3m)"
        ],
        "5. Matériel de transport et logistique": [
            "", "Brouette renforcée", "Charrette à traction", "Moto de livraison", "Tricycle de charge (Moto-tri)", 
            "Cuvette plastique de ramassage", "Panier en osier traditionnel", "Pousse-pousse", "Sangle de portage", "Remorque de plantation"
        ],
        "6. Équipements de Protection Individuelle (EPI)": [
            "", "Combinaison imperméable de traitement", "Masque respiratoire à cartouche", "Lunettes de protection", 
            "Gants en nitrile / caoutchouc", "Bottes de sécurité en caoutchouc", "Visière transparente", 
            "Tablier de protection", "Chapeau à large bord", "Trousse de premiers secours", "EPI COMPLET"
        ]
    }

    if "inventaire_materiels_p11" not in st.session_state:
        st.session_state.inventaire_materiels_p11 = [
            {"Type": "", "Designation": "", "Quantite": 0, "Annee": "", "Cout": 0, "Bon": 0, "Acceptable": 0, "Mauvais": 0}
            for _ in range(4)
        ]

    col_btn1, col_btn2 = st.columns([0.25, 0.75])
    with col_btn1:
        if st.button("➕ Ajouter un équipement", use_container_width=True):
            st.session_state.inventaire_materiels_p11.append(
                {"Type": "", "Designation": "", "Quantite": 0, "Annee": "", "Cout": 0, "Bon": 0, "Acceptable": 0, "Mauvais": 0}
            )
            leila_tracker_central()
            st.rerun()
    with col_btn2:
        if len(st.session_state.inventaire_materiels_p11) > 1:
            if st.button("❌ Supprimer le dernier équipement"):
                st.session_state.inventaire_materiels_p11.pop()
                leila_tracker_central()
                st.rerun()

    inventaire_global = []
    liste_types_disponibles = list(base_materiels_cacao.keys())

    for idx, item in enumerate(st.session_state.inventaire_materiels_p11):
        num_affiche = idx + 1
        type_actuel = item["Type"] if item["Type"] != "" else "Non sélectionné"
        desig_actuelle = item["Designation"] if item["Designation"] != "" else "Outil en attente"
        label_expander = f"📦 Équipement N° {num_affiche} : {desig_actuelle} ({type_actuel.split('. ')[-1]})"

        with st.expander(label_expander, expanded=(idx == len(st.session_state.inventaire_materiels_p11) - 1)):
            c1, c2 = st.columns(2)
            with c1:
                idx_type = liste_types_disponibles.index(item["Type"]) if item["Type"] in liste_types_disponibles else 0
                type_mat = st.selectbox(
                    f"Sélectionner le Type de Matériel #{num_affiche}", 
                    liste_types_disponibles, 
                    index=idx_type,
                    key=f"p11_type_mat_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Type"] = type_mat
                
            with c2:
                liste_desig_filtree = base_materiels_cacao.get(type_mat, [""])
                idx_desig = liste_desig_filtree.index(item["Designation"]) if item["Designation"] in liste_desig_filtree else 0
                desig_mat = st.selectbox(
                    f"Désignation précise de l'outil #{num_affiche}", 
                    liste_desig_filtree, 
                    index=idx_desig,
                    key=f"p11_desig_mat_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Designation"] = desig_mat

            c3, c4, c5 = st.columns([1.5, 1.5, 2])
            with c3:
                quantite = st.number_input(
                    f"Quantité Totale constatée #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Quantite"]), 
                    key=f"p11_qty_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Quantite"] = quantite
            with c4:
                annee = st.text_input(
                    f"Année d'acquisition #{num_affiche}", 
                    value=str(item["Annee"]), 
                    placeholder="Ex: 2024", 
                    key=f"p11_annee_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Annee"] = annee
            with c5:
                cout = st.number_input(
                    f"Coût total d'achat (FCFA) #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Cout"]), 
                    step=5000, 
                    key=f"p11_cout_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Cout"] = cout

            st.markdown("**🔍 Répartition de l'état du matériel :**")
            col_b, col_a, col_m = st.columns(3)
            with col_b:
                bon = st.number_input(
                    f"Nombre en Bon état #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Bon"]), 
                    key=f"p11_bon_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Bon"] = bon
            with col_a:
                acceptable = st.number_input(
                    f"Nombre en état Acceptable #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Acceptable"]), 
                    key=f"p11_acc_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Acceptable"] = acceptable
            with col_m:
                mauvais = st.number_input(
                    f"Nombre en Mauvais état #{num_affiche}", 
                    min_value=0, 
                    value=int(item["Mauvais"]), 
                    key=f"p11_mauv_{idx}"
                )
                st.session_state.inventaire_materiels_p11[idx]["Mauvais"] = mauvais

            somme_etats = bon + acceptable + mauvais
            if quantite > 0 and somme_etats != quantite:
                st.markdown(f"""
                <div class="statut-coherence-11">
                    ⚠️ <b>Alerte Saisie Leila :</b> La somme des états ({bon} Bon + {acceptable} Acceptable + {mauvais} Mauvais = <b>{somme_etats}</b>) 
                    ne correspond pas à la quantité totale déclarée (<b>{quantite}</b>).
                </div>
                """, unsafe_allow_html=True)

            if type_mat != "" and desig_mat != "" and quantite > 0:
                inventaire_global.append({
                    "N°": num_affiche,
                    "Type de matériel": type_mat,
                    "Désignation de l'outil": desig_mat,
                    "Quantité totale": quantite,
                    "Année d'acquisition": annee,
                    "Coût d'achat (FCFA)": cout,
                    "Bon": bon,
                    "Acceptable": acceptable,
                    "Mauvais": mauvais
                })

    st.write("---")
    st.markdown("### 📊 Grand Tableau d'Évaluation Logistique (Page 11)")
    
    alertes_danger = []
    alertes_warning = []
    
    has_phytosanitaire = False
    has_epi_complet = False
    total_epi_masques = 0
    total_pulverisateurs = 0

    if inventaire_global:
        df_global_mat = pd.DataFrame(inventaire_global)
        st.dataframe(df_global_mat.set_index("N°"), use_container_width=True)
        
        total_outils = df_global_mat["Quantité totale"].sum()
        total_investissement = df_global_mat["Coût d'achat (FCFA)"].sum()
        total_en_panne = df_global_mat["Mauvais"].sum()
        
        for index, row in df_global_mat.iterrows():
            t_mat = row["Type de matériel"]
            d_out = row["Désignation de l'outil"]
            qty = row["Quantité totale"]
            
            if "phytosanitaire" in t_mat.lower():
                has_phytosanitaire = True
                total_pulverisateurs += qty
                
            if "protection individuelle" in t_mat.lower() or "epi" in t_mat.lower():
                if "epi complet" in d_out.lower() or "masque" in d_out.lower() or "combinaison" in d_out.lower():
                    has_epi_complet = True
                    total_epi_masques += qty

        # Règles de croisement
        if has_phytosanitaire and not has_epi_complet:
            alertes_danger.append(
                "🚨 **CRITIQUE NORMES SOCIALES (ARS 1000)** : L'exploitation dispose d'appareils phytosanitaires "
                "mais aucun Équipement de Protection Individuelle (EPI) adéquat n'est répertorié. Risque d'intoxication sévère."
            )
        elif has_phytosanitaire and has_epi_complet:
            if total_epi_masques < total_pulverisateurs:
                alertes_warning.append(
                    f"⚠️ **Alerte Risque d'Exposition** : Le nombre d'EPI ({total_epi_masques}) "
                    f"est inférieur au nombre d'appareils applicateurs utilisables simultanément ({total_pulverisateurs})."
                )
            else:
                st.caption("✨ *Sécurité Travail* : Ratios de protection individuelle validés réglementairement.")

        if total_outils > 0 and (total_en_panne / total_outils) > 0.30:
            alertes_warning.append(
                f"⚠️ **Alerte Maintenance Élevée** : Plus de 30% du parc matériel de l'exploitation est en mauvais état "
                f"({total_en_panne} outils défectueux)."
            )

        # Métriques
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric("Outils fonctionnels recensés", total_outils)
        with c_m2:
            st.metric("Capital matériel investi", f"{total_investissement:,} FCFA")
        with c_m3:
            st.metric("Outils défectueux", total_en_panne, delta=f"-{total_en_panne}" if total_en_panne > 0 else "0", delta_color="inverse")
    else:
        st.info("Aucun outil configuré dans le tableau récapitulatif.")

    # Sauvegardes d'états
    st.session_state["p11_inventaire_materiel"] = inventaire_global
    st.session_state["p11_has_phytosanitaire_sans_epi"] = (has_phytosanitaire and not has_epi_complet)
    st.session_state["p11_alertes_danger"] = alertes_danger
    st.session_state["p11_alertes_warning"] = alertes_warning
    st.session_state["p11_is_conforme"] = len(alertes_danger) == 0

    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Analyse de la Capacité Opérationnelle par Layla IA")
    if alertes_danger or alertes_warning:
        for alerte in alertes_danger:
            st.markdown(f'<div class="alert-layla-agro-danger">{alerte}</div>', unsafe_allow_html=True)
        for alerte in alertes_warning:
            st.markdown(f'<div class="alert-layla-agro-warning">{alerte}</div>', unsafe_allow_html=True)
    elif inventaire_global:
        st.markdown('<div class="alert-layla-agro-ok">✅ Analyse Layla IA : Le ratio équipement/EPI est équilibré. Les outils essentiels à la plantation sont fonctionnels.</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p11", type="primary", use_container_width=True):
        st.session_state["page_11_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 12
        st.rerun()

    # Indication stricte de la pagination
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>11</span>", unsafe_allow_html=True)



def dessiner_page_12_Situation_Arbres_Forestiers():
    # --- STYLE CSS REPRODUCTION & INTELLIGENCE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-12 {
        background-color: #C6E0B4; /* Vert clair institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-12 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-recommande { background-color: #28A745; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-tolere { background-color: #FFC107; color: black; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-deconseille { background-color: #DC3545; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-alerte { background-color: #FD7E14; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }

    .bloc-conclusion-conforme { background-color: #D4EDDA; border: 2px solid #28A745; color: #155724; padding: 15px; border-radius: 6px; font-weight: bold; margin-top: 20px; }
    .bloc-conclusion-alerte { background-color: #F8D7DA; border: 2px solid #DC3545; color: #721C24; padding: 15px; border-radius: 6px; font-weight: bold; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BASE DE DONNÉES EXPERTE DES 50 ARBRES ---
    base_arbres_experts = {
        "": ["", "Toléré"],
        "Aboudikro": ["Entandrophragma cylindricum", "Recommandé"],
        "Acajou d'Afrique": ["Khaya ivorensis", "Recommandé"],
        "Ahun (Akoua)": ["Alstonia boonei", "Toléré"],
        "Aiélé": ["Canarium schweinfurthii", "Toléré"],
        "Ako": ["Antiaris toxicaria", "Déconseillé"],
        "Akpi": ["Ricinodendron heudelotii", "Recommandé"],
        "Alové": ["Aningeria robusta", "Toléré"],
        "Assaméla": ["Pericopsis elata", "Recommandé"],
        "Avodiré": ["Turraeanthus africanus", "Toléré"],
        "Azobé": ["Lophira alata", "Toléré"],
        "Badi": ["Nauclea diderrichii", "Toléré"],
        "Bété": ["Mansonia altissima", "Toléré"],
        "Bilinga": ["Nauclea diderrichii", "Toléré"],
        "Bossé clair": ["Guarea cedrata", "Recommandé"],
        "Cèdre d'Afrique": ["Lovoa trichilioides", "Recommandé"],
        "Dabéma": ["Piptadeniastrum africanum", "Toléré"],
        "Dali": ["Tarrietia utilis", "Toléré"],
        "Dibétou": ["Lovoa trichilioides", "Recommandé"],
        "Doussié": ["Afzelia africana", "Recommandé"],
        "Ebène": ["Diospyros crassiflora", "Toléré"],
        "Framiré": ["Terminalia ivorensis", "Recommandé"],
        "Fraqué": ["Terminalia superba", "Recommandé"],
        "Fromager": ["Ceiba pentandra", "Déconseillé"],
        "Iroko": ["Milicia excelsa", "Recommandé"],
        "Kapokier": ["Bombax buonopozense", "Déconseillé"],
        "Kondroti": ["Rhodognaphalon brevicuspe", "Toléré"],
        "Kosso": ["Pterocarpus erinaceus", "Recommandé"],
        "Kotibé": ["Nesogordonia papaverifera", "Toléré"],
        "Koto": ["Pterygota bequaertii", "Toléré"],
        "Lingue": ["Afzelia bipindensis", "Recommandé"],
        "Lotofa": ["Sterculia rhinopetala", "Déconseillé"],
        "Makoré": ["Tieghemella heckelii", "Recommandé"],
        "Moabi": ["Baillonella toxisperma", "Toléré"],
        "Movingui": ["Distemonanthus benthamianus", "Toléré"],
        "Niangon": ["Heritiera utilis", "Toléré"],
        "Oboto": ["Mammea africana", "Toléré"],
        "Obié": ["Triplochiton scleroxylon", "Toléré"],
        "Okoala": ["Sacoglottis gabonensis", "Toléré"],
        "Olona": ["Adansonia digitata", "Déconseillé"],
        "Onzabili": ["Antrocaryon klaineanum", "Toléré"],
        "Ozigo": ["Dacryodes buettneri", "Toléré"],
        "Padouk": ["Pterocarpus soyauxii", "Recommandé"],
        "Rônier": ["Borassus aethiopium", "Toléré"],
        "Samba": ["Triplochiton scleroxylon", "Toléré"],
        "Sapelli": ["Entandrophragma utile", "Recommandé"],
        "Sipo": ["Entandrophragma utile", "Recommandé"],
        "Tali": ["Erythrophleum ivorense", "Toléré"],
        "Tiama": ["Entandrophragma angolense", "Recommandé"],
        "Wengé": ["Millettia laurentii" , "Recommandé"]
    }

    # --- STRUCTURE INTERFACE DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-12">
        <div class="bullet-titre-12">• Situation des arbres autres que le cacaoyer</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗂️ Configuration de l'Inventaire Forestier (Section Page 12)")
    st.caption("Cette section permet de consigner l'état de l'ombrage et la diversité des essences forestières compagnes de la parcelle.")
    
    # Sélection du nombre total d'arbres
    nb_arbres_max = st.number_input("Nombre d'arbres identifiés sur la parcelle :", min_value=1, max_value=50, value=3, key="nb_arbres_p12")

    arbres_saisis = []

    # Génération dynamique des tiroirs
    for idx in range(1, int(nb_arbres_max) + 1):
        nom_session_key = f"local_p12_{idx}"
        
        # Valeurs d'exemples initiales intelligentes adaptées à la Côte d'Ivoire
        if nom_session_key not in st.session_state:
            if idx == 1: st.session_state[nom_session_key] = "Akpi"
            elif idx == 2: st.session_state[nom_session_key] = "Fraqué"
            elif idx == 3: st.session_state[nom_session_key] = "Fromager"
            else: st.session_state[nom_session_key] = ""

        arbre_titre = st.session_state[nom_session_key] if st.session_state[nom_session_key] != "" else "Non configuré"

        with st.expander(f"🌲 Emplacement & Caractéristiques - Arbre N° {idx} : {arbre_titre}"):
            
            # --- LIGNE 1 : Les Identifiants de l'arbre ---
            c1, c2, c3 = st.columns([2, 2, 1.5])
            with c1:
                liste_local = list(base_arbres_experts.keys())
                val_actuelle = st.session_state[nom_session_key]
                idx_default = liste_local.index(val_actuelle) if val_actuelle in liste_local else 0
                
                nom_local = st.selectbox(f"Nom Local #{idx}", liste_local, key=f"sel_nom_{idx}", index=idx_default)
                st.session_state[nom_session_key] = nom_local # Mise à jour de la clé maîtresse
                
            with c2:
                nom_botanique = base_arbres_experts[nom_local][0] if nom_local != "" else ""
                st.text_input(f"Nom Botanique #{idx}", value=nom_botanique, key=f"bot_p12_{idx}", disabled=True)
                
            with c3:
                def_circ = 200 if idx==1 else (70 if idx==2 else 212)
                circonference = st.number_input(f"Circonférence (cm) #{idx}", min_value=0, value=def_circ if nom_local != "" else 0, key=f"circ_p12_{idx}")

            # --- LIGNE 2 : Les Coordonnées Géographiques ---
            c_lat, c_lon, c_orig = st.columns([2, 2, 2])
            with c_lat:
                def_lat = 6.020668 if idx==1 else (6.020664 if idx==2 else 6.020614)
                latitude = st.text_input(f"Latitude #{idx}", value=str(def_lat) if nom_local != "" else "", key=f"lat_p12_{idx}", placeholder="Ex: 6.020668")
            with c_lon:
                def_lon = -4.357123 if idx==1 else (-4.356949 if idx==2 else -4.356929)
                longitude = st.text_input(f"Longitude #{idx}", value=str(def_lon) if nom_local != "" else "", key=f"lon_p12_{idx}", placeholder="Ex: -4.357123")
            with c_orig:
                origine = st.selectbox(f"Origine de l'arbre #{idx}", ["Préservé", "Planté"], key=f"orig_p12_{idx}")

            # --- LIGNE 3 : Usages, Avantages et Décisions ---
            c_av, c_us, c_dec, c_rais = st.columns([2, 2, 2, 2])
            with c_av:
                avantages = st.selectbox(f"Avantages cacaoyer #{idx}", ["Ombrage", "Fertilité du sol", "Protection érosion", "Brise-vent", "Lutte enherbement", "Aucun"], key=f"av_p12_{idx}", index=0 if idx==1 else (4 if idx==2 else 0))
            with c_us:
                usage = st.selectbox(f"Usage de l'arbre #{idx}", ["Bois d'œuvre", "Alimentaire", "Médicinale", "Bois de chauffage", "Protection"], key=f"us_p12_{idx}")
            with c_dec:
                decision = st.selectbox(f"Décision Norme #{idx}", ["A maintenir", "A éliminer"], key=f"dec_p12_{idx}", index=1 if idx==2 else 0)
            with c_rais:
                def_raison = "il y a 2 trop près" if idx==1 else ("Situé à 1,5 m d'un autre" if idx==2 else "")
                raison = st.text_input(f"Raison / Motif technique #{idx}", value=def_raison, key=f"rais_p12_{idx}")

            # --- INTERPRÉTATION INTELLIGENTE DE LEILA IA ---
            compatibilite_finale = "Toléré"
            if nom_local != "":
                statut_botanique = base_arbres_experts[nom_local][1]
                
                if decision == "A éliminer" and statut_botanique == "Recommandé":
                    st.markdown(f"**Avis de Leila :** <span class='badge-alerte'>⚠️ Arbitrage de terrain</span> — L'essence *{nom_local}* est agronomiquement excellente pour le cacao, mais votre décision d'éliminer est validée car motivée par l'espacement (*'{raison}'*). Attention à ne pas sur-éclaircir cette zone.", unsafe_allow_html=True)
                    compatibilite_finale = "Recommandé (Éliminé par contrainte d'espace)"
                
                elif decision == "A éliminer" and statut_botanique == "Déconseillé":
                    st.markdown(f"**Avis de Leila :** <span class='badge-recommande'>👍 Décision approuvée</span> — Correct. Le *{nom_local}* doit être éliminé car il présente un risque pour la plantation (hôte potentiel du Swollen Shoot ou concurrence linéaire).", unsafe_allow_html=True)
                    compatibilite_finale = "Déconseillé"
                
                elif statut_botanique == "Recommandé":
                    st.markdown(f"**Avis de Leila :** <span class='badge-recommande'>👍 Recommandé pour le cacao</span> (Excellent pour la durabilité)", unsafe_allow_html=True)
                    compatibilite_finale = "Recommandé"
                elif statut_botanique == "Toléré":
                    st.markdown(f"**Avis de Leila :** <span class='badge-tolere'>🫳 Toléré</span> (Pas d'effet négatif majeur constaté)", unsafe_allow_html=True)
                    compatibilite_finale = "Toléré"
                else:
                    st.markdown(f"**Avis de Leila :** <span class='badge-deconseille'>⚠️ Déconseillé</span> (Risque sanitaire / Réservoir potentiel Swollen Shoot)", unsafe_allow_html=True)
                    compatibilite_finale = "Déconseillé"

                arbres_saisis.append({
                    "N°": idx,
                    "Nom Local": nom_local,
                    "Nom Botanique": nom_botanique,
                    "Circonférence (cm)": circonference,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Origine": origine,
                    "Avantages": avantages,
                    "Usage": usage,
                    "Décision Norme": decision,
                    "Compatibilité Cacao": compatibilite_finale,
                    "Raison": raison
                })

    st.write("---")

    # --- AFFICHAGE DU GRAND TABLEAU RÉCAPITULATIF ---
    st.markdown("### 📊 Grand Tableau Récapitulatif de la Parcelle")
    if arbres_saisis:
        df_global = pd.DataFrame(arbres_saisis)
        colonnes_ordonnees = ["N°", "Nom Local", "Nom Botanique", "Circonférence (cm)", "Latitude", "Longitude", "Origine", "Avantages", "Usage", "Décision Norme", "Compatibilité Cacao", "Raison"]
        df_global = df_global.reindex(columns=colonnes_ordonnees)
        st.dataframe(df_global.set_index("N°"), use_container_width=True)
    else:
        st.info("Aucun arbre configuré pour le moment.")

    # Sauvegarde dans le session_state pour exploitation ultérieure
    st.session_state["p12_inventaire_forestier"] = arbres_saisis

    # --- CONCLUSION DE LEILA SUR LA CONFORMITÉ ---
    st.markdown("### ⚖️ Conclusion de l'Expert Leila sur la Conformité Agroforestière")
    st.markdown("**NOTE :** Analyse de conformité réglementaire de l'ombrage selon les critères durables.")

    if arbres_saisis:
        total_maintenus = sum(1 for a in arbres_saisis if a["Décision Norme"] == "A maintenir")

        if total_maintenus < 2:
            st.markdown(f"""
            <div class="bloc-conclusion-alerte">
                ⚠️ PARCELLE NON CONFORME (Sous-densité d'ombrage)<br>
                <span style='font-weight:normal; font-size:14px;'>
                    Leila constate un manque d'arbres d'ombrage préservés au sein de cette section (seulement {total_maintenus} maintenu(s)). Même si certaines éliminations s'expliquent par des contraintes d'espace (arbres trop serrés), le périmètre global requiert une meilleure couverture forestière pour atténuer les stress thermiques. 
                    <br>💡 <i>Conseil de Leila : Stabilisez le déboisement technique et planifiez l'introduction de nouvelles essences recommandées (comme l'Akpi ou l'Acajou) bien espacées pour atteindre l'équilibre agronomique idéal.</i>
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bloc-conclusion-conforme">
                ✅ PARCELLE CONFORME (Gestion agroforestière intelligente)<br>
                <span style='font-weight:normal; font-size:14px;'>
                    Leila valide le diagnostic ! L'équilibre entre les strates conservées pour l'ombrage protecteur ({total_maintenus} arbres) et les éliminations ciblées témoigne d'une maîtrise technique rigoureuse de la densité de l'espace agroforestier.
                </span>
            </div>
            """, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p12", type="primary", use_container_width=True):
        st.session_state["page_12_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 13
        st.rerun()

    # Numéro de page exact (12)
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>12</span>", unsafe_allow_html=True)


def dessiner_page_13_Donnees_Agronomiques():
    # --- STYLE CSS REPRODUCTION & PRESTIGE AGRONOMIQUE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-13 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-13 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .section-box-p13 { 
        background-color: #F2F4F4; 
        border-left: 5px solid #16A085; 
        padding: 18px; 
        border-radius: 4px; 
        margin-bottom: 20px; 
    }
    
    .bullet-title { font-weight: bold; color: #16A085; font-size: 16px; margin-bottom: 10px; }
    .bullet-text { font-size: 14px; color: #34495E; margin-left: 20px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-13">
        <div class="bullet-titre-13">C - Données Agronomiques (Fiche 3)</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 📐 Évaluation Expérimentale de la Densité des Cacaoyers")
    
    # --- BLOC MÉTHODOLOGIQUE ---
    st.markdown("""
    <div class="section-box-p13">
        <div class="bullet-title">🧠 Méthodologie d'évaluation de la densité (Standards Côte d'Ivoire) :</div>
        <div class="bullet-text">1. Poser <b>4 carrés de densité de 10 m × 10 m</b> sur un hectare.</div>
        <div class="bullet-text">2. Les carrés sont choisis aléatoirement par la <b>méthode des diagonales</b>.</div>
        <div class="bullet-text">3. Dans chaque carré de densité, compter scrupuleusement les arbres productifs et le nombre de tiges.</div>
        <div class="bullet-text">4. <i>Note : Multiplier par 100 le nombre moyen d'arbres par carré pour obtenir la densité moyenne automatique par hectare.</i></div>
    </div>
    """, unsafe_allow_html=True)

    # --- INITIALISATION DE LA GRILLE DANS LE SESSION STATE ---
    if "grille_densite_p13" not in st.session_state:
        st.session_state.grille_densite_p13 = [
            {"Indicateur": "Nombre cacaoyers productifs", "Carré 1": 12, "Carré 2": 11, "Carré 3": 13, "Carré 4": 12},
            {"Indicateur": "Nb moyen de tiges / pied", "Carré 1": 1.0, "Carré 2": 1.1, "Carré 3": 1.0, "Carré 4": 1.2}
        ]

    if "rendement_p13" not in st.session_state:
        st.session_state.rendement_p13 = 450

    # --- AFFICHAGE SAA (Saisie Assistée Interactive) DE LA GRILLE ---
    st.markdown("#### 📊 Grille de comptage des 4 Carrés (100m² chacun)")
    
    # Pour rendre le tableau éditable de manière persistante, on passe par un st.data_editor
    df_grille = pd.DataFrame(st.session_state.grille_densite_p13)
    edited_df = st.data_editor(df_grille, use_container_width=True, key="editor_grille_p13")
    
    # Réinjection immédiate dans la session pour conserver les modifications
    st.session_state.grille_densite_p13 = edited_df.to_dict(orient="records")

    # --- LOGIQUE DE CALCUL AUTOMATIQUE ---
    try:
        prod_row = edited_df[edited_df["Indicateur"] == "Nombre cacaoyers productifs"].iloc[0]
        moyenne_carre = (float(prod_row["Carré 1"]) + float(prod_row["Carré 2"]) + float(prod_row["Carré 3"]) + float(prod_row["Carré 4"])) / 4
        densite_calculee = int(moyenne_carre * 100)
    except Exception:
        densite_calculee = 1200 # Sécurité si mauvaise manipulation de la structure de l'indicateur

    st.metric(label="🌲 Densité Moyenne Estimée Calculée par Leila", value=f"{densite_calculee} pieds / hectare", 
              delta=f"{densite_calculee - 1333} par rapport à l'idéal (1333 pieds/ha)", delta_color="inverse")
    
    # Sauvegarde de la densité calculée
    st.session_state["p13_densite_hectare"] = densite_calculee

    # --- COLLECTE DU RENDEMENT ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("#### 📦 Suivi de la Productivité Commerciale :")
    
    st.number_input(
        "Collecter les données de commercialisation avec le producteur sur au moins la dernière campagne (kg / ha) :",
        min_value=0,
        step=50,
        key="rendement_p13"
    )

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p13", type="primary", use_container_width=True):
        st.session_state["page_13_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 14
        st.rerun()

    # --- NUMÉRO DE PAGE (13) ---
    st.write("<br><br>", unsafe_allow_html=True)
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>13</span>", unsafe_allow_html=True)



def dessiner_page_14_Determination_Densite():
    # --- STYLE CSS STANDARD REPRODUCTION & PRESTIGE LEILA ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-14 {
        background-color: #C6E0B4; /* Vert institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-14 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .formula-box { 
        background-color: #008080; 
        color: white; 
        padding: 22px; 
        border-radius: 8px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        height: 100%; 
    }
    .formula-title { font-weight: bold; font-size: 16px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .canvas-container-p14 { background-color: white; padding: 10px; border-radius: 8px; border: 2px solid #1ABC9C; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    /* Blocs d'informations clairs et scannables */
    .pouperee-level-1 { border-left: 5px solid #1ABC9C; background-color: #F8FBFB; padding: 15px; border-radius: 4px; margin-bottom: 15px; color: black; }
    .pouperee-level-2 { border-left: 5px solid #008080; background-color: #F4FBF9; padding: 15px; border-radius: 4px; margin-bottom: 15px; color: black; }
    .pouperee-level-3 { border-left: 5px solid #E0115F; background-color: #FFF5F7; padding: 15px; border-radius: 4px; color: black; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-14">
        <div class="bullet-titre-14">• Détermination de la densité</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # =========================================================================
    # PARTIE SUPÉRIEURE : RENDER SVG DIRECT & FORMULES MATHÉMATIQUES
    # =========================================================================
    col_gauche, col_droite = st.columns([0.50, 0.50])

    with col_gauche:
        st.markdown("<p style='font-weight:bold; color:#1A252F; margin-bottom:5px;'>Dispositif d'échantillonnage sur la parcelle :</p>", unsafe_allow_html=True)
        
        html_svg_securise = """
        <div class="canvas-container-p14" style="text-align: center;">
            <svg width="100%" height="260" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="display: block; margin: auto;">
                <defs>
                    <filter id="shadow_p14" x="-5%" y="-5%" width="110%" height="110%">
                        <feDropShadow dx="2" dy="2" stdDeviation="2" flood-opacity="0.15"/>
                    </filter>
                </defs>
                <path d="M 90,40 C 180,20 280,30 310,80 C 340,130 290,200 310,250 C 320,270 260,290 190,275 C 120,260 70,240 65,190 C 60,140 40,70 90,40 Z" fill="#F2FDFB" stroke="#4D79FF" stroke-width="3" filter="url(#shadow_p14)" />
                <line x1="85" y1="45" x2="285" y2="265" stroke="#2C3E50" stroke-width="2.5" />
                <g transform="translate(90, 50) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="-25" y="4" font-size="11" fill="#1A252F" font-weight="bold">C1</text>
                </g>
                <g transform="translate(130, 95) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="-25" y="4" font-size="11" fill="#1A252F">C2</text>
                </g>
                <g transform="translate(175, 145) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="-25" y="4" font-size="11" fill="#1A252F">C3</text>
                </g>
                <g transform="translate(225, 200) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                </g>
                <g transform="translate(265, 245) rotate(35)">
                    <rect x="-18" y="-18" width="36" height="36" fill="none" stroke="#2C3E50" stroke-width="1.5" />
                    <circle cx="0" cy="0" r="3" fill="#8E44AD" />
                    <text x="24" y="4" font-size="11" fill="#1A252F" font-weight="bold">Cn</text>
                </g>
                <text x="200" y="285" font-size="12" fill="#7F8C8D" font-weight="bold" text-anchor="middle">Méthode des carrés en diagonale (10m × 10m)</text>
            </svg>
        </div>
        """
        st.markdown(html_svg_securise, unsafe_allow_html=True)

    with col_droite:
        st.markdown("""
        <div class="formula-box">
            <div class="formula-title">🧮 Équations de Densité Étalon</div>
        """, unsafe_allow_html=True)
        st.write(r"$$\text{Moyenne par carré} = \frac{\sum \text{Cacaoyers Comptés}}{n \text{ (Nombre de carrés)}}$$")
        st.write(r"$$\text{Densité Moyenne Extrapolée} = \text{Moyenne} \times 100 \text{ (pieds/ha)}$$")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")

    # =========================================================================
    # CONFIGURATION & PERSISTANCE DU SESSION STATE
    # =========================================================================
    if "p14_nb_carres" not in st.session_state:
        st.session_state.p14_nb_carres = 4  # Standard recommandé en Côte d'Ivoire

    if "p14_valeurs_cacaoyers" not in st.session_state:
        st.session_state.p14_valeurs_cacaoyers = {f"cac_{i}": (12 if i % 2 == 0 else 13) for i in range(20)}
    if "p14_valeurs_tiges" not in st.session_state:
        st.session_state.p14_valeurs_tiges = {f"tig_{i}": 1.1 for i in range(20)}

    # --- ÉTAPE 1 : CONFIGURATION ---
    st.markdown("### 🎛️ ÉTAPE 1 : Configuration & Saisie des Données de Terrain")
    with st.container():
        st.markdown('<div class="pouperee-level-1">', unsafe_allow_html=True)
        
        nb_carres = st.number_input(
            "Nombre de carrés d'observation installés (n) :", 
            min_value=1, max_value=20, 
            value=int(st.session_state.p14_nb_carres), 
            key="nb_carres_p14_root"
        )
        st.session_state.p14_nb_carres = nb_carres
        
        st.markdown("##### 📏 Pieds et tiges comptés par zone carrée :")
        
        cols_saisie = st.columns(int(nb_carres))
        cacaoyers_par_carre = []
        tiges_par_carre = []
        
        for idx in range(int(nb_carres)):
            with cols_saisie[idx]:
                key_cac = f"cac_{idx}"
                key_tig = f"tig_{idx}"
                
                val_cac = st.number_input(
                    f"Cacaoyers C{idx+1}", 
                    min_value=0, 
                    value=st.session_state.p14_valeurs_cacaoyers.get(key_cac, 12),
                    key=f"p14_input_{key_cac}"
                )
                val_tig = st.number_input(
                    f"Tiges/Pied C{idx+1}", 
                    min_value=1.0, max_value=5.0, 
                    value=st.session_state.p14_valeurs_tiges.get(key_tig, 1.1), 
                    step=0.1,
                    key=f"p14_input_{key_tig}"
                )
                
                st.session_state.p14_valeurs_cacaoyers[key_cac] = val_cac
                st.session_state.p14_valeurs_tiges[key_tig] = val_tig
                
                cacaoyers_par_carre.append(val_cac)
                tiges_par_carre.append(val_tig)
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ÉTAPE 2 : RENDU VISUEL DU TABLEAU COMPILÉ ---
    st.markdown("### 📊 ÉTAPE 2 : Rendu Visuel du Tableau Récapitulatif")
    with st.container():
        st.markdown('<div class="pouperee-level-2">', unsafe_allow_html=True)
        
        dict_recap = {"Indicateur": ["Nombre cacaoyers", "Nb moyen de tiges/cacaoyer"]}
        for i in range(len(cacaoyers_par_carre)):
            dict_recap[f"Carré {i+1}"] = [cacaoyers_par_carre[i], tiges_par_carre[i]]
            
        df_recap = pd.DataFrame(dict_recap)
        # CORRECTION : use_container_width=True remplace l'ancien paramètre instable width="stretch"
        st.dataframe(df_recap.set_index("Indicateur"), use_container_width=True) 
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ÉTAPE 3 : ANALYSE & CRITÈRES DU SYSTÈME EXPERT LEILA IA ---
    st.markdown("### 🧠 ÉTAPE 3 : Analyse & Rapport d'Expert de Leila IA")
    with st.container():
        st.markdown('<div class="pouperee-level-3">', unsafe_allow_html=True)
        
        total_cacaoyers = sum(cacaoyers_par_carre)
        moyenne_pieds_carre = total_cacaoyers / nb_carres if nb_carres > 0 else 0
        densite_calculee = moyenne_pieds_carre * 100
        moyenne_tiges = sum(tiges_par_carre) / nb_carres if nb_carres > 0 else 0
        
        c_res1, c_res2, c_res3 = st.columns(3)
        with c_res1:
            st.metric("Total Cacaoyers Observés", f"{total_cacaoyers} pieds")
        with c_res2:
            st.metric("Moyenne par Carré (100m²)", f"{moyenne_pieds_carre:.2f} pieds")
        with c_res3:
            st.metric("Densité Estimée à l'Hectare", f"{int(densite_calculee)} pieds/ha")

        st.write("")
        st.markdown("**⚡ Rapport de diagnostic agronomique automatique :**")
        
        st.session_state["p14_densite_calculee"] = int(densite_calculee)
        st.session_state["p14_moyenne_tiges"] = moyenne_tiges

        # Grille réglementaire d'interprétation ARS 1000
        if densite_calculee < 1000:
            st.error(f"⚠️ **Sous-densité critique détectée ({int(densite_calculee)} pieds/ha) :** La parcelle est très peu dense par rapport aux recommandations de la norme ARS 1000 (cible : 1111 à 1333 pieds/ha). Leila recommande d'envisager un plan de recépage ou un regarnissage rigoureux des espaces vides.")
            st.session_state["p14_etat_peuplement"] = "Sous-population Critique"
        elif 1000 <= densite_calculee <= 1400:
            st.success(f"✅ **Densité Optimale ({int(densite_calculee)} pieds/ha) :** Excellente configuration spatiale conforme aux exigences techniques du Manuel du Planteur. L'ombrage et la circulation de l'air sont optimisés pour limiter le Swollen Shoot.")
            st.session_state["p14_etat_peuplement"] = "Optimale"
        else:
            st.warning(f"⚠️ **Sur-densité détectée ({int(densite_calculee)} pieds/ha) :** Compétition hydrique et nutritionnelle élevée entre les cacaoyers. Risque d'augmentation du taux d'humidité favorisant la pourriture brune. Leila suggère un élagage ciblé.")
            st.session_state["p14_etat_peuplement"] = "Sur-population / Compétition Haute"

        if moyenne_tiges > 1.2:
            st.info(f"⚠️ **Alerte Architecture ({moyenne_tiges:.2f} tiges/pied) :** Présence trop élevée d'axes multiples (gourmands verticaux). Leila préconise un planning urgent d'égourmandage pour concentrer la sève vers la fructification.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p14", type="primary", use_container_width=True):
        st.session_state["page_14_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 15
        st.rerun()

    # --- PIED DE PAGE ---
    st.write("---")
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>14</span>", unsafe_allow_html=True)


def dessiner_page_15_Degradation_Arbres():
    # 1. Configuration du Design Général Conforme à la Charte Applicative
    st.markdown("""
    <style>
    .stApp {
        background-color: white; /* Changé pour harmonisation de l'application */
    }
    .diapo-slide-15 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-15 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .content-box-p15 {
        background-color: #F8FBFB;
        padding: 30px;
        border-radius: 8px;
        border-left: 5px solid #16A085;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 10px;
        font-family: 'Arial', sans-serif;
    }
    .main-title-p15 {
        color: #1A252F;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 25px;
        line-height: 1.4;
    }
    .bullet-list-p15 {
        list-style-type: square;
        padding-left: 20px;
    }
    .bullet-item-p15 {
        color: #2C3E50;
        font-size: 15px;
        margin-bottom: 20px;
        line-height: 1.6;
    }
    .highlight-red {
        color: #DC3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE (Harmonisation des Titres Institutionnels) ---
    st.markdown("""
    <div class="diapo-slide-15">
        <div class="bullet-titre-15">• Critères de dégradation des arbres</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Structure textuelle réglementaire exacte
    st.markdown("""
    <div class="content-box-p15">
        <div class="main-title-p15">
            Les arbres considérés comme dégradés et non productifs sont ceux ayant les caractéristiques suivantes :
        </div>
        <ul class="bullet-list-p15">
            <li class="bullet-item-p15">
                La frondaison est ouverte et si dégradée qu'aucune action <span class="highlight-red">technique ne peut permettre</span> de la corriger ;
            </li>
            <li class="bullet-item-p15">
                L'attaque de loranthus (plantes parasites) est si forte qu'aucune taille ne permet de redonner de la vigueur aux arbres ;
            </li>
            <li class="bullet-item-p15">
                Le tronc est si dégradé que l'arbre n'a plus la possibilité de porter des cabosses ;
            </li>
            <li class="bullet-item-p15">
                Les arbres chétifs ne pouvant plus produire des cabosses.
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p15", type="primary", use_container_width=True):
        st.session_state["page_15_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 16
        st.rerun()

    # 3. Pied de page avec le Numéro de Slide 15 exact et harmonisé
    st.write("<br>", unsafe_allow_html=True)
    _, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>15</span>", unsafe_allow_html=True)



def dessiner_page_16_Etat_Cacaoyere_Strict():
    st.markdown("""
    <style>
    .stApp { background-color: #E8F8F5; }
    .main-title-p16 { color: #1A252F; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; margin-left: 20px; }
    .sub-title-p16 { color: #1F4E78; font-size: 18px; font-weight: bold; margin-left: 20px; margin-bottom: 15px; }
    .badge-p16 { background-color: #008080; color: white; padding: 4px 10px; font-weight: bold; border-radius: 4px; display: inline-block; font-size: 14px; }
    
    /* Structure en poupées russes */
    .pouperee-p16-l1 { border-left: 5px solid #1ABC9C; background-color: #FFFFFF; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p16-l2 { border-left: 5px solid #1F4E78; background-color: #F4FBF9; padding: 15px; border-radius: 4px; margin-bottom: 15px; }
    .pouperee-p16-l3 { border-left: 5px solid #E0115F; background-color: #FFF5F7; padding: 15px; border-radius: 4px; }
    
    /* Cartes de diagnostic */
    .diagnostic-critique { background-color: #F8D7DA; color: #721C24; padding: 10px; border-radius: 4px; border-left: 4px solid #DC3545; margin-bottom: 8px; }
    .diagnostic-warning { background-color: #FFF3CD; color: #856404; padding: 10px; border-radius: 4px; border-left: 4px solid #FFC107; margin-bottom: 8px; }
    .diagnostic-ok { background-color: #D4EDDA; color: #155724; padding: 10px; border-radius: 4px; border-left: 4px solid #28A745; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p16">• Etat de la cacaoyère</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title-p16">⮚ Etat végétatif et sanitaire des cacaoyers (<span class="badge-p16">Fiche 3</span>)</div>', unsafe_allow_html=True)

    st.info("💡 **Questions directrices de l'évaluation :**\n"
            "* *Etat de dégradation des cacaoyers*\n"
            "* *Y a-t-il des attaques prononcées ou non de maladies ou ravageurs ?*")

    st.write("---")

    # =========================================================================
    # BANQUE DE DONNÉES DES CHOIX MULTIPLES PAR STRATE DE SÉVÉRITÉ
    # =========================================================================
    bibliotheque_layla = {
        "Mirides": {
            "1. Aucun": ["Aucune piqûre visible sur capsules ou jeunes pousses.", "Parcelle saine, absence totale de grilles de mirides.", "Feuillage et rameaux intacts, pas d'activité d'insectes.", "Structure des jeunes branches parfaitement saine.", "Aucun symptôme de dessèchement lié aux piqueurs-suceurs."],
            "2. Faible": ["Quelques grilles diffuses sur les rameaux terminaux.", "Présence isolée de piqûres sur de rares cabosses.", "Légers chancres de mirides localisés sur vieux bois.", "Attaque mineure concentrée en bordure de parcelle.", "Premiers signes de piqûres sans impact sur le rendement.", "Traces de passages anciens sans insectes actifs observés."],
            "3. Moyen": ["Dessèchement partiel de la cime (balais de sorcière).", "Chutes de feuilles significatives sur les branches hautes.", "Présence active de populations de mirides dans les zones ombragées.", "Plusieurs cabosses marquées entraînant des pertes locales.", "Chancres multiples bloquant partiellement la sève.", "Dessèchement de quelques apex terminaux."],
            "4. Fort": ["Cimes fortement calcinées, fortes pertes de sève.", "Dessèchement généralisé de la couronne des cacaoyers.", "Attaque massive destructrice sur les jeunes plantations.", "Chute totale des feuilles sur les arbres touchés.", "Parcelle sévèrement impactée, risque de perte d'arbres.", "Chancres profonds généralisés sur toute la structure."]
        },
        "Pourriture Brune": {
            "1. Aucun": ["Cabosses saines, aucune tache chocolat détectée.", "Absence complète de symptômes de Phytophthora.", "Fruits vigoureux sans nécrose sur toute la parcelle.", "Conditions saines, aucun foyer fongique repéré.", "Parcelle propre, cabosses en parfait état sanitaire."],
            "2. Faible": ["Attaque localisée sur de rares cabosses de bas-tronc.", "Petites taches bruises isolées à la pointe de quelques fruits.", "Début d'infection favorisé par une herbe légèrement haute.", "Attaque discrète n'impactant pas encore les fèves.", "Quelques fruits touchés près du sol uniquement.", "Symptômes initiaux stoppés par le retour du soleil."],
            "3. Moyen": ["Infection visible à hauteur d'homme, pertes modérées.", "Propagation du champignon sur plusieurs arbres voisins.", "Taches chocolat couvrant plus de la moitié de plusieurs cabosses.", "Pertes de récolte notables sur les branches intermédiaires.", "Feutrage blanc (spores) visible sur les fruits infectés.", "Infection active en progression due à l'humidité ambiante."],
            "4. Fort": ["Momification généralisée, forte pression fongique.", "Totalité des cabosses d'un même arbre complètement noires.", "Pourriture interne complète des fèves sur de nombreux arbres.", "Perte économique majeure imminente sur la récolte en cours.", "Infection invasive touchant toutes les strates du cacaoyer.", "Destruction massive des fruits suite à des pluies continues."]
        },
        "Épiphytes": {
            "1. Aucun": ["Troncs propres, pas de mousses parasites encombrantes.", "Absence totale de plantes épiphytes.", "Écorce saine et dégagée.", "Zéro encombrement végétal sur le tronc.", "Parcelle parfaitement entretenue au niveau du vieux bois."],
            "2. Faible": ["Légère présence de mousses ou lichens sur le vieux bois.", "Présence discrète sans étouffement des branches.", "Quelques lichens grisâtres sur les troncs ombragés.", "Mousses superficielles faciles à brosser.", "Début d'installation dans les fourches basses."],
            "3. Moyen": ["Fougères et mousses envahissant les fourches principales.", "Colonisation des axes porteurs de cabosses.", "Épiphytes denses réduisant la visibilité des fleurs.", "Humidité résiduelle élevée maintenue sur l'écorce.", "Présence de fougères de taille moyenne sur le tronc."],
            "4. Fort": ["Asphyxie végétative par surpopulation d'épiphytes.", "Troncs et branches totalement dissimulés sous la mousse.", "Poids excessif brisant les petites branches.", "Humidité permanente provoquant des nécroses cutanées.", "Prolifération invasive bloquant l'accès à la lumière."]
        },
        "Foreurs": {
            "1. Aucun": ["Aucune galerie ni rejet de sciure sur les troncs.", "Absence de perforations dues aux insectes xylophages.", "Tiges et branches vigoureuses sans dommages internes.", "Zéro activité de foreurs détectée.", "Bois sain sans perforation."],
            "2. Faible": ["Présence isolée de trous de pénétration sur vieilles branches.", "Rares rejets de sciure fine au pied d'un arbre.", "Attaque superficielle sur bois sec.", "Une à deux galeries mineures sans gravité apparente.", "Traces anciennes cicatrisées."],
            "3. Moyen": ["Galeriage actif avec présence de sciure fraîche.", "Perforations multiples sur les branches de production.", "Flétrissement de quelques rameaux terminaux minés.", "Écoulement de sève au niveau des points d'entrée.", "Activité manifeste de larves foreuses."],
            "4. Fort": ["Rameaux et axes majeurs cassants dus aux galeries internes.", "Destruction structurelle du tronc principal.", "Mort de branches charpentières entières.", "Sciure abondante accumulée aux bases des arbres.", "Risque d'effondrement ou de perte totale du cacaoyer."]
        },
        "CSSVD": {
            "1. Aucun": ["Feuillage normal, aucun symptôme suspect.", "Absence complète de signes du Swollen Shoot.", "Rameaux cylindriques et sains.", "Feuilles bien vertes, pas de décoloration atypique.", "Parcelle indemne de toute suspicion virale."],
            "2. Faible": ["Légère décoloration des nervures (feuilles en mosaïque).", "Rougeur suspecte sur les jeunes feuilles.", "Début de déformation foliaire isolée.", "Symptômes mineurs localisés sur un seul arbre.", "Suspicion à surveiller lors des prochains passages."],
            "3. Moyen": ["Gonflement visible sur quelques rameaux ou entre-nœuds.", "Mosaïque foliaire prononcée et généralisée sur un foyer.", "Ralentissement visible de la croissance de l'arbre.", "Gonflement caractéristique en forme de massue.", "Présence de cochenilles vectrices à proximité."],
            "4. Fort": ["Dépérissement progressif et mort de la structure de l'arbre.", "Défoliation massive et mort des extrémités des branches.", "Foyer d'infection étendu à plusieurs arbres adjacents.", "Perte de vigueur totale, arrêt de production.", "Destruction irréversible du squelette du cacaoyer."]
        },
        "Gourmands": {
            "1. Aucun": ["Troncs propres, entretien et regetonnage parfaits.", "Zéro gourmand sur l'axe principal.", "Toillettage rigoureux effectué récemment.", "Énergie de l'arbre concentrée sur la couronne.", "Architecture idéale du cacaoyer."],
            "2. Faible": ["Quelques jeunes gourmands fins à la base du tronc.", "Présence discrète de rejets herbacés.", "Gourmands de petite taille faciles à éliminer à la main.", "Début de repousse sans gêne pour la récolte.", "Entretien mineur à planifier."],
            "3. Moyen": ["Gourmands vigoureux entrant en compétition avec la couronne.", "Rejets lignifiés colonisant le tronc principal.", "Diminution de la pénétration de la lumière sous le couvert.", "Gourmands captant une part importante de la sève.", "Accès aux cabosses de tronc rendu difficile."],
            "4. Fort": ["Cacaoyers buissonnants, gourmands bloquant la lumière.", "Asphyxie complète de la couronne d'origine par les rejets.", "Perte drastique de rendement sur les branches principales.", "Parcelle non rejetonnée depuis de longs mois.", "Transformation du cacaoyer en buisson inextricable."]
        },
        "Cabosses momifiées": {
            "1. Aucun": ["Parcelle propre, résidus de récolte bien nettoyés.", "Absence de fruits momifiés sur les arbres.", "Aucun réservoir de spores de la saison passée.", "Hygiène de la cacaoyère impeccable.", "Zéro source d'inoculum résiduelle."],
            "2. Faible": ["Rares vieilles cabosses noires restées sur l'arbre.", "Présence isolée de fruits secs oubliés en hauteur.", "Impact négligeable à éliminer au prochain passage.", "Momies sporadiques sans contagion active.", "Quelques restes de récolte précédente."],
            "3. Moyen": ["Plusieurs cabosses sèches non récoltées, réservoirs d'inoculum.", "Fruits noirs desséchés fixés aux branches principales.", "Risque accru de propagation des maladies fongiques.", "Oubli manifeste lors des récoltes sanitaires.", "Momies servant de refuge à certains insectes."],
            "4. Fort": ["Accumulation critique de momies sur les branches.", "Arbres chargés de vieux fruits noirs desséchés.", "Source massive d'infection pour les nouvelles fleurs.", "Négligence sanitaire complète sur la parcelle.", "Pression parasitaire et fongique entretenue par les momies."]
        },
        "Loranthus": {
            "1. Aucun": ["Aucun plant de Loranthus (gui) détecté.", "Parcelle totalement exempte de plantes parasites.", "Branches saines sans fixation de Loranthus.", "Aucune concurrence sur la canopée.", "Zéro infestation."],
            "2. Faible": ["Une ou deux touffes isolées sur les branches hautes.", "Début d'installation du gui de cacaoyer.", "Parasitisme discret facile à élaguer.", "Présence localisée sur de vieux arbres.", "Impact physiologique minime pour le moment."],
            "3. Moyen": ["Parasitisme marqué provoquant le dessèchement de l'axe infesté.", "Plusieurs touffes vigoureuses installées dans la couronne.", "Perte de vigueur des branches situées au-dessus du parasite.", "Compétition sévère pour l'eau et les minéraux.", "Nécessité d'une intervention d'échenillage."],
            "4. Fort": ["Envahissement sévère, dépérissement des houppiers.", "Loranthus dominant la majorité de la canopée du cacaoyer.", "Mort programmée des branches charpentières.", "Chute drastique de la production de la parcelle.", "Infestation massive étouffant littéralement les arbres."]
        },
        "Enherbement": {
            "1. Aucun": ["Sol propre ou paillé, enherbement nul sous le couvert.", "Sous-bois totalement dégagé sous l'ombrage.", "Excellent contrôle des adventices.", "Circulation fluide sur toute la parcelle.", "Conditions idéales pour la récolte."],
            "2. Faible": ["Couvert herbeux ras, adventices sous contrôle.", "Tapis vert minime ne concurrençant pas les cacaoyers.", "Sarclage récent encore efficace.", "Légère pousse d'herbes non agressives.", "Sol bien entretenu."],
            "3. Moyen": ["Hauteur des adventices gênant la circulation sur la ligne.", "Herbes hautes entrant en concurrence pour l'azote du sol.", "Humidité stagnante favorisée au pied des arbres.", "Difficulté à repérer les cabosses tombées.", "Besoin urgent de réaliser un faucardage ou sarclage."],
            "4. Fort": ["Enherbement sauvage agressif, compétition nutritionnelle intense.", "Envahissement par des lianes ou des plantes arbustives.", "Accès à la parcelle bloqué par la végétation spontanée.", "Asphyxie des jeunes plants de cacaoyer.", "Foyer d'infestation pour les rongeurs et insectes."]
        },
        "Rien à signaler": {
            "1. Aucun": ["Aucune autre anomalie constatée sur la parcelle.", "Parcelle parfaitement conforme aux standards.", "Pas d'autres facteurs de stress identifiés."],
            "2. Faible": ["Rien à signaler d'anormal."], "3. Moyen": ["Rien à signaler d'anormal."], "4. Fort": ["Rien à signaler d'anormal."]
        },
        "Rongeurs / Écureuils": {
            "1. Aucun": ["Aucune morsure de rongeur détectée sur les cabosses.", "Faune locale en équilibre, pas de dégâts économiques.", "Cabosses de tronc intactes."],
            "2. Faible": ["Quelques rares cabosses grignotées au sol.", "Traces de dents superficielles sur une ou deux écorces.", "Pertes très isolées sans urgence de piégeage."],
            "3. Moyen": ["Attaque régulière sur les cabosses mûres à mi-hauteur.", "Pertes de fèves visibles sur plusieurs arbres du même alignement.", "Nécessité de réguler ou d'avancer la récolte."],
            "4. Fort": ["Ravages systématiques, forte proportion de cabosses vidées.", "Écureuils ou rats omniprésents détruisant la récolte utile.", "Urgence d'une stratégie de lutte ou de piégeage biologique."]
        },
        "Trachéomycose (Vascular Dieback)": {
            "1. Aucun": ["Aucun symptôme de dépérissement vasculaire repéré.", "Feuillage vigoureux, vaisseaux conducteurs sains."],
            "2. Faible": ["Jaunissement isolé de quelques feuilles sur une branche.", "Premiers signes de flétrissement sans blocage majeur de sève."],
            "3. Moyen": ["Dessèchement net d'un rameau entier avec persistance des feuilles mortes.", "Brunissement des tissus conducteurs internes après test au couteau."],
            "4. Fort": ["Dépérissement brutal et mort de branches charpentières entières.", "Blocage total des flux nutritionnels, arbre condamné à court terme."]
        },
        "Psylles / Chenilles défoliatrices": {
            "1. Aucun": ["Jeunes pousses saines, aucun insecte défoliateur actif.", "Bourgeons terminaux intacts."],
            "2. Faible": ["Quelques feuilles perforées ou enroulées sur les rejets.", "Présence discrète de chenilles sans ralentissement de croissance."],
            "3. Moyen": ["Attaque visible sur les flushes (jeunes poussées de feuilles).", "Déformation des bourgeons terminaux par les attaques de psylles."],
            "4. Fort": ["Destruction systématique des jeunes bourgeons (blocage du flush).", "Défoliation sévère des jeunes plants mettant en péril leur survie."]
        },
        "Stress Hydrique / Coup de soleil": {
            "1. Aucun": ["Ombrage optimal, humidité interne de l'arbre stable.", "Feuilles bien orientées."],
            "2. Faible": ["Léger flétrissement des pointes de feuilles aux heures chaudes.", "Ombrage un peu clairsemé par endroits."],
            "3. Moyen": ["Chute de feuilles vertes à cause de la sécheresse prolongée.", "Brûlures marginales nettes (dessèchement du limbe) dues à l'ensoleillement direct."],
            "4. Fort": ["Défoliation massive due au stress hydrique sévère.", "Dessèchement des extrémités, risque de mort par rupture de la canopée."]
        }
    }

    severites_options = ["1. Aucun", "2. Faible", "3. Moyen", "4. Fort"]
    liste_autres_anomalies = ["Rien à signaler", "Rongeurs / Écureuils", "Trachéomycose (Vascular Dieback)", "Psylles / Chenilles défoliatrices", "Stress Hydrique / Coup de soleil"]

    # =========================================================================
    # 🔐 PERSISTANCE ET INITIALISATION STRUCTURÉE DU SESSION STATE
    # =========================================================================
    cles_initialisation = {
        "p16_s_mir": "1. Aucun", "p16_o_mir": bibliotheque_layla["Mirides"]["1. Aucun"][0],
        "p16_s_pbr": "1. Aucun", "p16_o_pbr": bibliotheque_layla["Pourriture Brune"]["1. Aucun"][0],
        "p16_s_epi": "1. Aucun", "p16_o_epi": bibliotheque_layla["Épiphytes"]["1. Aucun"][0],
        "p16_s_for": "1. Aucun", "p16_o_for": bibliotheque_layla["Foreurs"]["1. Aucun"][0],
        "p16_s_css": "1. Aucun", "p16_o_css": bibliotheque_layla["CSSVD"]["1. Aucun"][0],
        "p16_type_aut": "Rien à signaler",
        "p16_s_aut": "1. Aucun", "p16_o_aut": bibliotheque_layla["Rien à signaler"]["1. Aucun"][0],
        "p16_v_gou": "1. Aucun", "p16_o_gou": bibliotheque_layla["Gourmands"]["1. Aucun"][0],
        "p16_v_mom": "1. Aucun", "p16_o_mom": bibliotheque_layla["Cabosses momifiées"]["1. Aucun"][0],
        "p16_v_lor": "1. Aucun", "p16_o_lor": bibliotheque_layla["Loranthus"]["1. Aucun"][0],
        "p16_v_enh": "1. Aucun", "p16_o_enh": bibliotheque_layla["Enherbement"]["1. Aucun"][0],
    }

    for cle, defaut in cles_initialisation.items():
        if cle not in st.session_state:
            st.session_state[cle] = defaut

    # Helper pour trouver l'index de sécurité lors du rechargement
    def obtenir_index(liste, cle_state):
        valeur = st.session_state[cle_state]
        return liste.index(valeur) if valeur in liste else 0

    # =========================================================================
    # LE SYSTÈME EXPERT EN ACTION
    # =========================================================================
    
    # 🪆 Poupée 1 : Saisie de Terrain segmentée
    with st.expander("🪆 ÉTAPE 1 : Évaluation des indicateurs phytosanitaires", expanded=True):
        st.markdown('<div class="pouperee-p16-l1">', unsafe_allow_html=True)
        
        col_tab1, col_tab2 = st.columns(2)
        
        with col_tab1:
            st.markdown("##### 🪲 Section A : Maladies & Ravageurs")
            
            # Attaque Mirides
            c1, c2 = st.columns([1.2, 2.8])
            sev_mirides = c1.selectbox("Sévérité Mirides", severites_options, index=obtenir_index(severites_options, "p16_s_mir"), key="p16_s_mir")
            # Sécurité si la sévérité change pour éviter le crash d'index hors-limite
            liste_obs_mir = bibliotheque_layla["Mirides"][sev_mirides]
            obs_mirides = c2.selectbox("Observation Mirides (Choix Layla)", liste_obs_mir, index=obtenir_index(liste_obs_mir, "p16_o_mir"), key="p16_o_mir")
            
            # Pourriture Brune
            c1, c2 = st.columns([1.2, 2.8])
            sev_pbrune = c1.selectbox("Sévérité Pourriture Brune", severites_options, index=obtenir_index(severites_options, "p16_s_pbr"), key="p16_s_pbr")
            liste_obs_pbr = bibliotheque_layla["Pourriture Brune"][sev_pbrune]
            obs_pbrune = c2.selectbox("Observation Pourriture Brune (Choix Layla)", liste_obs_pbr, index=obtenir_index(liste_obs_pbr, "p16_o_pbr"), key="p16_o_pbr")
            
            # Épiphytes
            c1, c2 = st.columns([1.2, 2.8])
            sev_epiphytes = c1.selectbox("Présence Épiphytes", severites_options, index=obtenir_index(severites_options, "p16_s_epi"), key="p16_s_epi")
            liste_obs_epi = bibliotheque_layla["Épiphytes"][sev_epiphytes]
            obs_epiphytes = c2.selectbox("Observation Épiphytes (Choix Layla)", liste_obs_epi, index=obtenir_index(liste_obs_epi, "p16_o_epi"), key="p16_o_epi")
            
            # Foreurs
            c1, c2 = st.columns([1.2, 2.8])
            sev_foreurs = c1.selectbox("Attaque Foreurs", severites_options, index=obtenir_index(severites_options, "p16_s_for"), key="p16_s_for")
            liste_obs_for = bibliotheque_layla["Foreurs"][sev_foreurs]
            obs_foreurs = c2.selectbox("Observation Foreurs (Choix Layla)", liste_obs_for, index=obtenir_index(liste_obs_for, "p16_o_for"), key="p16_o_for")
            
            # CSSVD (Swollen Shoot)
            c1, c2 = st.columns([1.2, 2.8])
            sev_cssvd = c1.selectbox("Attaque CSSVD", severites_options, index=obtenir_index(severites_options, "p16_s_css"), key="p16_s_css")
            liste_obs_css = bibliotheque_layla["CSSVD"][sev_cssvd]
            obs_cssvd = c2.selectbox("Observation CSSVD (Choix Layla)", liste_obs_css, index=obtenir_index(liste_obs_css, "p16_o_css"), key="p16_o_css")
            
            # ---- GESTION INTELLIGENTE DU PARAMÈTRE "AUTRES" ----
            st.markdown("---")
            st.caption("🔍 **Diagnostic Complémentaire sur Choix Spécifique**")
            
            type_autre = st.selectbox("Type d'anomalie détectée", liste_autres_anomalies, index=obtenir_index(liste_autres_anomalies, "p16_type_aut"), key="p16_type_aut")
            
            c1, c2 = st.columns([1.2, 2.8])
            sev_autres = c1.selectbox("Sévérité Autre", severites_options, index=obtenir_index(severites_options, "p16_s_aut"), key="p16_s_aut")
            
            liste_obs_aut = bibliotheque_layla[type_autre][sev_autres]
            obs_autres = c2.selectbox(f"Observation {type_autre} (Choix Layla)", liste_obs_aut, index=obtenir_index(liste_obs_aut, "p16_o_aut"), key="p16_o_aut")

        with col_tab2:
            st.markdown("##### 🌿 Section B : Paramètres Végétatifs")
            
            # Gourmands
            c1, c2 = st.columns([1.2, 2.8])
            val_gourmands = c1.selectbox("Présence de gourmands", severites_options, index=obtenir_index(severites_options, "p16_v_gou"), key="p16_v_gou")
            liste_obs_gou = bibliotheque_layla["Gourmands"][val_gourmands]
            obs_gourmands = c2.selectbox("Observation Gourmands (Choix Layla)", liste_obs_gou, index=obtenir_index(liste_obs_gou, "p16_o_gou"), key="p16_o_gou")
            
            # Cabosses momifiées
            c1, c2 = st.columns([1.2, 2.8])
            val_momifiees = c1.selectbox("Cabosses momifiées", severites_options, index=obtenir_index(severites_options, "p16_v_mom"), key="p16_v_mom")
            liste_obs_mom = bibliotheque_layla["Cabosses momifiées"][val_momifiees]
            obs_momifiees = c2.selectbox("Observation Momifiées (Choix Layla)", liste_obs_mom, index=obtenir_index(liste_obs_mom, "p16_o_mom"), key="p16_o_mom")
            
            # Loranthus
            c1, c2 = st.columns([1.2, 2.8])
            val_loranthus = c1.selectbox("Présence de Loranthus", severites_options, index=obtenir_index(severites_options, "p16_v_lor"), key="p16_v_lor")
            liste_obs_lor = bibliotheque_layla["Loranthus"][val_loranthus]
            obs_loranthus = c2.selectbox("Observation Loranthus (Choix Layla)", liste_obs_lor, index=obtenir_index(liste_obs_lor, "p16_o_lor"), key="p16_o_lor")
            
            # Enherbement
            c1, c2 = st.columns([1.2, 2.8])
            val_enherbement = c1.selectbox("Niveau d'enherbement", severites_options, index=obtenir_index(severites_options, "p16_v_enh"), key="p16_v_enh")
            liste_obs_enh = bibliotheque_layla["Enherbement"][val_enherbement]
            obs_enherbement = c2.selectbox("Observation Enherbement (Choix Layla)", liste_obs_enh, index=obtenir_index(liste_obs_enh, "p16_o_enh"), key="p16_o_enh")

    st.markdown('</div>', unsafe_allow_html=True)

    # 🪆 Poupée 2 : Le Grand Tableau Restructuré (Mise à jour width="stretch" pour 2026)
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Tableau de Synthèse)", expanded=True):
        st.markdown('<div class="pouperee-p16-l2">', unsafe_allow_html=True)
        
        label_autre_affichage = f"Autre : {type_autre}" if type_autre != "Rien à signaler" else "Autres anomalies"
        
        data_tableau_p16 = {
            "Maladies/ravageurs": ["Attques de mirides", "Attaques de Pourriture Brune", "Présence de plantes épiphytes", "Attaque Foreurs", "Attaque CSSVD", label_autre_affichage],
            "Sévérité": [sev_mirides, sev_pbrune, sev_epiphytes, sev_foreurs, sev_cssvd, sev_autres],
            "Observations (A)": [obs_mirides, obs_pbrune, obs_epiphytes, obs_foreurs, obs_cssvd, obs_autres],
            "Paramètres": ["Présence de gourmands", "Présence de cabosses momifiées", "Présence de loranthus", "Enherbement", "-", "-"],
            "Valeur": [val_gourmands, val_momifiees, val_loranthus, val_enherbement, "-", "-"],
            "Observations (B)": [obs_gourmands, obs_momifiees, obs_loranthus, obs_enherbement, "-", "-"]
        }
        
        df_p16 = pd.DataFrame(data_tableau_p16)
        st.dataframe(df_p16.set_index("Maladies/ravageurs"), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

        # 🪆 Poupée 3 : Moteur d'Avis Diagnostique de Layla
        with st.expander("🧠 ÉTAPE 3 : Matrice d'Arbitrage & Conseils de Layla", expanded=True):
            st.markdown('<div class="pouperee-p16-l3">', unsafe_allow_html=True)
            st.markdown("#### 💬 Alertes Décisionnelles de l'Expert")
            
            alertes_declenches = 0
            
            if "1. Aucun" not in sev_cssvd:
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-critique">
                    🚨 <strong>ALERTE CRITIQUE DE LAYLA (CSSVD / Swollen Shoot) :</strong> L'anomalie est signalée au niveau {sev_cssvd}. 
                    Conformément à la réglementation phytosanitaire en Côte d'Ivoire, l'éradication (arrachage des pieds atteints et des arbres contacts) est impérative pour freiner la progression du virus.
                </div>
                """, unsafe_allow_html=True)
            
            if "3. Moyen" in sev_autres and type_autre == "Trachéomycose (Vascular Dieback)" or "4. Fort" in sev_autres and type_autre == "Trachéomycose (Vascular Dieback)":
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-critique">
                    🍂 <strong>ALERTE PHYTOSANITAIRE DE LAYLA (Trachéomycose) :</strong> Niveau {sev_autres} détecté. 
                    Cette maladie vasculaire bloque la sève de manière irréversible. Couper et brûler immédiatement les branches atteintes en dessous de la zone brune pour protéger le reste de l'arbre.
                </div>
                """, unsafe_allow_html=True)

            if "3. Moyen" in sev_mirides or "4. Fort" in sev_mirides or "3. Moyen" in sev_foreurs or "4. Fort" in sev_foreurs:
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-warning">
                    🪲 <strong>ALERTE RAVAGEURS :</strong> Pression parasitaire trop élevée des insectes piqueurs-suceurs ou foreurs. 
                    Layla recommande de synchroniser un traitement de lutte intégrée (physique et chimique ciblée) avant la grande fuite de sève.
                </div>
                """, unsafe_allow_html=True)
                
            if ("4. Fort" in val_gourmands or "4. Fort" in val_enherbement or "3. Moyen" in val_loranthus or 
                "4. Fort" in val_loranthus or "3. Moyen" in sev_pbrune or "4. Fort" in sev_pbrune or 
                ("3. Moyen" in sev_autres or "4. Fort" in sev_autres) and type_autre in ["Rongeurs / Écureuils", "Stress Hydrique / Coup de soleil"]):
                alertes_declenches += 1
                st.markdown(f"""
                <div class="diagnostic-warning">
                    🌿 <strong>ALERTE MAINTENANCE AGRONOMIQUE & COMPLÉMENTS :</strong> L'état général montre un besoin de suivi.
                    Vérifier l'ombrage (si stress hydrique fort) ou intensifier le rythme des récoltes sanitaires (si pression des rongeurs ou Pourriture Brune).
                </div>
                """, unsafe_allow_html=True)

            if alertes_declenches == 0:
                st.markdown("""
                <div class="diagnostic-ok">
                    🟢 <strong>DIAGNOSTIC GLOBAL DE LAYLA :</strong> L'état végétatif et sanitaire général est maîtrisé. Les pressions parasitaires et fongiques restent sous le seuil d'intervention économique. Maintenir le protocole d'observation bimensuel.
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p16", type="primary", use_container_width=True):
        st.session_state["page_16_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 17
        st.rerun()

    # Numérotation réglementaire en bas à droite
    st.write("---")
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>16</span>", unsafe_allow_html=True)
