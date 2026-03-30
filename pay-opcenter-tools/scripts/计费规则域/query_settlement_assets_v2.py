"""
结算资产规则 — 查询结算资产规则
来源：schemas/计费规则域/v2_结算资产规则.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "prefix": {"type": "string", "required": False, "default": "kdtId", "description": "店铺信息查询维度（kdtId/kdtName）"},
    "shopInfo": {"type": "string", "required": True, "description": "店铺信息值（按 prefix 解释）"},
    "kdtId": {"type": "number", "required": False, "description": "当 prefix=kdtId 时传值"},
    "kdtName": {"type": "string", "required": False, "description": "当 prefix=kdtName 时传值"},
    "feeType": {"type": "string", "required": False, "description": "计费产品名称或代码"},
}

DISPLAY_TYPE = "multi-table"
DISPLAY_TABLES = [
    {"name": "结算资产规则列表", "columns": ["kdtId", "kdtName", "assetsType", "settlementType"]},
    {"name": "赠送资源", "columns": ["createTime", "total", "protocolNo"]},
    {"name": "订购资源", "columns": ["createTime", "total", "protocolNo"]},
    {"name": "共享资源", "columns": ["createTime", "total", "protocolNo", "mainKdtId", "subKdtList"]},
    {"name": "无限量订购包", "columns": ["createTime", "expireTime", "protocolNo"]},
]


def execute(
    shop_info: str,
    prefix: Literal["kdtId", "kdtName"] = "kdtId",
    fee_type: Optional[str] = None,
) -> dict:
    """查询结算资产规则

    Args:
        shop_info: 店铺信息值，根据 prefix 解释为 kdtId 或 kdtName。必填。
        prefix: 店铺信息查询维度。枚举：kdtId / kdtName。默认=kdtId。
        fee_type: 计费产品名称或代码。可选。
    """
    url = f"{BASE_URL}/dispatcher/finance.fee.resource.query.list"

    payload = {
        "prefix": prefix,
    }

    if prefix == "kdtId":
        payload["kdtId"] = int(shop_info)
    else:
        payload["kdtName"] = shop_info

    if fee_type is not None:
        payload["feeType"] = fee_type

    return client.post(url, payload)
