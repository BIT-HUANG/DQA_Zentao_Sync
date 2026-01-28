import tkinter as tk
from tkinter import ttk
import random

#========mario module import========
import threading
import pygame as pg
import sys
from tkinter import messagebox
# 导入超级玛丽核心启动函数（复刻mario_level_1.py的核心逻辑）
from data.main import main as mario_main
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
        self.game_window = BreakoutGameWindow(self.parent)

    def open_snake_game(self):
        """打开贪吃蛇游戏窗口"""
        self.on_close_game_select()  # 关闭选择弹窗
        self.game_window = SnakeGameWindow(self.parent)  # 创建贪吃蛇游戏窗口

    def open_2048_game(self):
        """打开2048游戏窗口"""
        self.on_close_game_select()
        self.game_window = Game2048Window(self.parent)

    def open_tetris_game(self):
        """打开俄罗斯方块游戏窗口"""
        # 关闭原有弹窗
        self.on_close_game_select()
        # 创建俄罗斯方块游戏窗口
        self.game_window = TetrisGameWindow(self.parent)

    def on_close_game_select(self):
        """关闭关于弹窗"""
        if self.about_dialog:
            self.about_dialog.destroy()
            self.about_dialog = None


class BreakoutGameWindow:
    """打砖块游戏窗口类（优化版-鼠标控制）"""

    def __init__(self, parent):
        # 游戏窗口配置
        self.root = tk.Toplevel(parent)
        self.root.title("打砖块游戏 Breakout")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.transient(parent)

        # 游戏参数
        self.PADDLE_WIDTH = 80
        self.PADDLE_HEIGHT = 15
        self.BALL_SIZE = 10
        self.BRICK_WIDTH = 50
        self.BRICK_HEIGHT = 20
        self.BRICK_ROWS = 5
        self.BRICK_COLS = 10
        self.BALL_SPEED_X = 4
        self.BALL_SPEED_Y = -4

        # 游戏状态
        self.score = 0
        self.lives = 3
        self.game_running = False  # 游戏运行状态
        self.game_paused = False  # 游戏暂停状态

        # 创建游戏画布
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 隐藏画布中的鼠标光标
        self.canvas.config(cursor="none")

        # 显示得分和生命
        self.score_text = self.canvas.create_text(
            50, 10, text=f"得分: {self.score}", fill="white", font=("Arial", 12)
        )
        self.lives_text = self.canvas.create_text(
            550, 10, text=f"生命: {self.lives}", fill="white", font=("Arial", 12)
        )

        # 初始化游戏元素
        self.init_game_elements()

        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.toggle_game_state)  # 左键控制开始/暂停
        self.canvas.bind("<Motion>", self.move_paddle_with_mouse)  # 鼠标移动控制球拍

        # 显示开始提示
        self.start_prompt = self.canvas.create_text(
            300, 200, text="单击鼠标左键开始游戏\n鼠标移动控制球拍",
            fill="white", font=("Arial", 16)
        )

        # 显示暂停提示（初始隐藏）
        self.pause_prompt = self.canvas.create_text(
            300, 230, text="游戏已暂停 | 单击左键继续",
            fill="yellow", font=("Arial", 14)
        )
        self.canvas.itemconfig(self.pause_prompt, state="hidden")

        # 游戏循环
        self.game_loop()

    def init_game_elements(self):
        """初始化游戏元素（球拍、小球、砖块）"""
        # 创建球拍（居中底部）
        self.paddle = self.canvas.create_rectangle(
            300 - self.PADDLE_WIDTH // 2, 380 - self.PADDLE_HEIGHT,
            300 + self.PADDLE_WIDTH // 2, 380,
            fill="blue"
        )

        # 创建小球（初始在球拍上方）
        self.ball = self.canvas.create_oval(
            300 - self.BALL_SIZE // 2, 380 - self.PADDLE_HEIGHT - self.BALL_SIZE,
            300 + self.BALL_SIZE // 2, 380 - self.PADDLE_HEIGHT,
            fill="white"
        )

        # 创建砖块
        self.bricks = []
        brick_colors = ["red", "orange", "yellow", "green", "cyan"]
        for row in range(self.BRICK_ROWS):
            row_color = brick_colors[row % len(brick_colors)]
            for col in range(self.BRICK_COLS):
                x1 = col * (self.BRICK_WIDTH + 5) + 30
                y1 = row * (self.BRICK_HEIGHT + 5) + 40
                x2 = x1 + self.BRICK_WIDTH
                y2 = y1 + self.BRICK_HEIGHT
                brick = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=row_color, outline="white"
                )
                self.bricks.append(brick)

        # 小球初始速度（静止）
        self.ball_dx = 0
        self.ball_dy = 0

    def toggle_game_state(self, event):
        """鼠标左键切换游戏开始/暂停状态"""
        if self.lives <= 0 or not self.bricks:
            # 游戏结束/通关状态，点击左键不响应（需点重新开始按钮）
            return

        if not self.game_running:
            # 游戏未开始 → 开始游戏
            self.game_running = True
            self.game_paused = False
            self.ball_dx = self.BALL_SPEED_X
            self.ball_dy = self.BALL_SPEED_Y
            # 移除开始提示，隐藏暂停提示
            self.canvas.delete(self.start_prompt)
            self.canvas.itemconfig(self.pause_prompt, state="hidden")
        else:
            # 游戏运行中 → 切换暂停状态
            self.game_paused = not self.game_paused
            if self.game_paused:
                # 暂停游戏，显示暂停提示
                self.canvas.itemconfig(self.pause_prompt, state="normal")
            else:
                # 继续游戏，隐藏暂停提示
                self.canvas.itemconfig(self.pause_prompt, state="hidden")

    def move_paddle_with_mouse(self, event):
        """鼠标移动控制球拍位置"""
        if self.lives <= 0:
            return

        # 获取鼠标x坐标（y坐标固定）
        mouse_x = event.x
        # 计算球拍新位置（保证球拍中心与鼠标对齐）
        paddle_x1 = mouse_x - self.PADDLE_WIDTH // 2
        paddle_x2 = mouse_x + self.PADDLE_WIDTH // 2

        # 边界检测（球拍不超出画布）
        if paddle_x1 < 0:
            paddle_x1 = 0
            paddle_x2 = self.PADDLE_WIDTH
        elif paddle_x2 > 600:
            paddle_x1 = 600 - self.PADDLE_WIDTH
            paddle_x2 = 600

        # 更新球拍位置（y坐标固定）
        self.canvas.coords(
            self.paddle,
            paddle_x1, 380 - self.PADDLE_HEIGHT,
            paddle_x2, 380
        )

        # 如果游戏未开始，同步移动小球位置
        if not self.game_running:
            self.canvas.coords(
                self.ball,
                mouse_x - self.BALL_SIZE // 2, 380 - self.PADDLE_HEIGHT - self.BALL_SIZE,
                mouse_x + self.BALL_SIZE // 2, 380 - self.PADDLE_HEIGHT
            )

    def check_collisions(self):
        """检测碰撞（边界、球拍、砖块）"""
        # 获取小球位置
        x1, y1, x2, y2 = self.canvas.coords(self.ball)

        # 左右边界碰撞
        if x1 <= 0 or x2 >= 600:
            self.ball_dx *= -1

        # 上边界碰撞
        if y1 <= 0:
            self.ball_dy *= -1

        # 下边界碰撞（生命减1）
        if y2 >= 400:
            self.lives -= 1
            self.canvas.itemconfig(self.lives_text, text=f"生命: {self.lives}")
            # 重置小球和球拍位置
            self.reset_ball_and_paddle()
            if self.lives <= 0:
                self.game_over()
            return

        # 检测小球与球拍碰撞
        paddle_coords = self.canvas.coords(self.paddle)
        if (y2 >= paddle_coords[1] and y1 <= paddle_coords[3] and
                x2 >= paddle_coords[0] and x1 <= paddle_coords[2]):
            # 反弹（根据碰撞位置调整x方向速度，增加游戏趣味性）
            self.ball_dy *= -1
            ball_center = (x1 + x2) / 2
            paddle_center = (paddle_coords[0] + paddle_coords[2]) / 2
            self.ball_dx = (ball_center - paddle_center) / 8

        # 检测小球与砖块碰撞
        hit_items = self.canvas.find_overlapping(x1, y1, x2, y2)
        for item in hit_items:
            if item in self.bricks:
                # 移除砖块
                self.canvas.delete(item)
                self.bricks.remove(item)
                # 得分增加
                self.score += 10
                self.canvas.itemconfig(self.score_text, text=f"得分: {self.score}")
                # 反弹
                self.ball_dy *= -1
                # 检查是否通关
                if not self.bricks:
                    self.game_win()
                break

    def reset_ball_and_paddle(self):
        """重置小球和球拍位置"""
        self.game_running = False
        self.game_paused = False
        # 重置球拍位置到中心
        self.canvas.coords(
            self.paddle,
            300 - self.PADDLE_WIDTH // 2, 380 - self.PADDLE_HEIGHT,
            300 + self.PADDLE_WIDTH // 2, 380
        )
        # 重置小球位置
        self.canvas.coords(
            self.ball,
            300 - self.BALL_SIZE // 2, 380 - self.PADDLE_HEIGHT - self.BALL_SIZE,
            300 + self.BALL_SIZE // 2, 380 - self.PADDLE_HEIGHT
        )
        # 重置小球速度
        self.ball_dx = 0
        self.ball_dy = 0
        # 隐藏暂停提示，显示重新开始提示
        self.canvas.itemconfig(self.pause_prompt, state="hidden")
        self.start_prompt = self.canvas.create_text(
            300, 200, text=f"生命剩余: {self.lives}\n点击重新开始",
            fill="white", font=("Arial", 16)
        )

    def game_over(self):
        """游戏结束"""
        self.game_running = False
        self.game_paused = False
        self.canvas.create_text(
            300, 300, text=f"游戏结束！\n最终得分: {self.score}",
            fill="red", font=("Arial", 20)
        )
        # 添加重新开始按钮
        restart_btn = tk.Button(
            self.root, text="重新开始", command=self.restart_game,
            font=("Arial", 14), bg="green", fg="white"
        )
        restart_btn_window = self.canvas.create_window(300, 250, window=restart_btn)

    def game_win(self):
        """游戏胜利"""
        self.game_running = False
        self.game_paused = False
        self.canvas.create_text(
            300, 200, text=f"恭喜通关！\n最终得分: {self.score}",
            fill="yellow", font=("Arial", 20)
        )
        # 添加重新开始按钮
        restart_btn = tk.Button(
            self.root, text="重新开始", command=self.restart_game,
            font=("Arial", 14), bg="green", fg="white"
        )
        restart_btn_window = self.canvas.create_window(300, 250, window=restart_btn)

    def restart_game(self):
        """重新开始游戏"""
        # 清空画布
        self.canvas.delete("all")
        # 重置游戏状态
        self.score = 0
        self.lives = 3
        self.game_running = False
        self.game_paused = False

        # 重新初始化
        self.score_text = self.canvas.create_text(
            50, 10, text=f"得分: {self.score}", fill="white", font=("Arial", 12)
        )
        self.lives_text = self.canvas.create_text(
            550, 10, text=f"生命: {self.lives}", fill="white", font=("Arial", 12)
        )
        self.init_game_elements()

        # 显示开始提示
        self.start_prompt = self.canvas.create_text(
            300, 200, text="单击鼠标左键开始游戏\n鼠标移动控制球拍",
            fill="white", font=("Arial", 16)
        )

        # 重建暂停提示（初始隐藏）
        self.pause_prompt = self.canvas.create_text(
            300, 230, text="游戏已暂停 | 单击左键继续",
            fill="yellow", font=("Arial", 14)
        )
        self.canvas.itemconfig(self.pause_prompt, state="hidden")

    def game_loop(self):
        """游戏主循环"""
        if self.game_running and not self.game_paused:
            # 仅在游戏运行且未暂停时更新
            # 移动小球
            self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
            # 检测碰撞
            self.check_collisions()
        # 循环调用（60帧/秒）
        self.root.after(16, self.game_loop)

