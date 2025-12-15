from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.ontology_loader import get_linear_equations, get_quadratic_equations

bp = Blueprint('quiz', __name__, url_prefix='/quiz')

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Solve: x + 5 = 12",
        "options": ["x = 7", "x = 17", "x = 5", "x = 12"],
        "correct": 0,
        "difficulty": "easy",
        "type": "linear"
    },
    {
        "id": 2,
        "question": "What is the coefficient in 3x + 2 = 11?",
        "options": ["3", "2", "11", "x"],
        "correct": 0,
        "difficulty": "easy",
        "type": "linear"
    },
    {
        "id": 3,
        "question": "Solve: 2x - 4 = 10",
        "options": ["x = 7", "x = 3", "x = 5", "x = 2"],
        "correct": 0,
        "difficulty": "medium",
        "type": "linear"
    },
    {
        "id": 4,
        "question": "What is the general form of a quadratic equation?",
        "options": ["ax² + bx + c = 0", "ax + b = 0", "x + y = 0", "2x² = 4"],
        "correct": 0,
        "difficulty": "easy",
        "type": "quadratic"
    },
    {
        "id": 5,
        "question": "For x² - 5x + 6 = 0, what are a, b, c?",
        "options": ["a=1, b=-5, c=6", "a=1, b=5, c=6", "a=2, b=-5, c=3", "a=-1, b=5, c=-6"],
        "correct": 0,
        "difficulty": "medium",
        "type": "quadratic"
    },
    {
        "id": 6,
        "question": "What is the AC product for x² + 7x + 12 = 0?",
        "options": ["12", "7", "84", "19"],
        "correct": 2,
        "difficulty": "hard",
        "type": "quadratic"
    },
    {
        "id": 7,
        "question": "Solve: x² - 4 = 0",
        "options": ["x = 2 or x = -2", "x = 4", "x = 2", "No solution"],
        "correct": 0,
        "difficulty": "medium",
        "type": "quadratic"
    }
]


@bp.route('/get_questions')
def get_questions():
    return jsonify({"questions": QUIZ_QUESTIONS})


@bp.route('/submit', methods=['POST'])
def submit_quiz():
    data = request.json
    answers = data.get('answers', {})

    correct = 0
    total = len(QUIZ_QUESTIONS)

    for q_id, selected_idx in answers.items():
        q = next((q for q in QUIZ_QUESTIONS if q['id'] == int(q_id)), None)
        if q and selected_idx == q['correct']:
            correct += 1

    score = (correct / total) * 100

    # Determine performance level based on score
    if score >= 75:
        level = "high"
    elif score >= 50:
        level = "moderate"
    else:
        level = "low"

    # Store in session
    session['performance_level'] = level
    session['quiz_completed'] = True
    session['quiz_score'] = score
    session['quiz_correct'] = correct

    # Initialize progress
    linear_equations = get_linear_equations()
    quadratic_equations = get_quadratic_equations()

    session['linear_progress'] = {
        f"Equation{i+1}": {
            "attempts": 0,
            "time": 0,
            "status": "unlocked" if i == 0 else "locked"
        } for i in range(len(linear_equations))
    }

    session['quadratic_progress'] = {
        f"Equation{i+1}": {
            "attempts": 0,
            "time": 0,
            "status": "unlocked" if i == 0 else "locked"
        } for i in range(len(quadratic_equations))
    }

    return jsonify({
        "success": True,
        "score": score,
        "correct": correct,
        "total": total,
        "level": level
    })
