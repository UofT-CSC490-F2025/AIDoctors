import boto3

region = "us-east-1"
bedrock = boto3.client("bedrock", region_name=region)

resp = bedrock.list_foundation_models()
print(f"Found {len(resp['modelSummaries'])} models in {region}:\n")
for m in resp["modelSummaries"]:
    print(
        f"{m['modelId']:45}  "
        f"provider={m.get('providerName')}  "
        f"in={m.get('inputModalities')}  "
        f"out={m.get('outputModalities')}"
    )