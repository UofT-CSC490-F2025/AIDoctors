import sys
import types
from pathlib import Path
import runpy

import pytest

# Make sure the data_extraction package directory is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def fake_kagglehub(monkeypatch):
    """
    Ensure that importing `utilities` (which imports `kagglehub`) never fails,
    even if kagglehub is not installed in the environment.
    """
    fake_mod = types.SimpleNamespace(
        dataset_download=lambda *args, **kwargs: None
    )
    monkeypatch.setitem(sys.modules, "kagglehub", fake_mod)
    yield
    # no explicit cleanup needed; pytest process is shared


def _run_fetch_datasets(tmp_path, monkeypatch, behavior=None):
    """
    behavior can be:
      None or "all_ok"
      "cres_fail"
      "synthea_fail"
      "mendeley_fail"
      "ddinter_fail"
      "aeolus_fail"
    """
    import utilities  # noqa: E402

    calls = {
        "extract_and_save": [],
        "extract_zip_and_save_members": [],
        "extract_kaggle_dataset_and_save_members": [],
    }

    failure = behavior or "all_ok"

    def fake_extract_and_save(url, out_dir, filename=None, overwrite=False, timeout=30):
        calls["extract_and_save"].append(
            {
                "url": url,
                "out_dir": out_dir,
                "filename": filename,
                "overwrite": overwrite,
                "timeout": timeout,
            }
        )
        # Fail on any CRESCENDDI file
        if failure == "cres_fail" and filename and "CRESCENDDI" in filename:
            raise RuntimeError("boom cres")
        # Fail on Mendeley only
        if failure == "mendeley_fail" and filename and "Mendeley" in filename:
            raise RuntimeError("boom mendeley")

        return str(Path(out_dir) / (filename or "file.bin"))

    def fake_extract_zip_and_save_members(
        url, out_dir, members=None, pattern=None, overwrite=False, timeout=30
    ):
        calls["extract_zip_and_save_members"].append(
            {
                "url": url,
                "out_dir": out_dir,
                "members": members,
                "pattern": pattern,
                "overwrite": overwrite,
                "timeout": timeout,
            }
        )
        if failure == "synthea_fail":
            raise RuntimeError("boom synthea")

        return [str(Path(out_dir) / (m or "dummy.txt")) for m in (members or ["dummy.txt"])]

    def fake_extract_kaggle_dataset_and_save_members(dataset, out_dir, overwrite=False):
        calls["extract_kaggle_dataset_and_save_members"].append(
            {"dataset": dataset, "out_dir": out_dir, "overwrite": overwrite}
        )
        if failure == "ddinter_fail" and dataset.startswith(
            "montassarba/drug-drug-interactions-database-ddinter"
        ):
            raise RuntimeError("boom ddinter")
        if failure == "aeolus_fail" and dataset.startswith(
            "fda/adverse-pharmaceuticals-events"
        ):
            raise RuntimeError("boom aeolus")

        return None

    monkeypatch.setattr(utilities, "extract_and_save", fake_extract_and_save)
    monkeypatch.setattr(
        utilities,
        "extract_zip_and_save_members",
        fake_extract_zip_and_save_members,
    )
    monkeypatch.setattr(
        utilities,
        "extract_kaggle_dataset_and_save_members",
        fake_extract_kaggle_dataset_and_save_members,
    )

    out_dir = tmp_path / "raw_datasets"
    monkeypatch.setattr(
        sys,
        "argv",
        ["fetch_datasets.py", "--output-dir", str(out_dir)],
    )

    runpy.run_module("fetch_datasets", run_name="__main__")

    return calls, out_dir


