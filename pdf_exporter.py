"""
pdf_exporter.py
Renders the tailored CV dict into a styled PDF using WeasyPrint + Jinja2.

Requires WeasyPrint and GTK+ runtime on Windows.
GTK+ installer: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
"""

import os
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).parent / "templates"
CSS_PATH = TEMPLATES_DIR / "cv_style.css"

# On Windows, register the GTK+ DLL directory so WeasyPrint's cffi loader can
# find libgobject, pango, etc. without requiring the user to set PATH manually.
# os.add_dll_directory() is available on Python 3.8+ (Windows only).
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    _GTK_CANDIDATES = [
        r"C:\Program Files\GTK3-Runtime Win64\bin",
        r"C:\Program Files (x86)\GTK3-Runtime\bin",
        r"C:\GTK\bin",
    ]
    for _gtk_path in _GTK_CANDIDATES:
        if Path(_gtk_path).is_dir():
            os.add_dll_directory(_gtk_path)
            break


def _load_css() -> str:
    try:
        return CSS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def render_cv_html(
    tailored_cv: dict,
    headshot_data_uri: str | None = None,
    candidate_name: str = "Your Name",
    candidate_title: str = "",
    contact_line: str = "",
    cv_sections: dict | None = None,
) -> str:
    """
    Renders cv_template.html with the provided data and returns the HTML string.

    Args:
        tailored_cv:      dict with keys: summary (str), experience (list of dicts)
        headshot_data_uri: base64 data-URI string or None
        candidate_name:   full name for the CV header
        candidate_title:  job title / tagline for the header
        contact_line:     email, phone, LinkedIn, etc.
        cv_sections:      dict from cv_parser.parse_cv_sections — contains skills,
                          education, certifications, languages

    Returns:
        Rendered HTML string ready for WeasyPrint.
    """
    sections = cv_sections or {}
    skills = sections.get("skills", {})

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("cv_template.html")

    html = template.render(
        css=_load_css(),
        candidate_name=candidate_name,
        candidate_title=candidate_title,
        contact_line=contact_line,
        headshot_uri=headshot_data_uri or "",
        summary=tailored_cv.get("summary", ""),
        experience=tailored_cv.get("experience", []),
        skills_governance=skills.get("governance", []),
        skills_technical=skills.get("technical", []),
        skills_tools=skills.get("tools", []),
        education=sections.get("education", []),
        certifications=sections.get("certifications", []),
        languages=sections.get("languages", []),
    )
    return html


def generate_cv_pdf(
    tailored_cv: dict,
    headshot_data_uri: str | None = None,
    candidate_name: str = "Your Name",
    candidate_title: str = "",
    contact_line: str = "",
    cv_sections: dict | None = None,
) -> bytes:
    """
    Renders the CV template and converts it to a PDF using WeasyPrint.

    Returns:
        PDF as bytes, suitable for st.download_button.

    Raises:
        RuntimeError: if WeasyPrint or GTK+ is not available, or rendering fails.
    """
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError(
            "WeasyPrint is not available. On Windows, install the GTK+ runtime from "
            "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases"
        ) from exc

    try:
        html_string = render_cv_html(
            tailored_cv=tailored_cv,
            headshot_data_uri=headshot_data_uri,
            candidate_name=candidate_name,
            candidate_title=candidate_title,
            contact_line=contact_line,
            cv_sections=cv_sections,
        )
        pdf_bytes = HTML(string=html_string, base_url=str(TEMPLATES_DIR)).write_pdf()
        return pdf_bytes
    except Exception as exc:
        raise RuntimeError(f"PDF generation failed: {exc}") from exc


def generate_cover_letter_pdf(
    cover_letter_text: str,
    candidate_name: str = "",
) -> bytes:
    """
    Wraps cover letter plain text in minimal HTML and converts to PDF.

    Returns:
        PDF as bytes, suitable for st.download_button.
    """
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError(
            "WeasyPrint is not available. Install the GTK+ runtime on Windows."
        ) from exc

    # Escape the text and convert newlines to <br> / paragraphs
    import html as html_lib
    escaped = html_lib.escape(cover_letter_text)
    paragraphs = "".join(
        f"<p>{para.strip()}</p>"
        for para in escaped.split("\n\n")
        if para.strip()
    )

    html_string = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <style>
        @page {{ size: A4; margin: 25mm 20mm; }}
        body {{ font-family: Georgia, serif; font-size: 11pt; color: #222; line-height: 1.6; }}
        h1 {{ font-size: 13pt; margin-bottom: 4px; color: #1a2a3a; }}
        hr {{ border: none; border-top: 1px solid #ccc; margin: 8px 0 20px 0; }}
        p {{ margin: 0 0 12px 0; text-align: justify; }}
      </style>
    </head>
    <body>
      {'<h1>' + html_lib.escape(candidate_name) + '</h1><hr>' if candidate_name else ''}
      {paragraphs}
    </body>
    </html>
    """

    try:
        return HTML(string=html_string).write_pdf()
    except Exception as exc:
        raise RuntimeError(f"Cover letter PDF generation failed: {exc}") from exc
