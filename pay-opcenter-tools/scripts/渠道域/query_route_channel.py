"""
路由渠道管理 — 查询路由渠道列表
来源：schemas/渠道域/v3_路由渠道管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_路由渠道管理.json）
PARAM_SCHEMA = {
    "payMode": {
        "type": "enum", "required": False, "default": "", 
        "description": "支付模式：自有/代销（self=自有，proxy=代销）",
        "enum_values": {"self": "自有", "proxy": "代销"},
    },
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "页数据量，默认10"},
    "payChannelApi": {"type": "string", "required": False, "default": "", "description": "支付工具编码"},
    "page": {"type": "number", "required": False, "description": "页码,默认1"},
    "channelInst": {
        "type": "enum", "required": False, "default": "", 
        "description": "支付渠道机构：银联/网联（union=银联，net_union=网联）",
        "enum_values": {"union": "银联", "net_union": "网联"},
    },
}

# 数据展示列（来源：v3_路由渠道管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "支付方式api", "dataIndex": "payChannelApi"},
    {"title": "支付模式", "dataIndex": "payMode"},
    {"title": "支付工具", "dataIndex": "payMedium"},
    {"title": "渠道机构", "dataIndex": "channelInst"},
    {"title": "支付形式", "dataIndex": "payPattern"},
    {"title": "渠道编码", "dataIndex": "channelCode"},
    {"title": "渠道状态", "dataIndex": "status", "enum_values": {"0": "不可用", "1": "可用"}},
    {"title": "百分比/权重/优先级", "dataIndex": "percent/weight/priority"},
    {"title": "创建时间", "dataIndex": "gmtCreate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "gmtUpdate", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    pay_mode: Optional[Literal['self', 'proxy']] = None,
    pay_channel_api: Optional[str] = None,
    channel_inst: Optional[Literal['union', 'net_union']] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询路由渠道列表
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        pay_mode: 支付模式(自有、代销)。可选。默认=""。
        pay_channel_api: 支付工具编码。可选。默认=""。
        channel_inst: 支付渠道机构：银联/网联。可选。默认=""。
        page: 页码。可选。默认=1。
        page_size: 页数据量。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.channel.routeChannel.queryList"

    payload = {
        "payMode": pay_mode if pay_mode is not None else "",
        "pageSize": page_size,
        "payChannelApi": pay_channel_api if pay_channel_api is not None else "",
        "page": page,
        "channelInst": channel_inst if channel_inst is not None else "",
    }

    return client.post(url, payload)
