"""
发票红冲管理查询
来源：schemas/退款域/v3_发票红冲管理.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 注意：实际查询参数通过 filterBaseParams 对象传递
PARAM_SCHEMA = {
    "filterBaseParams": {
        "type": "object",
        "required": False,
        "description": "筛选参数对象（kdt、originInvoiceType、originInvoiceNo、redState、startTime、endTime、subject）"
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
    {"title": "申请单号", "dataIndex": "originInvoiceNo"},
    {"title": "店铺名/ID", "dataIndex": "kdtName"},
    {"title": "开票类型", "dataIndex": "typeText"},
    {"title": "申请时间", "dataIndex": "createAtStr", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "开票主体", "dataIndex": "subjectText"},
    {"title": "发票信息", "dataIndex": "ticketVO"},
    {"title": "申请信息", "dataIndex": "redApplyVO"},
    {"title": "发票状态", "dataIndex": "stateText"},
]


def execute(
    kdt: Optional[str] = None,
    origin_invoice_type: Optional[str] = None,
    origin_invoice_no: Optional[str] = None,
    red_state: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    subject: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询发票红冲管理列表（v3）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        kdt: 店铺标识（kdtId或kdtName）。可选。
        origin_invoice_type: 开票类型。可选。
        origin_invoice_no: 申请单号。可选。
        red_state: 发票状态。可选。
        start_time: 申请开始时间。可选。
        end_time: 申请结束时间。可选。
        subject: 开票主体。可选。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.ticket.redTicket.list"

    filter_base_params = {}
    if kdt is not None:
        filter_base_params["kdt"] = kdt
    if origin_invoice_type is not None:
        filter_base_params["originInvoiceType"] = origin_invoice_type
    if origin_invoice_no is not None:
        filter_base_params["originInvoiceNo"] = origin_invoice_no
    if red_state is not None:
        filter_base_params["redState"] = red_state
    if start_time is not None:
        filter_base_params["startTime"] = start_time
    if end_time is not None:
        filter_base_params["endTime"] = end_time
    if subject is not None:
        filter_base_params["subject"] = subject

    payload = {
        "page": page,
        "pageSize": page_size,
    }
    if filter_base_params:
        payload["filterBaseParams"] = filter_base_params

    return client.post(url, payload)
