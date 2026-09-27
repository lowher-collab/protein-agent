import sys

from agent.core import ReActAgent
from agent.llm_client import GeminiClient
from tools.daily_summary import DailySummaryTool
from tools.delete_meal import DeleteMealEntryTool
from tools.edit_meal import EditMealEntryTool
from tools.identify_food import IdentifyFoodTool
from tools.log_meal import LogMealTool
from tools.lookup_nutrition import LookupNutritionTool
from tools.recommend_meals import RecommendMealsTool
from tools.set_profile import SetUserProfileTool


def build_agent() -> ReActAgent:
    tools = {t.name: t for t in [
        LookupNutritionTool(),
        LogMealTool(),
        SetUserProfileTool(),
        DailySummaryTool(),
        IdentifyFoodTool(),
        RecommendMealsTool(),
        EditMealEntryTool(),
        DeleteMealEntryTool(),
    ]}
    llm_client = GeminiClient()
    return ReActAgent(llm_client=llm_client, tools=tools)


def run_once(agent: ReActAgent, task: str) -> None:
    state = agent.run(task)
    for i, step in enumerate(state.steps, 1):
        print(f"--- Step {i} ---")
        print(f"Thought: {step.thought}")
        if step.action:
            print(f"Action: {step.action}")
            print(f"Action Input: {step.action_input}")
        if step.observation is not None:
            print(f"Observation: {step.observation}")
        if step.final_answer:
            print(f"Final Answer: {step.final_answer}")
        print()


def main():
    agent = build_agent()

    if len(sys.argv) > 1:
        run_once(agent, " ".join(sys.argv[1:]))
        return

    print("今天，你吃够了吗？已启动。直接说你吃了什么、或者问今天的进度，输入 退出 结束。\n")
    while True:
        try:
            task = input("你: ").strip()
        except EOFError:
            break
        if task in ("退出", "exit", "quit"):
            break
        if not task:
            continue
        run_once(agent, task)


if __name__ == "__main__":
    main()
