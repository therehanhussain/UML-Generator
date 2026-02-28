import logging
import sys
import os

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.nlp.clean_text import clean_srs_text
from src.nlp.parser import SRSParser
from src.nlp.extractor import UMLExtractor

logger = logging.getLogger(__name__)

class RelationshipClassifier:
    """
    Detects UML relationships (Association, Aggregation, Inheritance) 
    between extracted classes using rule-based NLP heuristics.
    """
    def __init__(self):
        # Lexical cues for identifying relationship types
        self.inheritance_cues = {"is a", "is an", "extends", "inherits", "type of", "kind of", "are a"}
        self.aggregation_cues = {"has", "have", "contains", "contain", "consists of", "composed of", "comprises"}

    def classify_relationships(self, doc, extracted_classes):
        relationships = [] 
        
        if not doc or not extracted_classes:
            return relationships
        
        # Sort classes by length descending so we match 'LibraryManagementSystem' before 'Library'
        sorted_classes = sorted(extracted_classes, key=len, reverse=True)
            
        for sent in doc.sents:
            text_lower = sent.text.lower()
            
            # Find classes in the sentence, preserving order to determine Subject -> Object direction
            classes_in_sent = []
            
            for token in sent:
                if token.pos_ in ["NOUN", "PROPN"]:
                    compounds = [w.text for w in token.lefts if w.dep_ == "compound"]
                    compounds.append(token.text)
                    noun_phrase = "".join(word.capitalize() for word in compounds)
                    
                    if noun_phrase in sorted_classes and noun_phrase not in classes_in_sent:
                        classes_in_sent.append(noun_phrase)

            # If a sentence contains at least 2 distinct classes, evaluate their relationship
            if len(classes_in_sent) >= 2:
                # The first class mentioned is typically the source (subject), the second is the target (object)
                source = classes_in_sent[0]
                target = classes_in_sent[1]
                
                is_inheritance = any(cue in text_lower for cue in self.inheritance_cues)
                is_aggregation = any(cue in text_lower for cue in self.aggregation_cues)
                
                if is_inheritance:
                    relationships.append((source, "Inheritance", target))
                elif is_aggregation:
                    relationships.append((source, "Aggregation", target))
                else:
                    relationships.append((source, "Association", target))
                    
        unique_rels = list(set(relationships))
        return sorted(unique_rels)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    sample_text = """
    The Library Management System manages the Library.
    A Librarian is a User.
    The Library contains Books.
    """
    
    print("Parsing text and classifying relationships...")
    
    cleaned = clean_srs_text(sample_text)
    parser = SRSParser()
    doc = parser.parse(cleaned)
    
    extractor = UMLExtractor()
    components = extractor.extract_components(doc)
    
    classifier = RelationshipClassifier()
    rels = classifier.classify_relationships(doc, components['classes'])
    
    print(f"\nExtracted Classes available for linking: {components['classes']}")
    print("\n=== CLASSIFIED RELATIONSHIPS ===")
    for source, rel_type, target in rels:
        print(f"[{source}] --({rel_type})--> [{target}]")