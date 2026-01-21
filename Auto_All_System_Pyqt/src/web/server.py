"""
@file server.py
@brief Web Admin 服务器
@details 提供账号、代理、卡片的Web管理界面
"""
import http.server
import socketserver
import json
import os
import sys
import urllib.parse

# 获取当前目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 添加src目录到路径（web模块现在在src/web/下）
_src_dir = os.path.dirname(CURRENT_DIR)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

# 导入核心模块（尝试新路径，失败则用旧路径）
try:
    from core.database import DBManager
except ImportError:
    from database import DBManager

# 配置路径
PORT = 8080
TEMPLATE_DIR = os.path.join(CURRENT_DIR, 'templates')
STATIC_DIR = os.path.join(CURRENT_DIR, 'static')


class AccountHandler(http.server.SimpleHTTPRequestHandler):
    """
    @class AccountHandler
    @brief HTTP请求处理器
    @details 处理Web管理界面的所有HTTP请求
    """
    
    def log_message(self, format, *args):
        """
        @brief 静默日志
        """
        pass
    
    def send_json(self, data, status=200):
        """
        @brief 发送JSON响应
        @param data 响应数据
        @param status HTTP状态码
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str, ensure_ascii=False).encode('utf-8'))
    
    def send_html(self, file_path):
        """
        @brief 发送HTML文件
        @param file_path HTML文件路径
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())

    def do_OPTIONS(self):
        """
        @brief 处理CORS预检请求
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """
        @brief 处理GET请求
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 页面路由
        if path == '/':
            self.send_html(os.path.join(TEMPLATE_DIR, 'index.html'))
            return
        
        if path == '/proxies':
            self.send_html(os.path.join(TEMPLATE_DIR, 'proxies.html'))
            return
        
        if path == '/cards':
            self.send_html(os.path.join(TEMPLATE_DIR, 'cards.html'))
            return
            
        # 静态文件
        if path.startswith('/static/'):
            rel_path = path[1:]
            full_path = os.path.join(CURRENT_DIR, rel_path)
            if os.path.exists(full_path):
                self.send_response(200)
                ext = os.path.splitext(full_path)[1]
                content_type = {
                    '.css': 'text/css',
                    '.js': 'application/javascript',
                    '.png': 'image/png',
                    '.ico': 'image/x-icon'
                }.get(ext, 'text/plain')
                self.send_header('Content-type', content_type)
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
            return

        # ==================== API 路由 ====================
        
        # 账号API
        if path == '/api/accounts':
            accounts = DBManager.get_all_accounts()
            self.send_json(accounts)
            return
        
        if path == '/api/accounts/stats':
            stats = DBManager.get_accounts_count_by_status()
            self.send_json(stats)
            return
        
        # 代理API
        if path == '/api/proxies':
            proxies = DBManager.get_all_proxies()
            self.send_json(proxies)
            return
        
        if path == '/api/proxies/available':
            proxies = DBManager.get_available_proxies()
            self.send_json(proxies)
            return
        
        # 卡片API
        if path == '/api/cards':
            cards = DBManager.get_all_cards()
            self.send_json(cards)
            return
        
        if path == '/api/cards/available':
            cards = DBManager.get_available_cards()
            self.send_json(cards)
            return
        
        # 设置API
        if path == '/api/settings':
            settings = DBManager.get_all_settings()
            self.send_json(settings)
            return
        
        # 日志API
        if path == '/api/logs':
            logs = DBManager.get_recent_logs(100)
            self.send_json(logs)
            return

        self.send_error(404)

    def do_POST(self):
        """
        @brief 处理POST请求
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            params = json.loads(post_data.decode('utf-8')) if post_data else {}
        except json.JSONDecodeError:
            self.send_json({'success': False, 'message': 'Invalid JSON'}, 400)
            return
        
        # ==================== 账号操作 ====================
        
        if path == '/api/accounts/import':
            accounts_text = params.get('accounts', '')
            status = params.get('status', 'pending_check')
            separator = params.get('separator', '----')
            
            if not accounts_text:
                self.send_json({'success': False, 'message': '没有提供账号数据'}, 400)
                return
            
            success, errors, error_list = DBManager.import_accounts_from_text(
                accounts_text, separator, status
            )
            
            self.send_json({
                'success': True,
                'imported': success,
                'errors': errors,
                'error_details': error_list[:10]
            })
            return
        
        if path == '/api/accounts/delete':
            emails = params.get('emails', [])
            deleted_count = 0
            
            for email in emails:
                try:
                    DBManager.delete_account(email)
                    deleted_count += 1
                except Exception as e:
                    print(f"删除账号 {email} 失败: {e}")
            
            self.send_json({'success': True, 'deleted': deleted_count})
            return
        
        if path == '/api/accounts/export':
            target_emails = set(params.get('emails', []))
            fields = params.get('fields', ['email'])
            
            all_accs = DBManager.get_all_accounts()
            export_lines = []
            
            for acc in all_accs:
                if acc['email'] in target_emails:
                    parts = []
                    for f in fields:
                        val = acc.get(f) or ''
                        parts.append(str(val))
                    export_lines.append('----'.join(parts))
            
            output = '\n'.join(export_lines)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="export.txt"')
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
            return
        
        if path == '/api/accounts/import_from_browsers':
            try:
                DBManager.import_from_browsers()
                self.send_json({
                    'success': True, 
                    'message': '已开始后台导入任务，请留意控制台日志'
                })
            except Exception as e:
                self.send_json({'success': False, 'message': str(e)}, 500)
            return
        
        # ==================== 代理操作 ====================
        
        if path == '/api/proxies/import':
            proxies_text = params.get('proxies', '')
            proxy_type = params.get('type', 'socks5')
            
            if not proxies_text:
                self.send_json({'success': False, 'message': '没有提供代理数据'}, 400)
                return
            
            success, errors, error_list = DBManager.import_proxies_from_text(
                proxies_text, proxy_type
            )
            
            self.send_json({
                'success': True,
                'imported': success,
                'errors': errors,
                'error_details': error_list[:10]
            })
            return
        
        if path == '/api/proxies/delete':
            proxy_ids = params.get('ids', [])
            deleted_count = 0
            
            for proxy_id in proxy_ids:
                try:
                    DBManager.delete_proxy(proxy_id)
                    deleted_count += 1
                except Exception as e:
                    print(f"删除代理 {proxy_id} 失败: {e}")
            
            self.send_json({'success': True, 'deleted': deleted_count})
            return
        
        if path == '/api/proxies/clear':
            DBManager.clear_all_proxies()
            self.send_json({'success': True, 'message': '所有代理已清空'})
            return
        
        # ==================== 卡片操作 ====================
        
        if path == '/api/cards/import':
            cards_text = params.get('cards', '')
            max_usage = params.get('max_usage', 1)
            
            if not cards_text:
                self.send_json({'success': False, 'message': '没有提供卡片数据'}, 400)
                return
            
            success, errors, error_list = DBManager.import_cards_from_text(
                cards_text, max_usage
            )
            
            self.send_json({
                'success': True,
                'imported': success,
                'errors': errors,
                'error_details': error_list[:10]
            })
            return
        
        if path == '/api/cards/delete':
            card_ids = params.get('ids', [])
            deleted_count = 0
            
            for card_id in card_ids:
                try:
                    DBManager.delete_card(card_id)
                    deleted_count += 1
                except Exception as e:
                    print(f"删除卡片 {card_id} 失败: {e}")
            
            self.send_json({'success': True, 'deleted': deleted_count})
            return
        
        if path == '/api/cards/clear':
            DBManager.clear_all_cards()
            self.send_json({'success': True, 'message': '所有卡片已清空'})
            return
        
        if path == '/api/cards/toggle':
            card_id = params.get('id')
            is_active = params.get('is_active', True)
            
            if card_id:
                DBManager.set_card_active(card_id, is_active)
                self.send_json({'success': True})
            else:
                self.send_json({'success': False, 'message': '缺少卡片ID'}, 400)
            return
        
        # ==================== 设置操作 ====================
        
        if path == '/api/settings/save':
            for key, value in params.items():
                DBManager.set_setting(key, str(value))
            self.send_json({'success': True})
            return
        
        # ==================== 导出文件（兼容旧版） ====================
        
        if path == '/api/export_files':
            DBManager.export_to_files()
            self.send_json({'success': True, 'message': '已导出到txt文件'})
            return
            
        self.send_error(404)


def run_server(port=8080):
    """
    @brief 启动Web Admin服务器
    @param port 服务器端口
    """
    # 确保目录存在
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)
    
    # 初始化数据库
    DBManager.init_db()
    
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), AccountHandler) as httpd:
            print(f"WEB ADMIN STARTED: http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        print(f"Web Admin Port {port} busy or error: {e}")


if __name__ == "__main__":
    run_server()
