"""
产品规则配置 — 查询产品规则配置列表
来源：schemas/计费规则域/v3_产品规则配置.json
"""
import sys
import os
from typing import Optional, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "factorQueryList": {
        "type": "array", "required": False,
        "description": "因子查询列表。当 product 非空时传入，格式：[{\"factorKey\": \"product\", \"content\": \"<产品码>\"}]",
    },
    "namespace": {"type": "string", "required": True, "default": "yz-settle-center", "description": "命名空间，固定值"},
}

DISPLAY_TYPE = "card"
DISPLAY_NOTE = "非表格：展示业务产品结算规则流程列表卡片，含ruleConfigNo和desc"


def execute(
    product: Optional[str] = None,
    namespace: str = "yz-settle-center",
) -> dict:
    """查询产品规则配置列表

    Args:
        product: 产品码。可选，非空时作为因子查询条件传入。
        namespace: 命名空间，固定值。默认=yz-settle-center。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.list"

    payload = {
        "namespace": namespace,
    }

    if product:
        payload["factorQueryList"] = [
            {"factorKey": "product", "content": product}
        ]

    return client.post(url, payload)
