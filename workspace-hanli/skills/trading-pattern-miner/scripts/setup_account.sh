#!/bin/bash
# 淘股吧账号配置脚本

echo "======================================"
echo "淘股吧账号配置"
echo "======================================"
echo ""
echo "请输入你的淘股吧账号信息："
echo ""

# 读取用户名
read -p "用户名/手机号： " username

# 读取密码（隐藏输入）
read -sp "密码： " password
echo ""
echo ""

# 添加到 ~/.zshrc
cat >> ~/.zshrc << EOF

# 淘股吧账号配置 (交易模式挖掘技能) - $(date +%Y-%m-%d)
export TAOGUBA_USERNAME="$username"
export TAOGUBA_PASSWORD="$password"
EOF

echo "✅ 账号已配置到 ~/.zshrc"
echo ""
echo "运行以下命令生效："
echo "  source ~/.zshrc"
echo ""
echo "然后测试登录："
echo "  cd ~/.openclaw/workspace-hanli/skills/trading-pattern-miner"
echo "  python3 scripts/test_login.py"
