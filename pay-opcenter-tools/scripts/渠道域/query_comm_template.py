"""
通讯模板管理 — 查询通讯模板列表
来源：schemas/渠道域/v3_通讯模板管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_通讯模板管理.json）
PARAM_SCHEMA = {
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "一页获取的数据条数, 默认为 10"},
    "page": {"type": "number", "required": False, "description": "页码，页数据, 默认为 1"},
    "templateCode": {"type": "string", "required": False, "description": "通信模板编码，选填"},
    "api": {"type": "string", "required": False, "description": "通信场景(api)，选填"},
    "status": {
        "type": "enum", "required": False,
        "description": "可用状态，选填（USABLE=可用，DISABLE=不可用）",
        "enum_values": {"USABLE": "可用", "DISABLE": "不可用"},
    },
}

# 数据展示列（来源：v3_通讯模板管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "模板编码", "dataIndex": "templateCode"},
    {"title": "通信场景", "dataIndex": "api"},
    {"title": "描述", "dataIndex": "templateDesc"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    template_code: Optional[str] = None,
    api: Optional[str] = None,
    status: Optional[Literal['USABLE', 'DISABLE']] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询通讯模板列表
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        template_code: 通信模板编码。可选。
        api: 通信场景(api)。可选。
        status: 可用状态。可选。枚举：USABLE=可用, DISABLE=不可用。
        page: 页码。可选。默认=1。
        page_size: 一页获取的数据条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/communication.template.pageQuery"

    payload = {
        "pageSize": page_size,
        "page": page,
    }
    if template_code is not None:
        payload["templateCode"] = template_code
    if api is not None:
        payload["api"] = api
    if status is not None:
        payload["status"] = status

    return client.post(url, payload)
