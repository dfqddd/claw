#!/usr/bin/env python3
"""
批量爬取选手详细信息和言论
包含：基本信息 + 发帖内容 + 交易记录 + 布道言论
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
COOKIES_FILE = BASE_DIR / ".cookies"

DATA_DIR.mkdir(exist_ok=True)

# ============================================================
# 加载 Cookie
# ============================================================

def load_cookies():
    """加载 Cookie"""
    if not COOKIES_FILE.exists():
        return {}
    
    cookies = {}
    with open(COOKIES_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    cookies[key.strip()] = value.strip()
    
    return cookies

# ============================================================
# 爬取函数
# ============================================================

def get_trader_profile(user_id):
    """获取选手基本信息"""
    url = f"https://www.tgb.cn/blog/{user_id}"
    
    cookie_str = "; ".join([f"{k}={v}" for k, v in load_cookies().items()])
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie_str,
        'Referer': 'https://www.tgb.cn/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        profile = {
            'user_id': user_id,
            'name': '',
            'fans': 0,
            'follow': 0,
            'join_date': '',
            'ip_location': '',
            'bio': '',
            'total_posts': 0,
            'total_likes': 0
        }
        
        # 提取姓名
        h1 = soup.find('h1')
        if h1:
            profile['name'] = h1.get_text(strip=True).replace('的博客', '')
        
        # 提取粉丝数
        for item in soup.select('a, span, div'):
            text = item.get_text(strip=True)
            if '粉丝' in text:
                nums = ''.join(filter(str.isdigit, text))
                if nums:
                    profile['fans'] = int(nums)
            elif '关注' in text and '粉丝' not in text:
                nums = ''.join(filter(str.isdigit, text))
                if nums:
                    profile['follow'] = int(nums)
        
        # 提取简介
        for item in soup.select('[ref*="e"], span, div'):
            text = item.get_text(strip=True)
            if text and len(text) < 100 and '保持' in text or '审美' in text or '纯粹' in text:
                profile['bio'] = text
        
        # 提取 IP 属地
        for item in soup.select('[ref*="e"], span'):
            text = item.get_text(strip=True)
            if 'IP 属地' in text:
                profile['ip_location'] = text.replace('IP 属地:', '').strip()
        
        # 提取注册时间
        for item in soup.select('[ref*="e"], span'):
            text = item.get_text(strip=True)
            if '注册时间' in text:
                profile['join_date'] = text.replace('注册时间：', '').strip()
        
        return profile
    
    except Exception as e:
        print(f"  ❌ 获取基本信息失败：{e}")
        return None

def get_trader_posts(user_id, limit=20):
    """获取选手发帖列表"""
    url = f"https://www.tgb.cn/user/blog/moreTopic?userID={user_id}"
    
    cookie_str = "; ".join([f"{k}={v}" for k, v in load_cookies().items()])
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie_str,
        'Referer': 'https://www.tgb.cn/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        posts = []
        
        # 提取帖子列表
        for item in soup.select('a[href*="/a/"]'):
            title = item.get_text(strip=True)
            href = item.get('href', '')
            
            if title and len(title) > 5:
                post = {
                    'title': title,
                    'url': f"https://www.tgb.cn{href}" if href.startswith('/a/') else href,
                    'type': 'main_post'
                }
                posts.append(post)
                
                if len(posts) >= limit:
                    break
        
        return posts
    
    except Exception as e:
        print(f"  ❌ 获取帖子失败：{e}")
        return []

def get_post_content(post_url):
    """获取帖子详细内容"""
    cookie_str = "; ".join([f"{k}={v}" for k, v in load_cookies().items()])
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie_str,
        'Referer': 'https://www.tgb.cn/',
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = {
            'title': '',
            'content': '',
            'publish_date': '',
            'views': 0,
            'comments': 0,
            'likes': 0,
            'tags': []
        }
        
        # 提取标题
        h1 = soup.find('h1')
        if h1:
            content['title'] = h1.get_text(strip=True)
        
        # 提取正文
        content_div = soup.find('div', class_='content') or soup.find('div', id='content')
        if content_div:
            content['content'] = content_div.get_text(strip=True)[:2000]  # 限制长度
        
        # 提取元数据
        for item in soup.select('span, div'):
            text = item.get_text(strip=True)
            
            if '阅读' in text:
                nums = ''.join(filter(str.isdigit, text))
                if nums:
                    content['views'] = int(nums)
            elif '评论' in text:
                nums = ''.join(filter(str.isdigit, text))
                if nums:
                    content['comments'] = int(nums)
            elif '赞' in text or '加油' in text:
                nums = ''.join(filter(str.isdigit, text))
                if nums:
                    content['likes'] = int(nums)
        
        return content
    
    except Exception as e:
        print(f"    ❌ 获取内容失败：{e}")
        return None

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("淘股吧知名选手详细信息批量爬取")
    print("=" * 70)
    print()
    
    # 加载选手列表
    with open(DATA_DIR / "all_famous_traders.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    traders = data['traders']
    
    # 只处理有 ID 的选手
    traders_with_id = [t for t in traders if t.get('user_id')]
    
    print(f"待处理：{len(traders_with_id)} 个选手 (共{len(traders)}个，{len(traders)-len(traders_with_id)}个无 ID)\n")
    
    all_data = {
        'collect_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': '淘股吧',
        'total': len(traders_with_id),
        'traders': []
    }
    
    for i, trader in enumerate(traders_with_id, 1):
        print(f"[{i}/{len(traders_with_id)}] {trader['name']} (ID: {trader['user_id']})")
        
        # 获取基本信息
        profile = get_trader_profile(trader['user_id'])
        
        if profile:
            trader_data = {
                **trader,
                **profile,
                'posts': [],
                'status': 'collected'
            }
            
            # 获取发帖列表
            posts = get_trader_posts(trader['user_id'], limit=10)
            
            if posts:
                print(f"  📝 找到 {len(posts)} 个帖子")
                
                # 获取前 3 个帖子的详细内容
                detailed_posts = []
                for post in posts[:3]:
                    print(f"    读取：{post['title'][:30]}...")
                    post_content = get_post_content(post['url'])
                    if post_content:
                        detailed_posts.append(post_content)
                    time.sleep(0.5)  # 避免请求过快
                
                trader_data['posts'] = detailed_posts
                trader_data['total_posts'] = len(posts)
            
            all_data['traders'].append(trader_data)
            print(f"  ✅ 粉丝：{profile.get('fans', 0)}, 帖子：{len(posts)}")
        else:
            print(f"  ❌ 获取失败")
            all_data['traders'].append({
                **trader,
                'status': 'failed'
            })
        
        print()
        time.sleep(1)  # 避免请求过快
        
        # 每 5 个保存一次
        if i % 5 == 0:
            temp_file = DATA_DIR / "traders_temp.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            print(f"  💾 临时保存进度：{i}/{len(traders_with_id)}\n")
    
    # 保存最终结果
    output_file = DATA_DIR / "famous_traders_full.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✅ 爬取完成！")
    print(f"✅ 保存至：{output_file}")
    print(f"✅ 成功：{sum(1 for t in all_data['traders'] if t.get('status')=='collected')}/{len(traders_with_id)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
