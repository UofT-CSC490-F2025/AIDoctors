import os
import re
import json
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
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
    