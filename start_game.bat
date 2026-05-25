@echo off
chcp 65001 >nul
echo ========================================
echo   奇幻冒险RPG - Fantasy RPG Adventure
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

:: 检查并安装依赖
echo [1/3] 检查依赖...
pip install kivy numpy >nul 2>&1

:: 生成音频资源
echo [2/3] 生成音频资源...
if exist music_generator.py (
    python music_generator.py
) else (
    echo [警告] 未找到音乐生成器，将使用静音模式运行
)

:: 启动游戏
echo [3/3] 启动游戏...
echo.
echo ========================================
echo   操作说明：
echo   WASD/方向键 - 移动
echo   空格键 - 互动（对话/开宝箱）
echo   鼠标点击 - 操作按钮
echo   ESC - 返回上级菜单
echo ========================================
echo.
python fantasy_rpg_complete.py

pause
