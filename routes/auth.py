
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from utils.ontology_loader import get_linear_equations, get_quadratic_equations

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    return render_template('login.html')


@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    session['student_name'] = data.get('name', '')
    session['quiz_completed'] = False  # Track if quiz is done
    session['performance_level'] = None  # Will be set after quiz

    return jsonify({"success": True})


@bp.route('/quiz')
def quiz():
    if session.get('quiz_completed'):
        return redirect(url_for('auth.home'))
    return render_template('diagnostic_quiz.html', student_name=session.get('student_name', ''))


@bp.route('/home')
def home():
    if not session.get('quiz_completed'):
        return redirect(url_for('auth.quiz'))

    return render_template('home.html',
                           student_name=session.get('student_name', ''),
                           performance_level=session.get('performance_level', 'moderate'))
