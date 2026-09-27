from storage import store
from tools.base import Tool


class DailySummaryTool(Tool):
    name = "get_daily_summary"
    description = (
        "查询今天目前为止的摄入汇总（蛋白质/碳水/脂肪/热量）和距离目标的差距，"
        "每条记录带编号，配合 edit_meal_entry / delete_meal_entry 使用。不需要参数。参数：{}"
    )

    def run(self) -> str:
        entries = store.get_intake()
        if not entries:
            return "今天还没有记录任何食物。"

        total_protein = sum(e["protein"] for e in entries)
        total_carbs = sum(e.get("carbs", 0) for e in entries)
        total_fat = sum(e.get("fat", 0) for e in entries)
        total_calories = sum(e["calories"] for e in entries)
        food_list = "、".join(f"{i}.{e['food']}{e['grams']}克" for i, e in enumerate(entries, start=1))

        result = (
            f"今天已记录：{food_list}。累计蛋白质{total_protein:.1f}克、"
            f"碳水{total_carbs:.1f}克、脂肪{total_fat:.1f}克，热量{total_calories:.0f}千卡。"
        )

        profile = store.get_profile()
        if profile:
            protein_left = profile["protein_target"] - total_protein
            carb_left = profile["carb_target"] - total_carbs
            fat_left = profile["fat_target"] - total_fat
            calories_left = profile["calorie_target"] - total_calories
            result += (
                f" 蛋白质目标{profile['protein_target']}克，还差{max(protein_left, 0):.1f}克；"
                f"碳水目标{profile['carb_target']}克，还差{max(carb_left, 0):.1f}克；"
                f"脂肪目标{profile['fat_target']}克，还差{max(fat_left, 0):.1f}克；"
                f"热量目标{profile['calorie_target']}千卡，剩余缺口{calories_left:.0f}千卡。"
            )
        else:
            result += " 还没有设置用户资料，无法对比目标，可以先用 set_user_profile 设置。"

        return result
