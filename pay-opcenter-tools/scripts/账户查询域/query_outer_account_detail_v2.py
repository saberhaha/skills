"""
外部账户明细查询（支付资金账户明细查询）(v2)
来源：schemas/账户查询域/v2_外部账户明细查询.json
"""
import sys
import os
import time
from datetime import timedelta, datetime
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "acctNo": {
        "type": "string", "required": True,
        "description": "资金账号"
    },
    "acctType": {
        "type": "number", "required": True,
        "description": "账户类型（由系统根据acctNo自动查询填充）"
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
    {"title": "业务类型", "dataIndex": "inoutLogTypeDesc"},
    {"title": "业务单号", "dataIndex": "orderNo"},
    {"title": "收支类型", "dataIndex": "inOutFlag", "note": "枚举：1=收入，2=支出"},
    {"title": "发生额", "dataIndex": "amount", "note": "单位：分"},
    {"title": "余额(元)", "dataIndex": "balanceAmount", "note": "单位：分"},
    {"title": "对手账户", "dataIndex": "opponentAccountName"},
    {"title": "备注", "dataIndex": "extraInfo"},
]


def execute(
    acct_no: str,
    acct_type: int,
    begin_time: Optional[int] = None,
    end_time: Optional[int] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """外部账户明细查询（支付资金账户明细查询）(v2)
    根据资金账号和账户类型查询账户收支明细。

    Args:
        acct_no: 资金账号。必填。
        acct_type: 账户类型。必填。
        begin_time: 查询开始时间。可选。秒级Unix时间戳，默认近7天。
        end_time: 查询结束时间。可选。秒级Unix时间戳，默认当前时间。
        page_no: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.inout.getInoutPageListByAcctType"

    now = datetime.now()
    if begin_time is None:
        begin_time = int((now - timedelta(days=7)).timestamp())
    if end_time is None:
        end_time = int(now.timestamp())

    payload = {
        "acctNo": acct_no,
        "acctType": acct_type,
        "beginTime": begin_time,
        "endTime": end_time,
        "pageNo": page_no,
        "pageSize": page_size,
    }

    return client.post(url, payload)
