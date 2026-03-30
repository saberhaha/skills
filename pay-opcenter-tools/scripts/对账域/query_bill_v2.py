"""
账单查询 — v2 备付金账单查询
来源：schemas/对账域/v2_账单查询.json
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
    "account": {
        "type": "string",
        "required": False,
        "default": "210401323",
        "description": "备付金账号，默认 210401323"
    },
    "clearingStartDate": {
        "type": "number",
        "format": "YYYYMMDD",
        "required": False,
        "default": "now-3M",
        "description": "银行清算开始日期（格式：YYYYMMDD）"
    },
    "clearingEndDate": {
        "type": "number",
        "format": "YYYYMMDD",
        "required": False,
        "default": "now",
        "description": "银行清算结束日期（格式：YYYYMMDD）"
    },
    "bizStartDate": {
        "type": "string",
        "format": "YYYYMMDD HH:mm:ss",
        "required": False,
        "description": "银行业务开始日期（格式：YYYYMMDD HH:mm:ss）"
    },
    "bizEndDate": {
        "type": "string",
        "format": "YYYYMMDD HH:mm:ss",
        "required": False,
        "description": "银行业务结束日期（格式：YYYYMMDD HH:mm:ss）"
    },
    "minAmount": {
        "type": "number",
        "required": False,
        "description": "最小金额（单位：分）"
    },
    "maxAmount": {
        "type": "number",
        "required": False,
        "description": "最大金额（单位：分）"
    },
    "analogueAccount": {
        "type": "string",
        "required": False,
        "description": "对方账户号"
    },
    "analogueAccountName": {
        "type": "string",
        "required": False,
        "description": "对方账户名"
    },
    "datagramType": {
        "type": "number",
        "required": False,
        "description": "报文类型（[UNRESOLVED: 枚举值未从源码确认，请人工补全]）"
    },
    "remark": {
        "type": "string",
        "required": False,
        "description": "摘要"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "银行业务日期", "dataIndex": "bizDate"},
    {"title": "银行清算日期", "dataIndex": "clearingDate"},
    {"title": "借方金额", "dataIndex": "debitAmount"},
    {"title": "贷方金额", "dataIndex": "creditAmount"},
    {"title": "余额", "dataIndex": "balance"},
    {"title": "对方账户账号", "dataIndex": "analogueAccount"},
    {"title": "对方账户名称", "dataIndex": "analogueAccountName"},
    {"title": "业务类型", "dataIndex": "bizTypeName"},
    {"title": "报文类型", "dataIndex": "datagramTypeName"},
    {"title": "摘要", "dataIndex": "remark"},
]


def execute(
    page: int = 1,
    page_size: int = 10,
    account: str = "210401323",
    clearing_start_date: Optional[int] = None,
    clearing_end_date: Optional[int] = None,
    biz_start_date: Optional[str] = None,
    biz_end_date: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None,
    analogue_account: Optional[str] = None,
    analogue_account_name: Optional[str] = None,
    datagram_type: Optional[int] = None,
    remark: Optional[str] = None,
) -> dict:
    """账单查询（v2）- 查询备付金账单明细列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        account: 备付金账号，默认 210401323。
        clearing_start_date: 银行清算开始日期，格式 YYYYMMDD（整型，如 20260101）。默认近 3 个月。
        clearing_end_date: 银行清算结束日期，格式 YYYYMMDD（整型）。默认今天。
        biz_start_date: 银行业务开始日期，格式 "YYYYMMDD HH:mm:ss"。可选。
        biz_end_date: 银行业务结束日期，格式 "YYYYMMDD HH:mm:ss"。可选。
        min_amount: 最小金额（单位：分）。可选。
        max_amount: 最大金额（单位：分）。可选。
        analogue_account: 对方账户号。可选。
        analogue_account_name: 对方账户名。可选。
        datagram_type: 报文类型。可选。[UNRESOLVED: 枚举值未确认]
        remark: 摘要。可选。
    """
    url = f"{BASE_URL}/dispatcher/com.youzan.pay.hvp.api.payhvpapiservice.queryacsbill/"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    default_start = int(three_months_ago.strftime("%Y%m%d"))
    default_end = int(now.strftime("%Y%m%d"))

    payload = {
        "page": page,
        "pageSize": page_size,
        "account": account,
        "clearingStartDate": clearing_start_date if clearing_start_date is not None else default_start,
        "clearingEndDate": clearing_end_date if clearing_end_date is not None else default_end,
    }

    if biz_start_date is not None:
        payload["bizStartDate"] = biz_start_date
    if biz_end_date is not None:
        payload["bizEndDate"] = biz_end_date
    if min_amount is not None:
        payload["minAmount"] = min_amount
    if max_amount is not None:
        payload["maxAmount"] = max_amount
    if analogue_account is not None:
        payload["analogueAccount"] = analogue_account
    if analogue_account_name is not None:
        payload["analogueAccountName"] = analogue_account_name
    if datagram_type is not None:
        payload["datagramType"] = datagram_type
    if remark is not None:
        payload["remark"] = remark

    return client.post(url, payload)
