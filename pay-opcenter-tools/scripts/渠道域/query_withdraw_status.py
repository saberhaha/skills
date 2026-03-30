"""
提现渠道管理 — 查询提现状态详情 (v1)
来源：schemas/渠道域/v1_提现渠道管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v1_提现渠道管理.json）
PARAM_SCHEMA = {
    "withdrawNo": {
        "type": "string", "required": True,
        "description": "提现单号（sentData直接传提现单号字符串）",
    },
}

# 数据展示列（来源：v1_提现渠道管理.json → display.columns，type: detail）
DISPLAY_COLUMNS = [
    {"title": "提现单号", "dataIndex": "withdrawNo"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "提现描述", "dataIndex": "statusText"},
    {"title": "耗时(毫秒)", "dataIndex": "elapsed"},
    {"title": "请求报文", "dataIndex": "requestText"},
    {"title": "响应报文", "dataIndex": "responseText"},
]


def execute(
    withdraw_no: str,
) -> dict:
    """查询提现状态详情 (v1)
    用户提供提现单号，查询该笔提现在各渠道的处理状态详情。

    Args:
        withdraw_no: 提现单号。必填。（sentData直接传提现单号字符串）
    """
    url = f"{BASE_URL}/dispatcher/channel.withdrawStatus.queryAll"

    payload = {"sentData": withdraw_no}

    return client.post(url, payload)


def get_processor_status() -> dict:
    """查询前置机状态（辅助接口）
    无入参，返回前置机地址/状态/耗时/报文列表。
    来源：aux_apis → channel.processorStatus.query
    """
    url = f"{BASE_URL}/dispatcher/channel.processorStatus.query"

    return client.post(url, {})
