import sys
import os
import threading  # 用于异步启动Flask，不阻塞UI

# ========== 原有环境适配逻辑 ==========
if getattr(sys, "frozen", False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(current_dir, 'libmirror')
    sys.path.append(lib_path)

# ========== 导入Flask启动函数 ==========
try:
    from portal import start_flask_server
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"Flask模块导入失败：{e}，请执行 pip install flask")
    FLASK_AVAILABLE = False

# ========== 原有UI导入逻辑 ==========
from ui import Win as MainWin
from control import Controller as MainController

# ========== 异步启动Flask后台 ==========
def start_app_services():
    """启动应用附属服务（Flask后台）"""
    if FLASK_AVAILABLE:
        # 异步启动Flask，避免阻塞UI
        flask_thread = threading.Thread(
            target=start_flask_server,
            kwargs={"host": "0.0.0.0", "port": 5000, "debug": False},
            daemon=True  # 守护线程：UI关闭时，Flask自动退出
        )
        flask_thread.start()
        print("✅ Flask后台已启动，监听地址：http://0.0.0.0:5000")
    else:
        print("⚠️ Flask后台未启动，接口功能不可用")

# ========== 原有UI初始化逻辑 ==========
app = MainWin(MainController())

if __name__ == "__main__":
    # 第一步：启动Flask后台服务
    start_app_services()
    # 第二步：启动UI主循环（阻塞）
    app.mainloop()