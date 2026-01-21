"""
@file worker_thread.py
@brief 后台工作线程模块
@details 提供QThread工作线程，避免阻塞主界面
"""

import time
from typing import Dict, List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtCore import QThread, pyqtSignal


class WorkerThread(QThread):
    """
    @class WorkerThread
    @brief 通用后台工作线程
    @details 用于执行耗时任务，避免阻塞主界面
    """
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int, int)  # current, total
    
    def __init__(self, task_type: str, **kwargs):
        """
        @brief 初始化工作线程
        @param task_type 任务类型: 'sheerlink', 'create', 'delete', 'open', '2fa'
        @param kwargs 任务参数
        """
        super().__init__()
        self.task_type = task_type
        self.kwargs = kwargs
        self.is_running = True
    
    def stop(self):
        """停止任务"""
        self.is_running = False
    
    def log(self, message: str):
        """发送日志信号"""
        self.log_signal.emit(message)
    
    def msleep_safe(self, ms: int):
        """可中断的sleep"""
        t = ms
        while t > 0 and self.is_running:
            time.sleep(0.1)
            t -= 100
    
    def run(self):
        """执行任务"""
        try:
            if self.task_type == 'sheerlink':
                self.run_sheerlink()
            elif self.task_type == 'create':
                self.run_create()
            elif self.task_type == 'delete':
                self.run_delete()
            elif self.task_type == 'open':
                self.run_open()
            elif self.task_type == '2fa':
                self.run_2fa()
        except Exception as e:
            self.log(f"❌ 任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            self.finished_signal.emit({'type': self.task_type, 'error': str(e)})
    
    def run_sheerlink(self):
        """执行SheerLink提取任务 (多线程)"""
        ids_to_process = self.kwargs.get('ids', [])
        thread_count = self.kwargs.get('thread_count', 1)
        
        if not ids_to_process:
            self.finished_signal.emit({'type': 'sheerlink', 'count': 0})
            return
        
        self.log(f"\n[开始] 提取 SheerID Link，共 {len(ids_to_process)} 个窗口，并发: {thread_count}")
        
        # 统计计数
        stats = {
            'link_unverified': 0,
            'link_verified': 0,
            'subscribed': 0,
            'ineligible': 0,
            'timeout': 0,
            'error': 0
        }
        
        success_count = 0
        
        # 导入处理函数
        try:
            from google.backend.sheerlink_service import process_browser
        except ImportError as e:
            self.log(f"❌ 导入失败: {e}")
            self.finished_signal.emit({'type': 'sheerlink', 'count': 0, 'error': str(e)})
            return
        
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            future_to_id = {}
            for bid in ids_to_process:
                if not self.is_running:
                    break
                # 回调函数
                callback = lambda msg, b=bid: self.log_signal.emit(f"[{b[:8]}...] {msg}")
                future = executor.submit(process_browser, bid, log_callback=callback)
                future_to_id[future] = bid
            
            finished_tasks = 0
            for future in as_completed(future_to_id):
                if not self.is_running:
                    self.log('[用户操作] 任务已停止')
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                bid = future_to_id[future]
                finished_tasks += 1
                self.progress_signal.emit(finished_tasks, len(ids_to_process))
                
                try:
                    success, msg = future.result()
                    if success:
                        self.log(f"✅ ({finished_tasks}/{len(ids_to_process)}) {bid[:12]}...: {msg}")
                        success_count += 1
                    else:
                        self.log(f"❌ ({finished_tasks}/{len(ids_to_process)}) {bid[:12]}...: {msg}")
                    
                    # 统计分类
                    if "Verified" in msg or "Get Offer" in msg:
                        stats['link_verified'] += 1
                    elif "Link Found" in msg or "提取成功" in msg:
                        stats['link_unverified'] += 1
                    elif "Subscribed" in msg or "已绑卡" in msg:
                        stats['subscribed'] += 1
                    elif "无资格" in msg or "Not Available" in msg:
                        stats['ineligible'] += 1
                    elif "超时" in msg or "Timeout" in msg:
                        stats['timeout'] += 1
                    else:
                        stats['error'] += 1
                        
                except Exception as e:
                    self.log(f"❌ ({finished_tasks}/{len(ids_to_process)}) {bid[:12]}...: {e}")
                    stats['error'] += 1
        
        # 统计报告
        summary = (
            f"\n📊 任务统计报告:\n"
            f"--------------------------------\n"
            f"🔗 有资格待验证:   {stats['link_unverified']}\n"
            f"✅ 已过验证未绑卡: {stats['link_verified']}\n"
            f"💳 已过验证已绑卡: {stats['subscribed']}\n"
            f"❌ 无资格 (不可用): {stats['ineligible']}\n"
            f"⏳ 超时/错误:      {stats['timeout'] + stats['error']}\n"
            f"--------------------------------\n"
            f"总计处理: {finished_tasks}/{len(ids_to_process)}"
        )
        self.log(summary)
        self.finished_signal.emit({
            'type': 'sheerlink', 
            'count': success_count, 
            'stats': stats,
            'summary': summary
        })
    
    def run_create(self):
        """执行创建窗口任务"""
        accounts = self.kwargs.get('accounts', [])
        name_prefix = self.kwargs.get('name_prefix', '默认模板')
        template_id = self.kwargs.get('template_id', None)
        proxies = self.kwargs.get('proxies', [])
        platform_url = self.kwargs.get('platform_url', '')
        extra_url = self.kwargs.get('extra_url', '')
        
        if not accounts:
            self.log("❌ 未提供账号列表")
            self.finished_signal.emit({'type': 'create', 'count': 0})
            return
        
        self.log(f"\n[开始] 批量创建窗口，共 {len(accounts)} 个账号...")
        
        try:
            from core.bit_api import create_browsers_batch
            from core.database import DBManager
        except ImportError as e:
            self.log(f"❌ 导入失败: {e}")
            self.finished_signal.emit({'type': 'create', 'count': 0, 'error': str(e)})
            return
        
        created_count = 0
        
        def on_create(index, account, browser_id, error):
            nonlocal created_count
            email = account.get('email', '')
            self.progress_signal.emit(index + 1, len(accounts))
            
            if browser_id:
                self.log(f"  [{index+1}/{len(accounts)}] ✅ {email} -> {browser_id[:12]}...")
                DBManager.update_account_browser_id(email, browser_id)
                created_count += 1
            else:
                self.log(f"  [{index+1}/{len(accounts)}] ❌ {email}: {error}")
        
        def stop_check():
            return not self.is_running
        
        # 批量创建
        success, total = create_browsers_batch(
            accounts=accounts,
            name_prefix=name_prefix,
            template_id=template_id,
            proxies=proxies,
            platform_url=platform_url,
            extra_url=extra_url,
            callback=on_create,
            stop_check=stop_check
        )
        
        if not self.is_running:
            self.log("\n⚠️ 任务已停止")
        
        self.log(f"\n创建完成，成功 {created_count}/{total} 个")
        self.finished_signal.emit({
            'type': 'create', 
            'count': created_count,
            'total': total
        })
    
    def run_delete(self):
        """执行删除窗口任务"""
        ids_to_delete = self.kwargs.get('ids', [])
        
        if not ids_to_delete:
            self.finished_signal.emit({'type': 'delete', 'count': 0})
            return
        
        self.log(f"\n[开始] 批量删除窗口，共 {len(ids_to_delete)} 个...")
        
        try:
            from core.bit_api import delete_browsers_batch
        except ImportError as e:
            self.log(f"❌ 导入失败: {e}")
            self.finished_signal.emit({'type': 'delete', 'count': 0, 'error': str(e)})
            return
        
        deleted_count = 0
        failed_count = 0
        
        for i, bid in enumerate(ids_to_delete):
            if not self.is_running:
                self.log('[用户操作] 任务已停止')
                break
            
            self.progress_signal.emit(i + 1, len(ids_to_delete))
            
            try:
                result = delete_browsers_batch([bid])
                if result.get('success'):
                    self.log(f"  ✅ ({i+1}/{len(ids_to_delete)}) {bid[:12]}... 已删除")
                    deleted_count += 1
                else:
                    self.log(f"  ❌ ({i+1}/{len(ids_to_delete)}) {bid[:12]}... 删除失败")
                    failed_count += 1
            except Exception as e:
                self.log(f"  ❌ ({i+1}/{len(ids_to_delete)}) {bid[:12]}... 异常: {e}")
                failed_count += 1
            
            self.msleep_safe(200)  # 避免API过载
        
        self.log(f"\n删除完成，成功 {deleted_count}，失败 {failed_count}")
        self.finished_signal.emit({
            'type': 'delete', 
            'count': deleted_count,
            'failed': failed_count
        })
    
    def run_open(self):
        """执行打开窗口任务"""
        ids_to_open = self.kwargs.get('ids', [])
        
        if not ids_to_open:
            self.finished_signal.emit({'type': 'open', 'count': 0})
            return
        
        self.log(f"\n[开始] 批量打开窗口，共 {len(ids_to_open)} 个...")
        
        try:
            from core.bit_api import open_browsers_batch
        except ImportError as e:
            self.log(f"❌ 导入失败: {e}")
            self.finished_signal.emit({'type': 'open', 'count': 0, 'error': str(e)})
            return
        
        opened_count = 0
        failed_count = 0
        
        for i, bid in enumerate(ids_to_open):
            if not self.is_running:
                self.log('[用户操作] 任务已停止')
                break
            
            self.progress_signal.emit(i + 1, len(ids_to_open))
            
            try:
                result = open_browsers_batch([bid])
                if result.get('success'):
                    self.log(f"  ✅ ({i+1}/{len(ids_to_open)}) {bid[:12]}... 已打开")
                    opened_count += 1
                else:
                    self.log(f"  ❌ ({i+1}/{len(ids_to_open)}) {bid[:12]}... 打开失败: {result.get('msg')}")
                    failed_count += 1
            except Exception as e:
                self.log(f"  ❌ ({i+1}/{len(ids_to_open)}) {bid[:12]}... 异常: {e}")
                failed_count += 1
            
            self.msleep_safe(500)  # 间隔打开，避免过载
        
        self.log(f"\n打开完成，成功 {opened_count}，失败 {failed_count}")
        self.finished_signal.emit({
            'type': 'open', 
            'count': opened_count,
            'failed': failed_count
        })
    
    def run_2fa(self):
        """生成并保存2FA验证码"""
        self.log("\n[开始] 刷新2FA验证码...")
        
        try:
            import pyotp
            from core.bit_api import get_browser_list_simple
        except ImportError as e:
            self.log(f"❌ 导入失败: {e}")
            self.finished_signal.emit({'type': '2fa', 'count': 0, 'error': str(e)})
            return
        
        # 获取所有浏览器
        browsers = get_browser_list_simple(page=0, page_size=1000)
        
        twofa_data = []
        for browser in browsers:
            if not self.is_running:
                break
            
            name = browser.get('name', '')
            remark = browser.get('remark', '')
            
            if '----' in remark:
                parts = remark.split('----')
                email = parts[0] if len(parts) > 0 else ''
                secret = parts[3].strip() if len(parts) >= 4 else ''
                
                if secret:
                    try:
                        totp = pyotp.TOTP(secret.replace(" ", "").strip())
                        code = totp.now()
                        twofa_data.append({
                            'name': name,
                            'email': email,
                            'secret': secret,
                            'code': code
                        })
                    except Exception as e:
                        self.log(f"  ⚠️ {email}: 2FA生成失败 - {e}")
        
        self.log(f"  生成了 {len(twofa_data)} 个2FA验证码")
        
        self.finished_signal.emit({
            'type': '2fa', 
            'count': len(twofa_data),
            'data': twofa_data
        })

