"""
通讯关联管理 — 查询通讯关联列表
来源：schemas/渠道域/v3_通讯关联管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_通讯关联管理.json）
PARAM_SCHEMA = {
    "relationCode": {"type": "string", "required": False, "description": "通信关系编码，选填"},
    "senderCode": {"type": "string", "required": False, "description": "发送方编码，选填"},
    "receiverCode": {"type": "string", "required": False, "description": "接收方编码，选填"},
    "status": {
        "type": "enum", "required": False,
        "description": "可用状态，选填（USABLE=可用，DISABLE=不可用）",
        "enum_values": {"USABLE": "可用", "DISABLE": "不可用"},
    },
    "page": {"type": "number", "required": False, "description": "页码，默认为 1"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "一页获取的数据条数，默认为 10"},
}

# 数据展示列（来源：v3_通讯关联管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "关系编码", "dataIndex": "relationCode"},
    {"title": "父关系编码", "dataIndex": "parentCode"},
    {"title": "关系层级", "dataIndex": "relationLevel"},
    {"title": "描述", "dataIndex": "relationDesc"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "发送方", "dataIndex": "senderCode"},
    {"title": "接收方", "dataIndex": "receiverCode"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    relation_code: Optional[str] = None,
    sender_code: Optional[str] = None,
    receiver_code: Optional[str] = None,
    status: Optional[Literal['USABLE', 'DISABLE']] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询通讯关联列表
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        relation_code: 通信关系编码。可选。
        sender_code: 发送方编码。可选。
        receiver_code: 接收方编码。可选。
        status: 可用状态。可选。枚举：USABLE=可用, DISABLE=不可用。
        page: 页码。可选。默认=1。
        page_size: 一页获取的数据条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/communication.relation.pageQuery"

    payload = {
        "page": page,
        "pageSize": page_size,
    }
    if relation_code is not None:
        payload["relationCode"] = relation_code
    if sender_code is not None:
        payload["senderCode"] = sender_code
    if receiver_code is not None:
        payload["receiverCode"] = receiver_code
    if status is not None:
        payload["status"] = status

    return client.post(url, payload)
