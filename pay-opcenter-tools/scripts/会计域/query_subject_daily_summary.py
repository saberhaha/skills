"""
科目日汇总 — 科目日汇总
来源：schemas/会计域/v1_科目日汇总.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_科目日汇总.json）
PARAM_SCHEMA = {
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
    "accountingDate": {
        "type": "string",
        "format": "YYYYMMDD",
        "required": False,
        "default": "today",
        "description": "会计日期，格式 YYYYMMDD，默认今天",
    },
    "subjectCode": {
        "type": "string",
        "required": False,
        "description": "会计科目代码",
    },
}

# 数据展示列（来源：schemas/会计域/v1_科目日汇总.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "会计日期", "dataIndex": "accountDate", "format": "YYYY-MM-DD"},
    {"title": "科目代码", "dataIndex": "subjectCode"},
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "余额方向", "dataIndex": "balanceDirDesc"},
    {"title": "期初余额", "dataIndex": "beginBalance"},
    {"title": "期末余额", "dataIndex": "endBalance"},
    {"title": "借方发生额", "dataIndex": "debtIncurredBalance"},
    {"title": "贷方发生额", "dataIndex": "creditIncurredBalance"},
    {"title": "借方笔数", "dataIndex": "debtCount"},
    {"title": "贷方笔数", "dataIndex": "creditCount"},
]


def execute(
    accounting_date: Optional[str] = None,
    subject_code: Optional[str] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """查询科目日汇总数据。
    用户只需提供会计日期和科目代码，其余参数自动使用页面默认值。

    Args:
        accounting_date: 会计日期，格式 YYYYMMDD（如 "20260313"）。可选，默认今天。
        subject_code: 会计科目代码。可选。
        page_no: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/accounting.subjectCollect.list"

    now = datetime.now()
    payload = {
        "pageNo": page_no,
        "pageSize": page_size,
        "accountingDate": accounting_date if accounting_date is not None else now.strftime("%Y%m%d"),
    }
    if subject_code is not None:
        payload["subjectCode"] = subject_code

    return client.post(url, payload)
