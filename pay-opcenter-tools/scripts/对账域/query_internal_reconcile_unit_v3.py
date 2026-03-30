"""
内部对账-单元 — v3 内部对账单元任务列表查询
来源：schemas/对账域/v3_内部对账_单元.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 注意：分页字段为嵌套结构 pageable.pageNo / pageable.pageSize
PARAM_SCHEMA = {
    "pageable.pageNo": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageable.pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
    "defId": {
        "type": "string",
        "required": False,
        "description": "对账双方"
    },
    "bizType": {
        "type": "string",
        "required": False,
        "description": "业务类型"
    },
    "status": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "I": "待对账",
            "P": "对账中",
            "C": "对账取消",
            "S": "核对一致",
            "F": "核对不一致",
            "E": "对账异常",
            "R": "可对账"
        },
        "description": "任务状态"
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "对账开始日期（格式：YYYY-MM-DD HH:mm:ss，时间部分补 00:00:00）"
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "对账结束日期（格式：YYYY-MM-DD HH:mm:ss，时间部分补 23:59:59）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "核对规则ID", "dataIndex": "taskId"},
    {"title": "核对双方", "dataIndex": "taskName"},
    {"title": "截止核对账期时间", "dataIndex": "endTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "状态", "dataIndex": "taskStatus"},
    {"title": "累计差异", "dataIndex": "allCount"},
]


def execute(
    page_no: int = 1,
    page_size: int = 10,
    def_id: Optional[str] = None,
    biz_type: Optional[str] = None,
    status: Optional[Literal["I", "P", "C", "S", "F", "E", "R"]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """内部对账-单元（v3）- 查询内部对账单元任务列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        page_no: 页码，默认 1。
        page_size: 每页条数，默认 10。
        def_id: 对账双方。可选。
        biz_type: 业务类型。可选。
        status: 任务状态。枚举：I=待对账, P=对账中, C=对账取消, S=核对一致, F=核对不一致, E=对账异常, R=可对账。
        start_date: 对账开始日期，格式 "YYYY-MM-DD HH:mm:ss"（时间部分补 00:00:00）。可选。
        end_date: 对账结束日期，格式 "YYYY-MM-DD HH:mm:ss"（时间部分补 23:59:59）。可选。
    """
    url = f"{BASE_URL}/v3/api/check-web-inner/payCheck/getTask"

    payload = {
        "pageable": {
            "pageNo": page_no,
            "pageSize": page_size,
        },
    }

    if def_id is not None:
        payload["defId"] = def_id
    if biz_type is not None:
        payload["bizType"] = biz_type
    if status is not None:
        payload["status"] = status
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date

    return client.post(url, payload)
