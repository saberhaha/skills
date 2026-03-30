"""
产品规则结果查询 — 查询产品规则结果
来源：schemas/计费规则域/v3_产品规则结果查询.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "ruleConfigNo": {"type": "string", "required": True, "description": "规则配置编号"},
    "namespace": {"type": "string", "required": True, "default": "yz-settle-center", "description": "命名空间，固定值"},
}

DISPLAY_TYPE = "multi-section"
DISPLAY_SECTIONS = [
    {"name": "规则基本信息"},
    {
        "name": "付款方资产优先级表",
        "columns": [
            {"title": "付款方的资产", "dataIndex": "payerAssets"},
            {"title": "资产不可用条件", "dataIndex": "payerAssetLimit"},
            {"title": "排序", "dataIndex": "paymentPriority"},
        ],
    },
    {
        "name": "收款方资产优先级表",
        "columns": [
            {"title": "收款方的资产", "dataIndex": "payeeAssets"},
            {"title": "资产不可用条件", "dataIndex": "payeeAssetLimit"},
            {"title": "排序", "dataIndex": "receivePriority"},
        ],
    },
]


def execute(
    rule_config_no: str,
    namespace: str = "yz-settle-center",
) -> dict:
    """查询产品规则结果

    Args:
        rule_config_no: 规则配置编号。必填。
        namespace: 命名空间，固定值。默认=yz-settle-center。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.query"

    payload = {
        "ruleConfigNo": rule_config_no,
        "namespace": namespace,
    }

    return client.post(url, payload)
