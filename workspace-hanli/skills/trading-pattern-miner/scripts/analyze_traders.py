#!/usr/bin/env python3
"""
批量收集选手详细数据 + 自动分析交易模式
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# ============================================================
# 配置
# ============================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "analysis"

OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# 加载数据
# ============================================================

def load_data():
    """加载已收集的选手数据"""
    with open(DATA_DIR / "all_famous_traders.json", 'r', encoding='utf-8') as f:
        return json.load(f)

# ============================================================
# 分析函数
# ============================================================

def analyze_trader_names(traders):
    """分析选手命名特点"""
    patterns = {
        '数字型': [],  # 如：简单 6855、小宝 1105
        '情绪型': [],  # 如：韭菜抄家、爆金币
        '目标型': [],  # 如：十万起家、平凡的世界
        '技术型': [],  # 如：趋势主升、超短
        '其他': []
    }
    
    for t in traders:
        name = t.get('name', '')
        if any(c.isdigit() for c in name):
            patterns['数字型'].append(name)
        elif '韭菜' in name or '爆' in name or '妖' in name:
            patterns['情绪型'].append(name)
        elif '万' in name or '目标' in name or '起' in name:
            patterns['目标型'].append(name)
        elif '趋势' in name or '超短' in name or '龙头' in name:
            patterns['技术型'].append(name)
        else:
            patterns['其他'].append(name)
    
    return patterns

def analyze_sources(traders):
    """分析选手来源分布"""
    sources = Counter([t.get('source', '未知') for t in traders])
    return dict(sources.most_common())

def generate_statistics(traders):
    """生成统计数据"""
    stats = {
        'total': len(traders),
        'with_id': sum(1 for t in traders if t.get('user_id')),
        'without_id': sum(1 for t in traders if not t.get('user_id')),
        'by_source': analyze_sources(traders),
        'name_patterns': analyze_trader_names(traders)
    }
    return stats

# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 70)
    print("淘股吧知名选手数据分析")
    print("=" * 70)
    print()
    
    # 加载数据
    data = load_data()
    traders = data['traders']
    
    print(f"加载 {len(traders)} 个选手数据...\n")
    
    # 生成统计
    stats = generate_statistics(traders)
    
    # 输出报告
    report = {
        'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'statistics': stats,
        'trader_list': traders
    }
    
    # 打印摘要
    print("=" * 70)
    print("📊 数据摘要")
    print("=" * 70)
    print(f"\n总选手数：{stats['total']} 人")
    print(f"有 ID 的：{stats['with_id']} 人")
    print(f"无 ID 的：{stats['without_id']} 人")
    
    print("\n来源分布:")
    for source, count in stats['by_source'].items():
        print(f"  {source}: {count} 人")
    
    print("\n命名特点:")
    for pattern, names in stats['name_patterns'].items():
        if names:
            print(f"  {pattern}: {len(names)} 人")
            print(f"    例：{', '.join(names[:3])}")
    
    # 保存报告
    output_file = OUTPUT_DIR / "trader_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 70)
    print(f"✅ 分析报告已保存：{output_file}")
    print("=" * 70)
    
    # 生成 Markdown 报告
    generate_markdown_report(report)

def generate_markdown_report(report):
    """生成 Markdown 格式报告"""
    
    md = f"""# 淘股吧知名选手数据分析报告

**生成时间**: {report['report_date']}  
**数据来源**: 淘股吧风云榜 + 知名游资

---

## 📊 总体统计

| 指标 | 数值 |
|------|------|
| 总选手数 | {report['statistics']['total']} 人 |
| 有 ID 可访问 | {report['statistics']['with_id']} 人 |
| 待搜索 ID | {report['statistics']['without_id']} 人 |

---

## 📈 来源分布

| 来源 | 人数 | 占比 |
|------|------|------|
"""
    
    stats = report['statistics']
    total = stats['total']
    
    for source, count in stats['by_source'].items():
        pct = round(count / total * 100, 1)
        md += f"| {source} | {count} | {pct}% |\n"
    
    md += """
---

## 🏷️ 命名特点分析

### 数字型 (使用数字 ID)
特点：直接用数字或包含数字，便于记忆
"""
    
    for name in stats['name_patterns']['数字型'][:5]:
        md += f"- {name}\n"
    
    md += """
### 情绪型 (表达情感/状态)
特点：表达炒股情绪，如韭菜、爆仓等
"""
    
    for name in stats['name_patterns']['情绪型'][:5]:
        md += f"- {name}\n"
    
    md += """
### 目标型 (表达目标/愿景)
特点：表达投资目标或人生理想
"""
    
    for name in stats['name_patterns']['目标型'][:5]:
        md += f"- {name}\n"
    
    md += """
### 技术型 (表达交易风格)
特点：直接表明交易模式，如超短、趋势等
"""
    
    for name in stats['name_patterns']['技术型'][:5]:
        md += f"- {name}\n"
    
    md += f"""
---

## 📋 完整选手名单

### 风云榜 TOP10

| 排名 | 选手 | ID | 来源 |
|------|------|-----|------|
"""
    
    # 添加风云榜选手
    for t in report['trader_list']:
        if '风云榜' in t.get('source', ''):
            md += f"| {t.get('index', '-')} | {t.get('name', '-')} | {t.get('user_id', '-')} | {t.get('source', '-')} |\n"
    
    md += """
### 知名游资

| 选手 | ID | 来源 |
|------|-----|------|
"""
    
    for t in report['trader_list']:
        if '知名游资' in t.get('source', ''):
            md += f"| {t.get('name', '-')} | {t.get('user_id', '-')} | {t.get('source', '-')} |\n"
    
    md += """
### 活跃选手

| 选手 | ID | 来源 |
|------|-----|------|
"""
    
    for t in report['trader_list']:
        if '活跃选手' in t.get('source', ''):
            md += f"| {t.get('name', '-')} | {t.get('user_id', '-')} | {t.get('source', '-')} |\n"
    
    md += f"""
---

## 🎯 下一步

1. **补充缺失 ID** - 搜索"故事漂泊记/水哥炒股/太牛啦"
2. **收集言论** - 批量访问选手主页，提取发帖内容
3. **模式分析** - 从言论中提取交易模式
4. **回测验证** - 用历史数据验证模式有效性

---

**报告生成**: 淘股吧交易模式挖掘工具  
**下次更新**: 收集更多详细数据后
"""
    
    # 保存 Markdown 报告
    md_file = OUTPUT_DIR / "trader_analysis.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f"✅ Markdown 报告已保存：{md_file}")

if __name__ == "__main__":
    main()
