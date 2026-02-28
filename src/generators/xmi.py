import os
import sys
import logging
import xml.etree.ElementTree as ET
import xml.dom.minidom

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class XMIGenerator:
    """
    Generates standard XMI (XML Metadata Interchange) format 
    from extracted UML components for tool interoperability.
    """
    def __init__(self):
        # Define standard UML namespaces
        self.namespaces = {
            "xmi": "http://www.omg.org/spec/XMI/20131001",
            "uml": "http://www.eclipse.org/uml2/5.0.0/UML"
        }

    def generate_xmi(self, classes: list, attributes: list, methods: list, relationships: list) -> str:
        """
        Builds an XML tree representing the UML model and returns a formatted XML string.
        """
        # 1. Create Root Element
        root = ET.Element("xmi:XMI", {
            "xmlns:xmi": self.namespaces["xmi"],
            "xmlns:uml": self.namespaces["uml"],
            "xmi:version": "2.5"
        })
        
        # 2. Create Model Container
        model = ET.SubElement(root, "uml:Model", {"name": "Automated_SRS_Model", "xmi:id": "model_1"})
        
        # Map class names to dynamically generated XMI IDs for relationship linking
        class_id_map = {}
        
        # 3. Generate Classes, Attributes, and Methods
        for i, cls in enumerate(classes):
            cls_id = f"class_{i}"
            class_id_map[cls] = cls_id
            
            # Create Class Node
            class_node = ET.SubElement(model, "packagedElement", {
                "xmi:type": "uml:Class", 
                "xmi:id": cls_id, 
                "name": cls
            })
            
            # Add Attributes
            cls_attrs = [attr for c, attr in attributes if c == cls]
            for j, attr in enumerate(cls_attrs):
                ET.SubElement(class_node, "ownedAttribute", {
                    "xmi:id": f"{cls_id}_attr_{j}",
                    "name": attr,
                    "visibility": "public"
                })
                
            # Add Methods
            cls_methods = [method for c, method in methods if c == cls]
            for k, method in enumerate(cls_methods):
                ET.SubElement(class_node, "ownedOperation", {
                    "xmi:id": f"{cls_id}_op_{k}",
                    "name": method,
                    "visibility": "public"
                })
                
        # 4. Generate Relationships
        for i, (source, rel_type, target) in enumerate(relationships):
            source_id = class_id_map.get(source, "unknown")
            target_id = class_id_map.get(target, "unknown")
            rel_id = f"rel_{i}"
            
            uml_type = "uml:Association"
            if rel_type == "Inheritance":
                uml_type = "uml:Generalization"
                
                # FIXED: Safely find the source node without relying on XPath namespaces
                source_node = next(
                    (node for node in model.findall("packagedElement") if node.get("xmi:id") == source_id), 
                    None
                )
                
                if source_node is not None:
                    ET.SubElement(source_node, "generalization", {
                        "xmi:id": rel_id,
                        "general": target_id
                    })
                continue
            
            # For Association and Aggregation
            rel_node = ET.SubElement(model, "packagedElement", {
                "xmi:type": uml_type,
                "xmi:id": rel_id,
                "name": f"{source}_{rel_type}_{target}"
            })
            
            # Add member ends to link the two classes
            ET.SubElement(rel_node, "ownedEnd", {"type": source_id})
            ET.SubElement(rel_node, "ownedEnd", {"type": target_id})
            
            if rel_type == "Aggregation":
                # Mark aggregation explicitly
                rel_node.set("aggregation", "shared")

        # 5. Pretty Print XML
        xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        parsed_xml = xml.dom.minidom.parseString(xml_string)
        return parsed_xml.toprettyxml(indent="  ")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Reusing the same simulated data
    test_classes = ['Books', 'Librarian', 'Library', 'LibraryManagementSystem', 'User']
    test_attributes = [('User', 'name'), ('User', 'email_address'), ('User', 'user_id')]
    test_methods = [('LibraryManagementSystem', 'allow'), ('User', 'borrow')]
    test_relationships = [
        ('Librarian', 'Inheritance', 'User'),
        ('Library', 'Aggregation', 'Books'),
        ('LibraryManagementSystem', 'Association', 'Library') 
    ]
    
    generator = XMIGenerator()
    xmi_code = generator.generate_xmi(test_classes, test_attributes, test_methods, test_relationships)
    
    print("=== GENERATED XMI CODE ===")
    print(xmi_code)