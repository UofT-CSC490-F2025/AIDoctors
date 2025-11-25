# src/data-pipelines/sync_raw_from_s3.py
from __future__ import annotations
from pathlib import Path

import boto3


RAW_DIR = Path("data/raw_datasets")

def get_ssm_vars():
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name="/aidoctors/s3/raw-datasets-bucket", WithDecryption=True)
    bucket = response["Parameter"]["Value"]
    response = ssm.get_parameter(Name="/aidoctors/s3/raw-datasets-prefix", WithDecryption=True)
    prefix = response["Parameter"]["Value"]
    return bucket, prefix

def main():
    
    # Fetch variables from SSM Parameter Store
    bucket, prefix = get_ssm_vars()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3")
    
    print(f"[s3-sync] Downloading from s3://{bucket}/{prefix} → {RAW_DIR}/")

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue

            rel_name = key[len(prefix):] if key.startswith(prefix) else key
            local_path = RAW_DIR / rel_name

            local_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"[s3-sync]   {key} → {local_path}")
            s3.download_file(bucket, key, str(local_path))

    print("[s3-sync] Done.")


if __name__ == "__main__":
    main()
