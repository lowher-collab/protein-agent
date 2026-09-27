from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Step:
    """一轮 ReAct 推理产生的记录：一个 Thought，接一个 Action 或者一个 Final Answer。"""

    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None
    is_final: bool = False
    final_answer: Optional[str] = None


@dataclass
class AgentState:
    """一次任务从开始到结束的全部状态：任务描述 + 逐步累积的推理记录。"""

    task: str
    steps: list = field(default_factory=list)
    finished: bool = False
    final_answer: Optional[str] = None

    def add_step(self, step: Step) -> None:
        self.steps.append(step)
        if step.is_final:
            self.finished = True
            self.final_answer = step.final_answer

    def scratchpad_text(self) -> str:
        """把历史步骤拼成文本，作为下一轮 prompt 的一部分喂给模型。"""
        parts = []
        for step in self.steps:
            parts.append(f"Thought: {step.thought}")
            if step.action:
                parts.append(f"Action: {step.action}")
                parts.append(f"Action Input: {step.action_input}")
            if step.observation is not None:
                parts.append(f"Observation: {step.observation}")
        return "\n".join(parts)
