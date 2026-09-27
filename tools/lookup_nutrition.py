from tools.base import Tool
from tools.nutrition_data import FOOD_TABLE


class LookupNutritionTool(Tool):
    name = "lookup_nutrition"
    description = (
        "仅用于查询某种食物的蛋白质、碳水、脂肪和热量含量，不会记录进今日摄入（记录请用 log_meal）。"
        '参数：{"food": "食物名称", "grams": 克重数字}'
    )

    def run(self, food: str, grams: float) -> str:
        info = FOOD_TABLE.get(food)
        if info is None:
            known = "、".join(FOOD_TABLE.keys())
            return f"数据表中没有「{food}」，已知食物有：{known}"
        grams = float(grams)
        protein = info["protein"] * grams / 100
        carbs = info["carbs"] * grams / 100
        fat = info["fat"] * grams / 100
        calories = info["calories"] * grams / 100
        return (
            f"{grams}克{food}约含蛋白质{protein:.1f}克、碳水{carbs:.1f}克、脂肪{fat:.1f}克，"
            f"热量{calories:.0f}千卡"
        )
