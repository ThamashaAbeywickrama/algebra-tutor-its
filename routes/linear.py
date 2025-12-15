from flask import Blueprint, render_template, request, jsonify, session
from utils.ontology_loader import get_linear_equations, get_equation_data, get_hints
from utils.hint_personalizer import get_hint_for_performance
import time

bp = Blueprint('linear', __name__, url_prefix='/linear')

linear_equations = get_linear_equations()


@bp.route('/dashboard')
def dashboard():
    return render_template('linear_dashboard.html', student_name=session.get('student_name', ''))


@bp.route('/equations')
def get_equations():
    progress = session.get('linear_progress', {})
    equation_list = []

    for i, eq in enumerate(linear_equations):
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
    if eq_id >= len(linear_equations):
        return jsonify({"error": "Equation not found"}), 404

    eq = linear_equations[eq_id]
    eq_data = get_equation_data(eq)

    session['current_equation'] = eq_id
    session['current_type'] = 'linear'
    session['current_step'] = 0
    session['step_attempts'] = 0
    session['start_time'] = time.time()

    return jsonify({
        "id": eq_id,
        "type": "linear",
        "expression": eq_data['expression'],
        "constant": eq_data.get('constant', 0),
        "coefficient": eq_data.get('coefficient', 0),
        "solution": eq_data.get('solution', 0)
    })


@bp.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    user_input = data.get('answer', '')
    eq_id = session.get('current_equation', 0)
    current_step = session.get('current_step', 0)
    step_attempts = session.get('step_attempts', 0)

    try:
        user_value = int(user_input)
    except ValueError:
        return jsonify({"success": False, "message": "Please enter a valid number"})

    eq = linear_equations[eq_id]
    eq_data = get_equation_data(eq)
    constant = eq_data.get('constant', 0)
    coefficient = eq_data.get('coefficient', 0)
    solution = eq_data.get('solution', 0)

    step_attempts += 1
    session['step_attempts'] = step_attempts

    # Get personalized hint after 3 attempts
    hint = None
    if step_attempts >= 3:
        performance_level = session.get('performance_level', 'moderate')
        hints = get_hints(eq)

        # Get adaptive hint based on performance level
        hint = get_hint_for_performance(
            hints, performance_level, 'linear', current_step)
        session['step_attempts'] = 0

    # Check answer based on step
    if current_step == 0:  # Constant
        if user_value == constant:
            session['current_step'] = 1
            session['step_attempts'] = 0
            return jsonify({
                "success": True,
                "correct": True,
                "message": "Correct! Moving to next step.",
                "next_step": 1,
                "progress_text": f"After subtracting constant: {coefficient}x = {solution * coefficient}"
            })
        else:
            return jsonify({"success": True, "correct": False, "message": "Incorrect. Try again!", "hint": hint})

    elif current_step == 1:  # Coefficient
        if user_value == coefficient:
            session['current_step'] = 2
            session['step_attempts'] = 0
            return jsonify({
                "success": True,
                "correct": True,
                "message": "Correct! Moving to final step.",
                "next_step": 2,
                "progress_text": f"After dividing: x = {solution}"
            })
        else:
            return jsonify({"success": True, "correct": False, "message": "Incorrect. Try again!", "hint": hint})

    elif current_step == 2:  # Solution
        if user_value == solution:
            time_taken = round(
                time.time() - session.get('start_time', time.time()), 2)

            progress = session.get('linear_progress', {})
            progress[f"Equation{eq_id+1}"]["attempts"] += 1
            progress[f"Equation{eq_id+1}"]["time"] = time_taken
            progress[f"Equation{eq_id+1}"]["status"] = "completed"

            if eq_id + 2 <= len(linear_equations):
                progress[f"Equation{eq_id+2}"]["status"] = "unlocked"

            session['linear_progress'] = progress

            return jsonify({
                "success": True,
                "correct": True,
                "message": "Excellent! You've solved the equation!",
                "completed": True,
                "time": time_taken
            })
        else:
            return jsonify({"success": True, "correct": False, "message": "Incorrect. Try again!", "hint": hint})


@bp.route('/hint')
def get_hint():
    current_step = session.get('current_step', 0)
    eq_id = session.get('current_equation', 0)
    performance_level = session.get('performance_level', 'moderate')

    if eq_id >= len(linear_equations):
        default_hints = [
            "The constant is the number added or subtracted from x in the equation.",
            "The coefficient is the number multiplied by x.",
            "Divide both sides by the coefficient to isolate x."
        ]
        return jsonify({
            "hint": default_hints[current_step] if current_step < 3 else "Keep trying!",
            "source": "Default (no equation loaded)"
        })

    eq = linear_equations[eq_id]
    hints = get_hints(eq)

    # Get personalized hint
    hint = get_hint_for_performance(
        hints, performance_level, 'linear', current_step)

    return jsonify({"hint": hint, "source": "Personalized for your level"})


@bp.route('/graph_data/<int:eq_id>')
def graph_data(eq_id):
    if eq_id >= len(linear_equations):
        return jsonify({"error": "Equation not found"}), 404

    eq = linear_equations[eq_id]
    eq_data = get_equation_data(eq)

    constant = eq_data.get('constant', 0)
    coefficient = eq_data.get('coefficient', 0)
    solution = eq_data.get('solution', 0)

    x_vals = list(range(-10, 11))
    y_vals = [coefficient * x + constant for x in x_vals]

    return jsonify({
        "x_values": x_vals,
        "y_values": y_vals,
        "solution": solution
    })
