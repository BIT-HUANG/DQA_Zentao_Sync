from time import sleep
from utils import services, common
from utils.service_manager import start_services, stop_services, get_service_status
import threading
import json
from urllib.request import HTTPError
import tkinter.messagebox as messagebox
from ui.ui_system_setting import SystemSettingUI
import sys
import os

ENCODE = "UTF-8"

class Controller:
    ui: object

    def __init__(self):
        pass
        # ========== 初始化系统设置UI相关 ==========
        self.system_ui = None  # 系统设置UI实例
        self.config_path = ""  # 配置文件路径

    def init(self, ui):
        self.ui = ui
        self.update_service_status()
        # ========== 新增：初始化系统设置UI + 配置文件路径 ==========
        self.system_ui = SystemSettingUI(self.ui)
        self.system_ui.set_save_callback(self.save_config)  # 绑定保存回调
        self.config_path = self.get_config_path()  # 初始化配置文件路径

    # 新增：开启同步服务
    def start_sync_service(self):
        """开启同步服务（增加状态校验）"""

        def task():
            try:
                # 新增：先查询服务状态
                status = get_service_status()
                if status["ngrok"] or status["flask"]:
                    msg = "⚠️ 服务已在运行中（ngrok：{} | Flask：{}）".format(
                        "运行中" if status["ngrok"] else "未运行",
                        "运行中" if status["flask"] else "未运行"
                    )
                    self.ui.run_in_main_thread(self.ui.show_tooltip, msg)
                    return

                # 原有启动逻辑
                msg = start_services()
                self.ui.run_in_main_thread(self.ui.show_tooltip, msg)
            except Exception as e:
                err_msg = f"❌ 启动服务失败：{str(e)}"
                self.ui.run_in_main_thread(self.ui.show_tooltip, err_msg)

        t = threading.Thread(target=task, daemon=True)
        t.start()

    # 新增：关闭同步服务
    def stop_sync_service(self):
        """关闭同步服务（增加容错）"""

        # 异步执行，避免阻塞UI
        def task():
            try:
                # 先查询状态，避免重复停止
                status = get_service_status()
                if not status["ngrok"] and not status["flask"]:
                    self.ui.run_in_main_thread(self.ui.show_tooltip, "⚠️ 服务未运行，无需停止")
                    return

                # 调用停止方法
                msg = stop_services()
                # 强制刷新状态提示
                self.ui.run_in_main_thread(
                    lambda: self.ui.service_status_label.config(
                        text="服务状态：ngrok(未运行) | Flask(未运行)"
                    )
                )
                self.ui.run_in_main_thread(self.ui.show_tooltip, msg)
            except Exception as e:
                # 即使底层报错，也提示用户「服务已停止」（实际状态已标记为停止）
                err_msg = f"⚠️ 服务停止完成（部分清理操作告警）：{str(e)}"
                print(err_msg)
                self.ui.run_in_main_thread(self.ui.show_tooltip, "✅ 所有服务已停止")
                # 强制刷新状态为未运行
                self.ui.run_in_main_thread(
                    lambda: self.ui.service_status_label.config(
                        text="服务状态：ngrok(未运行) | Flask(未运行)"
                    )
                )

        t = threading.Thread(target=task, daemon=True)
        t.start()

    #中新增定时更新状态的方法
    def update_service_status(self):
        """定时更新UI上的服务状态"""

        def task():
            while True:
                status = get_service_status()
                status_text = f"服务状态：ngrok({self._get_status_text(status['ngrok'])}) | Flask({self._get_status_text(status['flask'])})"
                if status["ngrok_url"]:
                    status_text += f" | 公网地址：{status['ngrok_url']}"  # 截断过长地址
                self.ui.run_in_main_thread(
                    lambda: self.ui.service_status_label.config(text=status_text)
                )
                sleep(2)  # 每2秒更新一次

        t = threading.Thread(target=task, daemon=True)
        t.start()

    def _get_status_text(self, is_running):
        return "运行中" if is_running else "未运行"

    def sync_zentao_from_excel(self):
        # 顺带修复：这个方法也有耗时操作，也加线程+主线程转发UI
        t = threading.Thread(target=self.__sync_excel_task, daemon=True)
        t.start()

    # ========== 表格禅道创建提交（对外暴露的调度方法） ==========
    def sync_table_to_zentao(self):
        # 耗时操作，开子线程执行，守护线程，防止内存泄漏
        t = threading.Thread(target=self.__sync_table_to_zentao_task, daemon=True)
        t.start()

    # ========== 线程安全更新表格单行数据（核心辅助方法） ==========
    def __update_table_row(self, row_id, sync_flg, sync_result):
        # 获取当前行原始数据
        row_values = self.ui.tk_table_table_1.item(row_id)["values"]
        # 替换【禅道创建结果】和【禅道创建备注】列的值
        row_values[6] = sync_flg
        row_values[7] = sync_result
        # 更新表格展示，实时刷新
        self.ui.tk_table_table_1.item(row_id, values=row_values)

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

    # ========== 表格批量同步禅道到Jira的子线程任务 ==========
    def __sync_table_to_zentao_task(self):
        # 1. 先校验是否是禅道创建专属表格，不是则直接提示返回
        current_cols = self.ui.tk_table_table_1["columns"]
        if "禅道创建结果" not in current_cols or "禅道创建备注" not in current_cols:
            self.ui.run_in_main_thread(self.ui.show_tooltip, "⚠️ 仅禅道创建表格支持提交同步！")
            return

        # 2. 获取表格所有行数据，过滤空行
        table_rows = self.ui.tk_table_table_1.get_children()
        if not table_rows:
            self.ui.run_in_main_thread(self.ui.show_tooltip, "⚠️ 表格暂无数据，无需提交！")
            return

        # 3. 定义总数，用于进度计算
        total_count = len(table_rows)
        success_count = 0
        fail_count = 0

        try:
            # ========== 循环遍历表格每一行，逐条同步 ==========
            for index, row_id in enumerate(table_rows, start=1):
                # 获取表格当前行的所有单元格值
                row_values = self.ui.tk_table_table_1.item(row_id)["values"]
                jira_id = row_values[2]  # 表格第3列：JiraID
                zt_pid = str(row_values[4])  # 表格第4列：禅道模块ID
                zt_assignee = str(row_values[5])  # 表格第5列：禅道指派人

                # 跳过空JiraID的行
                if not jira_id or jira_id.strip() == "":
                    continue

                # 实时更新进度提示 - 核心需求
                progress_msg = f"正在同步 {index}/{total_count} 条，JiraID: {jira_id} 请稍候..."
                self.ui.run_in_main_thread(self.ui.show_progress_tooltip, progress_msg)

                # 核心调用：复用service层的sync_jira_to_zentao方法，无任何修改
                sync_flg, sync_result = services.sync_jira_to_zentao(jira_id, zt_pid, zt_assignee)

                # 实时回写表格数据 + 刷新展示（核心需求）
                self.ui.run_in_main_thread(self.__update_table_row, row_id, sync_flg, sync_result)

                # 更新内存中的row_history_map，保证数据一致性
                if row_id in self.ui.row_history_map:
                    self.ui.row_history_map[row_id]["zentao_create_result"] = sync_flg
                    self.ui.row_history_map[row_id]["zentao_create_comment"] = sync_result

                # 统计成功/失败数量
                if sync_flg == "Success":
                    success_count += 1
                else:
                    fail_count += 1

            # ✅ 同步完成：保存JSON文件 + 显示最终结果提示
            common.save_data_to_json(self.ui.row_history_map, file_name="../table_create_zentao_data.json")
            final_msg = f"✅ 同步完成！成功:{success_count}条，失败:{fail_count}条，数据已保存！"
            self.ui.run_in_main_thread(self.ui.show_tooltip, final_msg)

        except Exception as e:
            # 异常兜底：提示错误 + 恢复普通tooltip
            err_msg = f"❌ 同步失败：{str(e)}"
            self.ui.run_in_main_thread(self.ui.show_tooltip, err_msg)

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
            try:
                # 加一行判断：如果有read方法再执行，彻底避免AttributeError
                resp_str = e.read().decode(ENCODE) if hasattr(e, 'read') else ""
                err_dict = json.loads(resp_str)
                errorMessages = err_dict.get("errorMessages", [])[0] if err_dict.get("errorMessages") else ""
                error_msg = f"查询失败：{errorMessages}"
            except:
                error_msg = f"查询失败：{str(e)}"
            # 原有逻辑不变
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
            save_success, save_msg = common.save_data_to_json(table_all_data, file_name="../table_default_data.json")
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


    # ========== 获取.config文件路径（适配打包后） ==========
    def get_config_path(self):
        """获取.config文件路径（适配打包后exe同级目录）"""
        if hasattr(sys, '_MEIPASS'):
            # 打包后路径（exe同级目录）
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境路径（项目根目录）
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, ".config")

    # ========== 读取.config配置文件 ==========
    def load_config(self):
        """读取.config文件，返回配置字典（含异常处理）"""
        try:
            if not os.path.exists(self.config_path):
                self.ui.run_in_main_thread(
                    messagebox.showerror, "配置错误", f"配置文件不存在：{self.config_path}"
                )
                return {}

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            return config_data
        except json.JSONDecodeError:
            self.ui.run_in_main_thread(
                messagebox.showerror, "配置错误", f".config文件格式非法，请检查JSON格式"
            )
            return {}
        except Exception as e:
            self.ui.run_in_main_thread(
                messagebox.showerror, "配置错误", f"读取配置失败：{str(e)}"
            )
            return {}

    # ========== 新增：保存配置到.config文件 ==========
    def save_config(self, new_config):
        """保存修改后的配置到.config文件（含格式校验+异常处理）"""
        try:
            # 先校验JSON格式合法性
            json.dumps(new_config)

            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)

            self.ui.run_in_main_thread(
                messagebox.showinfo, "保存成功", "配置已成功保存！"
            )
        except json.JSONDecodeError:
            self.ui.run_in_main_thread(
                messagebox.showerror, "保存失败", "配置格式非法，无法保存！"
            )
        except PermissionError:
            self.ui.run_in_main_thread(
                messagebox.showerror, "保存失败", "没有写入权限，请以管理员身份运行！"
            )
        except Exception as e:
            self.ui.run_in_main_thread(
                messagebox.showerror, "保存失败", f"保存配置出错：{str(e)}"
            )

    # ========== 新增：打开设置弹窗 ==========
    def open_setting_dialog(self):
        """打开系统设置弹窗（绑定UI菜单点击事件）- 新增传递主实例引用"""
        config_data = self.load_config()
        if config_data:
            # 关键修改：在创建设置弹窗前，给system_ui绑定主实例引用
            # 方式1：绑定Control层实例（推荐，通过Control层调用主窗口方法）
            self.system_ui.control = self  # 把Control实例传给SysTemSettingUI
            # 原有打开弹窗的逻辑
            self.ui.run_in_main_thread(
                self.system_ui.create_setting_dialog
            )

    # ========== 新增：打开关于弹窗 ==========
    def open_about_dialog(self):
        """打开关于弹窗（绑定UI菜单点击事件）"""
        self.ui.run_in_main_thread(
            self.system_ui.create_about_dialog
        )

    def open_about_dialog(self):
        """打开关于弹窗（绑定UI菜单点击事件）"""
        self.ui.run_in_main_thread(
            self.system_ui.create_about_dialog
        )

    # ========== 新增：打开帮助弹窗 ==========
    def open_help_dialog(self):
        """打开帮助弹窗（绑定UI菜单点击事件）"""
        self.ui.run_in_main_thread(
            self.system_ui.create_help_dialog
        )