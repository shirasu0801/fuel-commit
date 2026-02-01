from datetime import datetime, date
from models import db


class Meal(db.Model):
    __tablename__ = 'meals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('MealItem', backref='meal', lazy='dynamic', cascade='all, delete-orphan')

    MEAL_TYPES = {
        'breakfast': '朝食',
        'lunch': '昼食',
        'dinner': '夕食',
        'snack': '間食'
    }

    def get_meal_type_display(self):
        return self.MEAL_TYPES.get(self.meal_type, self.meal_type)

    def get_total_nutrition(self):
        """食事の合計栄養素を計算"""
        totals = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'fiber': 0,
            'sodium': 0
        }

        for item in self.items:
            nutrition = item.food.get_nutrition_for_quantity(item.quantity)
            for key in totals:
                totals[key] += nutrition[key]

        for key in totals:
            totals[key] = round(totals[key], 1)

        return totals

    def __repr__(self):
        return f'<Meal {self.date} {self.meal_type}>'


class MealItem(db.Model):
    __tablename__ = 'meal_items'

    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # グラム

    def get_nutrition(self):
        return self.food.get_nutrition_for_quantity(self.quantity)

    def __repr__(self):
        return f'<MealItem {self.food.name} {self.quantity}g>'
