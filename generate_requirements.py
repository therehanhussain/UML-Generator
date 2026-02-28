required_packages = [
    "streamlit",
    "spacy",
    "scikit-learn",
    "networkx",
    "pandas",
    # SpaCy model for Streamlit Cloud deployment
    "en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz"
]

with open("requirements.txt", "w", encoding="utf-8") as f:
    for package in required_packages:
        f.write(package + "\n")

print("✅ requirements.txt generated successfully!")