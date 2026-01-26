# service_manager.py
import threading
import time
import sys
import os
import ngrok
from flask import Flask
import asyncio
from libmirror import mconfig

# 全局变量存储服务状态和线程对象
service_status = {
    "flask_running": False,
    "ngrok_running": False,
    "flask_thread": None,
    "ngrok_thread": None,
    "ngrok_listener": None,
    "ngrok_loop": None
}

# Flask应用实例（和portal.py保持一致）
if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
    app = Flask(__name__, root_path=base_path)
else:
    app = Flask(__name__)

# 导入Flask路由（复用portal.py的接口）
try:
    from portal import dqa_get_zentao_webhook, hello_world

    app.add_url_rule('/dqa_get_zentao_webhook', view_func=dqa_get_zentao_webhook, methods=['POST'])
    app.add_url_rule('/hello_world', view_func=hello_world, methods=['GET', 'POST'])
except ImportError as e:
    print(f"导入Flask路由失败：{e}")


def start_ngrok(port=5000):
    """启动ngrok内网穿透（新增事件循环存储）"""
    rgrok_auth_token = mconfig.get_ngrok_auth_token()
    global service_status
    try:
        # 显式创建asyncio事件循环并存储
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        service_status["ngrok_loop"] = loop

        # 启动ngrok
        listener = ngrok.forward(
            port,
            authtoken=rgrok_auth_token  # 替换为你的token
        )
        service_status["ngrok_listener"] = listener
        service_status["ngrok_running"] = True
        print(f"✅ ngrok启动成功，公网地址：{listener.url()}")

        # 保持ngrok线程存活
        while service_status["ngrok_running"]:
            time.sleep(1)
    except Exception as e:
        print(f"❌ ngrok启动失败：{str(e)}")
        service_status["ngrok_running"] = False
    finally:
        # 清理事件循环
        if service_status["ngrok_loop"]:
            service_status["ngrok_loop"].close()
            service_status["ngrok_loop"] = None

def start_flask(port=5000):
    """启动Flask服务"""
    global service_status
    try:
        service_status["flask_running"] = True
        print("✅ Flask服务启动中...")
        app.run(
            host="0.0.0.0",
            port=port,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        print(f"❌ Flask启动失败：{str(e)}")
        service_status["flask_running"] = False


def start_services():
    """启动所有服务（先ngrok，后Flask）"""
    global service_status

    # 检查服务是否已运行
    if service_status["ngrok_running"] or service_status["flask_running"]:
        print("⚠️ 服务已在运行中")
        return "服务已在运行中"

    # 1. 启动ngrok（异步线程）
    service_status["ngrok_thread"] = threading.Thread(
        target=start_ngrok,
        daemon=True
    )
    service_status["ngrok_thread"].start()

    # 等待ngrok启动（最多5秒）
    wait_time = 0
    while wait_time < 5 and not service_status["ngrok_running"]:
        time.sleep(0.5)
        wait_time += 0.5

    # 2. 启动Flask（异步线程）
    service_status["flask_thread"] = threading.Thread(
        target=start_flask,
        daemon=True
    )
    service_status["flask_thread"].start()

    # 等待Flask启动
    time.sleep(1)

    if service_status["ngrok_running"] and service_status["flask_running"]:
        msg = f"✅ 同步服务启动成功！ngrok地址：{service_status['ngrok_listener'].url()}"
    elif service_status["flask_running"]:
        msg = "✅ Flask服务启动成功（ngrok启动失败）"
    else:
        msg = "❌ 服务启动失败"

    print(msg)
    return msg


def stop_services():
    """停止所有服务（修复ngrok关闭逻辑）"""
    global service_status

    # 1. 停止ngrok（核心修复：手动管理事件循环）
    if service_status["ngrok_running"]:
        try:
            # 标记状态为停止（让ngrok线程的while循环退出）
            service_status["ngrok_running"] = False

            # 关闭ngrok listener（处理asyncio事件循环）
            if service_status["ngrok_listener"]:
                # 方案1：如果listener.close()是异步方法
                if service_status["ngrok_loop"] and service_status["ngrok_loop"].is_running():
                    # 在原有循环中执行关闭操作
                    asyncio.run_coroutine_threadsafe(
                        service_status["ngrok_listener"].close(),
                        service_status["ngrok_loop"]
                    )
                else:
                    # 方案2：兼容同步关闭（直接调用，忽略循环错误）
                    try:
                        service_status["ngrok_listener"].close()
                    except RuntimeError as e:
                        if "no running event loop" in str(e):
                            print("⚠️ ngrok事件循环已销毁，强制停止线程")
                        else:
                            raise e

                service_status["ngrok_listener"] = None

            # 等待ngrok线程退出
            if service_status["ngrok_thread"]:
                service_status["ngrok_thread"].join(timeout=2)
                service_status["ngrok_thread"] = None

            # 清理事件循环
            if service_status["ngrok_loop"]:
                service_status["ngrok_loop"].close()
                service_status["ngrok_loop"] = None

            print("✅ ngrok服务已停止")
        except Exception as e:
            print(f"⚠️ ngrok停止时出现异常：{str(e)}")
            # 即使报错，也强制标记为停止
            service_status["ngrok_running"] = False
            service_status["ngrok_listener"] = None

    # 2. 停止Flask（Flask无法直接关闭，标记状态）
    if service_status["flask_running"]:
        service_status["flask_running"] = False
        print("✅ Flask服务已标记为停止（需重启程序完全关闭）")

    return "✅ 所有服务已停止"


def get_service_status():
    """获取服务状态"""
    return {
        "ngrok": service_status["ngrok_running"],
        "flask": service_status["flask_running"],
        "ngrok_url": service_status["ngrok_listener"].url() if service_status["ngrok_listener"] else ""
    }