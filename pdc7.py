

def dessiner_page_31_Programme_Annuel_Activites():
    import time  # 🟢 SÉCURITÉ 1 : Import local pour éviter le plantage du sleep
    
    # --- 1. DONNÉES ET OPTIONS ---
    choix_regler_densite = [
        {"sa": "Diagnostic initial et cartographie des surpeuplements", "ind": "10% des parcelles cartographiées"},
        {"sa": "Identifier les pieds à supprimer et marquage à la peinture", "ind": "80% des pieds à supprimer identifiés"},
        {"sa": "Supprimer les cacaoyers identifiés (Abattage ciblé)", "ind": "50% des pieds identifiés sont supprimés"},
        {"sa": "Dessouchage ou dévitalisation des souches fraîches", "ind": "40% des souches traités"},
        {"sa": "Débitage et évacuation du bois d'abattage hors du verger", "ind": "100% du bois encombrant retiré"},
        {"sa": "Essartage et nettoyage des interlignes libérés", "ind": "60% des interlignes nettoyés"},
        {"sa": "Régulation de l'ombrage permanent (arbres forestiers)", "ind": "Densité d'ombrage ajustée à 15%"},
        {"sa": "Rajeunissement par recépage des vieux troncs viables", "ind": "30% des vieux pieds recépés"},
        {"sa": "Destruction des nids de fourmis associés aux surpeuplements", "ind": "90% des nids ciblés détruits"},
        {"sa": "Contrôle de la repousse des rejets sur souches abattues", "ind": "100% de suivi des repousses"}
    ]

    choix_entretenir = [
        {"sa": "Réaliser la taille des loranthacées (Émondage du Gui)", "ind": "80% des loranthus sont supprimés"},
        {"sa": "Faire la taille d'entretien (Aération de la canopée)", "ind": "La taille réalisée à 90%"},
        {"sa": "Faire la récolte sanitaire (Élimination des cabosses pourries)", "ind": "Récolte sanitaire réalisée à 80%"},
        {"sa": "Taille de formation sur les jeunes cacaoyers", "ind": "70% des jeunes arbres structurés"},
        {"sa": "Égourmandage systématique (Retrait des rejets épuisants)", "ind": "100% des gourmands éliminés"},
        {"sa": "Désherbage manuel complet au pied des arbres (Couronnement)", "ind": "Rayon de 1m propre autour du tronc"},
        {"sa": "Fauchage de l'enherbement dans les inter-rangs", "ind": "Hauteur du couvert contrôlée à 20cm"},
        {"sa": "Élagage des branches basses touchant le sol", "ind": "Zéro branche rampante sur la parcelle"},
        {"sa": "Cicatrisation des grosses plaies de taille à la pâte de cuivre", "ind": "100% des plaies > 5cm protégées"},
        {"sa": "Ramassage et compostage des débris de taille sains", "ind": "50% de la biomasse valorisée en andains"}
    ]

    liste_executeurs = ["Producteur", "Ouvrier agricole", "Applicateur certifié", "Équipe de la Coopérative"]
    liste_suivants = ["Coopérative", "ANADER", "Cabinet d'Audit", "Délégué de section"]
    liste_pourcentages = [f"{i}%" for i in range(10, 111, 10)]

    # --- 2. INITIALISATION DU SESSION_STATE ---
    defaults_p31 = {
        "p31_sa_rd": choix_regler_densite[0]["sa"],
        "p31_pct_rd": "50%",
        "p31_ex_rd": liste_executeurs[0],
        "p31_su_rd": liste_suivants[0],
        "p31_c_rd": "-",
        "p31_rd_t1": False, "p31_rd_t2": True, "p31_rd_t3": False, "p31_rd_t4": False,
        
        "p31_sa_ent": choix_entretenir[1]["sa"],
        "p31_pct_ent": "80%",
        "p31_ex_ent": liste_executeurs[0],
        "p31_su_ent": liste_suivants[1],
        "p31_c_ent": "25 000",
        "p31_ent_t1": True, "p31_ent_t2": True, "p31_ent_t3": False, "p31_ent_t4": False
    }

    for key, val in defaults_p31.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # --- 3. RENDU DES STYLES CSS EXCLUSIFS ---
    st.markdown("""
    <style>
    .header-plan-p31 {
        background-color: #D9E1F2; 
        padding: 15px;
        border: 1px solid #8FAADC;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .header-title-p31 {
        color: #1F4E78;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    .table-paa-p31 {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 13px;
        margin-top: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .table-paa-p31 th {
        background-color: #305496; 
        color: white;
        border: 1px solid black;
        padding: 8px;
        text-align: center;
    }
    .table-paa-p31 td {
        border: 1px solid black;
        padding: 6px;
        text-align: center;
        background-color: white;
        color: black !important;
    }
    .text-left-p31 { text-align: left !important; }
    
    /* Numérotation de page style PowerPoint fixe */
    .footer-page-p31 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="header-plan-p31">
        <h1 class="header-title-p31">PROGRAMME ANNUEL D'ACTIVITÉS (Axe 1 complet multi-lignes)</h1>
    </div>
    """, unsafe_allow_html=True)

    st.write("### 🛠️ Configuration simultanée de l'Axe 1")
    
    # --- 4. INTERFACE DE SAISIE AVEC VERROUILLAGE STATE ---
    # --- Bloc de Configuration : Ligne 1 (Régler la densité) ---
    with st.expander("🪵 Ligne 1 : Options pour 'Régler la densité'", expanded=True):
        col1_1, col1_2 = st.columns([2, 1])
        with col1_1:
            noms_rd = [item["sa"] for item in choix_regler_densite]
            try:
                idx_rd = noms_rd.index(st.session_state.p31_sa_rd)
            except ValueError:
                idx_rd = 0
            st.session_state.p31_sa_rd = st.selectbox("Sous-activité (Régler la densité) :", noms_rd, index=idx_rd, key="widget_sa_rd")
            fiche_rd = next(item for item in choix_regler_densite if item["sa"] == st.session_state.p31_sa_rd)
        with col1_2:
            try:
                idx_pct_rd = liste_pourcentages.index(st.session_state.p31_pct_rd)
            except ValueError:
                idx_pct_rd = 4
            st.session_state.p31_pct_rd = st.selectbox("Progression cible (RD) :", liste_pourcentages, index=idx_pct_rd, key="widget_pct_rd")
            
        col1_3, col1_4, col1_5 = st.columns(3)
        with col1_3: 
            idx_ex_rd = liste_executeurs.index(st.session_state.p31_ex_rd) if st.session_state.p31_ex_rd in liste_executeurs else 0
            st.session_state.p31_ex_rd = st.selectbox("Exécution (RD) :", liste_executeurs, index=idx_ex_rd, key="widget_ex_rd")
        with col1_4: 
            idx_su_rd = liste_suivants.index(st.session_state.p31_su_rd) if st.session_state.p31_su_rd in liste_suivants else 0
            st.session_state.p31_su_rd = st.selectbox("Suivi (RD) :", liste_suivants, index=idx_su_rd, key="widget_su_rd")
        with col1_5: 
            st.session_state.p31_c_rd = st.text_input("Coût (FCFA) (RD) :", value=st.session_state.p31_c_rd, key="widget_c_rd")
        
        st.write("*Période d'exécution (Ligne 1) :*")
        c_rd_t1, c_rd_t2, c_rd_t3, c_rd_t4 = st.columns(4)
        with c_rd_t1: st.session_state.p31_rd_t1 = st.checkbox("T1", value=st.session_state.p31_rd_t1, key="widget_rd_t1")
        with c_rd_t2: st.session_state.p31_rd_t2 = st.checkbox("T2", value=st.session_state.p31_rd_t2, key="widget_rd_t2")
        with c_rd_t3: st.session_state.p31_rd_t3 = st.checkbox("T3", value=st.session_state.p31_rd_t3, key="widget_rd_t3")
        with c_rd_t4: st.session_state.p31_rd_t4 = st.checkbox("T4", value=st.session_state.p31_rd_t4, key="widget_rd_t4")

    # --- Bloc de Configuration : Ligne 2 (Entretenir) ---
    with st.expander("🌿 Ligne 2 : Options pour 'Entretenir'", expanded=True):
        col2_1, col2_2 = st.columns([2, 1])
        with col2_1:
            noms_ent = [item["sa"] for item in choix_entretenir]
            try:
                idx_ent = noms_ent.index(st.session_state.p31_sa_ent)
            except ValueError:
                idx_ent = 1
            st.session_state.p31_sa_ent = st.selectbox("Sous-activité (Entretenir) :", noms_ent, index=idx_ent, key="widget_sa_ent")
            fiche_ent = next(item for item in choix_entretenir if item["sa"] == st.session_state.p31_sa_ent)
        with col2_2:
            try:
                idx_pct_ent = liste_pourcentages.index(st.session_state.p31_pct_ent)
            except ValueError:
                idx_pct_ent = 7
            st.session_state.p31_pct_ent = st.selectbox("Progression cible (ENT) :", liste_pourcentages, index=idx_pct_ent, key="widget_pct_ent")
            
        col2_3, col2_4, col2_5 = st.columns(3)
        with col2_3: 
            idx_ex_ent = liste_executeurs.index(st.session_state.p31_ex_ent) if st.session_state.p31_ex_ent in liste_executeurs else 0
            st.session_state.p31_ex_ent = st.selectbox("Exécution (ENT) :", liste_executeurs, index=idx_ex_ent, key="widget_ex_ent")
        with col2_4: 
            idx_su_ent = liste_suivants.index(st.session_state.p31_su_ent) if st.session_state.p31_su_ent in liste_suivants else 0
            st.session_state.p31_su_ent = st.selectbox("Suivi (ENT) :", liste_suivants, index=idx_su_ent, key="widget_su_ent")
        with col2_5: 
            st.session_state.p31_c_ent = st.text_input("Coût (FCFA) (ENT) :", value=st.session_state.p31_c_ent, key="widget_c_ent")
        
        st.write("*Période d'exécution (Ligne 2) :*")
        c_ent_t1, c_ent_t2, c_ent_t3, c_ent_t4 = st.columns(4)
        with c_ent_t1: st.session_state.p31_ent_t1 = st.checkbox("T1", value=st.session_state.p31_ent_t1, key="widget_ent_t1")
        with c_ent_t2: st.session_state.p31_ent_t2 = st.checkbox("T2", value=st.session_state.p31_ent_t2, key="widget_ent_t2")
        with c_ent_t3: st.session_state.p31_ent_t3 = st.checkbox("T3", value=st.session_state.p31_ent_t3, key="widget_ent_t3")
        with c_ent_t4: st.session_state.p31_ent_t4 = st.checkbox("T4", value=st.session_state.p31_ent_t4, key="widget_ent_t4")

    # --- 5. PARSAGE ET FUSION DES INDICATEURS ---
    def nettoyer_et_fusionner_indicateur(indicateur_brut, nouveau_pourcentage):
        parties = indicateur_brut.split(" ", 1)
        if len(parties) > 1:
            return f"{nouveau_pourcentage} {parties[1]}"
        return f"{nouveau_pourcentage} {indicateur_brut}"

    indicateur_rd_final = nettoyer_et_fusionner_indicateur(fiche_rd["ind"], st.session_state.p31_pct_rd)
    indicateur_ent_final = nettoyer_et_fusionner_indicateur(fiche_ent["ind"], st.session_state.p31_pct_ent)

    # Préparation des marqueurs visuels "X"
    x_rd1 = "X" if st.session_state.p31_rd_t1 else ""
    x_rd2 = "X" if st.session_state.p31_rd_t2 else ""
    x_rd3 = "X" if st.session_state.p31_rd_t3 else ""
    x_rd4 = "X" if st.session_state.p31_rd_t4 else ""

    x_ent1 = "X" if st.session_state.p31_ent_t1 else ""
    x_ent2 = "X" if st.session_state.p31_ent_t2 else ""
    x_ent3 = "X" if st.session_state.p31_ent_t3 else ""
    x_ent4 = "X" if st.session_state.p31_ent_t4 else ""

    # --- 6. RENDU DU TABLEAU HTML DYNAMIQUE ---
    st.write("### 👁️ Rendu Visuel Officiel de la Page 31 :")
    
    html_table = f"""
    <table class="table-paa-p31">
        <thead>
            <tr>
                <th rowspan="2">Axes stratégiques</th>
                <th rowspan="2">Activités</th>
                <th rowspan="2">Sous activités</th>
                <th rowspan="2">Indicateurs</th>
                <th colspan="4">Période</th>
                <th rowspan="2">Responsable d'exécution</th>
                <th rowspan="2">Responsable suivi</th>
                <th rowspan="2">Coût FCFA</th>
            </tr>
            <tr>
                <th style="background-color:#305496; width:30px;">T1</th>
                <th style="background-color:#305496; width:30px;">T2</th>
                <th style="background-color:#305496; width:30px;">T3</th>
                <th style="background-color:#305496; width:30px;">T4</th>
            </tr>
        </thead>
        <tbody>
            <!-- PREMIÈRE LIGNE : RÉGLER LA DENSITÉ -->
            <tr>
                <td rowspan="2" style="background-color:#F2F2F2; font-weight:bold; font-size:12px; width:15%;">Axe 1 : Réhabilitation du verger</td>
                <td style="font-weight:bold; width:12%;">Régler la densité</td>
                <td class="text-left-p31" style="background-color: #FFF2CC; font-weight:bold;">{st.session_state.p31_sa_rd}</td>
                <td class="text-left-p31" style="font-style: italic; color: #203764;">{indicateur_rd_final}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_rd1}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_rd2}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_rd3}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_rd4}</td>
                <td>{st.session_state.p31_ex_rd}</td>
                <td>{st.session_state.p31_su_rd}</td>
                <td style="font-weight:bold;">{st.session_state.p31_c_rd}</td>
            </tr>
            <!-- DEUXIÈME LIGNE : ENTRETENIR -->
            <tr>
                <td style="font-weight:bold;">Entretenir</td>
                <td class="text-left-p31" style="background-color: #FFF2CC; font-weight:bold;">{st.session_state.p31_sa_ent}</td>
                <td class="text-left-p31" style="font-style: italic; color: #203764;">{indicateur_ent_final}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_ent1}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_ent2}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_ent3}</td>
                <td style="font-weight:bold; color:red; font-size:15px; background-color:#FDF2F2;">{x_ent4}</td>
                <td>{st.session_state.p31_ex_ent}</td>
                <td>{st.session_state.p31_su_ent}</td>
                <td style="font-weight:bold; color:#C00000;">{st.session_state.p31_c_ent}</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

    # --- 7. CONSEILS AGRONOMIQUES DE LEILA ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Conseils Agronomiques de Leila :")
    
    analyses_declenchees = False

    # Analyse Chronologique Ligne 1
    trimestres_rd = [("T1", st.session_state.p31_rd_t1), 
                     ("T2", st.session_state.p31_rd_t2), 
                     ("T3", st.session_state.p31_rd_t3), 
                     ("T4", st.session_state.p31_rd_t4)]
    for t_nom, t_active in trimestres_rd:
        if t_active:
            analyses_declenchees = True
            statut, msg = analyser_trimestre_layla("Régler la densité", st.session_state.p31_sa_rd, t_nom)
            if statut == "success": st.success(msg)
            elif statut == "warning": st.warning(msg)
            elif statut == "error": st.error(msg)
            elif statut == "info": st.info(msg)

    # Analyse Chronologique Ligne 2
    trimestres_ent = [("T1", st.session_state.p31_ent_t1), 
                      ("T2", st.session_state.p31_ent_t2), 
                      ("T3", st.session_state.p31_ent_t3), 
                      ("T4", st.session_state.p31_ent_t4)]
    for t_nom, t_active in trimestres_ent:
        if t_active:
            analyses_declenchees = True
            statut, msg = analyser_trimestre_layla("Entretenir", st.session_state.p31_sa_ent, t_nom)
            if statut == "success": st.success(msg)
            elif statut == "warning": st.warning(msg)
            elif statut == "error": st.error(msg)
            elif statut == "info": st.info(msg)

    if not analyses_declenchees:
        st.info("💡 **Leila :** Cochez au moins un trimestre d'activité pour voir apparaître mes recommandations.")

    st.write("<br>", unsafe_allow_html=True)

    # --- 8. BOUTON DE NAVIGATION ET VALIDATION GLOBALE ---
    if st.button("Valider et passer à l'étape suivante ➡️", type="primary", use_container_width=True):
        # 1. On coche la case mémoire de cette page
        st.session_state["page_31_validee"] = True  
        
        # 2. 🟢 SÉCURITÉ 2 : Appels de synchronisation sécurisés
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            try:
                leila_tracker_central()
            except Exception:
                pass
                
        # 3. Message de succès et redirection
        st.success("✅ Programme annuel d'activités validé avec succès.")
        time.sleep(0.4)
        
        # 4. Changement de page vers la Page 32
        st.session_state.page_actuelle = 32
        st.rerun()

    # 🟢 SÉCURITÉ 3 : Numérotation PowerPoint officielle en bas à droite
    st.markdown('<div class="footer-page-p31">31</div>', unsafe_allow_html=True)



import streamlit as tf  # Importation standard
import re

def dessiner_page_32_Determination_Moyens_Couts():
    # --- STYLE CSS REPRODUISANT LE DESIGN DEMANDÉ ---
    st.markdown("""
    <style>
    /* Fond de page blanc */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Bandeau d'en-tête vert (Fidèle à la photo) */
    .header-bar-p32 {
        background-color: #C6EFCE; 
        border: 1.5px solid #2E7D32;
        padding: 15px 25px;
        margin-bottom: 40px;
    }

    .header-title-p32 {
        color: #006100;
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Conteneur principal aligné pour le contenu */
    .content-area-p32 {
        margin-left: 40px;
        font-family: 'Arial', sans-serif;
        color: #000000;
        font-size: 19px;
        line-height: 1.6;
    }

    /* Style pour les titres de section avec l'icône ❖ */
    .section-title-container-p32 {
        display: flex;
        align-items: flex-start;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .diamond-icon-p32 {
        color: #008080; /* Couleur teal/pétrole */
        font-size: 24px;
        margin-right: 12px;
        line-height: 1;
    }

    .section-title-text-p32 {
        color: #008080;
        font-size: 21px;
        font-weight: bold;
        text-decoration: underline;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p32 {
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
    st.markdown('<div class="header-bar-p32"><h1 class="header-title-p32">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1></div>', unsafe_allow_html=True)

    # 2. Premier bloc : Titre Fiche 8 + Paragraphe descriptif
    st.markdown("""
        <div class="section-title-container-p32">
            <span class="diamond-icon-p32">❖</span>
            <span class="section-title-text-p32">Détermination des moyens et des coûts (Fiche 8)</span>
        </div>
    """, unsafe_allow_html=True)

    # Contenu textuel principal sous le premier titre
    col_space1, col_content1 = st.columns([0.08, 0.92])
    with col_content1:
        st.markdown(
            "Les moyens sont les apports humains, matériels et financiers, grâce auxquels les actions prévues vont "
            "pouvoir s'exécuter (moyens humains, moyens d'investissement, moyens de fonctionnement)."
        )

    # 3. Deuxième bloc : Les moyens spécifiques
    st.markdown("""
        <div class="section-title-container-p32" style="margin-top: 35px;">
            <span class="diamond-icon-p32">❖</span>
            <span class="section-title-text-p32">les moyens spécifiques : c’est-à-dire les moyens nécessaires pour chacune des activités :</span>
        </div>
    """, unsafe_allow_html=True)

    # Liste à puces avec cercles (o) gérée via colonnes natives
    col_space2, col_content2 = st.columns([0.12, 0.88])
    with col_content2:
        st.markdown("**o** &nbsp; **Moyens humains :** la qualité et les hommes/mois")
        st.write("") # Espacement léger
        st.markdown("**o** &nbsp; **Moyens de production (Investissements) :** Le type, le nombre, la durée d’utilisation.")
        st.write("")
        st.markdown("**o** &nbsp; **Moyens de fonctionnement :** Le type (de biens) et le nombre")

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p32", type="primary", use_container_width=True):
        st.session_state["page_32_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 33
        st.rerun()

    # 4. Numéro de page officiel (44 comme indiqué sur ta diapo)
    st.markdown('<div class="footer-page-p32">44</div>', unsafe_allow_html=True)


def dessiner_page_33_Moyens_Globaux_Couts():
    # --- STYLE CSS REPRODUISANT LE DESIGN DE LA PAGE 32 ---
    st.markdown("""
    <style>
    /* Fond de page blanc */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Bandeau d'en-tête vert */
    .header-bar-p33 {
        background-color: #C6EFCE; 
        border: 1.5px solid #2E7D32;
        padding: 15px 25px;
        margin-bottom: 40px;
    }

    .header-title-p33 {
        color: #006100;
        font-family: 'Arial', sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }

    /* Conteneur principal aligné pour le contenu */
    .content-area-p33 {
        margin-left: 40px;
        font-family: 'Arial', sans-serif;
        color: #000000;
        font-size: 19px;
        line-height: 1.6;
    }

    /* Style pour les titres de section avec l'icône ❖ */
    .section-title-container-p33 {
        display: flex;
        align-items: flex-start;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .diamond-icon-p33 {
        color: #008080; /* Couleur teal/pétrole */
        font-size: 24px;
        margin-right: 12px;
        line-height: 1;
    }

    .section-title-text-p33 {
        color: #008080;
        font-size: 21px;
        font-weight: bold;
        text-decoration: underline;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p33 {
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
    st.markdown('<div class="header-bar-p33"><h1 class="header-title-p33">2.4.3 - PLANIFICATION DES ACTIVITÉS</h1></div>', unsafe_allow_html=True)

    # 2. Premier bloc : Moyens globaux
    st.markdown("""
        <div class="section-title-container-p33">
            <span class="diamond-icon-p33">❖</span>
            <span class="section-title-text-p33">les moyens globaux c’est-à-dire les moyens liés aux activités d’appui et de gestion.</span>
        </div>
    """, unsafe_allow_html=True)

    # 3. Deuxième bloc : Les coûts
    st.markdown("""
        <div class="section-title-container-p33" style="margin-top: 35px;">
            <span class="diamond-icon-p33">❖</span>
            <span class="section-title-text-p33">les coûts</span>
        </div>
    """, unsafe_allow_html=True)

    # Liste à puces avec cercles (o) pour les coûts
    col_space1, col_content1 = st.columns([0.12, 0.88])
    with col_content1:
        st.markdown("**o** &nbsp; Évaluer le coût des investissements ;")
        st.write("") 
        st.markdown("**o** &nbsp; Évaluer le coût de chaque activité ;")
        st.write("")
        st.markdown("**o** &nbsp; Évaluer les coûts liés aux activités d’appui et de gestion.")

    # 4. Troisième bloc : Les sources de financement
    st.markdown("""
        <div class="section-title-container-p33" style="margin-top: 35px;">
            <span class="diamond-icon-p33">❖</span>
            <span class="section-title-text-p33">les sources de financement pour chacune des activités</span>
        </div>
    """, unsafe_allow_html=True)

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p33", type="primary", use_container_width=True):
        st.session_state["page_33_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 34
        st.rerun()

    # 5. Numéro de page officiel (45 comme indiqué sur ta diapo)
    st.markdown('<div class="footer-page-p33">45</div>', unsafe_allow_html=True)


import streamlit as st
import re  

def dessiner_page_34_Tableau_Moyens_Couts():
    import time  
    
    # --- 1. Style CSS PowerPoint Académique Isolé ---
    st.markdown("""
    <style>
    .header-moyens-p34 {
        background-color: #E2EFDA;
        padding: 15px;
        border: 1px solid #A9D08E;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    .title-moyens-p34 {
        color: #375623;
        font-size: 20px;
        font-weight: bold;
        margin: 0;
        text-transform: uppercase;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    .table-container-p34 {
        width: 100%;
        overflow-x: auto;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .table-moyens-p34 {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 13px;
    }
    .table-moyens-p34 th {
        background-color: #2F5597 !important;
        color: white !important;
        border: 1px solid #000000 !important;
        padding: 8px;
        text-align: center;
        font-weight: bold;
    }
    .table-moyens-p34 td {
        border: 1px solid #000000 !important;
        padding: 6px;
        text-align: center;
        color: black !important;
        background-color: #FFFFFF !important;
    }
    .cat-row-p34 {
        background-color: #D9E1F2 !important;
        font-weight: bold !important;
        text-align: left !important;
        padding-left: 10px !important;
        color: #1F4E78 !important;
    }
    .act-row-p34 {
        background-color: #FFF2CC !important;
        font-weight: bold !important;
        text-align: left !important;
        padding-left: 10px !important;
        color: #C00000 !important;
        font-size: 14px;
    }
    .text-left-p34 { 
        text-align: left !important; 
        padding-left: 15px !important; 
    }
    .footer-page-p34 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. Banques de données immuables ---
    banque_investissement = {
        "Atomiseur thermique": "Nombre",
        "Brouette renforcée": "Nombre",
        "Machettes de qualité supérieure": "Nombre",
        "Sécateurs professionnels d'élagage": "Nombre",
        "Scies arboricoles": "Nombre",
        "Bâche de séchage en polyéthylène": "Nombre",
        "Balance romaine ou électronique": "Nombre",
        "Claies de séchage surélevées": "Nombre",
        "Équipements de Protection Individuelle (EPI)": "Kit",
        "Atomiseur de remplacement": "Nombre",
        "Podomètre ou GPS de cartographie": "Nombre"
    }

    banque_intrants = {
        "Engrais NPK (Formule Cacao)": "Sac",
        "Engrais Urée": "Sac",
        "Engrais Organique / Compost certifié": "Sac",
        "Engrais Foliaire": "Litre",
        "Insecticide : Lambda-cyhalothrine": "Litre",
        "Insecticide : Bifenthrine": "Litre",
        "Fongicide anti-pourriture brune": "Sachet",
        "Nématicide homologué": "Kg/Litre",
        "Bio-stimulant racinaire": "Litre",
        "Pâte de cuivre pour cicatrisation": "Boîte",
        "Sacs de jute pour stockage": "Nombre"
    }

    banque_mo = {
        "Main d'œuvre Permanente": "Personne",
        "Main d'œuvre Occasionnelle (Tâcheron)": "Homme/Jour",
        "Groupe de main d'œuvre (Travail communautaire)": "Coup de main"
    }

    # --- 3. Titre de la diapositive ---
    st.markdown("""
    <div class="header-moyens-p34">
        <div class="title-moyens-p34">TABLEAU DE DETERMINATION DES MOYENS ET DES COUTS</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("### ⚙️ Configuration Globale du Programme")
    
    if "p34_nb_activites" not in st.session_state:
        st.session_state.p34_nb_activites = 2

    nb_activites = st.number_input(
        "Combien d'activités voulez-vous planifier au total ?", 
        min_value=1, max_value=10, 
        value=int(st.session_state.p34_nb_activites), 
        step=1, 
        key="widget_global_nb_act"
    )
    st.session_state.p34_nb_activites = nb_activites

    donnees_activites = {}

    for a in range(1, int(nb_activites) + 1):
        st.write("---")
        st.markdown(f"#### 🛠️ Saisie des Moyens - **Activité {a}**")
        
        key_nom_act = f"p34_nom_act_{a}"
        key_choix_inv = f"p34_choix_inv_{a}"
        key_choix_int = f"p34_choix_int_{a}"
        key_choix_mo = f"p34_choix_mo_{a}"

        if key_nom_act not in st.session_state:
            st.session_state[key_nom_act] = "Réhabilitation du verger (Densité & Entretien)" if a == 1 else f"Activité {a} personnalisée"
        if key_choix_inv not in st.session_state:
            st.session_state[key_choix_inv] = []
        if key_choix_int not in st.session_state:
            st.session_state[key_choix_int] = []
        if key_choix_mo not in st.session_state:
            st.session_state[key_choix_mo] = [list(banque_mo.keys())[0]]

        act_nom = st.text_input(f"Nom de l'Activité {a} :", value=st.session_state[key_nom_act], key=f"widget_nom_act_{a}")
        st.session_state[key_nom_act] = act_nom

        choix_inv = st.multiselect(f"Sélectionnez les Investissements pour l'Activité {a} :", list(banque_investissement.keys()), default=st.session_state[key_choix_inv], key=f"widget_inv_act_{a}")
        st.session_state[key_choix_inv] = choix_inv

        choix_int = st.multiselect(f"Sélectionnez les Intrants pour l'Activité {a} :", list(banque_intrants.keys()), default=st.session_state[key_choix_int], key=f"widget_int_act_{a}")
        st.session_state[key_choix_int] = choix_int

        choix_mo = st.multiselect(f"Sélectionnez les types de Main d'œuvre pour l'Activité {a} :", list(banque_mo.keys()), default=st.session_state[key_choix_mo], key=f"widget_mo_act_{a}")
        st.session_state[key_choix_mo] = choix_mo

        elements_configures = {"investissement": [], "intrant": [], "mo": []}

        # --- GESTION : INVESTISSEMENTS ---
        if choix_inv:
            st.info(f"💰 Quantités et Coûts des Investissements sur 5 ans - Activité {a}")
            for inv in choix_inv:
                unite = banque_investissement[inv]
                st.write(f"**{inv} ({unite})**")
                cols = st.columns(5)
                years_data = {}
                for yr in range(1, 6):
                    k_q = f"p34_q_inv_{a}_{inv}_an{yr}"
                    k_c = f"p34_c_inv_{a}_{inv}_an{yr}"
                    if k_q not in st.session_state: st.session_state[k_q] = "1" if yr == 1 else "0"
                    if k_c not in st.session_state: st.session_state[k_c] = "50 000" if yr == 1 else "0"
                    
                    with cols[yr-1]:
                        q = st.text_input(f"Qté An {yr}", value=st.session_state[k_q], key=f"widget_q_inv_{a}_{inv.replace(' ', '_')}_an{yr}")
                        c = st.text_input(f"Coût An {yr}", value=st.session_state[k_c], key=f"widget_c_inv_{a}_{inv.replace(' ', '_')}_an{yr}")
                        st.session_state[k_q] = q
                        st.session_state[k_c] = c
                        years_data[yr] = {"q": q, "c": c}
                elements_configures["investissement"].append({"nom": inv, "unite": unite, "annees": years_data})

        # --- GESTION : INTRANTS ---
        if choix_int:
            st.info(f"🌿 Quantités et Coûts des Intrants sur 5 ans - Activité {a}")
            for intrant in choix_int:
                unite = banque_intrants[intrant]
                st.write(f"**{intrant} ({unite})**")
                cols = st.columns(5)
                years_data = {}
                for yr in range(1, 6):
                    k_q = f"p34_q_int_{a}_{intrant}_an{yr}"
                    k_c = f"p34_c_int_{a}_{intrant}_an{yr}"
                    if k_q not in st.session_state: st.session_state[k_q] = "10"
                    if k_c not in st.session_state: st.session_state[k_c] = "45 000"
                    
                    with cols[yr-1]:
                        q = st.text_input(f"Qté An {yr}", value=st.session_state[k_q], key=f"widget_q_int_{a}_{intrant.replace(' ', '_')}_an{yr}")
                        c = st.text_input(f"Coût An {yr}", value=st.session_state[k_c], key=f"widget_c_int_{a}_{intrant.replace(' ', '_')}_an{yr}")
                        st.session_state[k_q] = q
                        st.session_state[k_c] = c
                        years_data[yr] = {"q": q, "c": c}
                elements_configures["intrant"].append({"nom": intrant, "unite": unite, "annees": years_data})

        # --- GESTION : MAIN D'ŒUVRE ---
        if choix_mo:
            st.info(f"👥 Coûts de la Main d'œuvre sur 5 ans - Activité {a}")
            for mo_item in choix_mo:
                unite = banque_mo[mo_item]
                st.write(f"**{mo_item} ({unite})**")
                cols = st.columns(5)
                years_data = {}
                for yr in range(1, 6):
                    k_q = f"p34_q_mo_{a}_{mo_item}_an{yr}"
                    k_c = f"p34_c_mo_{a}_{mo_item}_an{yr}"
                    if k_q not in st.session_state: st.session_state[k_q] = "1"
                    if k_c not in st.session_state: st.session_state[k_c] = "150 000"
                    
                    with cols[yr-1]:
                        q = st.text_input(f"Nbre An {yr}", value=st.session_state[k_q], key=f"widget_q_mo_{a}_{mo_item.replace(' ', '_')}_an{yr}")
                        c = st.text_input(f"Coût An {yr}", value=st.session_state[k_c], key=f"widget_c_mo_{a}_{mo_item.replace(' ', '_')}_an{yr}")
                        st.session_state[k_q] = q
                        st.session_state[k_c] = c
                        years_data[yr] = {"q": q, "c": c}
                elements_configures["mo"].append({"nom": mo_item, "unite": unite, "annees": years_data})

        donnees_activites[a] = {"nom": act_nom, "elements": elements_configures}

    # --- 4. Rendu Visuel du Tableau HTML Réparé (Nettoyage strict des retours chariots) ---
    st.write("### 👁️ Rendu Visuel Structuré :")

    lignes_tableau_html = ""
    for act_id, act_data in donnees_activites.items():
        lignes_tableau_html += f'<tr><td colspan="12" class="act-row-p34 text-left-p34">Activité {act_id} : {act_data["nom"]}</td></tr>'

        # Section Investissements
        lignes_tableau_html += '<tr><td colspan="12" class="cat-row-p34">Investissement</td></tr>'
        if act_data["elements"]["investissement"]:
            for item in act_data["elements"]["investissement"]:
                ann = item["annees"]
                lignes_tableau_html += f'<tr><td class="text-left-p34">• {item["nom"]}</td><td>{item["unite"]}</td>' \
                                       f'<td>{ann[1]["q"]}</td><td>{ann[1]["c"]}</td><td>{ann[2]["q"]}</td><td>{ann[2]["c"]}</td>' \
                                       f'<td>{ann[3]["q"]}</td><td>{ann[3]["c"]}</td><td>{ann[4]["q"]}</td><td>{ann[4]["c"]}</td>' \
                                       f'<td>{ann[5]["q"]}</td><td>{ann[5]["c"]}</td></tr>'
        else:
            lignes_tableau_html += '<tr><td class="text-left-p34" style="color:gray; font-style:italic;">• Aucun investissement sélectionné</td><td colspan="11">-</td></tr>'

        # Section Intrants
        lignes_tableau_html += '<tr><td colspan="12" class="cat-row-p34">Intrants</td></tr>'
        if act_data["elements"]["intrant"]:
            for item in act_data["elements"]["intrant"]:
                ann = item["annees"]
                lignes_tableau_html += f'<tr><td class="text-left-p34">• {item["nom"]}</td><td>{item["unite"]}</td>' \
                                       f'<td>{ann[1]["q"]}</td><td>{ann[1]["c"]}</td><td>{ann[2]["q"]}</td><td>{ann[2]["c"]}</td>' \
                                       f'<td>{ann[3]["q"]}</td><td>{ann[3]["c"]}</td><td>{ann[4]["q"]}</td><td>{ann[4]["c"]}</td>' \
                                       f'<td>{ann[5]["q"]}</td><td>{ann[5]["c"]}</td></tr>'
        else:
            lignes_tableau_html += '<tr><td class="text-left-p34" style="color:gray; font-style:italic;">• Aucun intrant sélectionné</td><td colspan="11">-</td></tr>'

        # Section Main d'œuvre
        lignes_tableau_html += '<tr><td colspan="12" class="cat-row-p34">Main d\'œuvre</td></tr>'
        if act_data["elements"]["mo"]:
            for item in act_data["elements"]["mo"]:
                ann = item["annees"]
                lignes_tableau_html += f'<tr><td class="text-left-p34">• {item["nom"]}</td><td>{item["unite"]}</td>' \
                                       f'<td>{ann[1]["q"]}</td><td>{ann[1]["c"]}</td><td>{ann[2]["q"]}</td><td>{ann[2]["c"]}</td>' \
                                       f'<td>{ann[3]["q"]}</td><td>{ann[3]["c"]}</td><td>{ann[4]["q"]}</td><td>{ann[4]["c"]}</td>' \
                                       f'<td>{ann[5]["q"]}</td><td>{ann[5]["c"]}</td></tr>'
        else:
            lignes_tableau_html += '<tr><td class="text-left-p34" style="color:gray; font-style:italic;">• Aucune main d\'œuvre sélectionnée</td><td colspan="11">-</td></tr>'

    # Construction du bloc HTML final épuré
    html_table_moyens = f"""<div class="table-container-p34"><table class="table-moyens-p34"><thead><tr><th rowspan="2" style="width: 25%;">Moyens spécifiques</th><th rowspan="2" style="width: 10%;">Unités</th><th colspan="2">Année 1</th><th colspan="2">Année 2</th><th colspan="2">Année 3</th><th colspan="2">Année 4</th><th colspan="2">Année 5</th></tr><tr><th>Qté</th><th>Coût</th><th>Qté</th><th>Coût</th><th>Qté</th><th>Coût</th><th>Qté</th><th>Coût</th><th>Qté</th><th>Coût</th></tr></thead><tbody>{lignes_tableau_html}</tbody></table></div>"""
    
    # Injection stricte sans f-string résiduel pour éviter les sauts de lignes interprétés à tort
    st.markdown(html_table_moyens, unsafe_allow_html=True)

    # --- 5. Moteur d'Interprétation Pluriannuel Sécurisé ---
    st.write("### 📝 Interprétation Économique & Agronomique")
    
    totaux_par_annee = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0}
    
    for act_id in donnees_activites:
        for cat in ["investissement", "intrant", "mo"]:
            for item in donnees_activites[act_id]["elements"][cat]:
                for yr in range(1, 6):
                    raw_cost = item["annees"][yr]["c"]
                    try:
                        clean_cost = re.sub(r'[^\d.]', '', raw_cost.replace(',', '.'))
                        if clean_cost:
                            totaux_par_annee[yr] += float(clean_cost)
                    except ValueError:
                        pass

    if sum(totaux_par_annee.values()) > 0:
        interpretation_text = f"""
        **Analyse de la Trajectoire Budgétaire sur 5 ans :**
        * **Année 1 (Démarrage) :** Un budget total de **{totaux_par_annee[1]:,.0f} FCFA** est alloué. C'est l'année critique caractérisée par l'achat de l'équipement initial et le lancement des traitements de choc.
        * **Année 2 :** Les charges s'élèvent à **{totaux_par_annee[2]:,.0f} FCFA**. 
        * **Année 3 :** Les charges s'élèvent à **{totaux_par_annee[3]:,.0f} FCFA**.
        * **Année 4 :** Les charges s'élèvent à **{totaux_par_annee[4]:,.0f} FCFA**.
        * **Année 5 (Vitesse de croisière) :** Le budget récurrent se stabilise à **{totaux_par_annee[5]:,.0f} FCFA**.
        
        **Diagnostic Agronomique de Leila :**
        Le plan affiche une bonne maîtrise pluriannuelle. On constate que les coûts s'ajustent après l'Année 1, ce qui traduit une transition réussie vers une phase exclusive de maintenance du verger (application d'engrais de soutien et suivi phytosanitaire régulier) favorisant une rentabilité optimale à long terme.
        """
        st.success(interpretation_text)
    else:
        st.info("💡 Veuillez configurer des valeurs numériques de coût pour voir s'activer l'interprétation de Leila.")

    st.write("<br>", unsafe_allow_html=True)

    # --- 6. Bouton de Validation Globale ---
    if st.button("Valider et passer à l'étape suivante ➡️", type="primary", use_container_width=True):
        st.session_state["page_34_validee"] = True  
        
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            try:
                leila_tracker_central()
            except Exception:
                pass
                
        st.success("✅ Tableau des moyens et des coûts validé avec succès.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 35  
        st.rerun()

    st.markdown('<div class="footer-page-p34">46</div>', unsafe_allow_html=True)

    

def dessiner_page_35_Orientations_Pratiques():
    # --- STYLE CSS DÉDIÉ SÉCURISÉ (PARTIE IV) ---
    st.markdown("""
    <style>
    /* Conteneur central style PowerPoint Épuré */
    .transition-container-p35 {
        background-color: #FFFFFF;
        border-left: 8px solid #8B4513; /* Couleur Terre de Cacao */
        border-right: 1px solid #E0E0E0;
        border-top: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 40px;
        border-radius: 4px;
        margin-top: 40px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    .partie-label-p35 {
        color: #D35400; /* Orange dynamique */
        font-size: 18px;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 15px;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    .titre-principal-p35 {
        color: #2C3E50;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.4;
        margin: 0;
        font-family: 'Calibri', 'Arial', sans-serif;
    }
    
    .info-footer-p35 {
        margin-top: 40px;
        font-style: italic;
        color: #7F8C8D;
        font-size: 14px;
    }

    /* Numérotation de page en bas à droite */
    .footer-page-p35 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    # Rendu de la carte de transition centrale
    st.markdown("""
    <div class="transition-container-p35">
        <div class="partie-label-p35">PARTIE IV</div>
        <h1 class="titre-principal-p35">
            ORIENTATIONS POUR UNE ORGANISATION PRATIQUE<br>
            DE L'ÉLABORATION DES PDC
        </h1>
        <div class="info-footer-p35">
            Module de planification territoriale et de gouvernance de la filière
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    
    # Espace d'accompagnement agronomique
    st.info(
        "💡 **Note de l'agronome :** Cette section va regrouper les outils de gestion, "
        "le calendrier d'exécution des tâches sur le terrain, et la répartition des rôles entre les comités "
        "et les producteurs."
    )

    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p35", type="primary", use_container_width=True):
        st.session_state["page_35_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 36
        st.rerun()

    # Numérotation officielle de la page (Diapo 47)
    st.markdown('<div class="footer-page-p35">47</div>', unsafe_allow_html=True)
