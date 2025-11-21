"""
Script to download and extract datasets from:
  - DDInter
  - CRESCENDDI
  - Synthea
  - Mendeley
  - AEOLUS
"""

import argparse
import os
from utilities import (
    extract_and_save,
    extract_kaggle_dataset_and_save_members,
    extract_zip_and_save_members,
)


if __name__ == "__main__":
    # Get output directory from command-line arguments
    parser = argparse.ArgumentParser(
        description="Download and extract raw datasets to a destination folder"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="data/raw_datasets",
        help="Path to save the raw datasets (default: data/raw_datasets)",
    )
    args = parser.parse_args()
    EXTRACTION_DESTINATION = os.path.expanduser(args.output_dir)
    os.makedirs(EXTRACTION_DESTINATION, exist_ok=True)  # Create output dir if needed

    divider_length = 40
    print("=" * divider_length)
    print("Starting dataset extraction...")
    print("=" * divider_length + "\n")

    success_count = 0
    failure_count = 0

    # Extract CRESCENDDI files (can also use extract_xlsx_and_save_csv to save as CSVs)
    print("Extracting CRESCENDDI files...")
    try:
        extract_and_save(
            url="https://github.com/elpidakon/CRESCENDDI/raw/refs/heads/main/data_records/Data%20Record%201%20-%20Positive%20Controls.xlsx",
            out_dir=EXTRACTION_DESTINATION,
            filename="CRESCENDDI - Positive Controls.xlsx",
            overwrite=True,
        )
        extract_and_save(
            url="https://github.com/elpidakon/CRESCENDDI/raw/refs/heads/main/data_records/Data%20Record%202%20-%20Negative%20Controls.xlsx",
            out_dir=EXTRACTION_DESTINATION,
            filename="CRESCENDDI - Negative Controls.xlsx",
            overwrite=True,
        )
        extract_and_save(
            url="https://github.com/elpidakon/CRESCENDDI/raw/refs/heads/main/data_records/Data%20Record%204%20-%20Drug%20mappings.xlsx",
            out_dir=EXTRACTION_DESTINATION,
            filename="CRESCENDDI - Drug mappings.xlsx",
            overwrite=True,
        )

        success_count += 1
        print("Finished extracting CRESCENDDI files.\n")
    except Exception as e:
        failure_count += 1
        print(f"Failed to extract CRESCENDDI files: {e}\n")

    # Extract Synthea dataset
    print("Extracting Synthea files...")
    try:
        extract_zip_and_save_members(
            url="https://synthetichealth.github.io/synthea-sample-data/downloads/latest/synthea_sample_data_csv_latest.zip",
            out_dir=EXTRACTION_DESTINATION,
            members=["conditions.csv", "medications.csv", "patients.csv"],
            overwrite=True,
        )

        success_count += 1
        print("Finished extracting Synthea files.\n")
    except Exception as e:
        failure_count += 1
        print(f"Failed to extract Synthea files: {e}\n")

    # Extract Mendeley dataset
    print("Extracting Mendeley files...")
    try:
        extract_and_save(
            url="https://data.mendeley.com/public-files/datasets/md5czfsfnd/files/4530a4be-8cff-4cfb-a309-9343f92f6832/file_downloaded",
            out_dir=EXTRACTION_DESTINATION,
            filename="Mendeley.csv",
            overwrite=True,
            timeout=60,
        )

        success_count += 1
        print("Finished extracting Mendeley files.\n")
    except Exception as e:
        failure_count += 1
        print(f"Failed to extract Mendeley files: {e}\n")

    # Extract DDInter datasets from Kaggle
    print("Extracting DDInter files...")
    try:
        extract_kaggle_dataset_and_save_members(
            dataset="montassarba/drug-drug-interactions-database-ddinter",
            out_dir=EXTRACTION_DESTINATION,
            overwrite=True,
        )

        success_count += 1
        print("Finished extracting DDInter files.\n")
    except Exception as e:
        failure_count += 1
        print(f"Failed to extract DDInter files: {e}\n")

    # Extract AEOLUS dataset from Kaggle
    print("Extracting AEOLUS files...")
    try:
        extract_kaggle_dataset_and_save_members(
            dataset="fda/adverse-pharmaceuticals-events",
            out_dir=EXTRACTION_DESTINATION,
            overwrite=True,
        )

        success_count += 1
        print("Finished extracting AEOLUS files.\n")
    except Exception as e:
        failure_count += 1
        print(f"Failed to extract AEOLUS files: {e}\n")

    print("=" * divider_length)
    print(f"Successfully extracted {success_count} datasets.")

    if failure_count > 0:
        print(f"Failed to extract {failure_count} datasets.")
    print("=" * divider_length)
