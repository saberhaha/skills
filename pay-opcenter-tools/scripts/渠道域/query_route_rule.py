"""
路由规则管理 — 查询路由规则列表
来源：schemas/渠道域/v3_路由规则管理.json
"""
import sys
import os
from typing import Optional

# 将项目根目录加入 sys.path 以支持 shared 模块导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_路由规则管理.json）
PARAM_SCHEMA = {
    "page": {"type": "number", "required": True, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": True, "default": 10, "description": "页数据量"},
    "grayCode": {"type": "string", "required": True, "description": "灰度码"},
    "payChannelApi": {"type": "string", "required": True, "description": "支付方式api"},
}

# 数据展示列（来源：v3_路由规则管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "支付方式api", "dataIndex": "payChannelApi"},
    {"title": "类型", "dataIndex": "type"},
    {"title": "执行阶段", "dataIndex": "phase"},
    {"title": "执行层级", "dataIndex": "level"},
    {"title": "执行顺序", "dataIndex": "order"},
    {"title": "名称", "dataIndex": "name"},
    {"title": "灰度码", "dataIndex": "grayCode"},
    {"title": "状态", "dataIndex": "status", "enum_values": {"1": "可用", "0": "不可用"}},
    {"title": "创建时间", "dataIndex": "gmtCreate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "gmtUpdate", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    gray_code: str,
    pay_channel_api: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询路由规则列表
    用户只需提供灰度码和支付方式api，其余参数自动使用页面默认值。

    Args:
        gray_code: 灰度码。必填。
        pay_channel_api: 支付方式api。必填。
        page: 页码。可选。默认=1。
        page_size: 页数据量。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.channel.routeRule.queryList"

    payload = {
        "page": page,
        "pageSize": page_size,
        "grayCode": gray_code,
        "payChannelApi": pay_channel_api,
    }

    return client.post(url, payload)
