"""
支付信息详情 — 查询异常退款详情信息
来源：schemas/内部支付域/v1_支付信息详情.json
版本：v1
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "bizId": {"type": "string", "required": True, "description": "业务ID（从URL参数获取）"},
    "mistakeType": {"type": "string", "required": True, "description": "差错类型"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "序号", "dataIndex": "refundSort"},
    {"title": "退款流水号", "dataIndex": "tradeNo"},
    {"title": "申请时间", "dataIndex": "applyTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "订单更新时间", "dataIndex": "updatedTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "新退款方式", "dataIndex": "refundMethodDesc"},
    {"title": "新收款账号", "dataIndex": "accountNo"},
    {"title": "新收款户名", "dataIndex": "accountName"},
    {"title": "订单状态", "dataIndex": "refundStatusDesc"},
    {"title": "失败原因", "dataIndex": "refundMsg"}
]


def execute(
    biz_id: str,
    mistake_type: str,
) -> dict:
    """查询异常退款详情信息

    根据业务ID和差错类型查询异常退款的详细记录，包括退款流水、申请时间、退款方式、账号信息等。

    Args:
        biz_id: 业务ID。必填。从列表页获取。
        mistake_type: 差错类型。必填。
    """
    # v1 版本使用 /dispatcher/ 前缀
    url = f"{BASE_URL}/dispatcher/pay.mistake.refund.exception.queryMistakeDetail"

    payload = {
        "bizId": biz_id,
        "mistakeType": mistake_type
    }

    return client.post(url, payload)
