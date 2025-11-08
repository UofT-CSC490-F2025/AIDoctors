
import os

REGION = os.getenv("AWS_REGION", "us-east-1")

MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "openai.gpt-oss-120b-1:0")

CSV_PATH = os.getenv(
    "DDI_CSV_PATH",
    os.path.join("data", "joined_data", "patient_ddi_collapsed_from_topk.csv")
)

TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
TOP_P       = float(os.getenv("LLM_TOP_P", "0.9"))
MAX_TOKENS  = int(os.getenv("LLM_MAX_TOKENS", "1000"))

RANDOM_STATE         = int(os.getenv("RANDOM_STATE", "42"))
VAL_TEST_FRACTION    = float(os.getenv("VAL_TEST_FRAC", "0.30"))
TEST_FRACTION_OF_TEMP= float(os.getenv("TEST_FRAC_OF_TEMP", "0.50"))

OUT_DIR = os.getenv("OUT_DIR", os.path.join("llm_eval", "outputs"))
os.makedirs(OUT_DIR, exist_ok=True)
