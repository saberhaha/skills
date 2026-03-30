"""
快捷回款-渠道 — 快捷回款-渠道（渠道账户余额查询）
来源：schemas/财务域/v3_快捷回款-渠道.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "channel": {
        "type": "enum",
        "required": True,
        "default": "PICC",
        "enum_values": {
            "PICC": "人保财险",
            "YG": "阳光融担",
            "OW": "国佳保理",
            "OW_INSU": "有赞信保"
        },
        "description": "渠道（默认为 PICC 人保财险）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns，detail 类型）
DISPLAY_COLUMNS = [
    {"title": "理赔户余额（元）/ 头寸户余额（元）", "dataIndex": "claimBalance"},
    {"title": "收入户余额（元）", "dataIndex": "payBalance"},
    {"title": "理赔户放款预警余额（元）", "dataIndex": "alarmBalance"},
]


def execute(
    channel: Literal["PICC", "YG", "OW", "OW_INSU"] = "PICC",
) -> dict:
    """查询快捷回款渠道账户余额（详情）。
    用户只需提供渠道，默认为人保财险（PICC）。

    Args:
        channel: 渠道。必填。枚举："PICC"=人保财险, "YG"=阳光融担, "OW"=国佳保理, "OW_INSU"=有赞信保。默认="PICC"。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.fin.quick.channelbalanceaccount"

    payload = {
        "channel": channel,
    }

    return client.post(url, payload)
