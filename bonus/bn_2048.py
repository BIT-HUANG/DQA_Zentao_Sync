import tkinter as tk
from tkinter import ttk
import random

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