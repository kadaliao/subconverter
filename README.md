# 订阅转换服务

面向 Clash / Mihomo 内核客户端的订阅转换服务。用户填入自己的订阅链接，生成带自定义规则分组的 Clash 配置 URL。

支持 anytls、ss、vmess 等协议，采用白名单代理模式。

## 服务地址

- https://sub.cclsp.top
- https://sub.liaoxingyi.com

## 使用方法

1. 打开服务地址
2. 粘贴自己的订阅链接
3. 点击「生成配置链接」
4. 将生成的链接填入 Clash Verge / mihomo-party / Clash Party 等客户端

生成的链接格式：`https://sub.cclsp.top/convert?url=<你的订阅>`

## 架构

```
用户订阅链接
    ↓
GET /convert?url=<encoded>      # convert.py，端口 3003
    ↓
返回完整 Clash YAML：
  proxy-providers → 用户原始订阅（客户端直接拉取，支持 anytls）
  rule-providers  → 本服务的规则文件（/rules/*.list）
  proxy-groups    → 自定义分组逻辑
```

节点由客户端从用户的原始订阅直接获取，服务器不存储任何用户数据。

## 代理分组

| 分组 | 类型 | 说明 |
|------|------|------|
| 🔰 节点选择 | select | 手动选节点，默认走自动选择 |
| ♻️ 自动选择 | url-test | 自动测速选最优节点 |
| 🌏 ChatGPT/Claude | select | 过滤美国/日本节点 |
| 🎯 全球直连 | select | DIRECT |
| 🐟 漏网之鱼 | select | 未命中规则的流量 |

## 规则优先级

1. 自定义直连 `direct.list`
2. AI 平台 `ai-platform.list` → ChatGPT/Claude 分组
3. 白名单直连 `sr-direct.list`（sr top500 可直连站点）
4. 社交媒体 `social.list` → 代理
5. 开发工具 `devtools.list` → 代理
6. 游戏 `gaming.list` → 代理
7. 通用代理 `proxy-general.list` → 代理
8. GEOIP CN → 直连
9. MATCH → 漏网之鱼

## 目录结构

```
convert.py            # 订阅转换服务（端口 3003，systemd: sub-convert）
web/
├── index.html        # 前端页面
└── rules/            # 自定义规则文件（*.list）
config/               # sub-store Docker 挂载目录
├── all_base.tpl      # Clash 基础模板
├── groups.toml       # 代理分组模板
└── rulesets.toml     # 规则集模板
docker-compose.yml    # sub-store 容器（端口 3002，节点管理/预览）
Caddyfile             # Caddy 反代配置参考
```

## 部署

### 转换服务（convert.py）

systemd 服务文件位于 `/etc/systemd/system/sub-convert.service`：

```bash
systemctl enable sub-convert
systemctl start sub-convert
systemctl status sub-convert
```

### sub-store（节点管理，可选）

```bash
docker-compose up -d
docker-compose ps
```

管理界面通过 `/sub-store-api/` 路径访问，不对外暴露独立端口。

### Caddy

参考 `Caddyfile`，将 `<your-domain>` 替换为实际域名后合并到 `/etc/caddy/Caddyfile`：

```bash
caddy reload --config /etc/caddy/Caddyfile
```
