#!/usr/bin/env python3
"""
Reverse proxy for subconverter that replaces node hostnames with a fixed domain.
Handles Clash YAML, Sing-box JSON, and base64-encoded subscription formats.
"""
import re
import base64
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error

BACKEND = 'http://127.0.0.1:3000'
REPLACE_DOMAIN = 'h4.colacokeaa.com'

# Matches server field in Clash YAML (block and flow styles) and JSON
CLASH_YAML_PATTERN = re.compile(r'((?:^|\{|\s)server:\s)([^,\}\n\r\s]+)', re.MULTILINE)
JSON_SERVER_PATTERN = re.compile(r'("server"\s*:\s*")([^"]+)(")')


def process_vmess_line(line):
    try:
        encoded = line[8:]
        padding = 4 - len(encoded) % 4
        obj = json.loads(base64.b64decode(encoded + '=' * padding).decode('utf-8'))
        obj['add'] = REPLACE_DOMAIN
        return 'vmess://' + base64.b64encode(json.dumps(obj, ensure_ascii=False).encode()).decode()
    except Exception:
        return line


def process_trojan_line(line):
    try:
        # trojan://password@host:port[?params]#remark
        rest = line[9:]
        at_idx = rest.rfind('@')
        if at_idx == -1:
            return line
        credentials = rest[:at_idx]
        after = rest[at_idx + 1:]
        # after = host:port[?params][#remark]
        colon_idx = after.find(':')
        if colon_idx == -1:
            return line
        port_and_rest = after[colon_idx + 1:]
        return 'trojan://' + credentials + '@' + REPLACE_DOMAIN + ':' + port_and_rest
    except Exception:
        return line


def process_ss_sip002_line(line):
    try:
        # ss://base64(method:password)@host:port[#remark]
        rest = line[5:]
        at_idx = rest.rfind('@')
        if at_idx == -1:
            return line
        credentials = rest[:at_idx]
        after = rest[at_idx + 1:]
        colon_idx = after.find(':')
        if colon_idx == -1:
            return line
        port_and_rest = after[colon_idx + 1:]
        return 'ss://' + credentials + '@' + REPLACE_DOMAIN + ':' + port_and_rest
    except Exception:
        return line


def process_base64_sub(content_bytes):
    try:
        padded = content_bytes + b'=' * (4 - len(content_bytes) % 4)
        decoded = base64.b64decode(padded).decode('utf-8')
        lines = decoded.splitlines()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('vmess://'):
                stripped = process_vmess_line(stripped)
            elif stripped.startswith('trojan://'):
                stripped = process_trojan_line(stripped)
            elif stripped.startswith('ss://') and '@' in stripped:
                stripped = process_ss_sip002_line(stripped)
            new_lines.append(stripped)
        new_decoded = '\n'.join(new_lines)
        return base64.b64encode(new_decoded.encode('utf-8'))
    except Exception:
        return None


def process_response(content_bytes):
    try:
        text = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return content_bytes

    # Clash YAML / sing-box JSON — contains known keywords
    if 'proxies:' in text or 'outbounds' in text or 'inbounds' in text:
        text = CLASH_YAML_PATTERN.sub(lambda m: m.group(1) + REPLACE_DOMAIN, text)
        text = JSON_SERVER_PATTERN.sub(lambda m: m.group(1) + REPLACE_DOMAIN + m.group(3), text)
        return text.encode('utf-8')

    # Try base64 encoded subscription (V2Ray / SS)
    stripped = text.strip()
    if stripped and '\n' not in stripped[:100]:  # Likely base64 if no early newlines
        result = process_base64_sub(stripped.encode('utf-8'))
        if result:
            return result

    return content_bytes


class SubProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = BACKEND + self.path
        req = urllib.request.Request(url)
        if 'User-Agent' in self.headers:
            req.add_header('User-Agent', self.headers['User-Agent'])
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                modified = process_response(raw)
                self.send_response(200)
                for k, v in resp.headers.items():
                    if k.lower() in ('content-encoding', 'content-length',
                                     'transfer-encoding', 'connection'):
                        continue
                    self.send_header(k, v)
                self.send_header('Content-Length', str(len(modified)))
                self.end_headers()
                self.wfile.write(modified)
        except urllib.error.HTTPError as e:
            self.send_error(e.code, str(e.reason))
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, fmt, *args):
        sys.stderr.write('%s - - [%s] %s\n' % (self.address_string(),
                         self.log_date_time_string(), fmt % args))


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 3002), SubProxyHandler)
    print('Sub-proxy listening on 127.0.0.1:3002 -> localhost:3000', flush=True)
    server.serve_forever()
