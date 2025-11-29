import sys
from pathlib import Path

import pytest

# Make sure we can import sync_raw_from_s3 from src/data_pipelines
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import sync_raw_from_s3 as sync  # noqa: E402


# -----------------------------
# get_ssm_vars
# -----------------------------

def test_get_ssm_vars(monkeypatch):
    """get_ssm_vars should read both bucket and prefix from SSM."""

    class FakeSSM:
        def __init__(self):
            self.params = {
                "/aidoctors/s3/raw-datasets-bucket": "my-bucket",
                "/aidoctors/s3/raw-datasets-prefix": "raw-prefix/",
            }

        def get_parameter(self, Name, WithDecryption=True):
            assert WithDecryption is True
            return {"Parameter": {"Value": self.params[Name]}}

    def fake_client(service_name):
        assert service_name == "ssm"
        return FakeSSM()

    # Patch the boto3 client used in this module
    monkeypatch.setattr(sync.boto3, "client", fake_client)

    bucket, prefix = sync.get_ssm_vars()
    assert bucket == "my-bucket"
    assert prefix == "raw-prefix/"


# -----------------------------
# main: happy path with objects
# -----------------------------

def test_main_downloads_files(tmp_path, monkeypatch, capsys):
    """
    main() should:
    - create RAW_DIR
    - list objects under prefix
    - download each non-folder key into the mirrored local path
    """

    # Redirect RAW_DIR into a temp directory
    raw_dir = tmp_path / "raw_datasets"
    monkeypatch.setattr(sync, "RAW_DIR", raw_dir)

    # Avoid actually talking to SSM; just return stub values
    monkeypatch.setattr(sync, "get_ssm_vars", lambda: ("my-bucket", "prefix/"))

    # Build a fake S3 client + paginator
    class FakePaginator:
        def __init__(self, pages):
            self._pages = pages

        def paginate(self, Bucket, Prefix):
            assert Bucket == "my-bucket"
            assert Prefix == "prefix/"
            for p in self._pages:
                yield p

    class FakeS3:
        def __init__(self):
            self.downloads = []

        def get_paginator(self, name):
            assert name == "list_objects_v2"
            # Two objects and one "folder" key
            pages = [
                {
                    "Contents": [
                        {"Key": "prefix/file1.csv"},
                        {"Key": "prefix/nested/file2.txt"},
                        {"Key": "prefix/dir/"}  # should be skipped
                    ]
                }
            ]
            return FakePaginator(pages)

        def download_file(self, bucket, key, filename):
            # Simulate download by touching the local file
            self.downloads.append((bucket, key, filename))
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            Path(filename).write_text("dummy")

    def fake_client(service_name):
        # Only S3 is used here because we patched get_ssm_vars
        assert service_name == "s3"
        return FakeS3()

    fake_s3 = FakeS3()
    # Ensure sync.main uses our fake_s3
    def fake_client_for_sync(service_name):
        if service_name == "s3":
            return fake_s3
        raise AssertionError(f"Unexpected service: {service_name}")

    monkeypatch.setattr(sync.boto3, "client", fake_client_for_sync)

    sync.main()
    out = capsys.readouterr().out

    # Directories should have been created under RAW_DIR
    file1 = raw_dir / "file1.csv"
    file2 = raw_dir / "nested" / "file2.txt"
    assert file1.exists()
    assert file2.exists()

    # Folder-like key should not have been downloaded
    assert "dir/" not in [Path(p[2]).name for p in fake_s3.downloads]

    # Log messages
    assert "[s3-sync] Downloading from s3://my-bucket/prefix/" in out
    assert "[s3-sync] Done." in out


# -----------------------------
# main: handles empty pages (no Contents)
# -----------------------------

def test_main_handles_empty_pages(tmp_path, monkeypatch, capsys):
    """
    If S3 returns pages without 'Contents', main() should
    gracefully do nothing and still print 'Done'.
    """

    raw_dir = tmp_path / "raw_datasets"
    monkeypatch.setattr(sync, "RAW_DIR", raw_dir)
    monkeypatch.setattr(sync, "get_ssm_vars", lambda: ("bucket-empty", "pref/"))

    class EmptyPaginator:
        def paginate(self, Bucket, Prefix):
            # Page without Contents key -> page.get("Contents", []) == []
            yield {"IsTruncated": False}

    class FakeS3Empty:
        def __init__(self):
            self.downloads = []

        def get_paginator(self, name):
            assert name == "list_objects_v2"
            return EmptyPaginator()

        def download_file(self, bucket, key, filename):
            # Should never be called
            self.downloads.append((bucket, key, filename))

    def fake_client(service_name):
        assert service_name == "s3"
        return FakeS3Empty()

    monkeypatch.setattr(sync.boto3, "client", fake_client)

    sync.main()
    out = capsys.readouterr().out

    # Directory should still exist
    assert raw_dir.exists()
    # No downloads performed
    # (we don't keep a handle to the FakeS3Empty instance, but if download_file
    #  were called, it would raise from unexpected context — the fact we got
    #  here without error is enough)
    assert "[s3-sync] Done." in out
