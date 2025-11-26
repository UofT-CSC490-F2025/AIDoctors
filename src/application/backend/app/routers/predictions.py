import json
from fastapi import APIRouter, Depends, HTTPException
import os
import asyncio
from functools import partial
from sqlalchemy.orm import Session
from app.dependencies import get_current_active_user, get_db
from app.schemas.db.prediction import DDIPredictRequest, DDIPredictResponse
from app.schemas.bedrock.bedrock import build_system_prompt, build_user_prompt
from app.services.prediction_service import (
    invoke_bedrock_model,
    parse_bedrock_response,
    enrich_from_database,
)


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"],
    dependencies=[Depends(get_current_active_user)],
)


@router.post("/")
async def predict(request: DDIPredictRequest, db: Session = Depends(get_db)) -> DDIPredictResponse:
    """
    Predict drug-drug interaction severity using AWS Bedrock.

    Accepts application/json requests only.
    For form-data support, install python-multipart: pip install python-multipart
    """

    # Build separate system and user prompts
    enriched_context = enrich_from_database(db, request)

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(request, enriched_context)

    # Get model ID for response
    model_id = os.getenv("BEDROCK_MODEL_ID", "openai.gpt-oss-120b-1:0")

    # Invoke Bedrock model in thread pool to avoid blocking the event loop
    try:
        # Run the blocking boto3 call in a thread pool executor
        loop = asyncio.get_event_loop()
        completion = await loop.run_in_executor(
            None,  # Use default ThreadPoolExecutor
            partial(invoke_bedrock_model, system_prompt, user_prompt),
        )

        # Parse the response to extract reasoning and content
        parsed_response = parse_bedrock_response(completion)
        severity = parsed_response['content'].get('severity', 'Unknown')
        if 'predicted_severity' in parsed_response['content']:
            severity = parsed_response['content']['predicted_severity']
        return DDIPredictResponse(
            drug1=request.drug1,
            drug2=request.drug2,
            severity=severity,
            reasoning=parsed_response['reasoning'],
            completion=json.dumps(parsed_response['content']),
            model_path=model_id,
            enriched_context=enriched_context
        )
    except Exception as e:
        print("Error during Bedrock inference:", str(e))
        raise HTTPException(
            status_code=500, detail=f"Error during Bedrock inference: {str(e)}"
        )
