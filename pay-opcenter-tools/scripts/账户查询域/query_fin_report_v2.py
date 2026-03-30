"""
会计报表查询（科目总账表）(v2)
来源：schemas/账户查询域/v2_会计报表查询.json
"""
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "enum", "required": True,
        "enum_values": {"1": "高汇通支付", "2": "有赞平台"},
        "description": "核算主体"
    },
    "accountingDate": {
        "type": "number", "format": "timestamp_s",
        "required": True, "default": "yesterday",
        "description": "会计日期（秒级Unix时间戳），默认昨天"
    },
    "subjectLevel": {
        "type": "enum", "required": True, "default": 1,
        "enum_values": {"1": "一级", "2": "二级", "3": "三级"},
        "description": "科目级别，默认1（一级）"
    },
}

DISPLAY_COLUMNS = [
    {"title": "核算主体", "dataIndex": "totalCompute"},
    {"title": "会计日期", "dataIndex": "accountingDate"},
    {"title": "科目级别", "dataIndex": "subjectLevel"},
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "科目代码", "dataIndex": "subjectCode"},
    {"title": "借方期初余额", "dataIndex": "begBalance"},
    {"title": "贷方期初余额", "dataIndex": "begBalance"},
    {"title": "借方发生额", "dataIndex": "debitAmount"},
    {"title": "贷方发生额", "dataIndex": "creditAmount"},
    {"title": "借方期末余额", "dataIndex": "endBalance"},
    {"title": "贷方期末余额", "dataIndex": "endBalance"},
]


def execute(
    accounting_entity: Literal[1, 2],
    accounting_date: int = None,
    subject_level: Literal[1, 2, 3] = 1,
) -> dict:
    """会计报表查询（科目总账表）(v2)
    按核算主体、会计日期和科目级别查询科目总账表。

    Args:
        accounting_entity: 核算主体。枚举：1=高汇通支付, 2=有赞平台。必填。
        accounting_date: 会计日期。秒级Unix时间戳。可选，默认昨天。
        subject_level: 科目级别。枚举：1=一级, 2=二级, 3=三级。默认 1。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.summary.querySummaryByDateAndLevelFilterByAcctEnt"

    if accounting_date is None:
        yesterday = datetime.now() - timedelta(days=1)
        accounting_date = int(yesterday.timestamp())

    payload = {
        "accountingEntity": accounting_entity,
        "accountingDate": accounting_date,
        "subjectLevel": subject_level,
    }

    return client.post(url, payload)
