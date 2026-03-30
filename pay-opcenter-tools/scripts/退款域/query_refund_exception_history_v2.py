"""
退款异常历史查询
来源：schemas/退款域/v2_退款异常历史.json
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
    "operationType": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "长款收益": "长款收益",
            "原路退回": "原路退回",
            "退还卖家": "退还卖家",
            "退还买家": "退还买家",
        },
        "description": "操作类型（空字符串=全部）"
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
    "originPayToolType": {
        "type": "string",
        "required": False,
        "default": "",
        # UNRESOLVED: 枚举值由后端 assetcenter.refund.queryPayToolAndPayChannel 动态返回
        "description": "原支付方式（枚举值动态返回，无法静态枚举）"
    },
    "originPayChannelApi": {
        "type": "string",
        "required": False,
        "default": "",
        # UNRESOLVED: 枚举值由后端 assetcenter.refund.queryPayToolAndPayChannel 动态返回
        "description": "原支付渠道（枚举值动态返回，无法静态枚举）"
    },
    "startTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "default": "",
        "description": "创建时间开始（格式：YYYY-MM-DD HH:mm:ss）"
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
    {"title": "创建时间", "dataIndex": "startTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "业务单号", "dataIndex": "outBizNo"},
    {"title": "支付明细号", "dataIndex": "payDetailNo"},
    {"title": "收单号", "dataIndex": "acquireNo"},
    {"title": "退款明细号", "dataIndex": "refundDetailNo"},
    {"title": "退款金额(元)", "dataIndex": "refundAmount"},
    {"title": "退款单号", "dataIndex": "refundNo"},
    {"title": "原支付方式", "dataIndex": "payToolType"},
    {"title": "原支付渠道", "dataIndex": "payChannelApi"},
    {"title": "处理时间", "dataIndex": "endTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作状态", "dataIndex": "operationStatus"},
    {"title": "操作类型", "dataIndex": "operationType"},
    {"title": "操作人", "dataIndex": "operator"},
    {"title": "退款账户", "dataIndex": "refundAccount"},
]


def execute(
    out_biz_no: Optional[str] = None,
    pay_detail_no: Optional[str] = None,
    operation_type: Optional[Literal["长款收益", "原路退回", "退还卖家", "退还买家"]] = None,
    acquire_no: Optional[str] = None,
    refund_detail_no: Optional[str] = None,
    origin_pay_tool_type: Optional[str] = None,
    origin_pay_channel_api: Optional[str] = None,
    start_time: Optional[str] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询退款异常历史列表（v2）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        out_biz_no: 业务单号。可选。
        pay_detail_no: 支付明细号。可选。
        operation_type: 操作类型。可选。枚举：长款收益, 原路退回, 退还卖家, 退还买家。空=全部。
        acquire_no: 收单号。可选。
        refund_detail_no: 退款明细号。可选。
        origin_pay_tool_type: 原支付方式。可选。枚举值动态返回，无法静态枚举。
        origin_pay_channel_api: 原支付渠道。可选。枚举值动态返回，无法静态枚举。
        start_time: 创建时间开始。格式：YYYY-MM-DD HH:mm:ss。可选。
        current_page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/assetcenter.refund.queryHistoryExceptionOrder/"

    payload = {
        "outBizNo": out_biz_no if out_biz_no is not None else "",
        "payDetailNo": pay_detail_no if pay_detail_no is not None else "",
        "operationType": operation_type if operation_type is not None else "",
        "acquireNo": acquire_no if acquire_no is not None else "",
        "refundDetailNo": refund_detail_no if refund_detail_no is not None else "",
        "originPayToolType": origin_pay_tool_type if origin_pay_tool_type is not None else "",
        "originPayChannelApi": origin_pay_channel_api if origin_pay_channel_api is not None else "",
        "startTime": start_time if start_time is not None else "",
        "currentPage": current_page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
