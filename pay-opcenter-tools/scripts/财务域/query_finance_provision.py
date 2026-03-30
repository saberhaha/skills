"""
财务备付金 — 财务备付金（查询备款记录）
来源：schemas/财务域/v1_财务备付金.json
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
        "description": "备款提交开始时间（毫秒时间戳）"
    },
    "endDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "备款提交结束时间（毫秒时间戳）"
    },
    "finishStartDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "备款完成开始时间（毫秒时间戳）"
    },
    "finishEndDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "备款完成结束时间（毫秒时间戳）"
    },
    "insSeq": {
        "type": "string",
        "required": False,
        "description": "头寸序号，来自 initReservePage 接口返回的 insSeqList"
    },
    "payeeAcctNo": {
        "type": "string",
        "required": False,
        "description": "银联备款账号（acctNo），来自 initReservePage 接口返回的 provisionsAccts"
    },
    "transStatus": {
        "type": "enum",
        "required": False,
        "enum_values": {"1": "成功", "2": "失败", "3": "备款中"},
        "description": "备款状态"
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
    {"title": "备款提交时间", "dataIndex": "startTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "备款完成时间", "dataIndex": "endTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "头寸序号", "dataIndex": "insSeq"},
    {"title": "银行备款账号", "dataIndex": "account"},
    {"title": "备款金额（元）", "dataIndex": "money"},
    {"title": "备款状态", "dataIndex": "status"},
    {"title": "失败原因", "dataIndex": "reason"},
    {"title": "操作人", "dataIndex": "operator"},
]


def execute(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    finish_start_date: Optional[int] = None,
    finish_end_date: Optional[int] = None,
    ins_seq: Optional[str] = None,
    payee_acct_no: Optional[str] = None,
    trans_status: Optional[Literal["1", "2", "3"]] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询财务备付金（备款）记录列表。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        start_date: 备款提交开始时间。可选。格式：毫秒时间戳（timestamp_ms）。
        end_date: 备款提交结束时间。可选。格式：毫秒时间戳（timestamp_ms）。
        finish_start_date: 备款完成开始时间。可选。格式：毫秒时间戳（timestamp_ms）。
        finish_end_date: 备款完成结束时间。可选。格式：毫秒时间戳（timestamp_ms）。
        ins_seq: 头寸序号（来自 initReservePage 辅助接口的 insSeqList）。可选。
        payee_acct_no: 银联备款账号（来自 initReservePage 辅助接口的 provisionsAccts）。可选。
        trans_status: 备款状态。可选。枚举："1"=成功, "2"=失败, "3"=备款中。
        current_page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.queryReserveList"

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
    if payee_acct_no is not None:
        payload["payeeAcctNo"] = payee_acct_no
    if trans_status is not None:
        payload["transStatus"] = trans_status

    return client.post(url, payload)
