#!/bin/bash
# mx_selfselect 配置脚本

echo "🔑 mx_selfselect - 妙想自选股管理 API Key 配置"
echo ""
echo "注意：mx_selfselect 与其他妙想技能共用同一个 API Key"
echo ""
echo "请选择配置方式:"
echo "1. 直接输入 API Key（保存到 .env 文件）"
echo "2. 手动编辑 .env 文件"
echo "3. 使用环境变量（临时）"
echo ""
read -p "请选择 (1/2/3): " choice

case $choice in
    1)
        read -p "请输入 API Key: " apikey
        if [ -z "$apikey" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        echo "MX_APIKEY=$apikey" > .env
        echo "✅ API Key 已保存到 .env 文件"
        echo ""
        echo "🔍 测试连接..."
        python3 scripts/mx_selfselect.py --test
        ;;
    2)
        echo "请编辑 .env 文件，添加:"
        echo "MX_APIKEY=your_api_key_here"
        echo ""
        echo "文件位置：$(pwd)/.env"
        ;;
    3)
        read -p "请输入 API Key: " apikey
        export MX_APIKEY=$apikey
        echo "✅ API Key 已设置（当前会话有效）"
        echo ""
        echo "🔍 测试连接..."
        python3 scripts/mx_selfselect.py --test
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
