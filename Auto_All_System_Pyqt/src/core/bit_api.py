"""
@file bit_api.py
@brief 比特浏览器API简化接口
@details 提供简化的浏览器操作函数接口
"""
import requests
import json
import time
from .bitbrowser_api import BitBrowserAPI

# 官方文档地址
# https://doc2.bitbrowser.cn/jiekou/ben-di-fu-wu-zhi-nan.html

url = "http://127.0.0.1:54345"
headers = {'Content-Type': 'application/json'}

# 初始化新API实例（全局单例）
_api_instance = None


def get_api() -> BitBrowserAPI:
    """
    @brief 获取API实例（单例模式）
    @return BitBrowserAPI实例
    """
    global _api_instance
    if _api_instance is None:
        _api_instance = BitBrowserAPI()
    return _api_instance


def createBrowser() -> str:
    """
    @brief 创建浏览器窗口
    @return 创建的浏览器ID
    @throws Exception 创建失败时抛出
    """
    print("正在创建窗口...")
    api = get_api()
    result = api.create_browser(
        name='google',
        browser_fingerprint={'coreVersion': '130'},
        remark=''
    )
    
    if result['success']:
        browserId = result['data']['id']
        print(f"窗口创建成功，ID: {browserId}")
        return browserId
    else:
        raise Exception(f"创建窗口失败: {result}")


def updateBrowser():
    """
    @brief 更新浏览器窗口（示例）
    """
    api = get_api()
    result = api.update_browser_partial(
        ['93672cf112a044f08b653cab691216f0'],
        {'remark': '我是一个备注'}
    )
    print(result)


def openBrowser(id: str) -> dict:
    """
    @brief 打开浏览器窗口
    @param id 浏览器ID
    @return 打开结果，包含ws连接地址
    """
    print(f"正在打开窗口 {id}...")
    api = get_api()
    result = api.open_browser(id, queue=True)
    print(f"窗口打开响应: {result}")
    return result


def closeBrowser(id: str):
    """
    @brief 关闭浏览器窗口
    @param id 浏览器ID
    """
    print(f"正在关闭窗口 {id}...")
    api = get_api()
    result = api.close_browser(id)
    print(f"窗口关闭响应: {result}")


def deleteBrowser(id: str):
    """
    @brief 删除浏览器窗口
    @param id 浏览器ID
    """
    print(f"正在删除窗口 {id}...")
    api = get_api()
    result = api.delete_browser(id)
    print(f"窗口删除响应: {result}")


if __name__ == '__main__':
    try:
        browser_id = createBrowser()
        openBrowser(browser_id)

        print("\n等待10秒后自动关闭窗口...")
        time.sleep(10)

        closeBrowser(browser_id)

        print("\n等待10秒后自动删除窗口...")
        time.sleep(10)

        deleteBrowser(browser_id)
        print("\n程序执行完成！")
    except requests.exceptions.Timeout:
        print("\n[错误] 请求超时，请检查比特浏览器服务是否正常运行")
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接到比特浏览器API服务，请确保比特浏览器正在运行")
    except Exception as e:
        print(f"\n[错误] 发生异常: {e}")
        import traceback
        traceback.print_exc()
