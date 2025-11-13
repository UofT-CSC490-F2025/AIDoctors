import ast
from typing import Any, Optional
from pydantic import BaseModel, Field, validator


class DDIPredictRequest(BaseModel):
    # Required core fields
    patient_uuid: str
    drug1: Optional[str] = None
    drug2: Optional[str] = None
    drug1_norm: Optional[str] = None
    drug2_norm: Optional[str] = None
    overlap_start: Optional[str] = None
    overlap_stop: Optional[str] = None
    Age: Optional[int] = Field(
        None, description="Age in years (can be negative in synthetic data)"
    )
    Sex: Optional[str] = None
    Comorbidities: Optional[Any] = Field(
        None, description="List[str] or stringified list"
    )
    pair_key: Optional[str] = None

    # Optional labels/context
    unified_severity: Optional[str] = None
    unified_mechanism_text: Optional[str] = None
    ddi_confidence: Optional[float] = None
    ddi_known: Optional[bool] = None

    @validator("Comorbidities", pre=True)
    def coerce_comorbidities(cls, v):
        if v is None:
            return []
        # Already a list
        if isinstance(v, list):
            return v
        # Try to parse stringified python list "['a','b']"
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = ast.literal_eval(v)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            # Fallback: split by comma
            return [s.strip() for s in v.split(",") if s.strip()]
        return []

    @validator("ddi_known", pre=True)
    def coerce_bool(cls, v):
        if isinstance(v, bool) or v is None:
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            sv = v.strip().lower()
            if sv in {"true", "1", "yes", "y"}:
                return True
            if sv in {"false", "0", "no", "n"}:
                return False
        return None

    @validator("ddi_confidence", pre=True)
    def coerce_float(cls, v):
        if v is None:
            return None
        try:
            return float(v)
        except Exception:
            return None


class DDIPredictResponse(BaseModel):
    patient_uuid: str
    severity: str
    completion: str
    model_path: str
    used_prompt: str
    # Optional echo of known label if provided
    known_severity: Optional[str] = None
