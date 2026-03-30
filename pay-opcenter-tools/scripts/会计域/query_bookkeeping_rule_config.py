"""
记账规则配置 — 记账规则配置
来源：schemas/会计域/v1_记账规则配置.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_记账规则配置.json）
# 注：前端将 '0' 映射为空传参（即不传该字段），这里使用 None 表示不传
PARAM_SCHEMA = {
    "pageNo": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码",
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数",
    },
    "accountingCode": {
        "type": "string",
        "required": False,
        "description": "记账码（前端将 '0' 映射为空，即不传）",
    },
    "channelCode": {
        "type": "string",
        "required": False,
        "description": "渠道码（前端将 '0' 映射为空，即不传）",
    },
}

# 数据展示列（来源：schemas/会计域/v1_记账规则配置.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "记账码", "dataIndex": "bookkeepingCode"},
    {"title": "渠道码", "dataIndex": "channelCode"},
    {"title": "渠道名称", "dataIndex": "channelName"},
    {"title": "内部户类别", "dataIndex": "houseHoldTypeValue"},
    {"title": "借方科目", "dataIndex": "debtSubjectValue"},
    {"title": "借方账户", "dataIndex": "debtAccount"},
    {"title": "贷方科目", "dataIndex": "creditSubjectValue"},
    {"title": "贷方账户", "dataIndex": "creditAccount"},
    {"title": "可用标识", "dataIndex": "availableLogo"},
    {"title": "备注信息", "dataIndex": "remark"},
]


def execute(
    accounting_code: Optional[str] = None,
    channel_code: Optional[str] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """查询记账规则配置列表。
    用户只需提供记账码或渠道码筛选条件，其余参数自动使用页面默认值。

    Args:
        accounting_code: 记账码。可选（传 '0' 或不传均表示全部）。
        channel_code: 渠道码。可选（传 '0' 或不传均表示全部）。
        page_no: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/accounting.rule.list"

    payload: dict = {
        "pageNo": page_no,
        "pageSize": page_size,
    }
    # 前端将 '0' 映射为空（不传），这里遵循同样逻辑
    if accounting_code is not None and accounting_code != "0":
        payload["accountingCode"] = accounting_code
    if channel_code is not None and channel_code != "0":
        payload["channelCode"] = channel_code

    return client.post(url, payload)
