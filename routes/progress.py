from flask import Blueprint, render_template, jsonify, session
from utils.ontology_loader import get_linear_equations, get_quadratic_equations

bp = Blueprint('progress', __name__, url_prefix='/progress')


@bp.route('/')
def index():
    return render_template('progress.html', student_name=session.get('student_name', ''))


@bp.route('/data')
def get_progress_data():
    linear_progress = session.get('linear_progress', {})
    quadratic_progress = session.get('quadratic_progress', {})
    student_name = session.get('student_name', '')

    # Calculate statistics for linear
    linear_completed = sum(
        1 for eq_data in linear_progress.values() if eq_data['status'] == 'completed')
    linear_total = len(linear_progress)
    linear_attempts = sum(eq_data['attempts']
                          for eq_data in linear_progress.values())
    linear_time = sum(eq_data['time'] for eq_data in linear_progress.values())

    # Calculate statistics for quadratic
    quadratic_completed = sum(
        1 for eq_data in quadratic_progress.values() if eq_data['status'] == 'completed')
    quadratic_total = len(quadratic_progress)
    quadratic_attempts = sum(eq_data['attempts']
                             for eq_data in quadratic_progress.values())
    quadratic_time = sum(eq_data['time']
                         for eq_data in quadratic_progress.values())

    # Combined statistics
    total_completed = linear_completed + quadratic_completed
    total_equations = linear_total + quadratic_total
    total_attempts = linear_attempts + quadratic_attempts
    total_time = linear_time + quadratic_time

    avg_attempts = round(total_attempts / total_completed,
                         1) if total_completed > 0 else 0
    avg_time = round(total_time / total_completed,
                     1) if total_completed > 0 else 0

    # Prepare chart data
    linear_equation_names = []
    linear_attempts_data = []
    linear_time_data = []

    for i in range(linear_total):
        eq_key = f"Equation{i+1}"
        if linear_progress[eq_key]['status'] == 'completed':
            linear_equation_names.append(f"L{i+1}")
            linear_attempts_data.append(linear_progress[eq_key]['attempts'])
            linear_time_data.append(linear_progress[eq_key]['time'])

    quadratic_equation_names = []
    quadratic_attempts_data = []
    quadratic_time_data = []

    for i in range(quadratic_total):
        eq_key = f"Equation{i+1}"
        if quadratic_progress[eq_key]['status'] == 'completed':
            quadratic_equation_names.append(f"Q{i+1}")
            quadratic_attempts_data.append(
                quadratic_progress[eq_key]['attempts'])
            quadratic_time_data.append(quadratic_progress[eq_key]['time'])

    # Calculate achievements
    achievements = []

    # Speed Solver
    all_progress = list(linear_progress.values()) + \
        list(quadratic_progress.values())
    speed_solver = any(eq_data['time'] > 0 and eq_data['time'] < 30 and eq_data['status'] == 'completed'
                       for eq_data in all_progress)
    if speed_solver:
        achievements.append({
            "icon": "⚡",
            "name": "Speed Solver",
            "description": "Solved an equation in under 30 seconds!"
        })

    # Perfect Score
    perfect_score = any(eq_data['attempts'] == 1 and eq_data['status'] == 'completed'
                        for eq_data in all_progress)
    if perfect_score:
        achievements.append({
            "icon": "🎯",
            "name": "Perfect Score",
            "description": "Solved an equation on the first try!"
        })

    # Linear Master
    if linear_completed == linear_total and linear_total > 0:
        achievements.append({
            "icon": "📐",
            "name": "Linear Master",
            "description": "Completed all linear equations!"
        })

    # Quadratic Champion
    if quadratic_completed == quadratic_total and quadratic_total > 0:
        achievements.append({
            "icon": "📊",
            "name": "Quadratic Champion",
            "description": "Completed all quadratic equations!"
        })

    # Algebra Expert
    if total_completed == total_equations and total_equations > 0:
        achievements.append({
            "icon": "🏆",
            "name": "Algebra Expert",
            "description": "Mastered both linear and quadratic equations!"
        })

    # Learning insights
    insights = []

    if total_completed >= 2:
        times = [eq_data['time'] for eq_data in all_progress if eq_data['status']
                 == 'completed' and eq_data['time'] > 0]
        if len(times) >= 2:
            first_half_avg = sum(times[:len(times)//2]) / (len(times)//2)
            second_half_avg = sum(
                times[len(times)//2:]) / (len(times) - len(times)//2)
            if second_half_avg < first_half_avg:
                improvement = round(
                    ((first_half_avg - second_half_avg) / first_half_avg) * 100)
                insights.append(
                    f"📈 You're getting faster! Your solving time improved by {improvement}%")

    if linear_completed > 0 and quadratic_completed > 0:
        linear_avg_time = linear_time / linear_completed
        quadratic_avg_time = quadratic_time / quadratic_completed
        if linear_avg_time < quadratic_avg_time:
            insights.append(
                f"💡 Linear equations are your strength! You solve them faster than quadratic ones.")
        else:
            insights.append(f"💡 You're excelling at quadratic equations!")

    if total_completed > 0:
        insights.append(
            f"✨ Great progress! You've completed {total_completed} out of {total_equations} equations")

    return jsonify({
        "student_name": student_name,
        "stats": {
            "completed": total_completed,
            "total": total_equations,
            "linear_completed": linear_completed,
            "linear_total": linear_total,
            "quadratic_completed": quadratic_completed,
            "quadratic_total": quadratic_total,
            "total_attempts": total_attempts,
            "total_time": round(total_time, 1),
            "avg_attempts": avg_attempts,
            "avg_time": avg_time,
            "accuracy": round((total_completed / total_equations) * 100) if total_equations > 0 else 0
        },
        "charts": {
            "linear": {
                "names": linear_equation_names,
                "attempts": linear_attempts_data,
                "times": linear_time_data
            },
            "quadratic": {
                "names": quadratic_equation_names,
                "attempts": quadratic_attempts_data,
                "times": quadratic_time_data
            }
        },
        "achievements": achievements,
        "insights": insights
    })
