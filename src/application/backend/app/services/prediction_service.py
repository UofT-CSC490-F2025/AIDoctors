import os
import re
from dotenv import load_dotenv
from functools import lru_cache
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

from app.schemas.prediction import DDIPredictRequest
from app.utils.helpers import compute_overlap_days


load_dotenv()


SEVERITIES = {"major": "Major", "moderate": "Moderate", "minor": "Minor"}

_CACHED_MODEL = None
_CACHED_TOKENIZER = None
_CACHED_GEN_CFG = None
_CACHED_MODEL_PATH = None
_CACHED_DEVICE = None

def extract_severity(text: str) -> str:
    """
    Extract {"severity": "<...>"} and the following from the model output.
    Robust to extra text and varied casing.
    """
    # Try to find a JSON-like severity block
    match = re.search(
        r'\{[^}]*"severity"\s*:\s*"([^"]+)"[^}]*\}', text, flags=re.IGNORECASE
    )
    severity = "Unknown"
    if match:
        sev_raw = match.group(1).strip().lower()
        for key in SEVERITIES:
            if key in sev_raw:
                severity = SEVERITIES[key]
                break

    return severity


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
    env_path = os.getenv("DDI_MODEL_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    here = Path(__file__).resolve()
    project_root = (
        here.parents[3] if len(here.parents) >= 4 else here.parent.parent.parent
    )
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
            if (
                (c / "config.json").exists()
                or (c / "tokenizer.json").exists()
                or (c / "tokenizer_config.json").exists()
            ):
                return str(c)
            # Or if it has a single subdir that looks like a model
            subdirs = [p for p in c.iterdir() if p.is_dir()]
            for sd in subdirs:
                if (sd / "config.json").exists() or (
                    sd / "tokenizer_config.json"
                ).exists():
                    return str(sd)
            return str(c)
    # Fallback to base model if no local checkpoints found
    return "Qwen/Qwen2.5-0.5B"


def get_model_and_tokenizer():
    """
    Load and cache the model/tokenizer so we don't reload on every request.

    Returns:
        model, tokenizer, gen_cfg, model_path
    """
    global _CACHED_MODEL, _CACHED_TOKENIZER, _CACHED_GEN_CFG, _CACHED_MODEL_PATH, _CACHED_DEVICE

    if _CACHED_MODEL is not None and _CACHED_TOKENIZER is not None:
        return _CACHED_MODEL, _CACHED_TOKENIZER, _CACHED_GEN_CFG, _CACHED_MODEL_PATH

    try:
        model_path = resolve_model_path()
    except NameError:
        model_path = os.getenv("DDI_MODEL_PATH", "Qwen/Qwen2.5-0.5B")

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

    _CACHED_MODEL = model
    _CACHED_TOKENIZER = tokenizer
    _CACHED_GEN_CFG = gen_cfg
    _CACHED_MODEL_PATH = model_path
    _CACHED_DEVICE = device

    return model, tokenizer, gen_cfg, model_path

