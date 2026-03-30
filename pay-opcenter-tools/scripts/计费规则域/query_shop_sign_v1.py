"""
店铺签约 — 查询店铺签约列表
来源：schemas/计费规则域/v1_店铺签约.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "mchId": {"type": "string", "required": False, "description": "商户ID"},
    "kdtId": {"type": "string", "required": False, "description": "店铺ID"},
    "packNo": {"type": "string", "required": False, "description": "计费包编号"},
    "state": {
        "type": "enum", "required": False,
        "enum_values": {"1": "生效", "2": "过期", "4": "待审核"},
        "description": "签约状态",
    },
    "userName": {"type": "string", "required": False, "description": "操作人"},
    "operateStartTime": {"type": "string", "required": False, "format": "YYYY-MM-DD HH:mm:ss", "description": "操作时间范围开始"},
    "operateEndTime": {"type": "string", "required": False, "format": "YYYY-MM-DD HH:mm:ss", "description": "操作时间范围结束"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "商户ID", "dataIndex": "mchId"},
    {"title": "计费包", "dataIndex": "packName"},
    {"title": "生效时间段", "dataIndex": "timeRange"},
    {"title": "操作人", "dataIndex": "createUser"},
    {"title": "操作时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "生效人", "dataIndex": "verifyUser"},
    {"title": "生效时间", "dataIndex": "beginEffectTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "备注", "dataIndex": "remark"},
]


def execute(
    mch_id: Optional[str] = None,
    kdt_id: Optional[str] = None,
    pack_no: Optional[str] = None,
    state: Optional[Literal["1", "2", "4"]] = None,
    user_name: Optional[str] = None,
    operate_start_time: Optional[str] = None,
    operate_end_time: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询店铺签约列表

    Args:
        mch_id: 商户ID。可选。
        kdt_id: 店铺ID。可选。
        pack_no: 计费包编号。可选。
        state: 签约状态。枚举：1=生效, 2=过期, 4=待审核。可选。
        user_name: 操作人。可选。
        operate_start_time: 操作时间范围开始，格式 YYYY-MM-DD HH:mm:ss。可选。
        operate_end_time: 操作时间范围结束，格式 YYYY-MM-DD HH:mm:ss。可选。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.fee.mch.signOps.queryKdtSignList"

    payload = {
        "page": page,
        "pageSize": page_size,
    }

    if mch_id is not None:
        payload["mchId"] = mch_id
    if kdt_id is not None:
        payload["kdtId"] = kdt_id
    if pack_no is not None:
        payload["packNo"] = pack_no
    if state is not None:
        payload["state"] = state
    if user_name is not None:
        payload["userName"] = user_name
    if operate_start_time is not None:
        payload["operateStartTime"] = operate_start_time
    if operate_end_time is not None:
        payload["operateEndTime"] = operate_end_time

    return client.post(url, payload)
