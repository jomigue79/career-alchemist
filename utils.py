import os
import json
import pypdf
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"

VOICE_PARAMS_PATH = "data/voice_params.json"


def _api_key_from_streamlit_secrets():
    """Read GOOGLE_API_KEY from Streamlit secrets when available."""
    try:
        import streamlit as st
        return st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        return None


def _api_key_from_secrets_file():
    """Read GOOGLE_API_KEY from local .streamlit/secrets.toml when present."""
    path = ".streamlit/secrets.toml"
    if not os.path.exists(path):
        return None

    try:
        import tomllib
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return data.get("GOOGLE_API_KEY")
    except Exception:
        return None


def get_google_api_key():
    """Resolve the API key from environment or Streamlit secrets."""
    return (
        os.getenv("GOOGLE_API_KEY")
        or _api_key_from_streamlit_secrets()
        or _api_key_from_secrets_file()
    )


def has_google_api_key():
    """Quick check used by the UI to show setup guidance."""
    return bool(get_google_api_key())


def get_gemini_client():
    """Create a Gemini client with the configured API key."""
    api_key = get_google_api_key()
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is not configured. Set it in .env or Streamlit secrets."
        )
    return genai.Client(api_key=api_key)


def load_voice_params():
    """Load voice profile from disk, falling back to a sensible default."""
    try:
        with open(VOICE_PARAMS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "Professional, metric-driven, and active."


def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a file-like object (Streamlit UploadedFile).
    """
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"

        if not text.strip():
            raise ValueError("No text could be extracted from the PDF.")

        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Could not extract text from PDF: {e}") from e