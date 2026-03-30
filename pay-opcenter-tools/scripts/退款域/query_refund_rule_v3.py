"""
退款规则管理查询
来源：schemas/退款域/v3_退款规则管理.json
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
    "ruleNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "规则编号"
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
    "desc": {
        "type": "boolean",
        "required": False,
        "description": "排序是否降序"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "规则编号", "dataIndex": "ruleNo"},
    {"title": "业务方", "dataIndex": "bizSystem"},
    {"title": "业务类型", "dataIndex": "bizType"},
    {"title": "启用/禁用", "dataIndex": "state"},
    {"title": "出金账户", "dataIndex": "payer"},
    {"title": "目标账户", "dataIndex": "payeeType"},
    {"title": "是否追偿", "dataIndex": "recoverable"},
    {"title": "操作人", "dataIndex": "operator"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    rule_no: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    desc: Optional[bool] = None,
) -> dict:
    """查询退款规则管理列表（v3）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        rule_no: 规则编号。可选。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        desc: 排序是否降序。可选。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/refund.rules.searchData"

    payload = {
        "ruleNo": rule_no if rule_no is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    if desc is not None:
        payload["desc"] = desc

    return client.post(url, payload)
