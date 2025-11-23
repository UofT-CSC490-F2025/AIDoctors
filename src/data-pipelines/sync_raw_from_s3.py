# src/data-pipelines/sync_raw_from_s3.py
from __future__ import annotations
import os
from pathlib import Path

import boto3


BUCKET = os.getenv("RAW_DATA_S3_BUCKET")           
PREFIX = os.getenv("RAW_DATA_S3_PREFIX", "raw_datasets/")

RAW_DIR = Path("data/raw_datasets")


def main():
    
    if not BUCKET:
        raise RuntimeError(
            "RAW_DATA_S3_BUCKET is not set. Configure it in the task/Job definition."
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3")

    print(f"[s3-sync] Downloading from s3://{BUCKET}/{PREFIX} → {RAW_DIR}/")

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue

            rel_name = key[len(PREFIX):] if key.startswith(PREFIX) else key
            local_path = RAW_DIR / rel_name

            local_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"[s3-sync]   {key} → {local_path}")
            s3.download_file(BUCKET, key, str(local_path))

    print("[s3-sync] Done.")


if __name__ == "__main__":
    main()
