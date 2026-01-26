import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import json
import sys
import os
# 导入你新增的 ConfigManager（确保路径正确）
from utils.common import ConfigManager


class SystemSettingUI:
    """系统设置相关弹窗UI类（适配ConfigManager，保持原生类型）"""

    def __init__(self, parent):
        self.control = None  # 新增：保存Control层实例
        self.main_window = None  # 新增：保存主窗口UI实例
        self.parent = parent  # 主窗口引用
        self.config_manager = ConfigManager(".config")  # 初始化配置管理器
        self.original_config = {}  # 存储原始配置（用于重置）
        self.setting_dialog = None  # 设置弹窗
        self.about_dialog = None  # 关于弹窗
        self.help_dialog = None  # 帮助弹窗

        # 存储输入控件引用（区分不同类型：单行/多行/分组）
        self.config_widgets = {}

    def create_setting_dialog(self):
        """创建设置弹窗 - 新增主实例引用保留 + 优化滚动布局"""
        print("配置文件绝对路径：", self.config_manager.get_config_path())
        print("读取到的配置内容：", self.config_manager.config)

        self.original_config = json.loads(json.dumps(self.config_manager.config))

        # 创建设置弹窗（保留父窗口引用）
        self.setting_dialog = tk.Toplevel(self.parent)
        self.setting_dialog.title("系统设置")
        self.setting_dialog.geometry("1000x700")  # 加宽弹窗，适配键值对
        self.setting_dialog.resizable(True, True)
        self.setting_dialog.transient(self.parent)
        self.setting_dialog.grab_set()

        # 弹窗居中显示（优化）
        self.setting_dialog.withdraw()
        self.setting_dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        dialog_w = self.setting_dialog.winfo_width()
        dialog_h = self.setting_dialog.winfo_height()
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        self.setting_dialog.geometry(f"+{x}+{y}")
        self.setting_dialog.deiconify()

        # ========== 滚动容器（优化宽度适配）==========
        main_frame = ttk.Frame(self.setting_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame, bd=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_y.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scroll_y.set)

        scrollable_frame = ttk.Frame(canvas, padding=(5, 5))
        scrollable_frame_id = canvas.create_window(
            (0, 0),
            window=scrollable_frame,
            anchor="nw"
        )

        # 优化滚动区域更新逻辑（修复宽度适配问题）
        def update_scroll_region(event):
            # 更新滚动区域
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 同步滚动容器宽度到canvas宽度（去掉固定值，适配窗口缩放）
            if event.widget == canvas:
                canvas.itemconfig(scrollable_frame_id, width=canvas.winfo_width())

        # 绑定滚动更新事件（优化）
        self.setting_dialog.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_scroll_region)
        scrollable_frame.bind("<Configure>", update_scroll_region)

        # ========== 渲染配置项（原有逻辑保留）==========
        row = 0
        self.config_widgets.clear()

        for key, value in self.config_manager.config.items():
            ttk.Label(scrollable_frame, text=key, font=("微软雅黑", 9, "bold")).grid(
                row=row, column=0, sticky="w", padx=5, pady=10
            )

            # 分类型渲染
            if isinstance(value, dict):
                # 判断是否为键值对型dict
                is_kv_dict = all(isinstance(v, str) for v in value.values())
                if is_kv_dict:
                    # 键值对dict（旧格式兼容）
                    self._render_dict_kv_widget(scrollable_frame, key, value, row)
                else:
                    # 普通嵌套dict
                    self._render_dict_widget(scrollable_frame, key, value, row)
            elif isinstance(value, list):
                # 特殊处理：不同List[Dict]类型
                if key == "jira_project_name_list":
                    self._render_list_dict_widget(scrollable_frame, key, value, row)
                elif key == "create_zentao_map":
                    self._render_zentao_list_widget(scrollable_frame, key, value, row)
                else:
                    # 普通列表 → Listbox+增删
                    self._render_list_widget(scrollable_frame, key, value, row)
            else:
                # 基础类型
                self._render_basic_widget(scrollable_frame, key, value, row)

            row += 1

        # ========== 按钮区域（原有逻辑保留）==========
        btn_frame = ttk.Frame(self.setting_dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=(20, 10))

        ttk.Button(btn_frame, text="取消", command=self.on_cancel_setting).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置", command=self.on_reset_setting).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="确认", command=self.on_confirm_setting).pack(side=tk.LEFT, padx=5)

        # 优化列权重（让输入框自适应宽度）
        scrollable_frame.columnconfigure(1, weight=1)

        # ========== 新增：确保弹窗关闭时释放资源 ==========
        self.setting_dialog.protocol("WM_DELETE_WINDOW", self.on_cancel_setting)

    def _render_zentao_list_widget(self, parent, key, value, row):
        """渲染禅道项目映射列表（List[Dict]，三字段：zt_pname/zt_pid/zt_assignee）"""
        # ========== 外层容器：控制整体宽度（跟随弹窗自适应） ==========
        zentao_container = ttk.Frame(parent)
        zentao_container.grid(row=row, column=1, padx=5, pady=8, sticky="we")
        # 关键布局：4列（项目名称/项目ID/负责人/操作），仅负责人列自适应宽度
        zentao_container.columnconfigure(0, weight=0)  # 项目名称列：固定宽度
        zentao_container.columnconfigure(1, weight=0)  # 项目ID列：固定宽度
        zentao_container.columnconfigure(2, weight=1)  # 负责人列：自适应宽度
        zentao_container.columnconfigure(3, weight=0)  # 操作列：固定宽度

        # 1. 表头行（严格按列对齐）
        ttk.Label(zentao_container, text="项目名称", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=0, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(zentao_container, text="项目ID", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=1, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(zentao_container, text="负责人", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=2, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(zentao_container, text="操作", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=3, padx=(5, 10), pady=3, sticky="w"
        )

        # 2. 内容容器：高度随内容自适应（无固定高度）
        content_frame = ttk.Frame(zentao_container)
        content_frame.grid(row=1, column=0, columnspan=4, padx=0, pady=3, sticky="nsew")
        # 继承列布局
        content_frame.columnconfigure(0, weight=0)
        content_frame.columnconfigure(1, weight=0)
        content_frame.columnconfigure(2, weight=1)
        content_frame.columnconfigure(3, weight=0)

        # 3. 存储控件引用
        zentao_widgets = []
        self.config_widgets[key] = {
            "type": "zentao_list",  # 新增类型：禅道项目列表
            "widget": content_frame,
            "original_value": value,
            "zentao_widgets": zentao_widgets,
            "content_frame": content_frame,
            "zentao_container": zentao_container
        }

        # 4. 渲染初始List[Dict]数据
        for zt_row, item in enumerate(value):
            pname = item.get("zt_pname", "")
            pid = item.get("zt_pid", "")
            assignee = item.get("zt_assignee", "")
            self._add_zentao_row(content_frame, zentao_widgets, pname, pid, assignee, zt_row)

        # 5. 新增按钮：放在操作列（第3列），靠左对齐
        def add_new_row():
            """新增禅道项目行并更新高度"""
            new_row = len(zentao_widgets)
            self._add_zentao_row(content_frame, zentao_widgets, "", "", "", new_row)
            # 触发父容器刷新，更新高度
            zentao_container.update_idletasks()
            parent.update_idletasks()

        ttk.Button(zentao_container, text="新增", width=6, command=add_new_row).grid(
            row=2, column=3, padx=(5, 10), pady=5, sticky="w"
        )

        # 初始化高度适配
        zentao_container.update_idletasks()
        parent.update_idletasks()

    def _add_zentao_row(self, parent, zentao_widgets, init_pname, init_pid, init_assignee, row):
        """新增一行禅道项目键值对控件（删除行后更新高度）"""
        # 1. 项目名称输入框：固定宽度
        pname_entry = ttk.Entry(parent, font=("微软雅黑", 9), width=20)
        pname_entry.insert(0, init_pname)
        pname_entry.grid(row=row, column=0, padx=5, pady=3, sticky="we")

        # 2. 项目ID输入框：固定宽度
        pid_entry = ttk.Entry(parent, font=("微软雅黑", 9), width=10)
        pid_entry.insert(0, init_pid)
        pid_entry.grid(row=row, column=1, padx=5, pady=3, sticky="we")

        # 3. 负责人输入框：自适应宽度
        assignee_entry = ttk.Entry(parent, font=("微软雅黑", 9))
        assignee_entry.insert(0, init_assignee)
        assignee_entry.grid(row=row, column=2, padx=5, pady=3, sticky="we")

        # 4. 删除按钮：固定宽度，删除后更新高度
        del_btn = ttk.Button(parent, text="删除", width=6)

        # 删除逻辑
        def del_zentao_row():
            # 移除控件
            pname_entry.grid_forget()
            pid_entry.grid_forget()
            assignee_entry.grid_forget()
            del_btn.grid_forget()
            # 从列表移除
            for i, (pn_e, pid_e, ass_e, d_b) in enumerate(zentao_widgets):
                if pn_e == pname_entry and pid_e == pid_entry and ass_e == assignee_entry and d_b == del_btn:
                    zentao_widgets.pop(i)
                    break
            # 重新排列剩余行
            for new_row, (pn_e, pid_e, ass_e, d_b) in enumerate(zentao_widgets):
                pn_e.grid(row=new_row, column=0, padx=5, pady=3, sticky="we")
                pid_e.grid(row=new_row, column=1, padx=5, pady=3, sticky="we")
                ass_e.grid(row=new_row, column=2, padx=5, pady=3, sticky="we")
                d_b.grid(row=new_row, column=3, padx=5, pady=3, sticky="w")
            # 刷新父容器高度
            parent.update_idletasks()
            if zentao_widgets and hasattr(zentao_widgets[0][0].master, 'master'):
                zentao_widgets[0][0].master.master.update_idletasks()

        del_btn.configure(command=del_zentao_row)
        del_btn.grid(row=row, column=3, padx=5, pady=3, sticky="w")

        # 添加到控件列表
        zentao_widgets.append((pname_entry, pid_entry, assignee_entry, del_btn))

    def _render_basic_widget(self, parent, key, value, row):
        """渲染基础类型控件（字符串/数字/布尔）"""
        entry = ttk.Entry(parent, font=("微软雅黑", 9))
        entry.insert(0, str(value) if value is not None else "")
        entry.grid(row=row, column=1, padx=5, pady=3, sticky="we")
        self.config_widgets[key] = {
            "type": "basic",
            "widget": entry,
            "original_value": value
        }

    def _render_list_widget(self, parent, key, value, row):
        """渲染普通列表控件（Listbox + 新增/删除按钮，支持增删操作）"""
        # 创建列表容器（横向排列 Listbox + 按钮）
        list_container = ttk.Frame(parent)
        list_container.grid(row=row, column=1, padx=5, pady=3, sticky="we")
        list_container.columnconfigure(0, weight=1)  # Listbox 占满宽度

        # 1. Listbox 显示列表项
        listbox = tk.Listbox(list_container, font=("微软雅黑", 9), height=6)
        listbox.grid(row=0, column=0, rowspan=2, padx=5, pady=3, sticky="nsew")
        # 填充初始数据
        for item in value:
            listbox.insert(tk.END, item)

        # 2. 滚动条（适配长列表）
        list_scroll = ttk.Scrollbar(list_container, orient="vertical", command=listbox.yview)
        list_scroll.grid(row=0, column=1, rowspan=2, sticky="ns")
        listbox.configure(yscrollcommand=list_scroll.set)

        # 3. 按钮容器（新增/删除）
        btn_container = ttk.Frame(list_container)
        btn_container.grid(row=0, column=2, padx=5, pady=3, sticky="n")

        # 新增按钮
        def add_item():
            new_item = tk.simpledialog.askstring("新增项", f"请输入{key}的新值：")
            if new_item and new_item.strip():
                listbox.insert(tk.END, new_item.strip())

        ttk.Button(btn_container, text="新增", command=add_item).pack(fill=tk.X, pady=2)

        # 删除按钮
        def del_item():
            selected = listbox.curselection()
            if selected:
                listbox.delete(selected[0])

        ttk.Button(btn_container, text="删除选中", command=del_item).pack(fill=tk.X, pady=2)

        # 存储控件引用
        self.config_widgets[key] = {
            "type": "list",
            "widget": listbox,  # 核心：保存 Listbox 引用
            "original_value": value
        }

    def _render_list_dict_widget(self, parent, key, value, row):
        """渲染列表嵌套字典控件（List[Dict]，支持新增/删除键值对）"""
        # ========== 外层容器：控制整体宽度（跟随弹窗自适应） ==========
        list_dict_container = ttk.Frame(parent)
        list_dict_container.grid(row=row, column=1, padx=5, pady=8, sticky="we")
        # 关键布局：3列（键/值/操作），仅值列自适应宽度
        list_dict_container.columnconfigure(0, weight=0)  # 键列：固定宽度
        list_dict_container.columnconfigure(1, weight=1)  # 值列：自适应宽度（核心）
        list_dict_container.columnconfigure(2, weight=0)  # 操作列：固定宽度

        # 1. 表头行（严格按列对齐）
        ttk.Label(list_dict_container, text="键", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=0, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(list_dict_container, text="值", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=1, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(list_dict_container, text="操作", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=2, padx=(5, 10), pady=3, sticky="w"
        )

        # 2. 内容容器：高度随内容自适应（无固定高度）
        content_frame = ttk.Frame(list_dict_container)
        content_frame.grid(row=1, column=0, columnspan=3, padx=0, pady=3, sticky="nsew")
        # 继承列布局
        content_frame.columnconfigure(0, weight=0)
        content_frame.columnconfigure(1, weight=1)
        content_frame.columnconfigure(2, weight=0)

        # 3. 存储键值对控件引用
        list_dict_widgets = []
        self.config_widgets[key] = {
            "type": "list_dict",  # 新增类型：列表嵌套字典
            "widget": content_frame,
            "original_value": value,
            "list_dict_widgets": list_dict_widgets,
            "content_frame": content_frame,
            "list_dict_container": list_dict_container
        }

        # 4. 渲染初始List[Dict]数据
        for ld_row, item in enumerate(value):
            # 提取Dict中的唯一键值对
            k = list(item.keys())[0] if item else ""
            v = list(item.values())[0] if item else ""
            self._add_list_dict_row(content_frame, list_dict_widgets, k, v, ld_row)

        # 5. 新增按钮：放在操作列（第2列），和删除按钮同一列、靠左对齐
        def add_new_row():
            """新增List[Dict]行并更新高度"""
            new_row = len(list_dict_widgets)
            self._add_list_dict_row(content_frame, list_dict_widgets, "", "", new_row)
            # 触发父容器刷新，更新高度
            list_dict_container.update_idletasks()
            parent.update_idletasks()

        ttk.Button(list_dict_container, text="新增", width=6, command=add_new_row).grid(
            row=2, column=2, padx=(5, 10), pady=5, sticky="w"
        )

        # 初始化高度适配
        list_dict_container.update_idletasks()
        parent.update_idletasks()

    def _add_list_dict_row(self, parent, list_dict_widgets, init_key, init_value, row):
        """新增一行List[Dict]键值对控件（删除行后更新高度）"""
        # 1. 键输入框：固定宽度
        key_entry = ttk.Entry(parent, font=("微软雅黑", 9), width=20)
        key_entry.insert(0, init_key)
        key_entry.grid(row=row, column=0, padx=5, pady=3, sticky="we")

        # 2. 值输入框：自适应宽度
        value_entry = ttk.Entry(parent, font=("微软雅黑", 9))
        value_entry.insert(0, init_value)
        value_entry.grid(row=row, column=1, padx=5, pady=3, sticky="we")

        # 给值输入框加横向滚动（适配长文本）
        def scroll_value_entry(event):
            if event.delta > 0:
                value_entry.xview_scroll(-1, "units")
            else:
                value_entry.xview_scroll(1, "units")

        value_entry.bind("<MouseWheel>", scroll_value_entry)

        # 3. 删除按钮：固定宽度，删除后更新高度
        del_btn = ttk.Button(parent, text="删除", width=6)

        # 删除逻辑（新增：删除后更新高度）
        def del_list_dict_row():
            # 移除控件
            key_entry.grid_forget()
            value_entry.grid_forget()
            del_btn.grid_forget()
            # 从列表移除
            for i, (k_e, v_e, d_b) in enumerate(list_dict_widgets):
                if k_e == key_entry and v_e == value_entry and d_b == del_btn:
                    list_dict_widgets.pop(i)
                    break
            # 重新排列剩余行
            for new_row, (k_e, v_e, d_b) in enumerate(list_dict_widgets):
                k_e.grid(row=new_row, column=0, padx=5, pady=3, sticky="we")
                v_e.grid(row=new_row, column=1, padx=5, pady=3, sticky="we")
                d_b.grid(row=new_row, column=2, padx=5, pady=3, sticky="w")
            # 关键：删除后刷新父容器高度
            parent.update_idletasks()
            # 向上找外层容器并刷新（确保整体高度更新）
            if list_dict_widgets and hasattr(list_dict_widgets[0][0].master, 'master'):
                list_dict_widgets[0][0].master.master.update_idletasks()

        del_btn.configure(command=del_list_dict_row)
        del_btn.grid(row=row, column=2, padx=5, pady=3, sticky="w")  # 左对齐，不遮挡

        # 添加到控件列表
        list_dict_widgets.append((key_entry, value_entry, del_btn))

    def _render_dict_widget(self, parent, key, value, row):
        """渲染嵌套dict控件（区分普通dict和键值对dict）"""
        # 先判断是否为键值对型dict（自定义规则：值为字符串的dict）
        is_kv_dict = all(isinstance(v, str) for v in value.values())
        if is_kv_dict:
            # 键值对型dict → 用新增的kv控件
            self._render_dict_kv_widget(parent, key, value, row)
            return

        # 普通嵌套dict → 原有分组框逻辑
        dict_frame = ttk.LabelFrame(parent, text=f"{key}（嵌套配置）", padding=(10, 10))
        dict_frame.grid(row=row, column=1, padx=5, pady=10, sticky="we")
        dict_frame.columnconfigure(1, weight=1)

        self.config_widgets[key] = {
            "type": "dict",
            "widget": dict_frame,
            "original_value": value,
            "children": {}
        }

        child_row = 0
        for sub_key, sub_value in value.items():
            ttk.Label(dict_frame, text=sub_key, font=("微软雅黑", 9)).grid(
                row=child_row, column=0, sticky="w", padx=5, pady=5
            )

            if isinstance(sub_value, list):
                # 嵌套list → Listbox+增删按钮
                list_container = ttk.Frame(dict_frame)
                list_container.grid(row=child_row, column=1, padx=5, pady=3, sticky="we")
                list_container.columnconfigure(0, weight=1)

                sub_listbox = tk.Listbox(list_container, font=("微软雅黑", 9), height=4)
                sub_listbox.grid(row=0, column=0, rowspan=2, padx=5, pady=3, sticky="nsew")
                for item in sub_value:
                    sub_listbox.insert(tk.END, item)

                sub_scroll = ttk.Scrollbar(list_container, orient="vertical", command=sub_listbox.yview)
                sub_scroll.grid(row=0, column=1, rowspan=2, sticky="ns")
                sub_listbox.configure(yscrollcommand=sub_scroll.set)

                btn_container = ttk.Frame(list_container)
                btn_container.grid(row=0, column=2, padx=5, pady=3, sticky="n")

                def add_sub_item(slb=sub_listbox, sk=sub_key):
                    new_item = tk.simpledialog.askstring("新增项", f"请输入{sk}的新值：")
                    if new_item and new_item.strip():
                        slb.insert(tk.END, new_item.strip())

                ttk.Button(btn_container, text="新增", command=add_sub_item).pack(fill=tk.X, pady=2)

                def del_sub_item(slb=sub_listbox):
                    selected = slb.curselection()
                    if selected:
                        slb.delete(selected[0])

                ttk.Button(btn_container, text="删除选中", command=del_sub_item).pack(fill=tk.X, pady=2)

                self.config_widgets[key]["children"][sub_key] = {
                    "type": "list",
                    "widget": sub_listbox,
                    "original_value": sub_value
                }
            else:
                # 基础类型
                sub_entry = ttk.Entry(dict_frame, font=("微软雅黑", 9), width=80)
                sub_entry.insert(0, str(sub_value) if sub_value is not None else "")
                sub_entry.grid(row=child_row, column=1, padx=5, pady=5, sticky="we")
                self.config_widgets[key]["children"][sub_key] = {
                    "type": "basic",
                    "widget": sub_entry,
                    "original_value": sub_value
                }
            child_row += 1

    def _render_dict_kv_widget(self, parent, key, value, row):
        """渲染键值对型Dict控件（高度随内容行数自适应）"""
        # ========== 外层容器：控制整体宽度（跟随弹窗自适应） ==========
        dict_container = ttk.Frame(parent)
        dict_container.grid(row=row, column=1, padx=5, pady=8, sticky="we")
        # 关键布局：3列（键/值/操作），仅值列自适应宽度
        dict_container.columnconfigure(0, weight=0)  # 键列：固定宽度
        dict_container.columnconfigure(1, weight=1)  # 值列：自适应宽度（核心）
        dict_container.columnconfigure(2, weight=0)  # 操作列：固定宽度

        # 1. 表头行（严格按列对齐）
        ttk.Label(dict_container, text="键", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=0, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(dict_container, text="值", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=1, padx=(5, 10), pady=3, sticky="w"
        )
        ttk.Label(dict_container, text="操作", font=("微软雅黑", 9, "bold")).grid(
            row=0, column=2, padx=(5, 10), pady=3, sticky="w"
        )

        # 2. 内容容器：替代原Canvas，高度随内容自适应（无固定高度）
        content_frame = ttk.Frame(dict_container)
        content_frame.grid(row=1, column=0, columnspan=3, padx=0, pady=3, sticky="nsew")
        # 继承列布局
        content_frame.columnconfigure(0, weight=0)
        content_frame.columnconfigure(1, weight=1)
        content_frame.columnconfigure(2, weight=0)

        # 3. 存储键值对控件引用
        kv_widgets = []
        self.config_widgets[key] = {
            "type": "dict_kv",
            "widget": content_frame,  # 改为content_frame（替代原kv_frame）
            "original_value": value,
            "kv_widgets": kv_widgets,
            "content_frame": content_frame,  # 新增：保存内容容器引用
            "dict_container": dict_container  # 新增：保存外层容器引用
        }

        # 4. 渲染初始键值对
        for kv_row, (k, v) in enumerate(value.items()):
            self._add_kv_row(content_frame, kv_widgets, k, v, kv_row)

        # 5. 新增按钮：放在操作列，和删除按钮同一列、靠左对齐
        def add_new_row():
            """新增行并更新高度"""
            new_row = len(kv_widgets)
            self._add_kv_row(content_frame, kv_widgets, "", "", new_row)
            # 触发父容器刷新，更新高度
            dict_container.update_idletasks()
            parent.update_idletasks()

        ttk.Button(dict_container, text="新增", width=6, command=add_new_row).grid(
            row=2, column=2, padx=(5, 10), pady=5, sticky="w"
        )

        # 初始化高度适配
        dict_container.update_idletasks()
        parent.update_idletasks()

    def _add_kv_row(self, parent, kv_widgets, init_key, init_value, row):
        """新增一行键值对控件（删除行后更新高度）"""
        # 1. 键输入框：固定宽度
        key_entry = ttk.Entry(parent, font=("微软雅黑", 9), width=20)
        key_entry.insert(0, init_key)
        key_entry.grid(row=row, column=0, padx=5, pady=3, sticky="we")

        # 2. 值输入框：自适应宽度
        value_entry = ttk.Entry(parent, font=("微软雅黑", 9))
        value_entry.insert(0, init_value)
        value_entry.grid(row=row, column=1, padx=5, pady=3, sticky="we")

        # 给值输入框加横向滚动（适配长文本）
        def scroll_value_entry(event):
            if event.delta > 0:
                value_entry.xview_scroll(-1, "units")
            else:
                value_entry.xview_scroll(1, "units")

        value_entry.bind("<MouseWheel>", scroll_value_entry)

        # 3. 删除按钮：固定宽度，删除后更新高度
        del_btn = ttk.Button(parent, text="删除", width=6)

        # 删除逻辑（新增：删除后更新高度）
        def del_kv_row():
            # 移除控件
            key_entry.grid_forget()
            value_entry.grid_forget()
            del_btn.grid_forget()
            # 从列表移除
            for i, (k_e, v_e, d_b) in enumerate(kv_widgets):
                if k_e == key_entry and v_e == value_entry and d_b == del_btn:
                    kv_widgets.pop(i)
                    break
            # 重新排列剩余行
            for new_row, (k_e, v_e, d_b) in enumerate(kv_widgets):
                k_e.grid(row=new_row, column=0, padx=5, pady=3, sticky="we")
                v_e.grid(row=new_row, column=1, padx=5, pady=3, sticky="we")
                d_b.grid(row=new_row, column=2, padx=5, pady=3, sticky="w")
            # 关键：删除后刷新父容器高度
            parent.update_idletasks()
            # 向上找外层容器并刷新（确保整体高度更新）
            if kv_widgets and hasattr(kv_widgets[0][0].master, 'master'):
                kv_widgets[0][0].master.master.update_idletasks()

        del_btn.configure(command=del_kv_row)
        del_btn.grid(row=row, column=2, padx=5, pady=3, sticky="w")  # 左对齐，不遮挡

        # 添加到控件列表
        kv_widgets.append((key_entry, value_entry, del_btn))

    def create_help_dialog(self):
        """创建帮助弹窗（保持原有逻辑不变）"""
        # 创建弹窗
        self.help_dialog = tk.Toplevel(self.parent)
        self.help_dialog.title("使用帮助")
        self.help_dialog.geometry("800x600")
        self.help_dialog.resizable(True, True)
        self.help_dialog.transient(self.parent)
        self.help_dialog.grab_set()

        # ========== 核心优化1：先隐藏弹窗 ==========
        self.help_dialog.withdraw()  # 隐藏弹窗

        # ========== 弹窗居中（和设置/关于弹窗一致） ==========
        self.help_dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        dialog_w = self.help_dialog.winfo_width()
        dialog_h = self.help_dialog.winfo_height()
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        self.help_dialog.geometry(f"+{x}+{y}")

        # ========== 核心优化2：显示弹窗 ==========
        self.help_dialog.deiconify()  # 显示弹窗

        # ========== 自定义ttk按钮样式（解决文字截断） ==========
        style = ttk.Style(self.help_dialog)
        style.configure(
            'Help.TButton',
            font=("微软雅黑", 10),
            padding=(10, 8)
        )

        # ========== 内容区域（带滚动条的文本框） ==========
        main_frame = ttk.Frame(self.help_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 滚动文本框
        help_text = scrolledtext.ScrolledText(
            main_frame,
            font=("微软雅黑", 9),
            wrap=tk.WORD,
            bg="#F8F9FA"
        )
        help_text.pack(fill=tk.BOTH, expand=True)

        # 读取README.md内容
        try:
            # 适配打包后路径
            if hasattr(sys, '_MEIPASS'):
                readme_path = os.path.join(os.path.dirname(sys.executable), "README.md")
            else:
                readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../README.md")

            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            help_text.insert(tk.END, readme_content)
        except FileNotFoundError:
            help_text.insert(tk.END, "❌ 未找到帮助文档（README.md），请检查文件是否存在！")
        except Exception as e:
            help_text.insert(tk.END, f"❌ 读取帮助文档失败：{str(e)}")

        # 设置文本框只读
        help_text.config(state=tk.DISABLED)

        # ========== 关闭按钮 ==========
        btn_frame = ttk.Frame(self.help_dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            btn_frame,
            text="关闭",
            command=self.on_close_help,
            style='Help.TButton'
        ).pack(side=tk.RIGHT)

    def on_close_help(self):
        """关闭帮助弹窗"""
        if self.help_dialog:
            self.help_dialog.destroy()
            self.help_dialog = None

    def create_about_dialog(self):
        """创建关于弹窗（保持原有逻辑不变）"""
        # 创建弹窗
        self.about_dialog = tk.Toplevel(self.parent)
        self.about_dialog.title("关于 DQA SYNC")
        self.about_dialog.geometry("400x200")
        self.about_dialog.resizable(False, False)
        self.about_dialog.transient(self.parent)
        self.about_dialog.grab_set()

        self.about_dialog.update_idletasks()  # 先更新弹窗尺寸
        # 主窗口位置和尺寸
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        # 弹窗尺寸
        dialog_w = self.about_dialog.winfo_width()
        dialog_h = self.about_dialog.winfo_height()
        # 计算居中坐标
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        # 设置弹窗位置
        self.about_dialog.geometry(f"+{x}+{y}")

        # 内容区域
        content_frame = ttk.Frame(self.about_dialog)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 版本信息
        ttk.Label(content_frame, text="DQA SYNC", font=("微软雅黑", 14, "bold")).pack(pady=5)
        ttk.Label(content_frame, text="FG204 2nd EDITION ver. 2.31", font=("微软雅黑", 10)).pack(pady=3)

        # 开发信息
        ttk.Label(content_frame, text="开发人员：BD4SLW", font=("微软雅黑", 10)).pack(pady=2)
        contact_label = ttk.Label(content_frame, text="联系方式：EL PSY KONGROO", font=("微软雅黑", 10))
        contact_label.pack(pady=2)
        # 绑定双击事件（<Double-1> 表示鼠标左键双击）
        contact_label.bind("<Double-1>", self.on_double_click_contact)

        # 确定按钮
        ttk.Button(content_frame, text="确定", command=self.on_close_about).pack(padx=5)

    def on_double_click_contact(self, event):
        """双击联系方式标签的处理函数（终极修复版）"""
        try:
            # 直接通过 parent（主UI Win实例）调用 show_game_menu_item 方法
            # 这是最直接、最可靠的方式，绕开control层的引用问题
            self.parent.show_game_menu_item()

            # 交互反馈：文字变蓝
            event.widget.config(foreground="blue")
            tk.messagebox.showinfo("提示", "隐藏彩蛋已激活！")
        except AttributeError as e:
            # 兜底：如果parent也没有该方法，手动创建菜单选项
            self.create_game_menu_item_manually()
            event.widget.config(foreground="blue")
            tk.messagebox.showinfo("提示", "隐藏彩蛋已激活（兜底模式）！")
        except Exception as e:
            print(f"激活菜单失败：{e}")
            tk.messagebox.showwarning("提示", f"彩蛋激活失败：{str(e)}")

    def create_game_menu_item_manually(self):
        """兜底方案：直接找到系统菜单并添加选项"""
        # 获取主窗口的菜单
        main_menu = self.parent.nametowidget(self.parent.cget("menu"))
        # 遍历菜单找到“其他”子菜单（system_menu）
        for i in range(main_menu.index("end") + 1):
            try:
                menu_item = main_menu.entrycget(i, "label")
                # 假设你的“其他”菜单标签是“其他”，请根据实际情况修改
                if menu_item == "其他":
                    sub_menu = main_menu.nametowidget(main_menu.entrycget(i, "menu"))
                    # 检查是否已添加“其他”选项
                    has_game_item = False
                    for j in range(sub_menu.index("end") + 1):
                        if sub_menu.entrycget(j, "label") == "其他":
                            has_game_item = True
                            break
                    if not has_game_item:
                        # 手动添加“其他”选项
                        sub_menu.add_command(
                            label="其他",
                            command=self.parent.ctl.open_game_select_dialog
                        )
                    break
            except:
                continue

    def on_cancel_setting(self):
        """取消设置（关闭弹窗，不保存）"""
        if self.setting_dialog:
            self.setting_dialog.destroy()
            self.setting_dialog = None

    def on_reset_setting(self):
        """重置配置（新增zentao_list类型重置）"""
        for key, widget_info in self.config_widgets.items():
            widget_type = widget_info["type"]
            original_value = widget_info["original_value"]
            widget = widget_info["widget"]

            if widget_type == "basic":
                widget.delete(0, tk.END)
                widget.insert(0, str(original_value) if original_value is not None else "")

            elif widget_type == "list":
                widget.delete(0, tk.END)
                for item in original_value:
                    widget.insert(tk.END, item)

            elif widget_type == "list_dict":
                # 重置jira_project_name_list
                list_dict_widgets = widget_info["list_dict_widgets"]
                for key_entry, value_entry, del_btn in list_dict_widgets:
                    key_entry.grid_forget()
                    value_entry.grid_forget()
                    del_btn.grid_forget()
                list_dict_widgets.clear()
                for ld_row, item in enumerate(original_value):
                    k = list(item.keys())[0] if item else ""
                    v = list(item.values())[0] if item else ""
                    self._add_list_dict_row(widget, list_dict_widgets, k, v, ld_row)

            elif widget_type == "zentao_list":
                # 重置create_zentao_map
                zentao_widgets = widget_info["zentao_widgets"]
                for pname_entry, pid_entry, assignee_entry, del_btn in zentao_widgets:
                    pname_entry.grid_forget()
                    pid_entry.grid_forget()
                    assignee_entry.grid_forget()
                    del_btn.grid_forget()
                zentao_widgets.clear()
                for zt_row, item in enumerate(original_value):
                    pname = item.get("zt_pname", "")
                    pid = item.get("zt_pid", "")
                    assignee = item.get("zt_assignee", "")
                    self._add_zentao_row(widget, zentao_widgets, pname, pid, assignee, zt_row)

            elif widget_type == "dict_kv":
                # 重置普通键值对Dict
                kv_widgets = widget_info["kv_widgets"]
                for key_entry, value_entry, del_btn in kv_widgets:
                    key_entry.grid_forget()
                    value_entry.grid_forget()
                    del_btn.grid_forget()
                kv_widgets.clear()
                for kv_row, (k, v) in enumerate(original_value.items()):
                    self._add_kv_row(widget, kv_widgets, k, v, kv_row)

            elif widget_type == "dict":
                for sub_key, sub_widget_info in widget_info["children"].items():
                    sub_widget = sub_widget_info["widget"]
                    sub_original = sub_widget_info["original_value"]
                    if sub_widget_info["type"] == "basic":
                        sub_widget.delete(0, tk.END)
                        sub_widget.insert(0, str(sub_original) if sub_original is not None else "")
                    elif sub_widget_info["type"] == "list":
                        sub_widget.delete(0, tk.END)
                        for item in sub_original:
                            sub_widget.insert(tk.END, item)

    def on_confirm_setting(self):
        """确认设置（新增zentao_list类型保存）- 适配ConfigManager实际方法"""
        try:
            import tkinter.simpledialog as sd

            for key, widget_info in self.config_widgets.items():
                # 原有配置保存逻辑（完全保留，无需修改）
                widget_type = widget_info["type"]
                widget = widget_info["widget"]
                original_type = type(widget_info["original_value"])

                if widget_type == "basic":
                    value_str = widget.get().strip()
                    if not value_str:
                        self.config_manager.set(key, "")
                        continue
                    if original_type == bool:
                        value = value_str.lower() == "true"
                    elif original_type == int:
                        value = int(value_str)
                    elif original_type == float:
                        value = float(value_str)
                    else:
                        value = value_str
                    self.config_manager.set(key, value)

                elif widget_type == "list":
                    value = list(widget.get(0, tk.END))
                    self.config_manager.set(key, value)

                elif widget_type == "list_dict":
                    list_dict_widgets = widget_info["list_dict_widgets"]
                    new_list_dict = []
                    for key_entry, value_entry, del_btn in list_dict_widgets:
                        k = key_entry.get().strip()
                        v = value_entry.get().strip()
                        if k:
                            new_list_dict.append({k: v})
                    self.config_manager.set(key, new_list_dict)

                elif widget_type == "zentao_list":
                    zentao_widgets = widget_info["zentao_widgets"]
                    new_zentao_list = []
                    for pname_entry, pid_entry, assignee_entry, del_btn in zentao_widgets:
                        pname = pname_entry.get().strip()
                        pid_str = pid_entry.get().strip()
                        assignee = assignee_entry.get().strip()
                        if pname:
                            pid = int(pid_str) if pid_str.isdigit() else 0
                            new_zentao_list.append({
                                "zt_pname": pname,
                                "zt_pid": pid,
                                "zt_assignee": assignee
                            })
                    self.config_manager.set(key, new_zentao_list)

                elif widget_type == "dict_kv":
                    kv_widgets = widget_info["kv_widgets"]
                    new_dict = {}
                    for key_entry, value_entry, del_btn in kv_widgets:
                        k = key_entry.get().strip()
                        v = value_entry.get().strip()
                        if k:
                            new_dict[k] = v
                    self.config_manager.set(key, new_dict)

                elif widget_type == "dict":
                    for sub_key, sub_widget_info in widget_info["children"].items():
                        sub_widget = sub_widget_info["widget"]
                        sub_original_type = type(sub_widget_info["original_value"])
                        sub_key_path = f"{key}.{sub_key}"

                        if sub_widget_info["type"] == "basic":
                            sub_value_str = sub_widget.get().strip()
                            if not sub_value_str:
                                self.config_manager.set(sub_key_path, "")
                                continue
                            if sub_original_type == bool:
                                sub_value = sub_value_str.lower() == "true"
                            elif sub_original_type == int:
                                sub_value = int(sub_value_str)
                            elif sub_original_type == float:
                                sub_value = float(sub_value_str)
                            else:
                                sub_value = sub_value_str
                            self.config_manager.set(sub_key_path, sub_value)

                        elif sub_widget_info["type"] == "list":
                            sub_value = list(sub_widget.get(0, tk.END))
                            self.config_manager.set(sub_key_path, sub_value)

            # ========== 核心修改：适配ConfigManager的保存逻辑 ==========
            # 1. 移除不存在的 save_config() 调用
            # self.config_manager.save_config()  # 删掉这行！

            # 2. 关键：ConfigManager的set方法已经自动调用了 _save_config
            #    所以无需额外保存，只需重新加载配置（确保内存和文件一致）
            self.config_manager.reload()

            # 3. 尝试调用全局配置重载方法
            reload_success = False
            try:
                # 方式1：通过Control层调用主窗口的重载方法
                if hasattr(self, 'control') and self.control and hasattr(self.control.ui, 'reload_all_config'):
                    self.control.ui.reload_all_config()
                    reload_success = True
                # 方式2：直接调用主窗口实例
                elif hasattr(self, 'main_window') and hasattr(self.main_window, 'reload_all_config'):
                    self.main_window.reload_all_config()
                    reload_success = True
            except Exception as reload_e:
                import logging
                logging.warning(f"配置重载失败（需重启生效）：{str(reload_e)}")

            # 关闭弹窗 + 回调通知
            self.setting = self.on_cancel_setting()
            if hasattr(self, 'on_save_config') and callable(self.on_save_config):
                self.on_save_config(self.config_manager.config)

            # 差异化提示
            if reload_success:
                tk.messagebox.showinfo("成功", "配置保存成功！所有配置已实时生效✅")
            else:
                tk.messagebox.showinfo("成功", "配置保存成功！需重启应用生效🔄")

        except ValueError as e:
            tk.messagebox.showerror("类型错误", f"数据类型转换失败：{str(e)}")
        except Exception as e:
            tk.messagebox.showerror("配置错误", f"保存配置失败：{str(e)}")

    def on_close_about(self):
        """关闭关于弹窗"""
        if self.about_dialog:
            self.about_dialog.destroy()
            self.about_dialog = None

    def set_save_callback(self, callback):
        """设置保存配置的回调函数（由控制层绑定）"""
        self.on_save_config = callback