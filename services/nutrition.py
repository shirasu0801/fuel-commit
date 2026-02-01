from datetime import timedelta
from models.meal import Meal


class NutritionService:
    """栄養計算サービス"""

    # 推奨摂取量（成人の目安）
    RECOMMENDED = {
        'protein': 60,      # g
        'fat': 60,          # g
        'carbs': 300,       # g
        'fiber': 20,        # g
        'sodium': 2000,     # mg
    }

    # PFC理想バランス
    IDEAL_PFC = {
        'protein': 0.15,    # 15%
        'fat': 0.25,        # 25%
        'carbs': 0.60       # 60%
    }

    def __init__(self, user):
        self.user = user

    def get_daily_nutrition(self, target_date):
        """指定日の合計栄養素を取得"""
        meals = Meal.query.filter_by(
            user_id=self.user.id,
            date=target_date
        ).all()

        totals = {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
            'fiber': 0,
            'sodium': 0
        }

        for meal in meals:
            nutrition = meal.get_total_nutrition()
            for key in totals:
                totals[key] += nutrition[key]

        for key in totals:
            totals[key] = round(totals[key], 1)

        return totals

    def get_weekly_calories(self, end_date):
        """1週間のカロリー推移を取得"""
        data = []
        for i in range(6, -1, -1):
            target_date = end_date - timedelta(days=i)
            nutrition = self.get_daily_nutrition(target_date)
            data.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'label': target_date.strftime('%m/%d'),
                'calories': nutrition['calories']
            })
        return data

    def calculate_pfc_balance(self, nutrition):
        """PFCバランスを計算"""
        protein_cal = nutrition['protein'] * 4  # 1g = 4kcal
        fat_cal = nutrition['fat'] * 9          # 1g = 9kcal
        carbs_cal = nutrition['carbs'] * 4      # 1g = 4kcal

        total_cal = protein_cal + fat_cal + carbs_cal

        if total_cal == 0:
            return {
                'protein': {'grams': 0, 'percentage': 0},
                'fat': {'grams': 0, 'percentage': 0},
                'carbs': {'grams': 0, 'percentage': 0}
            }

        return {
            'protein': {
                'grams': nutrition['protein'],
                'percentage': round(protein_cal / total_cal * 100, 1)
            },
            'fat': {
                'grams': nutrition['fat'],
                'percentage': round(fat_cal / total_cal * 100, 1)
            },
            'carbs': {
                'grams': nutrition['carbs'],
                'percentage': round(carbs_cal / total_cal * 100, 1)
            }
        }

    def get_nutrition_warnings(self, nutrition):
        """不足栄養素の警告を生成"""
        warnings = []
        tdee = self.user.calculate_tdee()

        # カロリー不足/過剰
        if tdee:
            if nutrition['calories'] < tdee * 0.8:
                warnings.append({
                    'type': 'warning',
                    'message': f"カロリーが目標({tdee}kcal)の80%未満です"
                })
            elif nutrition['calories'] > tdee * 1.2:
                warnings.append({
                    'type': 'danger',
                    'message': f"カロリーが目標({tdee}kcal)の120%を超えています"
                })

        # タンパク質
        if nutrition['protein'] < self.RECOMMENDED['protein'] * 0.7:
            warnings.append({
                'type': 'warning',
                'message': f"タンパク質が不足しています（推奨: {self.RECOMMENDED['protein']}g以上）"
            })

        # 食物繊維
        if nutrition['fiber'] < self.RECOMMENDED['fiber'] * 0.7:
            warnings.append({
                'type': 'info',
                'message': f"食物繊維が不足気味です（推奨: {self.RECOMMENDED['fiber']}g以上）"
            })

        # ナトリウム過剰
        if nutrition['sodium'] > self.RECOMMENDED['sodium']:
            warnings.append({
                'type': 'warning',
                'message': f"ナトリウムが多めです（推奨: {self.RECOMMENDED['sodium']}mg以下）"
            })

        return warnings

    def calculate_target_calories(self):
        """目標体重達成に必要なカロリーを計算"""
        tdee = self.user.calculate_tdee()
        if not tdee or not self.user.target_weight or not self.user.current_weight:
            return None

        diff = self.user.current_weight - self.user.target_weight

        if diff > 0:
            # 減量：1日500kcal削減で週0.5kg減
            return round(tdee - 500, 0)
        elif diff < 0:
            # 増量：1日500kcal追加で週0.5kg増
            return round(tdee + 500, 0)
        else:
            return tdee
