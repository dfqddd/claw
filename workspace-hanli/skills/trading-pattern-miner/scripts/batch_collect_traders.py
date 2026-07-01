#!/usr/bin/env python3
"""
淘股吧风云选手数据批量爬取
使用 Cookie 自动登录，高效批量收集选手数据
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
        raise Exception("未找到 Cookie 文件，请先登录并保存 Cookie")
    
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

def get_fengyun_ranking(page=1):
    """获取风云选手排行榜"""
    url = "https://www.tgb.cn/new/nrnt/toPopularityBoard?type=SP"
    
    cookie_str = "; ".join([f"{k}={v}" for k, v in load_cookies().items()])
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cookie': cookie_str,
        'Referer': 'https://www.tgb.cn/',
    }
    
    params = {'page': page}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        traders = []
        
        # 查找选手列表
        # 根据页面结构调整 selector
        for item in soup.select('[ref*="e"]'):
            text = item.get_text(strip=True)
            if text and any(c.isdigit() for c in text) and len(text) < 50:
                # 可能是选手信息
                traders.append({
                    'name': text,
                    'raw': str(item)
                })
        
        return traders
    
    except Exception as e:
        print(f"❌ 爬取失败：{e}")
        return []

def get_trader_profile(user_id):
    """获取选手详细信息"""
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
            'tags': []
        }
        
        # 提取姓名
        h1 = soup.find('h1')
        if h1:
            profile['name'] = h1.get_text(strip=True).replace('的博客', '')
        
        # 提取粉丝数
        for item in soup.select('[ref*="e"]'):
            text = item.get_text(strip=True)
            if '粉丝' in text:
                profile['fans'] = int(''.join(filter(str.isdigit, text)))
            elif '关注' in text and '粉丝' not in text:
                profile['follow'] = int(''.join(filter(str.isdigit, text)))
        
        # 提取简介
        intro = soup.find(string=lambda t: '保持审美' in t if t else False)
        if intro:
            profile['bio'] = intro.strip()
        
        # 提取 IP 属地
        for item in soup.select('[ref*="e"]'):
            text = item.get_text(strip=True)
            if 'IP 属地' in text:
                profile['ip_location'] = text.replace('IP 属地:', '').strip()
        
        return profile
    
    except Exception as e:
        print(f"❌ 获取选手 {user_id} 失败：{e}")
        return None

def get_trader_competitions(user_id):
    """获取选手比赛记录"""
    url = f"https://www.tgb.cn/user/blog/myspmath?userID={user_id}"
    
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
        
        competitions = []
        
        # 提取比赛记录（需要根据实际页面结构调整）
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 5:
                    competitions.append({
                        'name': cells[0].get_text(strip=True),
                        'rank': cells[1].get_text(strip=True) if len(cells) > 1 else '',
                        'return': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                        'days': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                    })
        
        return competitions
    
    except Exception as e:
        print(f"❌ 获取比赛记录失败：{e}")
        return []

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("淘股吧风云选手数据批量爬取")
    print("=" * 70)
    print()
    
    # Top 10 选手 ID（从排行榜获取）
    top_traders = [
        {'rank': 1, 'user_id': '13232170', 'name': '陈小炮'},
        {'rank': 2, 'user_id': '7834779', 'name': '简单 6855'},
        {'rank': 3, 'user_id': '9435281', 'name': '二池'},
        {'rank': 4, 'user_id': '242875', 'name': 'webqiang'},
        {'rank': 5, 'user_id': '3324313', 'name': '名字被你们'},
        {'rank': 6, 'user_id': '2210094', 'name': '请叫我小蟒夫'},
        {'rank': 7, 'user_id': '9418324', 'name': '徐润发'},
        {'rank': 8, 'user_id': '8252860', 'name': '陈药师'},
        {'rank': 9, 'user_id': '3320257', 'name': 'A 股菜徐坤'},
        {'rank': 10, 'user_id': '10690544', 'name': '平凡的世界 2008'},
    ]
    
    all_data = {
        'collect_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': '淘股吧风云选手榜',
        'traders': []
    }
    
    print(f"开始收集 {len(top_traders)} 个选手数据...\n")
    
    for i, trader in enumerate(top_traders, 1):
        print(f"[{i}/{len(top_traders)}] 收集：{trader['name']} (ID: {trader['user_id']})")
        
        # 获取详细信息
        profile = get_trader_profile(trader['user_id'])
        
        if profile:
            trader_data = {
                'rank': trader['rank'],
                **profile
            }
            
            # 获取比赛记录
            competitions = get_trader_competitions(trader['user_id'])
            if competitions:
                trader_data['competitions'] = competitions
            
            all_data['traders'].append(trader_data)
            print(f"  ✅ 粉丝：{profile.get('fans', 0)}, 简介：{profile.get('bio', '')[:20]}")
        else:
            print(f"  ❌ 获取失败")
        
        # 避免请求过快
        time.sleep(1)
        
        print()
    
    # 保存结果
    output_file = DATA_DIR / "fengyun_top10_full.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✅ 收集完成！")
    print(f"✅ 保存至：{output_file}")
    print(f"✅ 成功：{len(all_data['traders'])}/{len(top_traders)}")
    print("=" * 70)

if __name__ == "__main__":
    main()