class SnakeGameWindow:
    """贪吃蛇游戏窗口类（键盘控制版：方向键控方向，空格键开始/暂停）"""

    def __init__(self, parent):
        # 游戏窗口配置（原有逻辑不变）
        self.root = tk.Toplevel(parent)
        self.root.title("贪吃蛇游戏 Snake")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.transient(parent)

        # 游戏参数（原有逻辑不变）
        self.BLOCK_SIZE = 20  # 蛇/食物的方块大小
        self.SNAKE_SPEED = 250  # 移动间隔（ms），数值越小速度越快
        self.DIRECTIONS = {  # 方向映射
            "UP": (0, -self.BLOCK_SIZE),
            "DOWN": (0, self.BLOCK_SIZE),
            "LEFT": (-self.BLOCK_SIZE, 0),
            "RIGHT": (self.BLOCK_SIZE, 0)
        }

        # 游戏状态（原有逻辑不变）
        self.score = 0
        self.game_running = False
        self.game_paused = False
        self.current_dir = "RIGHT"  # 初始方向
        self.next_dir = "RIGHT"     # 缓冲方向（避免快速转向冲突）

        # 创建游戏画布（原有逻辑不变）
        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 恢复鼠标光标（键盘控制不需要隐藏）
        self.canvas.config(cursor="arrow")

        # 显示得分（原有逻辑不变）
        self.score_text = self.canvas.create_text(
            50, 10, text=f"得分: {self.score}", fill="white", font=("Arial", 12)
        )

        # 初始化游戏元素（原有逻辑不变）
        self.init_game_elements()

        # ========== 核心修改：替换为键盘绑定 ==========
        # 绑定方向键（↑↓←→）
        self.root.bind("<Up>", lambda e: self.set_direction("UP"))
        self.root.bind("<Down>", lambda e: self.set_direction("DOWN"))
        self.root.bind("<Left>", lambda e: self.set_direction("LEFT"))
        self.root.bind("<Right>", lambda e: self.set_direction("RIGHT"))
        # 绑定空格键（开始/暂停）
        self.root.bind("<space>", self.toggle_game_state)
        # 聚焦窗口，确保键盘事件生效
        self.root.focus_set()

        # ========== 修改提示文字：匹配键盘操作 ==========
        self.start_prompt = self.canvas.create_text(
            300, 200, text="按空格键开始游戏\n方向键控制移动",
            fill="white", font=("Arial", 16)
        )

        # 显示暂停提示（初始隐藏）
        self.pause_prompt = self.canvas.create_text(
            300, 230, text="游戏已暂停 | 按空格键继续",
            fill="yellow", font=("Arial", 14)
        )
        self.canvas.itemconfig(self.pause_prompt, state="hidden")

        # 游戏循环（原有逻辑不变）
        self.game_loop()

    def init_game_elements(self):
        """初始化贪吃蛇和食物（原有逻辑不变）"""
        # 初始化蛇（3个方块，初始在左侧）
        self.snake = []
        for i in range(3):
            x = 100 - i * self.BLOCK_SIZE
            y = 200
            snake_block = self.canvas.create_rectangle(
                x, y, x + self.BLOCK_SIZE, y + self.BLOCK_SIZE,
                fill="green", outline="white"
            )
            self.snake.append(snake_block)

        # 生成初始食物
        self.food = self.create_food()

    def create_food(self):
        """随机生成食物（原有逻辑不变）"""
        while True:
            # 保证食物坐标是BLOCK_SIZE的整数倍
            x = random.randint(0, (600 - self.BLOCK_SIZE) // self.BLOCK_SIZE) * self.BLOCK_SIZE
            y = random.randint(0, (400 - self.BLOCK_SIZE) // self.BLOCK_SIZE) * self.BLOCK_SIZE

            # 检查是否与蛇身重叠
            food_overlap = False
            for block in self.snake:
                bx1, by1, bx2, by2 = self.canvas.coords(block)
                if x == bx1 and y == by1:
                    food_overlap = True
                    break
            if not food_overlap:
                break

        # 创建食物（红色方块）
        return self.canvas.create_rectangle(
            x, y, x + self.BLOCK_SIZE, y + self.BLOCK_SIZE,
            fill="red", outline="white"
        )

    # ========== 核心修改：键盘版 toggle_game_state ==========
    def toggle_game_state(self, event=None):
        """空格键切换开始/暂停"""
        if not self.game_running:
            # 未开始 → 启动游戏
            self.game_running = True
            self.game_paused = False
            self.canvas.delete(self.start_prompt)
            self.canvas.itemconfig(self.pause_prompt, state="hidden")
        else:
            # 运行中 → 切换暂停
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.canvas.itemconfig(self.pause_prompt, state="normal")
            else:
                self.canvas.itemconfig(self.pause_prompt, state="hidden")

    # ========== 键盘方向控制方法 ==========
    def set_direction(self, new_dir):
        """根据方向键设置蛇的移动方向（禁止180度反向）"""
        if not self.game_running or self.game_paused:
            return  # 游戏未开始/暂停时，不响应方向键

        # 禁止180度反向（比如向右时不能直接向左）
        if (new_dir == "UP" and self.current_dir != "DOWN") or \
           (new_dir == "DOWN" and self.current_dir != "UP") or \
           (new_dir == "LEFT" and self.current_dir != "RIGHT") or \
           (new_dir == "RIGHT" and self.current_dir != "LEFT"):
            self.next_dir = new_dir

    def move_snake(self):
        """移动蛇（原有逻辑不变）"""
        # 更新当前方向（使用缓冲方向，避免转向冲突）
        self.current_dir = self.next_dir
        dx, dy = self.DIRECTIONS[self.current_dir]

        # 获取蛇头坐标，计算新头部位置
        head_x1, head_y1, head_x2, head_y2 = self.canvas.coords(self.snake[0])
        new_head_x1 = head_x1 + dx
        new_head_y1 = head_y1 + dy
        new_head_x2 = head_x2 + dx
        new_head_y2 = head_y2 + dy

        # 边界检测（撞墙游戏结束）
        if (new_head_x1 < 0 or new_head_x2 > 600 or
                new_head_y1 < 0 or new_head_y2 > 400):
            self.game_over()
            return

        # 检测是否撞到自己
        for block in self.snake:
            bx1, by1, _, _ = self.canvas.coords(block)
            if new_head_x1 == bx1 and new_head_y1 == by1:
                self.game_over()
                return

        # 创建新蛇头
        new_head = self.canvas.create_rectangle(
            new_head_x1, new_head_y1, new_head_x2, new_head_y2,
            fill="green", outline="white"
        )
        self.snake.insert(0, new_head)

        # 检测是否吃到食物
        food_x1, food_y1, _, _ = self.canvas.coords(self.food)
        if new_head_x1 == food_x1 and new_head_y1 == food_y1:
            # 吃到食物：加分，重新生成食物（不删除蛇尾）
            self.score += 10
            self.canvas.itemconfig(self.score_text, text=f"得分: {self.score}")
            self.canvas.delete(self.food)
            self.food = self.create_food()
        else:
            # 没吃到食物：删除蛇尾（保持长度）
            tail = self.snake.pop()
            self.canvas.delete(tail)

    def game_over(self):
        """游戏结束（原有逻辑不变）"""
        self.game_running = False
        self.game_paused = False
        self.canvas.create_text(
            300, 200, text=f"游戏结束！\n最终得分: {self.score}\n按空格键重新开始",
            fill="red", font=("Arial", 20)
        )
        # 重新开始按钮（保留，也可仅用空格键）
        restart_btn = tk.Button(
            self.root, text="重新开始", command=self.restart_game,
            font=("Arial", 14), bg="green", fg="white"
        )
        restart_btn_window = self.canvas.create_window(300, 250, window=restart_btn)

    def restart_game(self):
        """重新开始游戏（原有逻辑不变，仅更新提示文字）"""
        # 清空画布
        self.canvas.delete("all")
        # 重置状态
        self.score = 0
        self.game_running = False
        self.game_paused = False
        self.current_dir = "RIGHT"
        self.next_dir = "RIGHT"

        # 重新初始化
        self.score_text = self.canvas.create_text(
            50, 10, text=f"得分: {self.score}", fill="white", font=("Arial", 12)
        )
        self.init_game_elements()

        # 显示开始提示（匹配键盘操作）
        self.start_prompt = self.canvas.create_text(
            300, 200, text="按空格键开始游戏\n方向键控制移动",
            fill="white", font=("Arial", 16)
        )

        # 重建暂停提示
        self.pause_prompt = self.canvas.create_text(
            300, 230, text="游戏已暂停 | 按空格键继续",
            fill="yellow", font=("Arial", 14)
        )
        self.canvas.itemconfig(self.pause_prompt, state="hidden")

    def game_loop(self):
        """游戏主循环（原有逻辑不变）"""
        if self.game_running and not self.game_paused:
            self.move_snake()
        # 循环调用（间隔为蛇的速度）
        self.root.after(self.SNAKE_SPEED, self.game_loop)

class Game2048Window:
    """2048游戏窗口类（键盘控制：方向键移动，空格键重置）"""

    def __init__(self, parent):
        # 游戏窗口配置（和其他游戏风格统一）
        self.root = tk.Toplevel(parent)
        self.root.title("2048 游戏")
        self.root.geometry("400x500")  # 适配得分显示+游戏面板
        self.root.resizable(False, False)
        self.root.transient(parent)

        # 游戏参数
        self.GRID_SIZE = 4  # 4x4网格
        self.CELL_SIZE = 80  # 每个格子大小
        self.CELL_PADDING = 10  # 格子间距
        self.BG_COLOR = "#bbada0"  # 面板背景色
        self.CELL_COLORS = {  # 不同数值的格子颜色（2048经典配色）
            0: "#cdc1b4",
            2: "#eee4da",
            4: "#ede0c8",
            8: "#f2b179",
            16: "#f59563",
            32: "#f67c5f",
            64: "#f65e3b",
            128: "#edcf72",
            256: "#edcc61",
            512: "#edc850",
            1024: "#edc53f",
            2048: "#edc22e",
            4096: "#3c3a32",
            8192: "#3c3a32"
        }
        self.TEXT_COLORS = {  # 文字颜色
            0: "#776e65",
            2: "#776e65",
            4: "#776e65",
            8: "#f9f6f2",
            16: "#f9f6f2",
            32: "#f9f6f2",
            64: "#f9f6f2",
            128: "#f9f6f2",
            256: "#f9f6f2",
            512: "#f9f6f2",
            1024: "#f9f6f2",
            2048: "#f9f6f2",
            4096: "#f9f6f2",
            8192: "#f9f6f2"
        }
        self.FONT = ("Arial", 24, "bold")  # 数字字体

        # 游戏状态
        self.score = 0
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.game_over = False

        # 创建主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 得分显示
        score_frame = ttk.Frame(main_frame)
        score_frame.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(score_frame, text="得分：", font=("Arial", 16)).pack(side=tk.LEFT)
        self.score_label = ttk.Label(score_frame, text=str(self.score), font=("Arial", 16, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=10)

        # 游戏面板画布
        self.canvas = tk.Canvas(
            main_frame,
            width=self.GRID_SIZE * (self.CELL_SIZE + self.CELL_PADDING) + self.CELL_PADDING,
            height=self.GRID_SIZE * (self.CELL_SIZE + self.CELL_PADDING) + self.CELL_PADDING,
            bg=self.BG_COLOR
        )
        self.canvas.pack()

        # 操作提示
        tip_label = ttk.Label(
            main_frame,
            text="方向键：移动方块 | 空格键：重置游戏",
            font=("Arial", 12)
        )
        tip_label.pack(pady=(20, 0))

        # 初始化游戏
        self.spawn_random_tile()
        self.spawn_random_tile()
        self.draw_grid()

        # 绑定键盘事件
        self.root.bind("<Up>", lambda e: self.move("up"))
        self.root.bind("<Down>", lambda e: self.move("down"))
        self.root.bind("<Left>", lambda e: self.move("left"))
        self.root.bind("<Right>", lambda e: self.move("right"))
        self.root.bind("<space>", lambda e: self.reset_game())
        # 聚焦窗口，确保键盘生效
        self.root.focus_set()

    def spawn_random_tile(self):
        """随机生成新方块（2或4，4的概率10%）"""
        # 找空位置
        empty_cells = []
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        if not empty_cells:
            return

        # 随机选位置
        row, col = random.choice(empty_cells)
        # 随机数值（90%概率2，10%概率4）
        self.grid[row][col] = 2 if random.random() < 0.9 else 4

    def draw_grid(self):
        """绘制游戏网格和方块"""
        # 清空画布
        self.canvas.delete("all")

        # 绘制每个格子
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                # 计算格子坐标
                x1 = j * (self.CELL_SIZE + self.CELL_PADDING) + self.CELL_PADDING
                y1 = i * (self.CELL_SIZE + self.CELL_PADDING) + self.CELL_PADDING
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                # 获取数值和对应颜色
                value = self.grid[i][j]
                bg_color = self.CELL_COLORS.get(value, "#3c3a32")
                text_color = self.TEXT_COLORS.get(value, "#f9f6f2")

                # 绘制格子背景
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg_color,
                    outline="",
                    width=0
                )

                # 绘制数字（0不显示）
                if value != 0:
                    # 调整小数字的字体大小
                    font = self.FONT
                    if value >= 1024:
                        font = ("Arial", 18, "bold")
                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=str(value),
                        fill=text_color,
                        font=font
                    )

        # 检查游戏结束
        if self.check_game_over() and not self.game_over:
            self.game_over = True
            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text="游戏结束！\n按空格键重置",
                fill="#f9f6f2",
                font=("Arial", 20, "bold")
            )

    def check_game_over(self):
        """检查游戏是否结束（无空位置且无法合并）"""
        # 检查是否有空位置
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                if self.grid[i][j] == 0:
                    return False

        # 检查横向是否可合并
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE - 1):
                if self.grid[i][j] == self.grid[i][j + 1]:
                    return False

        # 检查纵向是否可合并
        for j in range(self.GRID_SIZE):
            for i in range(self.GRID_SIZE - 1):
                if self.grid[i][j] == self.grid[i + 1][j]:
                    return False

        return True

    def move(self, direction):
        """处理方块移动（核心逻辑）"""
        if self.game_over:
            return

        moved = False
        original_grid = [row.copy() for row in self.grid]

        if direction == "left":
            for i in range(self.GRID_SIZE):
                # 压缩并合并行
                self.grid[i] = self.merge_row(self.grid[i])
                if self.grid[i] != original_grid[i]:
                    moved = True

        elif direction == "right":
            for i in range(self.GRID_SIZE):
                # 反转行，按左处理，再反转回来
                row = self.grid[i][::-1]
                row = self.merge_row(row)
                self.grid[i] = row[::-1]
                if self.grid[i] != original_grid[i]:
                    moved = True

        elif direction == "up":
            for j in range(self.GRID_SIZE):
                # 提取列
                col = [self.grid[i][j] for i in range(self.GRID_SIZE)]
                # 压缩并合并列
                col = self.merge_row(col)
                # 放回原网格
                for i in range(self.GRID_SIZE):
                    self.grid[i][j] = col[i]
                if [self.grid[i][j] for i in range(self.GRID_SIZE)] != [original_grid[i][j] for i in range(self.GRID_SIZE)]:
                    moved = True

        elif direction == "down":
            for j in range(self.GRID_SIZE):
                # 提取列并反转
                col = [self.grid[i][j] for i in range(self.GRID_SIZE)][::-1]
                # 压缩并合并列
                col = self.merge_row(col)
                # 反转并放回原网格
                col = col[::-1]
                for i in range(self.GRID_SIZE):
                    self.grid[i][j] = col[i]
                if [self.grid[i][j] for i in range(self.GRID_SIZE)] != [original_grid[i][j] for i in range(self.GRID_SIZE)]:
                    moved = True

        # 移动后生成新方块
        if moved:
            self.spawn_random_tile()
            # 更新得分
            self.update_score()
            # 重置游戏结束状态
            self.game_over = False

        # 重新绘制网格
        self.draw_grid()

    def merge_row(self, row):
        """压缩并合并一行/列（核心辅助方法）"""
        # 第一步：移除所有0
        new_row = [num for num in row if num != 0]
        # 第二步：合并相邻相同数字
        merged_row = []
        i = 0
        while i < len(new_row):
            if i + 1 < len(new_row) and new_row[i] == new_row[i + 1]:
                # 合并，数值翻倍
                merged_row.append(new_row[i] * 2)
                i += 2
            else:
                merged_row.append(new_row[i])
                i += 1
        # 第三步：补0到原长度
        while len(merged_row) < self.GRID_SIZE:
            merged_row.append(0)
        return merged_row

    def update_score(self):
        """更新得分（总分=所有方块数值之和）"""
        self.score = sum(sum(row) for row in self.grid)
        self.score_label.config(text=str(self.score))

    def reset_game(self):
        """重置游戏（空格键触发）"""
        # 清空网格
        self.grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        # 生成初始方块
        self.spawn_random_tile()
        self.spawn_random_tile()
        # 重置状态
        self.score = 0
        self.game_over = False
        # 更新得分和绘制
        self.score_label.config(text=str(self.score))
        self.draw_grid()

