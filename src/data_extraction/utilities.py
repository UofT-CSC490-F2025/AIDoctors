"""
Helpers to download data files from the internet and save them.
"""

from __future__ import annotations

import io
import os
from typing import Dict

import requests
import pandas as pd
from urllib.parse import urlparse, unquote
import zipfile
import fnmatch
import kagglehub
import tempfile
import shutil


### General file downloads


def download_file(url: str, timeout: int = 30) -> bytes:
    """Download the file at `url` and return its bytes.

    Raises requests.exceptions.RequestException on network errors.
    """
    resp = requests.get(url, stream=True, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def extract_and_save(
    url: str,
    out_dir: str,
    filename: str | None = None,
    overwrite: bool = False,
    timeout: int = 30,
) -> str:
    """Download a file from `url` and save it to `out_dir`.

    If `filename` is provided, the downloaded file will be saved under that
    name. Otherwise the name is derived from the URL path. Returns the full
    path to the written file.

    Parameters
    - url: remote file URL
    - out_dir: directory to save into (created if missing)
    - filename: optional filename to use instead of the URL basename
    - overwrite: if False and target exists, raises FileExistsError
    - timeout: requests timeout in seconds
    """
    parsed = urlparse(url)
    # url path basename (unquote in case of percent-encoding)
    url_basename = unquote(parsed.path.split("/")[-1] or "")

    if filename:
        safe_name = os.path.basename(filename)
    else:
        safe_name = url_basename or "downloaded_file"

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, safe_name)

    if os.path.exists(out_path) and not overwrite:
        raise FileExistsError(f"Target file already exists: {out_path}")

    data = download_file(url, timeout=timeout)
    with open(out_path, "wb") as fh:
        fh.write(data)

    return out_path


### Excel file downloads as CSVs


def excel_bytes_to_dfs(excel_bytes: bytes) -> Dict[str, pd.DataFrame]:
    """Read an Excel file in memory and return a dict of sheet_name -> DataFrame.

    Uses pandas.read_excel with sheet_name=None to read all sheets.
    """
    bio = io.BytesIO(excel_bytes)
    # Let pandas infer engine (openpyxl for .xlsx)
    sheets = pd.read_excel(bio, sheet_name=None)
    return sheets


def save_sheets_as_csv(sheets: Dict[str, pd.DataFrame], out_dir: str, base_name: str = "data") -> None:
    """Save each DataFrame in `sheets` as a CSV file in `out_dir`.
    """
    os.makedirs(out_dir, exist_ok=True)
    # If only one sheet is present, name the file as <base_name>.csv
    single_sheet = len(sheets) == 1
    for sheet_name, df in sheets.items():
        # sanitize sheet name for filename
        safe_name = "_".join(sheet_name.strip().split()) or "sheet"
        if single_sheet:
            filename = f"{base_name}.csv"
        else:
            filename = f"{base_name}--{safe_name}.csv"
        out_path = os.path.join(out_dir, filename)
        df.to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(df)} rows)")


def extract_xlsx_and_save_csv(
    url: str,
    out_dir: str,
    base_name: str,
    sheet: str | int | None = None,  # Optional sheet name or index or None for all
) -> list[str]:
    """Programmatic function to download an Excel file from a URL and save
    the sheets as a CSV.

    Returns a list of file paths written.
    """
    excel_bytes = download_file(url)
    sheets = excel_bytes_to_dfs(excel_bytes)

    if sheet is not None:
        sheet_arg = str(sheet)
        selected: dict[str, pd.DataFrame] = {}
        try:
            idx = int(sheet_arg)
        except ValueError:
            if sheet_arg in sheets:
                selected[sheet_arg] = sheets[sheet_arg]
            else:
                raise KeyError(f"Sheet '{sheet_arg}' not found. Available: {list(sheets.keys())}")
        else:
            keys = list(sheets.keys())
            if idx < 1 or idx > len(keys):
                raise IndexError(f"Sheet index {idx} out of range (1..{len(keys)})")
            key = keys[idx - 1]
            selected[key] = sheets[key]
        sheets = selected

    os.makedirs(out_dir, exist_ok=True)
    written_files: list[str] = []
    single_sheet = len(sheets) == 1
    for sheet_name, df in sheets.items():
        safe_name = "_".join(sheet_name.strip().split()) or "sheet"
        if single_sheet:
            filename = f"{base_name}.csv"
        else:
            filename = f"{base_name}--{safe_name}.csv"
        out_path = os.path.join(out_dir, filename)
        df.to_csv(out_path, index=False)
        written_files.append(out_path)

    return written_files


