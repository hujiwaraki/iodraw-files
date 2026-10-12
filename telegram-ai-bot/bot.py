# -*- coding: utf-8 -*-
"""
Telegram AI 陪聊机器人（OpenAI 版）
你不需要改这个文件，只需要改 config.txt。
"""
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print("缺少 requests 库，请用启动脚本运行（它会自动安装）。")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(HERE, "config.txt")
PERSONA_FILE = os.path.join(HERE, "persona.txt")
MEMORY_FILE = os.path.join(HERE, "memory.json")


def load_config():
    cfg = {}
    with open(CONFIG_FILE, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            cfg[key.strip()] = value.strip()
    return cfg


cfg = load_config()
TELEGRAM_TOKEN = cfg.get("TELEGRAM_TOKEN", "")
OPENAI_API_KEY = cfg.get("OPENAI_API_KEY", "")
OPENAI_MODEL = cfg.get("OPENAI_MODEL", "gpt-5-mini")
OPENAI_BASE_URL = cfg.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
HISTORY_TURNS = int(cfg.get("HISTORY_TURNS", "20"))
ALLOWED_USERS = {u.strip() for u in cfg.get("ALLOWED_USERS", "").split(",") if u.strip()}
PROXY = cfg.get("PROXY", "")

if "填这里" in TELEGRAM_TOKEN or not TELEGRAM_TOKEN:
    sys.exit("❌ 请先在 config.txt 里填写 TELEGRAM_TOKEN")
if "填这里" in OPENAI_API_KEY or not OPENAI_API_KEY:
    sys.exit("❌ 请先在 config.txt 里填写 OPENAI_API_KEY")

with open(PERSONA_FILE, encoding="utf-8-sig") as f:
    PERSONA = f.read().strip()

session = requests.Session()
if PROXY:
    session.proxies = {"http": PROXY, "https": PROXY}

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=1)


memory = load_memory()


def send_message(chat_id, text):
    session.post(f"{TG_API}/sendMessage", json={"chat_id": chat_id, "text": text}, timeout=30)


def send_typing(chat_id):
    try:
        session.post(f"{TG_API}/sendChatAction", json={"chat_id": chat_id, "action": "typing"}, timeout=10)
    except requests.RequestException:
        pass


def ask_openai(history):
    messages = [{"role": "system", "content": PERSONA}] + history
    resp = session.post(
        f"{OPENAI_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": OPENAI_MODEL, "messages": messages},
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI 返回错误 {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def handle_message(msg):
    chat_id = msg["chat"]["id"]
    user_id = str(msg["from"]["id"])
    text = msg.get("text")
    if not text:
        send_message(chat_id, "我现在只看得懂文字哦～")
        return

    if text == "/myid":
        send_message(chat_id, f"你的用户 ID 是：{user_id}")
        return
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        send_message(chat_id, "抱歉，这是私人机器人。")
        return
    if text == "/start":
        send_message(chat_id, "你好呀！想聊点什么？（发送 /reset 可以清空聊天记忆）")
        return
    if text == "/reset":
        memory.pop(user_id, None)
        save_memory()
        send_message(chat_id, "好的，我们重新开始吧～")
        return

    history = memory.setdefault(user_id, [])
    history.append({"role": "user", "content": text})
    del history[:-HISTORY_TURNS * 2]

    send_typing(chat_id)
    try:
        reply = ask_openai(history)
    except Exception as e:
        history.pop()
        print("⚠️ 调用 OpenAI 失败：", e)
        send_message(chat_id, "（我刚刚走神了，请再说一次～）")
        return

    history.append({"role": "assistant", "content": reply})
    save_memory()
    send_message(chat_id, reply)


def main():
    print("正在连接 Telegram ...")
    try:
        me = session.get(f"{TG_API}/getMe", timeout=30).json()
    except requests.RequestException as e:
        sys.exit(f"❌ 连不上 Telegram：{e}\n   如果你在国内，请在 config.txt 里设置 PROXY。")
    if not me.get("ok"):
        sys.exit(f"❌ TELEGRAM_TOKEN 不正确：{me}")
    print(f"✅ 机器人 @{me['result']['username']} 已上线！去 Telegram 找它聊天吧。")
    print("   （关闭这个窗口机器人就会下线）")

    offset = 0
    while True:
        try:
            data = session.get(
                f"{TG_API}/getUpdates", params={"offset": offset, "timeout": 50}, timeout=60
            ).json()
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
        except requests.RequestException as e:
            print("⚠️ 网络波动，5 秒后重试：", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
