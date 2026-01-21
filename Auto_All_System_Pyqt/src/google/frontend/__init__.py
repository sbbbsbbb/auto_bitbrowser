"""
@file __init__.py
@brief 谷歌业务前端模块
@details 包含谷歌账号自动化的PyQt6 GUI界面

注意: GUI模块仍在src/目录下，迁移进行中
"""

import sys
import os

# 添加src目录到路径
_src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# 从旧位置导入GUI模块
try:
    from create_window_gui import BrowserWindowCreatorGUI
    from sheerid_gui import SheerIDWindow
    from bind_card_gui import BindCardWindow
    from auto_all_in_one_gui import AutoAllInOneWindow
except ImportError as e:
    print(f"[google.frontend] GUI模块导入失败: {e}")
    BrowserWindowCreatorGUI = None
    SheerIDWindow = None
    BindCardWindow = None
    AutoAllInOneWindow = None

__all__ = [
    'BrowserWindowCreatorGUI',
    'SheerIDWindow', 
    'BindCardWindow',
    'AutoAllInOneWindow'
]
