# app.py

import streamlit as st
from recommender import JobRecommender

# --- Page Configuration ---
st.set_page_config(
    page_title="Internship Recommender",
    page_icon="🤖",
    layout="centered"
)

# --- Caching the Recommender ---
@st.cache_resource
def load_recommender():
    """Loads the JobRecommender instance. Caching ensures it runs only once."""
    return JobRecommender('internships.csv')

recommender = load_recommender()
df = recommender.df

# --- UI Components ---
st.title("🎯 Internship Recommendation System")
st.write(
    "Enter the skills you have, and we'll recommend the best internships for you!"
)

# User input for skills
skills_input = st.text_area(
    "Enter your skills (comma-separated)",
    "Python, Machine Learning, Data Analysis, SQL, Docker"
)

# UI for filtering
col1, col2 = st.columns(2)
with col1:
    top_n = st.slider("Number of recommendations", 5, 20, 10)
with col2:
    job_type_options = ['Any'] + list(df['Job Type'].unique())
    job_type = st.selectbox("Select job type", options=job_type_options)

# Recommendation button
if st.button("Get Recommendations", type="primary"):
    if not skills_input:
        st.warning("Please enter at least one skill.")
    else:
        # Parse skills and get recommendations
        user_skills = [skill.strip() for skill in skills_input.split(',')]
        recommendations = recommender.recommend(user_skills, top_n=top_n, job_type=job_type)

        # --- Display Results ---
        if not recommendations.empty:
            st.success(f"Here are the top {len(recommendations)} recommendations for you:")
            for index, row in recommendations.iterrows():
                with st.container():
                    st.markdown(f"### {row['Job Title']}")
                    st.markdown(f"**Company:** {row['Company']}")
                    st.markdown(f"**Location:** {row['Location']}")
                    st.markdown(f"**Skills:** `{row['Skills']}`")
                    st.divider()
        else:
            st.error("No internships found matching your skills. Try different ones!")