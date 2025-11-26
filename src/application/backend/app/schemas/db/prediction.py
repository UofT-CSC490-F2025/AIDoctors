import ast
from typing import Any, Optional
from pydantic import BaseModel, Field, validator


class DDIPredictRequest(BaseModel):
    # Required core fields
    patient_uuid: Optional[str] = Field(default=None, examples=["patient-12345"])
    drug1: str = Field(examples=["Warfarin"])
    drug2: str = Field(examples=["Aspirin"])
    drug1_norm: Optional[str] = Field(default=None, examples=["warfarin"])
    drug2_norm: Optional[str] = Field(default=None, examples=["aspirin"])
    overlap_start: Optional[str] = Field(default=None, examples=["2024-01-15"])
    overlap_stop: Optional[str] = Field(default=None, examples=["2024-02-15"])
    Age: Optional[int] = Field(default=None, examples=[65])
    Sex: Optional[str] = Field(default=None, examples=["M"])
    Comorbidities: Optional[Any] = Field(
        default=None, examples=[["Hypertension", "Diabetes"]]
    )
    pair_key: Optional[str] = Field(default=None, examples=["warfarin_aspirin"])

    # Optional labels/context
    unified_severity: Optional[str] = Field(default=None, examples=["Major"])
    unified_mechanism_text: Optional[str] = Field(
        default=None, examples=["Both drugs affect blood clotting mechanisms"]
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
    drug1: str = Field(examples=["Warfarin"])
    drug2: str = Field(examples=["Aspirin"])
    severity: str = Field(examples=["Major"])
    reasoning: str = Field(examples=[
        "The combination of warfarin and aspirin significantly increases bleeding risk due to their synergistic anticoagulant effects."
    ])
    completion: str = Field(
        examples=[
            '{"severity": "Major"} The combination of warfarin and aspirin significantly increases bleeding risk due to their synergistic anticoagulant effects.'
        ]
    )
    model_path: str = Field(examples=["Qwen/Qwen2.5-0.5B"])
    # Optional echo of known label if provided
    known_severity: Optional[str] = Field(default=None, examples=["Major"])
    enriched_context: Optional[dict] = Field(default=None, examples=[{
        "similar_cases": [],
        "top_mechanisms": [],
        "representative_cases": [],
        "severity_distribution": {
            "known_severity_count": 10,
            "total_cases": 20
        }
    }])