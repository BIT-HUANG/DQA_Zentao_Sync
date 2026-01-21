import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import sys
import os


class SystemSettingUI:
    """系统设置相关弹窗UI类"""

    def __init__(self, parent):
        self.parent = parent  # 主窗口引用
        self.config_data = {}  # 存储读取的配置数据
        self.original_config = {}  # 存储原始配置（用于重置）
        self.setting_dialog = None  # 设置弹窗
        self.about_dialog = None  # 关于弹窗

    def create_setting_dialog(self, config_data):
        """创建设置弹窗"""
        # 保存原始配置和当前配置
        self.original_config = json.loads(json.dumps(config_data))  # 深拷贝
        self.config_data = json.loads(json.dumps(config_data))

        # 创建弹窗
        self.setting_dialog = tk.Toplevel(self.parent)
        self.setting_dialog.title("系统设置")
        self.setting_dialog.geometry("800x600")
        self.setting_dialog.resizable(True, True)
        self.setting_dialog.transient(self.parent)  # 置顶主窗口
        self.setting_dialog.grab_set()  # 模态窗口

        # ==========核心优化1： 先隐藏弹窗 ==========
        self.setting_dialog.withdraw()  # 隐藏弹窗，避免左上角闪屏

        # ========== 弹窗居中（相对于主窗口） ==========
        self.setting_dialog.update_idletasks()  # 先更新弹窗尺寸，否则获取的宽高为0
        # 主窗口位置和尺寸
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        # 弹窗尺寸
        dialog_w = self.setting_dialog.winfo_width()
        dialog_h = self.setting_dialog.winfo_height()
        # 计算居中坐标（主窗口中心 - 弹窗一半尺寸）
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        # 设置弹窗位置
        self.setting_dialog.geometry(f"+{x}+{y}")

        # ========== 核心优化2：显示弹窗 ==========
        self.setting_dialog.deiconify()  # 显示弹窗

        # 创建滚动容器
        main_frame = ttk.Frame(self.setting_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scroll_y = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        # 布局滚动容器
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # 生成配置项输入框
        row = 0
        self.config_entries = {}  # 存储输入框引用
        for key, value in self.config_data.items():
            # 标签
            ttk.Label(scrollable_frame, text=key, font=("微软雅黑", 9, "bold")).grid(
                row=row, column=0, sticky="w", padx=5, pady=3
            )
            # 输入框（嵌套结构转为JSON字符串）
            value_str = json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value, (dict, list)) else str(
                value)
            entry = scrolledtext.ScrolledText(scrollable_frame, width=80, height=4, font=("微软雅黑", 9))
            entry.insert(tk.END, value_str)
            entry.grid(row=row, column=1, padx=5, pady=3, sticky="we")
            self.config_entries[key] = entry
            row += 1

        # 按钮区域
        btn_frame = ttk.Frame(self.setting_dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # 取消按钮
        ttk.Button(btn_frame, text="取消", command=self.on_cancel_setting).pack(
            side=tk.LEFT, padx=5
        )
        # 重置按钮
        ttk.Button(btn_frame, text="重置", command=self.on_reset_setting).pack(
            side=tk.LEFT, padx=5
        )
        # 确认按钮
        ttk.Button(btn_frame, text="确认", command=self.on_confirm_setting).pack(
            side=tk.LEFT, padx=5
        )

        # 调整列宽
        scrollable_frame.columnconfigure(1, weight=1)

    def create_help_dialog(self):
        """创建帮助弹窗（读取README.md内容）"""
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
        """创建关于弹窗"""
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
        """重置配置（恢复原始数据）"""
        for key, entry in self.config_entries.items():
            # 清空输入框并恢复原始值
            entry.delete(1.0, tk.END)
            value = self.original_config.get(key, "")
            value_str = json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value, (dict, list)) else str(
                value)
            entry.insert(tk.END, value_str)

    def on_confirm_setting(self):
        """确认设置（校验并返回修改后的配置）"""
        try:
            # 读取输入框内容并解析
            new_config = {}
            for key, entry in self.config_entries.items():
                value_str = entry.get(1.0, tk.END).strip()
                if not value_str:
                    new_config[key] = ""
                    continue

                # 尝试解析JSON（针对字典/数组）
                try:
                    # 先判断原始类型
                    original_type = type(self.original_config.get(key))
                    if original_type in (dict, list):
                        new_config[key] = json.loads(value_str)
                    elif original_type == bool:
                        # 布尔值特殊处理
                        new_config[key] = value_str.lower() == "true"
                    elif original_type == int:
                        new_config[key] = int(value_str)
                    else:
                        new_config[key] = value_str
                except json.JSONDecodeError:
                    # 非JSON格式且原始类型不是字典/数组，直接存字符串
                    new_config[key] = value_str

            self.config_data = new_config
            self.on_cancel_setting()  # 关闭弹窗
            # 触发保存回调（由控制层实现）
            if hasattr(self, 'on_save_config') and callable(self.on_save_config):
                self.on_save_config(new_config)

        except Exception as e:
            messagebox.showerror("配置错误", f"解析配置失败：{str(e)}")

    def on_close_about(self):
        """关闭关于弹窗"""
        if self.about_dialog:
            self.about_dialog.destroy()
            self.about_dialog = None

    def set_save_callback(self, callback):
        """设置保存配置的回调函数（由控制层绑定）"""
        self.on_save_config = callback