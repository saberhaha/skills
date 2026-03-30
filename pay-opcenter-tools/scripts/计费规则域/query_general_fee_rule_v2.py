"""
通用计费规则 — 查询通用计费规则列表
来源：schemas/计费规则域/v2_通用计费规则.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "feeType": {"type": "string", "required": False, "description": "计费产品名称或代码"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "计费产品代码", "dataIndex": "feeType"},
    {"title": "计费产品名称", "dataIndex": "feeName"},
    {"title": "订单算账通用规则", "dataIndex": "discount"},
    {"title": "结算资产类型", "dataIndex": "feeResourceList"},
    {"title": "资产结算优先级", "dataIndex": "priorityFeeResourceList"},
]


def execute(
    fee_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询通用计费规则列表

    Args:
        fee_type: 计费产品名称或代码。可选。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/finance.fee.rule.general.query.list"

    payload = {
        "page": page,
        "pageSize": page_size,
    }

    if fee_type is not None:
        payload["feeType"] = fee_type

    return client.post(url, payload)
