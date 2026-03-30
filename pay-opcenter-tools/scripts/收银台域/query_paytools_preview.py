"""
PayTools预览 — 预览PayTools支付工具列表
来源：schemas/收银台域/v3_PayTools预览.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_PayTools预览.json）
PARAM_SCHEMA = {
    "biz": {
        "type": "string",
        "required": True,
        "description": "业务方标识（枚举值从服务端动态下发，如 wsc/wxd/beauty 等，具体值由运行时配置决定）"
    },
    "hostApp": {
        "type": "string",
        "required": True,
        "description": "App标识（枚举值从服务端动态下发，具体值由运行时配置决定）"
    },
    "runtime": {
        "type": "string",
        "required": True,
        "description": "运行时标识（枚举值从服务端动态下发，具体值由运行时配置决定）"
    },
    "kdtId": {"type": "string", "required": False, "description": "店铺ID（可选）"},
    "buyerId": {"type": "string", "required": False, "description": "用户ID（可选）"},
}

# 数据展示列（来源：v3_PayTools预览.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "支付方式名称", "dataIndex": "payChannelName"},
    {"title": "支付方式编码", "dataIndex": "payChannel"},
]


def execute(
    biz: str,
    host_app: str,
    runtime: str,
    kdt_id: Optional[str] = None,
    buyer_id: Optional[str] = None,
) -> dict:
    """预览PayTools支付工具列表
    根据业务方、App标识、运行时标识预览当前生效的支付工具列表。

    Args:
        biz: 业务方标识。必填。如 wsc/wxd/beauty 等（具体值由运行时配置决定）。
        host_app: App标识。必填。具体值由运行时配置决定。
        runtime: 运行时标识。必填。具体值由运行时配置决定。
        kdt_id: 店铺ID。可选。
        buyer_id: 用户ID。可选。
    """
    url = f"{BASE_URL}/v3/api/cashier-biz-manage/paytools/preview"
    params = {
        "biz": biz,
        "hostApp": host_app,
        "runtime": runtime,
    }
    if kdt_id is not None:
        params["kdtId"] = kdt_id
    if buyer_id is not None:
        params["buyerId"] = buyer_id
    return client.get(url, params)
