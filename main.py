"""
Fantasy RPG Adventure - Main Entry Point
"""
import os
import sys

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行主程序
from fantasy_rpg_complete import FantasyRPGApp

if __name__ == '__main__':
    FantasyRPGApp().run()
