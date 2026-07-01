#!/usr/bin/env python3
"""
批量收集淘股吧知名选手数据
包含风云榜 + 聪哥提到的知名选手
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
# 知名选手列表 (风云榜 + 聪哥提到)
# ============================================================

TRADERS = [
    # ===== 风云榜 TOP10 =====
    {'name': '陈小炮', 'user_id': '13232170', 'source': '风云榜#1'},
    {'name': '简单 6855', 'user_id': '7834779', 'source': '风云榜#2'},
    {'name': '二池', 'user_id': '9435281', 'source': '风云榜#3'},
    {'name': 'webqiang', 'user_id': '242875', 'source': '风云榜#4'},
    {'name': '名字被你们', 'user_id': '3324313', 'source': '风云榜#5'},
    {'name': '请叫我小蟒夫', 'user_id': '2210094', 'source': '风云榜#6'},
    {'name': '徐润发', 'user_id': '9418324', 'source': '风云榜#7'},
    {'name': '陈药师', 'user_id': '8252860', 'source': '风云榜#8'},
    {'name': 'A 股菜徐坤', 'user_id': '3320257', 'source': '风云榜#9'},
    {'name': '平凡的世界 2008', 'user_id': '10690544', 'source': '风云榜#10'},
    
    # ===== 聪哥提到的知名选手 =====
    {'name': 'a 拉神灯', 'user_id': '5727139', 'source': '聪哥推荐'},
    {'name': '故事漂泊记', 'user_id': '', 'source': '聪哥推荐'},
    {'name': '水哥炒股', 'user_id': '', 'source': '聪哥推荐'},
    {'name': '太牛啦', 'user_id': '', 'source': '聪哥推荐'},
    
    # ===== 其他知名选手 (从页面看到) =====
    {'name': '作手新一', 'user_id': '827264', 'source': '知名游资'},
    {'name': '炒股养家', 'user_id': '134434', 'source': '知名游资'},
    {'name': '赵老哥', 'user_id': '154034', 'source': '知名游资'},
    {'name': '龙飞虎', 'user_id': '103830', 'source': '知名游资'},
    {'name': '职业炒手', 'user_id': '4223', 'source': '知名游资'},
    {'name': '十万起家', 'user_id': '138280', 'source': '知名游资'},
    
    # ===== 页面看到的活跃选手 =====
    {'name': '大师兄擒妖', 'user_id': '9767895', 'source': '活跃选手'},
    {'name': '退学炒 A 股', 'user_id': '9767895', 'source': '活跃选手'},
    {'name': '涅槃重生 2018', 'user_id': '2888425', 'source': '活跃选手'},
    {'name': '小土堆爆金币', 'user_id': '9259508', 'source': '活跃选手'},
    {'name': '东北玄', 'user_id': '8580229', 'source': '活跃选手'},
    {'name': '星辰趋势主升', 'user_id': '8186648', 'source': '活跃选手'},
    {'name': '短狙作手', 'user_id': '8423616', 'source': '活跃选手'},
    {'name': '玫瑰超短', 'user_id': '11668853', 'source': '活跃选手'},
    {'name': '海擒涨停王', 'user_id': '12695061', 'source': '活跃选手'},
    {'name': '小宝 1105', 'user_id': '9239701', 'source': '活跃选手'},
    {'name': 'jl 韭菜抄家', 'user_id': '7737030', 'source': '活跃选手'},
    {'name': '米开朗基瑞', 'user_id': '11056656', 'source': '活跃选手'},
]

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("淘股吧知名选手数据批量收集")
    print("=" * 70)
    print()
    
    output_data = {
        'collect_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': '淘股吧',
        'total': len(TRADERS),
        'traders': []
    }
    
    for i, trader in enumerate(TRADERS, 1):
        trader_data = {
            'index': i,
            'name': trader['name'],
            'user_id': trader.get('user_id', ''),
            'blog_url': f"https://www.tgb.cn/blog/{trader.get('user_id', '')}" if trader.get('user_id') else '',
            'source': trader['source'],
            'status': 'pending'
        }
        output_data['traders'].append(trader_data)
        
        user_id = trader.get('user_id', 'N/A')
        print(f"[{i:2d}/{len(TRADERS)}] {trader['name']:15s} - ID: {user_id:10s} - {trader['source']}")
    
    # 保存结果
    output_file = DATA_DIR / "all_famous_traders.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 70)
    print(f"✅ 列表已保存：{output_file}")
    print(f"✅ 共 {len(output_data['traders'])} 个选手")
    print("=" * 70)
    print()
    print("分类统计:")
    
    # 按来源统计
    from collections import Counter
    sources = Counter([t['source'] for t in output_data['traders']])
    for source, count in sources.most_common():
        print(f"  {source}: {count} 人")

if __name__ == "__main__":
    main()
