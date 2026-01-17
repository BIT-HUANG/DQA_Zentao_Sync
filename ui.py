"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
import random
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

import mconfig
from utils import common
from utils import services
from urllib.error import HTTPError

class WinGUI(Tk):

    # ======== 场景表格 枚举所有场景（规范，防止写错场景名） ========
    TABLE_TYPE_DEFAULT = "default"  # Jira+禅道完整数据
    TABLE_TYPE_CREATE_ZENTAO = "create_zentao"  # 禅道创建专用数据
    TABLE_TYPE_JIRA = "only_jira"  # 仅Jira数据
    TABLE_TYPE_ZENTAO = "only_zentao"  # 仅禅道数据
    TABLE_TYPE_ERROR = "error"  # 错误提示
    TABLE_TYPE_EMPTY = "empty"  # 无数据提示

    # ========场景表格的表头配置 表头配置映射字典，场景名对应表头配置 ========
    TABLE_COLUMNS_MAP = {
        TABLE_TYPE_DEFAULT: {"ID": 30, "标题": 300, "JiraID": 130, "Jira状态": 60, "禅道ID": 60, "禅道状态": 60,
                         "禅道对策": 60, "禅道最新历史(点击查看所有)": 450},
        TABLE_TYPE_CREATE_ZENTAO: {"ID": 30, "标题": 300, "JiraID": 130, "禅道模块": 130, "禅道模块ID": 130,"禅道指派人": 130,
                            "禅道创建结果":130, "禅道创建备注": 250},
        TABLE_TYPE_JIRA: {"ID": 30, "标题": 300, "JiraID": 130, "Jira状态": 60,"Jira最新备注(点击查看所有)":450},
        TABLE_TYPE_ZENTAO: {"ID": 30, "标题": 300, "禅道ID": 60, "禅道状态": 60, "禅道对策": 60, "禅道最新历史(点击查看所有)": 450},
        TABLE_TYPE_ERROR: {"查询结果提示": 1180},
        TABLE_TYPE_EMPTY: {"查询结果提示": 1180},
    }
    # ======== 列名映射 ========
    COL_KEY_MAP = {
        "标题": "jira_summary",
        "JiraID": "jira_key",
        "Jira状态": "jira_status",
        "禅道ID": "zentao_id",
        "禅道状态": "zentao_status",
        "禅道对策": "zentao_resolution",
        "禅道最新历史(点击查看所有)": "zentao_history",
        "Jira最新备注(点击查看所有)": "jira_comments",
        "禅道模块": "zentao_module",
        "禅道模块ID": "zentao_module_id",
        "禅道指派人": "zentao_assignee",
        "禅道指派人ID": "zentao_assignee_id",
        "禅道创建结果": "zentao_create_result",
        "禅道创建备注": "zentao_create_comment",
        "查询结果提示": "tips"
    }

    # ======== 禅道创建弹窗 固定常量 ========
    CREATE_ZENTAO_POPUP_WIDTH = 720
    CREATE_ZENTAO_POPUP_HEIGHT = 480
    CREATE_ZENTAO_POPUP_TITLE = "添加创建禅道-添加记录"

    def __init__(self):
        super().__init__()
        self.__win()

        # ========== 禅道创建相关变量 ==========
        self.zentao_create_map = mconfig.get_create_zentao_map()  # 读取.config的禅道模块映射
        self.jira_project_name_map = mconfig.get_jira_project_name_list()  # 读取Jira项目名称映射
        self.jira_project_name_list = list(self.jira_project_name_map.values())  # 下拉框只展示value值列表
        self.create_zentao_popup = None  # 禅道创建表单弹窗对象
        self.create_form_widgets = {}  # 存储表单内所有控件，方便清空/取值
        self.jira_query_timer = None  # Jira查询防抖定时器，解决频繁查询问题
        self.cached_jira_query_result = None  # 新增：缓存Jira查询结果，杜绝重复请求

        self.tk_label_label_1 = self.__tk_label_label_1(self)
        self.tk_table_table_1 = self.__tk_table_table_1(self)
        self.tk_button_button_search = self.__tk_button_button_search(self)
        self.tk_button_button_update = self.__tk_button_button_update(self)
        self.tk_input_jql = self.__tk_input_jql(self)

        # ========== 禅道创建区域 控件初始化 ==========
        self.tk_label_zentao_create = self.__tk_label_zentao_create(self)
        self.tk_button_del_record = self.__tk_button_del_record(self)
        self.tk_button_add_record = self.__tk_button_add_record(self)
        self.tk_button_submit_create = self.__tk_button_submit_create(self)

        # ========== 定义映射字典 绑定【表格行id: 原始完整行数据】 ==========
        self.row_history_map = {}
        # ========== 弹窗初始化 ==========
        self.popup_win = None
        # ==========  设置输入框默认值  ==========
        self.tk_input_jql.insert(0, mconfig.get_issue_list_jql())
        # ========== 气泡提示 ==========
        self.tooltip_label = tk.Label(
            self,
            text="",
            bg="#FFE6E6",  # 浅红色背景，报错提示专用，醒目不刺眼
            fg="#E63946",  # 深红色字体
            padx=20, pady=8,
            font=("微软雅黑", 10),
            relief="solid", bd=1,
            justify="center"
        )
        self.tooltip_label.place_forget()  # 初始状态隐藏气泡
        # 用于存放定时器id，防止重复弹窗叠加
        self.tooltip_after_id = None
        # ========== 标题列悬浮提示组件 ==========
        self.title_tooltip = tk.Label(
            self,
            text="",
            bg="#FFF8DC",  # 浅金黄色背景，区分报错气泡，不刺眼
            fg="#333333",  # 黑色字体，清晰可读
            padx=10, pady=5,
            font=("微软雅黑", 9),
            relief="solid", bd=1,
            justify="left",  # 文本左对齐，方便阅读长标题
            wraplength=600  # 标题超长时自动换行，最大宽度600像素
        )
        self.title_tooltip.place_forget()  # 初始隐藏
        # ========== 绑定窗口大小变化事件 ==========
        self.bind('<Configure>', self.on_window_resize)

    def __win(self):
        self.title("DQA 同步工具")
        # 设置窗口大小、居中
        width = 1280
        height = 800
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        # ========== 开启窗口可拉伸+最大化 ==========
        self.resizable(width=True, height=True)

    def scrollbar_autohide(self,vbar, hbar, widget):
        """自动隐藏滚动条"""
        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)
        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)
        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())

    def v_scrollbar(self,vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')

    def h_scrollbar(self,hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')

    def create_bar(self,master, widget,is_vbar,is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)

    # ========== 窗口大小变化事件，刷新表格尺寸 ==========
    def on_window_resize(self, event):
        """窗口拉伸/最大化时，自动刷新表格和滚动条尺寸"""
        if event.widget == self:
            win_w = self.winfo_width()
            win_h = self.winfo_height()
            # 表格尺寸：左右留20px边距，上下留75px头部+60px底部
            table_w = win_w - 40
            table_h = win_h - 135
            if table_w < 800: table_w = 800
            if table_h < 400: table_h = 400
            # 更新表格尺寸
            self.tk_table_table_1.place(x=20, y=75, width=table_w, height=table_h)
            # 重新创建滚动条
            self.create_bar(self, self.tk_table_table_1, True, True, 20,75,table_w,table_h,win_w,win_h)
            # 更新输入框宽度
            self.tk_input_jql.place(x=100, y=20, width=win_w - 340, height=30)
            # 更新按钮位置
            self.tk_button_button_search.place(x=win_w - 200, y=20, width=80, height=30)
            self.tk_button_button_update.place(x=win_w - 110, y=20, width=80, height=30)
            # ========== 禅道创建区域 跟随窗口拉伸自动适配位置 ==========
            # 固定位置：窗口右下角、表格下方，间距统一20px，完美对齐
            base_x = win_w - 300
            base_y = win_h - 50
            self.tk_label_zentao_create.place(x=base_x - 190, y=base_y, width=80, height=30) # label
            self.tk_button_del_record.place(x=base_x - 110, y=base_y, width=100, height=30)    # 删除按钮
            self.tk_button_add_record.place(x=base_x, y=base_y, width=100, height=30)         # 添加按钮
            self.tk_button_submit_create.place(x=base_x + 110, y=base_y, width=100, height=30)# 提交按钮

    def __tk_label_label_1(self,parent):
        label = Label(parent,text="JQL： ",anchor="center", )
        label.place(x=20, y=20, width=80, height=30)
        return label

    def __tk_table_table_1(self,parent):
        # 表头字段 表头宽度
        columns = {"ID":30,"标题":300,"JiraID":130,"Jira状态":60,"禅道ID":60,"禅道状态":60,"禅道对策":60,"禅道最新历史(点击查看所有)":450}
        tk_table = Treeview(parent, show="headings", columns=list(columns),)
        for text, width in columns.items():  # 批量设置列属性
            tk_table.heading(text, text=text, anchor='center')
            tk_table.column(text, anchor='w', width=width, stretch=False)  # stretch 不自动拉伸

        tk_table.place(x=20, y=75, width=1200, height=665)
        self.create_bar(parent, tk_table,True, True,20, 75, 1200,665,1280,800)

        # ========== 绑定表格单元格点击事件 ==========
        tk_table.bind('<ButtonRelease-1>', self.show_history_detail)
        tk_table.bind('<Motion>', self.on_table_motion)    # 鼠标在表格内移动 → 核心触发悬浮提示
        tk_table.bind('<Leave>', self.on_table_leave)     # 鼠标离开表格 → 隐藏提示
        return tk_table

    def __tk_button_button_search(self,parent):
        btn = Button(parent, text="列表查询", takefocus=False,)
        btn.place(x=950, y=20, width=80, height=30)
        return btn

    def __tk_button_button_update(self,parent):
        btn = Button(parent, text="更新所有", takefocus=False,)
        btn.place(x=1050, y=20, width=80, height=30)
        return btn

    def __tk_input_jql(self, parent):
        ipt = Entry(parent, )
        ipt.place(x=100, y=20, width=800, height=30)
        return ipt

    # ========== 禅道创建 标题Label 定义 ==========
    def __tk_label_zentao_create(self, parent):
        label = Label(parent, text="禅道创建：", anchor="center")
        label.place(x=1000, y=760, width=80, height=30)
        return label

    # ========== 添加记录 按钮 定义 ==========
    def __tk_button_add_record(self, parent):
        btn = Button(parent, text="添加记录", takefocus=False)
        btn.place(x=1080, y=760, width=100, height=30)
        return btn

    # ========== 确认提交 按钮 定义 ==========
    def __tk_button_submit_create(self, parent):
        btn = Button(parent, text="确认提交", takefocus=False)
        btn.place(x=1190, y=760, width=100, height=30)
        return btn

    # ==========删除记录 按钮 定义 ==========
    def __tk_button_del_record(self, parent):
        # 核心：初始化ttk样式 + 配置【红底白字】样式，仅对当前按钮生效，不影响其他按钮
        style = Style(parent)
        style.configure('DelBtn.TButton', foreground='red')

        # 创建按钮并应用样式，其他参数和你原有代码完全一致，位置不变
        btn = Button(parent, text="删除记录", takefocus=False, style='DelBtn.TButton')
        btn.place(x=1030, y=760, width=100, height=30)
        return btn

    # ==========table control ==========
    def reset_table_style(self, table_type):
        """
        核心方法：根据表格类型重置表头+列结构，保留原有滚动条/事件绑定/布局
        :param table_type: 表格类型，对应 TABLE_TYPE_DEFAULT/TABLE_TYPE_CREATE_ZENTAO 等
        """
        table = self.tk_table_table_1
        columns_conf = self.TABLE_COLUMNS_MAP.get(table_type, self.TABLE_TYPE_DEFAULT)

        # 1. 清空表格所有数据行
        self.clear_table()
        table.selection_remove(table.selection())  # 切换表格时取消选中行
        # 3. 重新配置新列+表头+宽度
        table["columns"] = list(columns_conf)
        table["show"] = "headings"
        for text, width in columns_conf.items():
            table.heading(text, text=text, anchor='center')
            table.column(text, anchor='w', width=width, stretch=False)

    def clear_table(self):
        """清空表格所有数据"""
        for item in self.tk_table_table_1.get_children():
            self.tk_table_table_1.delete(item)
        # 清空时取消选中行
        self.tk_table_table_1.selection_remove(self.tk_table_table_1.selection())
        # 清空映射字典，防止残留数据
        self.row_history_map.clear()
        # 清空表格时，隐藏标题悬浮提示
        self.title_tooltip.place_forget()

    def insert_table_data(self, data_list):
        """把字典列表数据插入表格，精准映射表格列和你的数据字段"""
        table = self.tk_table_table_1
        # 获取当前表格的列名，动态适配所有表头
        current_cols = table["columns"]
        for idx, row in enumerate(data_list, start=1):
            # 动态取值：根据当前表格的列名，从字典中取值，无对应字段则显示空字符串
            show_values = []
            for col_name in current_cols:
                if col_name == "ID":
                    # ID列固定显示行号
                    show_values.append(idx)
                elif col_name == "禅道最新历史(点击查看所有)":
                    # 禅道历史列：调用方法显示最新历史
                    show_values.append(common.show_latest_zentao_history(row.get("zentao_history", {})))
                elif col_name == "Jira最新备注(点击查看所有)":
                    # Jira备注列：直接取值
                    show_values.append(row.get("jira_comments", ""))
                else:
                    # 其他列：通过精准映射表取值，无则显示空字符串
                    key = self.COL_KEY_MAP.get(col_name, "")
                    show_values.append(row.get(key, "") if key else "")

            # ========== 如果值的数量少于列数，补空字符串，防止列数不匹配报错 ==========
            show_values += [""] * (len(current_cols) - len(show_values))
            # 插入行并获取当前行的唯一ID
            row_id = table.insert('', END, values=show_values)
            # ========== 修复核心：所有行都存入完整的原始数据，不再做判断！ ==========
            self.row_history_map[row_id] = row

    def load_table_data(self, data_list):
        """一键加载数据：清空旧数据 + 插入新数据"""
        self.clear_table()
        self.insert_table_data(data_list)

    # ==========加载六种表格类型的数据 ==========
    def load_default_table(self, data_list):
        """加载默认表头(Jira+禅道完整数据) + 数据"""
        self.reset_table_style(self.TABLE_TYPE_DEFAULT)
        self.load_table_data(data_list)

    def load_zentao_create_table(self, data_list):
        """加载禅道创建专用表头 + 数据"""
        self.reset_table_style(self.TABLE_TYPE_CREATE_ZENTAO)
        self.load_table_data(data_list)

    def load_jira_table(self, data_list):
        """加载仅Jira数据的表头 + 数据"""
        self.reset_table_style(self.TABLE_TYPE_JIRA)
        self.load_table_data(data_list)

    def load_zentao_table(self, data_list):
        """加载仅禅道数据的表头 + 数据"""
        self.reset_table_style(self.TABLE_TYPE_ZENTAO)
        self.load_table_data(data_list)

    def load_error_table(self, error_msg):
        """加载错误提示表头 + 错误信息"""
        self.reset_table_style(self.TABLE_TYPE_ERROR)
        self.tk_table_table_1.insert('', END, values=[error_msg])

    def load_empty_table(self):
        """加载无数据提示表头 + 提示文本"""
        self.reset_table_style(self.TABLE_TYPE_EMPTY)
        self.tk_table_table_1.insert('', END, values=["查询完成，暂无匹配数据！"])

    # ==========jql input control ==========
    def get_jql_content(self):
        """获取输入框中的JQL查询内容"""
        return self.tk_input_jql.get().strip()  # strip()去掉首尾空格，防止输入无效空格

    def clear_jql_content(self):
        """清空输入框内容"""
        self.tk_input_jql.delete(0, END)  # 删除从索引0到末尾的所有内容

    # ========== 点击单元格展示完整历史 ==========
    def show_history_detail(self, event):
        """点击表格单元格，【仅默认表格】的【禅道最新历史】列则弹窗展示完整内容"""
        table = self.tk_table_table_1
        # 1. 获取点击的区域：只处理单元格点击
        region = table.identify('region', event.x, event.y)
        if region != 'cell':
            self.hide_popup()
            return

        # 2. 获取点击的行、列信息
        row_id = table.identify_row(event.y)  # 点击的行ID
        col_index = int(table.identify_column(event.x).replace('#', '')) - 1  # 列索引 从0开始

        # 获取当前表格的配置key，判断是否为【默认完整表格】
        current_table_cols = table["columns"]
        # 只有默认表格的列头包含 "禅道最新历史(点击查看所有)"，才继续执行弹窗逻辑
        is_default_table = "禅道最新历史(点击查看所有)" in current_table_cols
        # 【核心】不是默认表格 → 直接退出，不弹窗
        if not is_default_table:
            self.hide_popup()
            return

        # 默认表格下，仅点击索引7的【禅道最新历史】列 才弹窗
        if col_index != 7 or row_id not in self.row_history_map:
            self.hide_popup()
            return

        # 后续弹窗逻辑完全不变
        raw_history_dict = self.row_history_map[row_id].get("zentao_history", {})
        if not raw_history_dict:  # 匹配：空字典/None/空值，直接终止逻辑，不弹窗
            return

        all_history_list = common.show_all_zentao_history(raw_history_dict)
        all_history_text = '\n\n'.join(all_history_list)

        self.hide_popup()  # 先关闭旧弹窗
        self.popup_win = Toplevel(table)
        self.popup_win.title('禅道完整历史记录')
        x_cell = table.bbox(row_id, col_index)[0]
        y_cell = table.bbox(row_id, col_index)[1]
        cell_height = table.bbox(row_id, col_index)[3]

        win_x = table.winfo_rootx() + x_cell
        win_y = table.winfo_rooty() + y_cell + cell_height + 5
        self.popup_win.geometry(f'500x300+{win_x}+{win_y}')
        self.popup_win.attributes('-topmost', True)

        text_box = Text(self.popup_win, wrap=WORD, font=('宋体', 10))
        scroll = Scrollbar(self.popup_win, orient=VERTICAL, command=text_box.yview)
        text_box.configure(yscrollcommand=scroll.set)

        text_box.pack(side=LEFT, fill=BOTH, expand=YES, padx=5, pady=5)
        scroll.pack(side=RIGHT, fill=Y)

        text_box.insert(END, all_history_text)
        text_box.config(state=DISABLED)

    def hide_popup(self):
        """关闭弹窗"""
        if self.popup_win and self.popup_win.winfo_exists():
            self.popup_win.destroy()

    #========== 历史同步结果弹窗显示 ==========
    def show_popup(self, title: str, content: str):
        """
        新增专用弹窗：展示同步结果详细汇总信息 (独立弹窗，和单元格历史弹窗互不冲突)
        :param title: 弹窗标题
        :param content: 弹窗展示的详细内容文本
        """
        # 先关闭可能存在的旧弹窗（避免叠加）
        self.hide_popup()
        # 创建顶层弹窗窗口
        self.popup_win = Toplevel(self)
        self.popup_win.title(title)
        self.popup_win.geometry("700x450")  # 固定宽高，适配同步结果明细
        self.popup_win.resizable(width=True, height=True)  # 允许拉伸放大
        self.popup_win.attributes('-topmost', True)  # 置顶显示，优先展示
        # 窗口居中显示（核心优化，比跟随单元格更适合汇总弹窗）
        self.popup_win.update_idletasks()
        x = (self.popup_win.winfo_screenwidth() - self.popup_win.winfo_width()) // 2
        y = (self.popup_win.winfo_screenheight() - self.popup_win.winfo_height()) // 2
        self.popup_win.geometry(f"+{x}+{y}")

        # 添加带滚动条的文本框，适配超长内容，防止内容溢出
        text_box = Text(self.popup_win, wrap=tk.WORD, font=("微软雅黑", 10), bg="#F8F9FA")
        scroll_y = Scrollbar(self.popup_win, orient=tk.VERTICAL, command=text_box.yview)
        text_box.configure(yscrollcommand=scroll_y.set)

        # 布局：文本框占满，滚动条在右侧
        text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # 填充内容 + 设置只读不可编辑
        text_box.insert(tk.END, content)
        text_box.config(state=tk.DISABLED)

        # 绑定关闭事件，清理弹窗对象
        self.popup_win.protocol("WM_DELETE_WINDOW", self.hide_popup)

    # ========== 标题列悬浮提示 ==========
    def on_table_motion(self, event):
        table = self.tk_table_table_1
        # 1. 只处理单元格区域，非单元格隐藏气泡
        region = table.identify('region', event.x, event.y)
        if region != 'cell':
            self.title_tooltip.place_forget()
            return

        # 2. 获取行ID、列索引、当前列名（和你弹窗逻辑一致）
        row_id = table.identify_row(event.y)
        col_index = int(table.identify_column(event.x).replace('#', '')) - 1
        current_cols = table["columns"]

        # 3. 只对【标题】列生效
        if col_index < 0 or col_index >= len(current_cols) or current_cols[col_index] != "标题":
            self.title_tooltip.place_forget()
            return

        # 4. 获取完整标题文本
        if row_id not in self.row_history_map:
            self.title_tooltip.place_forget()
            return
        full_title = self.row_history_map[row_id].get("jira_summary", "")
        if not full_title.strip():
            self.title_tooltip.place_forget()
            return

        # ==========  核心：和你弹窗【完全一致】的【相对坐标】计算逻辑，一字不改 ==========
        # 1. 获取标题单元格 【相对表格】的坐标 + 宽高 (你的弹窗源码，完全复用)
        x_cell = table.bbox(row_id, col_index)[0]  # 单元格左上角X（相对表格）
        y_cell = table.bbox(row_id, col_index)[1]  # 单元格左上角Y（相对表格）
        cell_height = table.bbox(row_id, col_index)[3]  # 单元格高度

        # 2. 计算气泡【相对表格】的坐标 (你的弹窗源码，完全复用，间距+3和弹窗一致)
        tip_x = x_cell
        tip_y = y_cell + cell_height + 3

        # ==========  重中之重：place使用【相对位置】+ 绑定父容器table，这是弹窗位置正确的核心 ==========
        self.title_tooltip.config(text=full_title)
        self.title_tooltip.place(
            x=tip_x,  # X坐标：相对表格左上角的偏移量（不是屏幕）
            y=tip_y,  # Y坐标：相对表格左上角的偏移量（不是屏幕）
            anchor='nw',  # 气泡左上角 对齐 计算出来的坐标点
            in_=table  # 【核心关键】绑定父容器为表格table，所有坐标都是相对表格的！
        )

    def on_table_leave(self, event):
        """鼠标离开表格时，隐藏标题悬浮提示"""
        self.title_tooltip.place_forget()

    # ========== 气泡提示 ==========
    def show_tooltip(self, msg, auto_hide=True):
        """显示气泡提示，2秒后自动消失，msg=提示文本"""
        if self.tooltip_after_id:
            self.after_cancel(self.tooltip_after_id)
        self.tooltip_label.config(text=msg)
        self.tooltip_label.place_forget()
        self.tooltip_label.place(relx=0.5, rely=1.0, y=-20, anchor="s")
        if auto_hide:
            self.tooltip_after_id = self.after(3000, self.hide_tooltip)
        else:
            self.tooltip_after_id = None

    def hide_tooltip(self):
        """隐藏气泡提示"""
        self.tooltip_label.place_forget()
        self.tooltip_after_id = None

    def clear_tooltip(self):
        """清空气泡文本"""
        self.tooltip_label.config(text="")

    def show_progress_tooltip(self, msg):
        """实时进度提示专用：只更新气泡文本+显示气泡，无定时器、不自动消失、不清除任何标识"""
        self.tooltip_label.config(text=msg)
        self.tooltip_label.place_forget()
        self.tooltip_label.place(relx=0.5, rely=1.0, y=-20, anchor="s")

    # ========== 禅道创建-添加记录 核心方法开始 ==========
    def open_create_zentao_popup(self):
        """打开【添加创建禅道-添加记录】表单弹窗 极简重写✅ 800*600可变尺寸 + 信息框固定高450 + 按钮第一行布局"""
        self.reset_table_style(self.TABLE_TYPE_CREATE_ZENTAO)

        # 关闭已存在的弹窗
        if self.create_zentao_popup and self.create_zentao_popup.winfo_exists():
            self.create_zentao_popup.destroy()

        # 弹窗基础配置：初始800x600、可拉伸、置顶、模态框
        self.create_zentao_popup = tk.Toplevel(self)
        self.create_zentao_popup.title(self.CREATE_ZENTAO_POPUP_TITLE)
        self.create_zentao_popup.geometry("720x480")
        self.create_zentao_popup.resizable(width=True, height=True)
        self.create_zentao_popup.attributes("-topmost", True)
        self.create_zentao_popup.grab_set()

        # 弹窗居中显示
        self.create_zentao_popup.update_idletasks()
        win_w = self.create_zentao_popup.winfo_width()
        win_h = self.create_zentao_popup.winfo_height()
        x = (self.create_zentao_popup.winfo_screenwidth() - win_w) // 2
        y = (self.create_zentao_popup.winfo_screenheight() - win_h) // 2
        self.create_zentao_popup.geometry(f"+{x}+{y}")

        # 固定布局变量，无任何动态计算
        pad_y = 25
        base_x = 40
        label_width = 80
        main_input_w = 500
        gap = 15

        # ===================== 1. 第一行：Jira项目 → 编号 → 添加按钮 → 清空按钮 =====================
        tk.Label(self.create_zentao_popup, text="Jira项目：", anchor="w", width=label_width).place(x=base_x, y=pad_y)
        project_var = tk.StringVar(value="")
        project_combobox = tk.ttk.Combobox(self.create_zentao_popup, textvariable=project_var,
                                           values=self.jira_project_name_list, state="readonly", font=("微软雅黑", 10))
        project_combobox.place(x=base_x + label_width + gap, y=pad_y, width=150)
        if self.jira_project_name_list:
            project_var.set(self.jira_project_name_list[0])
        self.create_form_widgets["project_combobox"] = project_combobox
        self.create_form_widgets["project_var"] = project_var

        tk.Label(self.create_zentao_popup, text="编号：", anchor="w").place(x=300, y=pad_y)
        jira_no_entry = tk.Entry(self.create_zentao_popup, font=("微软雅黑", 10))
        jira_no_entry.place(x=350, y=pad_y, width=100)
        # 纯数字校验 + 防抖查询 + 失焦查询 事件绑定
        jira_no_entry.bind("<KeyPress>", self.__only_allow_digit_input)
        jira_no_entry.bind("<KeyRelease>", self.__jira_input_debounce)
        jira_no_entry.bind("<FocusOut>", lambda e: self.__query_single_jira_info())
        self.create_form_widgets["jira_no_entry"] = jira_no_entry

        # 添加按钮（原确认按钮改名）+ 清空按钮，紧贴编号框
        tk.Button(self.create_zentao_popup, text="添加", width=8, height=1, bg="#4CAF50", fg="white", relief="flat",
                  command=self.confirm_create_zentao_record).place(x=500, y=pad_y - 2)
        tk.Button(self.create_zentao_popup, text="清空", width=8, height=1, bg="#F44336", fg="white", relief="flat",
                  command=self.clear_create_zentao_form).place(x=590, y=pad_y - 2)

        # ===================== 2. 第二行：禅道模块 + 模块ID + 指派人 =====================
        pad_y += 60
        tk.Label(self.create_zentao_popup, text="禅道模块：", anchor="w", width=label_width).place(x=base_x, y=pad_y)
        module_list = list(self.zentao_create_map.keys())
        module_var = tk.StringVar(value="")
        module_combobox = tk.ttk.Combobox(self.create_zentao_popup, textvariable=module_var, values=module_list,
                                          state="readonly", font=("微软雅黑", 10))
        module_combobox.place(x=base_x + label_width + gap, y=pad_y, width=150)
        self.create_form_widgets["module_combobox"] = module_combobox
        self.create_form_widgets["module_var"] = module_var

        # 模块ID展示
        tk.Label(self.create_zentao_popup, text="模块ID：", anchor="w").place(x=300, y=pad_y)
        pid_label = tk.Label(self.create_zentao_popup, text="", bg="#F5F5F5", relief="solid", bd=1, width=10,
                             anchor="w", padx=5, font=("微软雅黑", 10))
        pid_label.place(x=355, y=pad_y)
        self.create_form_widgets["pid_label"] = pid_label

        # 指派人展示
        tk.Label(self.create_zentao_popup, text="指派人：", anchor="w").place(x=460, y=pad_y)
        assignee_label = tk.Label(self.create_zentao_popup, text="", bg="#F5F5F5", relief="solid", bd=1, width=15,
                                  anchor="w", padx=5, font=("微软雅黑", 10))
        assignee_label.place(x=515, y=pad_y)
        self.create_form_widgets["assignee_label"] = assignee_label

        # 禅道模块选中联动事件
        def select_module_event(event):
            select_module = module_var.get()
            module_info = self.zentao_create_map.get(select_module, {})
            pid_label.config(text=module_info.get("zt_pid", ""))
            assignee_label.config(text=module_info.get("zt_assignee", ""))

        module_combobox.bind("<<ComboboxSelected>>", select_module_event)

        # ===================== 3. Jira基本信息框 【核心：固定高度450px 写死】 =====================
        pad_y += 60
        tk.Label(self.create_zentao_popup, text="Jira基本信息：", anchor="w", width=label_width).place(x=base_x, y=pad_y)
        # 文本框：宽度600，高度450 固定值，永不变化
        jira_info_text = tk.Text(self.create_zentao_popup, font=("微软雅黑", 9), wrap=tk.WORD, bg="#F5F5F5",
                                 relief="solid", bd=1)
        jira_info_text.place(x=base_x + label_width + gap, y=pad_y, width=main_input_w, height=300)
        # 滚动条：高度和文本框一致450 固定值
        jira_info_scroll = tk.Scrollbar(self.create_zentao_popup, orient=tk.VERTICAL, command=jira_info_text.yview)
        jira_info_scroll.place(x=base_x + label_width + gap + main_input_w, y=pad_y, height=300)
        jira_info_text.configure(yscrollcommand=jira_info_scroll.set)

        # 默认提示文本 + 只读模式（禁止手动编辑）
        default_tip = "✅ 请输入Jira编号，将自动查询并展示Jira完整信息！"
        jira_info_text.insert(tk.END, default_tip)
        jira_info_text.config(state=tk.DISABLED)
        self.create_form_widgets["jira_info_text"] = jira_info_text

    def clear_create_zentao_form(self):
        """清空禅道创建表单的所有数据，恢复初始状态"""
        # Jira项目下拉框：清空后默认选中第一条CNUXBTRACK
        # 清空防抖定时器+查询缓存，双重清理
        if self.jira_query_timer:
            self.after_cancel(self.jira_query_timer)
        self.cached_jira_query_result = None  # 新增：清空查询结果缓存
        # 清空编号输入框
        self.create_form_widgets.get("jira_no_entry").delete(0, tk.END)
        # ========== 新增：清空Jira基本信息框，恢复默认提示 ==========
        jira_info_text = self.create_form_widgets.get("jira_info_text")
        jira_info_text.config(state=tk.NORMAL)
        jira_info_text.delete(1.0, tk.END)
        jira_info_text.insert(tk.END, "✅ 请输入Jira编号后自动查询信息")
        jira_info_text.config(state=tk.DISABLED)
        # 原有清空逻辑保持不变
        self.create_form_widgets.get("module_var").set("")
        self.create_form_widgets.get("pid_label").config(text="")
        self.create_form_widgets.get("assignee_label").config(text="")

    def __only_allow_digit_input(self, event):
        """
        核心校验方法：仅允许输入纯数字，屏蔽所有非数字按键
        放行：0-9数字键、小键盘0-9、退格键(BackSpace)、删除键(Delete)、左/右方向键
        拦截：字母、中文、空格、回车、Shift、Ctrl、Alt、Tab、标点符号等所有其他按键
        """
        # 可放行的按键列表（数字相关+编辑相关，保证正常输入和删除）
        allowed_keys = [
            # 主键盘数字键
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            # 小键盘数字键
            'KP_0', 'KP_1', 'KP_2', 'KP_3', 'KP_4', 'KP_5', 'KP_6', 'KP_7', 'KP_8', 'KP_9',
            # 编辑按键：退格、删除、左右方向键（必备，保证输入体验）
            'BackSpace', 'Delete', 'Left', 'Right'
        ]
        # 判断按键是否在放行列表中，不在则直接拦截
        if event.keysym not in allowed_keys:
            return "break"  # 返回break：tkinter底层阻断该按键的输入行为

    def __jira_input_debounce(self, event):
        """防抖延迟查询：输入停止1秒后才触发查询，避免频繁请求"""
        # 清除上一次的定时器，重置计时
        if self.jira_query_timer:
            self.after_cancel(self.jira_query_timer)
        # 延迟800毫秒后执行查询，输入过程中不会重复发起请求
        self.jira_query_timer = self.after(1000, self.__query_single_jira_info)

    def __query_single_jira_info(self):
        """
        核心私有方法：查询单个Jira详情并回显到信息框 + 存入缓存，只查询一次，全局复用
        逻辑：获取项目+编号 → 拼接JiraKey → 拼接JQL语句 → 调用services查询 → 缓存结果 → 解析结果 → 回显内容
        异常兜底：HTTP错误/无结果/空列表/其他异常，均展示对应提示
        """
        # 1. 获取表单值
        select_project = self.create_form_widgets.get("project_var").get().strip()
        jira_no = self.create_form_widgets.get("jira_no_entry").get().strip()
        jira_info_text = self.create_form_widgets.get("jira_info_text")

        # 2. 前置校验：项目未选/编号为空，直接重置为默认提示，不查询+清空缓存
        if not select_project or not jira_no:
            self.cached_jira_query_result = None  #  清空缓存
            jira_info_text.config(state=tk.NORMAL)
            jira_info_text.delete(1.0, tk.END)
            jira_info_text.insert(tk.END, " 请输入Jira编号后自动查询信息")
            jira_info_text.config(state=tk.DISABLED)
            return

        # 3. 拼接完整JiraKey和查询用JQL语句 (核心：key=xxx)
        jira_key = f"{select_project}-{jira_no}"
        jql_text = f"key={jira_key}"

        # 4. 耗时操作-线程调度：防止弹窗卡死，必加！
        def query_task():
            try:
                # 调用services的查询方法 → 仅执行这一次请求
                query_result = services.get_jira_sync_list(jql_text)

                # ==========  核心新增：把查询结果存入全局缓存，后续所有逻辑复用这个结果 ==========
                self.cached_jira_query_result = query_result

                # ========== 分场景解析返回结果 ==========
                show_content = ""
                # 场景1：查询返回HTTPError异常 → 报错提示
                if isinstance(query_result, HTTPError):
                    show_content = f"❌ 查询失败：Jira接口请求异常，错误码：{query_result.code}，原因：{query_result.reason}"
                # 场景2：查询返回空列表 → 未找到该JiraID
                elif isinstance(query_result, list) and len(query_result) == 0:
                    show_content = f"❌ 未查询到Jira信息：{jira_key}，该JiraID不存在或无权限访问！"
                # 场景3：查询成功，返回有效数据列表（只有1条）
                elif isinstance(query_result, list) and len(query_result) >= 1:
                    #  原始未处理数据（入参）：query_result[0] 是完整的原始dict
                    raw_jira_data = query_result[0]
                    #  调用你新增的工具方法：入参=原始数据，返回=处理后的精简dict

                    brief_jira_dict = common.get_jira_brief_result(raw_jira_data)

                    #  拼接处理后的精简数据，展示到UI → 替换原来的原始数据拼接逻辑
                    for brief_key, brief_value in brief_jira_dict.items():
                        show_content += f"{brief_key}：{brief_value}\n\n"
                    # 补全成功提示
                    show_content += "✅ 查询成功：已展示Jira精简核心信息（数据已格式化处理）"
                # 场景4：其他未知异常
                else:
                    show_content = f"❌ 查询异常：无法解析{jira_key}的返回结果，请检查JiraID是否正确！"

                # ========== 主线程回显内容到UI ==========
                self.run_in_main_thread(self.__show_jira_info_to_text, show_content)

            except Exception as e:
                self.cached_jira_query_result = None  #  异常时清空缓存
                self.run_in_main_thread(self.__show_jira_info_to_text, f"❌ 查询出错：{str(e)}")

        # 启动查询线程
        self.run_in_main_thread(query_task)

    # ========== 私有辅助方法 - 回显内容到信息框 ==========
    def __show_jira_info_to_text(self, content):
        """给Jira信息文本框赋值，封装只读/可写切换逻辑"""
        jira_info_text = self.create_form_widgets.get("jira_info_text")
        jira_info_text.config(state=tk.NORMAL)  # 临时解除只读，赋值内容
        jira_info_text.delete(1.0, tk.END)  # 清空原有内容
        jira_info_text.insert(tk.END, content)  # 插入新内容
        jira_info_text.config(state=tk.DISABLED)  # 恢复只读，禁止手动编辑

    def get_table_all_data(self):
        """获取表格内所有数据的完整列表（适配save_data_to_json的格式），复用现有row_history_map"""
        table_all_data = []
        table = self.tk_table_table_1
        for row_id in table.get_children():
            if row_id in self.row_history_map:
                table_all_data.append(self.row_history_map[row_id])
        return table_all_data

    def confirm_create_zentao_record(self):
        """确认添加禅道创建记录：复用缓存查询结果做校验 → 组装数据 → 添加到表格 → 保存到JSON → 提示结果，无重复请求"""
        # 1. 表单取值
        select_project = self.create_form_widgets.get("project_var").get().strip()
        jira_no = self.create_form_widgets.get("jira_no_entry").get().strip()
        select_module = self.create_form_widgets.get("module_var").get().strip()

        # ========== 原有基础校验，不变 ==========
        if not self.zentao_create_map:
            self.show_tooltip("未读取到禅道模块配置，请检查.config文件！")
            return
        module_info = self.zentao_create_map.get(select_module, {})
        zt_pid = module_info.get("zt_pid", "")
        zt_assignee = module_info.get("zt_assignee", "")

        if not select_project:
            self.show_tooltip("请选择Jira项目名称！")
            return
        if not jira_no:
            self.show_tooltip("请输入Jira编号！")
            return
        if not jira_no.isdigit():
            self.show_tooltip("Jira编号仅支持输入纯数字！")
            return
        if not select_module:
            self.show_tooltip("请选择禅道模块！")
            return

        # 2. 拼接完整JiraID
        jira_id = f"{select_project}-{jira_no}"

        # ========== ✅ 核心优化1：读取缓存的查询结果，做HTTP错误校验，无任何重复请求 ==========
        query_result = self.cached_jira_query_result
        # 校验场景1：缓存为空 → 未查询/查询异常，提示先查询
        if query_result is None:
            self.show_tooltip(f"❌ 请先查询Jira信息：{jira_id}，再点击确认！")
            return
        # 校验场景2：缓存结果是HTTPError → 阻断提交，提示错误，核心需求实现！
        if isinstance(query_result, HTTPError):
            self.show_tooltip(f"❌ Jira查询失败（HTTP错误 {query_result.code}），{jira_id} 无法提交，请检查网络或JiraID！")
            return

        # ========== ✅ 核心优化2：复用缓存结果，回填真实标题，无任何重复请求 ==========
        jira_summary = "标题"  # 默认值
        if isinstance(query_result, list) and len(query_result) >= 1:
            jira_summary = query_result[0].get("jira_summary", "标题")

        # 3. 组装数据字典，原有逻辑不变
        new_record = {
            "jira_key": jira_id,
            "jira_summary": jira_summary,
            "zentao_module": select_module,
            "zentao_module_id": zt_pid,
            "zentao_assignee": zt_assignee,
            "zentao_assignee_id": "",
            "zentao_create_result": "待创建",
            "zentao_create_comment": ""
        }

        # 4. 添加数据到表格 + 保存JSON，原有逻辑不变
        table = self.tk_table_table_1
        row_id = table.insert('', tk.END, values=[
            len(table.get_children()) + 1 if table.get_children() else 1,
            new_record["jira_summary"],
            new_record["jira_key"],
            new_record["zentao_module"],
            new_record["zentao_module_id"],
            new_record["zentao_assignee"],
            new_record["zentao_create_result"],
            new_record["zentao_create_comment"]
        ])
        self.row_history_map[row_id] = new_record

        table_all_data = self.get_table_all_data()
        save_success, save_msg = common.save_data_to_json(table_all_data)
        if save_success:
            self.show_tooltip(f"添加成功！{save_msg}")
        else:
            self.show_tooltip(f"添加成功，保存失败：{save_msg}")

        # 5. 清空表单，保持弹窗打开
        self.clear_create_zentao_form()
    # ========== 删除选中行核心方法 - 仅对 禅道创建表格 生效，不影响其他表格 ==========
    def delete_selected_record(self):
        table = self.tk_table_table_1
        # 1. 核心校验：获取当前表格列，判断是否为【禅道创建专用表格】
        current_cols = table["columns"]
        is_zentao_create_table = "禅道模块" in current_cols and "禅道创建结果" in current_cols

        if not is_zentao_create_table:
            self.show_tooltip("⚠️ 仅禅道创建表格支持删除操作！")
            return

        # 2. 获取选中的行id
        selected_items = table.selection()
        if not selected_items:
            self.show_tooltip("⚠️ 请选中需要删除的行！")
            return

        # 3. 循环删除选中行 + 同步删除映射字典数据（防止内存残留）
        del_count = 0
        for row_id in selected_items:
            table.delete(row_id)
            if row_id in self.row_history_map:
                del self.row_history_map[row_id]
                del_count += 1

        # 4. 删除后自动保存最新数据到JSON，和添加逻辑一致
        table_all_data = self.get_table_all_data()
        save_success, save_msg = common.save_data_to_json(table_all_data)

        # 5. 气泡提示删除结果
        if save_success:
            self.show_tooltip(f"✅ 成功删除 {del_count} 条记录，数据已保存")
        else:
            self.show_tooltip(f"✅ 成功删除 {del_count} 条记录，保存失败：{save_msg}")
    # ========== 禅道创建-添加记录 核心方法结束 ==========


    # ========== 主线程调用UI方法的工具函数 ==========
    def run_in_main_thread(self, func, *args):
        self.after(0, lambda: func(*args))


class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.config(menu=self.create_menu())
        self.ctl.init(self)

    def create_menu(self):
        menu = Menu(self,tearoff=False)
        menu.add_cascade(label="原始功能",menu=self.menu_sub_test_1(menu))
        return menu

    def menu_sub_test_1(self,parent):
        menu = Menu(parent,tearoff=False)
        menu.add_command(label="从Excel创建禅道",command=self.ctl.sync_zentao_from_excel)
        return menu

    def __event_bind(self):
        self.tk_button_button_search.bind('<Button-1>',self.ctl.search)
        self.tk_button_button_update.bind('<Button-1>',self.ctl.update)
        # ========== 添加记录按钮 点击添加记录 → 先切换表头 → 再打开弹窗 ==========
        self.tk_button_add_record.bind('<Button-1>', lambda e: [self.reset_table_style(self.TABLE_TYPE_CREATE_ZENTAO), self.open_create_zentao_popup()])
        self.tk_button_submit_create.bind('<Button-1>', lambda e: self.ctl.sync_table_to_zentao())
        self.tk_button_del_record.bind('<Button-1>', lambda e: self.delete_selected_record())
        pass

    def __style_config(self):
        pass