
from skill_matcher import extract_skills 


def rank_candidates(job_desc_text, candidate_resumes, known_skills):
    """
    Processes multiple resumes against a job description.
    Ranks them by skill match percentage and identifies gaps.
    """
    # 1. Extract skills from the job description
    jd_skills = set(extract_skills(job_desc_text, known_skills))
    
    # ... (rest of your existing code stays exactly the same) ...
    
    # ... rest of your code stays exactly the same ...
    
    if not jd_skills:
        return "Error: No skills found in the Job Description. Please add skills to skills.json."

    ranked_results = []
    
    for candidate in candidate_resumes:
        # Extract candidate's skills
        cand_skills = set(extract_skills(candidate['text'], known_skills))
        
        # Calculate overlapping skills (Intersection)
        matching_skills = jd_skills.intersection(cand_skills)
        
        # Calculate missing skills (Difference: What's in JD but NOT in Candidate)
        missing_skills = jd_skills.difference(cand_skills)
        
        # Calculate explicit Skill Match Score
        skill_score = round((len(matching_skills) / len(jd_skills)) * 100, 2)
        
        # Combine with structural TF-IDF score for a hybrid ranking weight (Optional)
        # For now, let's stick to pure skill match score as it's more accurate for screening
        
        ranked_results.append({
            "Candidate Name": candidate["name"],
            "Match Score (%)": skill_score,
            "Matched Skills": list(matching_skills),
            "Missing Skills (Gaps)": list(missing_skills),
            "All Skills": list(cand_skills)
        })
        
    # Sort candidates by Match Score in descending order
    ranked_results = sorted(ranked_results, key=lambda x: x["Match Score (%)"], reverse=True)
    
    return ranked_results


if __name__ == "__main__":
    from skill_matcher import load_skills_dictionary, extract_skills
    
    # Master skill list
    known_skills = load_skills_dictionary()
    
    # Inputs
    job_desc = "looking for a python data scientist with experience in machine learning scikit-learn and sql"
    
    resumes_pool = [
        {
            "name": "Candidate 1 (Your Sample)", 
            "text": "experienced software developer proficient in python sql and docker built machine learning models"
        },
        {
            "name": "Candidate 2 (Perfect Match)", 
            "text": "data scientist with expertise in python, sql, scikit-learn, and machine learning architectures."
        }
    ]
    
    results = rank_candidates(job_desc, resumes_pool, known_skills)
    
    print("--- RANKED CANDIDATE SCREENING RESULTS ---")
    import pprint
    pprint.pprint(results)