import json
import re
from dataclasses import dataclass
from typing import Optional


class ParseError(Exception):
    """模型输出不符合约定格式时抛出，交给上层决定怎么恢复。"""


@dataclass
class ParsedOutput:
    thought: str
    action: Optional[str] = None
    action_input: Optional[dict] = None
    action_input_raw: Optional[str] = None
    final_answer: Optional[str] = None


def _strip_code_fence(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(json)?", "", raw)
        raw = re.sub(r"```$", "", raw)
    return raw.strip()


def parse_model_output(text: str) -> ParsedOutput:
    """逐行扫描模型输出，按 Thought/Action/Action Input/Final Answer 归类。

    用状态机而不是一次性正则匹配，是为了容忍模型偶尔的格式抖动（比如
    多余空行、字段顺序略有出入），只要关键字段的前缀还在就能识别。
    """
    lines = text.strip().splitlines()

    thought_lines, action_input_lines, final_answer_lines = [], [], []
    action = None
    mode = None  # 当前正在累积哪个多行字段: 'thought' | 'action_input' | 'final'

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Thought:"):
            mode = "thought"
            thought_lines.append(stripped[len("Thought:"):].strip())
        elif stripped.startswith("Action Input:"):
            mode = "action_input"
            action_input_lines.append(stripped[len("Action Input:"):].strip())
        elif stripped.startswith("Action:"):
            mode = None
            action = stripped[len("Action:"):].strip()
        elif stripped.startswith("Final Answer:"):
            mode = "final"
            final_answer_lines.append(stripped[len("Final Answer:"):].strip())
        elif stripped.startswith("Observation:"):
            # 模型不应该自己编造 Observation，出现就直接截断，忽略后面的内容
            break
        elif mode == "thought":
            thought_lines.append(stripped)
        elif mode == "action_input":
            action_input_lines.append(stripped)
        elif mode == "final":
            final_answer_lines.append(stripped)

    thought = "\n".join(l for l in thought_lines if l).strip()
    if not thought:
        raise ParseError(f"未找到 Thought 字段，原始输出：\n{text}")

    if final_answer_lines:
        return ParsedOutput(thought=thought, final_answer="\n".join(final_answer_lines).strip())

    if not action or not action_input_lines:
        raise ParseError(f"既没有 Final Answer，也没有完整的 Action/Action Input，原始输出：\n{text}")

    raw_input = _strip_code_fence("\n".join(action_input_lines).strip())
    try:
        parsed_input = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        raise ParseError(f"Action Input 不是合法 JSON：{raw_input!r}（{exc}）") from exc

    return ParsedOutput(
        thought=thought,
        action=action,
        action_input=parsed_input,
        action_input_raw=raw_input,
    )
