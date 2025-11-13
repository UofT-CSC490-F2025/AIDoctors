from fastapi import APIRouter, Request, HTTPException
import json
from typing import Any, Dict
import torch

from app.schemas.prediction import DDIPredictRequest, DDIPredictResponse
from app.services.prediction_service import (
    build_prompt,
    extract_severity,
    get_model_and_tokenizer,
)


router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/")
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
            detail=f"Invalid JSON format: {str(e)}. Please ensure your request body is valid JSON.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing request: {str(e)}")

    # Validate and parse the payload
    try:
        payload = DDIPredictRequest(**payload_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid input data: {str(e)}")

    # Build prompt
    prompt = build_prompt(payload)

    # Load model
    try:
        model, tokenizer, gen_cfg, model_path = get_model_and_tokenizer()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

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
            completion = full_text[len(prompt) :].lstrip()
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
            status_code=500, detail=f"Error during model inference: {str(e)}"
        )
