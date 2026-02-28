import os
import logging
import sys

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class PlantUMLGenerator:
    """
    Generates standard PlantUML code from extracted UML components.
    """
    def __init__(self):
        # Mapping our relationship types to PlantUML syntax
        self.rel_mapping = {
            "Inheritance": "--|>",   # Source inherits from Target
            "Aggregation": "o--",    # Source aggregates Target
            "Association": "-->"     # Source is associated with Target
        }

    def generate_puml(self, classes: list, attributes: list, methods: list, relationships: list) -> str:
        """
        Takes structured UML data and returns a valid PlantUML string.
        """
        lines = ["@startuml", "skinparam classAttributeIconSize 0", ""]
        
        # 1. Generate Classes with Attributes and Methods
        for cls in classes:
            lines.append(f"class {cls} {{")
            
            # Add attributes specifically belonging to this class
            cls_attrs = [attr for c, attr in attributes if c == cls]
            for attr in cls_attrs:
                lines.append(f"  +{attr}")
                
            # Add methods specifically belonging to this class
            cls_methods = [method for c, method in methods if c == cls]
            for method in cls_methods:
                lines.append(f"  +{method}()")
                
            lines.append("}")
            lines.append("")
            
        # 2. Generate Relationships
        for source, rel_type, target in relationships:
            puml_arrow = self.rel_mapping.get(rel_type, "-->")
            
            if rel_type == "Association":
                # Label the generic associations
                lines.append(f"{source} {puml_arrow} {target} : {rel_type}")
            else:
                lines.append(f"{source} {puml_arrow} {target}")
                
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Simulated data from Phase 4 & 5 (with the Association logic corrected for the test)
    test_classes = ['Books', 'Librarian', 'Library', 'LibraryManagementSystem', 'User']
    test_attributes = [('User', 'name'), ('User', 'email_address'), ('User', 'user_id')]
    test_methods = [('LibraryManagementSystem', 'allow'), ('User', 'borrow')]
    test_relationships = [
        ('Librarian', 'Inheritance', 'User'),
        ('Library', 'Aggregation', 'Books'),
        ('LibraryManagementSystem', 'Association', 'Library') 
    ]
    
    generator = PlantUMLGenerator()
    puml_code = generator.generate_puml(test_classes, test_attributes, test_methods, test_relationships)
    
    print("=== GENERATED PLANTUML CODE ===")
    print(puml_code)