from django.apps import AppConfig

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection


class WebgoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'WEBGO'


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '470ec5fd9245344d8aca78527024a7cc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Создание таблицы для связи соответствия между географическим объектом и названием
class GeoObjectName(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    object_id = db.Column(db.Integer, db.ForeignKey('geography_object.id'), nullable=False)
    object = db.relationship('GeographyObject', backref='names')


# Класс для хранения информации о географических объектах
class GeographyObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    geo_json = db.Column(db.String(5000), nullable=False)


# Класс для хранения информации о викторинах
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='quizzes')
    questions = db.relationship('Question', backref='quiz', lazy=True)
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)


# Класс для хранения информации об ответах на задания в рамках викторины
class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    finished_at = db.Column(db.DateTime)


# Класс для хранения информации о заданиях в рамках викторины
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'map_choice', 'map_point', 'text_input'
    options_json = db.Column(db.String(5000), nullable=False)  # Список вариантов ответов в виде JSON
    correct_answer_json = db.Column(db.String(5000), nullable=False)  # Правильный ответ в виде JSON
    max_score = db.Column(db.Integer, nullable=False, default=10)  # Максимальное количество баллов за задание
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)


# Класс пользователей
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')


# Обработчик событий для активации внешних ключей перед использованием SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    quizzes = Quiz.query.all()
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.started_at.desc())
    return render_template('dashboard.html')
