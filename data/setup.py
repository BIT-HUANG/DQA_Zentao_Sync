__author__ = 'justinarmstrong'

"""
This module initializes the display and creates dictionaries of resources.
"""

import os
import pygame as pg
from . import tools
from . import constants as c

# 仅保留顶级常量/导入（无任何执行代码，导入时不触发任何操作）
ORIGINAL_CAPTION = c.ORIGINAL_CAPTION
# 新增：定义全局变量，存储资源和窗口对象（供其他模块调用）
SCREEN = None
SCREEN_RECT = None
FONTS = None
MUSIC = None
GFX = None
SFX = None

def init_game():
    """游戏核心初始化函数 → 封装所有Pygame初始化、窗口创建、资源加载逻辑"""
    global SCREEN, SCREEN_RECT, FONTS, MUSIC, GFX, SFX  # 声明使用全局变量
    # 原所有顶级执行代码，全部移入此函数内
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
    pg.display.set_caption(c.ORIGINAL_CAPTION)
    SCREEN = pg.display.set_mode(c.SCREEN_SIZE)
    SCREEN_RECT = SCREEN.get_rect()
    # 资源加载（字体、音乐、图像、音效）
    FONTS = tools.load_all_fonts(os.path.join("resources","fonts"))
    MUSIC = tools.load_all_music(os.path.join("resources","music"))
    GFX   = tools.load_all_gfx(os.path.join("resources","graphics"))
    SFX   = tools.load_all_sfx(os.path.join("resources","sound"))