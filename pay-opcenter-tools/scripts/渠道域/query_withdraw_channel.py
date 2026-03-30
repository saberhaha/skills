"""
提现渠道管理 — 查询提现渠道列表 (v2)
来源：schemas/渠道域/v2_提现渠道管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v2_提现渠道管理.json）
PARAM_SCHEMA = {
    "channelName": {"type": "string", "required": False, "default": "", "description": "渠道名称"},
    "channelType": {
        "type": "enum", "required": False,
        "default": "出金渠道",
        "enum_values": {"出金渠道": "出金渠道"},
        "description": "渠道类型",
    },
    "currentPage": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

# 数据展示列（来源：v2_提现渠道管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "渠道名称", "dataIndex": "channelName"},
    {"title": "渠道编码", "dataIndex": "channelCode"},
    {"title": "渠道类型", "dataIndex": "channelType", "enum_values": {"出金渠道": "出金渠道"}},
    {"title": "渠道费率", "dataIndex": "fee"},
    {"title": "渠道新增时间", "dataIndex": "createAt"},
    {"title": "渠道维护类型", "dataIndex": "maintenanceType"},
    {"title": "渠道状态", "dataIndex": "channelStatus"},
]


def execute(
    channel_name: Optional[str] = None,
    channel_type: Optional[str] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询提现渠道列表 (v2)
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        channel_name: 渠道名称。可选。默认=""。
        channel_type: 渠道类型。可选。枚举：出金渠道。默认=出金渠道。
        current_page: 当前页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.queryChannelList/"

    payload = {
        "channelName": channel_name if channel_name is not None else "",
        "channelType": channel_type if channel_type is not None else "出金渠道",  # 默认：出金渠道
        "currentPage": current_page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
