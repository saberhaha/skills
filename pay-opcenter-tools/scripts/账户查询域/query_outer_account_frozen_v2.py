"""
外部账户冻结明细查询（不可用余额明细查询）(v2)
来源：schemas/账户查询域/v2_外部账户冻结明细查询.json
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "acctNo": {
        "type": "string", "required": True,
        "description": "资金账号"
    },
    "beginTime": {
        "type": "number", "format": "timestamp_s",
        "required": False, "default": "now-7d",
        "description": "查询开始时间（秒级Unix时间戳），默认近7天"
    },
    "endTime": {
        "type": "number", "format": "timestamp_s",
        "required": False, "default": "now",
        "description": "查询结束时间（秒级Unix时间戳）"
    },
    "pageNo": {
        "type": "number", "required": False, "default": 1,
        "description": "页码"
    },
    "pageSize": {
        "type": "number", "required": False, "default": 10,
        "description": "每页条数"
    },
}

DISPLAY_COLUMNS = [
    {"title": "交易时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "冻结状态", "dataIndex": "freezeStateName"},
    {"title": "业务单号", "dataIndex": "targetId"},
    {"title": "冻结类型", "dataIndex": "freezeTypeName"},
    {"title": "发生额", "dataIndex": "amount", "note": "单位：分"},
    {"title": "余额(元)", "dataIndex": "balanceAmount", "note": "单位：分"},
    {"title": "备注", "dataIndex": "remark"},
]


def execute(
    acct_no: str,
    begin_time: Optional[int] = None,
    end_time: Optional[int] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """外部账户冻结明细查询（不可用余额明细查询）(v2)
    根据资金账号查询冻结/不可用余额明细。

    Args:
        acct_no: 资金账号。必填。
        begin_time: 查询开始时间。可选。秒级Unix时间戳，默认近7天。
        end_time: 查询结束时间。可选。秒级Unix时间戳，默认当前时间。
        page_no: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.inout.getFreezeLogPageList"

    now = datetime.now()
    if begin_time is None:
        begin_time = int((now - timedelta(days=7)).timestamp())
    if end_time is None:
        end_time = int(now.timestamp())

    payload = {
        "acctNo": acct_no,
        "beginTime": begin_time,
        "endTime": end_time,
        "pageNo": page_no,
        "pageSize": page_size,
    }

    return client.post(url, payload)
