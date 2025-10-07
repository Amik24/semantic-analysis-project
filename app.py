import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import base64
import json

# === Page configuration ===
st.set_page_config(
    page_title="Semantic Analysis Project",
    page_icon="🧠",
    layout="wide"
)

# === Custom CSS ===
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Roboto', sans-serif;
        }
        .header-title {
            font-size: 32px;
            font-weight: 700;
            color: #017179;
        }
        .header-subtitle {
            font-size: 18px;
            color: #017179;
            margin-bottom: 20px;
        }
        .stTextArea, .stSlider, .stTextInput {
            font-size: 16px;
        }
        .stButton>button {
            background-color: #017179;
            color: white;
            border-radius: 8px;
        }
        div[data-baseweb="slider"] > div > div > div > div > div[role="slider"] + div {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# === Display ECE Logo ===
logo_url = "https://raw.githubusercontent.com/thay-thay/semantic-analysis-project/main/data/ECE_LOGO_2021_web.png"
st.markdown(
    f"""
    <div style="display:flex; justify-content:center; margin-bottom:20px;">
        <img src="{logo_url}" width="200">
    </div>
    """,
    unsafe_allow_html=True
)

# === Header ===
st.markdown("""
<div>
    <div class="header-title">Project – Semantic Analysis</div>
    <div class="header-subtitle">Semantic Analysis for Competency Mapping and Job Profile Recommendation</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# === GitHub Configuration ===
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = "Amik24/semantic-analysis-project"  # ✅ Ton dépôt GitHub
FILE_PATH = "data/user_responses.csv"             # ✅ Chemin du fichier CSV

def append_to_github_csv(new_response):
    if not GITHUB_TOKEN:
        st.error("❌ GitHub token not configured. Please add it to Streamlit secrets.")
        return False

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            file_data = response.json()
            content = base64.b64decode(file_data['content']).decode('utf-8')
            sha = file_data['sha']

            from io import StringIO
            existing_df = pd.read_csv(StringIO(content))
            new_df = pd.concat([existing_df, pd.DataFrame([new_response])], ignore_index=True)
        elif response.status_code == 404:
            # Si le fichier n'existe pas encore, on le crée
            new_df = pd.DataFrame([new_response])
            sha = None
        else:
            st.error(f"❌ Error fetching file: {response.status_code}")
            return False

        csv_content = new_df.to_csv(index=False)
        encoded_content = base64.b64encode(csv_content.encode()).decode()

        commit_data = {
            "message": f"Add response from {new_response['First_Name']} {new_response['Last_Name']}",
            "content": encoded_content,
            "branch": "main"
        }

        if sha:
            commit_data["sha"] = sha

        update_response = requests.put(url, headers=headers, data=json.dumps(commit_data))

        if update_response.status_code in [200, 201]:
            return True
        else:
            st.error(f"❌ Error updating file: {update_response.status_code}")
            st.error(update_response.json())
            return False

    except Exception as e:
        st.error(f"❌ Exception occurred: {str(e)}")
        return False


# === Form ===
with st.form("skills_form"):
    # === Mandatory fields ===
    first_name = st.text_input("First Name", placeholder="Enter your first name")
    last_name = st.text_input("Last Name", placeholder="Enter your last name")

    # === Optional fields with suggestions ===
    prog_text = st.text_area(
        "Describe your experience with programming.",
        placeholder="Ex: I mostly use Python and SQL, and I work with Git and OOP concepts."
    )
    data_text = st.text_area(
        "Explain how you typically analyze a dataset.",
        placeholder="Ex: I clean the data, perform EDA, visualize distributions, and calculate statistics."
    )
    ml_text = st.text_area(
        "Tell us about a project where you applied machine learning.",
        placeholder="Ex: I built a regression model using scikit-learn and evaluated it with cross-validation."
    )
    ml_problem_text = st.text_area(
        "How would you approach designing a churn prediction model?",
        placeholder="Ex: I would perform feature engineering, select a model, train, and evaluate it."
    )
    nlp_text = st.text_area(
        "Have you ever worked with NLP?",
        placeholder="Ex: I tokenized text, used embeddings, transformers, sentiment analysis, and NER."
    )
    pipeline_text = st.text_area(
        "Explain a time when you built or maintained a data pipeline.",
        placeholder="Ex: I implemented an ETL pipeline using Airflow for batch processing."
    )
    sharing_text = st.text_area(
        "How do you usually share the results of your analysis?",
        placeholder="Ex: I create dashboards, visualizations, and prepare presentations to explain insights."
    )
    reflection_text = st.text_area(
        "What makes someone a strong Data Scientist / Engineer?",
        placeholder="Ex: Strong problem-solving, communication skills, and mastery of tools."
    )

    # === Sliders with tooltip ===
    col1, col2 = st.columns(2)
    with col1:
        git_level = st.slider(
            "Git & Collaboration",
            min_value=1, max_value=5, value=3,
            help="1 = Beginner / Weak, 5 = Expert / Strong"
        )
    with col2:
        presentation_level = st.slider(
            "Presentation Skills",
            min_value=1, max_value=5, value=3,
            help="1 = Beginner / Weak, 5 = Expert / Strong"
        )

    # === Submit button ===
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not first_name.strip() or not last_name.strip():
            st.warning("⚠️ Please fill in your First Name and Last Name before submitting.")
        else:
            responses = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "First_Name": first_name,
                "Last_Name": last_name,
                "Programming": prog_text,
                "Data_Analysis": data_text,
                "ML_Projects": ml_text,
                "ML_Problem": ml_problem_text,
                "NLP": nlp_text,
                "Data_Pipeline": pipeline_text,
                "Sharing_Results": sharing_text,
                "Git_Level": git_level,
                "Presentation_Level": presentation_level,
                "Reflection": reflection_text
            }

            with st.spinner("Saving your responses to GitHub..."):
                success = append_to_github_csv(responses)

            if success:
                st.success(f"✅ Thank you {first_name}! Your responses have been submitted successfully to GitHub.")
                st.balloons()
                st.markdown("### 📋 Your Submitted Responses:")
                df = pd.DataFrame([responses])
                st.dataframe(df)
            else:
                st.error("❌ Failed to save responses to GitHub. Please try again or contact support.")
