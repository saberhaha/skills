#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NSQ 消息发送脚本 - 通过 NSQ HTTP API 直接发送消息"""

import argparse
import json
import subprocess
import sys

try:
    from urllib import quote as url_quote
except ImportError:
    from urllib.parse import quote as url_quote

# 默认 NSQ 地址
DEFAULT_ADDRESS = "finbj2-qa-nsq6"
DEFAULT_PORT = "4151"


def main():
    parser = argparse.ArgumentParser(description="NSQ 消息发送 - 直接通过 HTTP API 发送")
    parser.add_argument("--topic", required=True, help="NSQ 消息 Topic")
    parser.add_argument("--sc", default="", help="SC 持续集成环境标识（如 prj0089187），可为空")
    parser.add_argument("--msg", required=True, help="消息体，JSON 字符串")
    parser.add_argument("--address", default=DEFAULT_ADDRESS, help="NSQ 地址（默认 %s）" % DEFAULT_ADDRESS)
    parser.add_argument("--port", default=DEFAULT_PORT, help="NSQ 端口（默认 %s）" % DEFAULT_PORT)
    args = parser.parse_args()

    # 校验 msg 是合法 JSON
    try:
        json.loads(args.msg)
    except (ValueError, TypeError):
        print("错误: --msg 必须是合法的 JSON 字符串", file=sys.stderr)
        sys.exit(2)

    # 构造 URL
    base_url = "http://%s:%s" % (args.address, args.port)
    if args.sc:
        ext_json = json.dumps({"##client_dispatch_tag": args.sc})
        ext_encoded = url_quote(ext_json)
        url = "%s/pub_ext?topic=%s&ext=%s" % (base_url, args.topic, ext_encoded)
    else:
        url = "%s/pub?topic=%s" % (base_url, args.topic)

    # 执行 curl
    cmd = [
        "curl", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-H", "cache-control: no-cache",
        "-d", args.msg
    ]

    print(">>> 发送 NSQ 消息")
    print("    Topic:   %s" % args.topic)
    if args.sc:
        print("    SC:      %s" % args.sc)
    print("    Address: %s:%s" % (args.address, args.port))
    print("    Body:    %s" % args.msg)
    print("")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    if result.returncode == 0:
        print("✅ 发送成功")
        if result.stdout.strip():
            print("   响应: %s" % result.stdout.strip())
    else:
        print("❌ 发送失败", file=sys.stderr)
        if result.stderr.strip():
            print("   错误: %s" % result.stderr.strip(), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
