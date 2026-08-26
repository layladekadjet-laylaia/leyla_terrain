def afficher():
    st.subheader("Module PDC 2")
# ==========================================================
# 4. FONCTIONS DE DESSIN DES PAGES (Contenu réel intégré)
# ==========================================================
def dessiner_page_accueil():
    st.markdown("<h1 style='text-align: center; color: #1d8348;'>BIENVENUE SUR LAYLA AGRI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1d8348;'>Logiciel de Gestion PDC ARS 1000</h3>", unsafe_allow_html=True)
    st.write("---")
    st.markdown("""
    <div style='text-align: center; font-size: 18px;'>
        Cet outil vous accompagne dans le diagnostic technique<br>
        et la planification des exploitations certifiées.
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    if st.button("COMMENCER L'IDENTIFICATION", use_container_width=True, type="primary"):
        st.session_state.page_actuelle = 0
        st.rerun()
    st.markdown("---")
    st.caption("© 2026 - Développé par Djè Akadjé - Projet Master Agro-Biodiversité")

def dessiner_page_0_identification():
    import time  # Assure-toi que l'import est bien présent
    
    st.subheader("📝 FICHE D'IDENTIFICATION DU RECENSEUR")
    
    # 1. Utilisation de clés uniques et stables liées à la page 0
    val_nom = st.session_state.get("P0_nom", "")
    val_village = st.session_state.get("P0_village", "")
    val_tel = st.session_state.get("P0_tel", "")
    val_role = st.session_state.get("P0_role", "")
    
    # Si c'est vide dans la session active, on regarde dans le tampon de Leila
    if "leila_memoire_tampon" in st.session_state:
        if not val_nom: val_nom = st.session_state.leila_memoire_tampon.get("P0_nom", "")
        if not val_village: val_village = st.session_state.leila_memoire_tampon.get("P0_village", "")
        if not val_tel: val_tel = st.session_state.leila_memoire_tampon.get("P0_tel", "")
        if not val_role: val_role = st.session_state.leila_memoire_tampon.get("P0_role", "")

    # 2. Rendu des champs avec sauvegarde en temps réel via la 'key'
    nom = st.text_input("Nom & Prénoms :", value=str(val_nom), key="P0_nom")
    village = st.text_input("Village / Localité :", value=str(val_village), key="P0_village")
    tel = st.text_input("Téléphone :", value=str(val_tel), key="P0_tel")
    role = st.text_input("Fonction / Rôle :", value=str(val_role), key="P0_role")
    
    st.write("")
    
    # 3. Bouton unique de validation et de transition (Plus propre et évite les doubles clics)
    if st.button("Valider et commencer le PDC ➡️", type="primary", use_container_width=True):
        if nom.strip() == "":
            st.warning("⚠️ Veuillez entrer au moins votre nom pour continuer.")
        else:
            # Structuration pour ton ancienne variable ou compatibilité
            st.session_state.infos_producteur = {
                "nom": nom, 
                "village": village, 
                "tel": tel, 
                "role": role
            }   
            
            # --- LE TRIPLE VERROU DE SÉCURITÉ DE LEILA IA ---
            
            # 1. Sauvegarde via ton tracker centralisé
            leila_tracker_central()
            
            # 2. COCHAGE DE LA CASE MÉMOIRE POUR TOUTE L'APPLICATION (PAGE 0 VALIDÉE)
            st.session_state["page_0_validee"] = True  
            
            # Feedback visuel pour l'utilisateur de la SCOOP
            st.success(f"✅ Identité enregistrée pour : {nom}")
            time.sleep(0.4) # Petite pause fluide
            
            # 3. Changement de page propre vers la Page 1 (Schéma de Certification)
            st.session_state.page_actuelle = 1
            st.rerun()


import streamlit as st

def dessiner_page_1_Schema_Certification():
    import time  # 🟢 SÉCURITÉ 1 : Import local pour éviter le plantage du sleep
    
    # --- 1. STYLE CSS EXCLUSIF ET SÉCURISÉ POUR LA PAGE 1 ---
    st.markdown("""
    <style>
    /* Labels des étapes du schéma */
    .step-label-p1 {
        border-radius: 8px; 
        padding: 15px; 
        text-align: center; 
        font-weight: bold;
        font-family: 'Calibri', 'Arial', sans-serif;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .lbl-engagement { background-color: #D5F5E3; border: 2px solid #27AE60; color: #196F3D; }
    .lbl-diagnostic { background-color: #FCF3CF; border: 2px solid #F39C12; color: #7E5109; }
    .lbl-execution { background-color: #EBF5FB; border: 2px solid #2980B9; color: #1B4F72; }
    .lbl-audit { background-color: #FDEDEC; border: 2px solid #C0392B; color: #641E16; }

    /* Blocs de description */
    .step-desc-p1 {
        background-color: #F8F9F9; 
        border-right: 1px solid #E0E0E0;
        border-top: 1px solid #E0E0E0;
        border-bottom: 1px solid #E0E0E0;
        padding: 12px; 
        margin-left: 10px; 
        border-radius: 0 4px 4px 0;
    }
    .desc-engagement { border-left: 5px solid #27AE60; }
    .desc-diagnostic { border-left: 5px solid #F39C12; }
    .desc-execution { border-left: 5px solid #2980B9; }
    .desc-audit { border-left: 5px solid #C0392B; }

    .step-desc-p1 span {
        color: black !important;
        font-family: 'Calibri', 'Arial', sans-serif;
        font-size: 14px;
    }

    /* Flèches de transition */
    .arrow-separator-p1 {
        text-align: center; 
        font-size: 24px; 
        margin: 8px 0;
    }

    /* Numérotation de page style PowerPoint fixe */
    .footer-page-p1 {
        position: fixed;
        bottom: 20px;
        right: 50px;
        font-size: 16px;
        font-weight: bold;
        color: #7F8C8D;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 2.2. LE SCHÉMA DE CERTIFICATION")
    st.write("---")
    
    # --- BLOC 1 : ENGAGEMENT ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-engagement">👉 ENGAGEMENT</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-engagement">
                <span>🔹 <b>Adhésion du producteur :</b> Signature de la charte d'engagement et respect du règlement intérieur du groupe.</span><br>
                <span>🔹 <b>Sensibilisation :</b> Information sur les exigences de la norme ARS 1000 et les principes de durabilité.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="arrow-separator-p1" style="color: #27AE60;">⬇️</div>', unsafe_allow_html=True)

    # --- BLOC 2 : DIAGNOSTIC ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-diagnostic">🔍 DIAGNOSTIC</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-diagnostic">
                <span>🔹 <b>Évaluation initiale :</b> Réalisation du Plan de Développement du Producteur (PDC) pour identifier les écarts.</span><br>
                <span>🔹 <b>Cartographie :</b> Délimitation des parcelles et géolocalisation pour exclure les zones de déforestation.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="arrow-separator-p1" style="color: #F39C12;">⬇️</div>', unsafe_allow_html=True)

    # --- BLOC 3 : MISE EN ŒUVRE ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-execution">🚀 MISE EN ŒUVRE</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-execution">
                <span>🔹 <b>Application des Bonnes Pratiques :</b> Pratiques agricoles, environnementales et sociales conformes à la norme.</span><br>
                <span>🔹 <b>Formations continues :</b> Renforcement des capacités du producteur sur la gestion des sols, intrants et agroforesterie.</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="arrow-separator-p1" style="color: #2980B9;">⬇️</div>', unsafe_allow_html=True)

    # --- BLOC 4 : CONTRÔLE ET AUDIT ---
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown('<div class="step-label-p1 lbl-audit">📋 AUDIT & SUIVI</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="step-desc-p1 desc-audit">
                <span>🔹 <b>Contrôle Interne :</b> Inspections régulières par l'équipe technique de la coopérative pour valider les progrès.</span><br>
                <span>🔹 <b>Audit Externe :</b> Évaluation finale par un organisme de certification indépendant pour l'obtention du certificat.</span>
            </div>
            """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # --- BOUTON DE NAVIGATION ET VALIDATION GLOBALE ---
    if st.button("Valider et passer à l'étape suivante ➡️", type="primary", use_container_width=True):
        # 1. On coche la case mémoire de cette page
        st.session_state["page_1_validee"] = True  
        
        # 2. 🟢 SÉCURITÉ 2 : Correction de la faute sur locals() et appel sécurisé
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            try:
                leila_tracker_central()
            except Exception:
                pass
                
        # 3. Message de succès et redirection
        st.success("✅ Schéma de certification validé.")
        time.sleep(0.4)
        
        # 4. Changement de page vers la Page 2
        st.session_state.page_actuelle = 2
        st.rerun()

    st.write("---")
    st.warning("**Note de conformité :** Le passage d'une étape à l'autre est conditionné par la validation des critères critiques de l'étape précédente.")
    
    # 🟢 SÉCURITÉ 3 : Numérotation PowerPoint officielle en bas à droite
    st.markdown('<div class="footer-page-p1">1</div>', unsafe_allow_html=True)



def dessiner_page_2_Exigences_Suite():
    import time # Sécurité import local
    
    st.subheader("📌 Exigences de la Norme (Suite)")
    st.markdown("<span style='color: #2e86c1; font-weight: bold;'>Le producteur doit démontrer :</span>", unsafe_allow_html=True)
    st.markdown("""
    1. Une gestion durable des ressources naturelles.
    2. Le respect des droits humains et sociaux :
        - *a. Interdiction du travail des enfants.*
        - *b. Conditions de travail décentes.*
    3. La transparence dans les transactions commerciales.
    """)
    
    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p2", type="primary", use_container_width=True):
        st.session_state["page_2_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Exigences validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 3
        st.rerun()

    # Numérotation de page PowerPoint
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>9</span>", unsafe_allow_html=True)
    st.caption("Page 2 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_3_Exigences_Norme():
    import time
    
    st.subheader("📋 Critères de Conformité")
    points = [
        "Traçabilité totale du produit.",
        "Protection des zones forestières et de la biodiversité.",
        "Usage raisonné des produits phytosanitaires.",
        "Maintien de la fertilité des sols."
    ]
    for p in points:
        st.write(f"✅ {p}")
        
    st.warning("**Note :** Toute non-conformité majeure entraîne l'exclusion du programme.")
    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p3", type="primary", use_container_width=True):
        st.session_state["page_3_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Critères de conformité validés.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 4
        st.rerun()

    # Numérotation de page PowerPoint
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>10</span>", unsafe_allow_html=True)
    st.caption("Page 3 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_4_Exigences_Fin():
    import time
    
    # Style de l'entête de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 10px; margin-bottom: 25px;'>
        <h2 style='color: #2E86C1; margin: 0; font-size: 22px; text-transform: uppercase;'>
            1.2 EXIGENCES DE LA NORME RELATIVES AU PDC
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Conteneur principal pour les points 5 et 6 (Sécurité couleur texte pour l'exécutable)
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.7; margin-left: 10px; color: black;'>
        <p><b style='color: black;'>5. Le PDC doit être révisé et mis à jour au moins une fois par an pour refléter les progrès réalisés et les changements de situation.</b></p>
        <p><b style='color: black;'>6. Les enregistrements des activités réalisées et des données collectées dans le cadre du PDC doivent être conservés pendant au moins 5 ans.</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p4", type="primary", use_container_width=True):
        st.session_state["page_4_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Exigences de conservation validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 5
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>11</span>", unsafe_allow_html=True)
    st.caption("Page 4 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_5_Etapes_Elaboration():
    import time
    
    # Style de l'entête de section principale
    st.markdown("""
    <div style='background-color: #E8F8F5; border-left: 6px solid #117A65; padding: 12px; margin-bottom: 10px;'>
        <h2 style='color: #117A65; margin: 0; font-size: 24px; font-weight: bold;'>
            II. MISE EN ŒUVRE DU PLAN DE DÉVELOPPEMENT DE LA CACAOYÈRE (PDC)
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Style du sous-titre de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 8px; margin-bottom: 25px;'>
        <h3 style='color: #2E86C1; margin: 0; font-size: 20px; text-transform: uppercase; font-weight: bold;'>
            2.1 ÉTAPES D'ÉLABORATION DU PDC
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Liste des 4 étapes d'élaboration avec sécurité de couleur CSS
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.8; margin-left: 15px; color: black;'>
        <p><b style='color: black;'>1. Réalisation du diagnostic initial</b> de la cacaoyère (évaluation des écarts par rapport à la norme).</p>
        <p><b style='color: black;'>2. Définition des objectifs</b> du producteur (à court, moyen et long terme).</p>
        <p><b style='color: black;'>3. Planification des activités</b> et des investissements nécessaires pour atteindre les objectifs.</p>
        <p><b style='color: black;'>4. Validation et signature</b> du PDC par le producteur et l'entité reconnue (coopérative).</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p5", type="primary", use_container_width=True):
        st.session_state["page_5_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Étapes d'élaboration validées.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 6
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>12</span>", unsafe_allow_html=True)
    st.caption("Page 5 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_6_Diagnostic_Initial():
    import time
    
    # Style du sous-titre de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 8px; margin-bottom: 25px;'>
        <h3 style='color: #2E86C1; margin: 0; font-size: 20px; text-transform: uppercase; font-weight: bold;'>
            2.1 ÉTAPES D'ÉLABORATION DU PDC
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Titre de l'étape en cours
    st.markdown("""
    <p style='font-size: 20px; font-weight: bold; color: #117A65; margin-left: 10px; margin-bottom: 20px;'>
        1. Le diagnostic initial doit permettre d'évaluer :
    </p>
    """, unsafe_allow_html=True)

    # Liste des 4 points d'évaluation avec couleur stabilisée
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.8; margin-left: 40px; color: black;'>
        <p style='color: black;'>– Les caractéristiques de la cacaoyère (superficie, âge, densité, etc.) ;</p>
        <p style='color: black;'>– Les pratiques agricoles actuelles du producteur ;</p>
        <p style='color: black;'>– Les aspects environnementaux (présence d'arbres d'ombrage, zones protégées) ;</p>
        <p style='color: black;'>– Les aspects sociaux (conditions de travail, logement, non-travail des enfants).</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p6", type="primary", use_container_width=True):
        st.session_state["page_6_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Éléments du diagnostic initial validés.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 7
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>13</span>", unsafe_allow_html=True)
    st.caption("Page 6 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_7_Definition_Objectifs():
    import time
    
    # Style du sous-titre de section
    st.markdown("""
    <div style='background-color: #F2F4F4; border-bottom: 3px solid #2E86C1; padding: 8px; margin-bottom: 25px;'>
        <h3 style='color: #2E86C1; margin: 0; font-size: 20px; text-transform: uppercase; font-weight: bold;'>
            2.1 ÉTAPES D'ÉLABORATION DU PDC
        </h3>
    </div>
    """, unsafe_allow_html=True)

    # Titre de l'étape en cours
    st.markdown("""
    <p style='font-size: 20px; font-weight: bold; color: #117A65; margin-left: 10px; margin-bottom: 20px;'>
        2. La définition des objectifs doit être faite à court, moyen et long terme :
    </p>
    """, unsafe_allow_html=True)

    # Liste des 3 horizons d'objectifs
    st.markdown("""
    <div style='font-size: 19px; line-height: 1.8; margin-left: 40px; color: black;'>
        <p style='color: black;'>– Court terme (1 an) : actions immédiates (taille, fertilisation, etc.) ;</p>
        <p style='color: black;'>– Moyen terme (2-3 ans) : actions progressives (ombrage, replantation, etc.) ;</p>
        <p style='color: black;'>– Long terme (4-5 ans et plus) : vision globale (renouvellement complet, diversification).</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)
    
    # Bouton de navigation et validation globale
    if st.button("Valider et passer à la page suivante ➡️", key="btn_p7", type="primary", use_container_width=True):
        st.session_state["page_7_validee"] = True  
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Horizons d'objectifs validés.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 8 # En route vers la Page 8 !
        st.rerun()

    # Numérotation de page PowerPoint
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>14</span>", unsafe_allow_html=True)
    st.caption("Page 7 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_8_Socio_Demographiques():
    import time   # 🟢 SÉCURITÉ : Imports locaux requis pour l'exécutable
    import pandas as pd
    
    # --- STYLE CSS REPRODUCTION PRESTIGE DIAPO ---
    st.markdown("""
    <style>
    .stApp { background-color: white; }
    
    .diapo-slide-8 {
        background-color: #E2F0D9; /* Vert clair institutionnel */
        padding: 25px;
        border-radius: 8px;
        font-family: 'Calibri', 'Arial', sans-serif;
        color: black;
        border-left: 8px solid #385723;
        margin-bottom: 20px;
    }
    
    .titre-8 {
        color: #1F4E78; 
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .soustitre-8 {
        color: black;
        font-size: 16px;
        font-style: italic;
        margin-top: 5px;
    }

    .alert-layla-danger {
        background-color: #FCE4D6;
        color: #C00000;
        border-left: 6px solid #C00000;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .alert-layla-ok {
        background-color: #E2F0D9;
        color: #385723;
        border-left: 6px solid #385723;
        padding: 12px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- BANNIÈRE DE LA DIAPOSITIVE (Conforme à PAGE 8.jpg) ---
    st.markdown("""
    <div class="diapo-slide-8">
        <div class="titre-8">A - Données Socio-démographiques (fiche1)</div>
        <div class="soustitre-8">
            • Les personnes vivant dans le ménage, (ii) les actifs familiaux,<br>
            • La scolarisation des enfants, (iv) les travailleurs permanents et non permanents
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- INITIALISATION DE LA MÉMOIRE DE SAISIE (Ménage) ---
    if "membres_menage" not in st.session_state:
        st.session_state.membres_menage = [
            {"Nom et prénoms": "", "Statut Famille": "1. Chef de ménage", "Statut Plantation": "2. Propriétaire", "Statut Scolaire": "1. Scolarisé", "Contact": "", "Année de naissance": 1980, "Sexe": "M", "Niveau d'instruction": "3. Primaire", "Catégorie ethnique": "1. Autochtone"}
        ]

    # --- EN-TÊTE DE GESTION DES MEMBRES ---
    st.markdown("### 👥 Saisie des membres du ménage (Poupée Russe)")
    st.caption("Déployez chaque boîte pour configurer un membre du ménage. Layla IA analysera le tableau en temps réel.")

    # Boutons d'action pour la liste dynamique
    col_btn1, col_btn2 = st.columns([0.2, 0.8])
    with col_btn1:
        if st.button("➕ Ajouter un membre", key="btn_add_m", use_container_width=True):
            st.session_state.membres_menage.append(
                {"Nom et prénoms": "", "Statut Famille": "3. Enfant", "Statut Plantation": "1. Aucun", "Statut Scolaire": "1. Scolarisé", "Contact": "", "Année de naissance": 2012, "Sexe": "F", "Niveau d'instruction": "1. Aucun", "Catégorie ethnique": "1. Autochtone"}
            )
            if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
                leila_tracker_central()
            st.rerun()
            
    with col_btn2:
        if len(st.session_state.membres_menage) > 1:
            if st.button("❌ Supprimer le dernier membre", key="btn_del_m", type="secondary"):
                st.session_state.membres_menage.pop()
                if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
                    leila_tracker_central()
                st.rerun()

    # --- EXPANDERS IMBRIQUÉS ---
    opts_famille = ["1. Chef de ménage", "2. Conjoint", "3. Enfant", "4. Autre (Préciser)"]
    opts_plant = ["1. Aucun", "2. Propriétaire", "3. Gérant", "4. MO permanent", "5. MO Temporaire"]
    opts_scol = ["1. Scolarisé", "2. Déscolarisé"]
    opts_inst = ["1. Aucun", "2. Préscolaire", "3. Primaire", "4. Secondaire", "5. Supérieur", "6. Autres (préciser)"]
    opts_eth = ["1. Autochtone", "2. Allochtone", "3. Allogène"]

    for i, membre in enumerate(st.session_state.membres_menage):
        nom_affiche = membre['Nom et prénoms'] if membre['Nom et prénoms'] else 'Non renseigné'
        label_expander = f"👤 Membre #{i+1} : {nom_affiche} ({membre['Statut Famille']})"
        
        with st.expander(label_expander, expanded=(i == len(st.session_state.membres_menage)-1)):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.session_state.membres_menage[i]["Nom et prénoms"] = st.text_input(
                    f"Nom et prénoms #{i+1}", 
                    value=str(membre["Nom et prénoms"]), 
                    key=f"p8_nom_{i}"
                )
                st.session_state.membres_menage[i]["Statut Famille"] = st.selectbox(
                    f"Statut/Famille (lien de parenté) #{i+1}",
                    opts_famille,
                    index=opts_famille.index(membre["Statut Famille"]) if membre["Statut Famille"] in opts_famille else 0,
                    key=f"p8_famille_{i}"
                )
                st.session_state.membres_menage[i]["Statut Plantation"] = st.selectbox(
                    f"Statut/Plantation #{i+1}",
                    opts_plant,
                    index=opts_plant.index(membre["Statut Plantation"]) if membre["Statut Plantation"] in opts_plant else 0,
                    key=f"p8_plant_{i}"
                )
            with c2:
                st.session_state.membres_menage[i]["Sexe"] = st.radio(
                    f"Sexe #{i+1}", 
                    ["M", "F"], 
                    index=["M", "F"].index(membre["Sexe"]) if membre["Sexe"] in ["M", "F"] else 0, 
                    horizontal=True, 
                    key=f"p8_sexe_{i}"
                )
                st.session_state.membres_menage[i]["Année de naissance"] = st.number_input(
                    f"Année de naissance #{i+1}", 
                    min_value=1930, 
                    max_value=2026, 
                    value=int(membre["Année de naissance"]), 
                    key=f"p8_naiss_{i}"
                )
                st.session_state.membres_menage[i]["Contact"] = st.text_input(
                    f"Contact (Téléphone) #{i+1}", 
                    value=str(membre["Contact"]), 
                    key=f"p8_contact_{i}"
                )
            with c3:
                st.session_state.membres_menage[i]["Statut Scolaire"] = st.selectbox(
                    f"Statut Scolaire #{i+1}",
                    opts_scol,
                    index=opts_scol.index(membre["Statut Scolaire"]) if membre["Statut Scolaire"] in opts_scol else 0,
                    key=f"p8_scol_{i}"
                )
                st.session_state.membres_menage[i]["Niveau d'instruction"] = st.selectbox(
                    f"Niveau d'instruction #{i+1}",
                    opts_inst,
                    index=opts_inst.index(membre["Niveau d'instruction"]) if membre["Niveau d'instruction"] in opts_inst else 0,
                    key=f"p8_inst_{i}"
                )
                st.session_state.membres_menage[i]["Catégorie ethnique"] = st.selectbox(
                    f"Catégorie ethnique #{i+1}",
                    opts_eth,
                    index=opts_eth.index(membre["Catégorie ethnique"]) if membre["Catégorie ethnique"] in opts_eth else 0,
                    key=f"p8_eth_{i}"
                )

    if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
        leila_tracker_central()

    # --- AFFICHAGE DU TABLEAU SYNTHÈSE ---
    st.write("---")
    st.markdown("### 📋 Tableau Récapitulatif de la Fiche 1")
    df_menage = pd.DataFrame(st.session_state.membres_menage)
    st.dataframe(df_menage, use_container_width=True)

    # --- MOTEUR DE DIAGNOSTIC AUTOMATIQUE ---
    st.write("<br>", unsafe_allow_html=True)
    st.markdown("### 🧠 Diagnostic Social Automatique par Layla IA")
    
    annee_actuelle = 2026
    alertes_decouvertes = []
    cas_travail_enfants = False
    cas_discrimination_genre = False
    cas_travail_force = False

    total_femmes = len(df_menage[df_menage["Sexe"] == "F"])
    femmes_proprio_ou_gerant = len(df_menage[(df_menage["Sexe"] == "F") & (df_menage["Statut Plantation"].isin(["2. Propriétaire", "3. Gérant"]))])
    chefs_de_menage_femme = len(df_menage[(df_menage["Sexe"] == "F") & (df_menage["Statut Famille"] == "1. Chef de ménage")])

    for index, row in df_menage.iterrows():
        age = annee_actuelle - int(row["Année de naissance"]) if row["Année de naissance"] else 0
        nom_complet = row["Nom et prénoms"] if row["Nom et prénoms"] else f"Membre #{index+1}"

        if age < 15 and row["Statut Plantation"] in ["4. MO permanent", "5. MO Temporaire"]:
            cas_travail_enfants = True
            alertes_decouvertes.append(f"🚨 **Travail des Enfants** : {nom_complet} a {age} ans et est enregistré comme Main d'œuvre ({row['Statut Plantation']}). C'est strictement interdit par la norme.")
        
        if 6 <= age <= 16 and row["Statut Scolaire"] == "2. Déscolarisé":
            alertes_decouvertes.append(f"⚠️ **Alerte Scolarisation** : Enfant en âge d'obligation scolaire ({nom_complet}, {age} ans) est marqué comme Déscolarisé.")

        if row["Statut Plantation"] == "4. MO permanent" and not row["Contact"]:
            cas_travail_force = True
            alertes_decouvertes.append(f"🚨 **Suspicion de Travail Forcé / Vulnérabilité** : Le travailleur permanent {nom_complet} n'a aucun contact téléphonique renseigné. Risque d'isolement ou de non-contractualisation.")

    if total_femmes > 0 and femmes_proprio_ou_gerant == 0 and chefs_de_menage_femme == 0:
        cas_discrimination_genre = True
        alertes_decouvertes.append("⚠️ **Risque d'Inéquité de Genre** : Aucune femme du ménage ne possède de statut de décision (Propriétaire/Gérant) malgré leur présence active au sein de l'exploitation.")

    # Injection propre des diagnostics globaux dans la session
    st.session_state["p8_travail_enfants_detecte"] = cas_travail_enfants
    st.session_state["p8_discrimination_genre_detecte"] = cas_discrimination_genre
    st.session_state["p8_travail_force_detecte"] = cas_travail_force
    st.session_state["p8_fiche_complete"] = True

    if alertes_decouvertes:
        for alerte in alertes_decouvertes:
            st.markdown(f'<div class="alert-layla-danger">{alerte}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-layla-ok">✅ Analyse Layla IA : Aucune non-conformité sociale (Discrimination, genre, travail forcé ou travail des enfants) détectée sur cette fiche.</div>', unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # 🟢 AJOUT : Bouton de validation et navigation pour la Page 8
    if st.button("Valider la Fiche Sociale et Continuer ➡️", key="btn_p8_nav", type="primary", use_container_width=True):
        st.session_state["page_8_validee"] = True
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        st.success("✅ Données socio-démographiques validées avec succès.")
        time.sleep(0.4)
        st.session_state.page_actuelle = 9
        st.rerun()

    # Numérotation en bas à droite
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #BDC3C7; font-weight: bold;'>20</span>", unsafe_allow_html=True)
    st.caption("Page 8 - Système Expert Leila (Norme ARS 1000)")


def dessiner_page_9_Description_exploitation():
    import time  # 🟢 SÉCURITÉ : Import local pour le sleep
    
    st.markdown("""
    <style>
    .stApp {
        background-color: #E8F8F5;
    }
    .main-title-p9 {
        color: #1F618D;
        font-size: 26px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 30px;
        margin-left: 20px;
    }
    .custom-bullet-list-p9 {
        font-size: 19px;
        color: black; /* 🟢 FIX : Forcer le texte en noir pour la clarté dans l'exécutable */
        line-height: 1.8;
        margin-left: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1. Titre principal exact de la fiche 2
    st.markdown('<div class="main-title-p9">B - Description de l\'exploitation (fiche2)</div>', unsafe_allow_html=True)

    # 2. Liste à puces avec balises span pour assurer la couleur du texte
    st.markdown("""
    <div class="custom-bullet-list-p9">
        <span style='color: black;'>o &nbsp; Les informations sur la plantation de cacao,</span><br>
        <span style='color: black;'>o &nbsp; les superficies des autres cultures,</span><br>
        <span style='color: black;'>o &nbsp; la taille des autres spéculations (production animale, production halieutique, etc.),</span><br>
        <span style='color: black;'>o &nbsp; les terres disponibles,</span><br>
        <span style='color: black;'>o &nbsp; les outils de travail et équipements de production disponibles sur l'exploitation,</span><br>
        <span style='color: black;'>o &nbsp; la situation des arbres autres que le cacaoyer dans la cacaoyère.</span>
    </div>
    """, unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)

    # 🟢 AJOUT : Bouton de validation et navigation pour la Page 9
    if st.button("Ouvrir la fiche de description de l'exploitation ➡️", key="btn_p9_nav", type="primary", use_container_width=True):
        st.session_state["page_9_validee"] = True
        if "leila_tracker_central" in globals() or "leila_tracker_central" in locals():
            leila_tracker_central()
        time.sleep(0.2)
        st.session_state.page_actuelle = 10  # En route vers le premier formulaire de la Fiche 2 !
        st.rerun()

    # 3. Numéro de page exact en bas à droite (21)
    st.write("<br><br>", unsafe_allow_html=True)
    col_inf1, col_inf2 = st.columns([0.95, 0.05])
    with col_inf2:
        st.markdown("<span style='color: #4A5568; font-weight: bold; font-size: 14px;'>21</span>", unsafe_allow_html=True)

    st.caption("Page 9 - Système Expert Leila (Norme ARS 1000)")



# Sécurité si la fonction globale n'est pas encore déclarée ailleurs
if "leila_tracker_central" not in globals():
    def leila_tracker_central():
        pass
