"""
快捷退款-关闭扣款查询
来源：schemas/退款域/v3_快捷退款-关闭扣款.json
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
    "refundId": {
        "type": "string",
        "required": True,
        "description": "退款单号"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "订单号", "dataIndex": "eOrderNo"},
    {"title": "退款单号", "dataIndex": "refundId"},
    {"title": "店铺名称", "dataIndex": "kdtName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "退款金额", "dataIndex": "refundAmount"},
    {
        "title": "退款状态",
        "dataIndex": "status",
        "enum_values": {
            "INIT": "初始化",
            "EFFECTING": "生效中",
            "EFFECT": "已生效",
            "CANCELING": "取消中",
            "INVALID": "废弃",
            "RETURNED_BUYER": "已退买家",
            "WAIT_BUYER_RETURN": "待买家退",
            "BUYER_RETURNED": "买家已退",
            "BUYER_BAD_DEBT": "买家坏账",
            "WAIT_MCH_RETURN": "待商家退",
            "MCH_RETURNED": "商家已退",
            "MCH_RECOVERY": "商家追偿",
            "MCH_BAD_DEBT": "商家坏账",
        }
    },
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    refund_id: str,
) -> dict:
    """查询快捷退款-关闭扣款信息（v3）。
    根据退款单号查询快捷退款详情。

    Args:
        refund_id: 退款单号。必填。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/fast-refund.queryFastRefundOrderByRefundId"

    payload = {
        "refundId": refund_id,
    }

    return client.post(url, payload)
