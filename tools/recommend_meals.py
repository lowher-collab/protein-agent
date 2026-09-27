from datetime import datetime

from storage import store
from tools.base import Tool
from tools.nutrition_data import FOOD_TABLE

# (餐次名, 开始小时, 结束小时) —— 用当前时间判断今天还剩哪几顿可以安排。
MEAL_SLOTS = [("早餐", 0, 10), ("午餐", 10, 16), ("晚餐", 16, 24)]

BREAKFAST_CHOICES = ["鸡蛋", "希腊酸奶", "牛奶"]
MAIN_MEAL_CHOICES = ["鸡胸肉", "三文鱼", "虾", "豆腐", "牛肉", "鸡腿肉", "金枪鱼", "猪肉"]

MIN_GRAMS, MAX_GRAMS = 30, 350


def _pick_food(meal_name: str, index: int) -> str:
    if meal_name == "早餐":
        return BREAKFAST_CHOICES[index % len(BREAKFAST_CHOICES)]
    return MAIN_MEAL_CHOICES[index % len(MAIN_MEAL_CHOICES)]


class RecommendMealsTool(Tool):
    name = "recommend_meals"
    description = (
        "根据今天还差多少蛋白质和热量，结合当前时间判断今天剩下的几顿饭（早餐/午餐/晚餐），"
        "给出具体的食物和克重建议，帮用户规划怎么吃能刚好达标。不需要参数。参数：{}"
    )

    def run(self) -> str:
        profile = store.get_profile()
        if not profile:
            return "还没有设置用户资料，无法计算目标，请先用 set_user_profile 设置。"

        entries = store.get_intake()
        total_protein = sum(e["protein"] for e in entries)
        total_calories = sum(e["calories"] for e in entries)
        protein_remaining = profile["protein_target"] - total_protein
        calories_remaining = profile["calorie_target"] - total_calories

        if protein_remaining <= 0:
            return (
                f"蛋白质目标已经达成（今日累计{total_protein:.1f}克 / 目标{profile['protein_target']}克），"
                "不需要再额外安排了。"
            )

        current_hour = datetime.now().hour
        remaining_slots = [name for name, start, end in MEAL_SLOTS if current_hour < end]
        if not remaining_slots:
            remaining_slots = ["晚餐"]

        per_slot_protein = protein_remaining / len(remaining_slots)
        per_slot_calories = max(calories_remaining, 0) / len(remaining_slots)

        lines = [
            f"今日还差{protein_remaining:.1f}克蛋白质、{calories_remaining:.0f}千卡热量，"
            f"按剩下的{'、'.join(remaining_slots)}分配："
        ]

        for i, meal_name in enumerate(remaining_slots):
            food = _pick_food(meal_name, i)
            info = FOOD_TABLE[food]

            grams = per_slot_protein / info["protein"] * 100
            grams = max(MIN_GRAMS, min(MAX_GRAMS, round(grams / 10) * 10))

            protein = info["protein"] * grams / 100
            carbs = info["carbs"] * grams / 100
            fat = info["fat"] * grams / 100
            calories = info["calories"] * grams / 100
            lines.append(
                f"{meal_name}：建议吃 {grams:.0f}克{food}，约{protein:.1f}克蛋白质、{carbs:.1f}克碳水、"
                f"{fat:.1f}克脂肪、{calories:.0f}千卡（目标约{per_slot_protein:.1f}克蛋白质、{per_slot_calories:.0f}千卡）"
            )

        if calories_remaining < 0:
            lines.append("提醒：今天的热量已经超过目标了，如果还要补蛋白质，尽量选脂肪少的瘦肉、海鲜或蛋白粉。")

        return "\n".join(lines)
