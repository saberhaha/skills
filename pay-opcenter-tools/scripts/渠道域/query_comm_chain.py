"""
通讯链管理 — 查询通讯链列表
来源：schemas/渠道域/v3_通讯链管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_通讯链管理.json）
PARAM_SCHEMA = {
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "一页获取的数据条数, 默认为 10"},
    "ruleChainCode": {"type": "string", "required": True, "default": "", "description": "通信链编码，必填"},
    "page": {"type": "number", "required": False, "description": "页码，页数据, 默认为 1"},
    "grayCode": {"type": "string", "required": True, "default": "", "description": "灰度编码，必填"},
    "status": {
        "type": "enum", "required": False,
        "description": "可用状态，选填（USABLE=可用，DISABLE=不可用）",
        "enum_values": {"USABLE": "可用", "DISABLE": "不可用"},
    },
}

# 数据展示列（来源：v3_通讯链管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "通信链编号", "dataIndex": "ruleChainCode"},
    {"title": "灰度编码", "dataIndex": "grayCode"},
    {"title": "类型", "dataIndex": "type"},
    {"title": "执行阶段", "dataIndex": "phase"},
    {"title": "执行顺序", "dataIndex": "executionOrder"},
    {"title": "名称", "dataIndex": "name"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    rule_chain_code: str,
    gray_code: str,
    status: Optional[Literal['USABLE', 'DISABLE']] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询通讯链列表
    用户只需提供通信链编码和灰度编码，其余参数自动使用页面默认值。

    Args:
        rule_chain_code: 通信链编码。必填。
        gray_code: 灰度编码。必填。
        status: 可用状态。可选。枚举：USABLE=可用, DISABLE=不可用。
        page: 页码。可选。默认=1。
        page_size: 一页获取的数据条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/communication.ruleChain.pageQuery"

    payload = {
        "pageSize": page_size,
        "ruleChainCode": rule_chain_code,
        "page": page,
        "grayCode": gray_code,
    }
    if status is not None:
        payload["status"] = status

    return client.post(url, payload)
