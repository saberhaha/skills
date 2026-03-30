"""
客户费率详情 — 客户费率详情
来源：schemas/财务域/v3_客户费率详情.json
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
    "activityOrderNo": {
        "type": "string",
        "required": True,
        "description": "定价方案订单号（从列表页跳转时携带的 query 参数）"
    },
    "activityNo": {
        "type": "string",
        "required": False,
        "default": "AN00028",
        "description": "活动编号（硬编码常量 rateActivityNo = 'AN00028'，自动注入）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns，detail 类型）
DISPLAY_COLUMNS = [
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "GMV分层", "dataIndex": "gmv"},
    {"title": "店铺名称", "dataIndex": "extra.shopName"},
    {"title": "营销人", "dataIndex": "extra.marketer"},
    {"title": "营销方式", "dataIndex": "extra.marketMode"},
    {"title": "备注", "dataIndex": "extra.remark"},
    {"title": "费率类型", "dataIndex": "feeType"},
    {"title": "配置时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "产品线", "dataIndex": "rightsConsumer"},
    {"title": "费率", "dataIndex": "value"},
    {"title": "费率状态", "dataIndex": "state"},
    {"title": "生效时间", "dataIndex": "startTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "到期时间", "dataIndex": "endTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    activity_order_no: str,
) -> dict:
    """查询客户费率详情。
    用户提供定价方案订单号，活动编号 AN00028 自动注入。

    Args:
        activity_order_no: 定价方案订单号。必填。从列表页跳转时携带的 query 参数。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.fin.aigis.queryrightslist"

    payload = {
        "activityOrderNo": activity_order_no,
        "activityNo": "AN00028",  # 硬编码常量，自动注入
    }

    return client.post(url, payload)
