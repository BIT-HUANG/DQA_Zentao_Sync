# DQA_SYPC.py
import sys
import os
import threading

# ========== 原有环境适配逻辑 ==========
if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, 'libmirror')
    sys.path.append(lib_path)

# ========== 原有UI导入逻辑 ==========
from ui import Win as MainWin
from control import Controller as MainController

# ========== 原有UI初始化逻辑 ==========
app = MainWin(MainController())

if __name__ == "__main__":
    # 仅启动UI，不再自动启动ngrok/Flask
    app.mainloop()