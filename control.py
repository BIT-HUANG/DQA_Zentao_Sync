from time import sleep

from utils import services
import threading
import json
from urllib.request import HTTPError

ENCODE = "UTF-8"

class Controller:
    ui: object

    def __init__(self):
        pass

    def init(self, ui):
        self.ui = ui

    def sync_zentao_from_excel(self):
        # 顺带修复：这个方法也有耗时操作，也加线程+主线程转发UI
        t = threading.Thread(target=self.__sync_excel_task, daemon=True)
        t.start()

    def search(self, evt):
        print("更新查询事件处理:", evt)
        t = threading.Thread(target=self.__search_task, daemon=True)
        t.start()

    def update(self, evt):
        print("更新按钮事件处理:", evt)
        t = threading.Thread(target=self.__update_task, daemon=True)
        t.start()

    # ========== 同步Excel的子线程任务 ==========
    def __sync_excel_task(self):
        self.ui.run_in_main_thread(self.ui.show_tooltip, "正在同步Excel到禅道，请稍候...")
        try:
            services.sync_excel()
            self.ui.run_in_main_thread(self.ui.show_tooltip, "Excel同步完成！")
        except Exception as e:
            self.ui.run_in_main_thread(self.ui.show_tooltip, f"同步失败：{str(e)}")

    # ========== 核心查询任务 ==========
    def __search_task(self):
        jql_text = self.ui.get_jql_content()
        if not jql_text:
            tip_msg = "请输入JQL查询语句！"
            print(tip_msg)
            # 子线程调用UI → 通过主线程工具函数转发
            self.ui.run_in_main_thread(self.ui.load_error_table, tip_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, tip_msg)
            return

        # 加载提示 → 主线程执行
        self.ui.run_in_main_thread(self.ui.show_tooltip, "正在查询数据，请稍候...", False)

        try:
            # 这里是纯业务逻辑，子线程执行完全安全，无任何问题
            jira_list = services.get_jira_sync_list(jql_text)
            if isinstance(jira_list, HTTPError):
                raise jira_list
            # self.ui.run_in_main_thread(self.ui.show_tooltip, f"共：{len(jira_list)} 条数据，解析中。。。", False)
            data_list = services.get_jira_with_zentao(jira_list,self.ui)

            # 增加None判空【双保险】，防止data_list是None
            if not data_list:
                self.ui.run_in_main_thread(self.ui.load_empty_table)
                self.ui.run_in_main_thread(self.ui.show_tooltip, "查询完成，无匹配数据！")
                return

            # 加载表格+成功提示 → 全部主线程执行
            self.ui.run_in_main_thread(self.ui.load_default_table, data_list)
            self.ui.run_in_main_thread(self.ui.show_tooltip, "查询完成！")

        except Exception as e:
            # 错误提示 → 主线程执行，
            err_dict = json.loads(e.read().decode(ENCODE))
            errorMessages = err_dict.get("errorMessages", [])[0] if err_dict.get("errorMessages") else ""
            error_msg = f"查询失败：{errorMessages}"
            print(error_msg)
            self.ui.run_in_main_thread(self.ui.load_error_table, error_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, error_msg)
            return

    # ========== 核心更新任务 ==========
    def __update_task(self):
        self.ui.run_in_main_thread(self.ui.show_tooltip, "正在进行双向同步，请稍候...")
        try:
            print("Test SYNC ....")
            self.ui.after(2000, lambda:
            self.ui.run_in_main_thread(self.ui.show_tooltip, "骗你的，这功能还没做！")
                          )
        except Exception as e:
            self.ui.run_in_main_thread(self.ui.show_tooltip, f"双向同步失败：{str(e)}")
