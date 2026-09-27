from storage import store
from tools.base import Tool
from tools.nutrition_data import FOOD_TABLE


class EditMealEntryTool(Tool):
    name = "edit_meal_entry"
    description = (
        "修改今天摄入记录里某一条的克重（比如手滑记错了数字），会按新克重重新算营养值。"
        '序号从 get_daily_summary 的列表里看。参数：{"index": 序号数字, "grams": 新的克重数字}'
    )

    def run(self, index: int, grams: float) -> str:
        entries = store.get_intake()
        index = int(index)
        if index < 1 or index > len(entries):
            return f"没有找到第{index}条记录，今天可能没有这么多条，先用 get_daily_summary 看一下序号。"

        entry = entries[index - 1]
        food = entry["food"]
        info = FOOD_TABLE.get(food)
        if info is None:
            return f"「{food}」不在数据表中，没法重新计算营养值，建议直接用 delete_meal_entry 删除后重新记录。"

        grams = float(grams)
        new_entry = {
            "food": food,
            "grams": grams,
            "protein": round(info["protein"] * grams / 100, 1),
            "carbs": round(info["carbs"] * grams / 100, 1),
            "fat": round(info["fat"] * grams / 100, 1),
            "calories": round(info["calories"] * grams / 100, 1),
            "time": entry.get("time", ""),
        }
        store.update_intake(index, new_entry)
        return (
            f"已把第{index}条记录改成：{grams}克{food}，"
            f"约{new_entry['protein']}克蛋白质、{new_entry['carbs']}克碳水、{new_entry['fat']}克脂肪、{new_entry['calories']:.0f}千卡。"
        )
