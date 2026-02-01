from datetime import date, timedelta
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models.meal import Meal
from services.nutrition import NutritionService

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()
    nutrition_service = NutritionService(current_user)

    # 今日の栄養素
    daily_nutrition = nutrition_service.get_daily_nutrition(today)

    # 1週間のカロリー推移
    weekly_calories = nutrition_service.get_weekly_calories(today)

    # 目標カロリー
    tdee = current_user.calculate_tdee()

    # PFCバランス
    pfc_balance = nutrition_service.calculate_pfc_balance(daily_nutrition)

    # 不足栄養素の警告
    warnings = nutrition_service.get_nutrition_warnings(daily_nutrition)

    # 目標体重までの進捗
    weight_progress = None
    if current_user.current_weight and current_user.target_weight:
        diff = current_user.current_weight - current_user.target_weight
        weight_progress = {
            'current': current_user.current_weight,
            'target': current_user.target_weight,
            'difference': round(abs(diff), 1),
            'direction': 'lose' if diff > 0 else 'gain'
        }

    return render_template('dashboard/index.html',
                           daily_nutrition=daily_nutrition,
                           weekly_calories=weekly_calories,
                           tdee=tdee,
                           pfc_balance=pfc_balance,
                           warnings=warnings,
                           weight_progress=weight_progress,
                           today=today)


@dashboard_bp.route('/api/weekly-data')
@login_required
def weekly_data():
    end_date = request.args.get('end_date')
    if end_date:
        try:
            from datetime import datetime
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            end_date = date.today()
    else:
        end_date = date.today()

    nutrition_service = NutritionService(current_user)
    weekly_data = nutrition_service.get_weekly_calories(end_date)

    return jsonify(weekly_data)


@dashboard_bp.route('/api/daily-nutrition')
@login_required
def daily_nutrition():
    target_date = request.args.get('date')
    if target_date:
        try:
            from datetime import datetime
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()

    nutrition_service = NutritionService(current_user)
    nutrition = nutrition_service.get_daily_nutrition(target_date)
    pfc_balance = nutrition_service.calculate_pfc_balance(nutrition)

    return jsonify({
        'nutrition': nutrition,
        'pfc_balance': pfc_balance
    })
