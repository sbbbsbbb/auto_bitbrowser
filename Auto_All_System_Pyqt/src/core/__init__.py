"""
@file __init__.py
@brief 核心模块包
@details 包含数据库管理、比特浏览器API、Playwright封装等公共模块
"""

# 延迟导入以避免循环依赖
from .config import Config
from .database import DBManager

# 可选导入（需要playwright等依赖）
try:
    from .bit_api import openBrowser, closeBrowser, get_api, createBrowser, deleteBrowser
    from .bit_playwright import google_login
except ImportError as e:
    print(f"[core] 部分模块导入失败: {e}")
    openBrowser = closeBrowser = get_api = createBrowser = deleteBrowser = None
    google_login = None

# 导入比特浏览器API类
from .bitbrowser_api import (
    BitBrowserAPI, 
    BitBrowserManager, 
    BitBrowserAPIError,
    ProxyType,
    ProxyMethod,
    IPCheckService
)

__all__ = [
    'Config',
    'DBManager', 
    'openBrowser', 
    'closeBrowser', 
    'get_api',
    'createBrowser',
    'deleteBrowser',
    'google_login',
    'BitBrowserAPI',
    'BitBrowserManager',
    'BitBrowserAPIError',
    'ProxyType',
    'ProxyMethod',
    'IPCheckService',
]
