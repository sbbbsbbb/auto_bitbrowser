# _legacy 目录说明

此目录包含重构前的原始Python文件，保留供参考。

## 文件列表

| 文件名 | 说明 | 新位置 |
|--------|------|--------|
| `account_manager.py` | 账号状态管理 | `google/backend/account_manager.py` |
| `auto_all_in_one_gui.py` | 一键全自动GUI | 待迁移 |
| `auto_bind_card.py` | 自动绑卡逻辑 | 待迁移 |
| `bind_card_gui.py` | 绑卡GUI | 待迁移 |
| `bit_api.py` | 比特浏览器简化API | `core/bit_api.py` |
| `bit_playwright.py` | Playwright封装 | `core/bit_playwright.py` |
| `bitbrowser_api.py` | 比特浏览器完整API | `core/bitbrowser_api.py` |
| `create_window.py` | 浏览器窗口创建 | 待迁移 |
| `create_window_gui.py` | 主窗口GUI | 待迁移 |
| `database.py` | 数据库管理 | `core/database.py` |
| `migrate_txt_to_db.py` | TXT迁移工具 | 不再需要 |
| `run_playwright_google.py` | Google自动化 | 待迁移 |
| `sheerid_gui.py` | SheerID验证GUI | 待迁移 |
| `sheerid_verifier.py` | SheerID验证器 | `google/backend/sheerid_verifier.py` |

## 注意事项

1. 这些文件**不应该被导入或使用**
2. 如需要参考旧代码逻辑，可以查看这些文件
3. 重构完成后，可以安全删除此目录

---
*重构日期: 2026-01-21*
