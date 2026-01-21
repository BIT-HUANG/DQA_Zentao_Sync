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
        self.parent = parent  # 主窗口引用
        self.config_manager = ConfigManager(".config")  # 初始化配置管理器
        self.original_config = {}  # 存储原始配置（用于重置）
        self.setting_dialog = None  # 设置弹窗
        self.about_dialog = None  # 关于弹窗
        self.help_dialog = None  # 帮助弹窗

        # 存储输入控件引用（区分不同类型：单行/多行/分组）
        self.config_widgets = {}

    def create_setting_dialog(self):
        """创建设置弹窗"""
        print("配置文件绝对路径：", self.config_manager.get_config_path())
        print("读取到的配置内容：", self.config_manager.config)

        self.original_config = json.loads(json.dumps(self.config_manager.config))

        self.setting_dialog = tk.Toplevel(self.parent)
        self.setting_dialog.title("系统设置")
        self.setting_dialog.geometry("1000x700")  # 加宽弹窗，适配键值对
        self.setting_dialog.resizable(True, True)
        self.setting_dialog.transient(self.parent)
        self.setting_dialog.grab_set()

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

        # 滚动容器
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
            anchor="nw",
            width=canvas.winfo_width()
        )

        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(scrollable_frame_id, width=canvas.winfo_width())
        # 新增：监听内容变化后强制更新
        self.setting_dialog.bind("<Configure>", update_scroll_region)

        canvas.bind("<Configure>", update_scroll_region)
        scrollable_frame.bind("<Configure>", update_scroll_region)

        # 渲染配置项
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
                    # 键值对dict（如create_zentao_map）
                    self._render_dict_kv_widget(scrollable_frame, key, value, row)
                else:
                    # 普通嵌套dict
                    self._render_dict_widget(scrollable_frame, key, value, row)
            elif isinstance(value, list):
                # 列表 → Listbox+增删
                self._render_list_widget(scrollable_frame, key, value, row)
            else:
                # 基础类型
                self._render_basic_widget(scrollable_frame, key, value, row)

            row += 1

        # 按钮区域
        btn_frame = ttk.Frame(self.setting_dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=(20, 10))

        ttk.Button(btn_frame, text="取消", command=self.on_cancel_setting).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置", command=self.on_reset_setting).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="确认", command=self.on_confirm_setting).pack(side=tk.LEFT, padx=5)

        scrollable_frame.columnconfigure(1, weight=1)

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
        """渲染列表控件（Listbox + 新增/删除按钮，支持增删操作）"""
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
        del_btn.grid(row=row, column=2, padx=5, pady=3, sticky="w")

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
                readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md")

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

        # ========== 新增：弹窗居中（相对于主窗口） ==========
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
        ttk.Label(content_frame, text="联系方式：EL PSY KONGROO", font=("微软雅黑", 10)).pack(pady=2)

        # 确定按钮
        ttk.Button(content_frame, text="确定", command=self.on_close_about).pack(padx=5)

    def on_cancel_setting(self):
        """取消设置（关闭弹窗，不保存）"""
        if self.setting_dialog:
            self.setting_dialog.destroy()
            self.setting_dialog = None

    def on_reset_setting(self):
        """重置配置（支持键值对Dict重置）"""
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

            elif widget_type == "dict_kv":
                # 清空现有键值对
                kv_widgets = widget_info["kv_widgets"]
                for key_entry, value_entry, del_btn in kv_widgets:  # 改为 value_entry
                    key_entry.grid_forget()
                    value_entry.grid_forget()  # 改为 value_entry
                    del_btn.grid_forget()
                kv_widgets.clear()

                # 恢复原始键值对
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
        """确认设置（支持键值对Dict增删）"""
        try:
            import tkinter.simpledialog as sd

            for key, widget_info in self.config_widgets.items():
                widget_type = widget_info["type"]
                widget = widget_info["widget"]
                original_type = type(widget_info["original_value"])

                if widget_type == "basic":
                    # 基础类型
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
                    # Listbox列表
                    value = list(widget.get(0, tk.END))
                    self.config_manager.set(key, value)

                elif widget_type == "dict_kv":
                    # 键值对Dict（适配Entry值输入框）
                    kv_widgets = widget_info["kv_widgets"]
                    new_dict = {}
                    for key_entry, value_entry, del_btn in kv_widgets:  # 改为 value_entry
                        k = key_entry.get().strip()
                        v = value_entry.get().strip()  # 改为 get()（Entry的读取方式）
                        if k:  # 键不为空才保存
                            new_dict[k] = v
                    self.config_manager.set(key, new_dict)

                elif widget_type == "dict":
                    # 普通嵌套dict
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

            self.setting = self.on_cancel_setting()

            if hasattr(self, 'on_save_config') and callable(self.on_save_config):
                self.on_save_config(self.config_manager.config)

            tk.messagebox.showinfo("成功", "配置保存成功！")

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