import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
MODEL_ID = "openai.gpt-oss-120b-1:0"  # <-- use one you saw in your list

rt = boto3.client("bedrock-runtime", region_name=REGION)

def get_text_from_converse(resp):
    blocks = resp.get("output", {}).get("message", {}).get("content", [])
    texts = []
    for b in blocks:
        if "text" in b:
            texts.append(b["text"])
    return "\n".join(texts).strip()

messages = [
    {"role": "user", "content": [{"text": "Explain overfitting in one sentence."}]}
]

try:
    resp = rt.converse(
        modelId=MODEL_ID,
        messages=messages,
        # (optional) system messages are fine too:
        # system=[{"text": "You are a helpful assistant."}],
        inferenceConfig={"maxTokens": 128, "temperature": 0.7, "topP": 0.9},
    )
    text = get_text_from_converse(resp)
    if not text:
        print("No 'text' blocks found. Full response follows:\n", resp)
    else:
        print(text)

except ClientError as e:
    code = e.response["Error"]["Code"]
    msg  = e.response["Error"]["Message"]
    print(f"AWS ClientError [{code}]: {msg}")
    if code == "ValidationException":
        print("→ Double-check the modelId and region match list_foundation_models().")
    if code == "AccessDeniedException":
        print("→ Enable this model in Bedrock console > Model access for this account/region.")
except Exception as e:
    print("Unexpected error:", e)