from storage import store
from tools.base import Tool


class DeleteMealEntryTool(Tool):
    name = "delete_meal_entry"
    description = (
        "删除今天摄入记录里的某一条（比如记错了、重复记了）。序号从 get_daily_summary 的列表里看，"
        '1 表示今天第一条记录。参数：{"index": 序号数字}'
    )

    def run(self, index: int) -> str:
        removed = store.delete_intake(int(index))
        if removed is None:
            return f"没有找到第{index}条记录，今天可能没有这么多条，先用 get_daily_summary 看一下序号。"
        return f"已删除第{index}条记录：{removed['food']}{removed['grams']}克。"
