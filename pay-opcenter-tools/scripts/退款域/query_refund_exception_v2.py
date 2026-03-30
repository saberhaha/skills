"""
退款异常查询 — 退款异常（资产中心）
来源：schemas/退款域/v2_退款异常.json
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
    "outBizNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "业务单号"
    },
    "payDetailNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "支付明细号"
    },
    "acquireNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "收单号"
    },
    "refundDetailNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "退款明细号"
    },
    "startTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm",
        "required": False,
        "default": "",
        "description": "创建时间开始（格式：YYYY-MM-DD HH:mm）"
    },
    "endTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm",
        "required": False,
        "default": "",
        "description": "创建时间结束（格式：YYYY-MM-DD HH:mm）"
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码（源码实际传参字段名 currentPage）"
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
    {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "业务单号", "dataIndex": "outBizNo"},
    {"title": "支付明细号", "dataIndex": "payDetailNo"},
    {"title": "收单号", "dataIndex": "acquireNo"},
    {"title": "退款明细号", "dataIndex": "refundDetailNo"},
    {"title": "退款金额(元)", "dataIndex": "refundAmount"},
    {"title": "原支付方式", "dataIndex": "payToolType"},
    {"title": "原支付渠道", "dataIndex": "payChannelApi"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    out_biz_no: Optional[str] = None,
    pay_detail_no: Optional[str] = None,
    acquire_no: Optional[str] = None,
    refund_detail_no: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询退款异常列表（v2，资产中心）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        out_biz_no: 业务单号。可选。
        pay_detail_no: 支付明细号。可选。
        acquire_no: 收单号。可选。
        refund_detail_no: 退款明细号。可选。
        start_time: 创建时间开始。格式：YYYY-MM-DD HH:mm。可选。
        end_time: 创建时间结束。格式：YYYY-MM-DD HH:mm。可选。
        current_page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/assetcenter.refund.queryExceptionOrder/"

    payload = {
        "outBizNo": out_biz_no if out_biz_no is not None else "",
        "payDetailNo": pay_detail_no if pay_detail_no is not None else "",
        "acquireNo": acquire_no if acquire_no is not None else "",
        "refundDetailNo": refund_detail_no if refund_detail_no is not None else "",
        "startTime": start_time if start_time is not None else "",
        "endTime": end_time if end_time is not None else "",
        "currentPage": current_page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
