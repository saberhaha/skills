#!/usr/bin/env python3
"""
dp 平台 Token 管理
支持：保存 Cookie、读取 Cookie、验证认证

存储结构 (~/.config/dp-platform/token.json):
- cookie / base_url: 金融云 dp 平台
- main_cookie / main_base_url: 主站 dp 平台
- airflow_cookie: Airflow（两个站点共用，CAS SSO）
"""

import json
import sys
from pathlib import Path

TOKEN_DIR = Path.home() / ".config" / "dp-platform"
TOKEN_FILE = TOKEN_DIR / "token.json"

# Airflow base URL 映射（cookie 共用，只切换地址）
AIRFLOW_URLS = {
    "fin": "https://airflow.prod.fin.qima-inc.com",
    "main": "https://airflow.prod.qima-inc.com",
}


def ensure_token_dir():
    """确保 token 目录存在"""
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)


def _load_config():
    """读取配置文件"""
    if not TOKEN_FILE.exists():
        return {}
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取配置失败: {e}", file=sys.stderr)
        return {}


def _save_config(config):
    """写入配置文件"""
    ensure_token_dir()
    with open(TOKEN_FILE, "w") as f:
        json.dump(config, f, indent=2)


def save_token(cookie=None, base_url="https://dp.fin.qima-inc.com"):
    """保存金融云 dp cookie"""
    config = _load_config()
    config["cookie"] = cookie
    config["base_url"] = base_url
    _save_config(config)
    print(f"✅ 金融云 dp Cookie 已保存到: {TOKEN_FILE}")


def save_main_token(cookie=None, base_url="https://data.qima-inc.com/garden-api-request/dp"):
    """保存主站 dp cookie"""
    config = _load_config()
    config["main_cookie"] = cookie
    config["main_base_url"] = base_url
    _save_config(config)
    print(f"✅ 主站 dp Cookie 已保存到: {TOKEN_FILE}")


def save_airflow_token(cookie=None):
    """保存 Airflow cookie（金融云和主站共用，CAS SSO）"""
    config = _load_config()
    config["airflow_cookie"] = cookie
    # 清理旧的分站存储
    config.pop("main_airflow_cookie", None)
    config.pop("main_airflow_base_url", None)
    config.pop("airflow_base_url", None)
    _save_config(config)
    print(f"✅ Airflow Cookie 已保存到: {TOKEN_FILE}（金融云/主站共用）")


def load_token():
    """从配置文件读取 token（兼容旧代码）"""
    config = _load_config()
    return config or None


def get_site_config(site="fin"):
    """根据 site 参数获取对应 dp 平台的配置"""
    config = _load_config()
    if site == "main":
        if "main_cookie" not in config:
            return None
        return {
            "cookie": config["main_cookie"],
            "base_url": config.get("main_base_url", "https://data.qima-inc.com/garden-api-request/dp"),
        }
    else:
        if "cookie" not in config:
            return None
        return {
            "cookie": config["cookie"],
            "base_url": config.get("base_url", "https://dp.fin.qima-inc.com"),
        }


def get_site_auth_header(site="fin"):
    """根据 site 参数获取对应 dp 平台的认证 header"""
    site_config = get_site_config(site)
    if not site_config:
        return None
    return {"Cookie": site_config["cookie"]}


def get_airflow_site_config(site="fin"):
    """根据 site 参数获取 Airflow 配置（cookie 共用，只切换 base URL）"""
    config = _load_config()
    cookie = config.get("airflow_cookie")
    if not cookie:
        return None
    return {
        "cookie": cookie,
        "base_url": AIRFLOW_URLS.get(site, AIRFLOW_URLS["fin"]),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="dp 平台 Cookie 管理")
    parser.add_argument("--save", help="保存金融云 dp Cookie")
    parser.add_argument("--save-main", help="保存主站 dp Cookie")
    parser.add_argument("--save-airflow", help="保存 Airflow Cookie（金融云/主站共用）")
    parser.add_argument("--show", action="store_true", help="显示当前配置")
    parser.add_argument("--base-url", default="https://dp.fin.qima-inc.com", help="dp API 基础 URL")

    args = parser.parse_args()

    if args.save:
        save_token(cookie=args.save, base_url=args.base_url)
    elif args.save_main:
        save_main_token(cookie=args.save_main)
    elif args.save_airflow:
        save_airflow_token(cookie=args.save_airflow)
    elif args.show:
        config = _load_config()
        if config:
            display = config.copy()
            for key in ["cookie", "main_cookie", "airflow_cookie"]:
                if key in display and len(display[key]) > 50:
                    display[key] = display[key][:50] + "..."
            print(json.dumps(display, indent=2))
        else:
            print("❌ 未找到保存的配置")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
