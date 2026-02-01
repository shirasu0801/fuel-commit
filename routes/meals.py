from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.meal import Meal, MealItem
from models.food import Food

meals_bp = Blueprint('meals', __name__, url_prefix='/meals')


@meals_bp.route('/')
@login_required
def index():
    selected_date = request.args.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    meals = Meal.query.filter_by(
        user_id=current_user.id,
        date=selected_date
    ).order_by(Meal.meal_type).all()

    # 日の合計栄養素を計算
    daily_totals = {
        'calories': 0,
        'protein': 0,
        'fat': 0,
        'carbs': 0,
        'fiber': 0,
        'sodium': 0
    }

    for meal in meals:
        nutrition = meal.get_total_nutrition()
        for key in daily_totals:
            daily_totals[key] += nutrition[key]

    for key in daily_totals:
        daily_totals[key] = round(daily_totals[key], 1)

    return render_template('meals/index.html',
                           meals=meals,
                           selected_date=selected_date,
                           daily_totals=daily_totals)


@meals_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        meal_date = request.form.get('date')
        meal_type = request.form.get('meal_type')
        food_ids = request.form.getlist('food_id[]')
        quantities = request.form.getlist('quantity[]')

        if not meal_date or not meal_type:
            flash('日付と食事タイプを選択してください', 'error')
            return redirect(url_for('meals.add'))

        if not food_ids or not quantities:
            flash('食品を1つ以上追加してください', 'error')
            return redirect(url_for('meals.add'))

        try:
            meal_date = datetime.strptime(meal_date, '%Y-%m-%d').date()
        except ValueError:
            flash('日付の形式が正しくありません', 'error')
            return redirect(url_for('meals.add'))

        meal = Meal(
            user_id=current_user.id,
            meal_type=meal_type,
            date=meal_date
        )
        db.session.add(meal)
        db.session.flush()

        for food_id, quantity in zip(food_ids, quantities):
            if food_id and quantity:
                item = MealItem(
                    meal_id=meal.id,
                    food_id=int(food_id),
                    quantity=float(quantity)
                )
                db.session.add(item)

        db.session.commit()
        flash('食事を記録しました', 'success')
        return redirect(url_for('meals.index', date=meal_date.strftime('%Y-%m-%d')))

    foods = Food.query.order_by(Food.category, Food.name).all()
    return render_template('meals/add.html', foods=foods, today=date.today())


@meals_bp.route('/<int:meal_id>')
@login_required
def detail(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    return render_template('meals/detail.html', meal=meal)


@meals_bp.route('/<int:meal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        meal.meal_type = request.form.get('meal_type')
        meal_date = request.form.get('date')

        try:
            meal.date = datetime.strptime(meal_date, '%Y-%m-%d').date()
        except ValueError:
            flash('日付の形式が正しくありません', 'error')
            return redirect(url_for('meals.edit', meal_id=meal_id))

        # 既存のアイテムを削除
        MealItem.query.filter_by(meal_id=meal.id).delete()

        food_ids = request.form.getlist('food_id[]')
        quantities = request.form.getlist('quantity[]')

        for food_id, quantity in zip(food_ids, quantities):
            if food_id and quantity:
                item = MealItem(
                    meal_id=meal.id,
                    food_id=int(food_id),
                    quantity=float(quantity)
                )
                db.session.add(item)

        db.session.commit()
        flash('食事を更新しました', 'success')
        return redirect(url_for('meals.detail', meal_id=meal_id))

    foods = Food.query.order_by(Food.category, Food.name).all()
    return render_template('meals/edit.html', meal=meal, foods=foods)


@meals_bp.route('/<int:meal_id>/delete', methods=['POST'])
@login_required
def delete(meal_id):
    meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first_or_404()
    meal_date = meal.date
    db.session.delete(meal)
    db.session.commit()
    flash('食事を削除しました', 'success')
    return redirect(url_for('meals.index', date=meal_date.strftime('%Y-%m-%d')))


@meals_bp.route('/api/foods/search')
@login_required
def search_foods():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    foods = Food.query.filter(Food.name.contains(query)).limit(20).all()
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'calories': f.calories,
        'protein': f.protein,
        'fat': f.fat,
        'carbs': f.carbs,
        'category': f.category
    } for f in foods])
