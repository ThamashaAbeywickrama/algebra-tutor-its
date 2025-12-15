from flask import Blueprint, render_template, request, jsonify, session
from utils.ontology_loader import get_quadratic_equations, get_equation_data, get_hints
import time
import math

bp = Blueprint('quadratic', __name__, url_prefix='/quadratic')

quadratic_equations = get_quadratic_equations()


@bp.route('/dashboard')
def dashboard():
    """Quadratic equations dashboard"""
    return render_template('quadratic_dashboard.html', student_name=session.get('student_name', ''))


@bp.route('/equations')
def get_equations():
    """Get list of quadratic equations"""
    progress = session.get('quadratic_progress', {})
    equation_list = []

    for i, eq in enumerate(quadratic_equations):
        eq_data = get_equation_data(eq)
        equation_list.append({
            "id": i,
            "expression": eq_data['expression'],
            "status": progress.get(f"Equation{i+1}", {}).get("status", "locked"),
            "attempts": progress.get(f"Equation{i+1}", {}).get("attempts", 0),
            "time": progress.get(f"Equation{i+1}", {}).get("time", 0)
        })

    return jsonify({"equations": equation_list})


@bp.route('/equation/<int:eq_id>')
def get_equation(eq_id):
    """Get specific quadratic equation"""
    if eq_id >= len(quadratic_equations):
        return jsonify({"error": "Equation not found"}), 404

    eq = quadratic_equations[eq_id]
    eq_data = get_equation_data(eq)

    session['current_equation'] = eq_id
    session['current_type'] = 'quadratic'
    session['current_step'] = 0
    session['step_attempts'] = 0
    session['start_time'] = time.time()

    return jsonify({
        "id": eq_id,
        "type": "quadratic",
        "expression": eq_data['expression'],
        "a_coefficient": eq_data.get('a_coefficient', 1),
        "b_coefficient": eq_data.get('b_coefficient', 0),
        "c_coefficient": eq_data.get('c_coefficient', 0),
        "discriminant": eq_data.get('discriminant', 0),
        "solution1": eq_data.get('solution1', 0),
        "solution2": eq_data.get('solution2', None)
    })


