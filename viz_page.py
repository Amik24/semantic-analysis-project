from pathlib import Path
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import requests
from io import StringIO

GITHUB_REPO = "Amik24/semantic-analysis-project"
BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"

def load_from_github(file_path):
    url = f"{BASE_RAW_URL}/{file_path}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except Exception:
        return None

def render_header():
    PRIMARY = "#177E7B"
    TITLE_SIZE_REM = 3.0
    SUB_SIZE_REM = 1.15

    st.markdown(
        f"""
        <style>
          .sap-title {{
            font-size: {TITLE_SIZE_REM}rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0;
          }}
          .sap-subtitle {{
            font-size: {SUB_SIZE_REM}rem;
            color: {PRIMARY};
            margin: .35rem 0 0 0;
          }}
        </style>
        """,
        unsafe_allow_html=True
    )

    logo_url = f"{BASE_RAW_URL}/data/ECE_LOGO_2021_web.png"
    c_left, c_center, c_right = st.columns([1, 2, 1])
    with c_center:
        st.image(logo_url, width=360)

    st.markdown("<div class='sap-title'>Project – Semantic Analysis</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sap-subtitle'>Semantic Analysis for Competency Mapping and Job Profile Recommendation</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

def show_visualisations():
    render_header()
    st.subheader("Visualisations — Analyse Sémantique")

    SEUIL_FORT = 0.70

    with st.spinner("Chargement des résultats depuis GitHub..."):
        comp_content = load_from_github("outputs/competency_scores.csv")
        block_content = load_from_github("outputs/block_scores.csv")
        job_content = load_from_github("outputs/job_scores.csv")
        summary_content = load_from_github("outputs/results/summary.json")
        comp_ref_content = load_from_github("data/competencies.csv")

    missing = []
    if not comp_content: missing.append("competency_scores.csv")
    if not block_content: missing.append("block_scores.csv")
    if not job_content: missing.append("job_scores.csv")
    
    if missing:
        st.warning(
            "Fichiers manquants. Le semantic engine doit être exécuté.\n"
            + "\n".join(f"- {m}" for m in missing)
        )
        return

    comp_df = pd.read_csv(StringIO(comp_content))
    block_df = pd.read_csv(StringIO(block_content))
    job_df = pd.read_csv(StringIO(job_content))

    comp_df.columns = comp_df.columns.str.strip()
    block_df.columns = block_df.columns.str.strip()
    job_df.columns = job_df.columns.str.strip()

    summary = {}
    if summary_content:
        try:
            summary = json.loads(summary_content)
        except Exception:
            pass

    if comp_ref_content and "BlockName" not in comp_df.columns and "CompetencyID" in comp_df.columns:
        ref_comp = pd.read_csv(StringIO(comp_ref_content))
        ref_comp.columns = ref_comp.columns.str.strip()
        if {"CompetencyID", "BlockName"}.issubset(ref_comp.columns):
            comp_df = comp_df.merge(ref_comp[["CompetencyID", "BlockName"]], on="CompetencyID", how="left")

    with st.container():
        c1, c2, c3 = st.columns(3)

        final_cov = summary.get(
            "final_coverage",
            float(block_df["Score"].mean()) if "Score" in block_df.columns else None
        )

        job_score_col = next((c for c in ["JobScore", "Score", "FinalScore"] if c in job_df.columns), None)
        job_title_col = "JobTitle" if "JobTitle" in job_df.columns else job_df.columns[0]
        if job_score_col and len(job_df):
            j_sorted = job_df.sort_values(job_score_col, ascending=False)
            top_job = str(j_sorted.iloc[0][job_title_col])
            top_job_score = float(j_sorted.iloc[0][job_score_col])
        else:
            top_job, top_job_score = "—", None

        matched = int((comp_df["Score"] > 0.0).sum()) if "Score" in comp_df.columns else 0
        total = int(len(comp_df))

        c1.metric("Score global de couverture", f"{final_cov:.2f}" if final_cov is not None else "—")
        c2.metric("Métier recommandé #1", top_job, delta=(f"{top_job_score:.2f}" if top_job_score is not None else None))
        c3.metric("Compétences détectées", f"{matched}/{total}")

    st.caption("Lecture : moyenne des blocs. ≥ 0,70 = bon alignement.")
    st.markdown("---")

    st.subheader("Couverture par bloc")
    if {"BlockName", "Score"}.issubset(block_df.columns) and len(block_df) >= 3:
        b = block_df.copy()
        b["Score"] = b["Score"].clip(0, 1)
        fig = px.line_polar(b, r="Score", theta="BlockName", line_close=True, range_r=[0, 1])
        fig.update_traces(fill="toself")
        thetas = list(b["BlockName"])
        if len(thetas) >= 3:
            fig.add_trace(go.Scatterpolar(
                r=[SEUIL_FORT]*len(thetas),
                theta=thetas,
                mode="lines",
                line=dict(dash="dash"),
                name=f"Seuil {SEUIL_FORT:.2f}"
            ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Il faut 'BlockName' et 'Score' dans block_scores.csv.")

    st.subheader("Top compétences par similarité")
    if {"CompetencyText", "Score"}.issubset(comp_df.columns):
        default_n = min(10, len(comp_df))
        top_n = st.slider("Nombre de compétences à afficher :", 5, 35, default_n, step=1)

        top_comp = comp_df.sort_values("Score", ascending=False).head(top_n)

        fig2 = px.bar(
            top_comp.sort_values("Score"),
            x="Score",
            y="CompetencyText",
            orientation="h",
            range_x=[0, 1]
        )
        fig2.add_vline(
            x=SEUIL_FORT,
            line_dash="dash",
            annotation_text=f"Seuil {SEUIL_FORT:.2f}",
            annotation_position="top left"
        )
        st.plotly_chart(fig2, use_container_width=True)

        with st.expander("Voir le tableau détaillé"):
            st.dataframe(top_comp.reset_index(drop=True))
    else:
        st.info("Il faut 'CompetencyText' et 'Score' dans competency_scores.csv.")

    st.subheader("Détail par bloc")
    if "BlockName" in comp_df.columns:
        blocks = list(dict.fromkeys(comp_df["BlockName"].dropna().tolist()))
        if blocks:
            sel = st.selectbox("Choisir un bloc", blocks, index=0)
            sub = comp_df.loc[comp_df["BlockName"] == sel]
            fig3 = px.bar(
                sub.sort_values("Score", ascending=True),
                x="Score",
                y="CompetencyText",
                orientation="h",
                range_x=[0, 1]
            )
            fig3.add_vline(
                x=SEUIL_FORT,
                line_dash="dash",
                annotation_text=f"Seuil {SEUIL_FORT:.2f}",
                annotation_position="top left"
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.dataframe(sub.reset_index(drop=True))
        else:
            st.info("Aucun 'BlockName' trouvé.")
    else:
        st.info("Ajoute 'BlockName' via jointure avec competencies.csv si nécessaire.")

    st.subheader("Recommandations de métiers")
    job_score_col = next((c for c in ["JobScore", "Score", "FinalScore"] if c in job_df.columns), None)
    job_title_col = "JobTitle" if "JobTitle" in job_df.columns else job_df.columns[0]
    if job_score_col:
        top_jobs = job_df.sort_values(job_score_col, ascending=False).head(5)
        fig4 = px.bar(
            top_jobs.sort_values(job_score_col),
            x=job_score_col,
            y=job_title_col,
            orientation="h",
            range_x=[0, 1]
        )
        fig4.add_vline(
            x=SEUIL_FORT,
            line_dash="dash",
            annotation_text=f"Seuil {SEUIL_FORT:.2f}",
            annotation_position="top left"
        )
        st.plotly_chart(fig4, use_container_width=True)
        for _, row in top_jobs.iterrows():
            st.write(f"**{row[job_title_col]}** — {row[job_score_col]:.2f}")
    else:
        st.info("Colonne de score manquante pour les jobs.")

    if st.button("🔄 Rafraîchir les résultats"):
        st.rerun()

if __name__ == "__main__":
    show_visualisations()
