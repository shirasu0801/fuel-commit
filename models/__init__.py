from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.food import Food
from models.meal import Meal, MealItem
