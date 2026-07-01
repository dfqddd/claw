#!/usr/bin/env python3
"""
测试账号登录
验证配置的账号是否能正常登录各论坛
"""

import requests
from pathlib import Path
import os
import sys

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
CREDENTIALS_FILE = BASE_DIR / ".credentials"

# ============================================================
# 读取账号配置
# ============================================================

def get_credentials():
    """读取账号配置"""
    creds = {}
    
    # 方式 1: 从环境变量读取
    if os.getenv('TAOGUBA_USERNAME'):
        creds['taoguba'] = {
            'username': os.getenv('TAOGUBA_USERNAME'),
            'password': os.getenv('TAOGUBA_PASSWORD'),
        }
    
    if os.getenv('EASTMONEY_USERNAME'):
        creds['eastmoney'] = {
            'username': os.getenv('EASTMONEY_USERNAME'),
            'password': os.getenv('EASTMONEY_PASSWORD'),
        }
    
    if os.getenv('XUEQIU_PHONE'):
        creds['xueqiu'] = {
            'phone': os.getenv('XUEQIU_PHONE'),
            'password': os.getenv('XUEQIU_PASSWORD'),
        }
    
    # 方式 2: 从配置文件读取
    if CREDENTIALS_FILE.exists() and not creds:
        import configparser
        config = configparser.ConfigParser()
        config.read(CREDENTIALS_FILE)
        
        if 'taoguba' in config:
            creds['taoguba'] = dict(config['taoguba'])
        if 'eastmoney' in config:
            creds['eastmoney'] = dict(config['eastmoney'])
        if 'xueqiu' in config:
            creds['xueqiu'] = dict(config['xueqiu'])
    
    return creds

# ============================================================
# 登录测试函数
# ============================================================

def test_taoguba_login(username, password):
    """测试淘股吧登录"""
    print("\n" + "=" * 60)
    print("测试淘股吧登录...")
    print("=" * 60)
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.taoguba.com.cn/login',
    }
    
    # 登录接口 (需要根据实际 API 调整)
    login_url = 'https://www.taoguba.com.cn/ajax/login'
    data = {
        'username': username,
        'password': password,
    }
    
    try:
        response = session.post(login_url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 淘股吧登录成功!")
                print(f"   用户名：{username}")
                return session
            else:
                print(f"❌ 淘股吧登录失败：{result.get('message', '未知错误')}")
        else:
            print(f"❌ 淘股吧登录失败：HTTP {response.status_code}")
    
    except Exception as e:
        print(f"❌ 淘股吧登录异常：{e}")
    
    return None

def test_eastmoney_login(username, password):
    """测试东方财富登录"""
    print("\n" + "=" * 60)
    print("测试东方财富登录...")
    print("=" * 60)
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://passport.eastmoney.com/',
    }
    
    # 登录接口 (需要根据实际 API 调整)
    login_url = 'https://passport.eastmoney.com/user/login'
    data = {
        'userName': username,
        'pwd': password,
    }
    
    try:
        response = session.post(login_url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('Status') == 0 or result.get('success'):
                print("✅ 东方财富登录成功!")
                print(f"   用户名：{username}")
                return session
            else:
                print(f"❌ 东方财富登录失败：{result.get('Message', '未知错误')}")
        else:
            print(f"❌ 东方财富登录失败：HTTP {response.status_code}")
    
    except Exception as e:
        print(f"❌ 东方财富登录异常：{e}")
    
    return None

def test_xueqiu_login(phone, password):
    """测试雪球登录"""
    print("\n" + "=" * 60)
    print("测试雪球登录...")
    print("=" * 60)
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://xueqiu.com/',
    }
    
    # 登录接口 (需要根据实际 API 调整)
    login_url = 'https://xueqiu.com/snowman/login'
    data = {
        'phone': phone,
        'password': password,
    }
    
    try:
        response = session.post(login_url, data=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 雪球登录成功!")
                print(f"   手机号：{phone}")
                return session
            else:
                print(f"❌ 雪球登录失败：{result.get('error_description', '未知错误')}")
        else:
            print(f"❌ 雪球登录失败：HTTP {response.status_code}")
    
    except Exception as e:
        print(f"❌ 雪球登录异常：{e}")
    
    return None

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("交易模式挖掘 - 账号登录测试")
    print("=" * 60)
    
    # 读取配置
    creds = get_credentials()
    
    if not creds:
        print("\n❌ 未找到账号配置!")
        print("\n请按以下方式之一配置:")
        print("1. 环境变量：在 ~/.bashrc 或 ~/.zshrc 中添加 TAOGUBA_USERNAME 等")
        print("2. 配置文件：在 .credentials 文件中填写")
        print("\n详见：ACCOUNT_SETUP.md")
        sys.exit(1)
    
    print(f"\n找到 {len(creds)} 个账号配置")
    
    # 测试登录
    sessions = {}
    
    if 'taoguba' in creds:
        session = test_taoguba_login(creds['taoguba']['username'], creds['taoguba']['password'])
        if session:
            sessions['taoguba'] = session
    
    if 'eastmoney' in creds:
        session = test_eastmoney_login(creds['eastmoney']['username'], creds['eastmoney']['password'])
        if session:
            sessions['eastmoney'] = session
    
    if 'xueqiu' in creds:
        session = test_xueqiu_login(creds['xueqiu']['phone'], creds['xueqiu']['password'])
        if session:
            sessions['xueqiu'] = session
    
    # 总结
    print("\n" + "=" * 60)
    print("登录测试总结")
    print("=" * 60)
    
    if sessions:
        print(f"\n✅ 成功登录 {len(sessions)} 个网站:")
        for site in sessions.keys():
            print(f"   - {site}")
        print("\n可以开始爬取数据了!")
        print("\n运行:")
        print("  python3 scripts/crawl_taoguba.py --limit 100")
        print("  python3 scripts/crawl_eastmoney.py --limit 100")
    else:
        print("\n❌ 所有登录都失败了")
        print("\n请检查:")
        print("1. 账号密码是否正确")
        print("2. 是否需要验证码/短信验证")
        print("3. 网络是否正常")
        sys.exit(1)

if __name__ == "__main__":
    main()
