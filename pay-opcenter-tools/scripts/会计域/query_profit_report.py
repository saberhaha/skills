"""
利润报表 — 利润报表
来源：schemas/会计域/v1_利润报表.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_利润报表.json）
PARAM_SCHEMA = {
    "queryOption": {
        "type": "string",
        "format": "YYYYMMDD",
        "required": False,
        "default": "today",
        "description": "报表日期，格式 YYYYMMDD，默认今天",
    },
    "type": {
        "type": "enum",
        "required": False,
        "default": "1",
        "enum_values": {"1": "日报表", "2": "周报表", "3": "月报表"},
        "description": "报表类型",
    },
}

# 数据展示列（来源：schemas/会计域/v1_利润报表.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "期初余额", "dataIndex": "beginBalance"},
    {"title": "期末余额", "dataIndex": "endBalance"},
    {"title": "借方发生额", "dataIndex": "debitAmount"},
    {"title": "贷方发生额", "dataIndex": "creditAmount"},
]


def execute(
    query_option: Optional[str] = None,
    type: Optional[Literal["1", "2", "3"]] = None,
) -> dict:
    """查询利润报表。
    用户只需提供报表日期和类型，其余参数自动使用页面默认值。

    Args:
        query_option: 报表日期，格式 YYYYMMDD（如 "20260313"）。可选，默认今天。
        type: 报表类型。可选。枚举：1=日报表, 2=周报表, 3=月报表。默认=1(日报表)。
    """
    url = f"{BASE_URL}/dispatcher/accounting.profits.list"

    now = datetime.now()
    payload = {
        "queryOption": query_option if query_option is not None else now.strftime("%Y%m%d"),
        "type": type if type is not None else "1",  # 默认：日报表
    }

    return client.post(url, payload)
