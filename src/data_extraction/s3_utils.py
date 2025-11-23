from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

import boto3


S3_BUCKET = os.getenv("RAW_DATA_S3_BUCKET")          
S3_PREFIX = os.getenv("RAW_DATA_S3_PREFIX", "raw_datasets/")  

_s3_client: Optional[boto3.client] = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client


def s3_enabled() -> bool:
    return S3_BUCKET is not None


def upload_local_file(local_path: str | Path, key_prefix: str | None = None) -> str:
    if not s3_enabled():
        return ""

    local_path = Path(local_path)
    prefix = key_prefix if key_prefix is not None else S3_PREFIX
    prefix = prefix.rstrip("/") + "/"

    key = prefix + local_path.name

    s3 = get_s3_client()
    s3.upload_file(str(local_path), S3_BUCKET, key)

    print(f"[s3] Uploaded {local_path} → s3://{S3_BUCKET}/{key}")
    return key
