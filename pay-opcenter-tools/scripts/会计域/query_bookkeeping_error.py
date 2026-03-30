"""
记账错误查询 — 记账错误查询
来源：schemas/会计域/v1_记账错误查询.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_记账错误查询.json）
PARAM_SCHEMA = {
    "status": {
        "type": "enum",
        "required": False,
        "enum_values": {"0": "异常", "1": "正常"},
        "description": "核对状态",
    },
    "inoutlogWaterNo": {
        "type": "string",
        "required": False,
        "description": "账务流水号",
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "description": "订单号",
    },
    "acquireNO": {
        "type": "string",
        "required": False,
        "description": "收单号（源码字段名为 acquireNO）",
    },
    "voucherId": {
        "type": "string",
        "required": False,
        "description": "记账凭证ID",
    },
    "recordingId": {
        "type": "string",
        "required": False,
        "description": "会计分录ID",
    },
    "voucherAmount": {
        "type": "string",
        "required": False,
        "description": "记账凭证金额",
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "核对开始时间",
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "核对结束时间",
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

# 数据展示列（来源：schemas/会计域/v1_记账错误查询.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "核对状态", "dataIndex": "status"},
    {"title": "账务流水号", "dataIndex": "inoutlogWaterNo"},
    {"title": "订单号", "dataIndex": "orderNo"},
    {"title": "收单号", "dataIndex": "acquireNo"},
    {"title": "记账凭证id", "dataIndex": "voucherId"},
    {"title": "会计分录id", "dataIndex": "recordingId"},
    {"title": "记账凭证金额", "dataIndex": "voucherAmount"},
    {"title": "结算金额", "dataIndex": "settlement"},
    {"title": "借贷金额", "dataIndex": "debitCreditAmount"},
    {"title": "核对时间", "dataIndex": "checkTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "结算时间", "dataIndex": "settleTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "账户类型", "dataIndex": "accountType"},
    {"title": "单据时间", "dataIndex": "billDate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "业务线id", "dataIndex": "parternerId"},
    {"title": "科目代码", "dataIndex": "subjectCode"},
    {"title": "借贷方向", "dataIndex": "creditDebitDir"},
]


def execute(
    status: Optional[Literal["0", "1"]] = None,
    inoutlog_water_no: Optional[str] = None,
    order_no: Optional[str] = None,
    acquire_no: Optional[str] = None,
    voucher_id: Optional[str] = None,
    recording_id: Optional[str] = None,
    voucher_amount: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """查询记账错误记录。
    用户只需提供核对状态、订单号等条件，其余参数自动使用页面默认值。

    Args:
        status: 核对状态。可选。枚举：0=异常, 1=正常。
        inoutlog_water_no: 账务流水号。可选。
        order_no: 订单号。可选。
        acquire_no: 收单号。可选（API 字段名为 acquireNO）。
        voucher_id: 记账凭证ID。可选。
        recording_id: 会计分录ID。可选。
        voucher_amount: 记账凭证金额。可选。
        start_date: 核对开始时间，格式 YYYY-MM-DD HH:mm:ss。可选。
        end_date: 核对结束时间，格式 YYYY-MM-DD HH:mm:ss。可选。
        page_no: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.accountingErrorQuery"

    payload: dict = {
        "pageNo": page_no,
        "pageSize": page_size,
    }
    if status is not None:
        payload["status"] = status
    if inoutlog_water_no is not None:
        payload["inoutlogWaterNo"] = inoutlog_water_no
    if order_no is not None:
        payload["orderNo"] = order_no
    if acquire_no is not None:
        payload["acquireNO"] = acquire_no  # 注意：源码字段名为 acquireNO（大写O）
    if voucher_id is not None:
        payload["voucherId"] = voucher_id
    if recording_id is not None:
        payload["recordingId"] = recording_id
    if voucher_amount is not None:
        payload["voucherAmount"] = voucher_amount
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date

    return client.post(url, payload)