def test_fetch_datasets_all_success(tmp_path, monkeypatch, capsys):
    calls, out_dir = _run_fetch_datasets(tmp_path, monkeypatch, behavior="all_ok")

    # Directory should exist
    assert out_dir.exists()
    assert out_dir.is_dir()

    # Check that our helpers were invoked with expected datasets
    # CRESCENDDI (3 calls) + Mendeley (1 call) = 4 extract_and_save
    assert len(calls["extract_and_save"]) == 4
    cres_urls = [c["filename"] for c in calls["extract_and_save"][:3]]
    assert "CRESCENDDI - Positive Controls.xlsx" in cres_urls
    assert "CRESCENDDI - Negative Controls.xlsx" in cres_urls
    assert "CRESCENDDI - Drug mappings.xlsx" in cres_urls

    # Synthea zip extract
    assert len(calls["extract_zip_and_save_members"]) == 1
    synthea_call = calls["extract_zip_and_save_members"][0]
    assert "synthea_sample_data_csv_latest.zip" in synthea_call["url"]
    assert synthea_call["members"] == ["conditions.csv", "medications.csv", "patients.csv"]

    # Kaggle datasets: DDInter + AEOLUS
    kaggle_datasets = [c["dataset"] for c in calls["extract_kaggle_dataset_and_save_members"]]
    assert "montassarba/drug-drug-interactions-database-ddinter" in kaggle_datasets
    assert "fda/adverse-pharmaceuticals-events" in kaggle_datasets

    # Check the printed summary
    captured = capsys.readouterr().out
    assert "Successfully extracted 5 datasets." in captured
    assert "Failed to extract" not in captured or "Failed to extract 0 datasets." in captured


def test_fetch_datasets_with_failure(tmp_path, monkeypatch, capsys):
    # This time, we simulate a failure in the Mendeley step
    calls, out_dir = _run_fetch_datasets(tmp_path, monkeypatch, behavior="mendeley_fail")

    # Still should create the directory and run other steps
    assert out_dir.exists()

    # CRESCENDDI still should have run successfully: first 3 calls ok
    assert len(calls["extract_and_save"]) >= 3

    # Kaggle datasets and Synthea should still be processed
    assert len(calls["extract_zip_and_save_members"]) == 1
    assert len(calls["extract_kaggle_dataset_and_save_members"]) == 2

    captured = capsys.readouterr().out

    # We should see a specific failure message for Mendeley
    assert "Failed to extract Mendeley files" in captured

    # And the summary should reflect 1 failure (5 groups total)
    assert "Successfully extracted 4 datasets." in captured
    assert "Failed to extract 1 datasets." in captured


@pytest.mark.parametrize(
    "behavior, expected_fragment",
    [
        ("cres_fail", "Failed to extract CRESCENDDI files"),
        ("synthea_fail", "Failed to extract Synthea files"),
        ("mendeley_fail", "Failed to extract Mendeley files"),
        ("ddinter_fail", "Failed to extract DDInter files"),
        ("aeolus_fail", "Failed to extract AEOLUS files"),
    ],
)
def test_fetch_datasets_each_failure_branch(tmp_path, monkeypatch, capsys, behavior, expected_fragment):
    calls, out_dir = _run_fetch_datasets(tmp_path, monkeypatch, behavior=behavior)

    assert out_dir.exists()

    out = capsys.readouterr().out
    # Specific dataset failure message
    assert expected_fragment in out
    # Summary reflects 4 successes + 1 failure
    assert "Successfully extracted 4 datasets." in out
    assert "Failed to extract 1 datasets." in out


import os
import types
from pathlib import Path

def test_extract_kaggle_restores_existing_cache_env(monkeypatch, tmp_path):
    import utilities

    # Fake kagglehub.dataset_download so it writes a dummy file into the temp cache
    def fake_dataset_download(handle, force_download=False):
        cache_root = Path(os.environ["KAGGLEHUB_CACHE"])
        dest = cache_root / "datasets" / "owner" / "dataset" / "versions" / "1"
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "data.csv").write_text("hello")

    # IMPORTANT: patch utilities.kagglehub (not just sys.modules)
    fake_kaggle = types.SimpleNamespace(dataset_download=fake_dataset_download)
    monkeypatch.setattr(utilities, "kagglehub", fake_kaggle)

    # Make upload_local_file a no-op
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: None)

    # Pre-set KAGGLEHUB_CACHE so prev_cache is NOT None
    original_cache = str(tmp_path / "existing_cache")
    monkeypatch.setenv("KAGGLEHUB_CACHE", original_cache)

    out_dir = tmp_path / "out"
    moved = utilities.extract_kaggle_dataset_and_save_members(
        dataset="owner/dataset",
        out_dir=str(out_dir),
        overwrite=True,
    )

    # Env var should be restored to original_cache
    assert os.environ.get("KAGGLEHUB_CACHE") == original_cache

    # Our dummy file should have been moved into out_dir
    assert len(moved) == 1
    assert Path(moved[0]).parent == out_dir
    assert Path(moved[0]).name == "data.csv"
    assert Path(moved[0]).read_text() == "hello"