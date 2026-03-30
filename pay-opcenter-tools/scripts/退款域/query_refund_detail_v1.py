"""
退款详情查询 — 退款详情
来源：schemas/退款域/v1_退款详情.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "bizId": {
        "type": "string",
        "required": True,
        "description": "退款明细单号"
    },
    "mistakeType": {
        "type": "string",
        "required": True,
        "description": "差错类型"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "操作时间", "dataIndex": "opsTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作方式", "dataIndex": "opsName"},
    {"title": "处理状态", "dataIndex": "operateStatusDesc"},
    {"title": "操作详情", "dataIndex": "opsDetail"},
    {"title": "操作人", "dataIndex": "operatorName"},
    {"title": "备注", "dataIndex": "remark"},
    {"title": "序号", "dataIndex": "refundSort"},
    {"title": "退款流水号", "dataIndex": "tradeNo"},
    {"title": "申请时间", "dataIndex": "applyTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "订单更新时间", "dataIndex": "updatedTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "新退款方式", "dataIndex": "refundMethodDesc"},
    {"title": "新收款账号", "dataIndex": "accountNo"},
    {"title": "新收款户名", "dataIndex": "accountName"},
    {"title": "订单状态", "dataIndex": "refundStatusDesc"},
    {"title": "失败原因", "dataIndex": "refundMsg"},
]


def execute(
    biz_id: str,
    mistake_type: str,
) -> dict:
    """查询退款详情（v1）。
    根据退款明细单号和差错类型查询退款操作历史及退款订单详情。

    Args:
        biz_id: 退款明细单号。必填。
        mistake_type: 差错类型。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.mistake.refund.exception.queryMistakeDetail"

    payload = {
        "bizId": biz_id,
        "mistakeType": mistake_type,
    }

    return client.post(url, payload)
