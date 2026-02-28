import os
import logging

# --- NLP Configuration ---
SPACY_MODEL = "en_core_web_sm"

# --- Thresholds & Scoring ---
DEFAULT_CONFIDENCE = 0.85
RELATIONSHIP_THRESHOLD = 0.70

# --- Directory Paths ---
# Dynamically locate the root 'uml_generator' directory
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CORE_DIR)
BASE_DIR = os.path.dirname(SRC_DIR)

DATA_DIR = os.path.join(BASE_DIR, "data")
INPUT_DIR = os.path.join(DATA_DIR, "input")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
GROUND_TRUTH_DIR = os.path.join(DATA_DIR, "ground_truth") # <-- ADDED DIRECTORY

# Ensure required directories exist immediately upon import
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GROUND_TRUTH_DIR, exist_ok=True) # <-- AUTO-CREATE DIRECTORY

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("UML_Architecture")

if __name__ == "__main__":
    logger.info("Configuration loaded successfully.")
    logger.info(f"Base Directory: {BASE_DIR}")
    logger.info(f"Input Directory: {INPUT_DIR}")
    logger.info(f"Output Directory: {OUTPUT_DIR}")
    logger.info(f"Ground Truth Directory: {GROUND_TRUTH_DIR}")