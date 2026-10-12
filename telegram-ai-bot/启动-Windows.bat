@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在检查运行环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 没有找到 Python，请先安装：https://www.python.org/downloads/
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b
)
python -m pip install -q requests -i https://pypi.tuna.tsinghua.edu.cn/simple
python bot.py
pause
