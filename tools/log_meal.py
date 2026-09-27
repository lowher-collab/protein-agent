from datetime import datetime

from storage import store
from tools.base import Tool
from tools.nutrition_data import FOOD_TABLE


class LogMealTool(Tool):
    name = "log_meal"
    description = (
        "记录用户吃下的一份食物到今日摄入记录，并返回今日累计摄入（蛋白质/碳水/脂肪/热量）和距离目标还差多少。"
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

        store.append_intake({
            "food": food,
            "grams": grams,
            "protein": round(protein, 1),
            "carbs": round(carbs, 1),
            "fat": round(fat, 1),
            "calories": round(calories, 1),
            "time": datetime.now().strftime("%H:%M"),
        })

        # 用 .get(..., 0) 兼容加碳水/脂肪字段之前记录的旧数据，避免缺字段报错。
        today_entries = store.get_intake()
        total_protein = sum(e["protein"] for e in today_entries)
        total_carbs = sum(e.get("carbs", 0) for e in today_entries)
        total_fat = sum(e.get("fat", 0) for e in today_entries)
        total_calories = sum(e["calories"] for e in today_entries)

        result = (
            f"已记录：{grams}克{food}，约{protein:.1f}克蛋白质、{carbs:.1f}克碳水、{fat:.1f}克脂肪、{calories:.0f}千卡。"
            f"今日累计蛋白质{total_protein:.1f}克、碳水{total_carbs:.1f}克、脂肪{total_fat:.1f}克，热量{total_calories:.0f}千卡。"
        )

        profile = store.get_profile()
        if profile:
            protein_left = profile["protein_target"] - total_protein
            carb_left = profile["carb_target"] - total_carbs
            fat_left = profile["fat_target"] - total_fat
            calories_left = profile["calorie_target"] - total_calories
            result += (
                f" 距离目标还差：蛋白质{max(protein_left, 0):.1f}克、碳水{max(carb_left, 0):.1f}克、"
                f"脂肪{max(fat_left, 0):.1f}克；热量缺口还剩{calories_left:.0f}千卡。"
            )
        else:
            result += " （还没有设置用户资料，无法计算距离目标的差距，可以先用 set_user_profile 设置。）"

        return result
