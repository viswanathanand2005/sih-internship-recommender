# recommender.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class JobRecommender:
    def __init__(self, data_path):
        """Initializes the recommender, loads data, and builds the model."""
        self.df = self._load_and_preprocess_data(data_path)
        self.tfidf_vectorizer, self.tfidf_matrix = self._vectorize_skills()

    def _load_and_preprocess_data(self, data_path):
        """Loads and preprocesses the job listings data."""
        df = pd.read_csv(data_path)
        
        # Drop perk columns if they exist
        perk_cols = [f'Perk {i}' for i in range(1, 7)]
        df = df.drop(columns=perk_cols, errors='ignore')

        # Combine skill columns into a single 'Skills' string
        skill_cols = [f'Skill {i}' for i in range(1, 7)]
        df['Skills'] = df[skill_cols].apply(lambda row: ','.join(row.dropna()), axis=1)

        # Fill any remaining NaN values in the main 'Skills' column
        df['Skills'] = df['Skills'].fillna('')
        
        # Drop the original skill columns
        df = df.drop(columns=skill_cols, errors='ignore')
        
        return df

    def _vectorize_skills(self):
        """Creates a TF-IDF matrix from the 'Skills' column."""
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform(self.df['Skills'])
        return tfidf_vectorizer, tfidf_matrix

    def recommend(self, skills_list, top_n=5, job_type='any'):
        """Recommends jobs based on a list of input skills."""
        # 1. Transform the input skills into a TF-IDF vector
        skill_string = ', '.join(skills_list)
        skills_vector = self.tfidf_vectorizer.transform([skill_string])

        # 2. Calculate cosine similarity
        cosine_sim_scores = cosine_similarity(skills_vector, self.tfidf_matrix)

        # 3. Get the top N similar job indices
        sim_scores = list(enumerate(cosine_sim_scores[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 4. Filter results by job type
        recommended_indices = []
        for idx, score in sim_scores:
            if len(recommended_indices) >= top_n:
                break
            if job_type.lower() == 'any' or self.df['Job Type'].iloc[idx].lower() == job_type.lower():
                recommended_indices.append(idx)
        
        # Return the recommended job listings as a DataFrame
        return self.df.iloc[recommended_indices]