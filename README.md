# Intelligent Tutoring System for Algebra

An adaptive tutoring system for teaching linear and quadratic equations 
with personalized hint generation based on student proficiency levels.

## Features

- Diagnostic quiz to assess student proficiency
- Ontology-based domain knowledge representation
- Adaptive feedback with 3 proficiency levels
- Interactive problem-solving interface
- Progress tracking and achievements

## Technology Stack

- **Backend:** Python 3.9, Flask
- **Ontology:** OWL, Protégé
- **Frontend:** HTML5, CSS3, JavaScript
- **Ontology Processing:** Owlready2

## Setup

1. Clone repository: `git clone https://github.com/USERNAME/algebra-tutor-its.git`
2. Create virtual environment: `python -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Open browser to `http://localhost:5001`

## Project Structure
algebra-tutor/
├── app.py
├── algebra_tutor2.owl
├── requirements.txt
├── routes/
│   ├── auth.py
│   ├── linear.py
│   ├── quadratic.py
│   ├── quiz.py
│   └── progress.py
├── utils/
│   ├── ontology_loader.py
│   └── hint_personalizer.py
└── templates/
├── login.html
├── home.html
├── diagnostic_quiz.html
└── [other templates]

## Author

Thamasha Abeywickrama

## Date

October 2025 - December 2025
