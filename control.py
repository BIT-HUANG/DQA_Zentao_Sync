from time import sleep

from utils import services, common
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
        self.ui.run_in_main_thread(self.ui.show_progress_tooltip, "正在读取表格数据并保存，请稍候...")
        try:
            # 1. 获取表格中所有的原始完整数据
            table_all_data = list(self.ui.row_history_map.values())

            # 2. 判断是否有数据
            if not table_all_data:
                tip_msg = "表格暂无数据，无需保存！"
                self.ui.run_in_main_thread(self.ui.show_tooltip, tip_msg)
                print(tip_msg)
                return

            # 3. 保存JSON文件
            save_success, save_msg = common.save_data_to_json(table_all_data)
            print(save_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, save_msg)

            # 4. 更新comment
            result = services.sync_zentao_history_to_jira(table_all_data, self.ui)
            print(result)

            # ========== ✅ 核心修改：精准的文案拼接，完全匹配你的期望 ==========
            success_count = result.get("success", 0)
            no_sync_count = result.get("no_sync", 0)
            skip_count = result.get("skip", 0)
            fail_count = result.get("fail", 0)
            total_count = len(table_all_data)
            # 最终文案：无禅道历史=跳过，无需同步=无需同步，真实失败=失败，和你要的一模一样
            success_msg = f"同步完成！总计：{total_count}条 | 成功：{success_count}条 | 跳过：{skip_count}条 | 无需同步：{no_sync_count}条 | 失败：{fail_count}条"
            print(success_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, success_msg)

        except Exception as e:
            error_msg = f"同步禅道历史到Jira失败：{str(e)}"
            print(error_msg)
            self.ui.run_in_main_thread(self.ui.load_error_table, error_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, error_msg)
            return