from flask import Flask
from routes import auth, linear, quadratic, progress, quiz

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(linear.bp)
app.register_blueprint(quadratic.bp)
app.register_blueprint(progress.bp)
app.register_blueprint(quiz.bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
