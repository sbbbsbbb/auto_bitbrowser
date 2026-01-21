"""
@file bitbrowser_api.py
@brief 比特浏览器API封装模块
@details 提供比特浏览器的完整API接口封装，支持从Django应用导入或使用内置实现
"""
import sys
import os
import requests
from enum import Enum
from typing import Optional, List, Dict, Any

# 获取项目路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.dirname(_current_dir)
_pyqt_dir = os.path.dirname(_src_dir)
_project_root = os.path.dirname(_pyqt_dir)
_backend_dir = os.path.join(_project_root, 'Auto_All_System_Web', 'backend')

# 添加 Django 项目路径
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# 尝试从 Django 应用中导入
_django_import_success = False
try:
    from apps.integrations.bitbrowser.api import (
        BitBrowserAPI as _DjangoBitBrowserAPI,
        BitBrowserManager as _DjangoBitBrowserManager,
        BitBrowserAPIError as _DjangoBitBrowserAPIError,
        ProxyType as _DjangoProxyType,
        ProxyMethod as _DjangoProxyMethod,
        IPCheckService as _DjangoIPCheckService
    )
    _django_import_success = True
except ImportError:
    pass


class ProxyType(str, Enum):
    """
    @enum ProxyType
    @brief 代理类型枚举
    """
    NO_PROXY = "noproxy"
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class ProxyMethod(int, Enum):
    """
    @enum ProxyMethod
    @brief 代理获取方式枚举
    """
    CUSTOM = 2
    EXTRACT_IP = 3


class IPCheckService(str, Enum):
    """
    @enum IPCheckService
    @brief IP检测服务枚举
    """
    IP123IN = "ip123in"
    IP_API = "ip-api"


class BitBrowserAPIError(Exception):
    """
    @class BitBrowserAPIError
    @brief 比特浏览器API异常类
    """
    pass


