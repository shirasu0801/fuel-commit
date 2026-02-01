from models import db


class Food(db.Model):
    __tablename__ = 'foods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    calories = db.Column(db.Float, nullable=False)  # kcal/100g
    protein = db.Column(db.Float, nullable=False)   # g/100g
    fat = db.Column(db.Float, nullable=False)       # g/100g
    carbs = db.Column(db.Float, nullable=False)     # g/100g
    fiber = db.Column(db.Float, default=0)          # g/100g
    sodium = db.Column(db.Float, default=0)         # mg/100g
    category = db.Column(db.String(50), nullable=True)

    meal_items = db.relationship('MealItem', backref='food', lazy='dynamic')

    def get_nutrition_for_quantity(self, quantity):
        """指定量(g)の栄養素を計算"""
        ratio = quantity / 100.0
        return {
            'calories': round(self.calories * ratio, 1),
            'protein': round(self.protein * ratio, 1),
            'fat': round(self.fat * ratio, 1),
            'carbs': round(self.carbs * ratio, 1),
            'fiber': round(self.fiber * ratio, 1),
            'sodium': round(self.sodium * ratio, 1)
        }

    def __repr__(self):
        return f'<Food {self.name}>'
