import re
import pandas as pd

ALLOWED = {"Minor", "Moderate", "Major"}

SYSTEM_PROMPT = (
    "You are a clinical safety assistant. Read the case and return:\n"
    "1) A JSON object on a new line with an explicit severity level for this DDI interaction (Minor, Moderate, or Major) \n"
    "2)A brief explanation grounded in mechanism.\n"
    '{"severity": "<Minor|Moderate|Major>"}'
)

def build_user_prompt(row: pd.Series) -> str:
    g = lambda k, d="": (str(row.get(k, d)) if pd.notna(row.get(k, d)) else d)
    return f"""A patient is concurrently prescribed two medications.

Patient information:
- Age: {g('age')}
- Sex: {g('sex')}
- Comorbidities: {g('comorbidities')}

Medication exposure:
- Start: {g('overlap_start')}
- End: {g('overlap_stop')}
- Overlap days: {g('overlap_days')}

Drugs:
- Drug 1: {g('drug1_norm') or g('drug1')}
- Drug 2: {g('drug2_norm') or g('drug2')}
- Known interaction in clinical sources: {g('ddi_known')}
- Number of data sources supporting this: {g('ddi_confidence')}

Mechanistic context:
{g('unified_mechanism_text')}

Return:
1) A JSON object: {{"severity":"<Minor|Moderate|Major>"}} (exactly).
2) 1–3 sentence explanation citing your decision
"""

SEV_RE = re.compile(r'\{[^}]*"severity"\s*:\s*"([^"]+)"[^}]*\}', flags=re.I)

def extract_severity(text: str):
    m = SEV_RE.search(text or "")
    if m:
        s = m.group(1).strip().capitalize()
        return s if s in ALLOWED else None
    # fallback: bare token
    m2 = re.search(r'\b(Minor|Moderate|Major)\b', text or "", flags=re.I)
    return m2.group(1).capitalize() if m2 else None
