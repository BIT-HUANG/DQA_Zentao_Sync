__author__ = 'justinarmstrong'

"""
This module initializes the display and creates dictionaries of resources.
"""

import os,sys
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


    # ========== 新增：PyInstaller 路径适配（关键） ==========
    # 当 exe 运行时，_MEIPASS 是 PyInstaller 自动创建的临时目录（存放嵌入的资源）
    # 1. 优先判断是否是PyInstaller打包后的环境（exe运行）
    if hasattr(sys, '_MEIPASS'):
        # 打包后：resources/data 直接在exe解压的临时目录（sys._MEIPASS）根目录
        base_path = sys._MEIPASS
        resources_path = os.path.normpath(os.path.join(base_path, "resources"))
        data_path = os.path.normpath(os.path.join(base_path, "data"))
    else:
        # 开发环境：从当前setup.py所在的data目录 → 上级（bonus/mario）→ resources目录
        current_script_dir = os.path.dirname(os.path.abspath(__file__))  # data目录（bonus/mario/data）
        # 拼接resources路径：data目录向上一级（bonus/mario）→ resources文件夹
        resources_relative_path = os.path.join(current_script_dir, "../resources")
        resources_path = os.path.normpath(resources_relative_path)
        # 开发环境的data路径：直接用当前脚本所在的data目录（bonus/mario/data）
        data_path = current_script_dir


    # 原所有顶级执行代码，全部移入此函数内
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pg.init()
    pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
    pg.display.set_caption(c.ORIGINAL_CAPTION)
    SCREEN = pg.display.set_mode(c.SCREEN_SIZE)
    SCREEN_RECT = SCREEN.get_rect()
    # 资源加载（字体、音乐、图像、音效）
    FONTS = tools.load_all_fonts(os.path.join(resources_path, "fonts"))
    MUSIC = tools.load_all_music(os.path.join(resources_path, "music"))
    GFX   = tools.load_all_gfx(os.path.join(resources_path, "graphics"))
    SFX   = tools.load_all_sfx(os.path.join(resources_path, "sound"))