class TetrisGameWindow:
    """俄罗斯方块游戏窗口类（纯tkinter实现，无独立Pygame窗口）"""

    def __init__(self, parent):
        import time
        self.time = time  # 保存为实例属性，方便后续调用
        # 游戏窗口配置（和其他游戏风格统一）
        self.root = tk.Toplevel(parent)
        self.root.title("Tetris")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        self.root.transient(parent)
        self.root.focus_set()  # 聚焦窗口，确保键盘事件生效

        # 核心参数
        self.s_width = 800
        self.s_height = 700
        self.play_width = 300
        self.play_height = 600
        self.block_size = 30
        self.top_left_x = (self.s_width - self.play_width) // 2
        self.top_left_y = self.s_height - self.play_height

        # 游戏状态
        self.game_running = True
        self.score = 0
        self.fall_speed = 0.27  # 下落速度（秒/格）
        self.last_fall_time = self.time.time()  # 上次下落时间
        self.level_time = self.time.time()  # 等级计时

        # 俄罗斯方块形状定义
        self.S = [['.....', '.....', '..00.', '.00..', '.....'],
                  ['.....', '..0..', '..00.', '...0.', '.....']]
        self.Z = [['.....', '.....', '.00..', '..00.', '.....'],
                  ['.....', '..0..', '.00..', '.0...', '.....']]
        self.I = [['..0..', '..0..', '..0..', '..0..', '.....'],
                  ['.....', '0000.', '.....', '.....', '.....']]
        self.O = [['.....', '.....', '.00..', '.00..', '.....']]
        self.J = [['.....', '.0...', '.000.', '.....', '.....'],
                  ['.....', '..00.', '..0..', '..0..', '.....'],
                  ['.....', '.....', '.000.', '...0.', '.....'],
                  ['.....', '..0..', '..0..', '.00..', '.....']]
        self.L = [['.....', '...0.', '.000.', '.....', '.....'],
                  ['.....', '..0..', '..0..', '..00.', '.....'],
                  ['.....', '.....', '.000.', '.0...', '.....'],
                  ['.....', '.00..', '..0..', '..0..', '.....']]
        self.T = [['.....', '..0..', '.000.', '.....', '.....'],
                  ['.....', '..0..', '..00.', '..0..', '.....'],
                  ['.....', '.....', '.000.', '..0..', '.....'],
                  ['.....', '..0..', '.00..', '..0..', '.....']]

        self.shapes = [self.S, self.Z, self.I, self.O, self.J, self.L, self.T]
        self.shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                             (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

        # 创建tkinter画布（替代Pygame窗口）
        self.canvas = tk.Canvas(self.root, width=self.s_width, height=self.s_height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 初始化游戏数据
        self.locked_positions = {}  # 已固定的方块位置 (x,y): (r,g,b)
        self.grid = self.create_grid()
        self.current_piece = self.get_shape()
        self.next_piece = self.get_shape()

        # 绑定键盘事件
        self.root.bind("<Left>", lambda e: self.move_piece(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_piece(1, 0))
        self.root.bind("<Up>", lambda e: self.rotate_piece())
        self.root.bind("<Down>", lambda e: self.move_piece(0, 1))
        self.root.bind("<space>", lambda e: self.hard_drop())  # 空格键直接落底
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 启动游戏循环
        self.game_loop()

    class Piece:
        """俄罗斯方块方块类（内部类）"""

        def __init__(self, column, row, shape, color):
            self.x = column
            self.y = row
            self.shape = shape
            self.color = color
            self.rotation = 0

    def rgb_to_hex(self, rgb):
        """将RGB颜色转换为tkinter可用的十六进制格式"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def create_grid(self):
        """创建游戏网格"""
        grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in self.locked_positions:
                    grid[i][j] = self.locked_positions[(j, i)]
        return grid

    def convert_shape_format(self, shape):
        """转换方块格式为坐标"""
        positions = []
        format = shape.shape[shape.rotation % len(shape.shape)]
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((shape.x + j, shape.y + i))
        # 调整坐标偏移
        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)
        return positions

    def valid_space(self, shape):
        """检测位置是否合法"""
        for (x, y) in self.convert_shape_format(shape):
            # 检测边界
            if x < 0 or x >= 10 or y >= 20:
                return False
            # 检测已固定方块（y<0时是顶部外的位置，允许）
            if y >= 0 and (x, y) in self.locked_positions:
                return False
        return True

    def check_lost(self):
        """检测游戏是否结束"""
        for (x, y) in self.locked_positions:
            if y < 1:
                return True
        return False

    def get_shape(self):
        """随机生成新方块"""
        import random
        shape = random.choice(self.shapes)
        color = self.shape_colors[self.shapes.index(shape)]
        return self.Piece(5, 0, shape, color)

    def clear_rows(self):
        """清除满行并返回清除的行数"""
        inc = 0
        for i in range(len(self.grid) - 1, -1, -1):
            row = self.grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                # 删除当前行的所有固定方块
                for j in range(len(row)):
                    if (j, i) in self.locked_positions:
                        del self.locked_positions[(j, i)]
                # 将上方的方块下落
                for key in sorted(list(self.locked_positions), key=lambda x: x[1])[::-1]:
                    x, y = key
                    if y < i:
                        new_key = (x, y + 1)
                        self.locked_positions[new_key] = self.locked_positions.pop(key)
        # 重新创建网格
        self.grid = self.create_grid()
        return inc

    def move_piece(self, dx, dy):
        """移动方块"""
        if not self.game_running:
            return
        # 临时移动
        self.current_piece.x += dx
        self.current_piece.y += dy
        # 检测是否合法
        if not self.valid_space(self.current_piece):
            # 不合法则回退
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            # 如果是向下移动不合法，说明落地了
            if dy > 0:
                self.lock_piece()

    def rotate_piece(self):
        """旋转方块"""
        if not self.game_running:
            return
        # 临时旋转
        self.current_piece.rotation += 1
        # 检测是否合法
        if not self.valid_space(self.current_piece):
            # 不合法则回退
            self.current_piece.rotation -= 1

    def hard_drop(self):
        """空格键直接落底"""
        if not self.game_running:
            return
        while self.valid_space(self.current_piece):
            self.current_piece.y += 1
        self.current_piece.y -= 1
        self.lock_piece()

    def lock_piece(self):
        """锁定方块到网格"""
        shape_pos = self.convert_shape_format(self.current_piece)
        for (x, y) in shape_pos:
            if y >= 0:
                self.locked_positions[(x, y)] = self.current_piece.color
        # 生成新方块
        self.current_piece = self.next_piece
        self.next_piece = self.get_shape()
        # 清除满行并加分
        rows_cleared = self.clear_rows()
        self.score += rows_cleared * 10
        # 检测游戏结束
        if self.check_lost():
            self.game_running = False
            self.draw_game_over()

    def draw_grid(self):
        """绘制游戏网格和方块"""
        # 清空画布
        self.canvas.delete("all")

        # 绘制标题
        self.canvas.create_text(self.top_left_x + self.play_width / 2, 30,
                                text="TETRIS", fill="white", font=("comicsans", 60, "bold"))

        # 绘制得分
        self.canvas.create_text(self.top_left_x + self.play_width + 100, 200,
                                text=f"Score: {self.score}", fill="white", font=("comicsans", 30))

        # 游戏区域基准位置
        game_area_x = self.top_left_x
        game_area_y = self.top_left_y

        # 绘制游戏区域背景
        self.canvas.create_rectangle(game_area_x, game_area_y,
                                     game_area_x + self.play_width,
                                     game_area_y + self.play_height,
                                     outline="red", width=5)

        # 绘制网格线
        # 横向线
        for i in range(21):
            y = game_area_y + i * self.block_size
            self.canvas.create_line(game_area_x, y,
                                    game_area_x + self.play_width, y,
                                    fill="gray")
        # 纵向线
        for j in range(11):
            x = game_area_x + j * self.block_size
            self.canvas.create_line(x, game_area_y,
                                    x, game_area_y + self.play_height,
                                    fill="gray")

        # 绘制已固定的方块
        for (x, y), color in self.locked_positions.items():
            self.canvas.create_rectangle(
                game_area_x + x * self.block_size,
                game_area_y + y * self.block_size,
                game_area_x + (x + 1) * self.block_size,
                game_area_y + (y + 1) * self.block_size,
                fill=self.rgb_to_hex(color), outline="black"
            )

        # 绘制当前方块
        if self.game_running:
            shape_pos = self.convert_shape_format(self.current_piece)
            for (x, y) in shape_pos:
                if y >= 0:
                    self.canvas.create_rectangle(
                        game_area_x + x * self.block_size,
                        game_area_y + y * self.block_size,
                        game_area_x + (x + 1) * self.block_size,
                        game_area_y + (y + 1) * self.block_size,
                        fill=self.rgb_to_hex(self.current_piece.color), outline="black"
                    )

        # ========== 调整后的下一个方块区域配置 ==========
        # 下一个方块的基准位置（向下300，向右20）
        next_base_x = game_area_x + self.play_width + 80  - 40 # 原80 + 左移20
        next_base_y = 140 + 600  # 原140 + 下移300

        # 绘制"Next Shape"标题（向下400）
        self.canvas.create_text(next_base_x + 20 + self.block_size * 1.5, 110 + 450,
                                text="Next Shape", fill="white", font=("comicsans", 30))



        # 绘制下一个方块（居中显示）
        next_shape_pos = self.convert_shape_format(self.next_piece)
        offset_x, offset_y = self.get_next_shape_offset(self.next_piece)

        for (x, y) in next_shape_pos:
            draw_x = next_base_x + (x + offset_x) * self.block_size
            draw_y = next_base_y + (y + offset_y) * self.block_size
            self.canvas.create_rectangle(
                draw_x, draw_y,
                draw_x + self.block_size,
                draw_y + self.block_size,
                fill=self.rgb_to_hex(self.next_piece.color), outline="black"
            )

    def get_next_shape_offset(self, shape):
        """计算下一个方块的居中偏移量"""
        # 获取方块的形状矩阵
        format = shape.shape[shape.rotation % len(shape.shape)]
        # 找出方块的有效范围（去除空的行列）
        min_x, max_x = 4, 0
        min_y, max_y = 4, 0

        for y, line in enumerate(format):
            for x, cell in enumerate(line):
                if cell == '0':
                    if x < min_x:
                        min_x = x
                    if x > max_x:
                        max_x = x
                    if y < min_y:
                        min_y = y
                    if y > max_y:
                        max_y = y

        # 计算方块的宽度和高度
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # 计算居中偏移（基于5x5的形状矩阵，居中到3x3的显示区域）
        offset_x = (3 - width) // 2 - min_x
        offset_y = (3 - height) // 2 - min_y

        return offset_x, offset_y

    def draw_game_over(self):
        """绘制游戏结束画面"""
        self.canvas.create_text(self.top_left_x + self.play_width / 2,
                                self.top_left_y + self.play_height / 2,
                                text="You Lost", fill="white", font=("comicsans", 40, "bold"))
        # 添加重新开始按钮
        restart_btn = tk.Button(
            self.root, text="重新开始", command=self.restart_game,
            font=("Arial", 14), bg="green", fg="white"
        )
        self.canvas.create_window(self.top_left_x + self.play_width / 2,
                                  self.top_left_y + self.play_height / 2 + 50,
                                  window=restart_btn)

    def restart_game(self):
        """重新开始游戏"""
        self.locked_positions = {}
        self.score = 0
        self.fall_speed = 0.27
        self.last_fall_time = self.time.time()
        self.level_time = self.time.time()
        self.current_piece = self.get_shape()
        self.next_piece = self.get_shape()
        self.game_running = True
        self.game_loop()

    def game_loop(self):
        """游戏主循环（tkinter版）"""
        if not self.game_running:
            return

        # 处理自动下落
        current_time = self.time.time()
        # 检查是否到下落时间
        if current_time - self.last_fall_time >= self.fall_speed:
            self.move_piece(0, 1)
            self.last_fall_time = current_time

        # 处理等级提升（加速）
        if current_time - self.level_time >= 4:
            self.level_time = current_time
            if self.fall_speed > 0.15:
                self.fall_speed -= 0.005

        # 绘制画面
        self.draw_grid()

        # 继续循环（约60帧/秒）
        if self.game_running:
            self.root.after(16, self.game_loop)

    def on_close(self):
        """关闭窗口"""
        self.game_running = False
        self.root.destroy()