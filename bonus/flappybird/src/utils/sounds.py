import sys
import os

import pygame

# 与images.py保持一致的路径计算逻辑，确保assets路径统一
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # utils目录
FLAPPYBIRD_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "../../"))  # flappybird根目录
ASSETS_ROOT = os.path.join(FLAPPYBIRD_ROOT, "assets")  # assets绝对路径


class Sounds:
    die: pygame.mixer.Sound
    hit: pygame.mixer.Sound
    point: pygame.mixer.Sound
    swoosh: pygame.mixer.Sound
    wing: pygame.mixer.Sound

    def __init__(self) -> None:
        # 根据系统自动选择音频后缀（win=wav，其他=ogg）
        ext = "wav" if "win" in sys.platform else "ogg"

        # 拼接绝对路径加载所有音频资源
        self.die = pygame.mixer.Sound(os.path.join(ASSETS_ROOT, f"audio/die.{ext}"))
        self.hit = pygame.mixer.Sound(os.path.join(ASSETS_ROOT, f"audio/hit.{ext}"))
        self.point = pygame.mixer.Sound(os.path.join(ASSETS_ROOT, f"audio/point.{ext}"))
        self.swoosh = pygame.mixer.Sound(os.path.join(ASSETS_ROOT, f"audio/swoosh.{ext}"))
        self.wing = pygame.mixer.Sound(os.path.join(ASSETS_ROOT, f"audio/wing.{ext}"))