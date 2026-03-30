"""
退款异常查询 — 退款异常
来源：schemas/退款域/v1_退款异常.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-365d",
        "description": "交易开始日期（默认近一年）"
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "交易结束日期"
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "description": "交易E单号"
    },
    "payDetailNo": {
        "type": "string",
        "required": False,
        "description": "支付明细单号"
    },
    "payMethodList": {
        "type": "array",
        "required": False,
        "description": "原支付方式列表（多选）"
    },
    "refundMethodList": {
        "type": "array",
        "required": False,
        "description": "新退款方式列表（多选）"
    },
    "mistakeStatusList": {
        "type": "array",
        "required": False,
        "description": "差错状态列表（多选，枚举值由 pay.mistake.refund.exception.getMeta 动态返回，无法静态枚举）"
    },
    "mistakeHandleStatusList": {
        "type": "array",
        "required": False,
        "description": "业务状态列表（多选，枚举值由 pay.mistake.refund.exception.getHandleStatus 动态返回，无法静态枚举）"
    },
    "channelPaymentNo": {
        "type": "string",
        "required": False,
        "description": "三方支付单号"
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
    "queryTag": {
        "type": "string",
        "required": False,
        "default": "2",
        "description": "查询标识（2=退款异常处理页）"
    },
    "sortBy": {
        "type": "string",
        "required": False,
        "default": "trade_date",
        "description": "排序字段"
    },
    "sortType": {
        "type": "enum",
        "required": False,
        "default": "desc",
        "enum_values": {"desc": "降序", "asc": "升序"},
        "description": "排序方向"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "交易日期", "dataIndex": "tradeDate", "format": "YYYY-MM-DD"},
    {"title": "支付明细单号", "dataIndex": "payDetailNo"},
    {"title": "退款明细单号", "dataIndex": "bizNo"},
    {"title": "三方支付单号", "dataIndex": "channelPaymentNo"},
    {"title": "交易E单号", "dataIndex": "orderNo"},
    {"title": "退款类型", "dataIndex": "refundTypeDesc"},
    {"title": "退款金额", "dataIndex": "refundAmount"},
    {"title": "原支付方式", "dataIndex": "payMethodDesc"},
    {"title": "新退款方式", "dataIndex": "refundMethodDesc"},
    {"title": "新收款账号", "dataIndex": "accountNo"},
    {"title": "新收款户名", "dataIndex": "accountName"},
    {"title": "收款人手机号", "dataIndex": "phoneNumber"},
    {"title": "差错状态", "dataIndex": "mistakeStatusDesc"},
    {"title": "业务状态", "dataIndex": "handleStatusDesc"},
]


def execute(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    order_no: Optional[str] = None,
    pay_detail_no: Optional[str] = None,
    pay_method_list: Optional[list] = None,
    refund_method_list: Optional[list] = None,
    mistake_status_list: Optional[list] = None,
    mistake_handle_status_list: Optional[list] = None,
    channel_payment_no: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    sort_type: Optional[Literal["desc", "asc"]] = "desc",
) -> dict:
    """查询退款异常列表（v1）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        start_date: 交易开始日期。格式：YYYY-MM-DD。默认=近一年。
        end_date: 交易结束日期。格式：YYYY-MM-DD。默认=今天。
        order_no: 交易E单号。可选。
        pay_detail_no: 支付明细单号。可选。
        pay_method_list: 原支付方式列表（多选）。可选。枚举值动态返回，无法静态枚举。
        refund_method_list: 新退款方式列表（多选）。可选。枚举值动态返回，无法静态枚举。
        mistake_status_list: 差错状态列表（多选）。可选。枚举值动态返回，无法静态枚举。
        mistake_handle_status_list: 业务状态列表（多选）。可选。枚举值动态返回，无法静态枚举。
        channel_payment_no: 三方支付单号。可选。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        sort_type: 排序方向。枚举：desc=降序, asc=升序。默认=desc。
    """
    url = f"{BASE_URL}/dispatcher/pay.mistake.refund.exception.queryMistakeRecords"

    now = datetime.now()
    payload = {
        "startDate": start_date if start_date else (now - timedelta(days=365)).strftime("%Y-%m-%d"),
        "endDate": end_date if end_date else now.strftime("%Y-%m-%d"),
        "page": page,
        "pageSize": page_size,
        "queryTag": "2",  # 固定值：退款异常处理页
        "sortBy": "trade_date",
        "sortType": sort_type if sort_type else "desc",
    }

    if order_no is not None:
        payload["orderNo"] = order_no
    if pay_detail_no is not None:
        payload["payDetailNo"] = pay_detail_no
    if pay_method_list is not None:
        payload["payMethodList"] = pay_method_list
    if refund_method_list is not None:
        payload["refundMethodList"] = refund_method_list
    if mistake_status_list is not None:
        payload["mistakeStatusList"] = mistake_status_list
    if mistake_handle_status_list is not None:
        payload["mistakeHandleStatusList"] = mistake_handle_status_list
    if channel_payment_no is not None:
        payload["channelPaymentNo"] = channel_payment_no

    return client.post(url, payload)
