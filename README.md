# 今天，你吃够了吗？

一个手写 ReAct 循环的蛋白质/营养摄入追踪助手。两个目的：

1. **学习**：亲手实现 ReAct（Reasoning + Acting）的推理循环，不借助任何 SDK 自带的
   function-calling / tool_use 封装，让"模型怎么决定调用什么工具、参数怎么来、
   结果怎么喂回去"这套底层机制完整地留在代码里，可读、可调试。
2. **实用**：一个真的能每天用来记录三餐、追踪蛋白质/碳水/脂肪/热量摄入进度的小工具。

---

## 目录结构

```
protein-agent/
├── agent/
│   ├── core.py             # ReAct 循环本体
│   ├── parser.py           # 解析模型输出的 Thought/Action/Observation 文本
│   ├── prompt_templates.py # System prompt 模板
│   ├── state.py            # AgentState / Step：一次任务的状态和历史记录
│   └── llm_client.py       # Gemini 的最薄封装，纯文本对话，不用其自带的工具调用
├── tools/
│   ├── base.py             # Tool 抽象基类
│   ├── nutrition_data.py   # 67 种食物的蛋白质/碳水/脂肪/热量参考表
│   ├── lookup_nutrition.py # 查询食物营养成分（不记录）
│   ├── log_meal.py         # 记录一餐并返回今日累计 + 距离目标差距
│   ├── edit_meal.py        # 修改今天某一条记录的克重
│   ├── delete_meal.py      # 删除今天某一条记录
│   ├── set_profile.py      # 设置身体情况和目标，算出四项每日目标
│   ├── daily_summary.py    # 查询今日摄入汇总（带编号，配合改/删使用）
│   ├── identify_food.py    # 拍照识别食物（Gemini 多模态）
│   └── recommend_meals.py  # 按当前时间和剩余缺口推荐三餐怎么吃
├── storage/
│   ├── store.py            # JSON 读写封装
│   └── data/                 # profile.json（用户资料+目标）、intake_log.json（按日期分组的摄入记录）
├── api/
│   ├── main.py              # FastAPI：/chat /profile /summary /upload-image
│   └── static/index.html    # 单页网页前端（聊天界面 + 仪表盘）
├── run_cli.py                 # 终端交互入口
├── config.py                  # 常量、路径、API Key 读取
└── requirements.txt
```

---

## ReAct 循环是怎么工作的

这是整个项目最值得看的部分，代码都在 `agent/` 目录下。

### 核心循环（`agent/core.py`）

```
1. 把「system prompt + 工具列表 + 到目前为止的推理记录」拼成一个完整的文本 prompt
2. 把这个 prompt 发给模型（纯文本对话，不用 function-calling）
3. 解析模型返回的文本：
   - 如果是 Final Answer，结束，把答案返回给用户
   - 如果是 Action + Action Input，执行对应的工具，拿到 Observation
4. 把这一步的 Thought/Action/Observation 追加到历史记录里
5. 回到第 1 步，重新拼 prompt（这次历史记录里多了一步），再问模型下一步该做什么
6. 循环，直到出现 Final Answer，或者达到最大步数（MAX_STEPS = 8）
```

模型每次看到的 prompt 都包含**完整的历史记录**（`AgentState.scratchpad_text()`），这就是它"记得"自己上一步做了什么、工具返回了什么的原因——没有任何魔法，就是把文本原样拼回去再问一遍。

### 输出格式和解析（`agent/prompt_templates.py` + `agent/parser.py`）

System prompt 要求模型严格按这个格式输出：

```
Thought: 分析当前应该做什么
Action: 工具名称
Action Input: 一个 JSON 对象
```

或者收尾时：

```
Thought: 我已经有足够信息回答用户了
Final Answer: 给用户的最终回复
```

`parser.py` 用一个逐行扫描的状态机去识别这几个字段，而不是一次性的正则匹配——这是为了容忍模型偶尔的格式抖动（多余空行、字段顺序略有出入）。解析失败时不会让程序崩溃，而是把"格式错误：xxx"作为 Observation 写回 `AgentState`，让模型在下一轮的 scratchpad 里看到自己的错误、有机会自我纠正。

### 工具（`tools/`）

每个工具是 `Tool` 基类的子类，只需要定义 `name`、`description`（会被写进 system prompt 告诉模型怎么用）和 `run()` 方法。`Tool.run_safe()` 包了一层异常处理——参数错了或者执行报错，都变成 Observation 文本喂回给模型，而不是让整个 Agent 崩溃。

### 一个真实的调试案例：模型偶尔会"莫名拒绝"

开发过程中遇到过：明明 `identify_food` 工具就在工具列表里、任务里也给了图片路径，模型却直接在第一步给出 `Final Answer`，说"我没有权限读取本地文件"——完全没有尝试调用工具。复现后发现这不是代码 bug，而是大模型输出本身的随机性——同一个 prompt，多次调用的结果不完全一致。

