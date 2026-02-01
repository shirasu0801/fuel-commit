from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    target_weight = db.Column(db.Float, nullable=True)
    current_weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    activity_level = db.Column(db.Float, default=1.2)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    meals = db.relationship('Meal', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_bmr(self):
        """Harris-Benedict式で基礎代謝量を計算"""
        if not all([self.current_weight, self.height, self.age, self.gender]):
            return None

        if self.gender == 'male':
            bmr = 88.362 + (13.397 * self.current_weight) + (4.799 * self.height) - (5.677 * self.age)
        else:
            bmr = 447.593 + (9.247 * self.current_weight) + (3.098 * self.height) - (4.330 * self.age)

        return round(bmr, 1)

    def calculate_tdee(self):
        """1日の総消費カロリー(TDEE)を計算"""
        bmr = self.calculate_bmr()
        if bmr is None:
            return None
        return round(bmr * self.activity_level, 1)

    def __repr__(self):
        return f'<User {self.email}>'
