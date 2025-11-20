"""
Script to download and extract CSVs from:
  - DDInter
  - CRESCENDDI 
  - Synthea
  - Mendeley
  - AEOLUS
"""

if __name__ == "__main__":
    from utilities import extract_and_save, extract_zip_and_save_members, extract_kaggle_dataset_and_save_members

    EXTRACTION_DESTINATION = "data/raw_datasets"

    # Extract CRESCENDDI files (can also use extract_xlsx_and_save_csv to save as CSVs)
    print("Extracting CRESCENDDI files...")
    extract_and_save(
        url="https://github.com/elpidakon/CRESCENDDI/raw/refs/heads/main/data_records/Data%20Record%201%20-%20Positive%20Controls.xlsx",
        out_dir=EXTRACTION_DESTINATION,
        filename="CRESCENDDI - Positive Controls.xlsx",
        overwrite=True
    )
    extract_and_save(
        url="https://github.com/elpidakon/CRESCENDDI/raw/refs/heads/main/data_records/Data%20Record%202%20-%20Negative%20Controls.xlsx",
        out_dir=EXTRACTION_DESTINATION,
        filename="CRESCENDDI - Negative Controls.xlsx",
        overwrite=True
    )
    extract_and_save(
        url="https://github.com/elpidakon/CRESCENDDI/raw/refs/heads/main/data_records/Data%20Record%204%20-%20Drug%20mappings.xlsx",
        out_dir=EXTRACTION_DESTINATION,
        filename="CRESCENDDI - Drug mappings.xlsx",
        overwrite=True
    )
    print("Finished extracting CRESCENDDI files.\n")

    # Extract Synthea dataset
    print("Extracting Synthea files...")
    extract_zip_and_save_members(
        url="https://synthetichealth.github.io/synthea-sample-data/downloads/latest/synthea_sample_data_csv_latest.zip",
        out_dir=EXTRACTION_DESTINATION,
        members=["conditions.csv", "medications.csv", "patients.csv"],
        overwrite=True
    )
    print("Finished extracting Synthea files.\n")

    # Extract Mendeley dataset
    print("Extracting Mendeley files...")
    extract_and_save(
        url="https://data.mendeley.com/public-files/datasets/md5czfsfnd/files/4530a4be-8cff-4cfb-a309-9343f92f6832/file_downloaded",
        out_dir=EXTRACTION_DESTINATION,
        filename="Mendeley.csv",
        overwrite=True,
        timeout=60
    )
    print("Finished extracting Mendeley files.\n")

    # Extract DDInter datasets from Kaggle
    print("Extracting DDInter files...")
    extract_kaggle_dataset_and_save_members(
        dataset="montassarba/drug-drug-interactions-database-ddinter",
        out_dir=EXTRACTION_DESTINATION,
        overwrite=True
    )
    print("Finished extracting DDInter files.\n")

    # # Extract AEOLUS dataset (doesn't work because of bot protection)
    # print("Extracting AEOLUS files...")
    # extract_and_save(
    #     url="https://datadryad.org/downloads/file_stream/67855",
    #     out_dir=EXTRACTION_DESTINATION,
    #     overwrite=True
    # )
    # print("Finished extracting AEOLUS files.\n")
