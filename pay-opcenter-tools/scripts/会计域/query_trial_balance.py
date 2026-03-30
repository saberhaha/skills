"""
试算查询 — 试算查询
来源：schemas/会计域/v1_试算查询.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_试算查询.json）
PARAM_SCHEMA = {
    "acctNo": {
        "type": "string",
        "required": False,
        "description": "账号",
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "开始时间",
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "结束时间",
    },
    "pageNo": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码",
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数",
    },
}

# 数据展示列（来源：schemas/会计域/v1_试算查询.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "账号", "dataIndex": "acctNO"},
    {"title": "会计日期", "dataIndex": "accountingDate", "format": "YYYY-MM-DD"},
    {"title": "借方期初余额", "dataIndex": "debitInitBalance"},
    {"title": "贷方期初余额", "dataIndex": "creditInitBalance"},
    {"title": "借方期末余额", "dataIndex": "debitEndBalance"},
    {"title": "贷方期末余额", "dataIndex": "creditEndBalance"},
    {"title": "借方发生额", "dataIndex": "creditAmount"},
    {"title": "贷方发生额", "dataIndex": "debitAmount"},
]


def execute(
    acct_no: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """查询试算余额。
    用户只需提供账号和时间范围，其余参数自动使用页面默认值。

    Args:
        acct_no: 账号。可选。
        start_date: 开始时间，格式 YYYY-MM-DD HH:mm:ss（如 "2026-03-01 00:00:00"）。可选。
        end_date: 结束时间，格式 YYYY-MM-DD HH:mm:ss（如 "2026-03-13 23:59:59"）。可选。
        page_no: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.accountingTrialQuery"

    payload: dict = {
        "pageNo": page_no,
        "pageSize": page_size,
    }
    if acct_no is not None:
        payload["acctNo"] = acct_no
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date

    return client.post(url, payload)
