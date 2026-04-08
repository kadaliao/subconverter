#!/bin/bash

# Subconverter 缓存清理脚本
# 用途: 清除 subconverter Docker 容器的缓存，确保规则更新后立即生效

CONTAINER_NAME="subconverter"
CACHE_PATH="/base/cache"

echo "========================================"
echo "  Subconverter 缓存清理工具"
echo "========================================"
echo ""

# 检查容器是否运行
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "错误: $CONTAINER_NAME 容器未运行"
    exit 1
fi

# 显示清理前的缓存文件数量
CACHE_COUNT=$(docker exec $CONTAINER_NAME sh -c "ls $CACHE_PATH 2>/dev/null | wc -l")
echo "清理前缓存文件数量: $CACHE_COUNT"

# 清除缓存
echo "正在清除缓存..."
docker exec $CONTAINER_NAME sh -c "cd $CACHE_PATH && rm -f *"

# 验证清理结果
CACHE_COUNT_AFTER=$(docker exec $CONTAINER_NAME sh -c "ls $CACHE_PATH 2>/dev/null | wc -l")
echo "清理后缓存文件数量: $CACHE_COUNT_AFTER"

if [ "$CACHE_COUNT_AFTER" -eq 0 ]; then
    echo ""
    echo "缓存清理成功!"
    echo "提示: 现在可以重新获取订阅，新规则将立即生效"
else
    echo ""
    echo "警告: 可能还有部分缓存文件未清除"
fi

echo ""
echo "========================================"
