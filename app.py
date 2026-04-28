import streamlit as st
import os
from dotenv import load_dotenv
from requirement_extractor import extract_requirements
from match_evaluator import evaluate_match
from optimizer import get_tailored_cv
from cover_letter import generate_cover_letter
from utils import extract_text_from_pdf

# Load environment variables
load_dotenv()

# Validate API key on startup
if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY is not set. Please add it to your .env file.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="The Career Alchemist",
    page_icon="🧪",
    layout="wide"
)

# Session state initialization
if "jd_analysis" not in st.session_state:
    st.session_state.jd_analysis = None
if "cv_text" not in st.session_state:
    st.session_state.cv_text = None
if "tailored_cv" not in st.session_state:
    st.session_state.tailored_cv = None
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = None
if "jd_text" not in st.session_state:
    st.session_state.jd_text = None
if "match_result" not in st.session_state:
    st.session_state.match_result = None

# Sidebar - PM² Governance Info
st.sidebar.title("🧪 Project Info")
st.sidebar.info("""
**Project:** Career Alchemist  
**Phase:** Executing (Sprint 1)  
**Methodology:** PM²  
**Manager:** João Correia
""")

# Main UI Header
st.title("The Career Alchemist: AI Job Search Intelligence")
st.markdown("---")

# Layout: Two columns for inputs
col1, col2 = st.columns(2)

with col1:
    st.header("1. Personal Context")
    uploaded_cv = st.file_uploader("Upload your Baseline CV (PDF)", type="pdf")
    if uploaded_cv:
        try:
            cv_text = extract_text_from_pdf(uploaded_cv)
            st.session_state.cv_text = cv_text
            st.success("CV uploaded and parsed successfully.")
        except RuntimeError as e:
            st.error(str(e))

    st.subheader("Tone of Voice")
    st.info("The system will use your predefined Voice Profile for RAG optimization.")

with col2:
    st.header("2. Opportunity Context")
    jd_text = st.text_area("Paste the Job Description here", height=300, placeholder="Copy the JD from LinkedIn/Indeed...")

    if st.button("Analyze Job Requirements"):
        if jd_text.strip():
            if len(jd_text) > 15000:
                st.warning("JD is very long. Consider trimming to the most relevant sections.")
            with st.spinner("Agent 'Analyst' is extracting requirements..."):
                try:
                    st.session_state.jd_analysis = extract_requirements(jd_text)
                    st.session_state.jd_text = jd_text
                    st.session_state.match_result = None  # reset on new analysis
                except RuntimeError as e:
                    st.error(f"Analysis failed: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
            # Run match evaluation automatically if CV is loaded
            if st.session_state.jd_analysis and st.session_state.cv_text:
                with st.spinner("Agent 'Evaluator' is scoring your match..."):
                    try:
                        st.session_state.match_result = evaluate_match(
                            st.session_state.cv_text,
                            jd_text
                        )
                    except RuntimeError as e:
                        st.error(f"Match evaluation failed: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error during match evaluation: {e}")
        else:
            st.warning("Please paste a Job Description to proceed.")

# Display analysis result (persists across reruns via session state)
if st.session_state.jd_analysis:
    st.markdown("---")
    st.header("📋 Job Requirements Analysis")
    st.markdown(st.session_state.jd_analysis)

# Match Evaluation
if st.session_state.match_result:
    m = st.session_state.match_result
    score = m.get("overall_score", 0)
    recommendation = m.get("recommendation", "")

    st.markdown("---")
    st.header("🎯 Match Evaluation")

    if score >= 75:
        st.success(f"Match Score: {score}/100 — {recommendation}")
    elif score >= 50:
        st.warning(f"Match Score: {score}/100 — {recommendation}")
    else:
        st.error(f"Match Score: {score}/100 — {recommendation}")

    st.write(m.get("strengths", ""))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.subheader("✅ Hard Skills Matched")
        for s in m.get("hard_skills", {}).get("matched", []):
            st.markdown(f"- {s}")
        st.subheader("❌ Hard Skills Missing")
        for s in m.get("hard_skills", {}).get("missing", []):
            st.markdown(f"- {s}")
    with col_b:
        st.subheader("✅ Soft Skills Matched")
        for s in m.get("soft_skills", {}).get("matched", []):
            st.markdown(f"- {s}")
        st.subheader("❌ Soft Skills Missing")
        for s in m.get("soft_skills", {}).get("missing", []):
            st.markdown(f"- {s}")
    with col_c:
        st.subheader("✅ Qualifications Met")
        for q in m.get("qualifications", {}).get("met", []):
            st.markdown(f"- {q}")
        st.subheader("❌ Qualification Gaps")
        for q in m.get("qualifications", {}).get("gaps", []):
            st.markdown(f"- {q}")
elif st.session_state.jd_analysis and not st.session_state.cv_text:
    st.info("📌 Upload your CV to see your match score.")

# CV Optimization section
if st.session_state.jd_analysis and st.session_state.cv_text:
    st.markdown("---")
    st.header("✨ CV Optimizer")
    if st.button("Generate Tailored CV"):
        with st.spinner("Agent 'Optimizer' is rewriting your CV..."):
            try:
                st.session_state.tailored_cv = get_tailored_cv(
                    st.session_state.cv_text,
                    st.session_state.jd_text
                )
            except RuntimeError as e:
                st.error(f"Optimization failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

if st.session_state.tailored_cv:
    result = st.session_state.tailored_cv
    st.subheader("Professional Summary")
    st.write(result.get("summary", ""))
    st.subheader("Experience")
    for role in result.get("experience", []):
        st.markdown(f"**{role.get('role')}** — {role.get('company')}")
        for bullet in role.get("bullets", []):
            st.markdown(f"- {bullet}")

# Cover Letter section
if st.session_state.jd_analysis and st.session_state.cv_text:
    st.markdown("---")
    st.header("✉️ Cover Letter Generator")
    if st.button("Generate Cover Letter"):
        with st.spinner("Agent 'Writer' is crafting your cover letter..."):
            try:
                st.session_state.cover_letter = generate_cover_letter(
                    st.session_state.cv_text,
                    st.session_state.jd_text
                )
            except RuntimeError as e:
                st.error(f"Cover letter generation failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

if st.session_state.cover_letter:
    st.subheader("Your Cover Letter")
    st.markdown(st.session_state.cover_letter)
    st.text_area("Copy-ready version", value=st.session_state.cover_letter, height=400)

# Footer/Status Bar
st.markdown("---")
st.caption("Career Alchemist | Powered by Gemini 2.5 Flash & PM² Framework")