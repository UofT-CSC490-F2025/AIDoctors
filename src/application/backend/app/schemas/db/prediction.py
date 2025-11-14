import ast
from typing import Any, Optional
from pydantic import BaseModel, Field, validator


class DDIPredictRequest(BaseModel):
    # Required core fields
    patient_uuid: str = Field(examples=["patient-12345"])
    drug1: str = Field(examples=["Warfarin"])
    drug2: str = Field(examples=["Aspirin"])
    drug1_norm: Optional[str] = Field(default=None, examples=["warfarin"])
    drug2_norm: Optional[str] = Field(default=None, examples=["aspirin"])
    overlap_start: Optional[str] = Field(default=None, examples=["2024-01-15"])
    overlap_stop: Optional[str] = Field(default=None, examples=["2024-02-15"])
    Age: Optional[int] = Field(
        default=None,
        examples=[65]
    )
    Sex: Optional[str] = Field(default=None, examples=["M"])
    Comorbidities: Optional[Any] = Field(
        default=None,
        examples=[["Hypertension", "Diabetes"]]
    )
    pair_key: Optional[str] = Field(default=None, examples=["warfarin_aspirin"])

    # Optional labels/context
    unified_severity: Optional[str] = Field(default=None, examples=["Major"])
    unified_mechanism_text: Optional[str] = Field(
        default=None,
        examples=["Both drugs affect blood clotting mechanisms"]
    )
    ddi_confidence: Optional[float] = Field(default=None, examples=[0.95])
    ddi_known: Optional[bool] = Field(default=None, examples=[True])

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
    patient_uuid: str = Field(examples=["patient-12345"])
    severity: str = Field(examples=["Major"])
    completion: str = Field(
        examples=[
            '{"severity": "Major"} The combination of warfarin and aspirin significantly increases bleeding risk due to their synergistic anticoagulant effects.'
        ]
    )
    model_path: str = Field(examples=["Qwen/Qwen2.5-0.5B"])
    used_prompt: str = Field(
        examples=[
            "A patient is concurrently prescribed two medications.\n\nPatient information:\n- Age: 65\n- Sex: M\n- Comorbidities: ['Hypertension', 'Diabetes']\n\nMedication exposure:\n- Start: 2024-01-15\n- End: 2024-02-15\n- Overlap days: 31\n\nDrugs:\n- Drug 1: warfarin\n- Drug 2: aspirin\n- Known interaction in clinical sources: True\n- Number of data sources supporting this: 0.95\n\nMechanistic context:\nBoth drugs affect blood clotting mechanisms\n\nReturn:\n1) A JSON object: {\"severity\":\"<Minor|Moderate|Major>\"} (exactly).\n2) 1–3 sentence explanation citing your decision"
        ]
    )
    # Optional echo of known label if provided
    known_severity: Optional[str] = Field(default=None, examples=["Major"])
