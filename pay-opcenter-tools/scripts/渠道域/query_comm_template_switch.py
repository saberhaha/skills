"""
通讯模板开关管理 — 查询通讯模板开关列表
来源：schemas/渠道域/v3_通讯模板开关管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_通讯模板开关管理.json）
PARAM_SCHEMA = {
    "templateCode": {"type": "string", "required": True, "description": "通信模板编码，必填"},
    "relationCode": {"type": "string", "required": False, "description": "通信关系编码，选填"},
    "status": {
        "type": "enum", "required": False,
        "description": "可用状态，选填（USABLE=可用，DISABLE=不可用）",
        "enum_values": {"USABLE": "可用", "DISABLE": "不可用"},
    },
    "env": {
        "type": "enum", "required": False,
        "description": "环境标识，选填（prod=线上，pre=预发，qa=QA）",
        "enum_values": {"prod": "线上", "pre": "预发", "qa": "QA"},
    },
    "page": {"type": "number", "required": False, "description": "页码，默认为 1"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "一页获取的数据条数，默认为 10"},
}

# 数据展示列（来源：v3_通讯模板开关管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "模板编码", "dataIndex": "templateCode"},
    {"title": "通信链编码", "dataIndex": "ruleChainCode"},
    {"title": "通信关系编码", "dataIndex": "relationCode"},
    {"title": "灰度编码", "dataIndex": "grayCode"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "环境", "dataIndex": "env"},
    {"title": "权重/优先级", "dataIndex": "weight/priority"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    template_code: str,
    relation_code: Optional[str] = None,
    status: Optional[Literal['USABLE', 'DISABLE']] = None,
    env: Optional[Literal['prod', 'pre', 'qa']] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询通讯模板开关列表
    用户只需提供通信模板编码，其余参数自动使用页面默认值。

    Args:
        template_code: 通信模板编码。必填。
        relation_code: 通信关系编码。可选。
        status: 可用状态。可选。枚举：USABLE=可用, DISABLE=不可用。
        env: 环境标识。可选。枚举：prod=线上, pre=预发, qa=QA。
        page: 页码。可选。默认=1。
        page_size: 一页获取的数据条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/communication.templateSwitch.pageQuery"

    payload = {
        "templateCode": template_code,
        "page": page,
        "pageSize": page_size,
    }
    if relation_code is not None:
        payload["relationCode"] = relation_code
    if status is not None:
        payload["status"] = status
    if env is not None:
        payload["env"] = env

    return client.post(url, payload)
