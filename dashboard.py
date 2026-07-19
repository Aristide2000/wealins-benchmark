"""
dashboard.py
============
Interface web interactive — Wealins LLM Benchmark
Lancé avec : streamlit run dashboard.py

Pages :
1. Classement général
2. Analyse par critère
3. Réponses complètes
4. Évolution temporelle
"""

import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from questions import QUESTIONS, CRITERES
from src.loader import (
    charger_dernier_benchmark,
    charger_historique
)
from src.utils import formater_classement

# ============================================================
# CONFIGURATION PAGE
# ============================================================

st.set_page_config(
    page_title="Wealins — LLM Benchmark",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}
.carte {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border-left: 4px solid #D4A017;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 12px;
}
.header {
    background: linear-gradient(135deg, #1B3A6B, #0D2347);
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 32px;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

@st.cache_data(ttl=300)
def charger_donnees():
    """
    Charge les données avec cache 5 minutes.
    @st.cache_data = Streamlit ne recharge pas
    à chaque clic — c'est plus rapide !
    """
    return charger_dernier_benchmark()

@st.cache_data(ttl=300)
def charger_hist():
    return charger_historique()


# ============================================================
# SIDEBAR — CONTRÔLES
# ============================================================

with st.sidebar:
    st.markdown("##  À propos")
    st.markdown("---")

    st.markdown("###  Méthodologie")
    st.caption(
        "Chaque LLM répond à 10 questions métier, "
        "puis est évalué en aveugle par les autres "
        "LLMs sur 8 critères pondérés."
    )

    st.markdown("###  Pondération des critères")
    for c_id, c_info in CRITERES.items():
        pct = int(c_info["poids"] * 100)
        st.markdown(f"- **{c_info['label']}** : {pct}%")

    st.markdown("---")

    # Bouton relancer
    st.markdown("###  Nouveau run")
    if st.button(" Lancer benchmark", type="primary",
                 use_container_width=True):
        st.info("Lance : python -m src.benchmark")

    st.markdown("---")
    st.caption(" Wealins LLM Benchmark v1.0")
    st.caption(" Run trimestriel (tous les 3 mois)")

# Poids fixes (issus de questions.py)
poids = {c_id: c_info["poids"] for c_id, c_info in CRITERES.items()}

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header">
    <h1 style="margin:0;font-size:2rem;color:white;">
         Wealins — LLM Benchmark
    </h1>
    <p style="margin:8px 0 0 0;color:rgba(255,255,255,0.8)">
        Veille technologique automatisée ·
        10 questions assurance vie luxembourgeoise
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CHARGEMENT
# ============================================================

donnees   = charger_donnees()
historique = charger_hist()

# Si pas encore de données → message d'attente
if not donnees:
    st.warning(" Aucun résultat trouvé.")
    st.info("Lance d'abord : python -m src.benchmark")

    # Affiche quand même les questions
    st.markdown("###  Questions configurées")
    for q in QUESTIONS:
        st.markdown(f"**Q{q['id']}** — {q['theme']}")
        st.caption(q['question'])
    st.stop()

scores         = donnees.get("scores", {})
date_benchmark = donnees.get("date", "N/A")
classement     = formater_classement(scores)


# ============================================================
# MÉTRIQUES GLOBALES
# ============================================================

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(" Dernier run", date_benchmark)
with c2:
    st.metric(" LLMs testés", len(scores))
with c3:
    st.metric(" Questions", len(QUESTIONS))
with c4:
    top1 = classement[0]["nom"] if classement else "N/A"
    st.metric(" Meilleur LLM", top1)

st.markdown("---")


# ============================================================
# ONGLETS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    " Classement",
    " Par critère",
    " Réponses",
    " Évolution"
])


# ──────────────────────────────────────
# ONGLET 1 — CLASSEMENT
# ──────────────────────────────────────