### ZIP downloads and extraction


def extract_zip_and_save_members(
    url: str,
    out_dir: str,
    members: list[str] | None = None,
    pattern: str | None = None,
    overwrite: bool = False,
    timeout: int = 30,
) -> list[str]:
    """Download a ZIP from `url` and extract selected members into `out_dir`.

    Parameters
    - url: remote ZIP URL
    - out_dir: target directory to extract files into (created if needed)
    - members: optional explicit list of member names to extract (exact match)
    - pattern: optional glob pattern to select members (uses fnmatch). Ignored if `members` is provided.
    - overwrite: if False and a target file exists, raises FileExistsError
    - timeout: requests timeout seconds

    Returns list of extracted file paths (absolute paths).
    """
    data = download_file(url, timeout=timeout)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        all_names = zf.namelist()

        if members is not None:
            # exact-match selection
            selected = [name for name in all_names if name in members]
            missing = [m for m in members if m not in all_names]
            if missing:
                raise KeyError(f"Members not found in ZIP: {missing}")
        elif pattern is not None:
            selected = [name for name in all_names if fnmatch.fnmatch(name, pattern)]
        else:
            selected = all_names

        os.makedirs(out_dir, exist_ok=True)
        extracted_paths: list[str] = []
        base_abs = os.path.abspath(out_dir)

        for name in selected:
            # skip directory entries
            if name.endswith("/"):
                continue

            # compute target path and prevent path traversal
            dest_path = os.path.join(out_dir, name)
            dest_path_abs = os.path.abspath(dest_path)
            if not dest_path_abs.startswith(base_abs + os.sep) and dest_path_abs != base_abs:
                raise ValueError(f"Attempted Path Traversal in ZIP member: {name}")

            dest_dir = os.path.dirname(dest_path_abs)
            os.makedirs(dest_dir, exist_ok=True)

            if os.path.exists(dest_path_abs) and not overwrite:
                raise FileExistsError(f"Target file already exists: {dest_path_abs}")

            with zf.open(name) as src, open(dest_path_abs, "wb") as out_fh:
                out_fh.write(src.read())

            extracted_paths.append(dest_path_abs)

        return extracted_paths
    

### Kaggle downloads and extraction


def extract_kaggle_dataset_and_save_members(
    dataset: str,
    out_dir: str,
    overwrite: bool = False,
) -> None:
    """Download a Kaggle dataset via kagglehub and place its files directly into `out_dir`.

    kagglehub typically stores dataset versions under a cache directory with
    nested paths like `datasets/.../versions/1/`. To place files directly into
    `out_dir`, this function sets a temporary `KAGGLEHUB_CACHE`, runs the
    download, then moves the downloaded files from the temporary cache into
    `out_dir` (flat — top-level files placed directly under `out_dir`).

    Parameters
    - dataset: kaggle dataset handle (e.g., 'zynicide/wine-reviews')
    - out_dir: destination directory where dataset files will be moved
    - overwrite: if False and a target file exists in out_dir, raises FileExistsError
    """
    os.makedirs(out_dir, exist_ok=True)

    # Use a temporary cache dir so we can control where kagglehub writes
    with tempfile.TemporaryDirectory() as tmp_cache:
        prev_cache = os.environ.get("KAGGLEHUB_CACHE")
        try:
            os.environ["KAGGLEHUB_CACHE"] = tmp_cache
            # download into the temporary cache
            kagglehub.dataset_download(handle=dataset, force_download=overwrite)

            # Move all regular files from the cache tree into out_dir (flat)
            moved: list[str] = []
            for root, _, files in os.walk(tmp_cache):
                for fname in files:
                    # skip kagglehub completion marker files like '1.complete'
                    if fname.endswith(".complete"):
                        continue

                    src_path = os.path.join(root, fname)
                    dest_path = os.path.join(out_dir, fname)
                    if os.path.exists(dest_path) and not overwrite:
                        raise FileExistsError(f"Target file already exists: {dest_path}")
                    # Ensure destination dir exists (out_dir already created)
                    shutil.move(src_path, dest_path)
                    moved.append(dest_path)

            return moved
        finally:
            # restore previous env var if any
            if prev_cache is None:
                os.environ.pop("KAGGLEHUB_CACHE", None)
            else:
                os.environ["KAGGLEHUB_CACHE"] = prev_cache

