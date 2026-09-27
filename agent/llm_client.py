from google import genai
from google.genai import types

import config


class GeminiClient:
    """对 Gemini 的最薄封装：只做纯文本对话，不使用 SDK 自带的 function-calling 功能，
    这样 ReAct 的工具调用逻辑才会完全由我们自己的 prompt + parser 来驱动。
    """

    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise RuntimeError("环境变量 GEMINI_API_KEY 未设置")
        self._client = genai.Client(api_key=config.GEMINI_API_KEY)

    def complete(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
            # 低温度让"该不该调用工具"这类判断更稳定、更少随机拒绝；
            # ReAct 的推理步骤要的是遵守格式和规则，不需要创造性。
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return response.text
