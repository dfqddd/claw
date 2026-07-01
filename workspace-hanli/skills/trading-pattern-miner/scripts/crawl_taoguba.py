#!/usr/bin/env python3
"""
淘股吧实盘数据爬取
只抓取有交割单验证的实盘选手
使用 Cookie 自动登录
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from pathlib import Path
import configparser

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "trading_patterns.db"
COOKIES_FILE = BASE_DIR / ".cookies"

# 创建数据目录
DATA_DIR.mkdir(exist_ok=True)

# ============================================================
# 加载 Cookie
# ============================================================

def load_cookies():
    """加载 Cookie"""
    if not COOKIES_FILE.exists():
        print("⚠️  未找到 Cookie 文件，请先登录并保存 Cookie")
        print("   运行：python3 scripts/save_cookies.py")
        return {}
    
    # 直接读取文件，避免 configparser 的转义问题
    cookies = {}
    with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    cookies[key.strip()] = value.strip()
    
    # 构建 Cookie 字符串
    cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    return cookie_str

# ============================================================
# 淘股吧实盘帖列表
# ============================================================

REAL_POST_URLS = [
    # 实盘大赛专区
    "https://www.taoguba.com.cn/bbs/1000006",
    # 实盘比赛
    "https://www.taoguba.com.cn/bbs/1000007",
]

# ============================================================
# 爬取函数
# ============================================================

def get_post_list(url, page=1):
    """获取帖子列表"""
    params = {'p': page}
    
    # 加载 Cookie
    cookie_str = load_cookies()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie_str,
        'Referer': 'https://www.tgb.cn/',
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        posts = []
        # 解析帖子列表（需要根据实际 HTML 结构调整）
        for item in soup.select('.topic-item'):
            title_elem = item.select_one('.topic-title')
            author_elem = item.select_one('.author-name')
            reply_elem = item.select_one('.reply-count')
            view_elem = item.select_one('.view-count')
            
            if title_elem:
                posts.append({
                    'title': title_elem.get_text(strip=True),
                    'url': title_elem.get('href'),
                    'author': author_elem.get_text(strip=True) if author_elem else '',
                    'replies': int(reply_elem.get_text(strip=True) or 0),
                    'views': int(view_elem.get_text(strip=True) or 0),
                })
        
        return posts
    
    except Exception as e:
        print(f"[ERROR] 爬取失败：{e}")
        return []

def get_post_detail(url):
    """获取帖子详情"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取帖子内容
        content = []
        for post in soup.select('.post-item'):
            author = post.select_one('.author-name')
            content_elem = post.select_one('.post-content')
            time_elem = post.select_one('.post-time')
            
            # 检查是否有交割单
            has_receipt = False
            if content_elem:
                text = content_elem.get_text()
                if any(kw in text for kw in ['交割单', '持仓', '买入', '卖出', '收益']):
                    has_receipt = True
                
                # 检查是否有图片（交割单截图）
                images = content_elem.select('img')
                if images:
                    has_receipt = True
            
            content.append({
                'author': author.get_text(strip=True) if author else '',
                'content': content_elem.get_text(strip=True) if content_elem else '',
                'time': time_elem.get_text(strip=True) if time_elem else '',
                'has_receipt': has_receipt,
            })
        
        return content
    
    except Exception as e:
        print(f"[ERROR] 爬取失败：{e}")
        return []

def extract_trader_info(posts):
    """从帖子中提取选手信息"""
    traders = []
    
    for post in posts:
        # 筛选条件：
        # 1. 回复数 > 100（有人关注）
        # 2. 标题包含"实盘"（实盘帖）
        # 3. 浏览数 > 1000（有一定热度）
        
        if (post.get('replies', 0) > 100 and 
            '实盘' in post.get('title', '') and
            post.get('views', 0) > 1000):
            
            traders.append({
                'name': post.get('author', ''),
                'title': post.get('title', ''),
                'url': post.get('url', ''),
                'source': '淘股吧',
                'replies': post.get('replies', 0),
                'views': post.get('views', 0),
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
    
    return traders

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("淘股吧实盘数据爬取")
    print("=" * 60)
    
    all_traders = []
    
    for url in REAL_POST_URLS:
        print(f"\n爬取：{url}")
        
        # 爬取前 10 页
        for page in range(1, 11):
            print(f"  页码：{page}")
            
            posts = get_post_list(url, page)
            if not posts:
                break
            
            traders = extract_trader_info(posts)
            all_traders.extend(traders)
            
            # 避免请求过快
            time.sleep(1)
        
        print(f"  找到 {len(all_traders)} 个实盘选手")
    
    # 保存结果
    output_file = DATA_DIR / "taoguba_traders.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_traders, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 保存至：{output_file}")
    print(f"✅ 共 {len(all_traders)} 个实盘选手")

if __name__ == "__main__":
    main()
