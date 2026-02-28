import streamlit as st
import sys
import os
import logging

# Ensure the root directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlp.clean_text import clean_srs_text
from src.nlp.parser import SRSParser
from src.nlp.extractor import UMLExtractor
from src.logic.classifier import RelationshipClassifier
from src.logic.confidence import ConfidenceScorer
from src.generators.plantuml import PlantUMLGenerator
from src.generators.xmi import XMIGenerator

# --- Caching the NLP Model ---
@st.cache_resource
def load_nlp_pipeline():
    """Loads spaCy model once to prevent reloading on every UI interaction."""
    return SRSParser()

parser = load_nlp_pipeline()
extractor = UMLExtractor()
classifier = RelationshipClassifier()
scorer = ConfidenceScorer()
puml_gen = PlantUMLGenerator()
xmi_gen = XMIGenerator()

# --- Initialize Session State ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
    st.session_state.classes = []
    st.session_state.attributes = []
    st.session_state.methods = []
    st.session_state.relationships = []
    st.session_state.scores = {}
    
# Initialize the key for our text area to prevent hardcoding locks
if 'srs_text_key' not in st.session_state:
    st.session_state.srs_text_key = "" 

# --- UI Layout ---
st.set_page_config(page_title="AI UML Generator", layout="wide")
st.title("🧠 AI-Based Automated UML Diagram Generator")
st.markdown("Extract UML components from Software Requirements Specifications (SRS) with Human-in-the-Loop validation.")

# --- Sidebar: Input ---
with st.sidebar:
    st.header("1. Input Document")
    
    # Callback function: Instantly moves uploaded file text into the text area
    def update_text_from_file():
        if st.session_state.file_uploader is not None:
            text = st.session_state.file_uploader.getvalue().decode("utf-8")
            st.session_state.srs_text_key = text

    # File Uploader tied to the callback
    st.file_uploader(
        "Upload SRS Document (.txt)", 
        type=["txt"], 
        key="file_uploader", 
        on_change=update_text_from_file
    )
    
    # Text Area explicitly bound to the session state key
    srs_input = st.text_area(
        "Or Paste/Edit SRS Text Here:", 
        key="srs_text_key",
        height=300,
        placeholder="Type or paste your requirements here..."
    )
    
    if st.button("Extract Components", type="primary"):
        if not srs_input.strip():
            st.warning("Please enter or upload some text first.")
        else:
            with st.spinner("Parsing NLP & Extracting Entities..."):
                cleaned = clean_srs_text(srs_input)
                doc = parser.parse(cleaned)
                
                # Extraction
                components = extractor.extract_components(doc)
                rels = classifier.classify_relationships(doc, components['classes'])
                
                # Update Session State
                st.session_state.classes = components['classes']
                st.session_state.attributes = components['attributes']
                st.session_state.methods = components['methods']
                st.session_state.relationships = rels
                st.session_state.scores = scorer.score_all(components, rels)
                st.session_state.processed = True

# --- Main Area: Human-in-the-loop & Generation ---
if st.session_state.processed:
    st.header("2. Human-in-the-Loop Validation")
    st.info("Review the extracted components below. You can edit the text directly before generating the final UML code.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Classes")
        class_scores = ", ".join([f"{k} ({v})" for k, v in st.session_state.scores.get("classes", {}).items()])
        st.caption(f"AI Confidence: {class_scores}")
        
        classes_str = "\n".join(st.session_state.classes)
        edited_classes = st.text_area("Edit Classes (one per line):", value=classes_str, height=150)
        
        st.subheader("Attributes (Class, Attribute)")
        attrs_str = "\n".join([f"{c}, {a}" for c, a in st.session_state.attributes])
        edited_attrs = st.text_area("Edit Attributes:", value=attrs_str, height=150)

    with col2:
        st.subheader("Relationships (Source, Type, Target)")
        rel_scores = ", ".join([f"{v}" for k, v in st.session_state.scores.get("relationships", {}).items()])
        st.caption(f"AI Confidence: {rel_scores}")
        
        rels_str = "\n".join([f"{s}, {t}, {tgt}" for s, t, tgt in st.session_state.relationships])
        edited_rels = st.text_area("Edit Relationships:", value=rels_str, height=150)
        
        st.subheader("Methods (Class, Method)")
        methods_str = "\n".join([f"{c}, {m}" for c, m in st.session_state.methods])
        edited_methods = st.text_area("Edit Methods:", value=methods_str, height=150)

    st.markdown("---")
    st.header("3. Generate Code")
    
    if st.button("Generate PlantUML & XMI", type="primary"):
        # Parse the edited text areas back into lists/tuples
        final_classes = [c.strip() for c in edited_classes.split("\n") if c.strip()]
        
        final_attrs = []
        for line in edited_attrs.split("\n"):
            if "," in line:
                c, a = line.split(",", 1)
                final_attrs.append((c.strip(), a.strip()))
                
        final_methods = []
        for line in edited_methods.split("\n"):
            if "," in line:
                c, m = line.split(",", 1)
                final_methods.append((c.strip(), m.strip()))
                
        final_rels = []
        for line in edited_rels.split("\n"):
            if line.count(",") == 2:
                s, t, tgt = line.split(",")
                final_rels.append((s.strip(), t.strip(), tgt.strip()))

        # Generate output
        puml_output = puml_gen.generate_puml(final_classes, final_attrs, final_methods, final_rels)
        xmi_output = xmi_gen.generate_xmi(final_classes, final_attrs, final_methods, final_rels)
        
        # Display in tabs
        tab1, tab2 = st.tabs(["PlantUML", "XMI (XML)"])
        with tab1:
            st.code(puml_output, language="plantuml")
            st.caption("Tip: You can preview this code using the PlantUML VS Code extension.")
        with tab2:
            st.code(xmi_output, language="xml")