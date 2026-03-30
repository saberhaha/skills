"""
批量转账记录查询
来源：schemas/资金域/v3_批量转账.json
功能：查询批量转账记录列表，首屏默认查询近7天+执行成功的记录
"""
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "applyBeginTime": {
        "type": "string",
        "required": False,
        "format": "YYYY-MM-DD",
        "default": "近7天",
        "description": "申请开始时间"
    },
    "applyEndTime": {
        "type": "string",
        "required": False,
        "format": "YYYY-MM-DD",
        "default": "今天",
        "description": "申请结束时间"
    },
    "applyBy": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "申请人"
    },
    "checkBy": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "审核人"
    },
    "status": {
        "type": "enum",
        "required": False,
        "default": "执行成功",
        "enum_values": {
            "ALL": "全部（传空字符串给API）",
            "校验中": "校验中",
            "校验失败": "校验失败",
            "待复核": "待复核",
            "执行中": "执行中",
            "执行成功": "执行成功",
            "驳回": "驳回",
            "错误": "错误"
        },
        "description": "处理状态（默认'执行成功'；选择ALL时传空字符串给API）"
    },
    "batchNo": {
        "type": "string",
        "required": False,
        "description": "批次号（仅数字）"
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
    {"title": "批次号", "dataIndex": "batchId"},
    {"title": "申请时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "申请人", "dataIndex": "applyBy"},
    {"title": "审核时间", "dataIndex": "checkTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "审核人", "dataIndex": "checkBy"},
    {"title": "处理状态", "dataIndex": "status"}
]


def execute(
    apply_begin_time: Optional[str] = None,
    apply_end_time: Optional[str] = None,
    apply_by: Optional[str] = None,
    check_by: Optional[str] = None,
    status: Optional[str] = "执行成功",
    batch_no: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """查询批量转账记录列表

    Args:
        apply_begin_time: 申请开始时间。可选。格式：YYYY-MM-DD。默认：近7天
        apply_end_time: 申请结束时间。可选。格式：YYYY-MM-DD。默认：今天
        apply_by: 申请人。可选
        check_by: 审核人。可选
        status: 处理状态。可选。枚举：ALL=全部（传空）, 校验中, 校验失败, 待复核, 执行中, 执行成功, 驳回, 错误。默认：执行成功
        batch_no: 批次号。可选
        page: 页码。默认：1
        page_size: 每页条数。默认：10

    Returns:
        返回批量转账记录列表，包含批次号、申请时间、申请人、审核信息、处理状态等
    """
    # v3版本API路径
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.finance.batchtransfer"

    # 默认值处理
    now = datetime.now()
    if not apply_begin_time:
        apply_begin_time = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    if not apply_end_time:
        apply_end_time = now.strftime("%Y-%m-%d")

    # status特殊处理：ALL时传空字符串
    status_value = ""
    if status and status != "ALL":
        status_value = status

    # 构造payload，过滤空值
    payload = {
        "applyBeginTime": apply_begin_time,
        "applyEndTime": apply_end_time,
        "status": status_value,
        "page": page,
        "pageSize": page_size
    }

    if apply_by:
        payload["applyBy"] = apply_by
    if check_by:
        payload["checkBy"] = check_by
    if batch_no:
        payload["batchNo"] = batch_no

    # 过滤空字符串和None值
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}

    return client.post(url, payload)
