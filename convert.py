#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import re

BASE = "https://sub.cclsp.top"

TEMPLATE = """port: 7890
socks-port: 7891
allow-lan: true
mode: Rule
log-level: info
external-controller: 127.0.0.1:9090
ipv6: false

proxy-providers:
  user-sub:
    type: http
    url: "{user_url}"
    interval: 3600
    proxy: DIRECT
    health-check:
      enable: true
      url: http://www.gstatic.com/generate_204
      interval: 300

proxy-groups:
  - name: \U0001f530 节点选择
    type: select
    use:
      - user-sub
    filter: "^(?!.*(流量|时间|重置|到期|剩余|过期|官网|套餐|订阅|地址|网址|更新|EXPIRE|RESET|Traffic|Remain|Website|URL|Subscription)).*$"
    proxies:
      - ♻️ 自动选择
      - 🎯 全球直连

  - name: ♻️ 自动选择
    type: url-test
    use:
      - user-sub
    filter: "^(?!.*(流量|时间|重置|到期|剩余|过期|官网|套餐|订阅|地址|网址|更新|EXPIRE|RESET|Traffic|Remain|Website|URL|Subscription)).*$"
    url: http://www.gstatic.com/generate_204
    interval: 300
    tolerance: 50

  - name: 🌏 ChatGPT/Claude
    type: select
    use:
      - user-sub
    filter: "美|US|USA|United States|America|日|JP|Japan"
    proxies:
      - 🔰 节点选择
      - ♻️ 自动选择

  - name: 🎯 全球直连
    type: select
    proxies:
      - DIRECT

  - name: 🐟 漏网之鱼
    type: select
    proxies:
      - 🔰 节点选择
      - 🎯 全球直连
      - ♻️ 自动选择

rule-providers:
  direct-custom:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/direct.list"
    path: ./rules/direct.list
    interval: 86400
  ai-platform:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/ai-platform.list"
    path: ./rules/ai-platform.list
    interval: 86400
  sr-direct:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/sr-direct.list"
    path: ./rules/sr-direct.list
    interval: 86400
  social:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/social.list"
    path: ./rules/social.list
    interval: 86400
  devtools:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/devtools.list"
    path: ./rules/devtools.list
    interval: 86400
  gaming:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/gaming.list"
    path: ./rules/gaming.list
    interval: 86400
  proxy-general:
    type: http
    behavior: classical
    format: text
    url: "{base}/rules/proxy-general.list"
    path: ./rules/proxy-general.list
    interval: 86400

rules:
  - RULE-SET,direct-custom,🎯 全球直连
  - RULE-SET,ai-platform,🌏 ChatGPT/Claude
  - RULE-SET,sr-direct,🎯 全球直连
  - RULE-SET,social,🔰 节点选择
  - RULE-SET,devtools,🔰 节点选择
  - RULE-SET,gaming,🔰 节点选择
  - RULE-SET,proxy-general,🔰 节点选择
  - GEOIP,CN,🎯 全球直连
  - MATCH,🐟 漏网之鱼
"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # quiet logging

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/convert":
            self.send_error(404)
            return

        params = parse_qs(parsed.query)
        user_url = params.get("url", [""])[0]
        if user_url:
            user_url = unquote(user_url)

        if not user_url or not re.match(r"^https?://", user_url):
            self.send_error(400, "Missing or invalid url parameter")
            return

        # Escape double quotes in URL for YAML safety
        safe_url = user_url.replace('"', '%22')
        content = TEMPLATE.replace("{user_url}", safe_url).replace("{base}", BASE)
        # Fix emoji in proxy group name (unicode escape workaround)
        content = content.replace("\\U0001f530", "🔰")

        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 3003), Handler)
    print("Listening on 127.0.0.1:3003")
    server.serve_forever()
