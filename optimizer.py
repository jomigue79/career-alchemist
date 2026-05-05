"""
optimizer.py
Rewrites the CV's Professional Summary and Experience section using Gemini Pro,
tailored to a specific Job Description and the candidate's stored Voice Profile.

Process (internal to the prompt):
  1. JD Analysis  — identify role type, extract top 5-7 keywords, map to CV
  2. Rewrite      — produce Action+Context+Result bullets using JD vocabulary

Strict anti-hallucination rules are enforced:
  - No invented metrics or team sizes
  - No summing of years across different roles
  - Only skills/certs explicitly present in the baseline CV

Returns a dict: { "summary": str, "experience": [{ company, role, period, bullets }] }
"""
import json
from utils import groq_client, GROQ_MODEL, load_voice_params


def get_tailored_cv(cv_text, jd_text):
    """
    Rewrites CV bullet points tailored to a JD using the stored Voice Profile.
    Returns a parsed dict with 'summary' and 'experience' keys.
    """
    voice_context = load_voice_params()

    system_prompt = """You are an expert Executive Career Strategist and ATS Optimizer.
Rewrite the Professional Summary and Experience section of the CV to match the Job Description.

VOICE: Executive Achiever tone — impact-driven, no buzzwords, implied first-person (no I/my/we in bullets).
SYNTAX: Every bullet starts with a strong past-tense action verb. Use Action+Context+Result framework.
KEYWORDS: Mirror exact JD terminology. Extract top 5-7 keywords and inject naturally.
ANTI-HALLUCINATION: Never invent metrics, team sizes, or skills not in the CV. Never sum years across roles.

Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{
  "summary": "2-3 sentence professional summary tailored to this JD",
  "experience": [
    {
      "company": "Company Name",
      "role": "Role Name",
      "period": "Jan 2020 – Dec 2022",
      "bullets": ["bullet 1", "bullet 2", "bullet 3"]
    }
  ]
}
IMPORTANT: Begin your response immediately with `{`. Do not echo, repeat, or output any input text before the JSON."""
    user_content = (
        "===BASELINE CV (ground truth — do not invent beyond this)===\n" + cv_text
        + "\n\n===TARGET JOB DESCRIPTION===\n" + jd_text
        + "\n\n===VOICE PROFILE===\n" + str(voice_context)
    )

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error during CV optimization: {e}") from e

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse AI response as JSON: {e}") from e