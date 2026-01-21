"""
@file __init__.py
@brief 谷歌业务后端模块
@details 包含谷歌账号自动化的核心业务逻辑

注意: 部分模块仍在src/目录下，迁移进行中
已迁移: account_manager, sheerid_verifier
待迁移: playwright_google, auto_bind_card
"""

from .sheerid_verifier import SheerIDVerifier
from .account_manager import AccountManager

# 待迁移的模块 - 目前从旧位置导入
try:
    import sys
    import os
    _src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if _src_dir not in sys.path:
        sys.path.insert(0, _src_dir)
    
    from run_playwright_google import process_browser, check_google_one_status
    from auto_bind_card import auto_bind_card, check_and_login
except ImportError as e:
    print(f"[google.backend] 部分模块导入失败: {e}")
    process_browser = check_google_one_status = None
    auto_bind_card = check_and_login = None

__all__ = [
    'SheerIDVerifier',
    'AccountManager',
    'process_browser', 
    'check_google_one_status',
    'auto_bind_card',
    'check_and_login',
]
