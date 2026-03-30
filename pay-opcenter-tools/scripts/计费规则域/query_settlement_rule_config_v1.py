"""
结算规则配置 — 查询结算规则配置列表
来源：schemas/计费规则域/v1_结算规则配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "mchId": {"type": "string", "required": False, "description": "服务商商户号"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "服务商商户号", "dataIndex": "userNo"},
    {"title": "结算类型", "dataIndex": "settleType"},
    {"title": "结算账户类型", "dataIndex": "accountTypeDesc"},
    {"title": "收入/支出", "dataIndex": "inOut"},
    {"title": "产品类型", "dataIndex": "bizProd"},
    {"title": "业务模式", "dataIndex": "bizModel"},
    {"title": "动作", "dataIndex": "bizTotalType"},
    {"title": "支付工具", "dataIndex": "bizType"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    mch_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询结算规则配置列表

    Args:
        mch_id: 服务商商户号。可选。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.clearing.clear.getSettleRule"

    payload = {
        "page": page,
        "pageSize": page_size,
    }

    if mch_id is not None:
        payload["mchId"] = mch_id

    return client.post(url, payload)
