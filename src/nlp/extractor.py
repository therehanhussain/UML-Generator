import logging
import sys
import os

# Ensure the root directory is in the Python path for direct script execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.nlp.clean_text import clean_srs_text
from src.nlp.parser import SRSParser

logger = logging.getLogger(__name__)

class UMLExtractor:
    """
    Extracts UML components (Classes, Attributes, Methods) from parsed text 
    using NLP heuristic rules.
    """
    def __init__(self):
        self.attribute_verbs = {"have", "has", "contain", "contains", "include", "includes"}

    def extract_components(self, doc):
        classes = set()
        attributes = [] 
        methods = []    

        if not doc:
            return {"classes": [], "attributes": [], "methods": []}

        for sent in doc.sents:
            # 1. Extract Classes (Added "attr" to catch inheritance objects like "User")
            for token in sent:
                if token.pos_ in ["NOUN", "PROPN"] and token.dep_ in ["nsubj", "nsubjpass", "dobj", "pobj", "attr"]:
                    class_name = self._get_compound_noun(token)
                    classes.add(class_name)

            # 2. Extract Attributes
            for token in sent:
                if token.lemma_ in self.attribute_verbs and token.pos_ in ["VERB", "AUX"]:
                    subject = next((w for w in token.lefts if w.dep_ in ["nsubj", "nsubjpass"]), None)
                    if subject and subject.pos_ in ["NOUN", "PROPN"]:
                        class_name = self._get_compound_noun(subject)
                        
                        for child in token.rights:
                            if child.dep_ in ["dobj", "attr"]:
                                attrs = self._get_conjuncts(child)
                                for attr in attrs:
                                    attributes.append((class_name, attr))

            # 3. Extract Methods
            for token in sent:
                if token.pos_ == "VERB" and token.lemma_ not in self.attribute_verbs:
                    subject = next((w for w in token.lefts if w.dep_ in ["nsubj", "nsubjpass"]), None)
                    if subject and subject.pos_ in ["NOUN", "PROPN"]:
                        class_name = self._get_compound_noun(subject)
                        methods.append((class_name, token.lemma_))
                    
                    if token.dep_ in ["xcomp", "ccomp"]:
                        head_dobj = next((w for w in token.head.children if w.dep_ == "dobj"), None)
                        if head_dobj and head_dobj.pos_ in ["NOUN", "PROPN"]:
                            class_name = self._get_compound_noun(head_dobj)
                            methods.append((class_name, token.lemma_))

        return {
            "classes": sorted(list(classes)),
            "attributes": attributes,
            "methods": methods
        }

    def _get_compound_noun(self, token):
        compounds = [w.text for w in token.lefts if w.dep_ == "compound"]
        compounds.append(token.text)
        return "".join(word.capitalize() for word in compounds)

    def _get_conjuncts(self, token):
        conjuncts = [token.text]
        for child in token.children:
            if child.dep_ == "conj":
                conjuncts.extend(self._get_conjuncts(child))
        return conjuncts

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Updated test text to verify we catch "User" as a class
    sample_text = "A Librarian is a User."
    
    cleaned = clean_srs_text(sample_text)
    parser = SRSParser()
    doc = parser.parse(cleaned)
    
    extractor = UMLExtractor()
    components = extractor.extract_components(doc)
    
    print("\n=== EXTRACTED UML COMPONENTS ===")
    print(f"Classes found: {components['classes']}")