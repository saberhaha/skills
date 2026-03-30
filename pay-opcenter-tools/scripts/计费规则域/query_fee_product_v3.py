"""
计费产品管理 — 查询计费产品列表
来源：schemas/计费规则域/v3_计费产品管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "feeProductCode": {"type": "string", "required": False, "default": "", "description": "计费产品编码，默认空=全部"},
    "industryCode": {"type": "string", "required": False, "default": "", "description": "行业编码，默认空=全部"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "计费产品编码", "dataIndex": "feeProductCode"},
    {"title": "计费产品名称", "dataIndex": "feeProductName"},
    {"title": "是否有协议", "dataIndex": "hasProtocol"},
    {"title": "业务方", "dataIndex": "partnerName"},
    {"title": "行业", "dataIndex": "industryName"},
    {"title": "通用规则", "dataIndex": "commonRule"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "状态", "dataIndex": "state"},
]


def execute(
    fee_product_code: str = "",
    industry_code: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询计费产品列表

    Args:
        fee_product_code: 计费产品编码，默认空=全部。
        industry_code: 行业编码，默认空=全部。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.product.list"

    payload = {
        "feeProductCode": fee_product_code,
        "industryCode": industry_code,
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
