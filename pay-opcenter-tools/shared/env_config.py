#!/usr/bin/env python3
"""
环境变量配置管理
支持用户自定义 OPCENTER_BASE_URL
"""

import json
from pathlib import Path
from typing import Optional

# 配置目录
DATA_DIR = Path.home() / ".config" / "zan-tools"
ENV_FILE = DATA_DIR / "pay-opcenter-env.json"

# 默认值
DEFAULT_OPCENTER_BASE_URL = "https://pay-opcenter.prod.fin.qima-inc.com"

# 环境预设
ENVIRONMENTS = {
    "qa": "https://pay-opcenter.qa.fin.qima-inc.com",
    "pre": "https://pay-opcenter.pre.fin.qima-inc.com",
    "prod": "https://pay-opcenter.prod.fin.qima-inc.com",
}


class EnvConfig:
    """环境配置管理器"""

    def __init__(self):
        self._config: dict = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if ENV_FILE.exists():
            try:
                with open(ENV_FILE, 'r') as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}

    def _save_config(self):
        """保存配置文件"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(ENV_FILE, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value: str):
        """设置配置值"""
        self._config[key] = value
        self._save_config()

    def delete(self, key: str):
        """删除配置值"""
        if key in self._config:
            del self._config[key]
            self._save_config()

    @property
    def opcenter_base_url(self) -> str:
        """获取 OPCENTER_BASE_URL"""
        return self.get("OPCENTER_BASE_URL", DEFAULT_OPCENTER_BASE_URL)

    @opcenter_base_url.setter
    def opcenter_base_url(self, value: str):
        """设置 OPCENTER_BASE_URL"""
        self.set("OPCENTER_BASE_URL", value)

    def switch_env(self, env: str) -> str:
        """切换环境（qa/pre/prod）"""
        env_lower = env.lower()
        if env_lower not in ENVIRONMENTS:
            raise ValueError(f"不支持的环境: {env}，可选: {list(ENVIRONMENTS.keys())}")
        self.opcenter_base_url = ENVIRONMENTS[env_lower]
        return self.opcenter_base_url

    def get_current_env(self) -> str:
        """获取当前环境名称"""
        current = self.opcenter_base_url
        for name, url in ENVIRONMENTS.items():
            if current == url:
                return name
        return "custom"

    def reset_to_default(self):
        """重置为默认配置"""
        self._config = {}
        self._save_config()

    def show_config(self) -> dict:
        """显示当前配置"""
        return {
            "OPCENTER_BASE_URL": self.opcenter_base_url,
            "config_file": str(ENV_FILE),
            "is_default": self.opcenter_base_url == DEFAULT_OPCENTER_BASE_URL
        }


# 全局配置实例
env_config = EnvConfig()


def main():
    """命令行入口：配置环境变量"""
    import argparse
    parser = argparse.ArgumentParser(description='支付运营平台环境配置')
    subparsers = parser.add_subparsers(dest='command')

    # 设置 base-url
    set_parser = subparsers.add_parser('set', help='设置 OPCENTER_BASE_URL')
    set_parser.add_argument('--base-url', required=True, help='OPCENTER_BASE_URL 地址')

    # 切换环境
    switch_parser = subparsers.add_parser('switch', help='切换环境（qa/pre/prod）')
    switch_parser.add_argument('env', choices=['qa', 'pre', 'prod'], help='环境名称')

    # 查看当前配置
    subparsers.add_parser('show', help='显示当前配置')

    # 重置为默认
    subparsers.add_parser('reset', help='重置为默认配置')

    args = parser.parse_args()

    if args.command == 'set':
        env_config.opcenter_base_url = args.base_url
        print(f"✓ OPCENTER_BASE_URL 已设置为: {args.base_url}")
    elif args.command == 'switch':
        url = env_config.switch_env(args.env)
        env_name = {'qa': 'QA', 'pre': '预发', 'prod': '线上'}[args.env]
        print(f"✓ 已切换到{env_name}环境: {url}")
    elif args.command == 'show':
        config = env_config.show_config()
        current_env = env_config.get_current_env()
        env_display = {'qa': 'QA', 'pre': '预发', 'prod': '线上', 'custom': '自定义'}.get(current_env, '自定义')
        print("当前配置:")
        print(f"  环境: {env_display}")
        print(f"  OPCENTER_BASE_URL: {config['OPCENTER_BASE_URL']}")
        print(f"  配置文件: {config['config_file']}")
    elif args.command == 'reset':
        env_config.reset_to_default()
        print(f"✓ 已重置为默认配置: {DEFAULT_OPCENTER_BASE_URL}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
