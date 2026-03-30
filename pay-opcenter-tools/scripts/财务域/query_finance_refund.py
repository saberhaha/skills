"""
财务退款 — 财务退款（查询回款记录）
来源：schemas/财务域/v1_财务退款.json
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
    "startDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "回款提交开始时间（毫秒时间戳）"
    },
    "endDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "回款提交结束时间（毫秒时间戳）"
    },
    "finishStartDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "回款完成开始时间（毫秒时间戳）"
    },
    "finishEndDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "回款完成结束时间（毫秒时间戳）"
    },
    "insSeq": {
        "type": "string",
        "required": False,
        "description": "回款账户头寸序号，来自 initPage 接口返回的 insSeqList"
    },
    "transStatus": {
        "type": "enum",
        "required": False,
        "enum_values": {"1": "成功", "2": "失败", "3": "回款中"},
        "description": "回款状态"
    },
    "currentPage": {
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
    {"title": "回款提交时间", "dataIndex": "startTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "回款完成时间", "dataIndex": "endTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "回款账户", "dataIndex": "account"},
    {"title": "回款金额（元）", "dataIndex": "money"},
    {"title": "回款状态", "dataIndex": "status"},
    {"title": "失败原因", "dataIndex": "reason"},
    {"title": "交易号", "dataIndex": "transNo"},
    {"title": "操作人", "dataIndex": "operator"},
]


def execute(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    finish_start_date: Optional[int] = None,
    finish_end_date: Optional[int] = None,
    ins_seq: Optional[str] = None,
    trans_status: Optional[Literal["1", "2", "3"]] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询财务回款（退款）记录列表。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        start_date: 回款提交开始时间。可选。格式：毫秒时间戳（timestamp_ms）。
        end_date: 回款提交结束时间。可选。格式：毫秒时间戳（timestamp_ms）。
        finish_start_date: 回款完成开始时间。可选。格式：毫秒时间戳（timestamp_ms）。
        finish_end_date: 回款完成结束时间。可选。格式：毫秒时间戳（timestamp_ms）。
        ins_seq: 回款账户头寸序号（来自 initPage 辅助接口的 insSeqList）。可选。
        trans_status: 回款状态。可选。枚举："1"=成功, "2"=失败, "3"=回款中。
        current_page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.queryRefundList"

    payload: dict = {
        "currentPage": current_page,
        "pageSize": page_size,
    }

    # startDate 格式：timestamp_ms（毫秒时间戳）
    if start_date is not None:
        payload["startDate"] = start_date
    # endDate 格式：timestamp_ms
    if end_date is not None:
        payload["endDate"] = end_date
    # finishStartDate 格式：timestamp_ms
    if finish_start_date is not None:
        payload["finishStartDate"] = finish_start_date
    # finishEndDate 格式：timestamp_ms
    if finish_end_date is not None:
        payload["finishEndDate"] = finish_end_date
    if ins_seq is not None:
        payload["insSeq"] = ins_seq
    if trans_status is not None:
        payload["transStatus"] = trans_status

    return client.post(url, payload)
