import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
import os
import asyncio
from functools import partial
from sqlalchemy.orm import Session
from app.dependencies import get_current_active_user, get_db
from app.repositories.ddiref_repository import search_matching_drug_names
from app.repositories.patientddi_repository import search_comorbidities
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


@router.post("")
async def predict(
    request: DDIPredictRequest, db: Session = Depends(get_db)
) -> DDIPredictResponse:
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
        severity = parsed_response["content"].get("predicted_severity", "Unknown")
        return DDIPredictResponse(
            drug1=request.drug1,
            drug2=request.drug2,
            severity=severity,
            reasoning=parsed_response["reasoning"],
            completion=json.dumps(parsed_response["content"]),
            model_path=model_id,
            enriched_context=enriched_context,
            known_severity=enriched_context.get("static_severity", "Unknown"),
        )
    except Exception as e:
        print("Error during Bedrock inference:", str(e))
        raise HTTPException(
            status_code=500, detail=f"Error during Bedrock inference: {str(e)}"
        )


@router.get("/matching_drugs", response_model=List[str])
def search_matching_drugs(
    name: str = Query(
        ..., min_length=1, description="Name of the drug to search for"
    ),
    db: Session = Depends(get_db),
):
    """
    Route to search for drug names using the search_matching_drug_names utility.
    """
    return search_matching_drug_names(db, name, limit=5)


@router.get("/matching_comorbidities", response_model=List[str])
def search_comorbidities_route(
    name: str = Query(..., min_length=1, description="Name of the comorbidity to search for"),
    db: Session = Depends(get_db)
):
    """
    Route to search for comorbidity names.
    """
    return search_comorbidities(db, name, limit=5)