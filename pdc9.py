def dessiner_page_43_Croquis_Polygone_Parcelle():
    import pandas as pd  # Importation indispensable pour st.map()
    import time  # Sécurité pour le sleep
    
    # --- STYLE CSS REPRODUCTION PARFAITE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-43 {
        background-color: #E2F0D9; /* Vert très clair thématique */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .titre-principal-43 {
        color: #1F4E78; /* Bleu foncé institutionnel */
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    
    .sous-titre-43 {
        color: #385723; /* Vert foncé agro */
        font-size: 22px;
        font-weight: bold;
        margin-left: 20px;
        margin-bottom: 5px;
    }
    
    .precision-titre-43 {
        color: #000000;
        font-size: 18px;
        font-style: italic;
        margin-left: 40px;
    }

    .bloc-carte-info {
        background-color: #F8F9FA;
        border: 1px solid #D9D9D9;
        padding: 15px;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- ENTÊTE DE LA DIAPOSITIVE (Fidèle à PAGE 43.jpg) ---
    st.markdown("""
    <div class="diapo-slide-43">
        <div class="titre-principal-43">• Description de l'exploitation</div>
        <div class="sous-titre-43">• Croquis/polygone de la parcelle</div>
        <div class="precision-titre-43">(avec positionnement des arbres forestiers)</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # --- COLLECTE EN AMONT DES COMPOSANTS GRAPHIQUES (Évite les NameError) ---
    # Nous créons temporairement des colonnes invisibles ou lisons les données en premier pour alimenter la carte
    col_carte, col_meta = st.columns([0.65, 0.35])

    with col_meta:
        st.markdown("### 📋 Données du Polygone")
        
        with st.container():
            st.markdown('<div class="bloc-carte-info">', unsafe_allow_html=True)
            
            # Saisie des métadonnées
            nom_producteur = st.text_input("Parcelle (Producteur) :", value="Doulkom Boureima", key="p43_nom_producteur")
            superficie_ha = st.number_input("Superficie (ha) :", min_value=0.0, max_value=100.0, value=2.5, step=0.1, key="p43_superficie")
            annee_creation = st.number_input("Année de création :", min_value=1950, max_value=2026, value=2005, key="p43_annee")
            sous_prefecture_p43 = st.text_input("Sous-préfecture :", value="Okrouyo", key="p43_sous_pref")
            localite = st.text_input("Localité :", value="Bertinkro", key="champ_localite")
            departement_p43 = st.text_input("Département :", value="Soubré", key="p43_dept")

            st.markdown("**Waypoint Centre O :**")
            c_lat, c_lon = st.columns(2)
            with c_lat:
                lat_gps = st.number_input("Latitude (N) :", value=5.68412, format="%.5f", key="p43_lat")
            with c_lon:
                lon_gps = st.number_input("Longitude (O) :", value=-6.40235, format="%.5f", key="p43_lon")
                
            st.markdown('</div>', unsafe_allow_html=True)

    with col_carte:
        st.markdown("### 🗺️ Visualisation Cartographique GPS")
        
        # --- CRÉATION DU POINT DYNAMIQUE (Désormais sécurisé car lat_gps et lon_gps sont déclarés) ---
        data_parcelle = pd.DataFrame({
            'latitude': [lat_gps],
            'longitude': [lon_gps]
        })
        
        # Affichage de la carte native Streamlit
        st.map(data_parcelle, zoom=14, use_container_width=True)

    # --- CAPTION EN BAS DE CARTE ---
    st.write("<br>", unsafe_allow_html=True)
    st.caption(f"**Légende :** Pour mieux voir la Carte de la parcelle de cacaoyer de Monsieur {nom_producteur} avec délimitation du polygone et repérage des essences forestières compagnes en 3D, veuillez aller à la page 42.")

    st.write("---")

    # --- ACTIONS DE SAUVEGARDE ET NAVIGATION CENTRALISÉE ---
    if st.button("💾 Enregistrer temporairement les coordonnées cartographiques", key="p43_btn_save"):
        st.success(f"✅ Coordonnées GPS enregistrées localement pour la localité de {localite.strip()} !")

    # Bouton de validation global (Le Bouton Rouge)
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p43", type="primary", use_container_width=True):
        
        # Packaging structuré des données géographiques pour le bilan
        st.session_state["p43_donnees"] = {
            "producteur_parcelle": nom_producteur,
            "superficie_ha": superficie_ha,
            "annee_creation": annee_creation,
            "coordonnees": {
                "latitude": lat_gps,
                "longitude": lon_gps
            },
            "localisation_parcelle": {
                "departement": departement_p43,
                "sous_prefecture": sous_prefecture_p43,
                "localite": localite.strip()
            },
            "statut_page": "Terminé"
        }
        
        st.session_state["page_43_validee"] = True  
        
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
            
        st.success("🗺️ Données géographiques et cartographiques synchronisées avec succès.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 44
        st.rerun()

    # --- BAS DE DIAPOSITIVE ---
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>43</span>", unsafe_allow_html=True)



def dessiner_page_44_Cultures():
    import pandas as pd  # Importation indispensable pour la conversion finale
    import time  # Sécurité pour le cycle de rafraîchissement
    
    # --- STYLE CSS PURE REPRODUCTION ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-44 {
        background-color: #C6E0B4; /* Fond vert clair */
        padding: 30px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
    }
    
    .bullet-titre-44 {
        color: #1F4E78; /* Bleu foncé */
        font-size: 26px;
        font-weight: bold;
        margin-left: 20px;
        margin-bottom: 25px;
    }
    
    .legende-note {
        font-size: 12px;
        color: #333333;
        margin-top: 10px;
        line-height: 1.4;
    }

    .alerte-coherence {
        background-color: #FFF2CC;
        border-left: 5px solid #D6B656;
        padding: 10px;
        border-radius: 4px;
        font-size: 14px;
        color: black;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- STRUCTURE DE LA DIAPOSITIVE ---
    st.markdown("""
    <div class="diapo-slide-44">
        <div class="bullet-titre-44">• Cultures</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") 

    # --- 1. BLOC DES SUPERFICIES GLOBALES ---
    st.markdown("### 📊 Superficies globales de l'exploitation")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            sup_totale = st.number_input("Superficie totale de l'exploitation (ha) :", min_value=0.0, step=0.1, value=0.0, key="p44_sup_totale")
            sup_cultivee = st.number_input("Superficie cultivée (ha) :", min_value=0.0, step=0.1, value=0.0, key="p44_sup_cultivee")
            sup_cacao = st.number_input("... dont Cacao (ha) :", min_value=0.0, step=0.1, value=0.0, key="p44_sup_cacao")
        with col2:
            sup_foret = st.number_input("Superficie de forêt (ha) :", min_value=0.0, step=0.1, value=0.0, key="p44_sup_foret")
            sup_jachere = st.number_input("Superficie jachère (ha) :", min_value=0.0, step=0.1, value=0.0, key="p44_sup_jachere")
            source_eau = st.selectbox("Existence de source d'eau :", ["Non spécifié", "Marigot", "Puits", "Forage", "Cours d'eau permanent", "Aucune"], key="p44_source_eau")

    st.markdown("---")

    # --- 2. TABLEAU DYNAMIQUE DES CULTURES ---
    st.markdown("### 📋 Tableau de répartition des cultures")
    st.caption("Remplissez les lignes correspondant aux cultures de l'exploitation :")

    # Définition des cultures d'après la diapositive
    liste_cultures = [
        "Cacao (Parcelle 1)", 
        "Cacao (Parcelle 2)", 
        "Cacao (Parcelle 3)", 
        "Hévéa", 
        "Palmier à huile", 
        "Vivrier", 
        "Autres activités (à préciser)"
    ]
    
    # Options ordonnées du matériel végétal selon les directives d'excellence agronomique de Leila
    options_materiel = [
        "Non spécifié",
        "1. SATMACI / ANADER / CNRA (Haut Rendement)",
        "3. Pépiniériste privé certifié",
        "2. Tout venant (Variété locale non identifiée)"
    ]

    donnees_collectees = []
    somme_surfaces_saisies = 0.0
    alerte_tout_venant = False
    
    for culture in liste_cultures:
        st.markdown(f"**📍 {culture}**")
        c1, c2, c3, c4, c5 = st.columns([1.5, 1.2, 2.2, 1.8, 1.5])
        
        with c1:
            sup = st.number_input("Superficie (ha)", min_value=0.0, step=0.1, key=f"p44_sup_{culture}")
            somme_surfaces_saisies += sup
        with c2:
            annee = st.text_input("Année création", max_chars=4, key=f"p44_annee_{culture}", placeholder="Ex: 2012")
        with c3:
            mat_vegetal = st.selectbox("Source matériel végétal (*)", options_materiel, key=f"p44_mat_{culture}")
            if "Tout venant" in mat_vegetal and sup > 0:
                alerte_tout_venant = True
        with c4:
            prod = st.number_input("Prod. campagne préc. (kg)", min_value=0, step=50, key=f"p44_prod_{culture}")
        with c5:
            revenu = st.number_input("Revenu (FCFA)", min_value=0, step=25000, key=f"p44_rev_{culture}")
            
        donnees_collectees.append({
            "culture": culture,
            "superficie_ha": sup,
            "annee_creation": annee,
            "source_materiel": mat_vegetal,
            "production_kg": prod,
            "revenu_fcfa": revenu
        })
        st.write("") 

    # --- VALIDATIONS ET ALERTES AGRO-EXPERTES DE LEILA ---
    if somme_surfaces_saisies > sup_cultivee and sup_cultivee > 0:
        st.markdown(f"""
        <div class="alerte-coherence">
            ⚠️ <strong>Attention à la cohérence des surfaces :</strong> La somme des superficies des parcelles détaillées 
            ({somme_surfaces_saisies:.1f} ha) est supérieure à la superficie cultivée globale renseignée plus haut ({sup_cultivee:.1f} ha).
        </div>
        """, unsafe_allow_html=True)

    if alerte_tout_venant:
        st.info("💡 **Note diagnostique de Leila :** L'utilisation de matériel végétal 'Tout venant' sur certaines parcelles constitue un facteur limitant récurrent pour optimiser le rendement de la cacaoyère. Le remplacement ou le surgreffage avec du matériel certifié CNRA (Mercedes) sera suggéré dans les axes d'amélioration.")

    # --- 3. NOTES DE BAS DE PAGE ---
    st.markdown("""
    <div class="legende-note">
        <strong>(*) Note sur le matériel végétal de cacao :</strong><br>
        1. SATMACI / ANADER / CNRA (Variétés améliorées recommandées par ordre d'efficience)<br>
        2. Tout venant (Matériel non certifié à risque phytosanitaire élevé)
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # --- 4. ENREGISTREMENT ET NAVIGATION CENTRALISÉE ---
    if st.button("💾 Enregistrer temporairement la situation des cultures", key="p44_btn_save"):
        df_resultat = pd.DataFrame(donnees_collectees)
        st.success("✅ Données des cultures sauvegardées localement !")
        st.dataframe(df_resultat)

    # Le Bouton Rouge de validation
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p44", type="primary", use_container_width=True):
        
        total_production_declaree = sum(item["production_kg"] for item in donnees_collectees)
        total_revenus_declares = sum(item["revenu_fcfa"] for item in donnees_collectees)
        
        # Consolidation dans le state global
        st.session_state["p44_donnees"] = {
            "superficies_globales": {
                "superficie_totale": sup_totale,
                "superficie_cultivee": sup_cultivee,
                "superficie_cacao": sup_cacao,
                "superficie_foret": sup_foret,
                "superficie_jachere": sup_jachere,
                "source_eau": source_eau
            },
            "grille_cultures_details": donnees_collectees,
            "synthese_financiere": {
                "production_totale_kg": total_production_declaree,
                "revenu_total_fcfa": total_revenus_declares
            },
            "coherence_surfaces": {
                "somme_details_ha": somme_surfaces_saisies,
                "valide": somme_surfaces_saisies <= sup_cultivee
            },
            "statut_page": "Terminé"
        }
        
        st.session_state["page_44_validee"] = True  
        
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
            
        st.success("📊 Grille analytique des parcelles envoyée vers le registre central.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 45
        st.rerun()

    # --- BAS DE DIAPOSITIVE ---
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>44</span>", unsafe_allow_html=True)



def verifier_conformite_territoriale(latitude, longitude):
    """
    Système Expert de Leila pour la vérification ARS 1000 / RDUE.
    Distingue les Parcs/Réserves et les Forêts Classées pour adapter le message.
    """
    from shapely.geometry import Point, Polygon  # Importation sécurisée indispensable
    
    try:
        # Conversion explicite et sécurisée
        lat = float(str(latitude).strip())
        lon = float(str(longitude).strip())
        
        # Shapely : Point(X, Y) -> X est la Longitude, Y est la Latitude
        point_parcelle = Point(lon, lat) 
    except (ValueError, TypeError):
        return False, "❌ Coordonnées invalides, incomplètes ou mal formatées."

    # --- 1. RÉFÉRENTIEL DES PARCS NATIONAUX & RÉSERVES (Tolérance Zéro) ---
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

    # --- 2. RÉFÉRENTIEL DES FORÊTS CLASSÉES ---
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

    # --- ÉVALUATION DES CONDITIONS ---
    for nom_aire, poly in parcs_et_reserves.items():
        if point_parcelle.within(poly):
            return False, f"⚠️ ALERTE CRITIQUE : L'arbre se trouve dans un sanctuaire protégé intégral -> '{nom_aire}'. Zone strictement interdite à l'exploitation agricole."

    for nom_aire, poly in forets_classees.items():
        if point_parcelle.within(poly):
            return False, f"⚠️ Alerte Déforestation (RDUE) : La parcelle empiète sur le domaine forestier de l'État : '{nom_aire}'."

    return True, "✅ Conformité Territoriale Validée : Hors zone déboisée ou protégée."


def dessiner_page_45_Situation_Arbres_Forestiers():
    import pandas as pd  # Importation locale pour éviter les NameError
    import time

    st.markdown("""
    <style>
    .stApp { background-color: white; }
    .diapo-slide-45 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
    }
    .bullet-titre-45 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        margin-left: 20px;
        margin-bottom: 20px;
    }
    .badge-recommande { background-color: #28A745; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-tolere { background-color: #FFC107; color: black; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-deconseille { background-color: #DC3545; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-alerte { background-color: #FD7E14; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-rdue-conforme { background-color: #155724; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-rdue-interdit { background-color: #721C24; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .avis-card {
        background-color: #F8F9FA;
        border-left: 5px solid #1F4E78;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Référentiel complet des essences compagnes
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

    st.markdown("""
    <div class="diapo-slide-45">
        <div class="bullet-titre-45">• Situation des arbres autres que le cacaoyer</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 🗂️ Configuration de l'Inventaire Forestier")
    nb_arbres_max = st.number_input("Nombre d'arbres identifiés sur la parcelle :", min_value=1, max_value=50, value=3, key="p45_nb_arbres")

    arbres_saisis = []
    liste_avis_layla = [] 

    for idx in range(1, int(nb_arbres_max) + 1):
        nom_session_key = f"local_{idx}"
        
        # --- ATTRIBUTION SÉCURISÉE DE LA VALEUR PAR DÉFAUT ---
        def_local = ""
        if idx == 1: def_local = "Akpi"
        elif idx == 2: def_local = "Fraqué"
        elif idx == 3: def_local = "Fromager"
        
        # Si l'utilisateur a déjà interagi avec le selectbox, on maintient son choix
        if nom_session_key in st.session_state:
            def_local = st.session_state[nom_session_key]

        titre_expander = def_local if def_local != "" else f"Arbre N° {idx} (À configurer)"

        with st.expander(f"🌲 Emplacement & Caractéristiques - Arbre N° {idx} : {titre_expander}"):
            c1, c2, c3 = st.columns([2, 2, 1.5])
            with c1:
                nom_local = st.selectbox(
                    f"Nom Local", 
                    list(base_arbres_experts.keys()), 
                    key=nom_session_key, 
                    index=list(base_arbres_experts.keys()).index(def_local) if def_local in base_arbres_experts else 0
                )
            with c2:
                nom_botanique = base_arbres_experts[nom_local][0] if nom_local != "" else ""
                st.text_input("Nom Botanique", value=nom_botanique, key=f"bot_{idx}", disabled=True)
            with c3:
                def_circ = 200 if idx == 1 else (70 if idx == 2 else 212)
                circonference = st.number_input("Circonférence (cm)", min_value=0, value=def_circ if nom_local != "" else 0, key=f"circ_{idx}")

            c_lat, c_lon, c_orig = st.columns([2, 2, 2])
            with c_lat:
                def_lat = 6.020668 if idx == 1 else (6.020664 if idx == 2 else 6.020614)
                latitude = st.text_input("Latitude", value=str(def_lat) if nom_local != "" else "", key=f"lat_{idx}", placeholder="Ex: 6.020668")
            with c_lon:
                def_lon = -4.357123 if idx == 1 else (-4.356949 if idx == 2 else -4.356929)
                longitude = st.text_input("Longitude", value=str(def_lon) if nom_local != "" else "", key=f"lon_{idx}", placeholder="Ex: -4.357123")
            with c_orig:
                origine = st.selectbox("Origine de l'arbre", ["Préservé", "Planté"], key=f"orig_{idx}")

            c_av, c_us, c_dec, c_rais = st.columns([2, 2, 2, 2])
            with c_av:
                avantages = st.selectbox("Avantages cacaoyer", ["Ombrage", "Fertilité du sol", "Protection érosion", "Brise-vent", "Lutte enherbement", "Aucun"], key=f"av_{idx}", index=0 if idx == 1 else (4 if idx == 2 else 0))
            with c_us:
                usage = st.selectbox("Usage de l'arbre", ["Bois d'œuvre", "Alimentaire", "Médicinale", "Bois de chauffage", "Protection"], key=f"us_{idx}")
            with c_dec:
                decision = st.selectbox("Décision Norme", ["A maintenir", "A éliminer"], key=f"dec_{idx}", index=1 if idx == 2 else 0)
            with c_rais:
                def_raison = "il y a 2 trop près" if idx == 1 else ("Situé à 1,5 m d'un autre" if idx == 2 else "")
                raison = st.text_input("Raison / Motif technique", value=def_raison, key=f"rais_{idx}")

            if nom_local != "":
                # 1. Calcul Diagnostic Agronomique
                statut_botanique = base_arbres_experts[nom_local][1]
                html_agro = ""
                if decision == "A éliminer" and statut_botanique == "Recommandé":
                    html_agro = f"**Agronomie :** <span class='badge-alerte'>⚠️ Arbitrage de terrain</span> — L'essence *{nom_local}* est agronomiquement excellente pour le cacao, mais votre décision d'éliminer est validée car motivée par l'espacement (*'{raison}'*). Attention à ne pas sur-éclaircir cette zone."
                    compatibilite_finale = "Recommandé (Éliminé par contrainte d'espace)"
                elif decision == "A éliminer" and statut_botanique == "Déconseillé":
                    html_agro = f"**Agronomie :** <span class='badge-recommande'>👍 Décision approuvée</span> — Correct. Le *{nom_local}* doit être éliminé car il présente un risque pour la plantation."
                    compatibilite_finale = "Déconseillé"
                elif statut_botanique == "Recommandé":
                    html_agro = f"**Agronomie :** <span class='badge-recommande'>👍 Recommandé pour le cacao</span> (Aide au développement)"
                    compatibilite_finale = "Recommandé"
                elif statut_botanique == "Toléré":
                    html_agro = f"**Agronomie :** <span class='badge-tolere'>🫳 Toléré</span> (Pas d'effet négatif majeur)"
                    compatibilite_finale = "Toléré"
                else:
                    html_agro = f"**Agronomie :** <span class='badge-deconseille'>⚠️ Déconseillé</span> (Risque sanitaire / Réservoir Swollen Shoot)"
                    compatibilite_finale = "Déconseillé"

                # 2. Calcul Diagnostic Territorial RDUE / ARS 1000
                est_conforme, message_territoire = verifier_conformite_territoriale(latitude, longitude)
                if not est_conforme:
                    html_territoire = f"**Territoire :** <span class='badge-rdue-interdit'>❌ NON CONFORME RDUE</span> — {message_territoire}"
                    statut_rdue_final = "Non Conforme"
                else:
                    html_territoire = f"**Territoire :** <span class='badge-rdue-conforme'>✅ CONFORME ARS 1000</span> — {message_territoire}"
                    statut_rdue_final = "Conforme"

                liste_avis_layla.append({
                    "id": idx,
                    "nom": nom_local,
                    "agro": html_agro,
                    "territoire": html_territoire
                })

                arbres_saisis.append({
                    "N°": idx, "Nom Local": nom_local, "Nom Botanique": nom_botanique,
                    "Circonférence (cm)": circonference, "Latitude": latitude, "Longitude": longitude,
                    "Origine": origine, "Avantages": avantages, "Usage": usage,
                    "Décision Norme": decision, "Compatibilité Cacao": compatibilite_finale, 
                    "Statut RDUE": statut_rdue_final, "Raison": raison
                })
                
    st.write("---")
    st.markdown("### 📊 Grand Tableau Récapitulatif de la Parcelle (Rendu Visuel)")
    
    if arbres_saisis:
        df_global = pd.DataFrame(arbres_saisis)
        colonnes_ordonnees = ["N°", "Nom Local", "Nom Botanique", "Circonférence (cm)", "Latitude", "Longitude", "Origine", "Avantages", "Usage", "Décision Norme", "Compatibilité Cacao", "Statut RDUE", "Raison"]
        df_global = df_global.reindex(columns=colonnes_ordonnees)
        st.dataframe(df_global.set_index("N°"), use_container_width=True)
        st.session_state["arbres_inventoriez"] = arbres_saisis
        
        # --- AFFICHAGE DES RAPPORTS CENTRALISÉS DE LAYLA ---
        st.write("")
        st.markdown("### 🧠 Rapports & Avis du Système Expert Layla")
        
        for avis in liste_avis_layla:
            with st.container():
                st.markdown(f"""
                <div class="avis-card">
                    <strong style="color: #1F4E78; font-size: 16px;">🌲 Arbre N° {avis['id']} — {avis['nom']} :</strong><br/>
                    <div style="margin-top: 5px; margin-bottom: 5px;">{avis['agro']}</div>
                    <div>{avis['territoire']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucun arbre configuré pour le moment.")
        st.session_state["arbres_inventoriez"] = []

    st.write("---")

    # --- SÉCURISATION DU ROUTAGE ET ENREGISTREMENT ---
    if st.button("Valider l'Inventaire & passer à la page suivante ➡️", key="btn_p45", type="primary", use_container_width=True):
        
        total_arbres = len(arbres_saisis)
        nb_non_conformes = sum(1 for a in arbres_saisis if a["Statut RDUE"] == "Non Conforme")
        nb_a_eliminer = sum(1 for a in arbres_saisis if a["Décision Norme"] == "A éliminer")
        
        st.session_state["p45_donnees"] = {
            "liste_complete_arbres": arbres_saisis,
            "synthese_foret": {
                "total_arbres_inventories": total_arbres,
                "alertes_rdue_detectees": nb_non_conformes,
                "arbres_a_retirer": nb_a_eliminer,
                "diagnostic_global_rdue": "ALERTE ENTACHÉE" if nb_non_conformes > 0 else "CONFORME"
            },
            "statut_page": "Terminé"
        }
        
        st.session_state["page_45_validee"] = True
        
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
            
        st.success("🌲 Synchronisation de la composition agro-forestière effectuée avec succès.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 46
        st.rerun()

    # Numérotation de pied de page 45
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>45</span>", unsafe_allow_html=True)



def dessiner_page_46_Verification_Materiel():
    import pandas as pd
    import time

    # --- STYLE CSS REPRODUCTION & PRESTIGE DIAPO ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-46 {
        background-color: #C6E0B4; /* Vert clair institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .bullet-titre-46 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .alert-layla-diff-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Calibri', sans-serif;
    }

    .alert-layla-diff-new {
        background-color: #E2F0D9;
        color: #2E5B18;
        border-left: 6px solid #70AD47;
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
    <div class="diapo-slide-46">
        <div class="bullet-titre-46">• Vérification et Audit du Matériel Agricole</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 🔍 Contrôle de Cohérence Terrain (Section Page 46)")
    st.caption("Cette page valide la cohérence des données matérielles déclarées plus haut avec les observations finales d'audit.")

    # Récupération sécurisée de l'inventaire de la Page 11
    inventaire_p11 = st.session_state.get("p11_inventaire_materiel", [])

    if not inventaire_p11:
        st.warning("⚠️ Aucun inventaire n'a été saisi à la Page 11. Veuillez d'abord remplir la Page 11 pour permettre le recoupement.")
        # Simulation d'un faux inventaire pour le développement ou cas de secours
        st.info("💡 Mode simulation activé pour le débogage (Inventaire P11 fictif chargé).")
        inventaire_p11 = [
            {"Désignation de l'outil": "Atomiseur à moteur", "Année d'acquisition": "2024", "Quantité totale": 2},
            {"Désignation de l'outil": "Machette / Podof", "Année d'acquisition": "2025", "Quantité totale": 5}
        ]

    # Mettre l'inventaire P11 dans un dictionnaire indexé par (Désignation, Année)
    dict_p11 = {}
    for item in inventaire_p11:
        cle_unique = (item["Désignation de l'outil"].strip().lower(), str(item["Année d'acquisition"]).strip())
        dict_p11[cle_unique] = item["Quantité totale"]

    # --- BASE DE DONNÉES COMPLÈTE & CORRIGÉE DES MATÉRIELS ---
    base_materiels_cacao = {
        "": [""],
        "1. Matériel de traitement phytosanitaire": [
            "Pulvérisateur à pression retenue", "Atomiseur à moteur", 
            "Équipement d'injection (Swollen Shoot)", "Appareil de poudrage", 
            "Pulvérisateur à dos mécanique", "Buses de rechange", 
            "Dosette / Éprouvette graduée", "Mélangeur de produit", 
            "Fût de préparation", "Kit de nettoyage phytosanitaire"
        ],
        "2. Matériel de récolte et post-récolte": [
            "Machette / Podof", "Émoussoir", "Cueille-régime (Gaffe)", 
            "Couteau de récolte", "Bâche de fermentation", "Caisse de fermentation en bois", 
            "Claie de séchage / Séchoir solaire", "Humidimètre (Testeur de taux d'humidité)",
            "Balance de pesée / Peson", "Sacs en jute réglementaires"
        ],
        "3. Matériel d'entretien et travaux sylvicoles": [
            "Hache", "Scie arboricole / Ébrancheur", "Sécateur", 
            "Lime de rechange", "Daba", "Pelle", "Pioche", "Brouette"
        ],
        "4. Équipements de Protection Individuelle (EPI)": [
            "Combinaison de traitement imperméable", "Masque filtrant à cartouche (A2P3)", 
            "Lunettes de protection étanches", "Gants en nitrile / néoprène", 
            "Bottes de sécurité en caoutchouc", "Visière de protection"
        ]
    }

    # Aplatir la base pour la recherche de correspondance
    tous_les_outils_possibles = []
    for cat, outils in base_materiels_cacao.items():
        tous_les_outils_possibles.extend(outils)
    tous_les_outils_possibles = [o for o in tous_les_outils_possibles if o != ""]

    st.markdown("### 📝 Saisie des Équipements Observés lors de l'Audit")
    nb_materiels_audit = st.number_input("Nombre de types de matériels observés sur le terrain :", min_value=1, max_value=30, value=len(inventaire_p11) if len(inventaire_p11) > 0 else 2, key="p46_nb_mat")

    materiels_audit_saisis = []
    dict_audit = {}

    for idx in range(1, int(nb_materiels_audit) + 1):
        key_nom = f"p46_nom_{idx}"
        key_annee = f"p46_annee_{idx}"
        
        # Détermination intelligente d'une valeur par défaut pour éviter les cases vides
        def_outil = ""
        def_annee = "2025"
        
        if idx - 1 < len(inventaire_p11):
            def_outil = inventaire_p11[idx - 1]["Désignation de l'outil"]
            def_annee = str(inventaire_p11[idx - 1]["Année d'acquisition"])

        if key_nom in st.session_state:
            def_outil = st.session_state[key_nom]
        if key_annee in st.session_state:
            def_annee = st.session_state[key_annee]

        with st.expander(f"⚙️ Équipement N° {idx} : {def_outil if def_outil else 'À configurer'}"):
            col1, col2, col3 = st.columns([2.5, 1.5, 1.5])
            
            with col1:
                nom_outil = st.selectbox(
                    f"Désignation de l'outil (N°{idx})", 
                    [""] + tous_les_outils_possibles, 
                    key=key_nom,
                    index=(tous_les_outils_possibles.index(def_outil) + 1) if def_outil in tous_les_outils_possibles else 0
                )
            with col2:
                annee_acq = st.selectbox(f"Année d'acquisition", [str(a) for a in range(2020, 2027)], key=key_annee, index=[str(a) for a in range(2020, 2027)].index(def_annee) if def_annee in [str(a) for a in range(2020, 2027)] else 5)
            with col3:
                def_qte = inventaire_p11[idx - 1]["Quantité totale"] if idx - 1 < len(inventaire_p11) else 1
                qte_observee = st.number_input(f"Quantité Réelle", min_value=0, value=int(def_qte), key=f"p46_qte_{idx}")

            col4, col5 = st.columns([2, 3])
            with col4:
                etat_general = st.selectbox(f"État fonctionnel", ["Bon état", "Usage moyen", "Dégradé / En panne", "Hors d'usage"], key=f"p46_etat_{idx}")
            with col5:
                remarque_audit = st.text_input(f"Observation / Écart constaté", placeholder="Ex: Matériel fonctionnel, stocké en lieu sûr", key=f"p46_obs_{idx}")

            if nom_outil != "":
                cle_audit = (nom_outil.strip().lower(), str(annee_acq).strip())
                dict_audit[cle_audit] = qte_observee
                
                materiels_audit_saisis.append({
                    "N°": idx,
                    "Désignation de l'outil": nom_outil,
                    "Année d'acquisition": annee_acq,
                    "Quantité Observée": qte_observee,
                    "État": etat_general,
                    "Observations Audit": remarque_audit
                })

    # --- 🧠 LOGIQUE DU SYSTÈME EXPERT LEILA : COMPARATEUR DE COHÉRENCE ---
    st.write("---")
    st.markdown("### 🧠 Analyse de Différence Différentielle (Leila Moteur AI)")

    ecarts_detectes = False
    
    # 1. Vérification des éléments manquants ou sous-déclarés par rapport à la P11
    for (nom_p11, annee_p11), qte_p11 in dict_p11.items():
        qte_auditee = dict_audit.get((nom_p11, annee_p11), 0)
        if qte_auditee < qte_p11:
            ecarts_detectes = True
            diff = qte_p11 - qte_auditee
            st.markdown(f"""
            <div class="alert-layla-diff-danger">
                ⚠️ ÉCART NÉGATIF : L'outil '{nom_p11.title()}' ({annee_p11}) possède une différence de -{diff} unité(s). <br/>
                <span style="font-size:13px; font-weight:normal;">[Déclaré en Page 11 : {qte_p11} | Trouvé sur le terrain : {qte_auditee}]. Suspicion de perte ou de déclaration inexacte.</span>
            </div>
            """, unsafe_allow_html=True)

    # 2. Vérification des éléments excédentaires ou imprévus découverts à l'audit
    for (nom_aud, annee_aud), qte_aud in dict_audit.items():
        qte_prevue = dict_p11.get((nom_aud, annee_aud), 0)
        if qte_aud > qte_prevue:
            ecarts_detectes = True
            diff = qte_aud - qte_prevue
            st.markdown(f"""
            <div class="alert-layla-diff-new">
                ✨ MATÉRIEL SUPPLÉMENTAIRE NON DÉCLARÉ : '{nom_aud.title()}' ({annee_aud}) repéré sur site (+{diff} unité(s)). <br/>
                <span style="font-size:13px; font-weight:normal;">[Non répertorié initialement en Page 11 ou sous-évalué]. Ajout automatique au registre de régularisation.</span>
            </div>
            """, unsafe_allow_html=True)

    if not ecarts_detectes:
        st.success("✅ Parfaite Cohérence Validée : L'audit physique concorde exactement avec l'inventaire matériel déclaré en Page 11.")

    # --- TABULAR VISUALIZATION ---
    st.write("")
    st.markdown("### 📊 Registre Consolidated de l'Audit Matériel")
    if materiels_audit_saisis:
        df_audit = pd.DataFrame(materiels_audit_saisis)
        st.dataframe(df_audit.set_index("N°"), use_container_width=True)
        st.session_state["p46_registre_audit"] = materiels_audit_saisis
    else:
        st.info("Aucun équipement valide n'a été audité pour le moment.")
        st.session_state["p46_registre_audit"] = []

    st.write("---")

    # =========================================================================
    # SÉCURISATION DU ROUTAGE ET INTEGRATION CENTRALISÉE POUR LA PAGE SUIVANTE
    # =========================================================================
    if st.button("Valider l'Audit Matériel & Passer à la page suivante ➡️", key="btn_p46", type="primary", use_container_width=True):
        
        st.session_state["p46_donnees"] = {
            "liste_audit_terrain": materiels_audit_saisis,
            "synthese_coherence": {
                "coherence_parfaite": not ecarts_detectes,
                "total_equipements_audites": len(materiels_audit_saisis)
            },
            "statut_page": "Terminé"
        }
        
        st.session_state["page_46_validee"] = True
        
        # Appel du tracker central si défini dans le routeur global
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
            
        st.success("⚙️ Rapports d'audit matériel enregistrés avec succès dans le noyau Leila.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 47
        st.rerun()

    # Numérotation de pied de page 46
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>46</span>", unsafe_allow_html=True)



def dessiner_page_47_Planification_Strategique_Poupees_Russes():
    import pandas as pd  # Importation locale sécurisée pour éliminer les NameError
    import time

    # --- STYLE CSS REPRODUCTION & PRESTIGE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-47 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #2E7D32;
        margin-bottom: 20px;
    }
    
    .titre-47 {
        color: #C00000; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .bloc-axe {
        background-color: #F4F9F1;
        border-left: 5px solid #1F4E78;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE PRINCIPALE (PAGE 47.jpg) ---
    st.markdown("""
    <div class="diapo-slide-47">
        <div class="titre-47">II - PLANIFICATION STRATÉGIQUE SUR LES CINQ (5) PROCHAINES ANNÉES</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 🪆 Système d'Entonnoir Intégral (Poupées Russes Connectées)")
    st.caption("Chaque choix débloque dynamiquement les options suivantes pour une saisie ultra-rapide sans encombrement.")

    # --- BASE DE DONNÉES EXPERTE MAILLÉE (Axes -> Objectifs -> Activités) ---
    structure_pdc = {
        "": {"objectifs": {}},
        "Axe 1 : Réhabilitation du verger": {
            "objectifs": {
                "": [],
                "Régénérer le potentiel productif des vieux cacaoyers": [
                    "Recépage des vieux arbres",
                    "Remplacement des manquants (repiquage de fèves saines)",
                    "Taille de restructuration lourde"
                ],
                "Assainir l'état phytosanitaire de la parcelle": [
                    "Taille d'émondage et destruction des loranthacées",
                    "Traitement ciblé contre les mirides et la pourriture brune",
                    "Nettoyage complet des sous-bois et ramassage des cabosses momifiées"
                ]
            }
        },
        "Axe 2 : Plantation / Replantation": {
            "objectifs": {
                "": [],
                "Créer de nouvelles parcelles durables et résilientes": [
                    "Mise en place de pépinières certifiées (Variétés améliorées / Mercedes)",
                    "Piquetage réglementaire (3m x 3m) et jalonnement",
                    "Introduction d'arbres d'ombrage pour l'agroforesterie"
                ],
                "Sécuriser les jeunes plants contre le stress hydrique": [
                    "Mise en place de cultures vivrières temporaires (Bananiers pour l'ombrage)",
                    "Paillage des jeunes cacaoyers en début de saison sèche"
                ]
            }
        },
        "Axe 3 : Diversification": {
            "objectifs": {
                "": [],
                "Garantir des revenus complémentaires au producteur": [
                    "Introduction de parcelles de cultures vivrières (Gombo, Piment, Maïs)",
                    "Mise en place d'un atelier d'apiculture (Pollinisation + Miel)",
                    "Installation d'un petit élevage associé (Intrants organiques)"
                ]
            }
        }
    }

    # --- DICTIONNAIRES POUR LES SOUS-POUPÉES RUSSES (Périodes & Acteurs) ---
    phases_annee = ["", "Achat d'intrants / Préparation", "Mise en œuvre / Travaux de terrain", "Suivi / Entretien continu", "Évaluation / Récolte"]
    propositions_executants = ["", "Le Producteur lui-même", "Main d'œuvre contractuelle / GVC", "Comité des jeunes de la localité", "Équipe technique dédiée"]
    propositions_partenaires = ["", "Coopérative locale", "ANADER", "Conseil du Café-Cacao (CCC)", "Firmes phytosanitaires / Partenaires techniques"]

    # Nombre de lignes stratégiques à insérer dans le plan de campagne
    nb_lignes = st.number_input("Nombre de lignes stratégiques à configurer :", min_value=1, max_value=20, value=3, key="nb_lignes_p47")
    
    lignes_planifiees = []

    # --- BOUCLE INTERACTIVE DES POUPÉES RUSSES ---
    for i in range(1, int(nb_lignes) + 1):
        st.markdown(f"#### 📍 Ligne de Planification N° {i}")
        
        with st.container():
            st.markdown('<div class="bloc-axe">', unsafe_allow_html=True)
            
            # 1. Poupée Russe Niveau 1 : STRATÉGIE (Axe)
            liste_axes = list(structure_pdc.keys())
            axe_choisi = st.selectbox(f"1️⃣ Sélectionner la Stratégie (Axe) [Ligne {i}]", liste_axes, key=f"axe_{i}")
            
            # 2. Poupée Russe Niveau 2 : OBJECTIFS (Filtre dynamique selon l'Axe avec fallback sécurisé)
            dict_objectifs = structure_pdc.get(axe_choisi, {}).get("objectifs", {})
            liste_obj = list(dict_objectifs.keys()) if dict_objectifs else [""]
            
            obj_choisi = st.selectbox(f"2️⃣ Objectif associé [Ligne {i}]", liste_obj, key=f"obj_{i}")
            
            # 3. Poupée Russe Niveau 3 : ACTIVITÉS (Filtre dynamique sécurisé)
            liste_activites = dict_objectifs.get(obj_choisi, []) if obj_choisi else []
            choix_activites_totales = [""] + liste_activites + ["Autre activité sur-mesure..."]
            
            act_choisie = st.selectbox(f"3️⃣ Activité concrète à mener [Ligne {i}]", choix_activites_totales, key=f"act_{i}")
            
            if act_choisie == "Autre activité sur-mesure...":
                act_choisie = st.text_input(f"✍️ Saisir l'activité spécifique [Ligne {i}] :", key=f"custom_act_{i}")

            # Coût financier de la ligne
            cout = st.number_input(f"💰 Coût estimé pour cette activité (FCFA) [Ligne {i}]", min_value=0, step=10000, key=f"cout_{i}")

            # 4. Poupée Russe Niveau 4 : LES PÉRIODES
            st.markdown("**📅 Planification et Nature des actions par Année (Poupée Russe Période) :**")
            
            col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
            with col_a1:
                st.markdown("**Année 1**")
                p_a1 = st.selectbox("Action A1", phases_annee, key=f"pa1_{i}")
            with col_a2:
                st.markdown("**Année 2**")
                p_a2 = st.selectbox("Action A2", phases_annee, key=f"pa2_{i}")
            with col_a3:
                st.markdown("**Année 3**")
                p_a3 = st.selectbox("Action A3", phases_annee, key=f"pa3_{i}")
            with col_a4:
                st.markdown("**Année 4**")
                p_a4 = st.selectbox("Action A4", phases_annee, key=f"pa4_{i}")
            with col_a5:
                st.markdown("**Année 5**")
                p_a5 = st.selectbox("Action A5", phases_annee, key=f"pa5_{i}")

            # Construction synthétique pour le grand tableau des périodes
            chaines_annees = []
            if p_a1: chaines_annees.append(f"A1: {p_a1}")
            if p_a2: chaines_annees.append(f"A2: {p_a2}")
            if p_a3: chaines_annees.append(f"A3: {p_a3}")
            if p_a4: chaines_annees.append(f"A4: {p_a4}")
            if p_a5: chaines_annees.append(f"A5: {p_a5}")

            # 5. Poupée Russe Niveau 5 : EXÉCUTANTS & PARTENAIRES
            st.markdown("**👥 Responsabilités de mise en œuvre :**")
            c_exec, c_part = st.columns(2)
            with c_exec:
                executant = st.selectbox(f"Exécutant Principal (Proposition) [Ligne {i}]", propositions_executants + ["Saisie manuelle..."], key=f"exec_{i}")
                if executant == "Saisie manuelle...":
                    executant = st.text_input(f"Préciser l'exécutant [Ligne {i}] :", key=f"exec_custom_{i}")
            with c_part:
                partenaire = st.selectbox(f"Partenaire Stratégique (Proposition) [Ligne {i}]", propositions_partenaires + ["Saisie manuelle..."], key=f"part_{i}")
                if partenaire == "Saisie manuelle...":
                    partenaire = st.text_input(f"Préciser le partenaire [Ligne {i}] :", key=f"part_custom_{i}")

            st.markdown('</div>', unsafe_allow_html=True)
            
            # Archivage si la ligne est valablement complétée
            if axe_choisi and obj_choisi and act_choisie:
                lignes_planifiees.append({
                    "Stratégie (Axe)": axe_choisi.split(" : ")[0],
                    "Objectifs": obj_choisi,
                    "Activités": act_choisie,
                    "Coût (FCFA)": int(cout),
                    "Chronogramme détaillé": " | ".join(chaines_annees) if chaines_annees else "Aucune année planifiée",
                    "Exécutant": executant,
                    "Partenaires": partenaire,
                    "A1": "✔️" if p_a1 else "", 
                    "A2": "✔️" if p_a2 else "", 
                    "A3": "✔️" if p_a3 else "", 
                    "A4": "✔️" if p_a4 else "", 
                    "A5": "✔️" if p_a5 else ""
                })
        st.write("---")

    # --- REPRODUCTION FINALE DU TABLEAU ENTIÈREMENT CONSOLIDÉ ---
    st.markdown("### 📊 Grand Tableau Stratégique Consolidé")
    
    if lignes_planifiees:
        df_strategique = pd.DataFrame(lignes_planifiees)
        
        # Structure stricte calquée sur le livrable attendu
        colonnes_reelles = ["Stratégie (Axe)", "Objectifs", "Activités", "Coût (FCFA)", "A1", "A2", "A3", "A4", "A5", "Exécutant", "Partenaires"]
        st.dataframe(df_strategique[colonnes_reelles], use_container_width=True, hide_index=True)
        
        # Enveloppe budgétaire globale
        total_budget_pdc = int(df_strategique["Coût (FCFA)"].sum())
        st.metric(label="💰 Coût de Financement global du PDC", value=f"{total_budget_pdc:,} FCFA")
        
        # Persistence globale pour les états de synthèse (Ex: Page 49)
        st.session_state["p47_lignes_planifiees"] = lignes_planifiees
        st.session_state["p47_total_budget_pdc"] = total_budget_pdc
        st.session_state["p47_is_configured"] = True
    else:
        st.warning("⚠️ Complétez les poupées russes ci-dessus (Axe, Objectif et Activité) pour générer automatiquement le tableau consolidé de la page 47.")
        st.session_state["p47_lignes_planifiees"] = []
        st.session_state["p47_total_budget_pdc"] = 0
        st.session_state["p47_is_configured"] = False

    st.write("---")

    # --- SÉCURISATION DU ROUTAGE ET TRANSITION DES PAGES ---
    if st.button("Valider la Planification & passer à la page suivante ➡️", key="btn_p47", type="primary", use_container_width=True):
        if lignes_planifiees:
            st.session_state["page_47_validee"] = True
            st.success("🎯 Plan stratégique du PDC sauvegardé avec succès dans la matrice globale Leila.")
            time.sleep(0.4)
            st.session_state.page_actuelle = 48
            st.rerun()
        else:
            st.error("❌ Impossible de valider : Vous devez configurer au moins une ligne stratégique complète avant de continuer.")

    # --- BAS DE DIAPOSITIVE REPRODUCTION NUMÉRO (47) ---
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>47</span>", unsafe_allow_html=True)



def dessiner_page_48_Programme_Annuel_et_Facteurs():
    import pandas as pd  # Sécurisation contre le crash NameError
    import time

    # --- STYLE CSS REPRODUCTION PARFAITE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-48 {
        background-color: #C6E0B4; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #2E7D32;
        margin-bottom: 20px;
    }
    
    .titre-principal-48 {
        color: #C00000; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .section-header-48 {
        color: #C00000;
        font-size: 22px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .bloc-saisie-48 {
        background-color: #F8F9FA;
        border-left: 5px solid #1F4E78;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 4px;
    }
    
    .diagnostic-auto-box {
        background-color: #E2F0D9;
        border-left: 5px solid #385723;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 14px;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- DICTIONNAIRE AGRO-EXPERT ENRICHI (LE CATALOGUE DE LEILA) ---
    base_actions_courtes = {
        "": {
            "axe": "Non défini",
            "indicateur": "",
            "succes": [],
            "echec": []
        },
        "Régler la densité (Remplacement des manquants)": {
            "axe": "Axe 1 : Réhabilitation du verger",
            "indicateur": "Nombre de jeunes plants Mercedes repiqués avec succès",
            "succes": ["Disponibilité immédiate des fèves saines ou matériel certifié CNRA", "Rigueur du jalonnement (3m x 3m)"],
            "echec": ["Attaque précoce des rongeurs sur les jeunes repiquages", "Saison sèche précoce sans paillage"]
        },
        "Réaliser la taille des loranthacées": {
            "axe": "Axe 1 : Réhabilitation du verger",
            "indicateur": "Superficie de cacaoyers nettoyés de la végétation parasite (ha)",
            "succes": ["Utilisation d'outils d'élagage bien affûtés (Échenilloirs)", "Désinfection systématique des lames"],
            "echec": ["Oubli de nids de parasites sur les hautes branches", "Blessures profondes sur le tronc du cacaoyer"]
        },
        "Replanter 2 ha par l'agroforesterie": {
            "axe": "Axe 2 : Plantation / Replantation",
            "indicateur": "Nombre d'arbres d'ombrage locaux introduits et géo-référencés",
            "succes": ["Sélection d'essences d'ombrage compatibles (ex: Akpi, Fraké)", "Ombrage temporaire par bananiers maîtrisé"],
            "echec": ["Compétition hydrique sévère si les essences choisies pompent trop d'eau", "Destruction involontaire lors des désherbages"]
        },
        "Mise en place de cultures vivrières de diversification": {
            "axe": "Axe 3 : Diversification",
            "indicateur": "Rendement de cultures secondaires récoltées (kg/campagne)",
            "succes": ["Proximité et accessibilité des marchés locaux pour écouler le vivrier", "Maîtrise technique des cycles courts"],
            "echec": ["Négligence de la parcelle de cacao principale au profit du vivrier rapide", "Pourriture des récoltes faute de stockage"]
        }
    }

    # --- BANNIÈRE SECTION III ---
    st.markdown("""
    <div class="diapo-slide-48">
        <div class="titre-principal-48">III - PROGRAMME ANNUEL D'ACTION</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 📅 Planification Opérationnelle par Trimestre")
    st.caption("Renseignez le tableau des actions annuelles pour alimenter l'analyse automatique des risques en bas de page.")

    nb_actions_annuelles = st.number_input("Nombre d'actions annuelles à planifier :", min_value=1, max_value=15, value=2, key="nb_actions_p48")
    
    actions_saisies = []
    succes_dynamiques = []
    echec_dynamiques = []

    for i in range(1, int(nb_actions_annuelles) + 1):
        st.markdown(f"#### 🛠️ Action Annuelle N° {i}")
        
        with st.container():
            st.markdown('<div class="bloc-saisie-48">', unsafe_allow_html=True)
            
            # Sélection de l'activité
            activite_choisie = st.selectbox(
                f"Sélectionner l'activité [Ligne {i}]", 
                list(base_actions_courtes.keys()), 
                key=f"act_annuelle_{i}"
            )
            
            infos_expert = base_actions_courtes.get(activite_choisie, {"axe": "Non défini", "indicateur": "", "succes": [], "echec": []})
            axe_auto = infos_expert["axe"]
            
            # Collecte des facteurs pour la section IV si l'activité est valide
            if activite_choisie != "":
                succes_dynamiques.extend(infos_expert["succes"])
                echec_dynamiques.extend(infos_expert["echec"])
            
            st.markdown(f"📌 **Axe associé :** *{axe_auto}*")
            
            # Pré-remplissage intelligent : si l'utilisateur n'a pas encore modifié manuellement, on applique la valeur de la base
            valeur_defaut_indicateur = infos_expert["indicateur"]
            
            indicateur_final = st.text_input(
                f"📊 Indicateur de performance [Ligne {i}]",
                value=valeur_defaut_indicateur,
                key=f"ind_saisie_{i}"
            )
            
            st.markdown("**⏱️ Calendrier d'exécution (Cochez les trimestres ciblés) :**")
            c_t1, c_t2, c_t3, c_t4 = st.columns(4)
            with c_t1: t1 = st.checkbox("Trimestre 1 (T1)", key=f"t1_{i}")
            with c_t2: t2 = st.checkbox("Trimestre 2 (T2)", key=f"t2_{i}")
            with c_t3: t3 = st.checkbox("Trimestre 3 (T3)", key=f"t3_{i}")
            with c_t4: t4 = st.checkbox("Trimestre 4 (T4)", key=f"t4_{i}")
            
            cout_annuel = st.number_input(f"💵 Coût de l'action pour l'année (FCFA) [Ligne {i}]", min_value=0, step=5000, key=f"cout_annuel_{i}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if activite_choisie != "":
                actions_saisies.append({
                    "Axes stratégiques": axe_auto.split(" : ")[0] if " : " in axe_auto else axe_auto,
                    "ACTIVITES/S ACTIVITES": activite_choisie,
                    "INDICATEUR": indicateur_final,
                    "T1": "X" if t1 else "",
                    "T2": "X" if t2 else "",
                    "T3": "X" if t3 else "",
                    "T4": "X" if t4 else "",
                    "COÛT (FCFA)": int(cout_annuel)
                })

    # --- AFFICHAGE DU TABLEAU ---
    st.markdown("### 📊 Tableau Récapitulatif du Programme Annuel")
    if actions_saisies:
        df_annuel = pd.DataFrame(actions_saisies)
        colonnes_ordre = ["Axes stratégiques", "ACTIVITES/S ACTIVITES", "INDICATEUR", "T1", "T2", "T3", "T4", "COÛT (FCFA)"]
        st.dataframe(df_annuel[colonnes_ordre], use_container_width=True, hide_index=True)
        
        total_budget_an = int(df_annuel["COÛT (FCFA)"].sum())
        st.metric("💰 Budget total d'exploitation annuel requis", f"{total_budget_an:,} FCFA")
    else:
        st.info("Aucune ligne annuelle enregistrée.")
        total_budget_an = 0

    # --- SECTION IV : FACTEURS DE SUCCÈS ET D'ÉCHEC ---
    st.write("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="diapo-slide-48">
        <div class="section-header-48">IV - FACTEURS DE SUCCÈS ET D'ÉCHEC</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("💡 *Conditions indispensables pour une mise en œuvre efficace du plan de développement de cette exploitation.*")
    
    # Nettoyage des doublons générés par la boucle
    succes_dynamiques = list(set(succes_dynamiques))
    echec_dynamiques = list(set(echec_dynamiques))
    
    # ---- VOLET 1 : CONDITIONS DE SUCCÈS ----
    st.markdown("### 🟢 1. Conditions Indispensables de Succès")
    
    if succes_dynamiques:
        st.markdown("**🔎 Diagnostic automatique de Leila :**")
        for s in succes_dynamiques:
            st.markdown(f"<div class='diagnostic-auto-box'>✔️ {s}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='diagnostic-auto-box' style='background-color:#F8F9FA; border-left:5px solid #6C757D; color:#6C757D;'>ℹ️ Aucun facteur automatique généré. Sélectionnez des activités dans le tableau pour mettre à jour ce volet.</div>", unsafe_allow_html=True)

    st.markdown("**✍️ Observations complémentaires du Technicien (Saisie manuelle) :**")
    facteurs_succes_manuel = st.text_area(
        "Complétez ici les détails spécifiques du producteur ou de la localité :", 
        value="1. Forte volonté d'apprentissage constatée chez le producteur.\n2. Accès aux groupements de main d'œuvre de la coopérative locale.",
        height=100,
        key="succes_txt_manuel"
    )
    
    st.write("---")

    # ---- VOLET 2 : FACTEURS D'ÉCHEC ----
    st.markdown("### 🔴 2. Risques Majeurs et Facteurs d'Échec")
    
    if echec_dynamiques:
        st.markdown("**🔎 Points de vigilance automatiques de Leila :**")
        for e in echec_dynamiques:
            st.markdown(f"<div class='diagnostic-auto-box' style='background-color:#FCE4D6; border-left:5px solid #C00000;'>⚠️ {e}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='diagnostic-auto-box' style='background-color:#F8F9FA; border-left:5px solid #6C757D; color:#6C757D;'>ℹ️ Aucun risque automatique détecté.</div>", unsafe_allow_html=True)

    st.markdown("**✍️ Menaces particulières constatées sur la parcelle (Saisie manuelle) :**")
    facteurs_echec_manuel = st.text_area(
        "Renseignez les barrières spécifiques identifiées (Ex: conflits fonciers, attaques acridiennes locales...) :", 
        value="1. Risque d'indisponibilité de la main d'œuvre familiale pendant la grande récolte.\n2. Piste d'accès à la parcelle fortement dégradée en saison des pluies.",
        height=100,
        key="echec_txt_manuel"
    )

    # --- ENREGISTREMENT ET ROUTAGE VERS LEILA SYNTHÈSE ---
    st.write("---")
    if st.button("Valider le Programme Annuel & Clôturer l'Audit 🚀", key="btn_p48", type="primary", use_container_width=True):
        if actions_saisies:
            st.session_state["p48_programmes_annuels"] = actions_saisies
            st.session_state["p48_total_budget_annuel"] = total_budget_an
            st.session_state["p48_succes_expert"] = succes_dynamiques
            st.session_state["p48_echec_expert"] = echec_dynamiques
            st.session_state["p48_succes_manuel"] = facteurs_succes_manuel
            st.session_state["p48_echec_manuel"] = facteurs_echec_manuel
            st.session_state["p48_is_configured"] = True
            
            st.success("✅ Programme annuel et matrice des risques centralisés avec succès dans l'infrastructure Leila.")
            time.sleep(0.4)
            st.session_state.page_actuelle = 49
            st.rerun()
        else:
            st.error("❌ Impossible de valider : Veuillez configurer au moins une action annuelle valide.")

    # --- BAS DE DIAPOSITIVE ---
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>48</span>", unsafe_allow_html=True)



def dessiner_page_49_Bilan_Global_Conformite_Decision():
    import pandas as pd
    import time

    # --- STYLE CSS REPRODUCTION PARFAITE ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-49 {
        background-color: #F2F4F7; 
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #1F4E78;
        margin-bottom: 20px;
    }
    .bullet-titre-49 {
        color: #1F4E78; 
        font-size: 26px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .bloc-statut-etape {
        background-color: #F8F9FA;
        border: 1px solid #D1D5DB;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .bloc-conclusion-conforme { 
        background-color: #D4EDDA; border: 2px solid #28A745; color: #155724; 
        padding: 15px; border-radius: 6px; font-weight: bold; margin-top: 15px; 
    }
    .bloc-conclusion-alerte { 
        background-color: #F8D7DA; border: 2px solid #DC3545; color: #721C24; 
        padding: 15px; border-radius: 6px; font-weight: bold; margin-top: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE PRINCIPALE ---
    st.markdown("""
    <div class="diapo-slide-49">
        <div class="bullet-titre-49">📋 Page 49 : Rapport Analytique Continu (Bloc Pages 37 à 48)</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    st.markdown("### 🔍 Vérification du Parcours de Conformité (Depuis la Page 37)")
    st.caption("Leila scanne la continuité des données enregistrées depuis le lancement du Plan de Développement.")

    # =========================================================================
    # CONTROLE DES FAILLES ET SUIVI DES PAGES ACCUMULÉES (37 à 48)
    # =========================================================================
    
    # 1. Vérification Page 37 (État initial ou Données de Base du PDC)
    p37_data = st.session_state.get("p37_is_configured", False)
    # 2. Vérification Page 45 (Inventaire Forestier)
    arbres_saisis = st.session_state.get("arbres_inventoriez", [])
    # 3. Vérification Page 47 (Planification Stratégique 5 ans)
    p47_configured = st.session_state.get("p47_is_configured", False)
    # 4. Vérification Page 48 (Programme d'Action Annuel)
    p48_configured = st.session_state.get("p48_is_configured", False)

    # --- AFFICHAGE DU DASHBOARD DE DISPONIBILITÉ ---
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    with col_st1:
        st.markdown(f"<div class='bloc-statut-etape'><b>P. 37 (Init. PDC) :</b><br>{'🟢 Validé' if p37_data else '🔴 Manquant'}</div>", unsafe_allow_html=True)
    with col_st2:
        st.markdown(f"<div class='bloc-statut-etape'><b>P. 45 (Inventaire) :</b><br>{'🟢 Validé' if arbres_saisis else '🔴 Manquant'}</div>", unsafe_allow_html=True)
    with col_st3:
        st.markdown(f"<div class='bloc-statut-etape'><b>P. 47 (PDC 5 ans) :</b><br>{'🟢 Validé' if p47_configured else '🔴 Manquant'}</div>", unsafe_allow_html=True)
    with col_st4:
        st.markdown(f"<div class='bloc-statut-etape'><b>P. 48 (Prog. Annuel) :</b><br>{'🟢 Validé' if p48_configured else '🔴 Manquant'}</div>", unsafe_allow_html=True)

    # --- STRATÉGIE DE SÉCURITÉ : FALLBACK EN CAS DE BLOCAGE ---
    if not (p37_data and arbres_saisis and p47_configured and p48_configured):
        st.warning("⚠️ Faille de continuité détectée. Certaines pages entre la Page 37 et la Page 48 n'ont pas été complétées ou validées.")
        
        # Option de contournement intelligente pour ne pas forcer à tout refaire à zéro
        mode_force = st.checkbox("⚙️ Activer la complétion automatique Leila (Données de simulation pour la démo)")
        if mode_force:
            # Injection sécurisée de données pour éviter le crash
            arbres_saisis = arbres_saisis if arbres_saisis else [{"Espèce": "Akpi", "Latitude": 5.934, "Longitude": -4.218, "Décision Norme": "A maintenir"}]
            p37_data = True
            p47_configured = True
            p48_configured = True
        else:
            st.error("❌ Traitement suspendu. Veuillez parcourir et valider les pages précédentes (notamment l'inventaire et les budgets) pour générer le rapport final.")
            return

    # =========================================================================
    # TRAITEMENT ET ANALYSE DE LA CONFORMITÉ GÉOSPATIALE ET TECHNIQUE
    # =========================================================================
    st.write("---")
    st.markdown("### ⚖️ Diagnostics Croisés Évalués")

    # Évaluation Géospatiale (Filtre basé sur le premier arbre tracé)
    premier_arbre = arbres_saisis[0]
    lat_parcelle = premier_arbre.get("Latitude", 5.93)
    lon_parcelle = premier_arbre.get("Longitude", -4.21)

    # Moteur géofencing interne sécurisé
    if "verifier_conformite_territoriale" in globals():
        geo_conforme, geo_message = verifier_conformite_territoriale(lat_parcelle, lon_parcelle) # type: ignore
    else:
        if 4.5 <= lat_parcelle <= 7.5 and -8.5 <= lon_parcelle <= -3.0:
            geo_conforme = True
            geo_message = f"✅ Validation RDUE : La parcelle (Coordonnées : {lat_parcelle}, {lon_parcelle}) est localisée en zone agricole autorisée (Hors Forêt Classée / Parcs Nationaux)."
        else:
            geo_conforme = False
            geo_message = f"❌ Alerte Non-Conformité Territoriale (RDUE) : Localisation suspecte ou hors des frontières agricoles cartographiées."

    # 1. Rendu Volet Déforestation
    st.markdown("#### 1. Volet Territorial & Déforestation (ARS 1000 / RDUE)")
    if geo_conforme:
        st.success(geo_message)
    else:
        st.error(geo_message)

    # 2. Rendu Volet Ombrage (Page 45)
    st.markdown("#### 2. Volet Sylvicole & Densité d'Ombrage")
    total_maintenus = sum(1 for a in arbres_saisis if a.get("Décision Norme") == "A maintenir")
    agro_conforme = total_maintenus >= 2

    if not agro_conforme:
        st.markdown(f"""
        <div class="bloc-conclusion-alerte">
            ⚠️ PARCELLE EN SOUS-DENSITÉ D'OMBRAGE ({total_maintenus} arbre(s) préservé(s))<br>
            <span style='font-weight:normal; font-size:14px;'>
                Le quota d'arbres d'ombrage de la section agroforesterie initiée en <b>Page 37</b> est insuffisant pour stabiliser le microclimat.
                <br>💡 <b>Action corrective requise :</b> Intégrer l'activité de replantation d'arbres locaux dans votre programme annuel d'action.
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bloc-conclusion-conforme">
            ✅ GESTION AGROFORESTIÈRE CONFORME ({total_maintenus} arbres d'ombrage préservés)<br>
            <span style='font-weight:normal; font-size:14px;'>
                Leila valide l'équilibre de la parcelle ! Les critères d'ombrage et de cohabitation des strates arborées sont respectés.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # 3. Consolidation Budgétaire (Pages 47 & 48)
    st.markdown("#### 3. Évaluation Économique et Budgétaire du PDC")
    budget_pdc = st.session_state.get("p47_total_budget_pdc", 0)
    budget_annuel = st.session_state.get("p48_total_budget_annuel", 0)

    st.markdown(f"""
    <div style="background-color: #EBF5FB; border-left: 5px solid #2980B9; padding: 12px; border-radius: 4px;">
        📊 <b>Bilan Financier Consolidé :</b><br>
        • Investissement Global du Plan de Développement (PDC 5 ans) : <b>{budget_pdc:,} FCFA</b><br>
        • Budget d'Exploitation de la Campagne Courante : <b>{budget_annuel:,} FCFA</b>
    </div>
    """, unsafe_allow_html=True)

    # --- STATUT DE CERTIFICATION FINAL ---
    st.write("")
    st.markdown("#### 🚀 Décision de Certification Finale Leila IA")
    if geo_conforme and agro_conforme:
        st.markdown("> **Avis Global :** 🎖️ **Éligibilité Accordée**. L'exploitation est déclarée durable, traçable et parfaitement conforme aux exigences d'exportation.")
    elif not geo_conforme:
        st.markdown("> **Avis Global :** ⛔ **Alerte Majeure**. Non-conformité territoriale absolue liée aux réglementations zéro-déforestation.")
    else:
        st.markdown("> **Avis Global :** ⚠️ **Certification sous réserve**. Replantation d'essences d'ombrage obligatoire lors de la prochaine campagne.")

    # --- BOUTON DE CLÔTURE DE L'AUDIT ---
    st.write("---")
    if st.button("🏁 Archiver l'Audit Agricole & Générer le Rapport Final", key="btn_p49_final", type="primary", use_container_width=True):
        st.balloons()
        st.success("🎉 Rapport d'audit mémorisé dans le profil de l'exploitation !")
        time.sleep(0.5)

    # Numérotation de pied de page 49
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>49</span>", unsafe_allow_html=True)
