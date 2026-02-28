UML Generator – Automated UML Diagram Generation from SRS

An AI-powered system that automatically generates UML diagrams from Software Requirement Specifications (SRS) using Natural Language Processing techniques.

This project extracts entities, relationships, and components from textual requirements and generates:

PlantUML diagrams (.puml)

XMI files (.xmi)

Structured JSON components

Evaluation metrics against ground truth

Features

NLP-based requirement parsing

Automatic class & component extraction

PlantUML diagram generation

XMI export for UML tools

Confidence scoring

Evaluation against ground truth data

Modular and scalable architecture

Project Architecture

Input SRS (.txt)
↓
Text Cleaning
↓
Parsing & Extraction
↓
Classification & Logic Layer
↓
UML Generators
├── PlantUML (.puml)
└── XMI (.xmi)
↓
Evaluation Metrics

Project Structure

Uml_generator/

app/

main.py

src/

core/

nlp/

logic/

generators/

evaluation/

data/

input/

output/

ground_truth/

main.py

generate_requirements.py

requirements.txt

Installation

Clone the repository

git clone https://github.com/therehanhussain/UML-Generator.git

cd UML-Generator

Create a virtual environment (recommended)

python -m venv venv
venv\Scripts\activate (Windows)

Install dependencies

pip install -r requirements.txt

Usage

Place your SRS file inside:

data/input/

Run the project:

python main.py

Generated outputs will be available in:

data/output/

Example Output

sample_srs.puml → PlantUML class diagram

sample_srs.xmi → UML tool compatible file

sample_srs_components.json → Extracted structured components

Evaluation

The system compares generated UML components against ground truth and calculates performance metrics such as:

Precision

Recall

F1-score

Tech Stack

Python

NLP Techniques

PlantUML

JSON Processing

Modular Software Architecture

Use Cases

Software Engineering Automation

Requirement Engineering

AI-assisted System Design

Academic Research

CASE tool development

Author

MD Rehan Hussain
B.Tech – Artificial Intelligence & Machine Learning
Asansol Engineering College

Future Improvements

Transformer-based NLP model integration

GUI-based interface

Web deployment

Sequence and Activity diagram generation

LLM-assisted requirement understanding
