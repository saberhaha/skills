"""
备付金额度映射列表查询 — 备付金额度映射列表查询
来源：schemas/备付金额度域/v2_备付金额度映射.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/备付金额度域/v2_备付金额度映射.json）
PARAM_SCHEMA = {
    "applyStartTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "映射提交开始时间（毫秒时间戳，moment.valueOf()）",
    },
    "applyEndTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "映射提交结束时间（毫秒时间戳）",
    },
    "finishStartTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "映射完成开始时间（毫秒时间戳）",
    },
    "finishEndTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "映射完成结束时间（毫秒时间戳）",
    },
    "acctNo": {
        "type": "string",
        "required": False,
        "default": None,  # 默认全部（不传此字段）
        "description": "映射账户号（下拉选择，选项来自 queryAcctNoList 接口动态加载）",
    },
    "status": {
        "type": "enum",
        "required": False,
        "default": None,  # 默认全部（不传此字段）
        "enum_values": {
            "WAITING_REVIEW": "待审批",
            "MAPPING": "映射中",
            "REVIEWED": "审批通过",
            "REJECTED": "已驳回",
            "SUCCESS": "映射成功",
            "FAIL": "映射失败",
        },
        "description": "映射状态（默认全部=不传此字段）",
    },
    "channelType": {
        "type": "enum",
        "required": False,
        "default": "ALL",
        "enum_values": {
            "ALL": "全部",
            "UNION_PAY": "银联",
            "NET_PAY": "网联",
        },
        "description": "映射渠道（默认ALL=全部）",
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码",
    },
    "size": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数",
    },
}

# 数据展示列（来源：schemas/备付金额度域/v2_备付金额度映射.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "映射渠道", "dataIndex": "channelTypeDesc"},
    {"title": "映射账户", "dataIndex": "acctNo"},
    {"title": "映射类型", "dataIndex": "mappingTypeDesc"},
    {"title": "映射提交时间", "dataIndex": "startAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "映射完成时间", "dataIndex": "endAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "映射金额", "dataIndex": "amount"},
    {"title": "映射状态", "dataIndex": "statusDesc"},
    {"title": "失败原因", "dataIndex": "errorMsg"},
    {"title": "交易号", "dataIndex": "transNo"},
    {"title": "经办人", "dataIndex": "applicant"},
    {"title": "审核人", "dataIndex": "reviewer"},
]


def execute(
    apply_start_time: Optional[int] = None,
    apply_end_time: Optional[int] = None,
    finish_start_time: Optional[int] = None,
    finish_end_time: Optional[int] = None,
    acct_no: Optional[str] = None,
    status: Optional[Literal["WAITING_REVIEW", "MAPPING", "REVIEWED", "REJECTED", "SUCCESS", "FAIL"]] = None,
    channel_type: Optional[Literal["ALL", "UNION_PAY", "NET_PAY"]] = "ALL",
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """备付金额度映射列表查询（v2）
    查询备付金额度映射记录，支持按映射账户、状态、渠道类型及时间范围筛选。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        apply_start_time: 映射提交开始时间。可选。毫秒时间戳（timestamp_ms）。
        apply_end_time: 映射提交结束时间。可选。毫秒时间戳（timestamp_ms）。
        finish_start_time: 映射完成开始时间。可选。毫秒时间戳（timestamp_ms）。
        finish_end_time: 映射完成结束时间。可选。毫秒时间戳（timestamp_ms）。
        acct_no: 映射账户号。可选。不传则查询全部账户。
        status: 映射状态。可选。枚举：WAITING_REVIEW=待审批, MAPPING=映射中,
                REVIEWED=审批通过, REJECTED=已驳回, SUCCESS=映射成功, FAIL=映射失败。
                默认不传=全部。
        channel_type: 映射渠道。可选。枚举：ALL=全部, UNION_PAY=银联, NET_PAY=网联。默认=ALL。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.quota.mapping.list"

    payload: dict = {
        "channelType": channel_type if channel_type is not None else "ALL",
        "currentPage": current_page,
        "size": size,
    }

    # 时间字段：格式为 timestamp_ms（毫秒时间戳），仅在用户传入时附加
    if apply_start_time is not None:
        payload["applyStartTime"] = apply_start_time
    if apply_end_time is not None:
        payload["applyEndTime"] = apply_end_time
    if finish_start_time is not None:
        payload["finishStartTime"] = finish_start_time
    if finish_end_time is not None:
        payload["finishEndTime"] = finish_end_time

    # 账户号：不传则后端返回全部（filterParams 过滤空值逻辑在此处模拟）
    if acct_no is not None:
        payload["acctNo"] = acct_no

    # 状态：不传则查全部
    if status is not None:
        payload["status"] = status

    return client.post(url, payload)
