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

    # ========== 无参刷新表格公共方法 ==========
    def refresh_table_data(self):
        """无参刷新表格数据，复用原有查询逻辑，无点击事件，专门给update执行完后自动调用"""
        t = threading.Thread(target=self.__search_task, daemon=True)
        t.start()

    # ========== 添加禅道记录 按钮事件方法 ==========
    def add_zentao_record(self, evt):
        print("添加禅道记录按钮事件处理:", evt)
        t = threading.Thread(target=self.__add_zentao_record_task, daemon=True)
        t.start()

    # ========== 提交禅道创建 按钮事件方法 ==========
    def submit_zentao_create(self, evt):
        print("提交禅道创建按钮事件处理:", evt)
        t = threading.Thread(target=self.__submit_zentao_create_task, daemon=True)
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
        self.ui.run_in_main_thread(self.ui.show_progress_tooltip, "正在读取表格数据，请稍候...")
        try:
            # 1. 获取表格中所有的原始完整数据
            table_all_data = list(self.ui.row_history_map.values())

            # 2. 判断是否有数据
            if not table_all_data:
                tip_msg = "表格暂无数据！"
                self.ui.run_in_main_thread(self.ui.show_tooltip, tip_msg)
                print(tip_msg)
                return

            # 3. 保存JSON文件
            save_success, save_msg = common.save_data_to_json(table_all_data)
            print(save_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, save_msg)

            # 4. 更新comment - 接收返回的【统计结果】和【弹窗详情文案】
            result, detail_popup_msg = services.sync_zentao_history_to_jira(table_all_data, self.ui)
            print(result)  # 控制台打印统计字典
            print(detail_popup_msg)  # 控制台打印完整详情

            # ========== 核心新增：同步完成后，弹出【详细汇总弹窗】 ==========
            self.ui.run_in_main_thread(self.ui.show_popup, "禅道历史同步完成", detail_popup_msg)

            # 可选：底部简短提示（如果你的show_tooltip是气泡提示，弹窗是独立弹窗，可保留这行简短提示）
            short_tip = f"同步完成！总计：{len(table_all_data)}条 | 成功：{result['success']}条 | 跳过：{result['skip']}条 | 无需同步：{result['no_sync']}条 | 失败：{result['fail']}条"
            self.ui.run_in_main_thread(self.ui.show_tooltip, short_tip)

            # ========== 同步成功后，自动刷新表格数据==========
            print("🔄 同步成功，开始自动刷新表格数据...")
            self.ui.run_in_main_thread(self.ui.show_tooltip, "🔄 同步成功，正在刷新最新数据，请稍候...", False)
            sleep(0.5) # 短暂延时，让用户看到提示，体验更好
            self.refresh_table_data() # 调用新增的无参刷新方法

        except Exception as e:
            error_msg = f"同步禅道历史到Jira失败：{str(e)}"
            print(error_msg)
            self.ui.run_in_main_thread(self.ui.load_error_table, error_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, error_msg)
            return

    # ========== 添加禅道记录 子线程任务 ==========
    def __add_zentao_record_task(self):
        # 1. 显示加载提示，和你的其他方法一致，禁用自动隐藏
        self.ui.run_in_main_thread(self.ui.show_tooltip, "正在执行添加禅道记录操作，请稍候...", False)
        try:
            # ===================== 业务逻辑占位 - 替换区 =====================
            print("添加记录按钮任务")
            # 这里后续替换为真实的 service.py 业务调用：比如 services.add_zentao_record(xxx)
            # =================================================================

            # 执行成功后的UI提示
            self.ui.run_in_main_thread(self.ui.show_tooltip, "✅ 禅道记录添加成功！")

        except Exception as e:
            # 统一异常捕获+UI错误提示，和你的其他方法完全一致
            error_msg = f"❌ 禅道记录添加失败：{str(e)}"
            print(error_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, error_msg)
            return

    # ========== 提交禅道创建 子线程任务 ==========
    def __submit_zentao_create_task(self):
        # 1. 显示加载提示，和你的其他方法一致，禁用自动隐藏
        self.ui.run_in_main_thread(self.ui.show_tooltip, "正在批量提交禅道创建，请稍候...", False)
        try:
            # ===================== 业务逻辑占位 - 替换区 =====================
            print("提交记录按钮任务")
            # 这里后续替换为真实的 service.py 业务调用：比如 services.submit_zentao_create(xxx)
            # =================================================================

            # 执行成功后的UI提示
            self.ui.run_in_main_thread(self.ui.show_tooltip, "✅ 禅道工单批量创建提交成功！")

        except Exception as e:
            # 统一异常捕获+UI错误提示，和你的其他方法完全一致
            error_msg = f"❌ 禅道工单创建提交失败：{str(e)}"
            print(error_msg)
            self.ui.run_in_main_thread(self.ui.show_tooltip, error_msg)
            return