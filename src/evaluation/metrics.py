import logging
import sys
import os
import json

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.config import GROUND_TRUTH_DIR

logger = logging.getLogger(__name__)

class UMLEvaluator:
    """
    Calculates Precision, Recall, and F1-Score by comparing 
    extracted UML components against a ground truth dataset loaded from JSON.
    """
    def __init__(self):
        pass

    def load_ground_truth(self, filename: str) -> dict:
        """Loads a ground truth JSON file from the data/ground_truth directory."""
        file_path = os.path.join(GROUND_TRUTH_DIR, filename)
        if not os.path.exists(file_path):
            logger.error(f"Ground truth file not found: {file_path}")
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                
                # Convert lists of lists from JSON back to lists of tuples for strict matching
                if 'attributes' in data:
                    data['attributes'] = [tuple(x) for x in data['attributes']]
                if 'methods' in data:
                    data['methods'] = [tuple(x) for x in data['methods']]
                if 'relationships' in data:
                    data['relationships'] = [tuple(x) for x in data['relationships']]
                    
                return data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format in {file_path}")
                return {}

    def calculate_metrics(self, extracted: set, ground_truth: set) -> dict:
        """Calculates standard Information Retrieval (IR) metrics."""
        true_positives = len(extracted.intersection(ground_truth))
        false_positives = len(extracted - ground_truth)
        false_negatives = len(ground_truth - extracted)

        # Handle division by zero
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1_score": round(f1_score, 2)
        }

    def evaluate_pipeline(self, extracted_data: dict, ground_truth_data: dict) -> dict:
        """Evaluates all UML components and returns a comprehensive report."""
        if not ground_truth_data:
            logger.warning("Empty ground truth data provided. Cannot evaluate.")
            return {}

        ext_classes = set(extracted_data.get('classes', []))
        gt_classes = set(ground_truth_data.get('classes', []))
        
        ext_attrs = set(extracted_data.get('attributes', []))
        gt_attrs = set(ground_truth_data.get('attributes', []))
        
        ext_methods = set(extracted_data.get('methods', []))
        gt_methods = set(ground_truth_data.get('methods', []))
        
        ext_rels = set(extracted_data.get('relationships', []))
        gt_rels = set(ground_truth_data.get('relationships', []))

        report = {
            "Classes": self.calculate_metrics(ext_classes, gt_classes),
            "Attributes": self.calculate_metrics(ext_attrs, gt_attrs),
            "Methods": self.calculate_metrics(ext_methods, gt_methods),
            "Relationships": self.calculate_metrics(ext_rels, gt_rels)
        }
        
        return report

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    evaluator = UMLEvaluator()
    
    # 1. Create a dummy ground truth JSON file for testing
    dummy_gt_filename = "sample_srs_gt.json"
    dummy_gt_path = os.path.join(GROUND_TRUTH_DIR, dummy_gt_filename)
    
    dummy_gt_data = {
        "classes": ["Books", "Librarian", "Library", "LibraryManagementSystem", "User"], 
        "attributes": [["User", "name"], ["User", "email_address"], ["User", "user_id"]], 
        "methods": [["LibraryManagementSystem", "allow"], ["User", "borrow"]], 
        "relationships": [
            ["Librarian", "Inheritance", "User"],
            ["Library", "Aggregation", "Books"], 
            ["LibraryManagementSystem", "Association", "Library"]
        ]
    }
    
    logger.info(f"Creating sample ground truth file at {dummy_gt_path}...")
    with open(dummy_gt_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_gt_data, f, indent=4)
        
    # 2. Simulate what our AI extracted (perfect match for this test)
    extracted = {
        "classes": ['Books', 'Librarian', 'Library', 'LibraryManagementSystem', 'User'],
        "attributes": [('User', 'name'), ('User', 'email_address'), ('User', 'user_id')],
        "methods": [('LibraryManagementSystem', 'allow'), ('User', 'borrow')],
        "relationships": [
            ('Librarian', 'Inheritance', 'User'),
            ('Library', 'Aggregation', 'Books'),
            ('LibraryManagementSystem', 'Association', 'Library')
        ]
    }
    
    # 3. Load from the file and evaluate
    logger.info("Loading ground truth and evaluating...")
    loaded_gt = evaluator.load_ground_truth(dummy_gt_filename)
    results = evaluator.evaluate_pipeline(extracted, loaded_gt)
    
    print("\n=== EVALUATION METRICS ===")
    for category, metrics in results.items():
        print(f"\n-- {category} --")
        print(f"Precision: {metrics['precision']}")
        print(f"Recall:    {metrics['recall']}")
        print(f"F1 Score:  {metrics['f1_score']}")