"""
@file main.py
@brief 程序主入口
@details Auto_All_System_Pyqt 应用程序入口点
"""
import sys
import os

# 确保src目录在路径中
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# 初始化核心模块（尝试新路径，失败则用旧路径）
try:
    from core.database import DBManager
except ImportError:
    from database import DBManager

DBManager.init_db()


def run_gui():
    """
    @brief 运行主GUI界面
    """
    from PyQt6.QtWidgets import QApplication
    
    # 尝试新路径，失败则用旧路径
    try:
        from google.frontend import BrowserWindowCreatorGUI
    except ImportError:
        from create_window_gui import BrowserWindowCreatorGUI
    
    app = QApplication(sys.argv)
    window = BrowserWindowCreatorGUI()
    window.show()
    sys.exit(app.exec())


def run_web_admin(port=8080):
    """
    @brief 运行Web管理界面
    @param port 服务器端口
    """
    try:
        from web.server import run_server
    except ImportError:
        # 兼容旧路径
        try:
            _dist_path = os.path.join(os.path.dirname(SRC_DIR), 'dist')
            if _dist_path not in sys.path:
                sys.path.insert(0, _dist_path)
            from web_admin.server import run_server
        except ImportError:
            print("[ERROR] Web Admin模块未找到")
            return
    
    run_server(port)


def main():
    """
    @brief 主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto All System PyQt')
    parser.add_argument('--web', action='store_true', help='启动Web管理界面')
    parser.add_argument('--port', type=int, default=8080, help='Web服务器端口')
    
    args = parser.parse_args()
    
    if args.web:
        run_web_admin(args.port)
    else:
        run_gui()


if __name__ == '__main__':
    main()
