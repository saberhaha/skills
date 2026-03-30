"""
规则信息报表 — 规则信息报表
来源：schemas/会计域/v1_规则信息报表.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_规则信息报表.json）
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
    "orderNo": {
        "type": "string",
        "required": False,
        "description": "订单号",
    },
    "acquireNo": {
        "type": "string",
        "required": False,
        "description": "收单号（页面字段 receiveNo）",
    },
    "accountingDate": {
        "type": "string",
        "format": "YYYYMMDD",
        "required": False,
        "default": "today",
        "description": "会计日期，格式 YYYYMMDD，默认今天",
    },
}

# 数据展示列（来源：schemas/会计域/v1_规则信息报表.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "会计日期", "dataIndex": "accountDate", "format": "YYYY-MM-DD"},
    {"title": "记账码", "dataIndex": "bookkeepingCode"},
    {"title": "订单号", "dataIndex": "orderNo"},
    {"title": "收单号", "dataIndex": "receiveNo"},
    {"title": "外部流水号", "dataIndex": "outerSerialNo"},
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "账户", "dataIndex": "accountNo"},
    {"title": "借贷方向", "dataIndex": "debtCreditDir"},
    {"title": "交易金额", "dataIndex": "dealBalance"},
    {"title": "币种", "dataIndex": "currency"},
    {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "交易描述", "dataIndex": "remark"},
]


def execute(
    order_no: Optional[str] = None,
    acquire_no: Optional[str] = None,
    accounting_date: Optional[str] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """查询规则信息报表。
    用户只需提供订单号、收单号等筛选条件，其余参数自动使用页面默认值。

    Args:
        order_no: 订单号。可选。
        acquire_no: 收单号。可选。
        accounting_date: 会计日期，格式 YYYYMMDD（如 "20260313"）。可选，默认今天。
        page_no: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/accounting.ruleRecord.list"

    now = datetime.now()
    payload = {
        "pageNo": page_no,
        "pageSize": page_size,
        "accountingDate": accounting_date if accounting_date is not None else now.strftime("%Y%m%d"),
    }
    if order_no is not None:
        payload["orderNo"] = order_no
    if acquire_no is not None:
        payload["acquireNo"] = acquire_no

    return client.post(url, payload)
