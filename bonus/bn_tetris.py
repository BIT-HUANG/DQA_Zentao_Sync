import tkinter as tk


class GameTetrisWindow:
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