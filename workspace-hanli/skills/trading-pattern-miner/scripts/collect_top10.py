#!/usr/bin/env python3
"""
使用浏览器自动化批量收集淘股吧选手数据
"""

import json
from pathlib import Path
from datetime import datetime

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# ============================================================
# Top 10 选手列表
# ============================================================

TOP_TRADERS = [
    {'rank': 1, 'name': '陈小炮', 'user_id': '13232170', 'score': 390073},
    {'rank': 2, 'name': '简单 6855', 'user_id': '7834779', 'score': 217191},
    {'rank': 3, 'name': '二池', 'user_id': '9435281', 'score': 162145, 'tags': ['24 凤凰半年赛冠军']},
    {'rank': 4, 'name': 'webqiang', 'user_id': '242875', 'score': 149505},
    {'rank': 5, 'name': '名字被你们', 'user_id': '3324313', 'score': 148962, 'tags': ['第二届屠龙杯冠军']},
    {'rank': 6, 'name': '请叫我小蟒夫', 'user_id': '2210094', 'score': 135642, 'tags': ['第 15 届百万杯季军']},
    {'rank': 7, 'name': '徐润发', 'user_id': '9418324', 'score': 109139},
    {'rank': 8, 'name': '陈药师', 'user_id': '8252860', 'score': 76384},
    {'rank': 9, 'name': 'A 股菜徐坤', 'user_id': '3320257', 'score': 75160},
    {'rank': 10, 'name': '平凡的世界 2008', 'user_id': '10690544', 'score': 74209},
]

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("淘股吧风云选手 TOP10 数据整理")
    print("=" * 70)
    print()
    
    output_data = {
        'collect_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': '淘股吧风云选手榜',
        'url': 'https://www.tgb.cn/new/nrnt/toPopularityBoard?type=SP',
        'traders': []
    }
    
    for trader in TOP_TRADERS:
        trader_data = {
            'rank': trader['rank'],
            'name': trader['name'],
            'user_id': trader['user_id'],
            'blog_url': f"https://www.tgb.cn/blog/{trader['user_id']}",
            'fengyun_score': trader['score'],
            'tags': trader.get('tags', []),
            'status': 'pending'  # pending/collected/failed
        }
        output_data['traders'].append(trader_data)
        
        print(f"[{trader['rank']:2d}] {trader['name']:15s} - 风云值：{trader['score']:6d} - ID: {trader['user_id']}")
    
    # 保存结果
    output_file = DATA_DIR / "top10_traders_basic.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 70)
    print(f"✅ 基础数据已保存：{output_file}")
    print(f"✅ 共 {len(output_data['traders'])} 个选手")
    print("=" * 70)
    print()
    print("下一步:")
    print("1. 逐个访问选手主页获取详细信息")
    print("2. 提取交易记录和比赛成绩")
    print("3. 分析交易模式")

if __name__ == "__main__":
    main()
