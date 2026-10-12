#!/bin/bash
cd "$(dirname "$0")"
echo "正在检查运行环境..."
if ! command -v python3 >/dev/null 2>&1; then
    echo "没有找到 Python，请先安装：https://www.python.org/downloads/"
    read -p "按回车退出"
    exit 1
fi
python3 -m pip install -q --user requests -i https://pypi.tuna.tsinghua.edu.cn/simple
python3 bot.py
read -p "按回车退出"
