#!/usr/bin/env python3
"""陪伴AI六维评测：两版Prompt对比 + LLM-as-judge + 人工抽检一致性。

用法：
  python eval.py run                 # 跑对话 + 裁判打分，结果写入 results/
  python eval.py sample --n 12       # 抽样导出 results/human_review.csv 供人工打分
  python eval.py agree               # 人工打完后，计算与模型裁判的一致性
  python eval.py report              # 生成 results/report.md
  python eval.py view                # 生成 results/view.html：v1/v2 完整对话并排对比，浏览器打开
  python eval.py chat                # 自己在终端里和小暖聊天（默认 v2，可 --version v1）
  python eval.py web                 # 在浏览器里和小暖聊天，可 v1/v2 同时对比

环境变量（任意 OpenAI 兼容接口：DeepSeek / 通义 / Kimi ...）：
  LLM_BASE_URL   如 https://api.deepseek.com/v1
  LLM_API_KEY
  LLM_MODEL      被测模型，如 deepseek-chat
  JUDGE_BASE_URL / JUDGE_API_KEY / JUDGE_MODEL  裁判模型（可选，默认同上；建议用另一家）
  CONTEXT_TURNS  每次请求携带的最近对话轮数，默认 5（0 = 全部携带）
  LLM_MOCK=1     不调API，用假回复跑通流程
只用 Python 标准库，无需安装依赖。
"""
import argparse
import csv
import json
import os
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

from personas import V1_SYSTEM, v2_system, MEMORY_EXTRACT_PROMPT
from rubric import DIMENSIONS, RUBRIC, JUDGE_PROMPT

ROOT = Path(__file__).parent
OUT = ROOT / "results"
FILLER = [
    "今天吃了麻辣烫", "地铁好挤", "最近在追一部剧", "你喜欢下雨天吗",
    "我刚洗完澡", "有点想喝奶茶", "同事今天请假了", "周末想去爬山",
    "手机快没电了", "刚看了个搞笑视频", "楼下在装修好吵", "晚饭不知道吃啥",
]


# ---------------- LLM 调用 ----------------
def chat(messages, role="target", temperature=0.7):
    if os.getenv("LLM_MOCK"):
        return _mock(messages, role)
    pre = "JUDGE_" if role == "judge" else "LLM_"
    base = os.getenv(pre + "BASE_URL") or os.environ["LLM_BASE_URL"]
    key = os.getenv(pre + "API_KEY") or os.environ["LLM_API_KEY"]
    model = os.getenv(pre + "MODEL") or os.environ["LLM_MODEL"]
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temperature}).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["choices"][0]["message"]["content"].strip()
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                raise
            print(f"  ! {e}，{2 ** attempt}s 后重试", file=sys.stderr)
            time.sleep(2 ** attempt)


def _mock(messages, role):
    last = messages[-1]["content"]
    if role == "judge":
        return json.dumps({"score": random.randint(2, 5), "reason": "mock"})
    if role == "memory":
        return "（mock记忆）"
    return f"嗯嗯，我在呢～（mock回复：{last[:10]}）"


# ---------------- 跑对话 ----------------
def expand_turns(turns):
    out, pool = [], FILLER[:]
    for t in turns:
        m = re.fullmatch(r"@filler:(\d+)", t)
        if m:
            out += [pool[i % len(pool)] for i in range(int(m.group(1)))]
        else:
            out.append(t)
    return out


CONTEXT_TURNS = int(os.getenv("CONTEXT_TURNS", "5"))


def run_case(case, version):
    """两个版本都只把最近 CONTEXT_TURNS 轮对话发给模型（模拟真实产品的上下文截断），
    更早的信息 v1 只能遗忘，v2 依靠记忆注入找回。"""
    history, memory = [], ""
    for user in expand_turns(case["turns"]):
        system = V1_SYSTEM if version == "v1" else v2_system(case["scene"], memory)
        window = history[-CONTEXT_TURNS * 2:] if CONTEXT_TURNS > 0 else history
        msgs = [{"role": "system", "content": system}] + window + \
               [{"role": "user", "content": user}]
        reply = chat(msgs)
        history += [{"role": "user", "content": user},
                    {"role": "assistant", "content": reply}]
        if version == "v2":
            memory = chat([{"role": "user", "content": MEMORY_EXTRACT_PROMPT.format(
                memory=memory or "（空）", user=user, assistant=reply)}],
                role="memory", temperature=0)
    return history, memory


