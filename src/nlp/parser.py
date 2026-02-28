import spacy
import logging
import sys
import os

# Ensure the root directory is in the Python path for direct script execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.config import SPACY_MODEL
from src.nlp.clean_text import clean_srs_text

# Set up local logger
logger = logging.getLogger(__name__)

class SRSParser:
    """
    Handles natural language parsing of SRS documents using spaCy.
    Performs sentence splitting, POS tagging, and dependency parsing.
    """
    def __init__(self):
        logger.info(f"Loading spaCy model: '{SPACY_MODEL}'...")
        try:
            self.nlp = spacy.load(SPACY_MODEL)
            logger.info("spaCy model loaded successfully.")
        except OSError:
            logger.error(
                f"Model '{SPACY_MODEL}' not found. "
                f"Please run: python -m spacy download {SPACY_MODEL}"
            )
            raise

    def parse(self, text: str):
        """
        Processes text through the spaCy pipeline.
        Returns a spaCy Doc object containing tokens, POS tags, and dependencies.
        """
        if not text or not text.strip():
            logger.warning("Empty text passed to parser.")
            return None
        return self.nlp(text)

    def get_sentences(self, doc):
        """Extracts individual sentences from a parsed spaCy document."""
        if not doc:
            return []
        return list(doc.sents)


if __name__ == "__main__":
    # Basic Parsing Test Script
    logging.basicConfig(level=logging.INFO)
    
    sample_text = """
    The Library Management System shall allow a User to borrow books. 
    A User has a name, email_address, and user_id.
    """
    
    # 1. Clean the text using our Phase 2 module
    cleaned_text = clean_srs_text(sample_text)
    
    # 2. Initialize parser
    parser = SRSParser()
    
    # 3. Parse text
    doc = parser.parse(cleaned_text)
    
    if doc:
        print("\n=== SENTENCE SPLITTING ===")
        for i, sent in enumerate(parser.get_sentences(doc)):
            print(f"Sentence {i+1}: {sent.text}")
            
        print("\n=== POS & DEPENDENCY PARSING (First Sentence) ===")
        print(f"{'Token':<15} | {'POS Tag':<8} | {'Dependency':<12} | {'Head Word'}")
        print("-" * 55)
        
        # Display linguistic features for the first sentence
        first_sent = list(doc.sents)[0]
        for token in first_sent:
            print(f"{token.text:<15} | {token.pos_:<8} | {token.dep_:<12} | {token.head.text}")