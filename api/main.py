import uuid
from pathlib import Path
from typing import List, Optional

import config
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.core import ReActAgent
from agent.llm_client import GeminiClient
from storage import store
from tools.daily_summary import DailySummaryTool
from tools.delete_meal import DeleteMealEntryTool
from tools.edit_meal import EditMealEntryTool
from tools.identify_food import IdentifyFoodTool
from tools.log_meal import LogMealTool
from tools.lookup_nutrition import LookupNutritionTool
from tools.recommend_meals import RecommendMealsTool
from tools.set_profile import SetUserProfileTool

app = FastAPI(title="今天，你吃够了吗？")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.post("/upload-image")
async def upload_image(file: UploadFile):
    """手机拍照/相册选图先传到这里落地成服务器上的文件，拿到路径后才能喂给
    identify_food 工具——它认的是本机文件路径，不是上传流本身。
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只接受图片文件")

    upload_dir = Path(config.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "").suffix or ".jpg"
    saved_path = upload_dir / f"{uuid.uuid4().hex}{ext}"

    content = await file.read()
    saved_path.write_bytes(content)

    return {"path": str(saved_path)}


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
    return ReActAgent(llm_client=GeminiClient(), tools=tools)


# 只在进程启动时创建一次，所有请求共用同一个 agent（同一份工具、同一个模型客户端），
# 避免每次请求都重新建立连接；ReAct 的状态本身是每次 run() 单独创建的，请求之间不会串。
agent = build_agent()


class ChatRequest(BaseModel):
    message: str


class StepOut(BaseModel):
    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None
    final_answer: Optional[str] = None


class ChatResponse(BaseModel):
    task: str
    steps: List[StepOut]
    final_answer: Optional[str]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """对外的对话入口：接收一句话，内部跑一次完整的 ReAct 循环，把每一步推理过程和
    最终答案都原样返回——前端既可以只显示 final_answer，也可以把 steps 画成过程动画。
    """
    state = agent.run(req.message)
    steps = [
        StepOut(
            thought=s.thought,
            action=s.action,
            action_input=s.action_input,
            observation=s.observation,
            final_answer=s.final_answer,
        )
        for s in state.steps
    ]
    return ChatResponse(task=state.task, steps=steps, final_answer=state.final_answer)


@app.get("/profile")
def get_profile():
    """直接读存储，不走模型——纯粹的数据查询不需要浪费一次 LLM 调用。"""
    return store.get_profile() or {}


@app.get("/summary")
def get_summary(date: Optional[str] = None):
    """某一天的摄入汇总和距离目标的差距，同样不经过模型，给前端画图表用。"""
    entries = store.get_intake(date)
    total_protein = round(sum(e["protein"] for e in entries), 1)
    total_carbs = round(sum(e.get("carbs", 0) for e in entries), 1)
    total_fat = round(sum(e.get("fat", 0) for e in entries), 1)
    total_calories = round(sum(e["calories"] for e in entries), 1)

    result = {
        "date": date or store.today_str(),
        "entries": entries,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fat": total_fat,
        "total_calories": total_calories,
    }

    profile = store.get_profile()
    if profile:
        result["protein_target"] = profile["protein_target"]
        result["carb_target"] = profile.get("carb_target")
        result["fat_target"] = profile.get("fat_target")
        result["calorie_target"] = profile["calorie_target"]
        result["protein_remaining"] = round(max(profile["protein_target"] - total_protein, 0), 1)
        if profile.get("carb_target") is not None:
            result["carb_remaining"] = round(max(profile["carb_target"] - total_carbs, 0), 1)
        if profile.get("fat_target") is not None:
            result["fat_remaining"] = round(max(profile["fat_target"] - total_fat, 0), 1)
        result["calories_remaining"] = round(profile["calorie_target"] - total_calories, 1)

    return result
