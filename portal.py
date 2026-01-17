# -*- coding: utf-8 -*-
from flask import Flask, request, Response  # 新增导入Response
import sys
import os
import json  # 新增导入json模块

# 适配打包后的运行环境 & 普通python运行环境
if getattr(sys, "frozen", False):
    base_path = sys._MEIPASS
    app = Flask(__name__, root_path=base_path)
else:
    app = Flask(__name__)


# ========== 你的核心接口：dqa_get_zentao_webhook ==========
@app.route('/dqa_get_zentao_webhook', methods=['POST'])
def dqa_get_zentao_webhook():
    receive_data = None
    try:
        # 【核心优化】万能数据接收逻辑 - 兼容所有请求格式
        try:
            receive_data = request.get_json(force=True, silent=True)
        except:
            receive_data = None

        if not receive_data:
            receive_data = request.form.to_dict()

        if not receive_data:
            receive_data = request.get_data(as_text=True)

        # 打印数据（控制台看正常中文）
        print("=" * 80)
        print(f"【禅道WebHook】接收到数据：")
        print(receive_data)
        print("=" * 80)

        # ========== 核心修改：替换jsonify，返回【原生中文】的JSON响应，关闭Unicode转义 ==========
        res_data = {
            "code": 200,
            "status": "success",
            "msg": "禅道WebHook数据接收成功",
            "data": "111"
        }
        # 关键配置：ensure_ascii=False → 强制不转义中文，indent=None → 紧凑格式返回
        json_str = json.dumps(res_data, ensure_ascii=False, indent=None)
        return Response(json_str, content_type='application/json; charset=utf-8'), 200

    except Exception as e:
        print("=" * 80)
        print(f"【禅道WebHook】接收数据失败，异常信息：{str(e)}")
        print("=" * 80)
        # 异常返回也做中文兼容
        err_data = {
            "code": 500,
            "status": "error",
            "msg": f"接收失败: {str(e)}"
        }
        json_str = json.dumps(err_data, ensure_ascii=False, indent=None)
        return Response(json_str, content_type='application/json; charset=utf-8'), 500


def start_flask_server(host="0.0.0.0", port=5000, debug=False):
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    print("Flask后台单独启动，测试接口：http://127.0.0.1:5000/dqa_get_zentao_webhook")
    start_flask_server(debug=True)