def transcript_text(history):
    return "\n".join(("用户：" if m["role"] == "user" else "AI：") + m["content"]
                     for m in history)


def judge(case, history):
    prompt = JUDGE_PROMPT.format(
        dim_name=DIMENSIONS[case["dimension"]], rubric=RUBRIC[case["dimension"]],
        focus=case["focus"], scene=case["scene"] or "无特殊设定",
        transcript=transcript_text(history))
    raw = chat([{"role": "user", "content": prompt}], role="judge", temperature=0)
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        d = json.loads(m.group(0))
        return int(d["score"]), d.get("reason", "")
    except Exception:  # noqa: BLE001
        return None, f"裁判输出无法解析：{raw[:200]}"


def cmd_run(args):
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
    if args.only:
        cases = [c for c in cases if c["dimension"] in args.only.split(",")]
    OUT.mkdir(exist_ok=True)
    path = OUT / "runs.jsonl"
    done = set()
    if path.exists() and not args.fresh:
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done.add((r["id"], r["version"]))
    elif path.exists():
        path.unlink()
    with path.open("a", encoding="utf-8") as f:
        for case in cases:
            for v in ("v1", "v2"):
                if (case["id"], v) in done:
                    continue
                print(f"[{v}] {case['id']} ...", flush=True)
                history, memory = run_case(case, v)
                score, reason = judge(case, history)
                hit = None
                if case.get("expect"):
                    hit = case["expect"] in history[-1]["content"]
                rec = {"id": case["id"], "dimension": case["dimension"],
                       "version": v, "scene": case["scene"], "history": history,
                       "memory": memory, "judge_score": score,
                       "judge_reason": reason, "keyword_hit": hit}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                print(f"    -> {score}  {reason}")
    print(f"完成，结果在 {path}")


# ---------------- 人工抽检 ----------------
def load_runs():
    p = OUT / "runs.jsonl"
    if not p.exists():
        sys.exit("先运行 python eval.py run")
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]


