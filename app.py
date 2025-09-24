import streamlit as st
from recommender import JobRecommender
from googletrans import Translator
import sys
# This is the crucial fix: it imports the legacy_cgi.py file and makes it 
# available to the googletrans library, which needs it to run.
import legacy_cgi as cgi
sys.modules["cgi"] = cgi


# --- Page Configuration ---
st.set_page_config(
    page_title="Internship Recommender",
    page_icon="🤖",
    layout="centered"
)

# --- Language & Translation Setup ---
# Base English text and language codes for the translator
BASE_TEXT = {
    "title": "🎯 Internship Recommendation System",
    "subtitle": "Enter the skills you have, and we'll recommend the best internships for you!",
    "skills_label": "Enter your skills (comma-separated)",
    "skills_placeholder": "Python, Machine Learning, Data Analysis, SQL, Docker",
    "num_recs_label": "Number of recommendations",
    "job_type_label": "Select job type",
    "button_text": "Get Recommendations",
    "warning_text": "Please enter at least one skill.",
    "success_header": "Here are the top {count} recommendations for you:",
    "error_text": "No internships found matching your skills. Try different ones!",
    "company_label": "Company",
    "location_label": "Location",
    "skills_result_label": "Skills"
}

LANGUAGE_CODES = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Spanish (Español)": "es"
}

# --- Caching Functions ---
@st.cache_resource
def load_recommender():
    """Loads and caches the JobRecommender instance."""
    return JobRecommender('internships.csv')

@st.cache_data
def get_translated_texts(language_code):
    """Translates and caches the UI text using the Google Translate API."""
    if language_code == 'en':
        return BASE_TEXT
    
    translator = Translator()
    translated_texts = {}
    for key, value in BASE_TEXT.items():
        try:
            # **THE FIX IS HERE:** Special handling for strings with f-string placeholders
            # to prevent the placeholder itself from being translated.
            if key == "success_header":
                parts = value.split('{count}')
                translated_part1 = translator.translate(parts[0], dest=language_code).text
                translated_part2 = translator.translate(parts[1], dest=language_code).text
                # Reassemble the string with the placeholder intact
                translated_texts[key] = f"{translated_part1}{{count}}{translated_part2}"
            else:
                translated_texts[key] = translator.translate(value, dest=language_code).text
        except Exception as e:
            st.error(f"Translation Error: {e}")
            # Fallback to English if translation fails
            translated_texts[key] = value
            
    return translated_texts

# --- Load Data and Models ---
recommender = load_recommender()
df = recommender.df

# --- Sidebar for Language Selection ---
st.sidebar.header("Settings")
selected_language_name = st.sidebar.selectbox(
    label="Language",
    options=list(LANGUAGE_CODES.keys())
)
# Get the corresponding language code
selected_lang_code = LANGUAGE_CODES[selected_language_name]
# Get the translated UI texts
texts = get_translated_texts(selected_lang_code)


# --- Main UI Components ---
st.title(texts["title"])
st.write(texts["subtitle"])

skills_input = st.text_area(
    texts["skills_label"],
    # **THE SECOND FIX IS HERE:** The value in the text box is always the English
    # placeholder to ensure the model receives English input.
    value=BASE_TEXT["skills_placeholder"]
)

col1, col2 = st.columns(2)
with col1:
    top_n = st.slider(texts["num_recs_label"], 5, 20, 10)
with col2:
    job_type_options = ['Any'] + list(df['Job Type'].unique())
    job_type = st.selectbox(texts["job_type_label"], options=job_type_options)

if st.button(texts["button_text"], type="primary"):
    # The check now correctly compares against the English placeholder
    if not skills_input or skills_input == BASE_TEXT["skills_placeholder"]:
        st.warning(texts["warning_text"])
    else:
        user_skills = [skill.strip() for skill in skills_input.split(',')]
        recommendations = recommender.recommend(user_skills, top_n=top_n, job_type=job_type)

        if not recommendations.empty:
            st.success(texts["success_header"].format(count=len(recommendations)))
            for index, row in recommendations.iterrows():
                with st.container():
                    st.markdown(f"### {row['Job Title']}")
                    st.markdown(f"**{texts['company_label']}:** {row['Company']}")
                    st.markdown(f"**{texts['location_label']}:** {row['Location']}")
                    st.markdown(f"**{texts['skills_result_label']}:** `{row['Skills']}`")
                    st.divider()
        else:
            st.error(texts["error_text"])