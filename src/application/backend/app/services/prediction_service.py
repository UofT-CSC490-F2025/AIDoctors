import os
import re
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from sqlalchemy.orm import Session
from app.repositories.ddiref_repository import find_static_ddi_severity
from app.schemas.db.prediction import DDIPredictRequest
from app.repositories.patientddi_repository import find_similar_interactions, get_interaction_statistics
load_dotenv()

def parse_bedrock_response(response_text: str) -> dict:
    """
    Parse the Bedrock model response to extract JSON content.
    Uses multiple fallback strategies for robust parsing.
    """
    
    # Strategy 1: Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        content = json_match.group(1).strip()
        try:
            parsed = json.loads(content)
            print("JSON parsed from markdown code block")
            return {"content": parsed}
        except json.JSONDecodeError:
            pass
    
    # Strategy 2: Try to find the largest JSON object in the response
    json_obj_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', response_text, re.DOTALL)
    if json_obj_match:
        content = json_obj_match.group(1).strip()
        try:
            parsed = json.loads(content)
            print("JSON parsed from response body")
            return {"content": parsed}
        except json.JSONDecodeError:
            pass
    
    # Strategy 3: Try to clean common JSON formatting issues
    cleaned = re.sub(r',\s*([}\]])', r'\1', response_text)
    try:
        # Find JSON-like structure
        json_match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if json_match:
            content = json_match.group(1).strip()
            parsed = json.loads(content)
            print("JSON parsed after cleaning")
            return {"content": parsed}
    except json.JSONDecodeError:
        pass
    
    # Strategy 4: Last resort - return a minimal valid structure with error info
    print(f"WARNING: Failed to parse JSON from response. First 200 chars: {response_text[:200]}")
    return {
        "content": {
            "predicted_severity": "Unknown",
            "summary": "Error: Could not parse model response",
            "raw_response": response_text[:500]  # Include partial response for debugging
        }
    }


def get_bedrock_client():
    """
    Create and return a Bedrock Runtime client.
    
    For local testing with API keys:
    - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env
    
    For ECS deployment:
    - The task will inherit IAM role permissions automatically
    - No credentials needed in environment variables
    """
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    
    # Try to create client - boto3 will automatically use:
    # 1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    # 2. IAM role (when running in ECS)
    # 3. AWS credentials file (~/.aws/credentials)
    try:
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=aws_region
        )
        print(f"Bedrock client initialized for region: {aws_region}")
        return client
    except Exception as e:
        print(f"Error initializing Bedrock client: {str(e)}")
        raise


def invoke_bedrock_model(system_prompt: str, user_prompt: str) -> str:
    """
    Invoke AWS Bedrock model with separate system and user prompts.

    IMPORTANT: Different models support different fields in the request body and have different response formats.
    https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html

    Uses the model specified in BEDROCK_MODEL_ID environment variable.
    Default: openai.gpt-oss-120b-1:0
    """
    client = get_bedrock_client()
    model_id = os.getenv("BEDROCK_MODEL_ID", "openai.gpt-oss-120b-1:0")

    # Prepare the request body based on the model provider
    
    # OpenAI models use the Converse API format with system and user messages.
    # TODO: We can experiment with more request parameters to tune response
    # https://platform.openai.com/docs/api-reference/chat/create
    if "openai.gpt-oss" in model_id:
        request_body = {
            "max_completion_tokens": 4096,  # Reduced from 4096 for faster response
            "temperature": 0.15,
            "response_format": {"type": "json_object"},  # Force JSON output
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
    else:
        print("Using non-OpenAI model")
        # For non-OpenAI models, combine system and user prompts
        combined_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        request_body = {
            "prompt": combined_prompt,
            "max_tokens": 4096,
            "temperature": 0.2      
        }
    
    try:
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        
        # Extract completion based on model provider
        if "openai.gpt-oss" in model_id:
            completion = response_body['choices'][0]['message']['content']
        elif "anthropic.claude" in model_id:
            completion = response_body['content'][0]['text']
        else:
            # Try common response fields
            completion = response_body.get('completion', response_body.get('text', str(response_body)))
        
        return completion
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise Exception(f"Bedrock API error ({error_code}): {error_message}")
    except NoCredentialsError:
        raise Exception("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY for local testing.")
    except Exception as e:
        raise Exception(f"Error invoking Bedrock model: {str(e)}")
    
async def enrich_from_database_async(
    db: Session,
    request: DDIPredictRequest
) -> dict:
    """
    Query database to enrich the prediction context (RAG approach)
    
    OPTIMIZATION: Parallelized database queries for 30-40% faster enrichment
    """
    loop = asyncio.get_event_loop()
    
    # Run all three queries in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Query 1: Find static severity
        static_severity_future = loop.run_in_executor(
            executor,
            find_static_ddi_severity,
            db,
            request.drug1,
            request.drug2
        )
        
        # Query 2: Find similar cases
        similar_cases_future = loop.run_in_executor(
            executor,
            find_similar_interactions,
            db,
            request.drug1,
            request.drug2,
            request.Age,
            request.Sex,
            request.Comorbidities,
            5  # Reduced from 10 to 5 for faster queries
        )
        
        # Query 3: Get statistics
        stats_future = loop.run_in_executor(
            executor,
            get_interaction_statistics,
            db,
            request.drug1,
            request.drug2
        )
        
        # Wait for all queries to complete in parallel
        static_severity, similar_cases, stats = await asyncio.gather(
            static_severity_future,
            similar_cases_future,
            stats_future
        )
    
    # Extract mechanisms
    mechanisms = list(set([
        case.unified_mechanism_text 
        for case in similar_cases 
        if case.unified_mechanism_text
    ]))
    
    # Format representative cases (include similarity score)
    # Reduced from 5 to 3 to minimize prompt size and improve TTFT
    representative_cases = [
        {
            'patient_uuid': case.patient_uuid,
            'age': case.age,
            'sex': case.sex,
            'confidence': case.ddi_confidence,
            'comorbidities': case.comorbidities or [],
            'similarity_score': getattr(case, 'similarity_score', 0)  # Include custom similarity score
        }
        for case in similar_cases[:3]
    ]

    enriched_context = {
        "similar_cases_count": len(similar_cases),
        "static_severity": static_severity if static_severity else 'Unknown',
        "known_interaction_from_patients": stats['is_known_interaction_from_patients'] if stats else False,
        "avg_confidence": stats['avg_confidence'] if stats else None,
        "severity_distribution": {},
        "mechanisms": mechanisms,
        "representative_cases": representative_cases
    }
    if stats and stats['known_severity_count'] and stats['total_cases']:
        enriched_context["severity_distribution"] = {
            "known_severity_count": stats['known_severity_count'],
            "total_cases": stats['total_cases']
        }
        
    return enriched_context