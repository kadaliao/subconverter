# Subconverter 自定义配置

基于 [subconverter](https://github.com/tindy2013/subconverter) 的订阅转换服务，使用白名单代理模式和自定义规则分组。

## 服务地址

- https://sub.cclsp.top
- https://sub.liaoxingyi.com

## 目录结构

```
web/                  # Caddy 静态文件根目录
├── index.html        # 前端页面
├── config.ini        # 外部配置（规则集 + 代理分组）
└── rules/            # 自定义规则文件
config/               # Docker 挂载到 subconverter 容器
├── all_base.tpl      # Clash 基础模板（含 ipv6: false）
├── groups.toml       # 默认代理分组
└── rulesets.toml     # 默认规则集
docker-compose.yml    # 容器编排
```

## 代理分组

| 分组 | 说明 |
|------|------|
| 🔰 节点选择 | 手动选择节点或自动选择 |
| ♻️ 自动选择 | url-test 自动测速选优 |
| 🌏 ChatGPT/Claude | AI 平台专用，优先美日节点 |
| 🎯 全球直连 | DIRECT |
| 🐟 漏网之鱼 | 未匹配规则的流量 |

## 规则优先级

1. 自定义直连 (direct.list)
2. AI 平台 (ai-platform.list)
3. 白名单直连 - sr top500 (sr-direct.list)
4. 社交媒体 (social.list) → 代理
5. 开发工具 (devtools.list) → 代理
6. 游戏 (gaming.list) → 代理
7. 通用代理 (proxy-general.list) → 代理
8. GEOIP CN → 直连
9. FINAL → 漏网之鱼

## 部署

```bash
# 启动
docker-compose up -d

# 查看状态
docker-compose ps

# 重启（配置修改后）
docker-compose restart
```

Caddy 反代配置位于 `/etc/caddy/Caddyfile`，静态文件根目录指向本仓库的 `web/`。
