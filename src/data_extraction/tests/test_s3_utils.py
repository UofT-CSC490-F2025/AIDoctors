import sys
import types
from pathlib import Path
import pytest

# Make sure s3_utils.py is importable
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import s3_utils  # noqa: E402


# ---------------------------------------------------------
# Helpers: Reset module-level globals before each test
# ---------------------------------------------------------
@pytest.fixture(autouse=True)
def reset_globals():
    s3_utils._s3_client = None
    s3_utils.S3_BUCKET = None
    s3_utils.S3_PREFIX = None
    yield
    s3_utils._s3_client = None
    s3_utils.S3_BUCKET = None
    s3_utils.S3_PREFIX = None


# ---------------------------------------------------------
# Test get_ssm_vars(): Ensure SSM is called correctly
# ---------------------------------------------------------
def test_get_ssm_vars(monkeypatch):

    # mock boto3.client("ssm")
    class FakeSSM:
        def get_parameter(self, Name, WithDecryption):
            if Name.endswith("bucket"):
                return {"Parameter": {"Value": "my-bucket"}}
            elif Name.endswith("prefix"):
                return {"Parameter": {"Value": "my/prefix"}}
            raise ValueError("unexpected parameter")

    monkeypatch.setattr("boto3.client", lambda service: FakeSSM())

    bucket, prefix = s3_utils.get_ssm_vars()
    assert bucket == "my-bucket"
    assert prefix == "my/prefix"


# ---------------------------------------------------------
# Test get_s3_client(): ensure global _s3_client is memoized
# ---------------------------------------------------------
def test_get_s3_client_memoization(monkeypatch):

    created = []

    class FakeS3:
        pass

    def fake_client(service):
        assert service == "s3"
        obj = FakeS3()
        created.append(obj)
        return obj

    monkeypatch.setattr("boto3.client", fake_client)

    c1 = s3_utils.get_s3_client()
    c2 = s3_utils.get_s3_client()

    # Only created once
    assert c1 is c2
    assert len(created) == 1


# ---------------------------------------------------------
# Test upload_local_file(): bucket+prefix fetched from SSM and file uploaded.
# ---------------------------------------------------------
def test_upload_local_file(monkeypatch, tmp_path):

    # 1) Mock get_ssm_vars() so upload_local_file() has bucket+prefix
    monkeypatch.setattr(s3_utils, "get_ssm_vars", lambda: ("test-bucket", "some/prefix"))

    # 2) Mock S3 client upload_file()
    uploaded = {}

    class FakeS3Client:
        def upload_file(self, local, bucket, key):
            uploaded["local"] = local
            uploaded["bucket"] = bucket
            uploaded["key"] = key

    # monkeypatch get_s3_client() to return fake S3 client
    monkeypatch.setattr(s3_utils, "get_s3_client", lambda: FakeS3Client())

    # 3) Create a temporary file to upload
    f = tmp_path / "hello.txt"
    f.write_text("abc123")

    # 4) Call function
    out_key = s3_utils.upload_local_file(f)

    # Assert SSM info used correctly
    assert s3_utils.S3_BUCKET == "test-bucket"
    assert s3_utils.S3_PREFIX == "some/prefix"

    # Assert returned key is correct
    assert out_key == "some/prefix/hello.txt"

    # Assert upload_file was called correctly
    assert uploaded["local"] == str(f)
    assert uploaded["bucket"] == "test-bucket"
    assert uploaded["key"] == "some/prefix/hello.txt"
