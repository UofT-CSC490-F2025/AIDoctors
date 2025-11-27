from typing import Optional, Dict, Any
import boto3, time, random

from .config import REGION, MODEL_ID, TEMPERATURE, TOP_P, MAX_TOKENS

def get_bedrock_runtime():
    return boto3.client("bedrock-runtime", region_name=REGION)

def _collect_text(resp: Dict[str, Any]) -> str:
    blocks = resp.get("output", {}).get("message", {}).get("content", [])
    out = []
    for b in blocks:
        if "text" in b:
            out.append(b["text"])
    return "\n".join(out).strip()

def converse(user_text: str,
             system_text: Optional[str] = None,
             temperature: float = TEMPERATURE,
             top_p: float = TOP_P,
             max_tokens: int = MAX_TOKENS,
             retries: int = 3,
             backoff: float = 1.5) -> str:
    rt = get_bedrock_runtime()
    messages = [{"role": "user", "content": [{"text": user_text}]}]
    system = [{"text": system_text}] if system_text else None
    last_err = None
    for a in range(retries):
        try:
            resp = rt.converse(
                modelId=MODEL_ID,
                messages=messages,
                system=system,
                inferenceConfig={"temperature": temperature, "topP": top_p, "maxTokens": max_tokens},
            )
            return _collect_text(resp)
        except Exception as e:
            last_err = e
            time.sleep((backoff ** a) + random.random() * 0.2)
    raise last_err if last_err else RuntimeError("Unknown Bedrock error")
