"""
商户费率规则 — 查询商户费率规则列表
来源：schemas/计费规则域/v3_商户费率规则.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "kdtId": {"type": "string", "required": False, "description": "店铺kdtId（当 idType=kdtId 时传入）"},
    "mchId": {"type": "string", "required": False, "description": "商户号（当 idType=mchId 时传入）"},
    "feeProductCode": {"type": "string", "required": False, "default": "", "description": "计费产品编码，默认空=全部"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "计费产品编码", "dataIndex": "feeProductCode"},
    {"title": "计费产品名称", "dataIndex": "feeProductName"},
    {"title": "店铺kdtid", "dataIndex": "kdtId"},
    {"title": "商户号", "dataIndex": "mchId"},
    {"title": "创建人", "dataIndex": "creator"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "模板类型", "dataIndex": "packageType", "enum_values": {"COMMON": "通用", "CUSTOM": "个性化"}},
    {"title": "模板名称", "dataIndex": "packName"},
    {"title": "规则状态", "dataIndex": "ruleState", "enum_values": {"INVALID": "失效", "VALID": "运行中", "WAITING": "待生效"}},
]


def execute(
    kdt_id: Optional[str] = None,
    mch_id: Optional[str] = None,
    fee_product_code: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询商户费率规则列表

    Args:
        kdt_id: 店铺kdtId。可选。
        mch_id: 商户号。可选。
        fee_product_code: 计费产品编码，默认空=全部。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.feerule.list"

    payload = {
        "feeProductCode": fee_product_code,
        "page": page,
        "pageSize": page_size,
    }

    if kdt_id is not None:
        payload["kdtId"] = kdt_id
    if mch_id is not None:
        payload["mchId"] = mch_id

    return client.post(url, payload)
