"""
客户费率 — 客户费率
来源：schemas/财务域/v3_客户费率.json
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
    "userNo": {
        "type": "string",
        "required": False,
        "description": "店铺ID（kdtId）"
    },
    "startTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "费率配置开始时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
    "endTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "费率配置结束时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
    "extra.feeType": {
        "type": "enum",
        "required": False,
        "enum_values": {"打包费率": "打包费率", "单一费率": "单一费率"},
        "description": "费率类型"
    },
    "extra.marketMode": {
        "type": "enum",
        "required": False,
        "enum_values": {"自主营销": "自主营销", "KA联合营销": "KA联合营销"},
        "description": "营销方式"
    },
    "extra.marketer": {
        "type": "string",
        "required": False,
        "description": "营销人"
    },
    "activityNo": {
        "type": "string",
        "required": False,
        "default": "AN00028",
        "description": "活动编号（硬编码常量 rateActivityNo = 'AN00028'，自动注入）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "费率类型", "dataIndex": "feeType"},
    {"title": "配置时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "业务线", "dataIndex": "rightsConsumer"},
    {"title": "费率", "dataIndex": "value"},
    {"title": "费率状态", "dataIndex": "state"},
    {"title": "营销方式", "dataIndex": "marketMode"},
    {"title": "营销人", "dataIndex": "marketer"},
]


def execute(
    page: int = 1,
    page_size: int = 10,
    user_no: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    fee_type: Optional[Literal["打包费率", "单一费率"]] = None,
    market_mode: Optional[Literal["自主营销", "KA联合营销"]] = None,
    marketer: Optional[str] = None,
) -> dict:
    """查询客户费率列表。
    用户只需提供核心查询条件，活动编号 AN00028 自动注入，其余参数自动使用页面默认值。

    Args:
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
        user_no: 店铺ID（kdtId）。可选。
        start_time: 费率配置开始时间。可选。格式：YYYY-MM-DD HH:mm:ss，如 "2026-01-01 00:00:00"。
        end_time: 费率配置结束时间。可选。格式：YYYY-MM-DD HH:mm:ss，如 "2026-03-13 23:59:59"。
        fee_type: 费率类型。可选。枚举："打包费率", "单一费率"。
        market_mode: 营销方式。可选。枚举："自主营销", "KA联合营销"。
        marketer: 营销人。可选。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.fin.aigis.queryrightslist"

    payload: dict = {
        "page": page,
        "pageSize": page_size,
        "activityNo": "AN00028",  # 硬编码常量，自动注入
    }

    if user_no is not None:
        payload["userNo"] = user_no
    # startTime 格式：YYYY-MM-DD HH:mm:ss
    if start_time is not None:
        payload["startTime"] = start_time
    # endTime 格式：YYYY-MM-DD HH:mm:ss
    if end_time is not None:
        payload["endTime"] = end_time

    # extra 嵌套字段
    extra: dict = {}
    if fee_type is not None:
        extra["feeType"] = fee_type
    if market_mode is not None:
        extra["marketMode"] = market_mode
    if marketer is not None:
        extra["marketer"] = marketer
    if extra:
        payload["extra"] = extra

    return client.post(url, payload)
