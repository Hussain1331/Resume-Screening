import json
import spacy
from spacy.matcher import PhraseMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the spaCy engine
nlp = spacy.load("en_core_web_sm")

def load_skills_dictionary(json_path="skills.json"):
    """Loads categorized roles and skills from a JSON file."""
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: skills.json not found. Returning standard fallback.")
        return {
            "Data Science & AI": ["python", "machine learning", "sql", "scikit-learn"]
        }
    
def extract_skills(text, skills_list):
    """Uses spaCy's PhraseMatcher to extract known skills safely."""
    clean_text = text.lower()
    doc = nlp(clean_text)
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(str(skill).strip().lower()) for skill in skills_list if skill]
    if not patterns:
        return []     
    matcher.add("SKILL_KEYWORD", patterns)
    matches = matcher(doc)
    extracted_skills = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        extracted_skills.add(span.text.strip().lower())
    return list(extracted_skills)

def calculate_similarity(resume_text, job_desc_text):
    """Calculates the cosine similarity score percentage between a resume and a job description."""
    text_corpus = [resume_text, job_desc_text]
    
    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(text_corpus)
    
    # Compute Cosine Similarity between the first element (resume) and second element (job description)
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    # Convert to a clean percentage out of 100
    match_percentage = round(similarity_matrix[0][0] * 100, 2)
    return match_percentage





#test
if __name__ == "__main__":
    
    # Mock data
    job_description = "looking for a python data scientist with experience in machine learning scikit-learn and sql"
    candidate_resume = "experienced software developer proficient in python sql and docker built machine learning models"
    
    # Load our skills masterlist
    known_skills = load_skills_dictionary()
    
    # 1. Extract Skills
    jd_skills = extract_skills(job_description, known_skills)
    resume_skills = extract_skills(candidate_resume, known_skills)
    
    print("--- SKILL EXTRACTION ---")
    print(f"Required Skills in Job Desc: {jd_skills}")
    print(f"Candidate Skills Found:     {resume_skills}")
    
    # 2. Compute Similarity Score
    match_score = calculate_similarity(candidate_resume, job_description)
    print("\n--- SIMILARITY SCORE ---")
    print(f"Overall Match Score: {match_score}%")