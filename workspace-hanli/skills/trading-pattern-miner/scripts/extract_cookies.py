#!/usr/bin/env python3
"""
从浏览器提取淘股吧 Cookie
支持 Chrome/Firefox/Safari
"""

import subprocess
import json
import sqlite3
import os
from pathlib import Path

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
COOKIES_FILE = BASE_DIR / ".cookies"

# ============================================================
# 浏览器 Cookie 路径
# ============================================================

BROWSER_PATHS = {
    'chrome': {
        'mac': '~/Library/Application Support/Google/Chrome/Default/Cookies',
        'win': '%LOCALAPPDATA%/Google/Chrome/User Data/Default/Cookies',
    },
    'firefox': {
        'mac': '~/Library/Application Support/Firefox/Profiles/*.default-release/cookies.sqlite',
        'win': '%APPDATA%/Mozilla/Firefox/Profiles/*.default-release/cookies.sqlite',
    },
    'safari': {
        'mac': '~/Library/Cookies/Cookies.binarycookies',
    },
}

# ============================================================
# 提取函数
# ============================================================

def get_chrome_cookies():
    """提取 Chrome Cookie"""
    import glob
    
    cookie_path = os.path.expanduser(BROWSER_PATHS['chrome']['mac'])
    cookie_files = glob.glob(cookie_path)
    
    if not cookie_files:
        print("❌ 未找到 Chrome Cookie 文件")
        return {}
    
    cookie_file = cookie_files[0]
    print(f"找到 Chrome Cookie: {cookie_file}")
    
    # Chrome Cookie 是 SQLite 数据库
    try:
        conn = sqlite3.connect(cookie_file)
        cursor = conn.cursor()
        
        # 查询淘股吧 Cookie
        cursor.execute("""
            SELECT name, value, encrypted_value 
            FROM cookies 
            WHERE host_key LIKE '%tgb.cn%' OR host_key LIKE '%taoguba.com%'
        """)
        
        cookies = {}
        for row in cursor.fetchall():
            name = row[0]
            value = row[1]
            encrypted = row[2]
            
            if value:
                cookies[name] = value
            elif encrypted:
                # 需要解密（暂不处理）
                print(f"  ⚠️ {name} 是加密的，跳过")
        
        conn.close()
        return cookies
    
    except Exception as e:
        print(f"❌ 读取失败：{e}")
        return {}

def get_firefox_cookies():
    """提取 Firefox Cookie"""
    import glob
    
    cookie_path = os.path.expanduser(BROWSER_PATHS['firefox']['mac'])
    cookie_files = glob.glob(cookie_path)
    
    if not cookie_files:
        print("❌ 未找到 Firefox Cookie 文件")
        return {}
    
    cookie_file = cookie_files[0]
    print(f"找到 Firefox Cookie: {cookie_file}")
    
    try:
        conn = sqlite3.connect(cookie_file)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, value 
            FROM moz_cookies 
            WHERE baseDomain LIKE '%tgb.cn%' OR baseDomain LIKE '%taoguba.com%'
        """)
        
        cookies = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return cookies
    
    except Exception as e:
        print(f"❌ 读取失败：{e}")
        return {}

def save_cookies(cookies):
    """保存 Cookie 到文件"""
    if not cookies:
        print("❌ 没有 Cookie 可保存")
        return
    
    with open(COOKIES_FILE, 'w', encoding='utf-8') as f:
        f.write("[taoguba]\n")
        for name, value in cookies.items():
            f.write(f"{name} = {value}\n")
    
    # 设置权限
    os.chmod(COOKIES_FILE, 0o600)
    
    print(f"\n✅ Cookie 已保存到：{COOKIES_FILE}")
    print(f"✅ 共保存 {len(cookies)} 个 Cookie")

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("淘股吧 Cookie 提取工具")
    print("=" * 60)
    print()
    print("请确保你已经在浏览器中登录了淘股吧")
    print()
    
    # 尝试 Chrome
    print("尝试从 Chrome 提取 Cookie...")
    cookies = get_chrome_cookies()
    
    if not cookies:
        # 尝试 Firefox
        print("\n尝试从 Firefox 提取 Cookie...")
        cookies = get_firefox_cookies()
    
    if cookies:
        print(f"\n找到 {len(cookies)} 个淘股吧 Cookie:")
        for name in cookies.keys():
            print(f"  - {name}")
        
        save = input("\n是否保存这些 Cookie？(y/n): ").strip().lower()
        if save == 'y':
            save_cookies(cookies)
            print("\n✅ 完成！以后爬虫可以自动使用这些 Cookie 登录")
        else:
            print("\n❌ 已取消保存")
    else:
        print("\n❌ 未找到淘股吧 Cookie")
        print("\n请确保:")
        print("1. 已在浏览器中登录淘股吧")
        print("2. 浏览器是 Chrome 或 Firefox")
        print("3. 登录后没有退出")

if __name__ == "__main__":
    main()
