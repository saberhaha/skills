"""
内部支付工具-历史订单 — 查询历史订单信息
来源：schemas/内部支付域/v3_内部支付工具-历史订单.json
版本：v3
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "orderNO": {
        "type": "string",
        "required": True,
        "description": "外部交易单号（注意：API参数名为大写O的 orderNO，来源于源码 IOldOrdersRequestParam.orderNO）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "外部订单号", "dataIndex": "orderNo"},
    {"title": "收单号", "dataIndex": "tradeNo"},
    {"title": "金额", "dataIndex": "money"},
    {"title": "描述", "dataIndex": "desc"},
    {"title": "结算状态", "dataIndex": "settlestate"},
    {"title": "交易状态", "dataIndex": "state"},
    {"title": "商户号", "dataIndex": "mchId"}
]

# 交易状态枚举
STATE_ENUM = {
    "0": "初始化",
    "2": "交易处理中",
    "3": "交易成功",
    "5": "转入退款",
    "98": "交易关闭",
    "99": "交易失败",
    "100": "交易完成"
}


def execute(
    order_no: str,
) -> dict:
    """查询历史订单信息

    根据外部交易单号查询历史订单信息，包括订单金额、状态、描述等。

    Args:
        order_no: 外部交易单号。必填。
    """
    # v3 版本使用 /v3/api/dispatch/invoke/ 前缀
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.oldOrders.query"

    # 注意：API参数名为大写O的 orderNO
    payload = {
        "orderNO": order_no
    }

    return client.post(url, payload)