class BitBrowserAPI:
    """
    @class BitBrowserAPI
    @brief 比特浏览器API封装类
    @details 封装比特浏览器本地服务的HTTP API接口
    """
    
    def __init__(self, api_url: str = None, timeout: int = 30):
        """
        @brief 初始化API客户端
        @param api_url API服务地址，默认为本地服务
        @param timeout 请求超时时间（秒）
        """
        self.api_url = (api_url or "http://127.0.0.1:54345").rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _request(self, endpoint: str, data: dict = None) -> dict:
        """
        @brief 发送API请求
        @param endpoint API端点
        @param data 请求数据
        @return 响应数据
        @throws BitBrowserAPIError 请求失败时抛出
        """
        url = f"{self.api_url}/{endpoint}"
        try:
            response = self.session.post(url, json=data or {}, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            if not result.get('success', False):
                raise BitBrowserAPIError(f"API错误: {result.get('msg', '未知错误')}")
            return result
        except requests.RequestException as e:
            raise BitBrowserAPIError(f"请求失败: {e}")
    
    def health_check(self) -> bool:
        """
        @brief 健康检查
        @return 服务是否可用
        """
        try:
            return self._request('health').get('success', False)
        except:
            return False
    
    def list_browsers(self, page: int = 0, page_size: int = 50, **kwargs) -> dict:
        """
        @brief 获取浏览器列表
        @param page 页码
        @param page_size 每页数量
        @return 浏览器列表响应
        """
        data = {'page': page, 'pageSize': min(page_size, 100)}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        return self._request('browser/list', data)
    
    def get_browser_list(self, page: int = 0, page_size: int = 100) -> list:
        """
        @brief 获取浏览器列表（简化版）
        @param page 页码
        @param page_size 每页数量
        @return 浏览器列表
        """
        result = self.list_browsers(page=page, page_size=page_size)
        data = result.get('data', {})
        return data if isinstance(data, list) else data.get('list', [])
    
    def create_browser(self, name: str, browser_fingerprint: dict = None, **kwargs) -> dict:
        """
        @brief 创建浏览器窗口
        @param name 窗口名称
        @param browser_fingerprint 浏览器指纹配置
        @return 创建结果
        """
        data = {'name': name, 'browserFingerPrint': browser_fingerprint or {}, **kwargs}
        return self._request('browser/update', data)
    
    def update_browser_partial(self, browser_ids: list, update_fields: dict) -> dict:
        """
        @brief 批量部分更新浏览器
        @param browser_ids 浏览器ID列表
        @param update_fields 更新字段
        @return 更新结果
        """
        return self._request('browser/update/partial', {'ids': browser_ids, **update_fields})
    
    def open_browser(self, browser_id: str, queue: bool = True, **kwargs) -> dict:
        """
        @brief 打开浏览器窗口
        @param browser_id 浏览器ID
        @param queue 是否排队
        @return 打开结果，包含ws连接地址
        """
        data = {'id': browser_id, 'queue': queue, **kwargs}
        return self._request('browser/open', data)
    
    def close_browser(self, browser_id: str) -> dict:
        """
        @brief 关闭浏览器窗口
        @param browser_id 浏览器ID
        @return 关闭结果
        """
        return self._request('browser/close', {'id': browser_id})
    
    def delete_browser(self, browser_id: str) -> dict:
        """
        @brief 删除浏览器窗口
        @param browser_id 浏览器ID
        @return 删除结果
        """
        return self._request('browser/delete', {'id': browser_id})
    
    def get_browser_detail(self, browser_id: str) -> dict:
        """
        @brief 获取浏览器详情
        @param browser_id 浏览器ID
        @return 浏览器详情
        """
        return self._request('browser/detail', {'id': browser_id})


class BitBrowserManager:
    """
    @class BitBrowserManager
    @brief 比特浏览器管理器
    @details 提供更高层次的浏览器管理接口
    """
    
    def __init__(self, api_url: str = None):
        """
        @brief 初始化管理器
        @param api_url API服务地址
        """
        self.api = BitBrowserAPI(api_url)
    
    def open_and_get_ws(self, browser_id: str) -> str:
        """
        @brief 打开浏览器并获取WebSocket地址
        @param browser_id 浏览器ID
        @return WebSocket连接地址
        """
        result = self.api.open_browser(browser_id)
        return result.get('data', {}).get('ws')
    
    def launch_browser(self, profile_id: str) -> dict:
        """
        @brief 启动浏览器
        @param profile_id 配置文件ID
        @return 启动结果
        """
        result = self.api.open_browser(profile_id)
        data = result.get('data', {})
        return {
            'profile_id': profile_id,
            'ws_endpoint': data.get('ws'),
            'http_endpoint': data.get('http'),
            'pid': data.get('pid'),
        }
    
    def cleanup(self, profile_id: str, delete_profile: bool = False):
        """
        @brief 清理浏览器
        @param profile_id 配置文件ID
        @param delete_profile 是否删除配置
        """
        self.api.close_browser(profile_id)
        if delete_profile:
            self.api.delete_browser(profile_id)
    
    def get_all_browsers(self) -> list:
        """
        @brief 获取所有浏览器
        @return 浏览器列表
        """
        all_browsers = []
        page = 0
        while True:
            browsers = self.api.get_browser_list(page=page, page_size=100)
            if not browsers:
                break
            all_browsers.extend(browsers)
            if len(browsers) < 100:
                break
            page += 1
        return all_browsers


# 如果Django导入成功，使用Django版本
if _django_import_success:
    BitBrowserAPI = _DjangoBitBrowserAPI
    BitBrowserManager = _DjangoBitBrowserManager
    BitBrowserAPIError = _DjangoBitBrowserAPIError
    ProxyType = _DjangoProxyType
    ProxyMethod = _DjangoProxyMethod
    IPCheckService = _DjangoIPCheckService


__all__ = [
    'BitBrowserAPI',
    'BitBrowserManager',
    'BitBrowserAPIError',
    'ProxyType',
    'ProxyMethod',
    'IPCheckService',
]
