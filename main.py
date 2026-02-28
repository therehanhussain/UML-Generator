import os
import logging
import json

from src.core.config import INPUT_DIR, OUTPUT_DIR
from src.nlp.clean_text import clean_srs_text
from src.nlp.parser import SRSParser
from src.nlp.extractor import UMLExtractor
from src.logic.classifier import RelationshipClassifier
from src.generators.plantuml import PlantUMLGenerator
from src.generators.xmi import XMIGenerator

# Set up logging for the CLI pipeline
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("EndToEndPipeline")

def run_pipeline(input_filename="sample_srs.txt"):
    """
    Runs the fully automated, headless UML generation pipeline.
    """
    input_path = os.path.join(INPUT_DIR, input_filename)
    
    # --- Step 0: Ensure input file exists ---
    if not os.path.exists(input_path):
        logger.info(f"Creating sample input file at {input_path}...")
        sample_text = """
        The Library Management System shall allow a User to borrow books.
        A Librarian is a User.
        The Library contains Books.
        """
        with open(input_path, "w", encoding="utf-8") as f:
            f.write(sample_text.strip())
            
    # --- Step 1: Read & Preprocess ---
    logger.info(f"Reading input from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
        
    cleaned_text = clean_srs_text(raw_text)
    
    # --- Step 2: NLP Parsing ---
    logger.info("Initializing NLP Parser...")
    parser = SRSParser()
    doc = parser.parse(cleaned_text)
    
    # --- Step 3: Extraction & Classification ---
    logger.info("Extracting UML Components...")
    extractor = UMLExtractor()
    components = extractor.extract_components(doc)
    
    logger.info("Classifying Relationships...")
    classifier = RelationshipClassifier()
    relationships = classifier.classify_relationships(doc, components['classes'])
    
    # --- Step 4: Code Generation ---
    logger.info("Generating PlantUML and XMI code...")
    puml_gen = PlantUMLGenerator()
    xmi_gen = XMIGenerator()
    
    puml_code = puml_gen.generate_puml(
        components['classes'], components['attributes'], components['methods'], relationships
    )
    
    xmi_code = xmi_gen.generate_xmi(
        components['classes'], components['attributes'], components['methods'], relationships
    )
    
    # --- Step 5: Save Outputs ---
    base_name = os.path.splitext(input_filename)[0]
    puml_out_path = os.path.join(OUTPUT_DIR, f"{base_name}.puml")
    xmi_out_path = os.path.join(OUTPUT_DIR, f"{base_name}.xmi")
    json_out_path = os.path.join(OUTPUT_DIR, f"{base_name}_components.json")
    
    with open(puml_out_path, "w", encoding="utf-8") as f:
        f.write(puml_code)
        
    with open(xmi_out_path, "w", encoding="utf-8") as f:
        f.write(xmi_code)
        
    with open(json_out_path, "w", encoding="utf-8") as f:
        # Save the raw extracted components for debugging and evaluation
        full_data = {"components": components, "relationships": relationships}
        json.dump(full_data, f, indent=4)
        
    logger.info("=== PIPELINE COMPLETE ===")
    logger.info(f"Outputs saved to: {OUTPUT_DIR}")
    logger.info(f" - {os.path.basename(puml_out_path)}")
    logger.info(f" - {os.path.basename(xmi_out_path)}")
    logger.info(f" - {os.path.basename(json_out_path)}")


if __name__ == "__main__":
    print("\nStarting End-to-End Automated UML Pipeline...\n")
    run_pipeline("sample_srs.txt")