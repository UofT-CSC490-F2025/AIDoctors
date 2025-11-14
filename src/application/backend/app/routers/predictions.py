from fastapi import APIRouter, Depends, HTTPException
import torch

from app.dependencies import get_current_active_user
from app.schemas.prediction import DDIPredictRequest, DDIPredictResponse
from app.services.prediction_service import (
    build_prompt,
    extract_severity,
    get_model_and_tokenizer,
)


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/")
async def predict(request: DDIPredictRequest) -> DDIPredictResponse:
    """
    Accepts application/json requests only.
    For form-data support, install python-multipart: pip install python-multipart
    """

    # Build prompt
    prompt = build_prompt(request)

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
            patient_uuid=request.patient_uuid,
            severity=severity,
            completion=completion,
            model_path=model_path,
            used_prompt=prompt,
            known_severity=request.unified_severity,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error during model inference: {str(e)}"
        )
