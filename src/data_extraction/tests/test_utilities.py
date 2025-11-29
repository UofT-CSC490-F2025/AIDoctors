import sys
import os
from pathlib import Path
import io
import zipfile

import pytest
import pandas as pd
import requests

# Make sure src/data_extraction is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import utilities  # noqa: E402


# -------------------------------------------------------------------
# download_file
# -------------------------------------------------------------------

def test_download_file_success(monkeypatch):
    class FakeResp:
        def __init__(self):
            self.content = b"hello"

        def raise_for_status(self):
            pass

    def fake_get(url, stream=True, timeout=30):
        assert url == "https://example.com/file.txt"
        assert stream is True
        assert timeout == 10
        return FakeResp()

    monkeypatch.setattr("utilities.requests.get", fake_get)

    data = utilities.download_file("https://example.com/file.txt", timeout=10)
    assert data == b"hello"


def test_download_file_http_error(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            raise requests.HTTPError("boom")

    def fake_get(url, stream=True, timeout=30):
        return FakeResp()

    monkeypatch.setattr("utilities.requests.get", fake_get)

    with pytest.raises(requests.HTTPError):
        utilities.download_file("https://example.com/file.txt")


# -------------------------------------------------------------------
# extract_and_save
# -------------------------------------------------------------------

def test_extract_and_save_default_name(tmp_path, monkeypatch):
    called = {}

    def fake_download(url, timeout=30):
        called["url"] = url
        return b"file-bytes"

    uploaded = []

    def fake_upload(path):
        uploaded.append(path)

    monkeypatch.setattr(utilities, "download_file", fake_download)
    monkeypatch.setattr(utilities, "upload_local_file", fake_upload)

    out_dir = tmp_path / "out"
    url = "https://example.com/subdir/thefile.dat"
    out_path = utilities.extract_and_save(str(url), str(out_dir))

    assert out_path.endswith("thefile.dat")
    assert (out_dir / "thefile.dat").read_bytes() == b"file-bytes"
    assert called["url"] == url
    assert uploaded == [str(out_dir / "thefile.dat")]


def test_extract_and_save_custom_name_and_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(utilities, "download_file", lambda url, timeout=30: b"new")

    # no-op upload
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: None)

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    existing = out_dir / "custom.csv"
    existing.write_bytes(b"old")

    # without overwrite -> error
    with pytest.raises(FileExistsError):
        utilities.extract_and_save(
            "https://example.com/x.csv", str(out_dir), filename="custom.csv"
        )

    # with overwrite -> replaces
    p = utilities.extract_and_save(
        "https://example.com/x.csv",
        str(out_dir),
        filename="custom.csv",
        overwrite=True,
    )
    assert p == str(existing)
    assert existing.read_bytes() == b"new"


# -------------------------------------------------------------------
# excel_bytes_to_dfs / save_sheets_as_csv / extract_xlsx_and_save_csv
# -------------------------------------------------------------------

def _make_excel_bytes():
    """Helper: create an in-memory .xlsx with two sheets."""
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        pd.DataFrame({"a": [1, 2]}).to_excel(writer, sheet_name="SheetA", index=False)
        pd.DataFrame({"b": [3]}).to_excel(writer, sheet_name="Sheet B", index=False)
    return bio.getvalue()


def test_excel_bytes_to_dfs():
    excel_bytes = _make_excel_bytes()
    sheets = utilities.excel_bytes_to_dfs(excel_bytes)

    assert set(sheets.keys()) == {"SheetA", "Sheet B"}
    assert sheets["SheetA"].shape == (2, 1)
    assert sheets["Sheet B"].shape == (1, 1)


def test_save_sheets_as_csv_single_and_multi(tmp_path, capsys):
    # single sheet
    sheets_single = {"Only": pd.DataFrame({"x": [1]})}
    utilities.save_sheets_as_csv(sheets_single, str(tmp_path), base_name="single")
    assert (tmp_path / "single.csv").exists()

    # multiple sheets
    sheets_multi = {
        "First": pd.DataFrame({"x": [1]}),
        "Second sheet": pd.DataFrame({"y": [2]}),
    }
    utilities.save_sheets_as_csv(sheets_multi, str(tmp_path), base_name="multi")
    assert (tmp_path / "multi--First.csv").exists()
    assert (tmp_path / "multi--Second_sheet.csv").exists()

    # just exercise the print so it doesn't blow up
    captured = capsys.readouterr()
    assert "Wrote" in captured.out


