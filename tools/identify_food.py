import mimetypes
import os

from google import genai
from google.genai import types

import config
from tools.base import Tool
from tools.nutrition_data import FOOD_TABLE

IDENTIFY_PROMPT = (
    "你是一个食物识别助手。请识别图片里的食物，尽量从下面这个已知食物列表里选出最接近的名称，"
    "并估算大概的重量（克）。已知食物列表：{known_foods}。"
    "如果图片里的食物不在列表里，就直接写出你看到的食物名称。"
    "每种食物单独一行，格式：食物名称 - 约XX克。不要输出多余的解释。"
)


class IdentifyFoodTool(Tool):
    name = "identify_food"
    description = (
        "根据一张食物照片识别出图片里是什么食物、大概多少克，用户没法用文字说清楚吃了什么时用这个。"
        '参数：{"image_path": "本地图片文件的完整路径"}'
    )

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not config.GEMINI_API_KEY:
                raise RuntimeError("环境变量 GEMINI_API_KEY 未设置")
            self._client = genai.Client(api_key=config.GEMINI_API_KEY)
        return self._client

    def run(self, image_path: str) -> str:
        if not os.path.exists(image_path):
            return f"找不到图片文件：{image_path}"

        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None or not mime_type.startswith("image/"):
            return f"不是可识别的图片格式：{image_path}"

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        prompt = IDENTIFY_PROMPT.format(known_foods="、".join(FOOD_TABLE.keys()))
        response = self._get_client().models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[
                prompt,
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            ],
        )
        return response.text.strip()