@bp.route('/check_answer', methods=['POST'])
def check_answer():
    """Check quadratic equation answer"""
    data = request.json
    user_input = data.get('answer', '')
    eq_id = session.get('current_equation', 0)
    current_step = session.get('current_step', 0)
    step_attempts = session.get('step_attempts', 0)

    try:
        user_value = float(
            user_input) if '.' in user_input else int(user_input)
    except ValueError:
        return jsonify({"success": False, "message": "Please enter a valid number"})

    eq = quadratic_equations[eq_id]
    eq_data = get_equation_data(eq)

    a = eq_data.get('a_coefficient', 1)
    b = eq_data.get('b_coefficient', 0)
    c = eq_data.get('c_coefficient', 0)
    discriminant = eq_data.get('discriminant', 0)
    solution1 = eq_data.get('solution1', 0)
    solution2 = eq_data.get('solution2', None)

    step_attempts += 1
    session['step_attempts'] = step_attempts

    # Get hints after 3 attempts
    hint = None
    if step_attempts >= 3:
        hints = get_hints(eq)
        hint_keys = ['step1', 'step2', 'solution']
        hint = hints.get(hint_keys[current_step]) if current_step < len(
            hint_keys) else None
        session['step_attempts'] = 0

    # Step 0: Identify discriminant
    if current_step == 0:
        if user_value == discriminant:
            session['current_step'] = 1
            session['step_attempts'] = 0
            return jsonify({
                "success": True,
                "correct": True,
                "message": "Correct! Now find the first solution.",
                "next_step": 1,
                "progress_text": f"Discriminant = {discriminant}. Use quadratic formula: x = (-b ± √{discriminant}) / 2a"
            })
        else:
            return jsonify({"success": True, "correct": False, "message": "Incorrect. Try again!", "hint": hint})

    # Step 1: First solution
    elif current_step == 1:
        if abs(user_value - solution1) < 0.01:  # Allow small rounding error
            if solution2 is not None:
                session['current_step'] = 2
                session['step_attempts'] = 0
                return jsonify({
                    "success": True,
                    "correct": True,
                    "message": "Correct! Now find the second solution.",
                    "next_step": 2,
                    "progress_text": f"First solution: x = {solution1}"
                })
            else:
                # Only one solution (repeated root)
                time_taken = round(
                    time.time() - session.get('start_time', time.time()), 2)

                progress = session.get('quadratic_progress', {})
                progress[f"Equation{eq_id+1}"]["attempts"] += 1
                progress[f"Equation{eq_id+1}"]["time"] = time_taken
                progress[f"Equation{eq_id+1}"]["status"] = "completed"

                if eq_id + 2 <= len(quadratic_equations):
                    progress[f"Equation{eq_id+2}"]["status"] = "unlocked"

                session['quadratic_progress'] = progress

                return jsonify({
                    "success": True,
                    "correct": True,
                    "message": "Excellent! This equation has one repeated solution!",
                    "completed": True,
                    "time": time_taken
                })
        else:
            return jsonify({"success": True, "correct": False, "message": "Incorrect. Try again!", "hint": hint})

    # Step 2: Second solution
    elif current_step == 2:
        if abs(user_value - solution2) < 0.01:
            time_taken = round(
                time.time() - session.get('start_time', time.time()), 2)

            progress = session.get('quadratic_progress', {})
            progress[f"Equation{eq_id+1}"]["attempts"] += 1
            progress[f"Equation{eq_id+1}"]["time"] = time_taken
            progress[f"Equation{eq_id+1}"]["status"] = "completed"

            if eq_id + 2 <= len(quadratic_equations):
                progress[f"Equation{eq_id+2}"]["status"] = "unlocked"

            session['quadratic_progress'] = progress

            return jsonify({
                "success": True,
                "correct": True,
                "message": "Excellent! You've solved the quadratic equation!",
                "completed": True,
                "time": time_taken
            })
        else:
            return jsonify({"success": True, "correct": False, "message": "Incorrect. Try again!", "hint": hint})


@bp.route('/hint')
def get_hint():
    """Get hint for current step"""
    current_step = session.get('current_step', 0)
    eq_id = session.get('current_equation', 0)

    # Default hints as fallback
    default_hints = [
        "Calculate b² - 4ac where a, b, and c are the coefficients from your equation.",
        "Use the quadratic formula: x = (-b ± √discriminant) / (2a). Start with the + sign.",
        "Use the quadratic formula with the - sign: x = (-b - √discriminant) / (2a)."
    ]

    if eq_id >= len(quadratic_equations):
        return jsonify({
            "hint": default_hints[current_step] if current_step < 3 else "Keep trying!",
            "source": "Default (no equation loaded)"
        })

    eq = quadratic_equations[eq_id]
    hints = get_hints(eq)
    hint_keys = ['step1', 'step2', 'solution']

    # Try to get hint from ontology
    hint = hints.get(hint_keys[current_step]) if current_step < len(
        hint_keys) else None
    source = "Ontology" if hint else "Default Fallback"

    if not hint:
        hint = default_hints[current_step] if current_step < len(
            default_hints) else "Keep trying!"

    return jsonify({"hint": hint, "source": source})


@bp.route('/graph_data/<int:eq_id>')
def graph_data(eq_id):
    """Get graph data for quadratic equation"""
    if eq_id >= len(quadratic_equations):
        return jsonify({"error": "Equation not found"}), 404

    eq = quadratic_equations[eq_id]
    eq_data = get_equation_data(eq)

    a = eq_data.get('a_coefficient', 1)
    b = eq_data.get('b_coefficient', 0)
    c = eq_data.get('c_coefficient', 0)
    solution1 = eq_data.get('solution1', 0)
    solution2 = eq_data.get('solution2', None)

    x_vals = list(range(-10, 11))
    y_vals = [a * x**2 + b * x + c for x in x_vals]

    return jsonify({
        "x_values": x_vals,
        "y_values": y_vals,
        "solution1": solution1,
        "solution2": solution2
    })
