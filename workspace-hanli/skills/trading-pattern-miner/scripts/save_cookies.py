#!/usr/bin/env python3
"""
手动保存 Cookie
从浏览器控制台复制 Cookie 后运行此脚本保存
"""

import os
from pathlib import Path

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
COOKIES_FILE = BASE_DIR / ".cookies"

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("淘股吧 Cookie 手动保存")
    print("=" * 60)
    print()
    print("请按以下步骤操作:")
    print()
    print("1. 在浏览器中打开淘股吧 (https://www.tgb.cn/)")
    print("2. 按 F12 打开开发者工具")
    print("3. 切换到 Console (控制台) 标签")
    print("4. 粘贴以下代码并回车:")
    print()
    print("   console.log(document.cookie);")
    print()
    print("5. 复制输出的 Cookie 字符串")
    print("6. 粘贴到下面")
    print()
    print("=" * 60)
    
    cookie_str = input("\n粘贴 Cookie 字符串：").strip()
    
    if not cookie_str:
        print("\n❌ Cookie 为空，已取消")
        return
    
    # 解析 Cookie
    cookies = {}
    for item in cookie_str.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    
    if not cookies:
        print("\n❌ 无法解析 Cookie，格式错误")
        return
    
    print(f"\n✅ 解析到 {len(cookies)} 个 Cookie:")
    for name in cookies.keys():
        print(f"   - {name}")
    
    # 保存到文件
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        f.write("[taoguba]\n")
        for name, value in cookies.items():
            f.write(f"{name} = {value}\n")
    
    # 设置权限
    os.chmod(COOKIES_FILE, 0o600)
    
    print(f"\n✅ Cookie 已保存到：{COOKIES_FILE}")
    print(f"✅ 权限已设置为 600 (仅自己可读)")
    print()
    print("现在可以运行爬取脚本了:")
    print("  python3 scripts/crawl_taoguba.py")

if __name__ == "__main__":
    main()
