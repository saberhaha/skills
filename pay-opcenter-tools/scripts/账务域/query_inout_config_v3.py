"""
收支配置管理查询 (v3)
来源：schemas/账务域/v3_收支配置管理.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "status": {
        "type": "enum", "required": True, "default": 1,
        "enum_values": {"0": "申请中", "1": "成功", "2": "驳回", "3": "删除"},
        "description": "申请状态（默认 Tab 为收支类型管理，对应 status=1 成功）"
    },
    "acctransCode": {
        "type": "number", "required": False,
        "description": "收支类型编码（用户输入 string，提交时转为 Number）"
    },
    "bizTypeCode": {"type": "string", "required": False, "description": "收单业务编码"},
    "typeName": {"type": "string", "required": False, "description": "收支类型名称"},
    "applyUser": {"type": "string", "required": False, "description": "申请人名称"},
    "alchemyTypeName": {"type": "string", "required": False, "description": "一本账展示名称"},
    "acctransTypeName": {"type": "string", "required": False, "description": "账务展示名称"},
    "verifyUser": {
        "type": "string", "required": False,
        "description": "审核人名称（仅在 status=1 收支类型管理 Tab 可用）"
    },
    "applyStartTime": {
        "type": "string", "format": "YYYY-MM-DD 00:00:00",
        "required": False, "description": "申请开始时间"
    },
    "applyEndTime": {
        "type": "string", "format": "YYYY-MM-DD 23:59:59",
        "required": False, "description": "申请结束时间"
    },
    "verifyStartTime": {
        "type": "string", "format": "YYYY-MM-DD 00:00:00",
        "required": False,
        "description": "审核开始时间（status=0 待审核 Tab 不传此字段）"
    },
    "verifyEndTime": {
        "type": "string", "format": "YYYY-MM-DD 23:59:59",
        "required": False,
        "description": "审核结束时间（status=0 待审核 Tab 不传此字段）"
    },
    "oldFlag": {
        "type": "enum", "required": False, "default": 1,
        "enum_values": {"1": "最新", "2": "不是最新"},
        "description": "是否最新标识（默认1=最新，仅在 status=1 收支类型管理 Tab 传入）"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 9, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns，status=1 收支类型管理Tab）
DISPLAY_COLUMNS = [
    {"title": "申请日期", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "审核日期", "dataIndex": "verifyTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "收支类型编码", "dataIndex": "acctransCode"},
    {"title": "收单业务编码", "dataIndex": "bizTypeCode"},
    {"title": "收支类型名称", "dataIndex": "typeName"},
    {"title": "账务展示名称", "dataIndex": "acctransTypeName"},
    {"title": "一本账展示名称", "dataIndex": "alchemyTypeName"},
    {"title": "一本账索引", "dataIndex": "alchemyIndex"},
    {"title": "申请人", "dataIndex": "applyUser"},
    {"title": "审核人", "dataIndex": "verifyUser"}
]


def execute(
    status: Literal[0, 1, 2, 3] = 1,
    acctrans_code: Optional[int] = None,
    biz_type_code: Optional[str] = None,
    type_name: Optional[str] = None,
    apply_user: Optional[str] = None,
    alchemy_type_name: Optional[str] = None,
    acctrans_type_name: Optional[str] = None,
    verify_user: Optional[str] = None,
    apply_start_time: Optional[str] = None,
    apply_end_time: Optional[str] = None,
    verify_start_time: Optional[str] = None,
    verify_end_time: Optional[str] = None,
    old_flag: Literal[1, 2] = 1,
    page: int = 1,
    page_size: int = 9,
) -> dict:
    """收支配置管理查询（v3）
    查询收支配置列表，默认查询 status=1（成功/收支类型管理 Tab）的最新配置。

    Args:
        status: 申请状态。枚举：0=申请中,1=成功,2=驳回,3=删除。默认 1。
        acctrans_code: 收支类型编码。可选。
        biz_type_code: 收单业务编码。可选。
        type_name: 收支类型名称。可选。
        apply_user: 申请人名称。可选。
        alchemy_type_name: 一本账展示名称。可选。
        acctrans_type_name: 账务展示名称。可选。
        verify_user: 审核人名称。可选（仅 status=1 时有效）。
        apply_start_time: 申请开始时间。可选。格式 YYYY-MM-DD 00:00:00。
        apply_end_time: 申请结束时间。可选。格式 YYYY-MM-DD 23:59:59。
        verify_start_time: 审核开始时间。可选（status!=0 时有效）。格式 YYYY-MM-DD 00:00:00。
        verify_end_time: 审核结束时间。可选（status!=0 时有效）。格式 YYYY-MM-DD 23:59:59。
        old_flag: 是否最新标识。枚举：1=最新,2=不是最新。默认 1（仅 status=1 时传入）。
        page: 页码。默认 1。
        page_size: 每页条数。默认 9。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.acctrans.getInoutConfigList"

    payload = {
        "status": status,
        "page": page,
        "pageSize": page_size
    }

    if acctrans_code is not None:
        payload["acctransCode"] = acctrans_code
    if biz_type_code:
        payload["bizTypeCode"] = biz_type_code
    if type_name:
        payload["typeName"] = type_name
    if apply_user:
        payload["applyUser"] = apply_user
    if alchemy_type_name:
        payload["alchemyTypeName"] = alchemy_type_name
    if acctrans_type_name:
        payload["acctransTypeName"] = acctrans_type_name
    # verifyUser 仅在 status=1 时传入
    if verify_user and status == 1:
        payload["verifyUser"] = verify_user
    if apply_start_time:
        payload["applyStartTime"] = apply_start_time
    if apply_end_time:
        payload["applyEndTime"] = apply_end_time
    # verifyStartTime/EndTime 仅在 status!=0 时传入
    if verify_start_time and status != 0:
        payload["verifyStartTime"] = verify_start_time
    if verify_end_time and status != 0:
        payload["verifyEndTime"] = verify_end_time
    # oldFlag 仅在 status=1 时传入
    if status == 1:
        payload["oldFlag"] = old_flag

    return client.post(url, payload)