def cmd_sample(args):
    runs = load_runs()
    random.seed(args.seed)
    by_dim = {}
    for r in runs:
        by_dim.setdefault(r["dimension"], []).append(r)
    per = max(1, args.n // len(by_dim))
    picked = [r for rs in by_dim.values() for r in random.sample(rs, min(per, len(rs)))]
    random.shuffle(picked)
    path = OUT / "human_review.csv"
    with path.open("w", newline="", encoding="utf-8-sig") as f:  # Excel 可直接打开
        w = csv.writer(f)
        w.writerow(["id", "version", "dimension", "scene", "transcript",
                    "human_score(1-5)", "human_note"])
        for r in picked:
            w.writerow([r["id"], r["version"], DIMENSIONS[r["dimension"]],
                        r["scene"], transcript_text(r["history"]), "", ""])
    print(f"已导出 {len(picked)} 条到 {path}。表里故意不放模型分数，避免先入为主；"
          "填完 human_score 后运行 python eval.py agree")


def cmd_agree(_args):
    runs = {(r["id"], r["version"]): r for r in load_runs()}
    rows = list(csv.DictReader((OUT / "human_review.csv").open(encoding="utf-8-sig")))
    pairs = []
    for row in rows:
        h = row["human_score(1-5)"].strip()
        j = runs[(row["id"], row["version"])]["judge_score"]
        if h and j is not None:
            pairs.append((int(h), j, row))
    if not pairs:
        sys.exit("human_review.csv 里还没有填写 human_score")
    exact = sum(h == j for h, j, _ in pairs) / len(pairs)
    within1 = sum(abs(h - j) <= 1 for h, j, _ in pairs) / len(pairs)
    hs, js = [p[0] for p in pairs], [p[1] for p in pairs]
    res = {"n": len(pairs), "exact": exact, "within1": within1,
           "spearman": spearman(hs, js),
           "disagreements": [{"id": r["id"], "version": r["version"],
                              "human": h, "judge": j}
                             for h, j, r in pairs if abs(h - j) >= 2]}
    (OUT / "agreement.json").write_text(json.dumps(res, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


def spearman(a, b):
    def rank(x):
        order = sorted(range(len(x)), key=lambda i: x[i])
        r = [0.0] * len(x)
        i = 0
        while i < len(x):
            j = i
            while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** .5
    vb = sum((y - mb) ** 2 for y in rb) ** .5
    return round(cov / (va * vb), 3) if va and vb else None


# ---------------- 报告 ----------------
def cmd_report(_args):
    runs = load_runs()
    lines = ["# 陪伴AI评测报告：v1（基线）vs v2（场景注入+记忆注入）", ""]
    model = os.getenv("LLM_MODEL", "?")
    judge_m = os.getenv("JUDGE_MODEL", model)
    lines += [f"- 被测模型：`{model}`　裁判模型：`{judge_m}`",
              f"- 用例数：{len({r['id'] for r in runs})}，六个维度各 5 条，每条两版各跑一次",
              f"- 上下文窗口：两版均只携带最近 {CONTEXT_TURNS} 轮对话（模拟真实产品截断）", ""]
    lines += ["## 各维度得分（1-5，模型裁判均分）", "",
              "| 维度 | v1 | v2 | 差值 |", "|---|---|---|---|"]
    tot = {"v1": [], "v2": []}
    for dim, name in DIMENSIONS.items():
        s = {}
        for v in ("v1", "v2"):
            xs = [r["judge_score"] for r in runs
                  if r["dimension"] == dim and r["version"] == v and r["judge_score"]]
            tot[v] += xs
            s[v] = sum(xs) / len(xs) if xs else None
        d = (s["v2"] - s["v1"]) if s["v1"] and s["v2"] else None
        fmt = lambda x: f"{x:.2f}" if x is not None else "-"  # noqa: E731
        lines.append(f"| {name} | {fmt(s['v1'])} | {fmt(s['v2'])} | "
                     f"{'+' if d and d > 0 else ''}{fmt(d)} |")
    avg = {v: sum(x) / len(x) if x else 0 for v, x in tot.items()}
    lines.append(f"| **总分** | **{avg['v1']:.2f}** | **{avg['v2']:.2f}** | "
                 f"**{avg['v2'] - avg['v1']:+.2f}** |")

    kw = [r for r in runs if r["keyword_hit"] is not None]
    if kw:
        lines += ["", "**记忆关键词硬指标**（最后一轮是否包含正确答案）："]
        for v in ("v1", "v2"):
            xs = [r["keyword_hit"] for r in kw if r["version"] == v]
            lines.append(f"- {v}：{sum(xs)}/{len(xs)}")

    agree = OUT / "agreement.json"
    lines += ["", "## 裁判可信度（人工抽检）", ""]
    if agree.exists():
        a = json.loads(agree.read_text(encoding="utf-8"))
        lines += [f"- 抽检 {a['n']} 条：完全一致 {a['exact']:.0%}，相差≤1分 "
                  f"{a['within1']:.0%}，Spearman 相关 {a['spearman']}",
                  f"- 分歧≥2分的用例：{', '.join(d['id'] + '/' + d['version'] for d in a['disagreements']) or '无'}"]
    else:
        lines.append("- （尚未人工抽检：运行 `eval.py sample` 再 `eval.py agree`）")

    scored = [r for r in runs if r["judge_score"]]
    best = sorted(scored, key=lambda r: -r["judge_score"])[:3]
    worst = sorted(scored, key=lambda r: r["judge_score"])[:3]
    for title, group in (("典型好例子", best), ("典型坏例子", worst)):
        lines += ["", f"## {title}", ""]
        for r in group:
            last_u, last_a = r["history"][-2]["content"], r["history"][-1]["content"]
            lines += [f"**{r['id']} / {r['version']}（{r['judge_score']}分）**"
                      + (f"　场景：{r['scene']}" if r["scene"] else ""),
                      f"> 用户：{last_u}", ">", f"> AI：{last_a}", "",
                      f"裁判理由：{r['judge_reason']}", ""]

    lines += ["", "## 结论与改进方向", "",
              "_（跑完后根据上表填写：哪些维度 v2 提升明显、哪些没变化或变差、原因推测、下一步要改的 Prompt/机制）_"]
    path = OUT / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"报告已生成：{path}")


def build_viewer(runs, notes=None, caveats=None, standalone=True):
    """把运行结果嵌入查看页模板，返回 HTML 字符串。"""
    cases = {c["id"]: c for c in json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))}
    data = {"runs": runs, "cases": cases, "dims": DIMENSIONS,
            "notes": notes or {}, "caveats": caveats or [],
            "meta": {"model": os.getenv("LLM_MODEL", "?"),
                     "judge": os.getenv("JUDGE_MODEL") or os.getenv("LLM_MODEL", "?"),
                     "context_turns": CONTEXT_TURNS}}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "viewer_template.html").read_text(encoding="utf-8")
    html = html.replace("/*__DATA__*/null", blob)
    if standalone:
        html = ('<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
                '</head><body>\n' + html + "\n</body></html>")
    return html


