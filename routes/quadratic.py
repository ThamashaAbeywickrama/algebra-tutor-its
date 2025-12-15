from flask import Blueprint, render_template, request, jsonify, session
from utils.ontology_loader import get_quadratic_equations, get_equation_data, get_hints
from utils.hint_personalizer import get_hint_for_performance
import time


bp = Blueprint('quadratic', __name__, url_prefix='/quadratic')

quadratic_equations = get_quadratic_equations()

# Step definitions - 6 clear steps
STEPS = [
    {"id": 1, "instruction": "Step 1: Identify the coefficients. What are a, b, and c?",
        "input_type": "three_numbers"},
    {"id": 2,
        "instruction": "Step 2: Calculate a × c (the AC product).", "input_type": "number"},
    {"id": 3, "instruction": "Step 3: Find two numbers that multiply to ac AND add to b.",
        "input_type": "two_numbers"},
    {"id": 4, "instruction": "Step 4: Rewrite the equation with common factors.",
        "input_type": "text"},
    {"id": 5, "instruction": "Step 5: Rewrite the equation in factored form.",
        "input_type": "text"},
    {"id": 6, "instruction": "Step 6: What are the values of x?",
        "input_type": "two_numbers"},
]


@bp.route('/dashboard')
def dashboard():
    return render_template('quadratic_dashboard.html', student_name=session.get('student_name', ''))


@bp.route('/equations')
def get_equations():
    progress = session.get('quadratic_progress', {})
    equation_list = []

    for i, eq in enumerate(quadratic_equations):
        eq_data = get_equation_data(eq)
        equation_list.append({
            "id": i,
            "expression": eq_data['expression'],
            "status": progress.get(f"Equation{i+1}", {}).get("status", "locked" if i > 0 else "unlocked"),
            "attempts": progress.get(f"Equation{i+1}", {}).get("attempts", 0),
            "time": progress.get(f"Equation{i+1}", {}).get("time", 0)
        })

    return jsonify({"equations": equation_list})


@bp.route('/equation/<int:eq_id>')
def get_equation(eq_id):
    if eq_id >= len(quadratic_equations):
        return jsonify({"error": "Equation not found"}), 404

    eq = quadratic_equations[eq_id]
    eq_data = get_equation_data(eq)

    session['current_equation'] = eq_id
    session['current_type'] = 'quadratic'
    session['current_step'] = 1
    session['step_attempts'] = 0
    session['start_time'] = time.time()

    # Clear previous work
    session.pop('a', None)
    session.pop('b', None)
    session.pop('c', None)
    session.pop('ac_product', None)
    session.pop('factor1', None)
    session.pop('factor2', None)
    session.pop('rewritten_eq', None)
    session.pop('factored_eq', None)

    # Store step expressions from ontology
    session['step4_expression'] = eq_data.get('step4_expression', '')
    session['step5_expression'] = eq_data.get('step5_expression', '')
    session['step6_expression'] = eq_data.get('step6_expression', '')

    return jsonify({
        "id": eq_id,
        "type": "quadratic",
        "expression": eq_data['expression'],
        "current_step": STEPS[0],
        "total_steps": len(STEPS),
        "step4_expression": eq_data.get('step4_expression', ''),
        "step5_expression": eq_data.get('step5_expression', ''),
        "step6_expression": eq_data.get('step6_expression', '')
    })


