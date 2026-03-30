#!/usr/bin/env python3
"""Token 管理器 - 与其他 zan-tools skill 共享 OPS_JWT_TOKEN。

Token 统一存储在 ~/.config/zan-tools/token.json，格式：
  {"OPS_JWT_TOKEN": "eyJ...", "username": "liuzhiyu"}
"""

import base64
import json
import os
import time
from pathlib import Path


class TokenManager:
    """管理 OPS_JWT_TOKEN，与其他 zan-tools skill 共享存储。"""

    TOKEN_FILE = Path.home() / ".config" / "zan-tools" / "token.json"

    def __init__(self):
        self._token_data = self._load_token()

    def _load_token(self):
        """从统一的 zan-tools 配置文件加载 token。"""
        if not self.TOKEN_FILE.exists():
            return None

        try:
            with open(self.TOKEN_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

        if not isinstance(data, dict):
            return None

        token_value = data.get("OPS_JWT_TOKEN")
        if not isinstance(token_value, str) or not token_value:
            return None

        return {
            "value": token_value,
            "username": data.get("username"),
        }

    def _get_token_from_env(self):
        """从环境变量获取 token。"""
        for var_name in ("SKYNET_COOKIE", "SKYNET_TOKEN"):
            value = os.getenv(var_name)
            if value:
                return value
        return None

    def _is_jwt_expired(self, token):
        """通过解析 JWT payload 中的 exp 字段判断是否过期。"""
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return False
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            decoded = json.loads(base64.b64decode(payload))
            exp = decoded.get("exp")
            if exp and int(time.time()) > int(exp):
                return True
        except Exception:
            pass
        return False

    def _get_jwt_exp(self, token):
        """从 JWT payload 中提取 exp 字段。"""
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return None
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            decoded = json.loads(base64.b64decode(payload))
            return decoded.get("exp")
        except Exception:
            return None

    def _parse_jwt_username(self, token):
        """从 JWT payload 解析 username。"""
        try:
            parts = token.split(".")
            if len(parts) >= 2:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += "=" * padding
                decoded = json.loads(base64.b64decode(payload))
                return decoded.get("username")
        except Exception:
            pass
        return None

    def get_token(self, force_refresh=False):
        """获取当前有效 token。

        每次调用重新读取文件，以便获取其他 skill 更新的 token。
        """
        if not force_refresh and self._token_data:
            token = self._token_data["value"]
            if not self._is_jwt_expired(token):
                return token

        # 重新从文件加载（其他 skill 可能已更新 token）
        self._token_data = self._load_token()
        if self._token_data:
            token = self._token_data["value"]
            if not self._is_jwt_expired(token):
                return token

        # 环境变量兜底
        env_token = self._get_token_from_env()
        if env_token:
            return env_token

        return None

    def set_token(self, token):
        """设置 token（写入统一的 zan-tools 格式）。"""
        username = self._parse_jwt_username(token)

        data = {}
        # 先读后写，保留文件中已有的其他字段
        if self.TOKEN_FILE.exists():
            try:
                with open(self.TOKEN_FILE, "r") as f:
                    existing = json.load(f)
                if isinstance(existing, dict):
                    data = existing
            except Exception:
                pass

        data["OPS_JWT_TOKEN"] = token
        if username:
            data["username"] = username

        self.TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.TOKEN_FILE, "w") as f:
            json.dump(data, f, indent=2)

        self._token_data = {"value": token, "username": username}

    def list_tokens(self):
        """返回当前 token 的摘要信息。"""
        if not self._token_data:
            return {}

        token = self._token_data["value"]
        exp = self._get_jwt_exp(token)

        if exp:
            remaining = int(exp) - int(time.time())
            if remaining < 0:
                expiry_desc = "已过期"
            elif remaining < 3600:
                expiry_desc = f"{remaining // 60} 分钟后过期"
            else:
                expiry_desc = f"{remaining // 3600} 小时后过期"
            is_expired = remaining < 0
        else:
            expiry_desc = "无法判断（非JWT格式）"
            is_expired = False

        return {
            "username": self._token_data.get("username"),
            "expires_at": exp,
            "is_expired": is_expired,
            "expiry_desc": expiry_desc,
            "source": str(self.TOKEN_FILE),
        }

    def clear_tokens(self):
        """清空内存中的 token 缓存（不删除共享文件）。"""
        self._token_data = None

    def validate_token(self):
        """通过 apps 接口验证当前 token 是否有效。"""
        token = self.get_token()
        if not token:
            return False, "Token 未设置"

        try:
            import requests
            import urllib3

            urllib3.disable_warnings()

            cookie_header = token if ";" in token else (
                f"OPS_JWT_TOKEN={token}" if token.startswith("eyJ") else f"cas={token}"
            )
            resp = requests.get(
                "https://ops.qima-inc.com/v3/skynet/v1/apps",
                headers={
                    "x-yz-bu": "fincloud",
                    "x-yz-env": "prod",
                    "Cookie": cookie_header,
                },
                verify=False,
                timeout=10,
            )

            if resp.status_code == 200:
                return True, "Token 有效"
            if resp.status_code == 401:
                return False, "Token 已过期或无效"
            return False, f"验证失败: HTTP {resp.status_code}"
        except Exception as e:
            return False, f"验证异常: {e}"


def get_token():
    """便捷函数：获取全局 token。"""
    return TokenManager().get_token()


def set_token(token):
    """便捷函数：设置全局 token。"""
    TokenManager().set_token(token)


def main():
    """命令行入口。"""
    import argparse

    parser = argparse.ArgumentParser(description="Token 管理工具（共享 ~/.config/zan-tools/token.json）")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    set_parser = subparsers.add_parser("set", help="设置 token")
    set_parser.add_argument("token", help="OPS_JWT_TOKEN 值")

    subparsers.add_parser("get", help="获取 token")
    subparsers.add_parser("list", help="查看 token 状态")
    subparsers.add_parser("validate", help="验证 token")
    subparsers.add_parser("clear", help="清除内存中的 token 缓存")

    args = parser.parse_args()
    manager = TokenManager()

    if args.command == "set":
        manager.set_token(args.token)
        print(f"Token 已设置到 {manager.TOKEN_FILE}")
        return

    if args.command == "get":
        token = manager.get_token()
        if not token:
            print("未找到有效 token")
            print(f"提示：从 https://ops.qima-inc.com/ Cookie 获取 OPS_JWT_TOKEN，然后运行:")
            print(f"  python3 scripts/token_manager.py set '<OPS_JWT_TOKEN值>'")
            return
        masked = token[:10] + "..." + token[-4:] if len(token) > 14 else "***"
        print(f"Token: {masked}")
        print(f"来源: {manager.TOKEN_FILE}")
        return

    if args.command == "list":
        info = manager.list_tokens()
        if not info:
            print("未存储任何 token")
            print(f"文件: {manager.TOKEN_FILE}")
            return
        status = "有效" if not info["is_expired"] else "已过期"
        print(f"Token 状态: [{status}] {info['expiry_desc']}")
        if info.get("username"):
            print(f"用户: {info['username']}")
        print(f"来源: {info['source']}")
        return

    if args.command == "validate":
        is_valid, message = manager.validate_token()
        status = "有效" if is_valid else "失败"
        print(f"[{status}] {message}")
        return

    if args.command == "clear":
        manager.clear_tokens()
        print("已清空内存中的 token 缓存")
        print(f"注意：共享文件 {manager.TOKEN_FILE} 未删除（其他 skill 可能使用）")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
