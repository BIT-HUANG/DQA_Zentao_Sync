import random
import os
from typing import List, Tuple

import pygame

from .constants import BACKGROUNDS, PIPES, PLAYERS

# 核心：根据当前脚本位置，自动计算assets绝对路径（适配实际目录结构，无需手动改路径）
# 层级：images.py → utils → src → flappybird → 拼接assets
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # utils目录
FLAPPYBIRD_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))  # flappybird根目录
ASSETS_ROOT = os.path.join(FLAPPYBIRD_ROOT, "assets")  # 最终assets绝对路径


class Images:
    numbers: List[pygame.Surface]
    game_over: pygame.Surface
    welcome_message: pygame.Surface
    base: pygame.Surface
    background: pygame.Surface
    player: Tuple[pygame.Surface]
    pipe: Tuple[pygame.Surface]

    def __init__(self) -> None:
        # 加载数字图片（0.png ~ 9.png）
        self.numbers = list(
            pygame.image.load(os.path.join(ASSETS_ROOT, f"sprites/{num}.png")).convert_alpha()
            for num in range(10)
        )

        # 加载游戏结束、欢迎界面、地面图片
        self.game_over = pygame.image.load(
            os.path.join(ASSETS_ROOT, "sprites/gameover.png")
        ).convert_alpha()
        self.welcome_message = pygame.image.load(
            os.path.join(ASSETS_ROOT, "sprites/message.png")
        ).convert_alpha()
        self.base = pygame.image.load(
            os.path.join(ASSETS_ROOT, "sprites/base.png")
        ).convert_alpha()

        self.randomize()

    def randomize(self):
        # 随机选择背景、小鸟、管道资源
        rand_bg = random.randint(0, len(BACKGROUNDS) - 1)
        rand_player = random.randint(0, len(PLAYERS) - 1)
        rand_pipe = random.randint(0, len(PIPES) - 1)

        # 拼接绝对路径加载资源（剔除constants中多余的assets/前缀）
        bg_path = BACKGROUNDS[rand_bg].replace("assets/", "")
        self.background = pygame.image.load(os.path.join(ASSETS_ROOT, bg_path)).convert()

        player_paths = [p.replace("assets/", "") for p in PLAYERS[rand_player]]
        self.player = (
            pygame.image.load(os.path.join(ASSETS_ROOT, player_paths[0])).convert_alpha(),
            pygame.image.load(os.path.join(ASSETS_ROOT, player_paths[1])).convert_alpha(),
            pygame.image.load(os.path.join(ASSETS_ROOT, player_paths[2])).convert_alpha(),
        )

        pipe_path = PIPES[rand_pipe].replace("assets/", "")
        self.pipe = (
            pygame.transform.flip(
                pygame.image.load(os.path.join(ASSETS_ROOT, pipe_path)).convert_alpha(),
                False,
                True,
            ),
            pygame.image.load(os.path.join(ASSETS_ROOT, pipe_path)).convert_alpha(),
        )