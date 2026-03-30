"""
异常退款单/追偿单查询
来源：schemas/退款域/v2_异常退款单_追偿单.json
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
    "shopName": {
        "type": "string",
        "required": False,
        "description": "店铺名称"
    },
    "kdtId": {
        "type": "string",
        "required": False,
        "description": "店铺ID"
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "description": "订单编号"
    },
    "status": {
        "type": "string",
        "required": False,
        "default": "all",
        # UNRESOLVED: 除 "all" 外的枚举值由后端 RiskRefundService.riskRefundOrderStatusList 动态返回，无法静态枚举
        "description": "业务单状态（all=全部；其他枚举值动态返回，无法静态枚举）"
    },
    "operatorId": {
        "type": "string",
        "required": True,
        "description": "当前操作人ID"
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "退款业务单", "dataIndex": "riskRefundOrderNo"},
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "订单编号", "dataIndex": "eOrderNo"},
    {"title": "订单状态", "dataIndex": "eStatus"},
    {"title": "是否参与快速回款", "dataIndex": "quickSettleFlag"},
    {"title": "是否未确认收货", "dataIndex": "unReceiptedConfirmFlag"},
    {"title": "是否超时自动同意退款", "dataIndex": "timeOutAgreeRefundFlag"},
    {"title": "退款方式", "dataIndex": "refundType"},
    {"title": "退款业务单状态", "dataIndex": "status"},
    {"title": "退款金额（元）", "dataIndex": "refundAmount"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    operator_id: str,
    shop_name: Optional[str] = None,
    kdt_id: Optional[str] = None,
    order_no: Optional[str] = None,
    status: Optional[str] = "all",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询异常退款单/追偿单列表（v2）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        operator_id: 当前操作人ID。必填。
        shop_name: 店铺名称。可选。
        kdt_id: 店铺ID。可选。
        order_no: 订单编号。可选。
        status: 业务单状态。可选。"all"=全部；其他枚举值由后端动态返回，无法静态枚举。默认="all"。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/fin.shield.RiskRefundService.queryRiskRefundOrders"

    payload = {
        "operatorId": operator_id,
        "status": status if status is not None else "all",
        "page": page,
        "pageSize": page_size,
    }

    if shop_name is not None:
        payload["shopName"] = shop_name
    if kdt_id is not None:
        payload["kdtId"] = kdt_id
    if order_no is not None:
        payload["orderNo"] = order_no

    return client.post(url, payload)
