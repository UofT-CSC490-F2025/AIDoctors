import ast
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class DDIPredictRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    # Required core fields
    patient_uuid: Optional[str] = Field(default=None, examples=["patient-12345"])
    drug1: str = Field(examples=["amlodipine"])
    drug2: str = Field(examples=["lisinopril"])
    Age: Optional[int] = Field(default=None, examples=[65])
    Sex: Optional[str] = Field(default=None, examples=["M"])
    Comorbidities: Optional[Any] = Field(
        default=None, examples=[["Hypertension", "Diabetes"]]
    )
    pair_key: Optional[str] = Field(default=None, examples=["amlodipine_lisinopril"])

    # Optional labels/context
    unified_severity: Optional[str] = Field(default=None, examples=["Moderate"])
    unified_mechanism_text: Optional[str] = Field(
        default=None, examples=["Both drugs lower blood pressure and may cause hypotension"]
    )
    ddi_confidence: Optional[float] = Field(default=None, examples=[0.95])
    ddi_known: Optional[bool] = Field(default=None, examples=[True])

    @field_validator("Comorbidities", mode="before")
    @classmethod
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

    @field_validator("ddi_known", mode="before")
    @classmethod
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


class DDIPredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    drug1: str = Field(examples=["amlodipine"])
    drug2: str = Field(examples=["lisinopril"])
    severity: str = Field(examples=["Moderate"])
    reasoning: str = Field(examples=[
        "The combination of amLODIPine and lisinopril may cause additive hypotensive effects, requiring blood pressure monitoring."
    ])
    completion: str = Field(
        examples=[
            '{"severity": "Moderate"} The combination of amLODIPine and lisinopril may cause additive hypotensive effects, requiring blood pressure monitoring.'
        ]
    )
    model_path: str = Field(examples=["Qwen/Qwen2.5-0.5B"])
    # Optional echo of known label if provided
    known_severity: Optional[str] = Field(default=None, examples=["Moderate"])
    enriched_context: Optional[dict] = Field(default=None, examples=[{
        "similar_cases": [],
        "top_mechanisms": [],
        "representative_cases": [],
        "severity_distribution": {
            "known_severity_count": 10,
            "total_cases": 20
        }
    }])