import os
import re
import json
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
    Parse the Bedrock model response to extract reasoning and content separately.
    No JSON parsing - just separate the components.
    """
    
    # Extract reasoning content between <reasoning> tags
    reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response_text, re.DOTALL | re.IGNORECASE)
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
    
    # Extract content after the reasoning tags
    content = response_text
    if reasoning_match:
        # Get everything after the closing reasoning tag
        content_start = response_text.find('</reasoning>') + len('</reasoning>')
        content = response_text[content_start:].strip()
    
    # Change Content to JSON
    content = json.loads(content)
    
    return {
        "reasoning": reasoning,
        "content": content,
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
            "max_completion_tokens": 4096,
            "temperature": 0.7,
            # "reasoning_effort": "high",
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
            "temperature": 0.7        
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
        
        print()
        return completion
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        raise Exception(f"Bedrock API error ({error_code}): {error_message}")
    except NoCredentialsError:
        raise Exception("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY for local testing.")
    except Exception as e:
        raise Exception(f"Error invoking Bedrock model: {str(e)}")
    
def enrich_from_database(
    db: Session,
    request: DDIPredictRequest
) -> dict:
    """
    Query database to enrich the prediction context (RAG approach)
    """
    # Find static severity if exists
    static_severity = find_static_ddi_severity(
        db=db,
        drug1=request.drug1,
        drug2=request.drug2
    )

    # Find similar cases (top 5 most similar for RAG context)
    similar_cases = find_similar_interactions(
        db=db,
        drug1=request.drug1,
        drug2=request.drug2,
        age=request.Age,
        sex=request.Sex,
        comorbidities=request.Comorbidities,
        limit=10
    )
    
    # Get statistics
    stats = get_interaction_statistics(
        db=db,
        drug1=request.drug1,
        drug2=request.drug2
    )
    
    # Extract mechanisms
    mechanisms = list(set([
        case.unified_mechanism_text 
        for case in similar_cases 
        if case.unified_mechanism_text
    ]))
    
    # Format representative cases (include similarity score)
    representative_cases = [
        {
            'patient_uuid': case.patient_uuid,
            'age': case.age,
            'sex': case.sex,
            'severity': case.unified_severity,
            'confidence': case.ddi_confidence,
            'comorbidities': case.comorbidities or [],
            'similarity_score': getattr(case, 'similarity_score', 0)  # Include custom similarity score
        }
        for case in similar_cases[:5]
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