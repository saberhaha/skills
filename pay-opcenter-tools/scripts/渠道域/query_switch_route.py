"""
切路由配置 — 查询切路由配置列表 (v1)
来源：schemas/渠道域/v1_切路由配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v1_切路由配置.json）
PARAM_SCHEMA = {
    "orgName": {"type": "string", "required": False, "default": "", "description": "合作商户"},
    "channelCode": {"type": "string", "required": False, "default": "", "description": "渠道编码"},
    "partner": {"type": "string", "required": False, "default": "", "description": "合作商户"},
    "pageIndex": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

# 数据展示列（来源：v1_切路由配置.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "渠道名称", "dataIndex": "channelName"},
    {"title": "渠道编码", "dataIndex": "channelCode"},
    {"title": "合作商户", "dataIndex": "partner"},
    {"title": "支付方式", "dataIndex": "payMode"},
    {"title": "渠道账户", "dataIndex": "accountCode"},
    {"title": "状态", "dataIndex": "statusName"},
    {"title": "创建时间", "dataIndex": "gmtCreate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "gmtUpdate", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "备注", "dataIndex": "description"},
]


def execute(
    org_name: Optional[str] = None,
    channel_code: Optional[str] = None,
    partner: Optional[str] = None,
    page_index: int = 1,
    page_size: int = 10,
) -> dict:
    """查询切路由配置列表 (v1)
    用户只需提供感兴趣的筛选条件，其余参数自动使用页面默认值。

    Args:
        org_name: 合作商户。可选。默认=""。
        channel_code: 渠道编码。可选。默认=""。
        partner: 合作商户。可选。默认=""。
        page_index: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/channel.switchRoute.query"

    payload = {
        "orgName": org_name if org_name is not None else "",
        "channelCode": channel_code if channel_code is not None else "",
        "partner": partner if partner is not None else "",
        "pageIndex": page_index,
        "pageSize": page_size,
    }

    return client.post(url, payload)
