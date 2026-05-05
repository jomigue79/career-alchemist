"""
match_evaluator.py
Scores how well a candidate's CV matches a given Job Description using Gemini.

Returns a structured dict with:
  - overall_score (0-100)
  - hard_skills / soft_skills: matched and missing lists
  - qualifications: met and gaps lists
  - strengths: 2-3 sentence summary of strongest alignment
  - recommendation: one of Apply immediately | Strong fit | Needs gaps addressed | Stretch role

Triggered automatically after JD analysis if a CV is already loaded.
"""
import json
from utils import groq_client, GROQ_MODEL


def evaluate_match(cv_text, jd_text):
    """
    Evaluates how well a CV matches a Job Description.
    Returns a parsed dict with score, matched/missing skills, gaps, and recommendation.
    """
    system_prompt = """You are an expert ATS analyst and Senior Recruiter.
Evaluate how well the candidate's CV matches the Job Description provided.
Be honest and precise — do not inflate the score.
Return ONLY valid JSON (no markdown, no explanation) with exactly this structure:
{
  "overall_score": <integer 0-100>,
  "hard_skills": {"matched": ["skill1"], "missing": ["skill2"]},
  "soft_skills": {"matched": ["skill1"], "missing": ["skill2"]},
  "qualifications": {"met": ["requirement1"], "gaps": ["requirement2"]},
  "strengths": "<2-3 sentence summary of the strongest alignment points>",
  "recommendation": "<one of: Apply immediately | Strong fit | Needs gaps addressed | Stretch role>"
}"""

    user_content = "===CANDIDATE CV===\n" + cv_text + "\n\n===JOB DESCRIPTION===\n" + jd_text

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error during match evaluation: {e}") from e

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse match evaluation response as JSON: {e}") from e