def test_extract_xlsx_and_save_csv_all_sheets(tmp_path, monkeypatch):
    excel_bytes = _make_excel_bytes()
    monkeypatch.setattr(utilities, "download_file", lambda url: excel_bytes)

    out_dir = tmp_path / "csvs"
    written = utilities.extract_xlsx_and_save_csv(
        "https://example.com/file.xlsx", str(out_dir), base_name="base"
    )

    # both sheets -> two files, with --Sheet suffixes
    assert len(written) == 2
    names = {Path(p).name for p in written}
    assert names == {"base--SheetA.csv", "base--Sheet_B.csv"}


def test_extract_xlsx_and_save_csv_by_index(tmp_path, monkeypatch):
    excel_bytes = _make_excel_bytes()
    monkeypatch.setattr(utilities, "download_file", lambda url: excel_bytes)

    written = utilities.extract_xlsx_and_save_csv(
        "https://example.com/file.xlsx",
        str(tmp_path),
        base_name="base",
        sheet=1,  # first sheet
    )

    # single selected sheet => base_name.csv
    assert written == [str(tmp_path / "base.csv")]
    df = pd.read_csv(written[0])
    assert list(df.columns) == ["a"]


def test_extract_xlsx_and_save_csv_by_name(tmp_path, monkeypatch):
    excel_bytes = _make_excel_bytes()
    monkeypatch.setattr(utilities, "download_file", lambda url: excel_bytes)

    written = utilities.extract_xlsx_and_save_csv(
        "https://example.com/file.xlsx",
        str(tmp_path),
        base_name="base",
        sheet="Sheet B",
    )
    assert written == [str(tmp_path / "base.csv")]
    df = pd.read_csv(written[0])
    assert list(df.columns) == ["b"]


def test_extract_xlsx_and_save_csv_bad_sheet_name(tmp_path, monkeypatch):
    excel_bytes = _make_excel_bytes()
    monkeypatch.setattr(utilities, "download_file", lambda url: excel_bytes)

    with pytest.raises(KeyError):
        utilities.extract_xlsx_and_save_csv(
            "https://example.com/file.xlsx",
            str(tmp_path),
            base_name="base",
            sheet="NOPE",
        )


def test_extract_xlsx_and_save_csv_bad_sheet_index(tmp_path, monkeypatch):
    excel_bytes = _make_excel_bytes()
    monkeypatch.setattr(utilities, "download_file", lambda url: excel_bytes)

    with pytest.raises(IndexError):
        utilities.extract_xlsx_and_save_csv(
            "https://example.com/file.xlsx",
            str(tmp_path),
            base_name="base",
            sheet=99,
        )


# -------------------------------------------------------------------
# extract_zip_and_save_members
# -------------------------------------------------------------------

def _make_zip_bytes():
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, mode="w") as z:
        z.writestr("a.txt", "A")
        z.writestr("subdir/b.txt", "B")
        z.writestr("subdir/", "")  # directory entry
    return bio.getvalue()


def test_extract_zip_all_members(tmp_path, monkeypatch):
    monkeypatch.setattr(utilities, "download_file", lambda url, timeout=30: _make_zip_bytes())

    uploaded = []
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: uploaded.append(p))

    out_dir = tmp_path / "out"
    paths = utilities.extract_zip_and_save_members(
        "https://example.com/data.zip", str(out_dir)
    )

    names = {Path(p).relative_to(out_dir).as_posix() for p in paths}
    assert names == {"a.txt", "subdir/b.txt"}
    # upload called for each extracted path
    assert set(uploaded) == set(map(str, paths))


def test_extract_zip_members_list_and_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(utilities, "download_file", lambda url, timeout=30: _make_zip_bytes())
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: None)

    out_dir = tmp_path / "out"

    # valid subset
    paths = utilities.extract_zip_and_save_members(
        "https://example.com/data.zip", str(out_dir), members=["a.txt"]
    )
    assert [Path(p).name for p in paths] == ["a.txt"]

    # missing member raises KeyError
    with pytest.raises(KeyError):
        utilities.extract_zip_and_save_members(
            "https://example.com/data.zip", str(out_dir), members=["missing.txt"]
        )


