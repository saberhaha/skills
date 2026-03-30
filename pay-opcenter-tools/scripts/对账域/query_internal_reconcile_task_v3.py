"""
内部对账-任务详情 — v3 内部对账单元任务详情查询
来源：schemas/对账域/v3_内部对账_任务详情.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "taskId": {
        "type": "string",
        "required": True,
        "description": "任务ID（路由参数，必填）"
    },
    "resultStatus": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "S": "一致",
            "F": "不一致",
            "L": "少数据"
        },
        "description": "是否对平"
    },
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
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "核心单据号", "dataIndex": "resultId"},
    {"title": "对账时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "是否对平", "dataIndex": "resultStatus"},
    {"title": "账单明细", "dataIndex": "detail"},
]


def execute(
    task_id: str,
    result_status: Optional[Literal["S", "F", "L"]] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """内部对账-任务详情（v3）- 查询内部对账单元任务详情列表。

    Args:
        task_id: 任务ID（必填）。
        result_status: 是否对平。枚举：S=一致, F=不一致, L=少数据。可选。
        page_no: 页码，默认 1。
        page_size: 每页条数，默认 10。
    """
    url = f"{BASE_URL}/v3/api/check-web-inner/payCheck/getTaskDetail"

    payload = {
        "taskId": task_id,
        "pageable": {
            "pageNo": page_no,
            "pageSize": page_size,
        },
    }

    if result_status is not None:
        payload["resultStatus"] = result_status

    return client.post(url, payload)
