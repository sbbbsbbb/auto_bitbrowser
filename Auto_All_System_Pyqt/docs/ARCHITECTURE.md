# Auto_All_System_Pyqt 项目架构说明

## 📁 新目录结构（重构后）

```
Auto_All_System_Pyqt/
├── src/
│   ├── core/                    # 核心公共模块
│   │   ├── __init__.py
│   │   ├── config.py            # 统一配置管理
│   │   ├── database.py          # 数据库管理（SQLite）
│   │   ├── bitbrowser_api.py    # 比特浏览器API封装
│   │   ├── bit_api.py           # 比特浏览器简化接口
│   │   └── bit_playwright.py    # Playwright自动化封装
│   │
│   ├── google/                  # 谷歌业务模块（按业务分模块）
│   │   ├── __init__.py
│   │   ├── backend/             # 后端业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── account_manager.py    # 账号状态管理
│   │   │   └── sheerid_verifier.py   # SheerID验证器
│   │   │
│   │   ├── frontend/            # 前端GUI界面（兼容层）
│   │   │   └── __init__.py      # 从src/导入现有GUI
│   │   │
│   │   └── web/                 # Web管理界面
│   │       ├── __init__.py
│   │       ├── server.py        # HTTP服务器
│   │       ├── static/          # 静态资源(CSS/JS)
│   │       └── templates/       # HTML模板
│   │
│   ├── workers/                 # 工作线程模块
│   │   ├── __init__.py
│   │   └── base_worker.py       # 基础工作线程类
│   │
│   ├── main.py                  # 新的程序入口
│   │
│   │── # 旧文件（待完全迁移后可删除）
│   ├── create_window_gui.py     # 主窗口GUI
│   ├── bind_card_gui.py         # 绑卡窗口GUI
│   ├── sheerid_gui.py           # SheerID验证窗口
│   ├── auto_all_in_one_gui.py   # 一键全自动窗口
│   ├── run_playwright_google.py # Google自动化
│   ├── auto_bind_card.py        # 自动绑卡逻辑
│   └── ...
│
├── data/                        # 数据目录
│   └── accounts.db              # SQLite数据库
│
├── dist/                        # 打包输出（旧位置）
│   └── web_admin/               # 旧的Web管理界面（已迁移到google/web/）
│
├── docs/                        # 文档
├── resources/                   # 资源文件
└── scripts/                     # 脚本
```

## 🏗️ 架构设计原则

### 1. 前后端分离
- **后端（backend/）**: 纯业务逻辑，无UI依赖
- **前端（frontend/）**: PyQt6 GUI界面
- **Web界面（web/）**: HTTP服务器 + HTML/CSS/JS

### 2. 模块化设计
- **core/**: 所有业务共享的核心模块
- **google/**: 谷歌业务相关的所有代码
- **workers/**: 可复用的工作线程基类

### 3. 可扩展性
后续添加新业务（如其他平台）时，只需创建类似结构：
```
src/
├── google/          # 已有
├── facebook/        # 新业务
│   ├── backend/
│   ├── frontend/
│   └── web/
└── twitter/         # 新业务
    ├── backend/
    ├── frontend/
    └── web/
```

## 📦 导入方式

### 新方式（推荐）
```python
# 核心模块
from core.database import DBManager
from core.config import Config
from core import BitBrowserAPI

# 谷歌业务模块
from google.backend import SheerIDVerifier, AccountManager
from google.frontend import BrowserWindowCreatorGUI
from google.web import run_server
```

### 兼容方式（保持向后兼容）
```python
# 旧路径仍然可用
from database import DBManager
from create_window_gui import BrowserWindowCreatorGUI
```

## 🚀 运行方式

### GUI模式
```bash
python src/main.py
```

### Web管理界面
```bash
python src/main.py --web --port 8080
```

## ⚠️ 迁移状态

| 模块 | 状态 | 新位置 |
|------|------|--------|
| database.py | ✅ 已迁移 | core/database.py |
| bitbrowser_api.py | ✅ 已迁移 | core/bitbrowser_api.py |
| bit_api.py | ✅ 已迁移 | core/bit_api.py |
| bit_playwright.py | ✅ 已迁移 | core/bit_playwright.py |
| config.py | ✅ 新建 | core/config.py |
| account_manager.py | ✅ 已迁移 | google/backend/account_manager.py |
| sheerid_verifier.py | ✅ 已迁移 | google/backend/sheerid_verifier.py |
| web_admin/ | ✅ 已迁移 | google/web/ |
| base_worker.py | ✅ 新建 | workers/base_worker.py |
| run_playwright_google.py | 🔄 待迁移 | google/backend/playwright_google.py |
| auto_bind_card.py | 🔄 待迁移 | google/backend/auto_bind_card.py |
| create_window_gui.py | 🔄 待迁移 | google/frontend/main_window.py |
| bind_card_gui.py | 🔄 待迁移 | google/frontend/bind_card_window.py |
| sheerid_gui.py | 🔄 待迁移 | google/frontend/sheerid_window.py |
| auto_all_in_one_gui.py | 🔄 待迁移 | google/frontend/auto_all_window.py |

> 🔄 待迁移的模块目前通过兼容层从旧位置导入，功能正常
