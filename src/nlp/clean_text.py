import re
import logging

# Set up local logger
logger = logging.getLogger(__name__)

def clean_srs_text(raw_text: str) -> str:
    """
    Cleans and standardizes raw SRS text for NLP parsing.
    Removes noise but preserves punctuation required for dependency parsing.
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        logger.warning("Empty or invalid text provided for cleaning.")
        return ""

    # 1. Remove non-ASCII characters (common in PDF/Word copy-pastes)
    text = re.sub(r'[^\x00-\x7F]+', ' ', raw_text)
    
    # 2. Replace newlines and carriage returns with spaces 
    # (spaCy parses better when sentences flow normally)
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # 3. Standardize whitespace (remove double/triple spaces)
    text = re.sub(r'\s+', ' ', text)
    
    # 4. Strip leading/trailing whitespace
    text = text.strip()
    
    return text

if __name__ == "__main__":
    # Basic Preprocessing Test Script
    sample_srs_text = """
    The    Library Management System 
    shall allow a User to borrow books. 
    
    • A User has a name, email_address, and user_id.
    
    The system MUST   generate an invoice!
    """
    
    print("=== RAW TEXT ===")
    print(repr(sample_srs_text))
    
    print("\n=== CLEANED TEXT ===")
    cleaned_text = clean_srs_text(sample_srs_text)
    print(repr(cleaned_text))