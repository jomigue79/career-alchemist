"""
cv_parser.py
Extracts static CV sections (education, certifications, languages, skills)
from the raw CV text using Gemini. These sections are preserved as-is in
the PDF — they are not rewritten by the optimizer.
"""

import json
import re
from utils import groq_client, GROQ_MODEL


def _extract_json(text: str) -> dict:
    """Extract the first complete JSON object from a string, tolerating any preamble."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group())


def parse_cv_sections(cv_text: str) -> dict:
    """
    Extracts structured static sections from raw CV text.

    Returns a dict with keys:
        skills:         {"technical": [...], "soft": [...]}
        education:      [{"degree": "...", "institution": "...", "year": "..."}]
        certifications: ["cert1", "cert2"]
        languages:      [{"language": "...", "level": "..."}]

    If a section is absent from the CV, returns an empty list / object for that key.
    """
    system_prompt = """You are a CV data extraction engine. Extract structured sections from the CV provided by the user.
Return ONLY valid JSON with this exact structure (no markdown, no explanation):
{
  "skills": {
    "governance": ["PM² Methodology", "Risk Management", "SDLC"],
    "technical": ["Python", "AI Pipelines", "Automated QA"],
    "tools": ["Jira", "ClickUp", "GitHub"]
  },
  "education": [
    {"degree": "BSc Computer Science", "institution": "University of Lisbon", "year": "2010"}
  ],
  "certifications": ["AWS Solutions Architect Associate", "PMP"],
  "languages": [
    {"language": "English", "level": "Native"},
    {"language": "Portuguese", "level": "Fluent"}
  ]
}
Rules:
- Only include information explicitly stated in the CV. Do NOT invent or infer.
- Classify skills: governance=methodologies/frameworks/processes, technical=programming/data/AI/engineering, tools=software/platforms.
- If a category has no items, return an empty list [].
- All four top-level keys must always be present.
- IMPORTANT: Begin your response immediately with `{`. Do not echo, repeat, or output any input text before the JSON."""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": cv_text}
            ],
            temperature=0,
            max_tokens=2048
        )
    except Exception as e:
        raise RuntimeError(f"Groq API error during CV parsing: {e}") from e

    try:
        data = _extract_json(response.choices[0].message.content)
    except (ValueError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to parse CV sections response as JSON: {e}") from e

    # Guarantee all keys exist with safe defaults
    data.setdefault("skills", {})
    data["skills"].setdefault("governance", [])
    data["skills"].setdefault("technical", [])
    data["skills"].setdefault("tools", [])
    data.setdefault("education", [])
    data.setdefault("certifications", [])
    data.setdefault("languages", [])

    return data
