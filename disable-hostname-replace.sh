#!/bin/bash
# 关闭节点域名替换功能（临时特性回滚脚本）
# 用法: bash /root/subconverter/disable-hostname-replace.sh

set -e

echo "[1/4] 停止并禁用 sub-proxy 服务..."
systemctl stop sub-proxy
systemctl disable sub-proxy
rm -f /etc/systemd/system/sub-proxy.service
systemctl daemon-reload

echo "[2/4] 恢复 Caddyfile（3002 -> 3000）..."
sed -i 's/reverse_proxy localhost:3002/reverse_proxy localhost:3000/g' /etc/caddy/Caddyfile

echo "[3/4] 重载 Caddy..."
caddy reload --config /etc/caddy/Caddyfile

echo "[4/4] 完成。Caddy 已直连 subconverter:3000，域名替换关闭。"
echo ""
echo "如需彻底清理，手动执行："
echo "  rm /root/subconverter/sub-proxy.py"
echo "  rm /root/subconverter/disable-hostname-replace.sh"
