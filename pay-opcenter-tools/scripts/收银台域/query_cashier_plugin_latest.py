"""
收银台插件最新版本查询 — 查询收银台插件最新版本
来源：schemas/收银台域/v3_收银台插件最新版本查询.json
"""
import sys
import os
from typing import Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_收银台插件最新版本查询.json）
PARAM_SCHEMA = {
    "channel": {
        "type": "enum",
        "required": True,
        "default": "BETA_VERSION",
        "enum_values": {"BETA_VERSION": "测试版", "OFFICIAL_VERSION": "正式版"},
        "description": "插件通道类型。测试版=BETA_VERSION，正式版=OFFICIAL_VERSION"
    },
}

# 数据展示列（来源：v3_收银台插件最新版本查询.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "版本号", "dataIndex": "version"},
    {"title": "下载地址", "dataIndex": "url"},
    {"title": "通道类型", "dataIndex": "channel"},
]


def execute(
    channel: Literal["BETA_VERSION", "OFFICIAL_VERSION"] = "BETA_VERSION",
) -> dict:
    """查询收银台插件最新版本
    根据通道类型查询收银台插件的最新版本信息（版本号、下载地址）。

    Args:
        channel: 插件通道类型。必填。枚举：BETA_VERSION=测试版, OFFICIAL_VERSION=正式版。默认=BETA_VERSION（测试版）。
    """
    url = f"{BASE_URL}/v3/api/cashier-plugin/manage/version/{channel}/latest"
    return client.get(url)
