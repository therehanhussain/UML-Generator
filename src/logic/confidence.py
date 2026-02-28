import logging
import sys
import os

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """
    Assigns confidence scores (0.0 to 1.0) to extracted UML components 
    and relationships based on heuristic rules.
    """
    def __init__(self):
        # Base confidence levels
        self.base_class_score = 0.80
        self.base_attr_method_score = 0.85
        
        # Relationship specific base scores
        self.rel_scores = {
            "Inheritance": 0.95,  # High confidence due to strict lexical cues ("is a")
            "Aggregation": 0.90,  # High confidence due to explicit cues ("has a")
            "Association": 0.70   # Lower confidence as it's often a fallback inference
        }

    def score_all(self, components: dict, relationships: list) -> dict:
        """
        Takes extracted components and relationships, and returns a dictionary 
        of scores for UI rendering.
        """
        scores = {
            "classes": {},
            "attributes": {},
            "methods": {},
            "relationships": {}
        }

        # 1. Score Classes
        for cls in components.get("classes", []):
            score = self.base_class_score
            # Heuristic: Standard OOP classes are usually CamelCase or TitleCase
            if cls[0].isupper():
                score += 0.10
            # Cap at 0.95 for rule-based systems (never 100% sure without human review)
            scores["classes"][cls] = min(score, 0.95)

        # 2. Score Attributes
        for cls, attr in components.get("attributes", []):
            score = self.base_attr_method_score
            # Heuristic: Attributes shouldn't typically have spaces or start with uppercase
            if " " not in attr and attr[0].islower():
                score += 0.05
            scores["attributes"][f"{cls}.{attr}"] = min(score, 0.95)

        # 3. Score Methods
        for cls, method in components.get("methods", []):
            score = self.base_attr_method_score
            # Heuristic: Methods usually don't have spaces and are lowercase verbs
            if " " not in method and method[0].islower():
                score += 0.05
            scores["methods"][f"{cls}.{method}()"] = min(score, 0.95)

        # 4. Score Relationships
        for source, rel_type, target in relationships:
            score = self.rel_scores.get(rel_type, 0.70)
            
            # Heuristic Penalty: If the related classes have low confidence, 
            # the relationship confidence should also degrade slightly.
            source_conf = scores["classes"].get(source, 0.80)
            target_conf = scores["classes"].get(target, 0.80)
            
            if source_conf < 0.85 or target_conf < 0.85:
                score -= 0.10
                
            rel_key = f"[{source}] --({rel_type})--> [{target}]"
            scores["relationships"][rel_key] = round(score, 2)

        return scores


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Reusing the simulated data from Phase 5 & 6
    test_components = {
        "classes": ['Books', 'Librarian', 'Library', 'LibraryManagementSystem', 'User', 'system_error'],
        "attributes": [('User', 'name'), ('User', 'email_address'), ('User', 'UserID')],
        "methods": [('LibraryManagementSystem', 'allow'), ('User', 'borrow')]
    }
    
    test_relationships = [
        ('Librarian', 'Inheritance', 'User'),
        ('Library', 'Aggregation', 'Books'),
        ('LibraryManagementSystem', 'Association', 'Library'),
        ('system_error', 'Association', 'Library') # Simulating a low-confidence extracted relation
    ]
    
    scorer = ConfidenceScorer()
    confidence_results = scorer.score_all(test_components, test_relationships)
    
    print("=== CONFIDENCE SCORES ===")
    
    print("\n-- Classes --")
    for item, score in confidence_results["classes"].items():
        print(f"{item}: {score:.2f}")
        
    print("\n-- Attributes & Methods --")
    for item, score in confidence_results["attributes"].items():
        print(f"{item}: {score:.2f}")
    for item, score in confidence_results["methods"].items():
        print(f"{item}: {score:.2f}")
        
    print("\n-- Relationships --")
    for item, score in confidence_results["relationships"].items():
        print(f"{item}: {score:.2f}")