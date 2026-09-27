from storage import store
from tools.base import Tool

ACTIVITY_FACTORS = {
    "久坐": 1.2,
    "轻度活动": 1.375,
    "中度活动": 1.55,
    "高强度活动": 1.725,
    "极高强度活动": 1.9,
}

# 减脂期提高蛋白质比例以保住肌肉，增肌期适度盈余热量，均为常见经验值，非医学建议。
GOAL_CALORIE_ADJUST = {"减脂": -500, "增肌": 300, "维持": 0}
GOAL_PROTEIN_PER_KG = {"减脂": 2.0, "增肌": 1.8, "维持": 1.4}

# 脂肪按热量目标的 25% 算（常见健康范围下限附近），碳水填满剩下的热量额度，
# 这样三项目标换算回热量正好等于热量目标，逻辑自洽。
FAT_CALORIE_RATIO = 0.25


class SetUserProfileTool(Tool):
    name = "set_user_profile"
    description = (
        "设置或更新用户的身体情况和目标，用于计算每日热量、蛋白质、碳水、脂肪目标。"
        '参数：{"gender": "男"或"女", "age": 年龄, "weight_kg": 体重公斤, '
        '"height_cm": 身高厘米, '
        '"activity_level": "久坐"|"轻度活动"|"中度活动"|"高强度活动"|"极高强度活动", '
        '"goal": "减脂"|"增肌"|"维持"}'
    )

    def run(self, gender: str, age: float, weight_kg: float, height_cm: float,
            activity_level: str, goal: str) -> str:
        if activity_level not in ACTIVITY_FACTORS:
            return f"activity_level 必须是：{'、'.join(ACTIVITY_FACTORS.keys())} 之一"
        if goal not in GOAL_CALORIE_ADJUST:
            return f"goal 必须是：{'、'.join(GOAL_CALORIE_ADJUST.keys())} 之一"

        if gender == "男":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        elif gender == "女":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        else:
            return "gender 必须是「男」或「女」"

        tdee = bmr * ACTIVITY_FACTORS[activity_level]
        calorie_target = tdee + GOAL_CALORIE_ADJUST[goal]
        protein_target = GOAL_PROTEIN_PER_KG[goal] * weight_kg

        fat_target = calorie_target * FAT_CALORIE_RATIO / 9
        remaining_calories = calorie_target - protein_target * 4 - fat_target * 9
        carb_target = max(remaining_calories, 0) / 4

        profile = {
            "gender": gender,
            "age": age,
            "weight_kg": weight_kg,
            "height_cm": height_cm,
            "activity_level": activity_level,
            "goal": goal,
            "calorie_target": round(calorie_target),
            "protein_target": round(protein_target, 1),
            "carb_target": round(carb_target, 1),
            "fat_target": round(fat_target, 1),
        }
        store.save_profile(profile)

        return (
            f"已保存用户资料。根据体重{weight_kg}kg、目标「{goal}」，每日目标：热量约{profile['calorie_target']}千卡，"
            f"蛋白质约{profile['protein_target']}克，碳水约{profile['carb_target']}克，脂肪约{profile['fat_target']}克。"
        )
