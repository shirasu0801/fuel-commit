import os
import json
from datetime import timedelta
from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
from models import db
from models.user import User
from models.food import Food
from routes import register_blueprints


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初期化
    db.init_app(app)

    # Flask-Login設定
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'ログインが必要です'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprintを登録
    register_blueprints(app)

    # ルートURLをダッシュボードにリダイレクト
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    # テンプレートにtimedeltaを渡す
    @app.context_processor
    def utility_processor():
        from datetime import date, timedelta
        return dict(timedelta=timedelta, today=date.today())

    # データベース初期化
    with app.app_context():
        db.create_all()
        init_foods_data()

    return app


def init_foods_data():
    """食品マスタデータを初期化"""
    if Food.query.count() == 0:
        foods_file = os.path.join(os.path.dirname(__file__), 'data', 'foods.json')
        if os.path.exists(foods_file):
            with open(foods_file, 'r', encoding='utf-8') as f:
                foods_data = json.load(f)

            for food_data in foods_data:
                food = Food(
                    name=food_data['name'],
                    calories=food_data['calories'],
                    protein=food_data['protein'],
                    fat=food_data['fat'],
                    carbs=food_data['carbs'],
                    fiber=food_data.get('fiber', 0),
                    sodium=food_data.get('sodium', 0),
                    category=food_data.get('category')
                )
                db.session.add(food)

            db.session.commit()
            print(f'Loaded {len(foods_data)} foods into database')


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