def test_extract_zip_pattern_and_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(utilities, "download_file", lambda url, timeout=30: _make_zip_bytes())
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: None)

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    # pattern that picks only subdir/*
    paths = utilities.extract_zip_and_save_members(
        "https://example.com/data.zip", str(out_dir), pattern="subdir/*"
    )
    names = [Path(p).relative_to(out_dir).as_posix() for p in paths]
    assert names == ["subdir/b.txt"]

    # overwrite=False when file exists -> FileExistsError
    existing = out_dir / "a.txt"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("OLD")

    with pytest.raises(FileExistsError):
        utilities.extract_zip_and_save_members(
            "https://example.com/data.zip", str(out_dir), members=["a.txt"], overwrite=False
        )

    # overwrite=True should succeed
    paths2 = utilities.extract_zip_and_save_members(
        "https://example.com/data.zip", str(out_dir), members=["a.txt"], overwrite=True
    )
    assert (out_dir / "a.txt").read_text() == "A"
    assert len(paths2) == 1


def _make_zip_with_traversal():
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, mode="w") as z:
        z.writestr("../../evil.txt", "X")
    return bio.getvalue()


def test_extract_zip_path_traversal_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(
        utilities, "download_file",
        lambda url, timeout=30: _make_zip_with_traversal()
    )
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: None)

    with pytest.raises(ValueError):
        utilities.extract_zip_and_save_members(
            "https://example.com/bad.zip", str(tmp_path)
        )


# -------------------------------------------------------------------
# extract_kaggle_dataset_and_save_members
# -------------------------------------------------------------------

def test_extract_kaggle_dataset_moves_files_and_restores_env(tmp_path, monkeypatch):
    # fake kagglehub.dataset_download to write files into KAGGLEHUB_CACHE
    def fake_dataset_download(handle, force_download=False):
        cache = os.environ["KAGGLEHUB_CACHE"]
        root = Path(cache) / "datasets" / "foo" / "versions" / "1"
        root.mkdir(parents=True, exist_ok=True)
        (root / "data.csv").write_text("x\n1\n")
        (root / "1.complete").write_text("done")

    monkeypatch.setattr(utilities.kagglehub, "dataset_download", fake_dataset_download)

    uploaded = []
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: uploaded.append(p))

    # preserve any pre-existing env var
    prev_cache = os.environ.get("KAGGLEHUB_CACHE")

    out_dir = tmp_path / "kaggle"
    moved = utilities.extract_kaggle_dataset_and_save_members(
        "foo/bar", str(out_dir), overwrite=False
    )

    # one data file moved into out_dir
    assert moved == [str(out_dir / "data.csv")]
    assert (out_dir / "data.csv").exists()
    assert uploaded == [str(out_dir / "data.csv")]

    # env var restored
    assert os.environ.get("KAGGLEHUB_CACHE") == prev_cache


def test_extract_kaggle_dataset_overwrite_flag(tmp_path, monkeypatch):
    def fake_dataset_download(handle, force_download=False):
        cache = os.environ["KAGGLEHUB_CACHE"]
        root = Path(cache) / "datasets" / "foo" / "versions" / "1"
        root.mkdir(parents=True, exist_ok=True)
        (root / "data.csv").write_text("x\n1\n")

    monkeypatch.setattr(utilities.kagglehub, "dataset_download", fake_dataset_download)
    monkeypatch.setattr(utilities, "upload_local_file", lambda p: None)

    out_dir = tmp_path / "kaggle"
    out_dir.mkdir()
    dest = out_dir / "data.csv"
    dest.write_text("old")

    # overwrite=False -> error
    with pytest.raises(FileExistsError):
        utilities.extract_kaggle_dataset_and_save_members(
            "foo/bar", str(out_dir), overwrite=False
        )

    # overwrite=True -> OK and file replaced
    moved = utilities.extract_kaggle_dataset_and_save_members(
        "foo/bar", str(out_dir), overwrite=True
    )
    assert moved == [str(dest)]
    assert dest.read_text() == "x\n1\n"
