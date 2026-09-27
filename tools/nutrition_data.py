# 每 100 克食物的蛋白质/碳水/脂肪(克)和热量(千卡)，为常见参考值，非精确测量。
FOOD_TABLE = {
    # 肉禽蛋
    "鸡蛋": {"protein": 13, "carbs": 1.1, "fat": 10, "calories": 143},
    "蛋清": {"protein": 11, "carbs": 0.7, "fat": 0.2, "calories": 52},
    "鸡胸肉": {"protein": 31, "carbs": 0, "fat": 3.6, "calories": 165},
    "鸡腿肉": {"protein": 18, "carbs": 0, "fat": 11, "calories": 181},
    "鸡翅": {"protein": 19, "carbs": 0, "fat": 15, "calories": 220},
    "鸭肉": {"protein": 20, "carbs": 0, "fat": 19, "calories": 240},
    "牛肉": {"protein": 26, "carbs": 0, "fat": 15, "calories": 250},
    "猪肉": {"protein": 20, "carbs": 0, "fat": 18, "calories": 242},
    "羊肉": {"protein": 19, "carbs": 0, "fat": 13, "calories": 203},
    "培根": {"protein": 30, "carbs": 1.4, "fat": 42, "calories": 500},
    "火腿": {"protein": 17, "carbs": 1.5, "fat": 7, "calories": 145},
    "午餐肉": {"protein": 12, "carbs": 2, "fat": 27, "calories": 300},
    "香肠": {"protein": 14, "carbs": 3, "fat": 26, "calories": 300},

    # 水产
    "三文鱼": {"protein": 20, "carbs": 0, "fat": 13, "calories": 208},
    "虾": {"protein": 24, "carbs": 0.2, "fat": 1.7, "calories": 106},
    "金枪鱼": {"protein": 26, "carbs": 0, "fat": 1.3, "calories": 132},
    "鳕鱼": {"protein": 18, "carbs": 0, "fat": 0.7, "calories": 82},
    "鱿鱼": {"protein": 18, "carbs": 3, "fat": 1.4, "calories": 92},
    "螃蟹": {"protein": 18, "carbs": 0, "fat": 1, "calories": 95},

    # 奶制品
    "牛奶": {"protein": 3.4, "carbs": 4.8, "fat": 3.2, "calories": 54},
    "脱脂牛奶": {"protein": 3.4, "carbs": 5, "fat": 0.1, "calories": 34},
    "酸奶": {"protein": 3.5, "carbs": 4.7, "fat": 3.3, "calories": 60},
    "希腊酸奶": {"protein": 10, "carbs": 3.6, "fat": 0.4, "calories": 59},
    "奶酪": {"protein": 25, "carbs": 1.3, "fat": 28, "calories": 350},

    # 豆制品/蛋白粉
    "豆腐": {"protein": 8, "carbs": 1.9, "fat": 4.2, "calories": 76},
    "豆浆": {"protein": 3, "carbs": 1.8, "fat": 1.6, "calories": 31},
    "黄豆": {"protein": 35, "carbs": 34, "fat": 16, "calories": 390},
    "黑豆": {"protein": 21, "carbs": 62, "fat": 1.6, "calories": 341},
    "毛豆": {"protein": 13, "carbs": 10, "fat": 5, "calories": 121},
    "腐竹": {"protein": 44, "carbs": 22, "fat": 21, "calories": 461},
    "鹰嘴豆": {"protein": 9, "carbs": 27, "fat": 2.6, "calories": 164},
    "蛋白粉": {"protein": 80, "carbs": 6, "fat": 4, "calories": 380},

    # 主食
    "米饭": {"protein": 2.6, "carbs": 28, "fat": 0.3, "calories": 130},
    "面条": {"protein": 5.3, "carbs": 25, "fat": 1.1, "calories": 138},
    "馒头": {"protein": 7, "carbs": 47, "fat": 1.1, "calories": 223},
    "全麦面包": {"protein": 9, "carbs": 41, "fat": 3.4, "calories": 247},
    "燕麦": {"protein": 13, "carbs": 66, "fat": 7, "calories": 389},
    "红薯": {"protein": 1.6, "carbs": 20, "fat": 0.1, "calories": 86},
    "土豆": {"protein": 2, "carbs": 17, "fat": 0.1, "calories": 77},
    "玉米": {"protein": 3.3, "carbs": 21, "fat": 1.5, "calories": 96},

    # 坚果
    "花生": {"protein": 25, "carbs": 16, "fat": 49, "calories": 567},
    "杏仁": {"protein": 21, "carbs": 22, "fat": 50, "calories": 579},
    "核桃": {"protein": 15, "carbs": 14, "fat": 65, "calories": 654},

    # 蔬菜水果
    "西兰花": {"protein": 2.8, "carbs": 7, "fat": 0.4, "calories": 34},
    "菠菜": {"protein": 2.9, "carbs": 3.6, "fat": 0.4, "calories": 23},
    "黄瓜": {"protein": 0.7, "carbs": 3.6, "fat": 0.1, "calories": 15},
    "番茄": {"protein": 0.9, "carbs": 3.9, "fat": 0.2, "calories": 18},
    "香蕉": {"protein": 1.1, "carbs": 23, "fat": 0.3, "calories": 89},
    "苹果": {"protein": 0.3, "carbs": 14, "fat": 0.2, "calories": 52},

    # 家常成品菜（复合菜品，肉/菜/油/酱汁混在一起，数值是整道菜的平均估算，
    # 比单一食材的误差更大——同一道菜不同人做法差别很大，仅供大致参考）
    "宫保鸡丁": {"protein": 13, "carbs": 10, "fat": 10, "calories": 180},
    "鱼香肉丝": {"protein": 10, "carbs": 12, "fat": 10, "calories": 170},
    "麻婆豆腐": {"protein": 7, "carbs": 5, "fat": 8, "calories": 120},
    "红烧肉": {"protein": 9, "carbs": 6, "fat": 25, "calories": 280},
    "糖醋里脊": {"protein": 11, "carbs": 20, "fat": 10, "calories": 220},
    "清蒸鲈鱼": {"protein": 18, "carbs": 1, "fat": 3, "calories": 110},
    "水煮鱼": {"protein": 13, "carbs": 4, "fat": 13, "calories": 180},
    "回锅肉": {"protein": 12, "carbs": 6, "fat": 22, "calories": 260},
    "番茄炒蛋": {"protein": 6, "carbs": 4, "fat": 6, "calories": 90},
    "青椒肉丝": {"protein": 9, "carbs": 6, "fat": 9, "calories": 140},
    "酸菜鱼": {"protein": 13, "carbs": 3, "fat": 7, "calories": 140},
    "白灼虾": {"protein": 20, "carbs": 1, "fat": 1.5, "calories": 100},
    "蒸蛋羹": {"protein": 7, "carbs": 2, "fat": 5, "calories": 80},
    "小笼包": {"protein": 9, "carbs": 25, "fat": 9, "calories": 220},
    "海鲜粥": {"protein": 4, "carbs": 12, "fat": 1, "calories": 70},
    "蛋炒饭": {"protein": 6, "carbs": 25, "fat": 6, "calories": 180},
    "麻辣香锅": {"protein": 10, "carbs": 8, "fat": 14, "calories": 200},
    "鲜肉水饺": {"protein": 9, "carbs": 25, "fat": 7, "calories": 200},
    "胡萝卜炒黑木耳": {"protein": 2, "carbs": 8, "fat": 5, "calories": 80},
}