@bp.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    eq_id = session.get('current_equation', 0)
    current_step = session.get('current_step', 1)
    step_attempts = session.get('step_attempts', 0)

    eq = quadratic_equations[eq_id]
    eq_data = get_equation_data(eq)

    a = eq_data.get('a_coefficient', 1)
    b = eq_data.get('b_coefficient', 0)
    c = eq_data.get('c_coefficient', 0)
    ac_product = a * c
    solution1 = eq_data.get('solution1', 0)
    solution2 = eq_data.get('solution2', 0)

    step_attempts += 1
    session['step_attempts'] = step_attempts

    # Get hint after 3 attempts with performance personalization
    hint = None
    if step_attempts >= 3:
        performance_level = session.get('performance_level', 'moderate')
        hints = get_hints(eq)

        # Get adaptive hint based on current step and performance level
        hint = get_hint_for_performance(
            hints, performance_level, 'quadratic', current_step - 1)
        session['step_attempts'] = 0

    # Step 1: Identify a, b, c
    if current_step == 1:
        try:
            user_a = float(data.get('a', 0))
            user_b = float(data.get('b', 0))
            user_c = float(data.get('c', 0))

            if user_a == a and user_b == b and user_c == c:
                session['current_step'] = 2
                session['step_attempts'] = 0
                session['a'] = int(a)
                session['b'] = int(b)
                session['c'] = int(c)
                return jsonify({
                    "success": True,
                    "correct": True,
                    "message": f"Correct! a = {int(a)}, b = {int(b)}, c = {int(c)}",
                    "next_step": STEPS[1],
                    "progress": 17
                })
            else:
                return jsonify({
                    "success": True,
                    "correct": False,
                    "message": "Not quite. Match with ax² + bx + c.",
                    "hint": hint or "The coefficient of x² is a, the coefficient of x is b, and the constant is c."
                })
        except:
            return jsonify({"success": False, "message": "Please enter valid numbers"})

    # Step 2: Calculate a × c
    elif current_step == 2:
        try:
            user_ac = float(data.get('answer', 0))
            if user_ac == ac_product:
                session['current_step'] = 3
                session['step_attempts'] = 0
                session['ac_product'] = int(ac_product)
                return jsonify({
                    "success": True,
                    "correct": True,
                    "message": f"Correct! a × c = {int(ac_product)}",
                    "next_step": STEPS[2],
                    "progress": 34
                })
            else:
                return jsonify({
                    "success": True,
                    "correct": False,
                    "message": "Incorrect. Try again!",
                    "hint": hint or f"Multiply a ({int(a)}) by c ({int(c)})."
                })
        except:
            return jsonify({"success": False, "message": "Please enter a valid number"})

    # Step 3: Find two numbers that multiply to ac and add to b
    elif current_step == 3:
        try:
            num1 = float(data.get('num1', 0))
            num2 = float(data.get('num2', 0))

            # Check if they multiply to ac and add to b
            if (num1 * num2 == ac_product and num1 + num2 == b):
                session['factor1'] = int(num1)
                session['factor2'] = int(num2)
                session['current_step'] = 4
                session['step_attempts'] = 0
                return jsonify({
                    "success": True,
                    "correct": True,
                    "message": f"Excellent! {int(num1)} × {int(num2)} = {int(ac_product)} and {int(num1)} + {int(num2)} = {int(b)}",
                    "next_step": STEPS[3],
                    "progress": 51
                })
            else:
                return jsonify({
                    "success": True,
                    "correct": False,
                    "message": "These numbers don't work. Try again!",
                    "hint": hint or f"Find two numbers that multiply to {int(ac_product)} and add to {int(b)}."
                })
        except:
            return jsonify({"success": False, "message": "Please enter valid numbers"})

    # Step 4: Rewrite equation with common factors
    elif current_step == 4:
        answer = data.get('answer', '').strip()
        if answer:
            session['rewritten_eq'] = answer
            session['current_step'] = 5
            session['step_attempts'] = 0
            return jsonify({
                "success": True,
                "correct": True,
                "message": "Good! Now write the factored form.",
                "next_step": STEPS[4],
                "progress": 68
            })
        else:
            return jsonify({
                "success": True,
                "correct": False,
                "message": "Please enter your rewritten equation.",
                "hint": hint or f"Split the middle term using {session.get('factor1')} and {session.get('factor2')}."
            })

    # Step 5: Write factored form
    elif current_step == 5:
        answer = data.get('answer', '').strip()
        if answer:
            session['factored_eq'] = answer
            session['current_step'] = 6
            session['step_attempts'] = 0
            return jsonify({
                "success": True,
                "correct": True,
                "message": "Great! Now find the values of x.",
                "next_step": STEPS[5],
                "progress": 85
            })
        else:
            return jsonify({
                "success": True,
                "correct": False,
                "message": "Please enter your factored form.",
                "hint": hint or "Factor out common terms from each group."
            })

    # Step 6: Final solutions
    elif current_step == 6:
        try:
            sol1 = float(data.get('sol1', 0))
            sol2 = float(data.get('sol2', 0))

            correct_sols = sorted([solution1, solution2])
            user_sols = sorted([sol1, sol2])

            if user_sols == correct_sols:
                time_taken = round(
                    time.time() - session.get('start_time', time.time()), 2)

                progress = session.get('quadratic_progress', {})
                progress[f"Equation{eq_id+1}"] = {
                    "status": "completed",
                    "attempts": progress.get(f"Equation{eq_id+1}", {}).get("attempts", 0) + 1,
                    "time": time_taken
                }

                if eq_id + 1 < len(quadratic_equations):
                    progress[f"Equation{eq_id+2}"] = {"status": "unlocked",
                                                      "attempts": 0, "time": 0}

                session['quadratic_progress'] = progress

                return jsonify({
                    "success": True,
                    "correct": True,
                    "message": f"🎉 Perfect! The solutions are x = {solution1} and x = {solution2}",
                    "completed": True,
                    "time": time_taken,
                    "progress": 100
                })
            else:
                return jsonify({
                    "success": True,
                    "correct": False,
                    "message": "Not quite right. Check your work.",
                    "hint": hint or "Set each factor equal to 0 and solve."
                })
        except:
            return jsonify({"success": False, "message": "Please enter valid numbers"})


@bp.route('/hint')
def get_hint():
    current_step = session.get('current_step', 1)
    eq_id = session.get('current_equation', 0)
    performance_level = session.get('performance_level', 'moderate')

    if eq_id >= len(quadratic_equations):
        return jsonify({
            "hint": "Try working through the steps carefully!",
            "source": "Default"
        })

    eq = quadratic_equations[eq_id]
    hints = get_hints(eq)

    # Get personalized hint based on performance level
    hint = get_hint_for_performance(
        hints, performance_level, 'quadratic', current_step - 1)

    return jsonify({
        "hint": hint,
        "source": "Personalized for your level"
    })


@bp.route('/graph_data/<int:eq_id>')
def graph_data(eq_id):
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
