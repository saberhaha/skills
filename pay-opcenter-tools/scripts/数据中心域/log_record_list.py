"""
日志记录列表 — 查询操作日志记录列表
来源：schemas/数据中心域/v1_日志记录列表.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "userName": {
        "type": "string",
        "required": True,
        "description": "操作人"
    },
    "menuName": {
        "type": "string",
        "required": True,
        "description": "操作菜单"
    },
    "startDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "today_00:00:00",
        "description": "操作开始时间（毫秒时间戳）"
    },
    "endDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "today_23:59:59",
        "description": "操作结束时间（毫秒时间戳）"
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
    }
}

# 数据展示列
DISPLAY_COLUMNS = [
    {"title": "序号", "dataIndex": "index"},
    {"title": "操作人", "dataIndex": "userName"},
    {"title": "操作时间", "dataIndex": "operTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作菜单", "dataIndex": "menuName"},
    {"title": "操作类型", "dataIndex": "operName"},
    {"title": "操作结果", "dataIndex": "operResult"}
]

def execute(
    user_name: str,
    menu_name: str,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    page: int = 1,
    page_size: int = 10
) -> dict:
    """查询操作日志记录列表

    根据操作人和操作菜单查询日志记录。用户只需提供核心查询条件（操作人、操作菜单），
    时间范围默认为当天（00:00:00 - 23:59:59）。

    Args:
        user_name: 操作人。必填。
        menu_name: 操作菜单。必填。
        start_date: 操作开始时间。毫秒时间戳。默认=今天00:00:00。
        end_date: 操作结束时间。毫秒时间戳。默认=今天23:59:59。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.log.query.page"

    # 处理默认值（当天时间范围）
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)

    if start_date is None:
        start_date = int(today_start.timestamp() * 1000)
    if end_date is None:
        end_date = int(today_end.timestamp() * 1000)

    # 构建请求参数
    payload = {
        "userName": user_name,
        "menuName": menu_name,
        "startDate": start_date,
        "endDate": end_date,
        "page": page,
        "pageSize": page_size
    }

    return client.post(url, payload)
