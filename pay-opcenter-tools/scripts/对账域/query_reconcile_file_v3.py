"""
对账文件管理 — v3 渠道对账文件管理查询
来源：schemas/对账域/v3_对账文件管理.json
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
    {"title": "资金渠道", "dataIndex": "channelName"},
    {"title": "商户号", "dataIndex": "merchantNo"},
    {"title": "文件名称", "dataIndex": "fileName"},
    {"title": "文件账单日期", "dataIndex": "fileDate"},
    {"title": "上传进度", "dataIndex": "statusDesc"},
    {"title": "下载链接", "dataIndex": "downloadUrl"},
]


def execute(
    current_page: int = 1,
    page_size: int = 10,
    channel_type_list: Optional[List[str]] = None,
    merchant_list: Optional[List[str]] = None,
    start_check_date: Optional[str] = None,
    end_check_date: Optional[str] = None,
) -> dict:
    """对账文件管理（v3）- 查询渠道对账文件列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        current_page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        channel_type_list: 资金渠道列表，传具体编码；默认 ["0"]（全部）。
        merchant_list: 商户号列表，传具体商户号；默认 ["0"]（全部）。
        start_check_date: 文件账单开始日期，格式 "YYYY-MM-DD"。默认近 3 个月。
        end_check_date: 文件账单结束日期，格式 "YYYY-MM-DD"。默认今天。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/file/manage/getPayCheckFiles"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    payload = {
        "currentPage": current_page,
        "pageSize": page_size,
        "channelTypeList": channel_type_list if channel_type_list is not None else ["0"],
        "merchantList": merchant_list if merchant_list is not None else ["0"],
        "startCheckDate": start_check_date if start_check_date else three_months_ago.strftime("%Y-%m-%d"),
        "endCheckDate": end_check_date if end_check_date else now.strftime("%Y-%m-%d"),
    }

    return client.post(url, payload)
