import json
import os
import time
from typing import Dict

import config
from agent.parser import ParseError, parse_model_output
from agent.prompt_templates import SYSTEM_PROMPT, USER_TURN_TEMPLATE
from agent.state import AgentState, Step
from tools.base import Tool


class ReActAgent:
    """ReAct 循环本体：反复执行"构造 prompt -> 调用模型 -> 解析输出 -> 执行工具 -> 回填结果"，
    直到模型给出 Final Answer 或者达到最大步数。
    """

    def __init__(self, llm_client, tools: Dict[str, Tool], max_steps: int = config.MAX_STEPS):
        self.llm_client = llm_client
        self.tools = tools
        self.max_steps = max_steps

    def _build_prompt(self, state: AgentState) -> str:
        tool_descriptions = "\n".join(f"- {t.name}: {t.description}" for t in self.tools.values())
        tool_names = ", ".join(self.tools.keys())
        system = SYSTEM_PROMPT.format(tool_descriptions=tool_descriptions, tool_names=tool_names)
        user_turn = USER_TURN_TEMPLATE.format(task=state.task, scratchpad=state.scratchpad_text() or "（无）")
        return f"{system}\n\n{user_turn}"

    def run(self, task: str, log_run: bool = True) -> AgentState:
        state = AgentState(task=task)

        for _ in range(self.max_steps):
            prompt = self._build_prompt(state)
            raw_output = self.llm_client.complete(prompt)

            try:
                parsed = parse_model_output(raw_output)
            except ParseError as exc:
                # 解析失败也要写进 state，让模型在下一轮的 scratchpad 里看到自己的格式错误
                state.add_step(Step(thought="(解析模型输出失败)", observation=f"格式错误：{exc}"))
                continue

            if parsed.final_answer is not None:
                state.add_step(Step(thought=parsed.thought, is_final=True, final_answer=parsed.final_answer))
                break

            tool = self.tools.get(parsed.action)
            if tool is None:
                known = ", ".join(self.tools.keys())
                observation = f"未知工具「{parsed.action}」，可用工具：{known}"
            else:
                observation = tool.run_safe(parsed.action_input)

            state.add_step(Step(
                thought=parsed.thought,
                action=parsed.action,
                action_input=parsed.action_input_raw,
                observation=observation,
            ))
        else:
            state.add_step(Step(
                thought="(达到最大步数)",
                is_final=True,
                final_answer="抱歉，我在限定步数内没能得出结论。",
            ))

        if log_run:
            self._write_log(state)

        return state

    def _write_log(self, state: AgentState) -> None:
        os.makedirs(config.LOG_DIR, exist_ok=True)
        path = os.path.join(config.LOG_DIR, f"{int(time.time())}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "task": state.task,
                    "final_answer": state.final_answer,
                    "steps": [step.__dict__ for step in state.steps],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
