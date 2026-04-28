import os
import io
import json
import base64
import pypdf
from google import genai
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GOOGLE_API_KEY")
if not _api_key:
    raise EnvironmentError("GOOGLE_API_KEY is not set in the environment.")

gemini_client = genai.Client(api_key=_api_key)
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_PRO_MODEL = "gemini-2.5-pro"

VOICE_PARAMS_PATH = "data/voice_params.json"


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
        pages_text = [page.extract_text() or "" for page in pdf_reader.pages]
    except Exception as e:
        raise RuntimeError(f"Could not extract text from PDF: {e}") from e

    text = "\n".join(pages_text).strip()
    if not text:
        raise ValueError("No text could be extracted from the PDF.")
    return text


# Max target file size for the final PDF (2MB). The headshot is the main
# variable, so we constrain the embedded image to this budget.
_HEADSHOT_MAX_BYTES = 200_000   # 200 KB embedded leaves headroom for the rest
_HEADSHOT_MAX_DIMENSION = 300   # px — sufficient for a circular portrait at 96dpi


def process_headshot(uploaded_file):
    """
    Reads a headshot image, optionally resizes it so the embedded base64
    stays well under budget, and returns a data-URI string suitable for
    embedding directly in HTML (self-contained PDF).

    Returns None if Pillow is not installed or the file is invalid.
    """
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError(
            "Pillow is required for headshot processing. Run: pip install Pillow"
        )

    try:
        img = Image.open(uploaded_file).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Could not open image: {e}") from e

    # Resize if either dimension exceeds the cap
    if max(img.size) > _HEADSHOT_MAX_DIMENSION:
        img.thumbnail((_HEADSHOT_MAX_DIMENSION, _HEADSHOT_MAX_DIMENSION), Image.LANCZOS)

    # Encode to JPEG, stepping down quality until under byte budget
    quality = 85
    while quality >= 40:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() <= _HEADSHOT_MAX_BYTES:
            break
        quality -= 10
    # If still over budget at quality=40, use it as best-effort
    # (extremely high-detail image — acceptable for a portrait thumbnail)

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"