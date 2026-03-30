"""
差错诊断 — v3 渠道差错诊断列表查询
来源：schemas/对账域/v3_差错诊断.json
"""
import sys
import os
from typing import Optional, Literal, List
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
    "sortBy": {
        "type": "string",
        "required": False,
        "default": "tradeDate",
        "description": "排序字段，默认按交易日期排序"
    },
    "sortType": {
        "type": "enum",
        "required": False,
        "default": "desc",
        "enum_values": {
            "desc": "降序",
            "asc": "升序"
        },
        "description": "排序方向，默认降序"
    },
    "mistakeAcctTypeList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "差错类型列表（0=全部）"
    },
    "mistakeStatusList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "差错状态列表（0=全部）"
    },
    "channelTypeList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "资金渠道列表（0=全部）"
    },
    "bizTypeList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "业务类型列表（0=全部）"
    },
    "merchantList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "商户号列表（0=全部）"
    },
    "bizNo": {
        "type": "string",
        "required": False,
        "description": "原支付单号"
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-3M",
        "description": "交易开始日期（格式：YYYY-MM-DD）"
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "交易结束日期（格式：YYYY-MM-DD）"
    },
    "minAmount": {
        "type": "number",
        "required": False,
        "description": "最小金额（元输入，发送前转分）"
    },
    "maxAmount": {
        "type": "number",
        "required": False,
        "description": "最大金额（元输入，发送前转分）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "交易日期", "dataIndex": "tradeDate"},
    {"title": "原支付单号", "dataIndex": "originOrderNo"},
    {"title": "内部订单号", "dataIndex": "innerBizNo"},
    {"title": "渠道订单号", "dataIndex": "outerBizNo"},
    {"title": "资金渠道", "dataIndex": "channelName"},
    {"title": "商户号", "dataIndex": "merchantNo"},
    {"title": "差错类型", "dataIndex": "mistakeAcctTypeDesc"},
    {"title": "业务类型", "dataIndex": "bizTypeDesc"},
    {"title": "有赞金额(元)", "dataIndex": "innerBizAmount"},
    {"title": "渠道金额(元)", "dataIndex": "outerBizAmount"},
    {"title": "差错状态", "dataIndex": "mistakeStatusDesc"},
    {"title": "业务状态", "dataIndex": "handleStatusDesc"},
    {"title": "详情", "dataIndex": "detail"},
]


def execute(
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "tradeDate",
    sort_type: Literal["desc", "asc"] = "desc",
    mistake_acct_type_list: Optional[List[str]] = None,
    mistake_status_list: Optional[List[str]] = None,
    channel_type_list: Optional[List[str]] = None,
    biz_type_list: Optional[List[str]] = None,
    merchant_list: Optional[List[str]] = None,
    biz_no: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> dict:
    """差错诊断（v3）- 查询渠道差错诊断列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        sort_by: 排序字段，默认 "tradeDate"。
        sort_type: 排序方向，枚举：desc=降序, asc=升序。默认 desc。
        mistake_acct_type_list: 差错类型列表，传具体编码；默认 ["0"]（全部）。
        mistake_status_list: 差错状态列表，传具体编码；默认 ["0"]（全部）。
        channel_type_list: 资金渠道列表；默认 ["0"]（全部）。
        biz_type_list: 业务类型列表；默认 ["0"]（全部）。
        merchant_list: 商户号列表；默认 ["0"]（全部）。
        biz_no: 原支付单号。可选。
        start_date: 交易开始日期，格式 "YYYY-MM-DD"。默认近 3 个月。
        end_date: 交易结束日期，格式 "YYYY-MM-DD"。默认今天。
        min_amount: 最小金额（元）。可选，发送前自动转分。
        max_amount: 最大金额（元）。可选，发送前自动转分。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/diagnosic/getDiagnosic"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    payload = {
        "page": page,
        "pageSize": page_size,
        "sortBy": sort_by,
        "sortType": sort_type,
        "mistakeAcctTypeList": mistake_acct_type_list if mistake_acct_type_list is not None else ["0"],
        "mistakeStatusList": mistake_status_list if mistake_status_list is not None else ["0"],
        "channelTypeList": channel_type_list if channel_type_list is not None else ["0"],
        "bizTypeList": biz_type_list if biz_type_list is not None else ["0"],
        "merchantList": merchant_list if merchant_list is not None else ["0"],
        "startDate": start_date if start_date else three_months_ago.strftime("%Y-%m-%d"),
        "endDate": end_date if end_date else now.strftime("%Y-%m-%d"),
    }

    if biz_no is not None:
        payload["bizNo"] = biz_no
    # minAmount / maxAmount: 用户传元，接口要分（× 100）
    if min_amount is not None:
        payload["minAmount"] = int(min_amount * 100)
    if max_amount is not None:
        payload["maxAmount"] = int(max_amount * 100)

    return client.post(url, payload)
