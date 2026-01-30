import tkinter as tk
from tkinter import ttk

#========mario module import========
import threading
import pygame as pg
from tkinter import messagebox
from bonus.bn_breakout import GameBreakoutWindow
from bonus.bn_snake import GameSnakeWindow
from bonus.bn_2048 import Game2048Window
from bonus.bn_tetris import GameTetrisWindow
# 导入超级玛丽核心启动函数（复刻mario_level_1.py的核心逻辑）
from bonus.mario.data.main import main as mario_main
#========mario module import end========


class GameUI:
    def __init__(self, parent):
        self.parent = parent
        self.about_dialog = None  # 原弹窗引用
        self.game_window = None  # 游戏窗口引用
        self.mario_thread = None  # mario线程标记（避免重复启动）

    def create_game_select_dialog(self):
        """创建关于弹窗（保持原有逻辑不变）"""
        # 创建弹窗
        self.about_dialog = tk.Toplevel(self.parent)
        self.about_dialog.title("其他")
        self.about_dialog.geometry("200x300")
        self.about_dialog.resizable(False, False)
        self.about_dialog.transient(self.parent)
        self.about_dialog.grab_set()

        # ==========弹窗居中（相对于主窗口） ==========
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

        # 修改Breakout按钮的绑定函数
        ttk.Button(content_frame, text="Mario", command=self.open_mario_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="Tetris", command=self.open_tetris_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="2048", command=self.open_2048_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="Breakout", command=self.open_breakout_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="Snake", command=self.open_snake_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="关闭", command=self.on_close_game_select).pack(padx=5, pady=5)

    # ========== open_mario_game 直接内嵌启动逻辑 ==========
    def open_mario_game(self):
        """打开超级玛丽游戏（内嵌启动逻辑，新开线程不阻塞tkinter）"""
        # 1. 关闭原有游戏选择弹窗（保留原有UI交互）
        self.on_close_game_select()

        # 2. 防止重复启动游戏（检查线程是否已运行）
        if self.mario_thread and self.mario_thread.is_alive():
            messagebox.showinfo("提示", "超级玛丽游戏已在运行中！")
            return

        # 3. 定义游戏启动核心函数（复刻mario_level_1.py的逻辑）
        def run_mario():
            try:
                # 直接调用超级玛丽的核心启动函数（和mario_level_1.py的main()一致）
                mario_main()
            except Exception as e:
                # 捕获游戏运行异常，弹窗提示（不影响tkinter主程序）
                messagebox.showerror("游戏运行异常", f"超级玛丽运行出错：\n{str(e)}")
            finally:
                # 无论游戏正常退出/异常崩溃，都清理Pygame资源
                pg.quit()
                # 重置线程标记，方便再次启动
                self.mario_thread = None

        # 4. 新开线程运行游戏（核心：避免阻塞tkinter主线程）
        self.mario_thread = threading.Thread(target=run_mario, daemon=True)
        self.mario_thread.start()

    def open_breakout_game(self):
        """打开打砖块游戏窗口"""
        # 关闭原有弹窗
        self.on_close_game_select()
        # 创建游戏窗口
        self.game_window = GameBreakoutWindow(self.parent)

    def open_snake_game(self):
        """打开贪吃蛇游戏窗口"""
        self.on_close_game_select()  # 关闭选择弹窗
        self.game_window = GameSnakeWindow(self.parent)  # 创建贪吃蛇游戏窗口

    def open_2048_game(self):
        """打开2048游戏窗口"""
        self.on_close_game_select()
        self.game_window = Game2048Window(self.parent)

    def open_tetris_game(self):
        """打开俄罗斯方块游戏窗口"""
        # 关闭原有弹窗
        self.on_close_game_select()
        # 创建俄罗斯方块游戏窗口
        self.game_window = GameTetrisWindow(self.parent)

    def on_close_game_select(self):
        """关闭关于弹窗"""
        if self.about_dialog:
            self.about_dialog.destroy()
            self.about_dialog = None








