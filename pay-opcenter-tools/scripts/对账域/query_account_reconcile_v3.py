"""
账户核对 — v3 渠道账户核对日汇总列表查询
来源：schemas/对账域/v3_账户核对.json
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
    "startBizDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-3M",
        "description": "入账开始日期（格式：YYYY-MM-DD）"
    },
    "endBizDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "入账结束日期（格式：YYYY-MM-DD）"
    },
    "instTypeList": {
        "type": "array",
        "required": False,
        "description": "核算主体列表"
    },
    "bizTypeList": {
        "type": "array",
        "required": False,
        "description": "账号名称列表"
    },
    "bizTypeNameList": {
        "type": "array",
        "required": False,
        "description": "业务类型列表"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "核算主体", "dataIndex": "instName"},
    {"title": "账号名称", "dataIndex": "feeName"},
    {"title": "账号", "dataIndex": "acctNoName"},
    {"title": "业务类型", "dataIndex": "bizTypeName"},
    {"title": "入账时间", "dataIndex": "bizDate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "业务笔数/金额", "dataIndex": "leftCount"},
    {"title": "财务笔数/金额", "dataIndex": "rightCount"},
    {"title": "对账成功笔数/金额", "dataIndex": "successCount"},
    {"title": "存疑笔数/金额", "dataIndex": "bufferCount"},
    {"title": "差错笔数/金额", "dataIndex": "diffCount"},
]


def execute(
    current_page: int = 1,
    page_size: int = 10,
    start_biz_date: Optional[str] = None,
    end_biz_date: Optional[str] = None,
    inst_type_list: Optional[List[str]] = None,
    biz_type_list: Optional[List[str]] = None,
    biz_type_name_list: Optional[List[str]] = None,
) -> dict:
    """账户核对（v3）- 查询渠道账户核对日汇总列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        current_page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        start_biz_date: 入账开始日期，格式 "YYYY-MM-DD"。默认近 3 个月。
        end_biz_date: 入账结束日期，格式 "YYYY-MM-DD"。默认今天。
        inst_type_list: 核算主体列表。可选。
        biz_type_list: 账号名称列表。可选。
        biz_type_name_list: 业务类型列表。可选。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/actual/queryDailyAcctSummaryList"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    payload = {
        "currentPage": current_page,
        "pageSize": page_size,
        "startBizDate": start_biz_date if start_biz_date else three_months_ago.strftime("%Y-%m-%d"),
        "endBizDate": end_biz_date if end_biz_date else now.strftime("%Y-%m-%d"),
    }

    if inst_type_list is not None:
        payload["instTypeList"] = inst_type_list
    if biz_type_list is not None:
        payload["bizTypeList"] = biz_type_list
    if biz_type_name_list is not None:
        payload["bizTypeNameList"] = biz_type_name_list

    return client.post(url, payload)
