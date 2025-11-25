from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

import boto3

_s3_client: Optional[boto3.client] = None
S3_BUCKET: Optional[str] = None
S3_PREFIX: Optional[str] = None


def get_ssm_vars():
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name="/aidoctors/s3/raw-datasets-bucket", WithDecryption=True)
    bucket = response["Parameter"]["Value"]
    response = ssm.get_parameter(Name="/aidoctors/s3/raw-datasets-prefix", WithDecryption=True)
    prefix = response["Parameter"]["Value"]
    return bucket, prefix

def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client

def upload_local_file(local_path: str | Path) -> str:

    global S3_BUCKET
    global S3_PREFIX

    print("Uploading to S3...")

    if S3_BUCKET is None or S3_PREFIX is None:
       S3_BUCKET, S3_PREFIX = get_ssm_vars()
    
    local_path = Path(local_path)
    prefix = S3_PREFIX.rstrip("/") + "/"

    key = prefix + local_path.name

    s3 = get_s3_client()
    s3.upload_file(str(local_path), S3_BUCKET, key)

    print(f"[s3] Uploaded {local_path} → s3://{S3_BUCKET}/{key}")
    return key
