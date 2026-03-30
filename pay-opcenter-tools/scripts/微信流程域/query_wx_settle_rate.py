"""
支付配置详情-微信结算费率配置查询 — 查询微信结算费率配置
来源：schemas/微信流程域/支付配置详情.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "operator": {
        "type": "string",
        "required": True,
        "description": "操作人用户名（从localStorage获取）"
    },
}

DISPLAY_COLUMNS = [
    {"title": "主体类型编码", "dataIndex": "code"},
    {"title": "主体类型描述", "dataIndex": "desc"},
    {"title": "行业费率配置列表", "dataIndex": "wxIndustryRateConfigModelList"},
]

DISPLAY_TYPE = "detail"


def execute(
    operator: str,
) -> dict:
    """支付配置详情 — 微信结算费率配置查询（v1）

    Args:
        operator: 操作人用户名（必填，从localStorage获取）。
    """
    url = f"{BASE_URL}/dispatcher/pay.customercore.query.wx.settle.rate.config"

    payload = {
        "operator": operator,
    }

    return client.post(url, payload)
