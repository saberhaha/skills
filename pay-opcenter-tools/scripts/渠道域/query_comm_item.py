"""
通讯项管理 — 查询通讯项列表
来源：schemas/渠道域/v3_通讯项管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_通讯项管理.json）
PARAM_SCHEMA = {
    "itemType": {
        "type": "enum", "required": False, 
        "description": "配置项类型，选填（ACTOR=通信角色，RELATION=通信关系，TEMPLATE=通信模板）",
        "enum_values": {"ACTOR": "通信角色", "RELATION": "通信关系", "TEMPLATE": "通信模板"},
    },
    "configItemKey": {"type": "string", "required": False, "description": "配置项key，选填"},
    "configCode": {"type": "string", "required": False, "description": "配置编码，选填"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "一页获取的数据条数, 默认为 10"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码，页数据, 默认为 1"},
    "status": {
        "type": "enum", "required": False,
        "description": "可用状态，选填（USABLE=可用，DISABLE=不可用）",
        "enum_values": {"USABLE": "可用", "DISABLE": "不可用"},
    },
}

# 数据展示列（来源：v3_通讯项管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "配置项类型", "dataIndex": "itemType"},
    {"title": "配置项编码", "dataIndex": "configCode"},
    {"title": "配置项key", "dataIndex": "configItemKey"},
    {"title": "配置项value", "dataIndex": "configItemValue"},
    {"title": "拓展信息", "dataIndex": "extra"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    item_type: Optional[Literal['ACTOR', 'RELATION', 'TEMPLATE']] = None,
    config_item_key: Optional[str] = None,
    config_code: Optional[str] = None,
    status: Optional[Literal['USABLE', 'DISABLE']] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询通讯项列表
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        item_type: 配置项类型。可选。
        config_item_key: 配置项key。可选。
        config_code: 配置编码。可选。
        status: 可用状态。可选。枚举：USABLE=可用, DISABLE=不可用。
        page: 页码。可选。默认=1。
        page_size: 一页获取的数据条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/communication.item.pageQuery"

    payload = {
        "pageSize": page_size,
        "page": page,
    }
    if item_type is not None:
        payload["itemType"] = item_type
    if config_item_key is not None:
        payload["configItemKey"] = config_item_key
    if config_code is not None:
        payload["configCode"] = config_code
    if status is not None:
        payload["status"] = status

    return client.post(url, payload)
