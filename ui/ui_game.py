import tkinter as tk
from tkinter import ttk
import random


class GameUI:
    def __init__(self, parent):
        self.parent = parent
        self.about_dialog = None  # 原弹窗引用
        self.game_window = None  # 游戏窗口引用

    def create_game_select_dialog(self):
        """创建关于弹窗（保持原有逻辑不变）"""
        # 创建弹窗
        self.about_dialog = tk.Toplevel(self.parent)
        self.about_dialog.title("其他")
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

        # 修改Breakout按钮的绑定函数
        ttk.Button(content_frame, text="2048", command=self.open_2048_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="Breakout", command=self.open_breakout_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="Snake", command=self.open_snake_game).pack(padx=5, pady=5)
        ttk.Button(content_frame, text="关闭", command=self.on_close_game_select).pack(padx=5, pady=5)

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

    # ========== 新增：键盘方向控制方法 ==========
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