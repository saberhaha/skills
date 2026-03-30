"""
套餐保证金配置 — 查询套餐保证金配置列表
来源：schemas/计费规则域/v1_套餐保证金配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "mchId": {"type": "string", "required": False, "description": "商户ID"},
    "kdtId": {"type": "string", "required": False, "description": "店铺ID"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "商户ID", "dataIndex": "mchId"},
    {"title": "套餐版本", "dataIndex": "version"},
    {"title": "时间段", "dataIndex": "range", "note": "由 effectTime 和 expireTime 拼接"},
    {"title": "备注", "dataIndex": "remark"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    mch_id: Optional[str] = None,
    kdt_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询套餐保证金配置列表

    Args:
        mch_id: 商户ID。可选。
        kdt_id: 店铺ID。可选。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.fee.feeStrategy.queryGuaranteeStrategy"

    payload = {
        "page": page,
        "pageSize": page_size,
    }

    if mch_id is not None:
        payload["mchId"] = mch_id
    if kdt_id is not None:
        payload["kdtId"] = kdt_id

    return client.post(url, payload)
