#!/usr/bin/env python3
"""
真实热榜 - 只从权威来源抓取
数据源：百度热搜、36 氪、虎嗅
"""

import requests
import json
import re
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json,text/html,*/*',
}

def get_baidu_hot():
    """获取百度热搜"""
    try:
        url = "https://top.baidu.com/board"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        html = response.text
        
        # 提取 JSON 数据（百度热搜以 JSON 格式嵌入在 HTML 中）
        # 查找 "word":"xxx" 格式
        pattern = r'"word":"([^"]+)"'
        matches = re.findall(pattern, html)
        
        items = []
        seen = set()
        
        for i, word in enumerate(matches, 1):
            # 去重
            if word in seen:
                continue
            seen.add(word)
            
            # 排除娱乐/小说内容
            if any(kw in word for kw in ['小说', '电影', '电视剧', '综艺']):
                continue
            
            items.append({
                'rank': len(items) + 1,
                'title': word,
                'source': 'baidu',
                'category': 'general'
            })
            
            if len(items) >= 10:
                break
        
        if items:
            print(f"✅ 百度热搜获取成功（{len(items)} 条）")
        else:
            print("⚠️ 百度热搜未获取到数据")
        
        return items
            
    except Exception as e:
        print(f"❌ 百度热搜获取失败：{e}")
        return []

def get_36kr_hot():
    """获取 36 氪热榜"""
    try:
        # 36 氪热门列表 API
        url = "https://api.36kr.com/api/portal/list"
        params = {
            'portal_id': '123',  # 热门列表 ID
            'page': '1',
            'page_size': '10'
        }
        
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            items = []
            
            # 解析 36 氪数据
            articles = data.get('data', {}).get('items', [])
            for i, article in enumerate(articles[:10], 1):
                title = article.get('title', '')
                if title:
                    items.append({
                        'rank': i,
                        'title': title,
                        'source': '36kr',
                        'category': 'tech'
                    })
            
            if items:
                print(f"✅ 36 氪热榜获取成功（{len(items)} 条）")
            return items
        else:
            print(f"⚠️ 36 氪热榜获取失败：{response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 36 氪热榜获取失败：{e}")
        return []

def get_huxiu_hot():
    """获取虎嗅热文"""
    try:
        url = "https://www.huxiu.com/article/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            
            # 提取文章标题
            pattern = r'<a[^>]*class="article-title"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html)
            
            items = []
            for i, title in enumerate(matches[:10], 1):
                items.append({
                    'rank': i,
                    'title': title.strip(),
                    'source': 'huxiu',
                    'category': 'business'
                })
            
            if items:
                print(f"✅ 虎嗅热文获取成功（{len(items)} 条）")
            return items
        else:
            print(f"⚠️ 虎嗅热文获取失败：{response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 虎嗅热文获取失败：{e}")
        return []

def print_hot_list(items, title, emoji):
    """格式化输出热榜"""
    if not items:
        print(f"\n{emoji} {title} - 暂无数据")
        return
    
    print(f"\n{emoji} {title}")
    print("=" * 60)
    
    for item in items:
        rank = item.get('rank', '?')
        hot = item.get('hot', '')
        hot_tag = f" 🔥 {hot}" if hot else ""
        print(f"{rank:2d}. {item['title']}{hot_tag}")

def main():
    print("🔥 真实热榜 - 只从权威来源抓取")
    print(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 获取各平台热榜
    baidu_items = get_baidu_hot()
    kr_items = get_36kr_hot()
    huxiu_items = get_huxiu_hot()
    
    # 输出结果
    print_hot_list(baidu_items, "百度热搜 TOP 10", "📰")
    print_hot_list(kr_items, "36 氪热榜 TOP 10", "📊")
    print_hot_list(huxiu_items, "虎嗅热文 TOP 10", "💼")
    
    print("\n" + "=" * 60)
    print("✅ 数据来源：百度热搜、36 氪、虎嗅（权威来源）")
    print("❌ 已排除：微博、知乎、抖音、娱乐榜（数据不可靠）")

if __name__ == "__main__":
    main()
