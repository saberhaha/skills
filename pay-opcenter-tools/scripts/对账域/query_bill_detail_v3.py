"""
账单明细查询 — v3 渠道账单明细查询
来源：schemas/对账域/v3_账单明细查询.json
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
    "channelType": {
        "type": "string",
        "required": False,
        "default": "0",
        "description": "资金渠道（0=全部）"
    },
    "bizType": {
        "type": "string",
        "required": False,
        "default": "0",
        "description": "业务类型（0=全部）"
    },
    "merchantList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "商户号列表（0=全部）"
    },
    "startCheckDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-3M",
        "description": "文件账单开始日期（格式：YYYY-MM-DD）"
    },
    "endCheckDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "文件账单结束日期（格式：YYYY-MM-DD）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "对账日期", "dataIndex": "checkDate"},
    {"title": "资金渠道", "dataIndex": "channelTypeDesc"},
    {"title": "商户号", "dataIndex": "merchantNo"},
    {"title": "业务类型", "dataIndex": "bizTypeDesc"},
    {"title": "内部总笔数", "dataIndex": "innerCount"},
    {"title": "内部总金额(元)", "dataIndex": "innerAmount"},
    {"title": "渠道总笔数", "dataIndex": "channelCount"},
    {"title": "渠道总金额(元)", "dataIndex": "channelAmount"},
    {"title": "渠道总手续费(元)", "dataIndex": "channelFee"},
]


def execute(
    current_page: int = 1,
    page_size: int = 10,
    channel_type: str = "0",
    biz_type: str = "0",
    merchant_list: Optional[List[str]] = None,
    start_check_date: Optional[str] = None,
    end_check_date: Optional[str] = None,
) -> dict:
    """账单明细查询（v3）- 查询渠道账单明细汇总列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        current_page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        channel_type: 资金渠道，默认 "0"（全部）。
        biz_type: 业务类型，默认 "0"（全部）。
        merchant_list: 商户号列表；默认 ["0"]（全部）。
        start_check_date: 文件账单开始日期，格式 "YYYY-MM-DD"。默认近 3 个月。
        end_check_date: 文件账单结束日期，格式 "YYYY-MM-DD"。默认今天。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/billDetail/getBillDetail"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    payload = {
        "currentPage": current_page,
        "pageSize": page_size,
        "channelType": channel_type,
        "bizType": biz_type,
        "merchantList": merchant_list if merchant_list is not None else ["0"],
        "startCheckDate": start_check_date if start_check_date else three_months_ago.strftime("%Y-%m-%d"),
        "endCheckDate": end_check_date if end_check_date else now.strftime("%Y-%m-%d"),
    }

    return client.post(url, payload)
