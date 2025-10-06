import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# --- Page configuration ---
st.set_page_config(
    page_title="Semantic Analysis Project",
    page_icon="🧠",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        html, body, [class*="css"]  { font-family: 'Roboto', sans-serif; }
        .stTextArea, .stSlider, .stTextInput { font-size: 16px; }
        .stButton>button { background-color: #017179; color: white; }
        div[data-baseweb="slider"] > div > div > div > div > div[role="slider"] + div { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
logo_path = Path(r"C:\Users\bouai\MonProjetNLP\ECE_LOGO_2021_web.png")
col1, col2 = st.columns([4,1])
with col1:
    st.markdown("<div style='font-size:32px; font-weight:700; color:#017179;'>Project – Semantic Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:18px; color:#017179; margin-bottom:20px;'>Semantic Analysis for Competency Mapping and Job Profile Recommendation</div>", unsafe_allow_html=True)
with col2:
    st.image(logo_path, width=120)

st.markdown("---")

# --- Initialize session_state for form fields if not exist ---
fields = [
    "first_name", "last_name", "prog_text", "data_text", "ml_text",
    "ml_problem_text", "nlp_text", "pipeline_text", "sharing_text",
    "reflection_text", "git_level", "presentation_level"
]
for field in fields:
    if field not in st.session_state:
        if "level" in field:
            st.session_state[field] = 3
        else:
            st.session_state[field] = ""

# --- Form ---
with st.form("skills_form"):
    st.session_state.first_name = st.text_input("First Name", value=st.session_state.first_name, placeholder="Enter your first name")
    st.session_state.last_name = st.text_input("Last Name", value=st.session_state.last_name, placeholder="Enter your last name")

    st.session_state.prog_text = st.text_area("Describe your experience with programming.", value=st.session_state.prog_text, placeholder="Ex: I mostly use Python and SQL, and I work with Git and OOP concepts.")
    st.session_state.data_text = st.text_area("Explain how you typically analyze a dataset.", value=st.session_state.data_text, placeholder="Ex: I clean the data, perform EDA, visualize distributions, and calculate statistics.")
    st.session_state.ml_text = st.text_area("Tell us about a project where you applied ML techniques.", value=st.session_state.ml_text, placeholder="Ex: I built a regression model using scikit-learn and evaluated it with cross-validation.")
    st.session_state.ml_problem_text = st.text_area("How would you approach designing a churn prediction model?", value=st.session_state.ml_problem_text, placeholder="Ex: I would perform feature engineering, select a model, train, and evaluate it.")
    st.session_state.nlp_text = st.text_area("Have you ever worked with text data (NLP)?", value=st.session_state.nlp_text, placeholder="Ex: I tokenized text, used embeddings, transformers, sentiment analysis, and NER.")
    st.session_state.pipeline_text = st.text_area("Explain a time when you built a data pipeline.", value=st.session_state.pipeline_text, placeholder="Ex: I implemented an ETL pipeline using Airflow for batch processing.")
    st.session_state.sharing_text = st.text_area("How do you share your analysis results?", value=st.session_state.sharing_text, placeholder="Ex: I create dashboards, visualizations, and prepare presentations to explain insights.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.git_level = st.slider("Git & Collaboration", 1, 5, st.session_state.git_level)
    with col2:
        st.session_state.presentation_level = st.slider("Presentation Skills", 1, 5, st.session_state.presentation_level)

    st.session_state.reflection_text = st.text_area("In your opinion, what makes someone strong in Data Science?", value=st.session_state.reflection_text, placeholder="Ex: Strong problem-solving, communication skills, and mastery of tools.")

    submitted = st.form_submit_button("Submit")

    if submitted:
        # Vérifier les champs obligatoires
        required_fields = {
            "First Name": st.session_state.first_name,
            "Last Name": st.session_state.last_name,
            "Programming": st.session_state.prog_text,
            "Data Analysis": st.session_state.data_text,
            "ML Projects": st.session_state.ml_text,
            "ML Problem": st.session_state.ml_problem_text,
            "NLP": st.session_state.nlp_text,
            "Data Pipeline": st.session_state.pipeline_text,
            "Sharing Results": st.session_state.sharing_text,
            "Reflection": st.session_state.reflection_text
        }
        empty_fields = [name for name, value in required_fields.items() if not value.strip()]

        if empty_fields:
            st.warning(f"⚠️ Please fill in all required fields: {', '.join(empty_fields)}")
        else:
            responses = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "First_Name": st.session_state.first_name,
                "Last_Name": st.session_state.last_name,
                "Programming": st.session_state.prog_text,
                "Data_Analysis": st.session_state.data_text,
                "ML_Projects": st.session_state.ml_text,
                "ML_Problem": st.session_state.ml_problem_text,
                "NLP": st.session_state.nlp_text,
                "Data_Pipeline": st.session_state.pipeline_text,
                "Sharing_Results": st.session_state.sharing_text,
                "Git_Level": st.session_state.git_level,
                "Presentation_Level": st.session_state.presentation_level,
                "Reflection": st.session_state.reflection_text
            }
            df = pd.DataFrame([responses])
            try:
                existing_df = pd.read_csv("responses.csv")
                df = pd.concat([existing_df, df], ignore_index=True)
            except FileNotFoundError:
                pass
            df.to_csv("responses.csv", index=False)
            st.success("✅ Your responses have been successfully saved!")
            st.balloons()

            # --- Reset all form fields ---
            for field in fields:
                if "level" in field:
                    st.session_state[field] = 3
                else:
                    st.session_state[field] = ""

# --- Display previous responses ---
st.markdown("---")
st.subheader("📊 Previous Responses")
try:
    all_responses = pd.read_csv("responses.csv")
    st.dataframe(all_responses.sort_values("Timestamp", ascending=False))
except FileNotFoundError:
    st.info("No responses have been recorded yet.")
