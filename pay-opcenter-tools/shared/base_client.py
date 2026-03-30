#!/usr/bin/env python3
"""
支付运营平台基础客户端
负责：OAuth Token 管理、HTTP 请求封装
"""

import sys
import json
import requests
import warnings
from pathlib import Path
from typing import Optional, Dict, Any

# 抑制 SSL 警告（内部工具）
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# 配置目录
DATA_DIR = Path.home() / ".config" / "zan-tools"
TOKEN_FILE = DATA_DIR / "pay-opcenter-token.json"

# 导入环境配置（支持相对导入和直接运行）
try:
    from .env_config import env_config
except ImportError:
    from env_config import env_config


class PayOpcenterClient:
    """支付运营平台 API 客户端"""

    def __init__(self):
        self.token: Optional[str] = None
        self.base_url: str = env_config.opcenter_base_url
        self._load_token()

    def _load_token(self):
        """加载已保存的 Token"""
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                self.token = data.get('token')

    def save_token(self, token: str):
        """保存 Token"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            json.dump({'token': token}, f)
        self.token = token
        print("Token 已保存")

    def is_configured(self) -> bool:
        """检查是否已配置 Token"""
        return self.token is not None

    def _prompt_token(self):
        """提示用户输入 Token"""
        if sys.stdin.isatty():
            print("未配置 Token，请按以下步骤获取：")
            print(f"  1. 打开 {self.base_url}/")
            print("  2. F12 开发者工具 → 应用 → Cookie")
            print("  3. 复制 OAuth_TOKEN 的值")
            print("")
            token = input("请粘贴 Token: ").strip()
            if not token:
                raise Exception("Token 不能为空")
            self.save_token(token)
        else:
            raise Exception(
                "Token 未配置，请先运行：\n"
                "  python3 shared/base_client.py config --token <OAuth_TOKEN>\n"
                f"获取 Token：{self.base_url}/ → F12 → Cookie → OAuth_TOKEN"
            )

    def _ensure_token(self):
        """确保 Token 已配置"""
        if not self.is_configured():
            self._prompt_token()

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """GET 请求"""
        self._ensure_token()
        headers = {
            "Cookie": f"OAuth_TOKEN={self.token}",
            "Accept": "application/json",
        }
        try:
            resp = requests.get(url, params=params, headers=headers, verify=False, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Token 已过期或无效，请重新配置")
            raise Exception(f"HTTP 错误 {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("响应不是有效的 JSON 格式")

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """POST 请求"""
        self._ensure_token()
        headers = {
            "Cookie": f"OAuth_TOKEN={self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            resp = requests.post(url, json=data, headers=headers, verify=False, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Token 已过期或无效，请重新配置")
            raise Exception(f"HTTP 错误 {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("响应不是有效的 JSON 格式")


# 全局客户端实例
client = PayOpcenterClient()


def main():
    """命令行入口：配置 Token 和环境"""
    import argparse
    parser = argparse.ArgumentParser(description='支付运营平台工具配置')
    subparsers = parser.add_subparsers(dest='command')

    config_parser = subparsers.add_parser('config', help='配置 Token')
    config_parser.add_argument('--token', required=True, help='OAuth_TOKEN')

    subparsers.add_parser('status', help='检查配置状态')

    env_parser = subparsers.add_parser('env', help='环境配置')
    env_parser.add_argument('--base-url', help='设置 OPCENTER_BASE_URL')
    env_parser.add_argument('--reset', action='store_true', help='重置为默认环境')

    args = parser.parse_args()

    if args.command == 'config':
        client.save_token(args.token)
        print("✓ Token 配置成功")
    elif args.command == 'status':
        if client.is_configured():
            print("✓ Token 已配置")
        else:
            print("✗ Token 未配置")
            print("  运行：python3 shared/base_client.py config --token <OAuth_TOKEN>")
        print(f"  当前环境: {client.base_url}")
    elif args.command == 'env':
        if args.reset:
            env_config.reset_to_default()
            print(f"✓ 已重置为默认环境: {env_config.opcenter_base_url}")
        elif args.base_url:
            env_config.opcenter_base_url = args.base_url
            print(f"✓ OPCENTER_BASE_URL 已设置为: {args.base_url}")
        else:
            config = env_config.show_config()
            print("当前环境配置:")
            print(f"  OPCENTER_BASE_URL: {config['OPCENTER_BASE_URL']}")
            print(f"  配置文件: {config['config_file']}")
            print(f"  使用默认值: {'是' if config['is_default'] else '否'}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
