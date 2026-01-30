import tkinter as tk


class GameBreakoutWindow:
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