两个缓解措施（都在代码里能看到）：
1. `prompt_templates.py` 里加了一条明确规则："只要任务里提到图片路径，第一步必须先尝试调用 identify_food，不能以'没有权限'为理由直接拒绝"
2. `llm_client.py` 里把调用 Gemini 时的 `temperature` 调低到 `0.2`——温度控制模型输出的随机程度，ReAct 的推理步骤需要的是严格遵守格式和规则，不需要创造性

这两个改动明显降低了拒绝概率，但没法保证 100% 不再发生——这是大模型本身的局限，不是这套 ReAct 实现能完全解决的问题。

---

## 怎么运行

### 环境准备

```bash
cd /Users/louhe/protein-agent
python3 -m pip install -r requirements.txt
```

需要一个 Gemini API Key（[aistudio.google.com/apikey](https://aistudio.google.com/apikey) 免费申请），写在项目根目录的 `.env` 文件里：

```
GEMINI_API_KEY=你的key
```

### 方式一：终端

```bash
python3 run_cli.py
```

不带参数会进入交互模式，直接打字说话；带参数则是一次性执行：

```bash
python3 run_cli.py "我今天中午吃了200克鸡胸肉"
```

### 方式二：网页

```bash
python3 -m uvicorn api.main:app --reload --port 8000
```

打开 `http://localhost:8000/`，是一个聊天界面 + 仪表盘（蛋白质/碳水/脂肪/热量四项进度卡片 + 一个总进度环）。每条助手回复默认只显示最终答案，点"查看推理过程"才会展开完整的 ReAct 步骤——这样日常用着干净，调试/学习的时候完整过程也在。

### 已配置的开机自启（这台 Mac 专属）

网页服务已经配置成 `launchd` 管理，开机自动启动、崩溃自动重启，不需要手动跑上面的命令：

```bash
# 手动重启（改了代码之后需要这样才会生效，不会自动热加载）
launchctl bootout gui/$(id -u)/com.proteinagent.api
launchctl bootstrap gui/$(id -u) /Users/louhe/Library/LaunchAgents/com.proteinagent.api.plist
```

配置文件在 `~/Library/LaunchAgents/com.proteinagent.api.plist`。

**注意**：项目目录必须在 `~/Downloads`、`~/Desktop`、`~/Documents` 这几个 macOS 隐私保护的特殊文件夹之外——之前项目在 `~/Downloads/protein-agent` 时，`launchd` 启动的进程会被系统以隐私保护为由拒绝访问，报 `PermissionError`，而且这个权限没法通过系统设置手动开启（苹果不允许给 `/usr/bin/python3` 这类系统自带的通用解释器开这个口子）。这也是项目现在放在 `~/protein-agent` 而不是 `~/Downloads/protein-agent` 的原因。

### 手机访问

- **同一个 WiFi 下**：手机浏览器打开 `http://<Mac 的局域网 IP>:8000/`
- **随时随地（用流量也行）**：Mac 和手机都装 [Tailscale](https://tailscale.com/download)，用同一个账号登录，然后访问 Mac 在 Tailscale 网络里的地址（`tailscale ip` 查看）

手机上可以直接拍照/选相册图片，上传后走 `identify_food` 识别。

---

## 数据存储

`storage/data/profile.json`：用户资料和四项每日目标（蛋白质用体重和目标类型算，脂肪按热量目标的 25% 算，碳水填满剩余的热量额度）。

`storage/data/intake_log.json`：按日期分组的摄入记录，形如：

```json
{
  "2026-09-26": [
    {"food": "鸡蛋", "grams": 100.0, "protein": 13.0, "carbs": 1.1, "fat": 10.0, "calories": 143.0, "time": "12:02"}
  ]
}
```

两个文件都是纯 JSON，重启程序、跨天使用都不会丢；`get_daily_summary` 每次只统计当天日期对应的那个数组。

---

## 已知局限

- **食物库精度有限**：67 种食物（含常见家常成品菜）的蛋白质/碳水/脂肪/热量都是常见参考值，不是精确测量，尤其是复合菜品（宫保鸡丁、水煮鱼这类）误差比单一食材更大——同一道菜不同人做法差别很大。
- **中式桌餐定量本身有硬伤**：多人共享的桌菜没法像称重食材一样精确量化，这套工具的定位是"建立大致的量化习惯"，不是实验室级精确称重。
- **单用户**：没有账号体系，数据只有一份，不支持给多人分别记录。
- **接口没有身份验证**：`/chat` 等接口任何能连上（同 WiFi 或 Tailscale 网络里）的人都能调用，没做鉴权——对个人自用没问题，如果要暴露到公网必须先加一层认证。
- **没有运动/消耗记录**：目前只追踪"吃进去多少"，不追踪"消耗多少"，"热量缺口"实际是"距离摄入目标还有多少额度"，不是真正的"摄入-消耗"净差值。

## 可能的后续方向

- 运动记录 + 真正的每日净能量缺口（摄入 - 消耗）
- 多用户支持（`storage/store.py` 目前是单文件读写，改造成本不大，但"怎么识别是谁在用"需要先做设计决策）
- 更换成更权威的营养数据源（比如接入 USDA 数据库），但要解决中文食物名到英文数据库条目的匹配问题
