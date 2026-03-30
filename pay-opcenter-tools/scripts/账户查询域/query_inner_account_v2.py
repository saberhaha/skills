"""
内部账户查询（内部资金账户查询）(v2)
来源：schemas/账户查询域/v2_内部账户查询.json
"""
import sys
import os
from typing import Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "enum", "required": True, "default": 1,
        "enum_values": {"1": "高汇通支付", "2": "有赞平台"},
        "description": "核算主体"
    },
}

DISPLAY_COLUMNS = [
    {"title": "核算主体", "dataIndex": "accountingEntityName"},
    {"title": "内部户名称", "dataIndex": "innerAcctName"},
    {"title": "内部户账号", "dataIndex": "innerAcctNo"},
    {"title": "余额方向", "dataIndex": "balanceDirName", "note": "枚举：D=借方，C=贷方，O=两性"},
    {"title": "余额", "dataIndex": "balance", "note": "单位：分"},
]


def execute(
    accounting_entity: Literal[1, 2] = 1,
) -> dict:
    """内部账户查询（内部资金账户查询）(v2)
    根据核算主体查询内部资金账户列表。

    Args:
        accounting_entity: 核算主体。枚举：1=高汇通支付, 2=有赞平台。默认 1。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.account.queryInnerAcctInfo"

    payload = {
        "accountingEntity": accounting_entity,
    }

    return client.post(url, payload)
