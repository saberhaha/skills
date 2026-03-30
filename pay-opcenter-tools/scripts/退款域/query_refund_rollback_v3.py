"""
退款回退查询
来源：schemas/退款域/v3_退款回退查询.json
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
        "default": "",
        "description": "店铺名称"
    },
    "kdtId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺ID"
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "订单编号"
    },
    "status": {
        "type": "string",
        "required": False,
        "default": "",
        # UNRESOLVED: 枚举值由后端 /v3/api/refund/payback/getStatusList 动态返回
        "description": "申请单状态（枚举值动态返回，无法静态枚举；空=全部）"
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
    "desc": {
        "type": "boolean",
        "required": False,
        "description": "排序是否降序"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "退款申请单", "dataIndex": "caseNo"},
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "订单编号", "dataIndex": "orderNo"},
    {"title": "订单状态", "dataIndex": "eStatus"},
    {"title": "是否参与快速回款", "dataIndex": "quickSettleFlag"},
    {"title": "是否未确认收货", "dataIndex": "unReceiptedConfirmFlag"},
    {"title": "是否超时自动同意退款", "dataIndex": "timeOutAgreeRefundFlag"},
    {"title": "退款方式", "dataIndex": "refundType"},
    {"title": "退款申请单状态", "dataIndex": "status"},
    {"title": "退款金额", "dataIndex": "refundAmount"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    shop_name: Optional[str] = None,
    kdt_id: Optional[str] = None,
    order_no: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    desc: Optional[bool] = None,
) -> dict:
    """查询退款回退列表（v3）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        shop_name: 店铺名称。可选。
        kdt_id: 店铺ID。可选。
        order_no: 订单编号。可选。
        status: 申请单状态。可选。枚举值由后端动态返回，无法静态枚举。空=全部。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        desc: 排序是否降序。可选。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/refund.payback.searchData"

    payload = {
        "shopName": shop_name if shop_name is not None else "",
        "kdtId": kdt_id if kdt_id is not None else "",
        "orderNo": order_no if order_no is not None else "",
        "status": status if status is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    if desc is not None:
        payload["desc"] = desc

    return client.post(url, payload)
