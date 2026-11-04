# 陪伴AI六维评测（companion-eval）

搭一个陪伴角色「小暖」，用 30 条用例从六个维度对比两版 Prompt，让裁判模型打分（LLM-as-judge），再人工抽检，看裁判靠不靠谱。

| 维度 | 测什么 | 例子 |
|---|---|---|
| 人设一致性 | 被追问、被指令改写时会不会崩 | “你是AI吗”“你以前不是这么说话的” |
| 情绪承接 | 先共情还是先说教 | “今天被老板骂了” |
| 记忆 | 隔了 8 轮闲聊还记不记得 | 前面说“猫叫豆豆”，后面问“我的猫叫什么” |
| 现实感知 | 会不会和时间、季节矛盾 | 冬夜下雪的场景里说“阳光真好” |
| 剧情推进 | 用户只回“嗯”时能不能接下去 | “嗯”“随便”“……” |
| 安全边界 | 越界请求能不能挡住 | 露骨内容、下药、自伤、索要系统提示词 |

**两个版本**（见 `personas.py`）
- **v1 基线**：只有静态人设
- **v2**：人设 + 当前场景注入 + 每轮由模型抽取并注入的滚动记忆

## 使用方法

任何 OpenAI 兼容接口都可以用（DeepSeek / 通义千问 / Kimi …），只用 Python 标准库，不用安装依赖。

```bash
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_API_KEY=sk-xxx
export LLM_MODEL=deepseek-chat
# 可选：裁判换另一家模型，避免“自己给自己打分”
export JUDGE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export JUDGE_API_KEY=sk-yyy
export JUDGE_MODEL=qwen-plus
```

```bash
python eval.py run          # 跑对话 + 裁判打分，可断点续跑；--only memory,reality 只跑部分维度
python eval.py sample       # 抽 12 条导出 results/human_review.csv（不显示模型分数，避免先入为主）
# 用 Excel 打开 CSV，填写 human_score 列
python eval.py agree        # 计算人工与裁判的一致率、±1 分一致率、Spearman 相关
python eval.py report       # 生成 results/report.md：分维度得分、好/坏例子、结论
python eval.py view         # 生成 results/view.html：v1/v2 完整多轮对话并排对比
python eval.py web          # 浏览器里和小暖聊天：v1 / v2 / 同时对比，实时看记忆
python eval.py chat         # 终端里和小暖聊天（默认 v2；--version v1 对比；--scene "深夜，下雪" 指定场景）
```

不配 API key、先试流程：`LLM_MOCK=1 python eval.py run`

## 文件
- `personas.py`：角色设定、v1/v2 的 system prompt、记忆抽取 prompt
- `cases.json`：30 条用例；`@filler:N` 会展开成 N 轮闲聊干扰；`expect` 是记忆题的关键词硬指标
- `rubric.py`：各维度 1–5 分评分标准与裁判 prompt
- `chat.html`：`eval.py web` 的聊天页面
- `viewer_template.html`：`eval.py view` 用的对话对比页模板；可在 `results/notes.json` 里写人工批注，会显示在页面上
- `eval.py`：运行、抽样、一致性、报告、对话查看页。两版都只携带最近 5 轮对话（`CONTEXT_TURNS` 可调），否则记忆题测不出差别

## 成本估算
30 条 × 2 版，加上 v2 的记忆抽取和裁判，大约 400 次调用；用 deepseek-chat 一次跑完通常只要几毛钱到一两元人民币。
