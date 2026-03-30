"""
计费规则配置 — 查询计费规则配置列表
来源：schemas/计费规则域/v1_计费规则配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "packNo": {"type": "string", "required": False, "description": "服务包编号"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "服务包编号", "dataIndex": "packNo"},
    {"title": "服务包名称", "dataIndex": "packName"},
    {"title": "收费类型", "dataIndex": "feeTypeDesc"},
    {"title": "生效时间", "dataIndex": "range", "note": "由 effectTime 和 expireTime 拼接"},
    {"title": "费率", "dataIndex": "ratio"},
    {"title": "费率补贴", "dataIndex": "ratioSubsidy"},
    {"title": "交易下限金额(元)", "dataIndex": "amountLower"},
    {"title": "交易上限金额(元)", "dataIndex": "amountUpper"},
    {"title": "最低收费金额(元)", "dataIndex": "feeMin"},
    {"title": "最高收费金额(元)", "dataIndex": "feeMax"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    pack_no: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询计费规则配置列表

    Args:
        pack_no: 服务包编号。可选。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.fee.pack.getFeePackageDetail"

    payload = {
        "packNo": pack_no if pack_no is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