def cmd_view(_args):
    runs = load_runs()
    notes_path = OUT / "notes.json"   # 可选：人工批注 {"memory-3/v1": "...", "plot-2": "..."}
    notes = json.loads(notes_path.read_text(encoding="utf-8")) if notes_path.exists() else {}
    path = OUT / "view.html"
    path.write_text(build_viewer(runs, notes), encoding="utf-8")
    print(f"已生成 {path}\nMac 上运行 open {path} 用浏览器打开")


WEEKDAYS = "一二三四五六日"


def auto_scene():
    """根据电脑当前时间生成场景描述（天气未知，可用 /scene 手动补充）。"""
    t = time.localtime()
    season = {12: "冬天", 1: "冬天", 2: "冬天", 3: "春天", 4: "春天", 5: "春天",
              6: "夏天", 7: "夏天", 8: "夏天"}.get(t.tm_mon, "秋天")
    h = t.tm_hour
    part = ("凌晨" if h < 5 else "早上" if h < 9 else "上午" if h < 12 else "中午" if h < 14
            else "下午" if h < 18 else "晚上" if h < 23 else "深夜")
    return f"现在是{t.tm_mon}月{t.tm_mday}日 星期{WEEKDAYS[t.tm_wday]} {part}{h}点{t.tm_min:02d}分，{season}"


CHAT_HELP = """命令：/mem 看记忆  /scene 文字 改场景（只输 /scene 就清空）  /reset 重新开始  /quit 退出并保存"""


