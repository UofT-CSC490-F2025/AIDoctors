from __future__ import annotations

import os
import re
import json
import ast
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

# ---------------------------
# Input/Output schemas
# ---------------------------

class DDIPredictRequest(BaseModel):
    # Required core fields
    patient_uuid: str
    drug1: Optional[str] = None
    drug2: Optional[str] = None
    drug1_norm: Optional[str] = None
    drug2_norm: Optional[str] = None
    overlap_start: Optional[str] = None
    overlap_stop: Optional[str] = None
    Age: Optional[int] = Field(None, description="Age in years (can be negative in synthetic data)")
    Sex: Optional[str] = None
    Comorbidities: Optional[Any] = Field(None, description="List[str] or stringified list")
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


# ---------------------------
# Utilities
# ---------------------------

SEVERITIES = {"major": "Major", "moderate": "Moderate", "minor": "Minor"}

def extract_severity(text: str) -> str:
    """
    Extract {"severity": "<...>"} and the following from the model output.
    Robust to extra text and varied casing.
    """
    # Try to find a JSON-like severity block
    match = re.search(r'\{[^}]*"severity"\s*:\s*"([^"]+)"[^}]*\}', text, flags=re.IGNORECASE)
    severity = "Unknown"
    if match:
        sev_raw = match.group(1).strip().lower()
        for key in SEVERITIES:
            if key in sev_raw:
                severity = SEVERITIES[key]
                break


    return severity


def parse_date(s: Optional[str]) -> Optional[datetime]:
    if not s or not isinstance(s, str):
        return None
    # Try a few formats used in dataset
    for fmt in ("%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S+00:00", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            # Handle "+00:00" as UTC offset if %z not matched
            if fmt.endswith("+00:00") and s.endswith("+00:00"):
                s_fixed = s.replace("+00:00", "+0000")
                fmt_fixed = fmt.replace("+00:00", "%z")
                return datetime.strptime(s_fixed, fmt_fixed)
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def compute_overlap_days(start: Optional[str], stop: Optional[str]) -> Optional[int]:
    ds, de = parse_date(start), parse_date(stop)
    if ds and de:
        return max(0, (de - ds).days)
    return None


def build_prompt(payload: DDIPredictRequest) -> str:
    """
    Build the exact instruction format used during training.
    """
    age = payload.Age if payload.Age is not None else ""
    sex = payload.Sex or ""
    comorbidities = payload.Comorbidities or []
    start = payload.overlap_start or ""
    end = payload.overlap_stop or ""
    overlap_days = compute_overlap_days(payload.overlap_start, payload.overlap_stop)
    ol_days_str = str(overlap_days) if overlap_days is not None else ""

    drug1 = payload.drug1_norm or payload.drug1 or ""
    drug2 = payload.drug2_norm or payload.drug2 or ""
    known = payload.ddi_known
    known_str = "Unknown" if known is None else ("True" if known else "False")
    support = "" if payload.ddi_confidence is None else str(payload.ddi_confidence)
    mech = payload.unified_mechanism_text or ""

    prompt = (
        "A patient is concurrently prescribed two medications.\n\n"
        "          Patient information:\n"
        f"          - Age: {age}\n"
        f"          - Sex: {sex}\n"
        f"          - Comorbidities: {comorbidities}\n\n"
        "          Medication exposure:\n"
        f"          - Start: {start}\n"
        f"          - End: {end}\n"
        f"          - Overlap days: {ol_days_str}\n\n"
        "          Drugs:\n"
        f"          - Drug 1: {drug1}\n"
        f"          - Drug 2: {drug2}\n"
        f"          - Known interaction in clinical sources: {known_str}\n"
        f"          - Number of data sources supporting this: {support}\n\n"
        "          Mechanistic context:\n"
        f"          {mech}\n\n"
        "          Return:\n"
        '          1) A JSON object: {"severity":"<Minor|Moderate|Major>"} (exactly).\n'
        "          2) 1–3 sentence explanation citing your decision\n"
    )
    return prompt


def resolve_model_path() -> str:
    """
    Resolve a local fine-tuned model path. Tries env var DDI_MODEL_PATH first, then a few fallbacks.
    """
    env_path = os.environ.get("DDI_MODEL_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    here = Path(__file__).resolve()
    project_root = here.parents[3] if len(here.parents) >= 4 else here.parent.parent.parent
    candidates = [
        project_root / "local_checkpoints" / "grpo_ddi_model",
        project_root / "local_checkpoints",
        project_root / "checkpoints" / "grpo_ddi_model",
        Path.cwd() / "local_checkpoints" / "grpo_ddi_model",
        Path.cwd() / "local_checkpoints",
    ]
    for c in candidates:
        if c.is_dir():
            # If directory contains a HF model (config.json/tokenizer files), prefer it.
            if (c / "config.json").exists() or (c / "tokenizer.json").exists() or (c / "tokenizer_config.json").exists():
                return str(c)
            # Or if it has a single subdir that looks like a model
            subdirs = [p for p in c.iterdir() if p.is_dir()]
            for sd in subdirs:
                if (sd / "config.json").exists() or (sd / "tokenizer_config.json").exists():
                    return str(sd)
            return str(c)
    # Fallback to base model if no local checkpoints found
    return "Qwen/Qwen2.5-0.5B"


@lru_cache(maxsize=1)
def get_model_and_tokenizer():
    model_path = resolve_model_path()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

    print(f"Loading model from: {model_path}")
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        device_map="auto" if device == "cuda" else None,
        torch_dtype=dtype if device == "cuda" else None,
    )
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id

    gen_cfg = GenerationConfig(
        max_new_tokens=256,
        temperature=0.7,
        do_sample=False,
        top_p=1.0,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    return model, tokenizer, gen_cfg, model_path


# ---------------------------
# Prediction endpoint
# ---------------------------

async def predict(request: Request) -> DDIPredictResponse:
    """
    Accepts application/json requests only.
    For form-data support, install python-multipart: pip install python-multipart
    """
    payload_dict: Dict[str, Any]
    
    # Try to parse as JSON
    try:
        payload_dict = await request.json()
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid JSON format: {str(e)}. Please ensure your request body is valid JSON."
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error parsing request: {str(e)}"
        )

    # Validate and parse the payload
    try:
        payload = DDIPredictRequest(**payload_dict)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input data: {str(e)}"
        )

    # Build prompt
    prompt = build_prompt(payload)

    # Load model
    try:
        model, tokenizer, gen_cfg, model_path = get_model_and_tokenizer()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model: {str(e)}"
        )

    # Tokenize and generate
    try:
        inputs = tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(**inputs, generation_config=gen_cfg)
        full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # If model echoes prompt, try to strip it
        if full_text.startswith(prompt):
            completion = full_text[len(prompt):].lstrip()
        else:
            completion = full_text

        severity = extract_severity(completion)

        return DDIPredictResponse(
            patient_uuid=payload.patient_uuid,
            severity=severity,
            completion=completion,
            model_path=model_path,
            used_prompt=prompt,
            known_severity=payload.unified_severity,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during model inference: {str(e)}"
        )