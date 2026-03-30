"""
支付配置详情-操作日志查询 — 查询子商户号操作日志列表
来源：schemas/微信流程域/支付配置详情.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "subMchId": {
        "type": "string",
        "required": True,
        "description": "子商户号（从主查询列表行中获取）"
    },
    "pageParam.page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageParam.pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
}

DISPLAY_COLUMNS = [
    {"title": "操作人", "dataIndex": "operateUser"},
    {"title": "操作时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作事项", "dataIndex": "operateType", "enum_values": {"0": "开启", "2": "禁用", "5": "结算id修改"}},
    {"title": "操作原因", "dataIndex": "operateReasonDesc"},
]


def execute(
    sub_mch_id: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """支付配置详情 — 操作日志查询（v1）

    Args:
        sub_mch_id: 子商户号（必填，从主查询列表行中获取）。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/customercore.submchid.config.queryOpsLog"

    payload = {
        "subMchId": sub_mch_id,
        "pageParam": {
            "page": page,
            "pageSize": page_size,
        },
    }

    return client.post(url, payload)
