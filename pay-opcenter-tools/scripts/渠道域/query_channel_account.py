"""
渠道账户管理 — 查询渠道账户列表
来源：schemas/渠道域/v3_渠道账户管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_渠道账户管理.json）
PARAM_SCHEMA = {
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "页数据量，默认10"},
    "payChannelApi": {"type": "string", "required": False, "default": "", "description": "支付工具编码"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码,默认1"},
    "channelInst": {
        "type": "enum", "required": False, "default": "", 
        "description": "支付渠道机构：银联/网联（union=银联，net_union=网联）",
        "enum_values": {"union": "银联", "net_union": "网联"},
    },
    "partnerId": {"type": "string", "required": False, "default": "", "description": "合作方id"},
    "channelCode": {"type": "string", "required": False, "default": "", "description": "渠道编码"},
}

# 数据展示列（来源：v3_渠道账户管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "支付方式api", "dataIndex": "payChannelApi"},
    {"title": "合作方", "dataIndex": "partnerId"},
    {"title": "渠道机构", "dataIndex": "channelInst"},
    {"title": "渠道编码", "dataIndex": "channelCode"},
    {"title": "渠道账号", "dataIndex": "accountCode"},
    {"title": "账号状态", "dataIndex": "status", "enum_values": {"0": "不可用", "1": "可用"}},
    {"title": "创建时间", "dataIndex": "gmtCreate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "gmtUpdate", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    pay_channel_api: Optional[str] = None,
    channel_inst: Optional[Literal['union', 'net_union']] = None,
    partner_id: Optional[str] = None,
    channel_code: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询渠道账户列表
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        pay_channel_api: 支付工具编码。可选。默认=""。
        channel_inst: 支付渠道机构：银联/网联。可选。默认=""。
        partner_id: 合作方id。可选。默认=""。
        channel_code: 渠道编码。可选。默认=""。
        page: 页码。可选。默认=1。
        page_size: 页数据量。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.channel.routeChannelAccount.queryList"

    payload = {
        "pageSize": page_size,
        "payChannelApi": pay_channel_api if pay_channel_api is not None else "",
        "page": page,
        "channelInst": channel_inst if channel_inst is not None else "",
        "partnerId": partner_id if partner_id is not None else "",
        "channelCode": channel_code if channel_code is not None else "",
    }

    return client.post(url, payload)