with tab1:
    st.markdown("###  Classement général")

    # Recalcule avec poids personnalisés
    def recalc(criteres_moyens, poids_perso):
        total_p = sum(poids_perso.values())
        if total_p == 0:
            return 0
        return round(sum(
            criteres_moyens.get(c, 0) * (p / total_p)
            for c, p in poids_perso.items()
        ), 2)

    classement_perso = []
    for llm_id, data in scores.items():
        score = recalc(
            data.get("scores_criteres_moyens", {}),
            poids
        )
        classement_perso.append({
            "LLM":      data["nom"],
            "Provider": data["provider"],
            "Modèle":   data["modele"],
            "Score":    score,
            "Couleur":  data["couleur"]
        })
    classement_perso.sort(
        key=lambda x: x["Score"],
        reverse=True
    )

    # Podium Top 3
    col1, col2, col3 = st.columns(3)
    medailles = ["1", "2", "3"]
    cols      = [col1, col2, col3]

    for i, col in enumerate(cols):
        if i < len(classement_perso):
            llm = classement_perso[i]
            with col:
                st.markdown(f"""
                <div class="carte"
                     style="text-align:center;
                            border-left-color:{llm['Couleur']}">
                    <div style="font-size:2.5rem">
                        {medailles[i]}
                    </div>
                    <div style="font-family:'Syne',sans-serif;
                                font-size:1.3rem;
                                font-weight:700;
                                color:{llm['Couleur']}">
                        {llm['LLM']}
                    </div>
                    <div style="font-size:2rem;
                                font-weight:800;
                                color:#1B3A6B">
                        {llm['Score']}
                    </div>
                    <div style="font-size:0.85rem;
                                color:#888;">
                        Moyenne de {donnees.get('nb_runs', 1)} runs
                    </div>
                    <div style="color:#888;font-size:0.8rem">
                        {llm['Provider']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("")

    # Graphique barres
    df = pd.DataFrame(classement_perso)
    fig = go.Figure()
    for _, row in df.iterrows():
        fig.add_trace(go.Bar(
            y=[row["LLM"]],
            x=[row["Score"]],
            orientation="h",
            marker_color=row["Couleur"],
            name=row["LLM"],
            text=f"  {row['Score']}",
            textposition="outside",
        ))
    fig.update_layout(
        showlegend=False,
        xaxis=dict(range=[0, 11], title="Score /10"),
        yaxis=dict(autorange="reversed"),
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=13)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau
    st.markdown(f"###  Tableau détaillé (moyenne de {donnees.get('nb_runs', 1)} runs)")
    df_table = df[["LLM", "Provider", "Modèle", "Score"]].copy()
    df_table.index = range(1, len(df_table) + 1)
    st.dataframe(df_table, use_container_width=True)


# ──────────────────────────────────────
# ONGLET 2 — PAR CRITÈRE
# ──────────────────────────────────────

with tab2:
    st.markdown("###  Scores par critère")

    # Radar chart
    categories = [v["label"] for v in CRITERES.values()]
    c_ids      = list(CRITERES.keys())

    fig_radar = go.Figure()
    for llm_id, data in scores.items():
        valeurs = [
            data.get("scores_criteres_moyens", {}).get(c, 0)
            for c in c_ids
        ]
        valeurs += [valeurs[0]]
        cats    = categories + [categories[0]]

        fig_radar.add_trace(go.Scatterpolar(
            r=valeurs,
            theta=cats,
            fill="toself",
            fillcolor="rgba(100,100,100,0.1)",
            line_color=data["couleur"],
            line_width=2,
            name=data["nom"],
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(range=[0, 10])),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans")
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Heatmap
    st.markdown("###  Carte de chaleur")
    heatmap = {}
    for llm_id, data in scores.items():
        heatmap[data["nom"]] = {
            CRITERES[c]["label"]:
            data.get("scores_criteres_moyens", {}).get(c, 0)
            for c in c_ids
        }

    df_heat = pd.DataFrame(heatmap).T
    fig_heat = px.imshow(
        df_heat,
        color_continuous_scale="RdYlGn",
        zmin=0, zmax=10,
        text_auto=".1f",
        aspect="auto"
    )
    fig_heat.update_layout(
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans")
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ──────────────────────────────────────
# ONGLET 3 — RÉPONSES
# ──────────────────────────────────────

with tab3:
    st.markdown("###  Réponses complètes")

    col_q, col_l = st.columns(2)
    with col_q:
        q_choisie = st.selectbox(
            "Question",
            [f"Q{q['id']} — {q['theme']}" for q in QUESTIONS]
        )
    with col_l:
        llm_choisi = st.selectbox(
            "LLM",
            [data["nom"] for data in scores.values()]
        )

    # Récupère la question
    q_id = int(q_choisie.split("—")[0].replace("Q","").strip())
    q_texte = next(
        q["question"] for q in QUESTIONS if q["id"] == q_id
    )
    st.info(f"**Question :** {q_texte}")

    # Récupère la réponse
    llm_id_choisi = next(
        lid for lid, d in scores.items()
        if d["nom"] == llm_choisi
    )
    reponses_data = donnees.get("reponses", {})
    reponse = reponses_data.get(
        llm_id_choisi, {}
    ).get(str(q_id), "Réponse non disponible")

    couleur = scores[llm_id_choisi]["couleur"]
    st.markdown(f"""
    <div class="carte" style="border-left-color:{couleur}">
        <strong style="color:{couleur}">{llm_choisi}</strong>
        <br><br>{reponse}
    </div>
    """, unsafe_allow_html=True)

    # Scores pour cette réponse
    st.markdown("**Scores reçus :**")
    criteres_moyens = scores[llm_id_choisi].get(
        "scores_criteres_moyens", {}
    )
    cols = st.columns(4)
    for i, (c_id, c_info) in enumerate(CRITERES.items()):
        with cols[i % 4]:
            note  = criteres_moyens.get(c_id, 0)
            color = (
                "#10B981" if note >= 7
                else "#F59E0B" if note >= 5
                else "#EF4444"
            )
            st.markdown(f"""
            <div style="text-align:center;padding:10px;
                        background:#f8f9fa;border-radius:10px;
                        margin:4px">
                <div style="font-size:1.4rem;font-weight:700;
                            color:{color}">{note}/10</div>
                <div style="font-size:0.75rem;color:#666">
                    {c_info['label']}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ──────────────────────────────────────
# ONGLET 4 — ÉVOLUTION
# ──────────────────────────────────────

with tab4:
    st.markdown("###  Évolution dans le temps")

    if len(historique) < 2:
        st.info("""
         L'historique s'enrichit à chaque run !

        **Comment ça fonctionne :**
        - Le benchmark tourne tous les 3 mois
          via GitHub Actions
        - Chaque run est sauvegardé
        - Tu verras ici qui progresse et qui régresse
        """)
    else:
        evol = []
        for entry in historique:
            for item in entry.get("classement", []):
                evol.append({
                    "Date":  entry["date"],
                    "LLM":   item["llm"],
                    "Score": item["score"]
                })

        df_evol = pd.DataFrame(evol)
        fig_evol = px.line(
            df_evol,
            x="Date", y="Score",
            color="LLM",
            markers=True,
            title="Évolution des scores par mois"
        )
        fig_evol.update_layout(
            yaxis=dict(range=[0, 10]),
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans")
        )
        st.plotly_chart(fig_evol, use_container_width=True)