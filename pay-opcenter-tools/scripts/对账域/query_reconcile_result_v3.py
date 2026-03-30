"""
对账结果查询 — v3 渠道对账结果查询
来源：schemas/对账域/v3_对账结果查询.json
"""
import sys
import os
from typing import Optional, List
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "currentPage": {
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
    "startTradeDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-3M",
        "description": "交易开始日期（格式：YYYY-MM-DD）"
    },
    "endTradeDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "交易结束日期（格式：YYYY-MM-DD）"
    },
    "startCheckDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-3M",
        "description": "对账开始日期（格式：YYYY-MM-DD）"
    },
    "endCheckDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "对账结束日期（格式：YYYY-MM-DD）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "交易日期", "dataIndex": "tradeDate"},
    {"title": "对账日期", "dataIndex": "checkDate"},
    {"title": "资金渠道", "dataIndex": "channelTypeDesc"},
    {"title": "商户号", "dataIndex": "merchantNo"},
    {"title": "业务类型", "dataIndex": "bizTypeDesc"},
    {"title": "对方笔数/金额(元)", "dataIndex": "channel"},
    {"title": "我方笔数/金额(元)", "dataIndex": "inner"},
    {"title": "对平笔数/金额(元)", "dataIndex": "successCount"},
    {"title": "存疑笔数/金额(元)", "dataIndex": "bufferCount"},
    {"title": "差异笔数", "dataIndex": "diffCount"},
    {"title": "已处理差异笔数", "dataIndex": "dealCount"},
]


def execute(
    current_page: int = 1,
    page_size: int = 10,
    channel_type_list: Optional[List[str]] = None,
    biz_type_list: Optional[List[str]] = None,
    merchant_list: Optional[List[str]] = None,
    start_trade_date: Optional[str] = None,
    end_trade_date: Optional[str] = None,
    start_check_date: Optional[str] = None,
    end_check_date: Optional[str] = None,
) -> dict:
    """对账结果查询（v3）- 查询渠道对账结果汇总列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        current_page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        channel_type_list: 资金渠道列表；默认 ["0"]（全部）。
        biz_type_list: 业务类型列表；默认 ["0"]（全部）。
        merchant_list: 商户号列表；默认 ["0"]（全部）。
        start_trade_date: 交易开始日期，格式 "YYYY-MM-DD"。默认近 3 个月。
        end_trade_date: 交易结束日期，格式 "YYYY-MM-DD"。默认今天。
        start_check_date: 对账开始日期，格式 "YYYY-MM-DD"。默认近 3 个月。
        end_check_date: 对账结束日期，格式 "YYYY-MM-DD"。默认今天。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/payCheck/getChannelResult"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)
    default_start = three_months_ago.strftime("%Y-%m-%d")
    default_end = now.strftime("%Y-%m-%d")

    payload = {
        "currentPage": current_page,
        "pageSize": page_size,
        "channelTypeList": channel_type_list if channel_type_list is not None else ["0"],
        "bizTypeList": biz_type_list if biz_type_list is not None else ["0"],
        "merchantList": merchant_list if merchant_list is not None else ["0"],
        "startTradeDate": start_trade_date if start_trade_date else default_start,
        "endTradeDate": end_trade_date if end_trade_date else default_end,
        "startCheckDate": start_check_date if start_check_date else default_start,
        "endCheckDate": end_check_date if end_check_date else default_end,
    }

    return client.post(url, payload)
