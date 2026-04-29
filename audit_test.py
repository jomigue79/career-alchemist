"""
audit_test.py
Smoke-test and content audit for the core AI pipeline.

Run from the project root (with venv active):
    python audit_test.py

Checks:
  1. AI tailoring engine returns a valid JSON structure
  2. Each bullet follows Action-Governance-Impact syntax (starts with a strong verb)
  3. No hallucinated facts (invented metrics/percentages/team sizes not in baseline CV)
  4. No duration summing across roles (e.g. "10 years PM experience")
  5. PDF generation produces non-empty bytes
"""

import re
from optimizer import get_tailored_cv
from pdf_exporter import render_cv_html, generate_cv_pdf

# ---------------------------------------------------------------------------
# Mock inputs
# ---------------------------------------------------------------------------

MOCK_JD = """
Role: Technical Project Manager (AI/Operations)
Requirements:
- Mastery of Governance Frameworks (PM² or Prince2).
- Experience in SDLC for enterprise software.
- Proven ability to manage RAID logs and technical debt.
- Strong background in AI/Python for automation.
"""

# Minimal but representative baseline CV — enough for the optimizer to work with
MOCK_CV = """
Joao Correia
Technical Project Manager | PM² Specialist

Professional Experience:
- Ground Control Studios (2021–2024): Led cross-functional delivery of a live-ops gaming
  platform, managing RAID logs, technical debt backlog, and a team of 8 engineers.
  Implemented PM² governance framework across all workstreams.
- Freelance AI Consultant (2019–2021): Built Python automation pipelines for SME clients,
  reducing manual reporting time. Delivered SDLC governance for bespoke SaaS builds.

Certifications: PM² Practitioner, Prince2 Foundation, Google Project Management
Skills: SDLC, RAID Logs, Technical Debt Management, Python, AI Automation, Agile, Scrum
"""

# ---------------------------------------------------------------------------
# Step 1 — AI tailoring engine
# ---------------------------------------------------------------------------

print("Audit Step 1: Running AI Tailoring Engine...")
tailored_data = get_tailored_cv(MOCK_CV, MOCK_JD)

# ---------------------------------------------------------------------------
# Step 2 — Validate JSON structure
# ---------------------------------------------------------------------------

print("\nAudit Step 2: Validating JSON Structure...")
required_keys = ["summary", "experience"]
if all(k in tailored_data for k in required_keys):
    print("  ✅ Top-level keys present")
else:
    missing = [k for k in required_keys if k not in tailored_data]
    print(f"  ❌ Missing keys: {missing}")

# Validate each experience entry has the expected fields
exp_keys = ["company", "role", "period", "bullets"]
for i, role in enumerate(tailored_data.get("experience", [])):
    missing_exp = [k for k in exp_keys if k not in role]
    if missing_exp:
        print(f"  ❌ Experience[{i}] missing: {missing_exp}")
    else:
        print(f"  ✅ Experience[{i}] ({role.get('company', '?')}) structure valid")

# ---------------------------------------------------------------------------
# Step 3 — PDF generation
# ---------------------------------------------------------------------------

print("\nAudit Step 3: Generating Test PDF...")
pdf_bytes = generate_cv_pdf(tailored_data)

if pdf_bytes and len(pdf_bytes) > 1000:
    print(f"  ✅ PDF generated successfully ({len(pdf_bytes):,} bytes)")
else:
    print("  ❌ PDF generation failed or output is suspiciously small")

# ---------------------------------------------------------------------------
# Step 4 — Action-Governance-Impact bullet syntax check
# ---------------------------------------------------------------------------

# Strong action verbs drawn from voice_params.json
ACTION_VERBS = {
    "architected", "orchestrated", "deployed", "standardised", "standardized",
    "mitigated", "led", "built", "delivered", "implemented", "established",
    "accelerated", "ensured", "streamlined", "designed", "developed",
    "managed", "spearheaded", "drove", "created", "authored", "launched",
    "consolidated", "reduced", "increased", "optimised", "optimized",
    "automated", "aligned", "coordinated", "facilitated", "overhauled",
    "governed", "engineered", "directed", "championed", "transformed",
    "introduced", "scaled", "secured", "executed", "owned", "shaped",
}

print("\nAudit Step 4: Bullet Syntax — Action-Governance-Impact...")
all_bullets = [
    (role["company"], bullet)
    for role in tailored_data.get("experience", [])
    for bullet in role.get("bullets", [])
]
syntax_failures = []
for company, bullet in all_bullets:
    first_word = bullet.strip().split()[0].rstrip(",").lower() if bullet.strip() else ""
    if first_word not in ACTION_VERBS:
        syntax_failures.append((company, bullet[:80], first_word))

if not syntax_failures:
    print(f"  ✅ All {len(all_bullets)} bullets start with a recognised action verb")
else:
    print(f"  ⚠️  {len(syntax_failures)}/{len(all_bullets)} bullets may not follow the pattern:")
    for company, snippet, word in syntax_failures:
        print(f"       [{company}] first word '{word}' → {snippet}...")

# ---------------------------------------------------------------------------
# Step 5 — Hallucination check (invented facts not in baseline CV)
# ---------------------------------------------------------------------------

print("\nAudit Step 5: Hallucination Check...")

# Numbers that appear in the baseline CV are allowed; any NEW number is a red flag
ALLOWED_NUMBERS = {"8", "2021", "2024", "2019", "2021"}

hallucination_flags = []
# Pattern: a number followed by optional % or a word — e.g. "40%", "50 engineers", "12 years"
number_pattern = re.compile(r'\b(\d+)\s*(%|engineers?|developers?|staff|years?|months?|million|k\b)', re.IGNORECASE)

all_text_fields = [tailored_data.get("summary", "")] + [
    bullet
    for role in tailored_data.get("experience", [])
    for bullet in role.get("bullets", [])
]

for text in all_text_fields:
    for match in number_pattern.finditer(text):
        num = match.group(1)
        if num not in ALLOWED_NUMBERS:
            hallucination_flags.append(f"  Suspect: '{match.group(0)}' in → {text[:80]}...")

if not hallucination_flags:
    print(f"  ✅ No invented metrics detected across {len(all_text_fields)} text fields")
else:
    print(f"  ⚠️  {len(hallucination_flags)} potential hallucination(s) found:")
    for flag in hallucination_flags:
        print(f"     {flag}")

# ---------------------------------------------------------------------------
# Step 6 — Duration summing check
# ---------------------------------------------------------------------------

print("\nAudit Step 6: Duration Summing Check...")
duration_sum_pattern = re.compile(
    r'\b(\d{2})\s+years?\s+(of\s+)?(experience|background|expertise)',
    re.IGNORECASE
)
sum_violations = []
for text in all_text_fields:
    match = duration_sum_pattern.search(text)
    if match and int(match.group(1)) > 9:
        sum_violations.append(f"  Suspect: '{match.group(0)}' → {text[:80]}...")

if not sum_violations:
    print("  ✅ No cross-role duration summing detected")
else:
    print(f"  ❌ {len(sum_violations)} violation(s):")
    for v in sum_violations:
        print(v)

# ---------------------------------------------------------------------------
# Final report
# ---------------------------------------------------------------------------

total_warnings = len(syntax_failures) + len(hallucination_flags) + len(sum_violations)
print("\n" + "─" * 55)
if total_warnings == 0:
    print("✅ AUDIT PASSED — 0 warnings across all content checks")
else:
    print(f"⚠️  AUDIT COMPLETE — {total_warnings} warning(s) require review")
print("─" * 55)
