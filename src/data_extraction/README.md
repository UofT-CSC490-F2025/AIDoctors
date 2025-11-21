# Data Extraction

These files fetch and store the raw datasets required by the application.

## Setup

Open up a terminal and ensure your working directory is set to this folder (i.e. `data_extraction`).

Create a virtual environment using the `venv` module:

```bash
python3 -m venv .venv
```

Then, activate the virtual environment using the appropriate command:

```bash
# On macOS/Linux
source .venv/bin/activate
```

```bash
# On Windows
.\.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To run the data fetching script:

```bash
python3 fetch_datasets.py -o <OUTPUT_PATH>
```

This will fetch the raw datasets and place them in the relative directory defined by `<OUTPUT_PATH>`. Intermediate folders will be created if the path does not exist.
