"""
内部账户明细查询（内部账户收支明细）(v2)
来源：schemas/账户查询域/v2_内部账户明细查询.json
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "acctNo": {
        "type": "string", "required": True,
        "description": "内部户账号"
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
    "subjectDir": {
        "type": "enum", "required": False,
        "enum_values": {"D": "借方", "C": "贷方", "O": "两性"},
        "description": "借贷方向"
    },
    "archiveType": {
        "type": "enum", "required": False,
        "enum_values": {"1": "归档前", "2": "归档后"},
        "description": "归档时间筛选"
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
    {"title": "核算主体", "dataIndex": "accountingEntityName"},
    {"title": "交易时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "业务类型", "dataIndex": "inouttypeName"},
    {"title": "业务单号", "dataIndex": "targetId"},
    {"title": "借/贷方向", "dataIndex": "balanceDir"},
    {"title": "发生额", "dataIndex": "amount", "note": "单位：分"},
    {"title": "余额", "dataIndex": "balance", "note": "单位：分"},
    {"title": "对手账户", "dataIndex": "opponentAccountName"},
    {"title": "备注", "dataIndex": "remark"},
]


def execute(
    acct_no: str,
    begin_time: Optional[int] = None,
    end_time: Optional[int] = None,
    subject_dir: Optional[Literal["D", "C", "O"]] = None,
    archive_type: Optional[Literal["1", "2"]] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """内部账户明细查询（内部账户收支明细）(v2)
    根据内部户账号查询收支明细，支持按借贷方向和归档时间筛选。

    Args:
        acct_no: 内部户账号。必填。
        begin_time: 查询开始时间。可选。秒级Unix时间戳，默认近7天。
        end_time: 查询结束时间。可选。秒级Unix时间戳，默认当前时间。
        subject_dir: 借贷方向。可选。枚举：'D'=借方, 'C'=贷方, 'O'=两性。
        archive_type: 归档时间筛选。可选。枚举：'1'=归档前, '2'=归档后。
        page_no: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.inout.getInoutInnerPageList"

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
    if subject_dir is not None:
        payload["subjectDir"] = subject_dir
    if archive_type is not None:
        payload["archiveType"] = archive_type

    return client.post(url, payload)