def cmd_chat(args):
    try:
        import readline  # noqa: F401  让中文输入时退格、方向键更正常
    except ImportError:
        pass
    v = args.version
    scene = args.scene if args.scene is not None else auto_scene()
    history, memory, log = [], "", []
    print(f"\n和小暖聊天（{v}，携带最近 {CONTEXT_TURNS} 轮）")
    if v == "v2":
        print(f"当前场景：{scene or '（无）'}")
    print(CHAT_HELP + "\n")
    while True:
        try:
            user = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user in ("/quit", "/exit", "/q"):
            break
        if user == "/mem":
            print("── 小暖记得的事 ──\n" + (memory or "（还没有）") + "\n")
            continue
        if user.startswith("/scene"):
            scene = user[len("/scene"):].strip()
            print(f"场景已改为：{scene or '（无）'}\n")
            continue
        if user == "/reset":
            history, memory = [], ""
            print("已清空对话和记忆\n")
            continue
        system = V1_SYSTEM if v == "v1" else v2_system(scene, memory)
        window = history[-CONTEXT_TURNS * 2:] if CONTEXT_TURNS > 0 else history
        try:
            reply = chat([{"role": "system", "content": system}] + window +
                         [{"role": "user", "content": user}])
        except Exception as e:  # noqa: BLE001
            print(f"（请求失败：{e}）\n")
            continue
        print(f"小暖：{reply}\n")
        history += [{"role": "user", "content": user}, {"role": "assistant", "content": reply}]
        log.append({"user": user, "assistant": reply, "scene": scene})
        if v == "v2":
            old = set(memory.splitlines())
            memory = chat([{"role": "user", "content": MEMORY_EXTRACT_PROMPT.format(
                memory=memory or "（空）", user=user, assistant=reply)}],
                role="memory", temperature=0)
            new = [m for m in memory.splitlines() if m.strip() and m not in old]
            if new and args.show_memory:
                print("  \033[2m[记住了] " + "；".join(new) + "\033[0m\n")
    if log:
        d = OUT / "chats"
        d.mkdir(parents=True, exist_ok=True)
        path = d / time.strftime(f"chat-{v}-%Y%m%d-%H%M%S.json")
        path.write_text(json.dumps({"version": v, "memory": memory, "turns": log},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"对话已保存到 {path}")


def chat_turn(version, scene, history, memory, user):
    """一轮对话：与评测完全相同的 v1/v2 逻辑。返回 (回复, 更新后的记忆)。"""
    system = V1_SYSTEM if version == "v1" else v2_system(scene, memory)
    window = history[-CONTEXT_TURNS * 2:] if CONTEXT_TURNS > 0 else history
    reply = chat([{"role": "system", "content": system}] + window +
                 [{"role": "user", "content": user}])
    if version == "v2":
        memory = chat([{"role": "user", "content": MEMORY_EXTRACT_PROMPT.format(
            memory=memory or "（空）", user=user, assistant=reply)}],
            role="memory", temperature=0)
    return reply, memory


def cmd_web(args):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    import webbrowser

    page = (ROOT / "chat.html").read_bytes()

    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, page, "text/html; charset=utf-8")
            elif self.path == "/api/config":
                self._send(200, {"context_turns": CONTEXT_TURNS, "scene": auto_scene(),
                                 "model": os.getenv("LLM_MODEL", "mock"),
                                 "mock": bool(os.getenv("LLM_MOCK"))})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/api/turn":
                return self._send(404, {"error": "not found"})
            try:
                d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                v = d.get("version") if d.get("version") in ("v1", "v2") else "v2"
                reply, memory = chat_turn(v, d.get("scene", ""), d.get("history", []),
                                          d.get("memory", ""), d["user"])
                self._send(200, {"reply": reply, "memory": memory})
            except KeyError as e:
                self._send(500, {"error": f"缺少环境变量 {e}，先 export LLM_BASE_URL / LLM_API_KEY / LLM_MODEL"})
            except Exception as e:  # noqa: BLE001
                print(f"  ! {e}", file=sys.stderr)
                self._send(500, {"error": str(e)})

        def log_message(self, *a):
            pass

    if not os.getenv("LLM_MOCK") and not os.getenv("LLM_API_KEY"):
        print("提示：还没设置 LLM_API_KEY，网页能打开但发消息会失败。")
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), H)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"小暖已上线：{url}\n（浏览器没自动打开就手动访问这个地址；按 Control+C 停止）")
    if not args.no_open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--only", help="只跑部分维度，如 memory,reality")
    r.add_argument("--fresh", action="store_true", help="清空旧结果重跑")
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=12)
    s.add_argument("--seed", type=int, default=42)
    sub.add_parser("agree")
    sub.add_parser("report")
    sub.add_parser("view")
    w = sub.add_parser("web")
    w.add_argument("--port", type=int, default=8765)
    w.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    c = sub.add_parser("chat")
    c.add_argument("--version", choices=["v1", "v2"], default="v2")
    c.add_argument("--scene", help="手动指定场景，如 \"深夜，冬天，下雪\"；默认用电脑当前时间")
    c.add_argument("--hide-memory", dest="show_memory", action="store_false",
                   help="不显示每轮新记住的内容")
    a = p.parse_args()
    {"run": cmd_run, "sample": cmd_sample, "agree": cmd_agree,
     "report": cmd_report, "view": cmd_view, "chat": cmd_chat, "web": cmd_web}[a.cmd](a)


if __name__ == "__main__":
    main()
