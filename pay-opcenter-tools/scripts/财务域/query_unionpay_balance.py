"""
银联余额查询 — 银联余额查询
来源：schemas/财务域/v1_银联余额查询.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "acctNo": {
        "type": "string",
        "required": False,
        "description": "银联备款账号，来自 queryAcctList 辅助接口返回，传具体账号或不传（全部）"
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "开始时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "结束时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "时间", "dataIndex": "time", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "备款账号", "dataIndex": "account"},
    {"title": "金额", "dataIndex": "balance"},
]


def execute(
    acct_no: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询银联备付金余额记录列表。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        acct_no: 银联备款账号。可选。不传则查全部。
        start_date: 开始时间。可选。格式：YYYY-MM-DD HH:mm:ss，如 "2026-03-01 00:00:00"。
        end_date: 结束时间。可选。格式：YYYY-MM-DD HH:mm:ss，如 "2026-03-13 23:59:59"。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.queryReserveBalanceList"

    now = datetime.now()
    payload: dict = {
        "page": page,
        "pageSize": page_size,
    }

    if acct_no is not None:
        payload["acctNo"] = acct_no
    # startDate 格式：YYYY-MM-DD HH:mm:ss
    if start_date is not None:
        payload["startDate"] = start_date
    # endDate 格式：YYYY-MM-DD HH:mm:ss
    if end_date is not None:
        payload["endDate"] = end_date

    return client.post(url, payload)
