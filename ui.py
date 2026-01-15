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
        TABLE_TYPE_CREATE_ZENTAO: {"ID": 30, "标题": 300, "JiraID": 130, "禅道模块": 60, "禅道指派人": 60,
                            "禅道创建结果":60, "禅道创建备注": 450},
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

    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_label_label_1 = self.__tk_label_label_1(self)
        self.tk_table_table_1 = self.__tk_table_table_1(self)
        self.tk_button_button_search = self.__tk_button_button_search(self)
        self.tk_button_button_update = self.__tk_button_button_update(self)
        self.tk_input_jql = self.__tk_input_jql(self)

        # ========== 禅道创建区域 控件初始化 ==========
        self.tk_label_zentao_create = self.__tk_label_zentao_create(self)
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
            self.tk_label_zentao_create.place(x=base_x - 80, y=base_y, width=80, height=30)
            self.tk_button_add_record.place(x=base_x, y=base_y, width=100, height=30)
            self.tk_button_submit_create.place(x=base_x + 110, y=base_y, width=100, height=30)

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

    # ========== 提交创建 按钮 定义 ==========
    def __tk_button_submit_create(self, parent):
        btn = Button(parent, text="提交记录", takefocus=False)
        btn.place(x=1190, y=760, width=100, height=30)
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
    # ========== 点击单元格展示完整历史 ✅精准修改：仅默认表格的历史列触发弹窗 ==========
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
        # ========== 预留按钮事件绑定入口（后续在control.py实现逻辑即可） ==========
        self.tk_button_add_record.bind('<Button-1>', self.ctl.add_zentao_record)
        self.tk_button_submit_create.bind('<Button-1>', self.ctl.submit_zentao_create)
        pass
    def __style_config(self):
        pass