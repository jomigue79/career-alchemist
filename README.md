# 🧪 The Career Alchemist

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Pro%2FFlash-orange.svg)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**An AI-Driven ATS Optimization Engine & Executive Career Strategist.**

---

## 📌 The Business Problem & Solution

Job seekers spend countless hours manually tailoring their CVs to bypass Applicant Tracking Systems (ATS), often resulting in formatting errors or generic, low-impact bullet points.

**The Career Alchemist** solves this operational drag. It ingests a user's baseline CV and a target Job Description (JD) and rewrites the user's professional narrative using a strict, anti-hallucination prompt architecture — rendering a beautifully formatted, executive-grade PDF.

*Built as a personal job search tool and governed under PM².*

---

## ⚙️ Installation & Setup

1. Clone the repo: `git clone https://github.com/jomigue79/career-alchemist.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with `GOOGLE_API_KEY=your_key_here`
4. Run the app: `streamlit run app.py`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Brain | Google Gemini 2.5 Pro (optimisation, cover letter) + Gemini 2.5 Flash (parsing, analysis) |
| UI Framework | Streamlit |
| PDF Rendering | WeasyPrint (HTML/CSS to PDF) |
| Template Engine | Jinja2 |
| Language | Python 3.10+ |
| Governance | PM² Methodology |

---

## 🚀 Key Features

- **Action-Governance-Impact Bullets** — Every rewritten bullet starts with a strong action verb, includes methodological context, and closes with a qualitative or quantitative impact statement.
- **Voice Profile Injection** — A `voice_params.json` persona profile is injected into every prompt to maintain an analytical, authoritative tone.
- **Anti-Hallucination Rules** — The optimizer never invents metrics, team sizes, or budget figures, and never sums experience years across roles.
- **CV–JD Match Evaluator** — Scores the CV against the JD across hard skills, soft skills, and qualifications, with a gap analysis and recommendation.
- **Executive PDF Export** — Single-column navy-themed PDF with circular headshot, 3-column Core Competencies matrix, and inline role/period formatting.
- **Cover Letter Generator** — Structured 4-paragraph cover letter (Hook → Evidence x2 → Close) as Markdown and downloadable PDF.
- **Smart Filenames** — Exported PDFs are named `name_role_company.pdf` automatically.

---

## 🏛️ Project Governance (PM²)

- **Initiating** — Defined scope: tailored CV + cover letter generation for a specific candidate persona.
- **Planning** — Designed the AI agent pipeline, voice profile schema, and PDF template architecture.
- **Executing** — Built the Analyst, Evaluator, Optimizer, and Writer agents; iterated on prompt engineering and WeasyPrint layout constraints.
- **Closing** — Full code audit, dead-file removal, module documentation, and pipeline validation via `audit_test.py`.

---

## 📁 Project Structure

```
app.py                   # Streamlit UI — main entry point
optimizer.py             # Rewrites CV bullets tailored to the JD (Gemini Pro)
cover_letter.py          # Generates structured cover letter (Gemini Pro)
match_evaluator.py       # Scores CV vs JD match with gap analysis (Gemini Flash)
requirement_extractor.py # Extracts structured requirements from the JD (Gemini Flash)
cv_parser.py             # Extracts static CV sections: skills, education, certs (Gemini Flash)
pdf_exporter.py          # Renders Jinja2 template to PDF via WeasyPrint
utils.py                 # Shared utilities: Gemini client, PDF text extraction, headshot processing
audit_test.py            # Smoke-test: structure, bullet syntax, and hallucination checks
data/
  voice_params.json      # Candidate voice profile injected into all prompts
  targets/               # Sample JD files for development
templates/
  cv_template.html       # Jinja2 CV template (WeasyPrint-safe layout)
  cv_style.css           # Executive navy theme
```

---

## 🔍 Audit

```bash
python audit_test.py
```

Expected output: `✅ AUDIT PASSED — 0 warnings across all content checks`
