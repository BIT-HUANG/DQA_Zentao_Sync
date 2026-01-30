import tkinter as tk
import random

class GameSnakeWindow:
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
