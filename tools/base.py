from abc import ABC, abstractmethod


class Tool(ABC):
    """所有工具的统一接口：一个名字、一段描述（会被写进 prompt 告诉模型怎么用）、一个 run 方法。"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, **kwargs) -> str:
        """执行工具，返回给模型看的 Observation 文本。"""
        raise NotImplementedError

    def run_safe(self, action_input: dict) -> str:
        """包一层异常处理：参数错了或者执行报错，都变成 Observation 文本喂回给模型，
        而不是让整个 Agent 崩溃——模型看到错误信息后通常能自己纠正下一步的参数。
        """
        try:
            return self.run(**action_input)
        except TypeError as exc:
            return f"工具参数错误：{exc}"
        except Exception as exc:
            return f"工具执行出错：{exc}"
