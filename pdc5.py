

def dessiner_page_21_Finance_Production():
    # --- CONFIGURATION DU DESIGN ET STRUCTURES EN POUPÉES RUSSES ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-21 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .bullet-titre-21 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-p21 { background-color: #1F4E78; color: white; padding: 6px 14px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 14px; }
    .section-title-p21 { color: #16A085; font-size: 18px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    
    /* Structure Box Poupées Russes */
    .pouperee-p21-l1 { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p21-l2 { border-left: 5px solid #2980B9; background-color: #F4F8FA; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p21-l3 { border-left: 5px solid #D35400; background-color: #FFFBF5; padding: 20px; border-radius: 6px; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #16A085; margin-top: 15px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-21">
        <div class="bullet-titre-21">❖ D - Données Socio-économiques (Fiche 4)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="badge-p21">💳 Compte d\'épargne, Financement & Revenus</div>', unsafe_allow_html=True)

    types_epargne = ["Mobile Money", "Microfinance", "Banque", "Autres"]
    annees_cacao = ["Année N-1", "Année N-2", "Année N-3"]

    # =========================================================================
    # 🔐 PERSISTANCE ET SÉCURISATION DES CLÉS MULTI-LIGNES DU SESSION STATE
    # =========================================================================
    for ep in types_epargne:
        cle_ep = ep.replace(" ", "_").lower()
        if f"p21_hc_{cle_ep}" not in st.session_state: st.session_state[f"p21_hc_{cle_ep}"] = "Non"
        if f"p21_ha_{cle_ep}" not in st.session_state: st.session_state[f"p21_ha_{cle_ep}"] = "Non"
        if f"p21_hf_{cle_ep}" not in st.session_state: st.session_state[f"p21_hf_{cle_ep}"] = "Non"
        if f"p21_mt_{cle_ep}" not in st.session_state: st.session_state[f"p21_mt_{cle_ep}"] = 0

    for an in annees_cacao:
        cle_an = an.replace(" ", "_").replace("-", "_").lower()
        if f"p21_prod_{cle_an}" not in st.session_state: st.session_state[f"p21_prod_{cle_an}"] = 0
        if f"p21_rev_{cle_an}" not in st.session_state: st.session_state[f"p21_rev_{cle_an}"] = 0

    for i in range(1, 3):
        if f"p21_act_n_{i}" not in st.session_state: st.session_state[f"p21_act_n_{i}"] = ""
        if f"p21_act_p_{i}" not in st.session_state: st.session_state[f"p21_act_p_{i}"] = ""
        if f"p21_act_r_{i}" not in st.session_state: st.session_state[f"p21_act_r_{i}"] = 0

    def obtenir_idx_radio(options, valeur_actuelle):
        return options.index(valeur_actuelle) if valeur_actuelle in options else 0

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des données financières et de production", expanded=True):
        st.markdown('<div class="pouperee-p21-l1">', unsafe_allow_html=True)
        
        # --- SOUS-SECTION 1 : COMPTE D'ÉPARGNE ET FINANCEMENT ---
        st.markdown('<div class="section-title-p21">❖ 1. Compte d\'épargne et Financement</div>', unsafe_allow_html=True)
        saisies_epargne = []
        options_radio = ["Non", "Oui"]
        
        for ep in types_epargne:
            cle_ep = ep.replace(" ", "_").lower()
            st.markdown(f"**Option d'Épargne : {ep}**")
            c_ep1, c_ep2, c_ep3, c_ep4 = st.columns([2.5, 2.5, 2.5, 2.5])
            
            with c_ep1: 
                has_compte = st.radio("Avez-vous un compte ?", options_radio, index=obtenir_idx_radio(options_radio, st.session_state[f"p21_hc_{cle_ep}"]), horizontal=True, key=f"p21_hc_{cle_ep}_input")
            
            with c_ep2: 
                if has_compte == "Oui":
                    has_argent = st.radio("Argent sur le compte ?", options_radio, index=obtenir_idx_radio(options_radio, st.session_state[f"p21_ha_{cle_ep}"]), horizontal=True, key=f"p21_ha_{cle_ep}_input")
                else:
                    st.text_input("Argent sur le compte ?", value="N/A", disabled=True, key=f"p21_ha_dis_{cle_ep}")
                    has_argent = "Non"
            
            with c_ep3: 
                has_finance = st.radio("Bénéficié de financement ?", options_radio, index=obtenir_idx_radio(options_radio, st.session_state[f"p21_hf_{cle_ep}"]), horizontal=True, key=f"p21_hf_{cle_ep}_input")
            
            with c_ep4: 
                if has_finance == "Oui":
                    montant_fin = st.number_input("Montant (FCFA)", min_value=0, step=5000, value=st.session_state[f"p21_mt_{cle_ep}"], key=f"p21_mt_{cle_ep}_input")
                else:
                    st.text_input("Montant (FCFA)", value="0", disabled=True, key=f"p21_mt_dis_{cle_ep}")
                    montant_fin = 0
            
            # Synchro Session State
            st.session_state[f"p21_hc_{cle_ep}"] = has_compte
            st.session_state[f"p21_ha_{cle_ep}"] = has_argent
            st.session_state[f"p21_hf_{cle_ep}"] = has_finance
            st.session_state[f"p21_mt_{cle_ep}"] = montant_fin

            saisies_epargne.append({
                "Type d'Épargne": ep,
                "Possède un compte": has_compte,
                "Solde positif (Argent disponible)": has_argent,
                "Financement obtenu": has_finance,
                "Montant du financement (FCFA)": montant_fin
            })
            
        st.write("---")

        # --- SOUS-SECTION 2 : PRODUCTION DE CACAO ---
        st.markdown('<div class="section-title-p21">❖ 2. Production de cacao des trois (3) dernières années</div>', unsafe_allow_html=True)
        saisies_production = []
        
        c_h1, c_h2, c_h3 = st.columns([3, 3, 4])
        with c_h2: st.markdown("<span style='font-size:13px; font-weight:bold; color:#7F8C8D;'>Production (kg)</span>", unsafe_allow_html=True)
        with c_h3: st.markdown("<span style='font-size:13px; font-weight:bold; color:#7F8C8D;'>Revenu brut (FCFA)</span>", unsafe_allow_html=True)

        for an in annees_cacao:
            cle_an = an.replace(" ", "_").replace("-", "_").lower()
            c_p1, c_p2, c_p3 = st.columns([3, 3, 4])
            with c_p1: 
                st.markdown(f"<div style='padding-top:10px; font-weight:bold; color:#2C3E50;'>{an} :</div>", unsafe_allow_html=True)
            with c_p2: 
                prod_kg = st.number_input(f"Production (kg) - {an}", min_value=0, step=50, value=st.session_state[f"p21_prod_{cle_an}"], label_visibility="collapsed", key=f"p21_prod_{cle_an}_input")
            with c_p3: 
                rev_brut = st.number_input(f"Revenu brut (FCFA) - {an}", min_value=0, step=25000, value=st.session_state[f"p21_rev_{cle_an}"], label_visibility="collapsed", key=f"p21_rev_{cle_an}_input")
            
            st.session_state[f"p21_prod_{cle_an}"] = prod_kg
            st.session_state[f"p21_rev_{cle_an}"] = rev_brut

            saisies_production.append({
                "ANNÉE": an,
                "Production (kg)": prod_kg,
                "Revenu brut (FCFA)": rev_brut
            })

        st.write("---")

        # --- SOUS-SECTION 3 : SOURCES DE REVENUS ALTERNATIVES ---
        st.markdown('<div class="section-title-p21">❖ 3. Sources de revenus autres que le cacao</div>', unsafe_allow_html=True)
        saisies_autres = []
        
        for i in range(1, 3):
            st.markdown(f"**Activité alternative N°{i}**")
            c_a1, c_a2, c_a3 = st.columns([4, 3, 3])
            with c_a1: 
                nom_act = st.text_input(f"Nom / Type de l'activité {i}", value=st.session_state[f"p21_act_n_{i}"], key=f"p21_act_n_{i}_input")
            with c_a2: 
                prod_act = st.text_input(f"Production moyenne annuelle {i}", placeholder="Ex: 500 régimes", value=st.session_state[f"p21_act_p_{i}"], key=f"p21_act_p_{i}_input")
            with c_a3: 
                rev_act = st.number_input(f"Revenu brut moyen/an (FCFA) {i}", min_value=0, step=10000, value=st.session_state[f"p21_act_r_{i}"], key=f"p21_act_r_{i}_input")
            
            st.session_state[f"p21_act_n_{i}"] = nom_act
            st.session_state[f"p21_act_p_{i}"] = prod_act
            st.session_state[f"p21_act_r_{i}"] = rev_act

            saisies_autres.append({
                "ACTIVITÉ": nom_act if nom_act.strip() != "" else f"Activité {i}",
                "Production moyenne annuelle": prod_act if prod_act.strip() != "" else "Non spécifiée",
                "Revenu brut moyen/an (FCFA)": rev_act
            })

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : MATRICE SYNOPTIQUE / SORTIE DES TABLEAUX (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visuel Tableaux)", expanded=True):
        st.markdown('<div class="pouperee-p21-l2">', unsafe_allow_html=True)
        
        st.markdown("##### 💳 Matrice de Suivi de l'Épargne et du Financement Agricole")
        df_epargne = pd.DataFrame(saisies_epargne)
        st.dataframe(df_epargne, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 📉 Évolution Triennale de la Production Cacaoyère")
        df_production = pd.DataFrame(saisies_production)
        st.dataframe(df_production, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 🌾 État des Flux de Revenus de Diversification")
        df_autres = pd.DataFrame(saisies_autres)
        st.dataframe(df_autres, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA IA EXPERT / AVIS (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Rapport d'Analyse et Avis Experts de Leila IA", expanded=True):
        st.markdown('<div class="pouperee-p21-l3">', unsafe_allow_html=True)
        
        # --- LEILA : ANALYSE FINANCIÈRE & BANCARISATION ---
        st.markdown('<div class="subsection-analysis-title">💳 Bancarisation & Capacité de Financement (Leila IA)</div>', unsafe_allow_html=True)
        comptes_actifs = [r["Type d'Épargne"] for r in saisies_epargne if r["Possède un compte"] == "Oui"]
        financements_recus = sum(r["Montant du financement (FCFA)"] for r in saisies_epargne)
        
        if len(comptes_actifs) == 0:
            st.error("🚨 **Alerte exclusion financière :** Le producteur ne possède aucun compte d'épargne (ni Mobile Money, ni banque). Cela bloque toute éligibilité au versement électronique des primes de durabilité et limite l'accès aux crédits de campagne.")
        else:
            comptes_str = ", ".join(comptes_actifs)
            st.success(f"🟢 **Profil d'inclusion validé :** Producteur connecté au réseau financier via : **{comptes_str}**.")
            
        if financements_recus > 0:
            st.info(f"💰 **Levier de crédit :** Un financement externe total de **{financements_recus:,.0f} FCFA** a été mobilisé. Assurez-vous que le calendrier de remboursement coïncide avec les pics des récoltes de la grande campagne.")
        else:
            st.warning("⚠️ **Absence de soutien financier :** Aucun financement externe enregistré. L'autofinancement total ralentit les capacités de régénération ou d'achat d'intrants homologués.")

        # --- LEILA : ANALYSE DES PERFORMANCES CACAO ---
        st.markdown('<div class="subsection-analysis-title">📉 Diagnostic de Productivité Cacaoyère (Leila IA)</div>', unsafe_allow_html=True)
        
        p_n1 = saisies_production[0]["Production (kg)"]
        p_n2 = saisies_production[1]["Production (kg)"]
        p_n3 = saisies_production[2]["Production (kg)"]
        
        r_n1 = saisies_production[0]["Revenu brut (FCFA)"]
        r_n2 = saisies_production[1]["Revenu brut (FCFA)"]
        r_n3 = saisies_production[2]["Revenu brut (FCFA)"]
        
        tous_revenus_cacao = [r_n1, r_n2, r_n3]
        revenus_valides = [r for r in tous_revenus_cacao if r > 0]
        
        if len(revenus_valides) > 0:
            revenu_moyen_cacao = sum(revenus_valides) / len(revenus_valides)
            st.success(f"💰 **Revenu annuel moyen (Cacao) :** {revenu_moyen_cacao:,.0f} FCFA.")
            
            # Analyse des tendances de rendement triennal (N-3 -> N-2 -> N-1)
            if p_n3 > p_n2 > p_n1 and p_n1 > 0:
                st.error("🚨 **Alerte de baisse continue de rendement :** La production chute d'année en d'année ! Leila IA conseille d'auditer d'urgence le taux de sénescence (vieillissement) du verger ou l'extension latente de foyers du Swollen Shoot.")
            elif p_n1 > p_n2 and p_n2 > 0:
                st.success("📈 **Dynamique de production positive :** Hausse des rendements constatée sur la dernière campagne. Maintenir l'itinéraire technique actuel.")
        else:
            st.info("💡 Complétez les données de production des campagnes pour activer les graphiques de performance de Leila IA.")

        # --- LEILA : ANALYSE DE LA DIVERSIFICATION DES REVENUS ---
        st.markdown('<div class="subsection-analysis-title">🌾 Résilience Économique et Diversification (Leila IA)</div>', unsafe_allow_html=True)
        revenu_annexe_total = sum(r["Revenu brut moyen/an (FCFA)"] for r in saisies_autres)
        
        if revenu_annexe_total == 0:
            st.warning("⚠️ **Dépendance exclusive (Monoculture) :** 100% du budget repose sur le cacao. Le ménage est hautement vulnérable aux fluctuations des cours mondiaux ou aux aléas climatiques locaux. Leila IA préconise vivement de développer des cultures vivrières de contre-saison (piment, gombo) ou du petit élevage.")
        else:
            st.success(f"🍏 **Diversification validée :** Les sources annexes génèrent **{revenu_annexe_total:,.0f} FCFA / an**. Cette stratégie sécurise les dépenses courantes en période de soudure cacaoyère.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p21", type="primary", use_container_width=True):
        st.session_state["page_21_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 22
        st.rerun()

    # --- PIED DE PAGE ET PAGINATION REGLEMENTAIRE HARMONISÉE A 21 ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>21</span>", unsafe_allow_html=True)



def dessiner_page_22_Depenses_Et_Main_Doeuvre():
    # --- 1. CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-22 {
        background-color: #C6E0B4; /* Vert institutionnel standardisé */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    .main-title-p22 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-p22 { background-color: #1F4E78; color: white; padding: 6px 14px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 14px; }
    .section-title-p22 { color: #16A085; font-size: 18px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; }
    
    /* Structure Box Poupées Russes */
    .pouperee-p22-l1 { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p22-l2 { border-left: 5px solid #2980B9; background-color: #F4F8FA; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    .pouperee-p22-l3 { border-left: 5px solid #D35400; background-color: #FFFBF5; padding: 20px; border-radius: 6px; }
    
    .subsection-analysis-title { font-size: 15px; font-weight: bold; color: #16A085; margin-top: 15px; margin-bottom: 12px; border-bottom: 1px dashed #BDC3C7; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-22">
        <div class="main-title-p22">❖ D - Données Socio-économiques (Suite)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="badge-p22">🏠 Dépenses du foyer & 👥 Coût de la main d\'œuvre</div>', unsafe_allow_html=True)

    # Définition des structures de données fixes
    postes_depenses = [
        {"label": "Scolarité", "perio": "année"},
        {"label": "Nourriture", "perio": "mois"},
        {"label": "Santé", "perio": "année"},
        {"label": "Électricité", "perio": "2 mois"},
        {"label": "Eau courante", "perio": "mois"},
        {"label": "Charges sociales (Funérailles, mariage, baptême...)", "perio": "année"}
    ]
    categories_mo = ["Travailleur 1", "Travailleur 2", "Travailleur n", "Groupe de travail"]
    options_statut_mo = ["Non spécifié", "Mo permanente", "Mo occasionnelle", "Non rémunérée (familiale)"]
    options_sexe = ["M", "F"]

    # =========================================================================
    # 🔐 PERSISTANCE ET SÉCURISATION DES CLÉS DU SESSION STATE
    # =========================================================================
    for dp in postes_depenses:
        cle_dp = dp['label'].replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").replace(".", "").lower()
        if f"p22_mt_{cle_dp}" not in st.session_state: 
            st.session_state[f"p22_mt_{cle_dp}"] = 0

    for mo in categories_mo:
        cle_mo = mo.replace(" ", "_").lower()
        if f"p22_statut_{cle_mo}" not in st.session_state: st.session_state[f"p22_statut_{cle_mo}"] = "Non spécifié"
        if f"p22_sexe_{cle_mo}" not in st.session_state: st.session_state[f"p22_sexe_{cle_mo}"] = "M"
        if f"p22_temps_{cle_mo}" not in st.session_state: st.session_state[f"p22_temps_{cle_mo}"] = 0
        if f"p22_cout_{cle_mo}" not in st.session_state: st.session_state[f"p22_cout_{cle_mo}"] = 0

    def obtenir_idx_selection(options, valeur_actuelle):
        return options.index(valeur_actuelle) if valeur_actuelle in options else 0

    # =========================================================================
    # ÉTAPE 1 : ENTRÉES DU TERRAIN (POUPÉE 1)
    # =========================================================================
    with st.expander("🪆 ÉTAPE 1 : Saisie des dépenses domestiques et charges de main d'œuvre", expanded=True):
        st.markdown('<div class="pouperee-p22-l1">', unsafe_allow_html=True)
        
        # --- SOUS-SECTION 1 : DÉPENSES COURANTES DU FOYER ---
        st.markdown('<div class="section-title-p22">❖ 1. Dépenses courantes du foyer</div>', unsafe_allow_html=True)
        saisies_depenses = []
        
        for dp in postes_depenses:
            cle_dp = dp['label'].replace(" ", "_").replace("(", "").replace(")", "").replace(",", "").replace(".", "").lower()
            c_dp1, c_dp2, c_dp3 = st.columns([4, 2, 4])
            
            with c_dp1:
                st.markdown(f"<div style='padding-top:10px; font-weight:bold; color:#2C3E50;'>{dp['label']}</div>", unsafe_allow_html=True)
            with c_dp2:
                st.markdown(f"<div style='padding-top:10px; color:#7F8C8D; font-style:italic;'>par {dp['perio']}</div>", unsafe_allow_html=True)
            with c_dp3:
                montant_base = st.number_input(f"Montant ({dp['label']})", min_value=0, step=5000, value=st.session_state[f"p22_mt_{cle_dp}"], label_visibility="collapsed", key=f"p22_mt_{cle_dp}_input")
            
            st.session_state[f"p22_mt_{cle_dp}"] = montant_base

            # Normalisation annuelle
            if dp['perio'] == "année":
                montant_annuel = montant_base
            elif dp['perio'] == "mois":
                montant_annuel = montant_base * 12
            elif dp['perio'] == "2 mois":
                montant_annuel = montant_base * 6
                
            saisies_depenses.append({
                "Poste de Dépenses": dp['label'],
                "Périodicité d'origine": dp['perio'],
                "Montant saisi (FCFA)": montant_base,
                "Montant calculé / an (FCFA)": montant_annuel
            })
            
        st.write("---")

        # --- SOUS-SECTION 2 : COÛT DE LA MAIN D'ŒUVRE ---
        st.markdown('<div class="section-title-p22">❖ 2. Coût de la main d\'œuvre</div>', unsafe_allow_html=True)
        saisies_mo = []
        
        for mo in categories_mo:
            cle_mo = mo.replace(" ", "_").lower()
            st.markdown(f"**Profil de main d'œuvre : {mo}**")
            c_mo1, c_mo2, c_mo3, c_mo4 = st.columns([3, 2, 2, 3])
            
            with c_mo1:
                statut_mo = st.selectbox(f"Statut ({mo})", options_statut_mo, index=obtenir_idx_selection(options_statut_mo, st.session_state[f"p22_statut_{cle_mo}"]), key=f"p22_statut_{cle_mo}_input")
            with c_mo2:
                sexe_mo = st.selectbox(f"Sexe ({mo})", options_sexe, index=obtenir_idx_selection(options_sexe, st.session_state[f"p22_sexe_{cle_mo}"]), key=f"p22_sexe_{cle_mo}_input")
            with c_mo3:
                temps_j = st.number_input(f"Temps ({mo} jours/an)", min_value=0, step=5, value=st.session_state[f"p22_temps_{cle_mo}"], key=f"p22_temps_{cle_mo}_input")
            with c_mo4:
                if statut_mo == "Non rémunérée (familiale)":
                    st.text_input(f"Coût ({mo} FCFA/an)", value="0 (Familial)", disabled=True, key=f"p22_cout_dis_{cle_mo}")
                    cout_annuel = 0
                else:
                    cout_annuel = st.number_input(f"Coût ({mo} FCFA/an)", min_value=0, step=10000, value=st.session_state[f"p22_cout_{cle_mo}"], key=f"p22_cout_{cle_mo}_input")
            
            # Synchronisation Session State
            st.session_state[f"p22_statut_{cle_mo}"] = statut_mo
            st.session_state[f"p22_sexe_{cle_mo}"] = sexe_mo
            st.session_state[f"p22_temps_{cle_mo}"] = temps_j
            st.session_state[f"p22_cout_{cle_mo}"] = cout_annuel

            saisies_mo.append({
                "Travailleur": mo,
                "Mo permanente": "X" if statut_mo == "Mo permanente" else "",
                "Mo occasionnelle": "X" if statut_mo == "Mo occasionnelle" else "",
                "Non rémunérée (familiale)": "X" if statut_mo == "Non rémunérée (familiale)" else "",
                "Sexe": sexe_mo,
                "Coût annuel (FCFA)": cout_annuel,
                "Temps de travail (jours)": temps_j
            })
                
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 2 : MATRICE SYNOPTIQUE / SORTIE DES TABLEAUX (POUPÉE 2)
    # =========================================================================
    with st.expander("📊 ÉTAPE 2 : Rendu Synoptique Matriciel (Visuel Tableaux)", expanded=True):
        st.markdown('<div class="pouperee-p22-l2">', unsafe_allow_html=True)
        
        st.markdown("##### 🛒 Matrice Analytique des Dépenses Courantes du Foyer")
        df_depenses = pd.DataFrame(saisies_depenses)
        st.dataframe(df_depenses, use_container_width=True, hide_index=True)
        st.write("")
        
        st.markdown("##### 👥 Grille Structurelle et Coûts de la Main d'Œuvre")
        df_mo = pd.DataFrame(saisies_mo)
        cols_ordre = ["Travailleur", "Mo permanente", "Mo occasionnelle", "Non rémunérée (familiale)", "Sexe", "Coût annuel (FCFA)", "Temps de travail (jours)"]
        st.dataframe(df_mo[cols_ordre], use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # ÉTAPE 3 : LE CERVEAU DE LEILA IA / DIAGNOSTIC (POUPÉE 3)
    # =========================================================================
    with st.expander("🧠 ÉTAPE 3 : Rapport d'Analyse et Avis Experts de Leila IA", expanded=True):
        st.markdown('<div class="pouperee-p22-l3">', unsafe_allow_html=True)
        
        total_depenses_foyer = sum(r["Montant calculé / an (FCFA)"] for r in saisies_depenses)
        total_charges_mo = sum(r["Coût annuel (FCFA)"] for r in saisies_mo)
        total_jours_mo = sum(r["Temps de travail (jours)"] for r in saisies_mo)
        
        # --- LEILA : DIAGNOSTIC DES CHARGES DOMESTIQUES ---
        st.markdown('<div class="subsection-analysis-title">🛒 Structure du Budget Logistique Familial (Leila IA)</div>', unsafe_allow_html=True)
        if total_depenses_foyer > 0:
            st.info(f"📊 **Charges domestiques :** Les charges de vie incompressibles estimées pour le maintien du foyer s'élèvent à **{total_depenses_foyer:,.0f} FCFA / an**.")
            
            scolarite_row = next((r for r in saisies_depenses if r["Poste de Dépenses"] == "Scolarité"), None)
            if scolarite_row and scolarite_row["Montant saisi (FCFA)"] == 0:
                st.warning("⚠️ **Vigilance Éthique & Sociale :** La ligne de dépense 'Scolarité' est nulle. S'il y a présence d'enfants en âge scolaire au sein du ménage, veillez à auditer l'absence de travail des enfants sur les parcelles (Critère de tolérance zéro de la norme Rainforest Alliance).")
        else:
            st.info("💡 En attente des données budgétaires domestiques pour amorcer l'évaluation du niveau de vie.")

        # --- LEILA : BILAN IMPACT MAIN D'ŒUVRE ---
        st.markdown('<div class="subsection-analysis-title">👥 Évaluation Opérationnelle de la Main d\'œuvre (Leila IA)</div>', unsafe_allow_html=True)
        if total_jours_mo > 0:
            st.success(f"⚡ **Volume de travail absorbé :** La conduite des parcelles requiert **{total_jours_mo} hommes-jours / an** pour matérialiser le calendrier technique.")
            if total_charges_mo > 0:
                cout_moyen_jour = total_charges_mo / total_jours_mo
                st.info(f"💵 **Valeur moyenne de la tâche :** Le coût unitaire journalier de la force de travail externe équivaut à **{cout_moyen_jour:,.0f} FCFA / jour**.")
            
            fam_unites = sum(1 for r in saisies_mo if r["Non rémunérée (familiale)"] == "X")
            if fam_unites > 0:
                st.warning(f"💡 **Indice d'implication endogène :** L'exploitation intègre {fam_unites} ligne(s) de main d'œuvre familiale d'entraide. Utile pour la trésorerie de campagne, cette configuration demande un suivi rigoureux de la charge globale imposée aux proches.")
        else:
            st.warning("⚠️ **Indicateurs manquants :** Aucun volume temporel (jours/an) n'est consigné. Calcul de l'efficience économique suspendu.")

        # --- LEILA : SYNTHÈSE DES CHARGES OUT ---
        st.markdown('<div class="subsection-analysis-title">📉 Balance Consolide des Sorties (Leila IA)</div>', unsafe_allow_html=True)
        sorties_totales = total_depenses_foyer + total_charges_mo
        if sorties_totales > 0:
            st.markdown(f"**Cumul annuel des sorties financières (Foyer + Exploitation) :** <span style='color:#C0392B; font-weight:bold;'>{sorties_totales:,.0f} FCFA / an</span>", unsafe_allow_html=True)
            st.caption("Leila IA croisera automatiquement cette matrice de flux sortants avec le revenu brut calculé en page 21 afin de déterminer le solde net disponible de l'unité de production.")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p22", type="primary", use_container_width=True):
        st.session_state["page_22_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 23
        st.rerun()

    # --- PIED DE PAGE ET PAGINATION HARMONISÉE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    col_f1, col_f2 = st.columns([0.95, 0.05])
    with col_f2: 
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>22</span>", unsafe_allow_html=True)


def dessiner_page_23_Analyse_Des_Problemes():
    # --- 1. CONFIGURATION DU DESIGN ET DE LA CHARTE VISUELLE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-23 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 25px;
    }
    .main-title-p23 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .badge-p23 { background-color: #1F4E78; color: white; padding: 6px 14px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-size: 14px; }
    
    /* Structure d'encadrement institutionnel standardisé */
    .pouperee-p23-cadre { border-left: 5px solid #16A085; background-color: #F8FBFB; padding: 25px; border-radius: 6px; margin-bottom: 15px; }
    
    .bullet-list-p23 { font-size: 16px; color: #2C3E50; line-height: 1.8; margin-left: 10px; }
    .bullet-item-p23 { margin-bottom: 12px; list-style-position: inside; font-weight: 500; }
    .bullet-item-p23 strong { color: #1F4E78; }
    
    .sub-section-title-p23 { color: #16A085; font-size: 19px; font-weight: bold; margin-top: 25px; margin-bottom: 15px; border-bottom: 2px solid #16A085; padding-bottom: 6px; }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE D'HARMONISATION INSTITUTIONNELLE ---
    st.markdown("""
    <div class="diapo-slide-23">
        <div class="main-title-p23">❖ 2.4.2 ANALYSE DES PROBLÈMES</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="badge-p23">📋 Cadre Méthodologique du Diagnostic de l\'Exploitation</div>', unsafe_allow_html=True)

    # --- CONTENU PRINCIPAL ENCADRÉ ---
    st.markdown('<div class="pouperee-p23-cadre">', unsafe_allow_html=True)
    
    st.markdown("""
    <ul class="bullet-list-p23">
        <li class="bullet-item-p23">Ressortir les principales contraintes, les causes et les conséquences sur la cacaoyère.</li>
        <li class="bullet-item-p23">Classer les contraintes par domaine (Technique, Socio-économique, Environnemental).</li>
        <li class="bullet-item-p23">Déterminer les solutions à mettre en œuvre, en vue de rendre l'exploitation économiquement, socialement et environnementalement viable et de se conformer aux exigences de la norme de certification.</li>
    </ul>
    """, unsafe_allow_html=True)
    
    # --- SOUS-SECTION DIAGNOSTIC (Nettoyage structurel complet) ---
    st.markdown('<div class="sub-section-title-p23">Le diagnostic de la cacaoyère conduit à la prise de décision sur :</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <ul class="bullet-list-p23" style="margin-top: 10px;">
        <li class="bullet-item-p23"><strong>La réhabilitation :</strong> Recépage, taille de restructuration, densification.</li>
        <li class="bullet-item-p23"><strong>La replantation :</strong> Renouvellement total de la parcelle fatiguée ou sénescente.</li>
        <li class="bullet-item-p23"><strong>La reconversion :</strong> Changement de culture si le sol ou les contraintes climatiques ne répondent plus aux exigences du cacao.</li>
        <li class="bullet-item-p23"><strong>La poursuite des BPA :</strong> Application continue des Bonnes Pratiques Agricoles sur plantation saine.</li>
        <li class="bullet-item-p23"><strong>La diversification :</strong> Introduction structurée d'arbres d'ombrage utiles et intégration de cultures vivrières intermédiaires.</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p23", type="primary", use_container_width=True):
        st.session_state["page_23_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 24
        st.rerun()

    # --- PIED DE PAGE ET NUMÉRO DE PAGE HARMONISÉ ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    _, col_p = st.columns([0.95, 0.05])
    with col_p:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>23</span>", unsafe_allow_html=True)



def dessiner_page_24_Grille_Decision():
    # --- 1. INITIALISATION DE LA MÉMOIRE DE SESSION (PERSISTANCE ATOMIQUE) ---
    cles_checkbox = [
        "age_plus_30", "age_moins_30", 
        "densite_inf_800", "densite_800_1000", 
        "rendement_inf_400", "rendement_sup_400",
        "swollen_shoot_present", "swollen_shoot_absent", 
        "sol_favorable", "sol_hydromorphe", 
        "sol_grossier", "sol_sn_cuirasse", 
        "pluvio_inf_1200"
    ]
    
    for cle in cles_checkbox:
        if cle not in st.session_state:
            st.session_state[cle] = False

    # --- 2. INJECTION DES STYLES CSS NATIFS ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .main-title-p24 { color: #113f67; font-size: 24px; font-weight: bold; margin-top: 15px; margin-bottom: 5px; }
    .badge-p24 { background-color: #2e86de; color: white; padding: 5px 10px; font-weight: bold; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
    .box-decision { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 15px; margin-bottom: 20px; border: 1px solid #E2E8F0; }
    .critere-header { background-color: #34495e; color: white; padding: 10px; font-weight: bold; border-radius: 4px; margin-bottom: 15px; }
    
    /* Styles de la structure FAQ & Tableaux Natifs (Évite le bug de l'Iframe) */
    .title-faq { color: #113f67; font-size: 22px; font-weight: bold; margin-top: 25px; margin-bottom: 15px; }
    .box-question { background-color: #ffffff; padding: 15px 20px; border-radius: 8px; border-left: 5px solid #2e86de; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0; }
    .sub-title-leila { color: #1e3d2f; font-size: 17px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
    .badge-accent { background-color: #e8f4f8; color: #2e86de; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; }
    .badge-danger { background-color: #fff5f5; color: #c53030; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; }
    .triptyque-box { background-color: #f8f9fa; border: 1px dashed #cbd5e0; padding: 15px; border-radius: 6px; font-family: monospace; text-align: center; color: #2d3748; margin: 15px 0; line-height: 1.4; font-size: 13px; }
    
    /* Tableau épuré sans scrollbars externes */
    .edu-table-native { width: 100%; border-collapse: collapse; margin-top: 15px; background-color: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .edu-table-native th { background-color: #113f67; color: white; padding: 12px; text-align: left; font-size: 14px; border: 1px solid #E2E8F0; }
    .edu-table-native td { padding: 12px; border: 1px solid #E2E8F0; font-size: 13.5px; vertical-align: top; text-align: justify; color: #2D3748; line-height: 1.5; }
    .edu-table-native tr:hover { background-color: #F8FAFC; }
    .td-critere { font-weight: bold; color: #113f67; }
    
    /* --- NOUVEAUX BADGES INTERNES AU TABLEAU --- */
    .badge-adv { background-color: #E8F4F8; color: #1F4E78; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; margin-bottom: 4px; }
    .badge-inc { background-color: #FFF5F5; color: #C53030; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; margin-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title-p24">• Grille de décision du PDC</div>', unsafe_allow_html=True)
    st.markdown('<div class="badge-p24">Orientation Technique de la Parcelle</div>', unsafe_allow_html=True)

    st.write("### 🛠️ Cochez les critères observés sur la parcelle :")
    
    # --- 3. INTERFACE DE COCHAGE AVEC PERSISTANCE ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="critere-header">📈 Âge, Densité & Rendement</div>', unsafe_allow_html=True)
        age_plus_30 = st.checkbox("Plantation âgée de plus de 30 ans", key="age_plus_30")
        age_moins_30 = st.checkbox("Plantation âgée de moins de 30 ans", key="age_moins_30")
        st.divider()
        densite_inf_800 = st.checkbox("Densité inférieure à 800 arbres productifs / ha", key="densite_inf_800")
        densite_800_1000 = st.checkbox("Densité comprise entre 800 et 1 000 arbres productifs / ha", key="densite_800_1000")
        st.divider()
        rendement_inf_400 = st.checkbox("Rendement inférieur à 400 kg / ha", key="rendement_inf_400")
        rendement_sup_400 = st.checkbox("Rendement égal ou supérieur à 400 kg / ha", key="rendement_sup_400")

    with col2:
        st.markdown('<div class="critere-header">🌍 Sol, Climat & État Sanitaire</div>', unsafe_allow_html=True)
        swollen_shoot_present = st.checkbox("Présence de foyers de Swollen Shoot", key="swollen_shoot_present")
        swollen_shoot_absent = st.checkbox("Absence de foyers de Swollen Shoot", key="swollen_shoot_absent")
        st.divider()
        sol_favorable = st.checkbox("Sol favorable à la culture de cacao", key="sol_favorable")
        sol_hydromorphe = st.checkbox("Sol hydromorphe (engorgé d'eau)", key="sol_hydromorphe")
        sol_grossier = st.checkbox("Sol contenant plus de 50 % d'éléments grossiers", key="sol_grossier")
        cuirasse_proche = st.checkbox("Présence de cuirasse à moins d'un mètre de profondeur", key="sol_sn_cuirasse")
        st.divider()
        pluvio_inf_1200 = st.checkbox("Pluviométrie < 1200 mm avec plus de 4 mois de saison sèche", key="pluvio_inf_1200")

    # --- 4. BASE DE DONNÉES ENRICHIE ---
    dictionnaire_pedagogique = {
        "age_plus_30": {
            "nom": "Plantation âgée de plus de 30 ans",
            "avantage": "L'analyse de ce critère permet de caractériser le stade de sénescence physiologique terminale du verger cacaoyer. Sur le plan scientifique, il sert d'indicateur historique pour évaluer l'épuisement du potentiel de renouvellement cellulaire des arbres. Il permet aux chercheurs de planifier la transition variétale vers des générations de matériel végétal plus performantes. Enfin, cet indicateur valide l'arrêt immédiat des investissements en intrants chimiques complexes devenus inefficaces sur un système racinaire âgé.",
            "inconvenient": "À cet âge, les cacaoyers présentent une dégradation structurelle irréversible des vaisseaux conducteurs de sève (xylème et phloème), limitant la nutrition des cabosses. Le taux de mortalité naturelle des arbres s'accélère de façon exponentielle, créant des vides structurels dans la parcelle qui effondrent la rentabilité à l'hectare. La faible vigueur immunitaire des vieux arbres en fait des réservoirs épidémiologiques parfaits pour la multiplication des parasites. Pour le planteur, maintenir ce verger représente un gouffre financier en main-d'œuvre pour un retour sur investissement nul."
        },
        "age_moins_30": {
            "nom": "Plantation âgée de moins de 30 ans",
            "avantage": "Ce critère confirme la présence d'un appareil végétatif en pleine capacité métabolique, hormonal et structurelle. Les arbres possèdent encore la plasticité biologique nécessaire pour réagir positivement et rapidement aux techniques de régénération intensive. Il justifie scientifiquement l'application de programmes de fertilisation minérale raisonnée car l'absorption racinaire demeure optimale à ce stade. C'est un excellent feu vert technique pour rentabiliser des opérations de taille de restructuration ou de sur-greffage en clones améliorés.",
            "inconvenient": "Si le rendement de la parcelle est anormalement bas malgré cet âge théoriquement productif, cela indique un blocage agronomique majeur sous-jacent. Le risque est d'investir à perte dans la réhabilitation si l'échec initial est dû à un mauvais choix de matériel végétal non certifié à la plantation. De plus, un verger vigoureux de cet âge non entretenu développe une canopée anarchique qui séquestre la lumière solaire. Cela peut masquer une dégradation physico-chimique invisible des sols que le producteur ne détectera qu'après l'apparition des premiers symptômes de dépérissement."
        },
        "densite_inf_800": {
            "nom": "Densité inférieure à 800 arbres productifs / ha",
            "avantage": "Cet indicateur met scientifiquement en évidence une sous-utilisation critique de l'espace cultural et de l'énergie photonique disponible. Il permet de quantifier précisément le manque à gagner spatial pour optimiser l'indice de surface foliaire globale (LAI) de la parcelle. L'analyse de cette faible densité aide à planifier des stratégies précises de replantation intercalaire ciblée ou de densification. Elle offre également une opportunité agroforestière unique pour introduire des arbres d'ombrage sans étouffer les cacaoyers existants.",
            "inconvenient": "La rupture de la canopée causée par ce vide thermique provoque une forte insolation directe du sol, accélérant la minéralisation de la matière organique. Cette ouverture lumineuse favorise la germination agressive des adventices héliophiles, augmentant drastiquement la pénibilité et les coûts liés au désherbage. Le microclimat interne de la parcelle devient hautement instable, exposant le tronc des cacaoyers à des stress thermiques et aux attaques de foreurs de tiges. Sur le plan social, cette sous-population condamne le paysan à la pauvreté par l'impossibilité d'atteindre des rendements d'échelle."
        },
        "densite_800_1000": {
            "nom": "Densité comprise entre 800 et 1 000 arbres / ha",
            "avantage": "Ce critère valide la conformité rigoureuse de la structure spatiale du verger vis-à-vis des normes agronomiques recommandées en Côte d'Ivoire. Il garantit un équilibre optimal entre l'interception de la lumière solaire pour la photosynthèse et l'occupation du volume racinaire souterrain. Cette configuration stabilise le microclimat sous la canopée, protégeant naturellement la litière du sol contre le dessèchement direct. Pour l'expert, c'est la base idéale pour évaluer le potentiel réel des formules de fertilisation sans biais de surpeuplement.",
            "inconvenient": "Si cette densité théorique s'accompagne d'un manque de taille d'entretien, elle engendre un confinement de l'air sous le feuillage. Cette humidité relative stagnante devient le principal vecteur d'explosion des attaques de pourriture brune dues à Phytophthora palmivora. La compétition pour les nutriments du sol devient féroce si le producteur n'apporte pas de fumure de compensation régulière. Enfin, la récolte et la circulation sanitaire dans la parcelle peuvent devenir complexes si l'architecture des branches n'est pas canalisée."
        },
        "rendement_inf_400": {
            "nom": "Rendement inférieur à 400 kg / ha",
            "avantage": "L'analyse de ce seuil critique permet de matérialiser la faillite économique objective de la parcelle en l'état actuel du système. Scientifiquement, il prouve l'existence d'un facteur limitant absolu (sanitaire, pédologique ou génétique) qui bloque l'expression du métabolisme de la plante. Cet indicateur sert de levier d'aide à la décision pour orienter de force le producteur vers une reconversion culturale ou une replantation totale. Il permet aux coopératives d'identifier les zones de détresse agricole nécessitant une intervention d'urgence des projets de développement.",
            "inconvenient": "Un niveau de production aussi bas ne couvre même pas les charges de main-d'œuvre familiale ou salariée requises pour la récolte. Sur le plan social, cette situation entraîne un phénomène d'abandon psychologique du champ, transformant la parcelle en friche non entretenue. Ces parcelles abandonnées deviennent instantanément des foyers d'incubation géants pour les maladies qui contaminent les vergers sains voisins. Le producteur se retrouve prisonnier d'un cycle de précarité économique, l'empêchant d'investir dans l'éducation ou la santé de sa famille."
        },
        "rendement_sup_400": {
            "nom": "Rendement égal ou supérieur à 400 kg / ha",
            "avantage": "Ce critère garantit une base de productivité résiduelle permettant de rentabiliser rapidement des investissements de réhabilitation à faible coût. Il confirme que l'interaction entre le sol, le climat et le matériel végétal maintient une efficacité métabolique minimale stable. Pour le chercheur, c'est un indicateur de résilience agro-écosystémique qui valide la conservation temporaire du verger. Il sécurise un flux de trésorerie minimum pour le producteur pendant la mise en œuvre des réformes techniques.",
            "inconvenient": "Ce rendement peut dissimuler un épuisement silencieux et progressif des réserves minérales du sol si la production est maintenue sans compensation. Le producteur peut développer un faux sentiment de satisfaction économique, l'incitant à négliger les signes avant-coureurs de vieillissement des arbres. À long terme, l'absence de restructuration sur ces parcelles mène à un effondrement brutal et imprévisible de la production. Cela retarde l'adoption nécessaire des innovations agronomiques et des nouvelles variétés tolérantes."
        },
        "swollen_shoot_present": {
            "nom": "Présence de foyers de Swollen Shoot",
            "avantage": "La détection de ce critère permet de poser une alerte épidémiologique absolue, critique et prioritaire sur l'ensemble de l'exploitation. Sur le plan virologique, cet indicateur stoppe immédiatement l'application inutile de fertilisants ou de fongicides qui ne peuvent guérir ce phytovirus. Il permet de déclencher l'application stricte du protocole de quarantaine et d'arrachage pour sauver le bassin cacaoyer environnant. C'est l'argument scientifique incontestable pour mobiliser les fonds d'indemnisation et d'appui auprès des autorités nationales.",
            "inconvenient": "Ce virus complexe attaque le système vasculaire de l'arbre, provoquant des gonflements nodaux et un dépérissement fatal à court terme. L'inconvénient majeur est l'obligation de détruire non seulement les arbres infectés, mais aussi une ceinture de sécurité d'arbres sains autour du foyer. Cela impose au planteur un traumatisme social lié à la perte immédiate de son outil de travail et de sa seule source de revenus durables. Le sol exige un vide sanitaire rigoureux et l'éradication des plantes hôtes avant toute replantation certifiée."
        },
        "swollen_shoot_absent": {
            "nom": "Absence de foyers de Swollen Shoot",
            "avantage": "Ce critère apporte une garantie de sécurité et de sérénité phytosanitaire maximale pour planifier des investissements structurels lourds et durables. Il confirme que la parcelle est exempte du principal fléau virologique d'Afrique de l'Ouest, sécurisant les projections de rendement des bailleurs. Pour l'agronome, c'est le feu vert absolu pour déployer des programmes de fertilisation intensive ou de régénération par taille. Il valorise la position géographique et technique de l'exploitation au sein des réseaux de coopératives.",
            "inconvenient": "L'absence de symptômes visibles peut générer un excès de confiance dangereux et une baisse de vigilance face aux insectes vecteurs (cochenilles). Le producteur peut omettre d'inspecter régulièrement les parcelles limitrophes, s'exposant à une introduction surprise du virus par contamination aérienne. En outre, cela peut inciter à négliger l'éradication des barrières de plantes hôtes sauvages en bordure de champ. Le risque est de voir survenir une épidémie foudroyante dès que les conditions environnementales stressantes affaiblissent le verger."
        },
        "sol_favorable": {
            "nom": "Sol favorable à la culture de cacao",
            "avantage": "Ce paramètre assure un ancrage racinaire profond, une excellente porosité et une valorisation maximale de chaque unité de fertilisant apportée. Il garantit que les horizons pédologiques disposent d'un équilibre physico-chimique idéal pour nourrir durablement l'appareil végétatif. Scientifiquement, il maximise l'efficience de l'utilisation de l'eau (WUE) et protège les arbres contre les stress physiologiques mineurs. C'est le socle fondamental pour optimiser l'expression du potentiel génétique des variétés sélectionnées.",
            "inconvenient": "Un excellent sol incite malheureusement et très souvent à des pratiques de monoculture intensive destructrices, sans arbres d'ombrage associés. À terme, cette exploitation continue accélère la minéralisation de l'humus et provoque un déclin rapide de la biodiversité microbienne du sol. Le producteur tend à surestimer la résilience naturelle de sa terre, omettant d'apporter des amendements organiques de restitution. À long terme, cela conduit à une fatigue du sol difficile et coûteuse à corriger agronomiquement."
        },
        "sol_hydromorphe": {
            "nom": "Sol hydromorphe (engorgé d'eau)",
            "avantage": "L'analyse de ce critère permet de diagnostiquer un blocage physique majeur lié à l'anoxie (absence d'oxygène) dans les horizons racinaires. D'un point de vue scientifique, cet indicateur isole la cause mécanique de la mortalité des arbres, évitant les erreurs de traitement phytosanitaire. Il sert de base technique indiscutable pour recommander des travaux lourds de drainage ou pour réorienter la parcelle vers des cultures de bas-fonds. Il explique scientifiquement pourquoi les arbres sur-greffés s'effondrent subitement après une phase de surproduction factice.",
            "inconvenient": "L'excès d'eau permanent provoque l'asphyxie et le pourrissement biologique du pivot central et des radicelles absorbantes du cacaoyer. Ce milieu anaérobie stimule la prolifération de champignons racinaires destructeurs comme le genre Phytophthora, entraînant l'apoplexie de l'arbre. Le cacaoyer ne peut pas développer de racines d'ancrage stables, ce qui provoque des vagues de mortalité dès que les horizons supérieurs s'asphyxient. C'est une barrière environnementale éliminatoire : y investir dans le cacao garantit la perte totale du capital en moins de 6 ans."
        },
        "sol_grossier": {
            "nom": "Sol contenant plus de 50 % d'éléments grossiers",
            "avantage": "Ce paramètre met en évidence un déficit structural sévère de la texture du sol affectant directement sa Capacité d'Échange Cationique (CEC). Scientifiquement, il permet d'anticiper la faible rétention des nutriments et d'expliquer la faim minérale chronique constatée sur les arbres. Il permet aux agronomes de concevoir des plans de fertilisation fractionnée très spécifiques pour limiter le gaspillage économique des intrants. Cet indicateur justifie scientifiquement l'apport massif et impératif de compost pour recréer du complexe argilo-humique.",
            "inconvenient": "Ces sols gravillonneurs souffrent d'une porosité macro-texturale excessive qui accélère le lessivage des éléments nutritifs vers les nappes phréatiques. Pendant la saison sèche, la réserve en eau utile (RU) du sol s'épuise de manière fulgurante, plongeant les cacaoyers dans un stress hydrique létal. Le système racinaire superficiel s'use mécaniquement contre la fraction pierreuse, créant des micro-blessures propices aux infections bactériennes du bois. Pour le paysan, c'est un sol ingrat qui engendre de lourdes charges financières pour des rendements médiocres."
        },
        "sol_sn_cuirasse": {
            "nom": "Présence de cuirasse à moins d'un mètre de profondeur",
            "avantage": "L'identification de la cuirasse ferrugineuse permet de cartographier une barrière géologique verticale infranchissable pour le système racinaire. Sur le plan de la physique des sols, cet indicateur démontre une réduction drastique du volume de terre utile exploré par la plante. Il permet de stopper immédiatement les projets de replantation de cacaoyers sur des dalles rocheuses souterraines invisibles à l'œil nu. C'est une donnée spatiale précieuse pour réorienter le foncier vers des aménagements pastoraux ou des cultures superficielles.",
            "inconvenient": "La cuirasse indurée bloque mécaniquement la descente de la racine pivotante, élément vital pour l'accès à l'eau en période de stress climatique. Les cacaoyers développent un système racinaire anormalement plat et traçant, ce qui les rend extrêmement vulnérables au déracinement par les tornades. Dès que les premiers horizons supérieurs subissent la sécheresse, les arbres entrent en flétrissement et meurent massivement. Cette contrainte physique majeure condamne le verger à un nanisme végétatif irréversible."
        },
        "pluvio_inf_1200": {
            "nom": "Pluviométrie < 1200 mm avec longue saison sèche",
            "avantage": "Ce critère macroclimatique permet de poser les limites strictes de la viabilité géographique de la cacaoculture face au changement climatique global. Scientifiquement, il modélise le déficit hydrique cumulé qui bloque l'activité photosynthétique et perturbe la physiologie de la floraison. Il permet d'anticiper les baisses de récoltes régionales et d'orienter les politiques agricoles vers l'agroforesterie de substitution. C'est l'indicateur clé pour valider l'installation de systèmes d'irrigation ou de techniques de paillage lourd.",
            "inconvenient": "Le manque d'eau prolongé provoque l'avortement en série des coussinets floraux et le dessèchement précoce des jeunes cabosses (cherelles). Les arbres entrent en flétrissement permanent, perdent leur indice foliaire et deviennent incapables d'assimiler les éléments minéraux du sol. Ce stress hydrique chronique effondre le système immunitaire du cacaoyer, déclenchant des invasions massives et destructrices de mirides. Pour les communautés rurales, ce climat instable transforme la cacaoculture en une activité précaire qui menace la survie économique des ménages."
        }
    }

    # --- 5. MOTEUR DE DÉCISION ET TRAITEMENT DES INCOHÉRENCES ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Diagnostic de Cohérence et Croisement par Leila IA")

    choix = {
        "age_plus_30": age_plus_30, "age_moins_30": age_moins_30,
        "densite_inf_800": densite_inf_800, "densite_800_1000": densite_800_1000,
        "rendement_inf_400": rendement_inf_400, "rendement_sup_400": rendement_sup_400,
        "swollen_shoot_present": swollen_shoot_present, "swollen_shoot_absent": swollen_shoot_absent,
        "sol_favorable": sol_favorable, "sol_hydromorphe": sol_hydromorphe,
        "sol_grossier": sol_grossier, "sol_sn_cuirasse": cuirasse_proche,
        "pluvio_inf_1200": pluvio_inf_1200
    }
    
    criteres_coches = [k for k, v in choix.items() if v]
    nb_coches = len(criteres_coches)

    incoherence = False
    if age_plus_30 and age_moins_30:
        st.error("❌ **Incohérence :** Une plantation ne peut pas avoir plus de 30 ans et moins de 30 ans simultanément.")
        incoherence = True
    if densite_inf_800 and densite_800_1000:
        st.error("❌ **Incohérence :** Deux intervalles de densité différents ne peuvent pas être sélectionnés en même temps.")
        incoherence = True
    if rendement_inf_400 and rendement_sup_400:
        st.error("❌ **Incohérence :** Le rendement ne peut pas être à la fois inférieur et supérieur à 400 kg/ha.")
        incoherence = True
    if swollen_shoot_present and swollen_shoot_absent:
        st.error("❌ **Incohérence :** Statut contradictoire pour le Swollen Shoot.")
        incoherence = True

    if incoherence:
        st.stop()

    force_reconversion = sol_hydromorphe or cuirasse_proche or sol_grossier or pluvio_inf_1200
    force_replantation_economique = age_plus_30 or (densite_inf_800 and rendement_inf_400) or densite_inf_800

    if nb_coches > 0:
        if force_reconversion:
            st.error("🚨 **DÉCISION FINALE : RECONVERSION / DIVERSIFICATION**")
            msg_global = "Les barrières physiques du milieu (sol ou climat) sont éliminatoires pour le cacaoyer. Même si d'autres indicateurs semblent favorables à court terme, la parcelle subira un dépérissement irrémédiable."
            color_border = "#e74c3c"
            reco_pdc = "<li><strong>Arrêt définitif du cacao</strong> sur les zones à contraintes lourdes.</li><li>S'orienter vers une <strong>diversification culturale</strong> adaptée.</li>"
        elif swollen_shoot_present:
            st.warning("⚠️ **DÉCISION FINALE : REPLANTATION TOTALE (URGENCE SANITAIRE)**")
            msg_global = "La présence confirmée du virus du Swollen Shoot annule tout espoir de réhabilitation simple. L'arrachage de sécurité est inévitable pour stopper la contagion géographique."
            color_border = "#e67e22"
            reco_pdc = "<li>Arrachage complet des plants atteints selon le protocole national.</li><li>Mise en place d'un vide sanitaire strict avant replantation avec du matériel certifié tolérant.</li>"
        elif force_replantation_economique:
            st.warning("⚠️ **DÉCISION FINALE : REPLANTATION ÉCONOMIQUE**")
            msg_global = "Les indicateurs d'épuisement physiologique ou de sous-population critique dominent. Une restructuration totale par blocs s'impose pour retrouver un niveau de productivité viable."
            color_border = "#f39c12"
            reco_pdc = "<li>Planifier un remplacement complet et ordonné de la parcelle.</li><li>Régénérer le sol avec des apports organiques avant la replantation de matériel végétal sélectionné.</li>"
        elif age_moins_30 and densite_inf_800 and rendement_sup_400:
            st.success("🟢 **DÉCISION FINALE : RÉHABILITATION PAR REGARNISSAGE**")
            msg_global = "La plantation est jeune et garde une productivité encourageante sur un sol propice, mais elle souffre d'un manque cruel de pieds à l'hectare qu'il faut combler au plus vite."
            color_border = "#2ecc71"
            reco_pdc = "<li>Conserver la charpente des arbres existants toujours productifs.</li><li>Procéder à un <strong>regarnissage systématique</strong> en début de saison des pluies.</li>"
        else:
            st.success("🟢 **DÉCISION FINALE : RÉHABILITATION ET ENTRETIEN CLASSIQUE**")
            msg_global = "Les voyants agronomiques fondamentaux sont au vert (plantation saine, jeune, sol de qualité). Le potentiel de production doit juste être maintenu par de bonnes pratiques culturales."
            color_border = "#27ae60"
            reco_pdc = "<li>Poursuivre le calendrier de taille d'aération et la maîtrise de l'ombrage.</li><li>Optimiser la nutrition par un plan d'apport d'engrais équilibré.</li>"

        st.markdown(f"""
        <div class="box-decision" style="border-left: 5px solid {color_border};">
            <p style="margin: 0 0 10px 0; font-size: 15px; text-align: justify;">{msg_global}</p>
            <p style="margin: 5px 0 0 0; font-weight: bold; color: #333;">📋 Recommandations du PDC :</p>
            <ul style="margin: 5px 0 0 0; padding-left: 20px; font-size: 14px;">{reco_pdc}</ul>
        </div>
        """, unsafe_allow_html=True)

        # --- 6. TABLEAU PÉDAGOGIQUE EN RENDU STRIPÉ NATIF STYLES (PAS D'IFRAME) ---
        st.write("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 Décorticage Éducatif des Éléments Sélectionnés")
        st.info("Leila détaille ci-dessous les forces et les vulnérabilités propres à chaque facteur coché pour guider votre intervention :")

        lignes_html = ""
        for c in criteres_coches:
            if c in dictionnaire_pedagogique:
                infos = dictionnaire_pedagogique[c]
                lignes_html += f"""
                <tr>
                    <td class="td-critere">{infos['nom']}</td>
                    <td><span class="badge-adv">Avantage / Intérêt pédagogique</span><br>{infos['avantage']}</td>
                    <td><span class="badge-inc">Inconvénient / Risque terrain</span><br>{infos['inconvenient']}</td>
                </tr>
                """

        tableau_final_html = f"""
        <table class="edu-table-native">
            <thead>
                <tr>
                    <th style="width: 25%;">Critère Observé</th>
                    <th style="width: 37.5%;">Pourquoi Leila l'analyse (Avantages)</th>
                    <th style="width: 37.5%;">Ce que le terrain subit (Inconvénients)</th>
                </tr>
            </thead>
            <tbody>
                {lignes_html}
            </tbody>
        </table>
        """
        st.markdown(tableau_final_html, unsafe_allow_html=True)

# --- 7. SÉQUENCE INTERACTIVE : LEILA & SWOLLEN SHOOT ---
        if swollen_shoot_present:
            st.write("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="title-faq">💡 Guide Interactif & Savoir Agronomique Approfondi</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="box-question">
                <span style="color: #1F4E78; font-weight: bold; font-size: 13px; text-transform: uppercase;">Question Additionnelle du Planteur / Chercheur :</span><br>
                <p style="font-size: 15px; font-weight: 500; color: #2C3E50; margin-top: 5px; margin-bottom: 0;">
                    Est-ce qu'on peut replanter un nouveau champ de cacao après une attaque de Swollen Shoot ?
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🧠 Analyse de Cohérence et Stratégie Évolutive par Leila IA")
            
            st.info(
                "**Réponse de Leila :** C'est une excellente question de stratégie agronomique et de gestion des sols. "
                "La réponse courte est **oui, absolument**, et c'est même l'une des meilleures approches recommandées "
                "par la recherche (notamment le CNRA en Côte d'Ivoire) pour rompre le cycle du virus.\n\n"
                "Cependant, il y a des conditions biologiques strictes à respecter pendant ces 2 ou 3 cycles de cultures vivrières.\n\n"
                "Voici l'analyse agronomique détaillée de ce processus :"
            )
            
            st.markdown("""<div class="sub-title-leila">1. Pourquoi la rotation avec le vivrier fonctionne (L'effet "Vide Sanitaire")</div>""", unsafe_allow_html=True)
            st.markdown(
                "Le virus du Swollen Shoot (**CSSV** - *Cocoa Swollen Shoot Virus*) a une faiblesse majeure : "
                "il ne peut pas survivre directement dans le sol, ni dans les débris de bois morts une fois qu'ils "
                "sont totalement secs et décomposés. Le virus a impérativement besoin d'un hôte vivant (les cellules d'un arbre malade) "
                "et d'un vecteur mobile (les cochenilles) pour passer d'une plante à une autre.\n\n"
                "En éliminant complètement le verger infecté et en cultivant du vivrier pendant plusieurs cycles "
                "(ce qui prend généralement entre **2 et 3 ans**), tu crées un **vide sanitaire biologique** :"
            )
            
            st.markdown("""
            * 🪰 **Mortalité des vecteurs :** Les cochenilles infectées qui restent sur le site meurent ou perdent le virus (le virus n'est pas persistant indéfiniment chez le vecteur).
            * 🪵 **Destruction de la source :** Les racines résiduelles des vieux cacaoyers malades enfouies dans le sol meurent définitivement, coupant toute source de nourriture au virus.
            """)

            st.markdown('<div class="sub-title-leila">2. Le choix crucial des cultures vivrières (Les pièges à éviter)</div>', unsafe_allow_html=True)
            st.markdown(
                "Tous les vivriers ne se valent pas. Certains arbres ou plantes présents dans les champs en Côte d'Ivoire "
                "sont des **hôtes intermédiaires** (des réservoirs cachés) du Swollen Shoot. Si le planteur les laisse ou les cultive, "
                "le virus restera sur la parcelle."
            )
            
            col_ok, col_ban = st.columns(2)
            with col_ok:
                st.markdown('🟢 **Cultures vivrières excellentes (Sans danger) :**')
                st.markdown("""
                * **Le Maïs et le Riz :** Les graminées sont parfaites. Elles n'hébergent pas le virus et leur système racinaire de surface nettoie la structure supérieure du sol.
                * **L'Arachide et le Niébé :** <span class="badge-accent">Le choix d'expert</span>. En plus de rompre le cycle du virus, ces légumineuses fixent l'azote de l'air et enrichissent naturellement le sol pour les futurs cacaoyers.
                * **Le Manioc :** Utilisable, mais à condition de nettoyer drastiquement la parcelle à la récolte.
                """, unsafe_allow_html=True)
                
            with col_ban:
                st.markdown('⚠️ **Plantes à exclure absolument (Réservoirs) :**')
                st.markdown("""
                * **Le Colatier (*Cola nitida*) :** C'est le cousin germain du cacaoyer, il abrite le virus en mode asymptomatique (sans toujours de symptômes apparents).
                * **Le Baobab (*Adansonia digitata*) & Le Fromager (*Ceiba pentandra*) :** <span class="badge-danger">Hôtels 5 étoiles</span>. Ces grands arbres forestiers hébergent massivement les colonies de cochenilles. Ils doivent être abattus ou annelés si la parcelle a été détruite.
                """, unsafe_allow_html=True)

            st.markdown('<div class="sub-title-leila">3. Les 3 étapes indispensables avant le retour du cacao</div>', unsafe_allow_html=True)
            st.markdown(
                "Pour garantir que le nouveau verger ne retombe pas malade après les 3 cycles de vivriers, "
                "Leila conseille d'appliquer ce triptyque technique :"
            )
            
            st.markdown("""
            <div class="triptyque-box">
                [Éradication Totale & Incinération]<br>
                │<br>
                ▼<br>
                [2 à 3 Cycles de Vivriers (Azote / Rupture)]<br>
                │<br>
                ▼<br>
                [Replantation : Matériel Tolérant + Barrière Végétale]
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            * 🛡️ **La Ceinture de Sécurité Végétale :** Lors de la replantation, il est fortement recommandé de planter une barrière protectrice tout autour de l'espace (ex: 2 ou 3 rangées serrées de bananiers ou de *Prestige*) pour empêcher les cochenilles des plantations voisines de migrer par le vent vers la nouvelle parcelle saine.
            * 🧪 **Le choix de la variété :** Après un passif de Swollen Shoot, il est interdit de replanter du tout-venant. L'utilisation de semences certifiées tolérantes (comme le **Cacao Mercedes** distribué par le CNRA) est obligatoire pour assurer la résilience immunitaire du verger.
            * 🪱 **La restauration humique :** Les cycles de vivriers successifs épuisent la couche superficielle du sol. Avant de remettre les jeunes plants de cacao, un apport de compost ou de biomasse végétale est nécessaire pour redonner de la force à la structure de la terre.
            """)

            st.write("<br>", unsafe_allow_html=True)
            st.success(
                "🍀 **En résumé :** L'idée de transition par le vivrier est la **clé de voûte de la durabilité**. "
                "Elle résout un problème social immense : elle permet au planteur de continuer à nourrir sa famille et de "
                "générer des revenus à court terme avec le maïs ou l'arachide, tout en soignant scientifiquement sa terre "
                "pour relancer l'or brun sur des bases saines."
            )

    else:
        st.info("💡 **En attente de critères...** Cochez au moins un paramètre pour obtenir le diagnostic et le décorticage éducatif de Leila.")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p24", type="primary", use_container_width=True):
        st.session_state["page_24_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 25
        st.rerun()

    # --- 8. PIED DE PAGE ET NUMÉROTATION REGLEMENTAIRE ---
    st.write("<br>", unsafe_allow_html=True)
    st.write("---")
    _, col_p = st.columns([0.95, 0.05])
    with col_p:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>24</span>", unsafe_allow_html=True)
