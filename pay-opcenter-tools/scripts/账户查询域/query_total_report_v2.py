"""
总分平衡表查询 (v2)
来源：schemas/账户查询域/v2_总分平衡表查询.json
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "number", "required": True,
        "description": "核算主体code"
    },
    "accountingDate": {
        "type": "string", "format": "YYYYMMDD",
        "required": True, "default": "yesterday",
        "description": "会计日期，格式YYYYMMDD，默认昨天"
    },
    "balanceRelation": {
        "type": "enum", "required": False, "default": 0,
        "enum_values": {"0": "全部"},
        "description": "平衡关系筛选，默认0=全部"
    },
}

DISPLAY_COLUMNS = [
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "科目编码", "dataIndex": "subjectCode"},
    {"title": "资金账号", "dataIndex": "acctransAcctNo"},
    {"title": "分户账-借方期初余额", "dataIndex": "acctransDebitInitBalance"},
    {"title": "分户账-贷方期初余额", "dataIndex": "acctransCreditInitBalance"},
    {"title": "分户账-借方发生额", "dataIndex": "acctransDebitAmount"},
    {"title": "分户账-贷方发生额", "dataIndex": "acctransCreditAmount"},
    {"title": "分户账-借方期末余额", "dataIndex": "acctransDebitEndBalance"},
    {"title": "分户账-贷方期末余额", "dataIndex": "acctransCreditEndBalance"},
    {"title": "会计核算-借方期初余额", "dataIndex": "accountingDebitInitBalance"},
    {"title": "会计核算-贷方期初余额", "dataIndex": "accountingCreditInitBalance"},
    {"title": "会计核算-借方发生额", "dataIndex": "accountingDebitAmount"},
    {"title": "会计核算-贷方发生额", "dataIndex": "accountingCreditAmount"},
    {"title": "会计核算-借方期末余额", "dataIndex": "accountingDebitEndBalance"},
    {"title": "会计核算-贷方期末余额", "dataIndex": "accountingCreditEndBalance"},
    {"title": "发生额平衡", "dataIndex": "amountEquals", "note": "1=平衡，2=不平衡"},
    {"title": "余额平衡", "dataIndex": "balanceEquals", "note": "1=平衡，2=不平衡"},
]


def execute(
    accounting_entity: int,
    accounting_date: Optional[str] = None,
    balance_relation: int = 0,
) -> dict:
    """总分平衡表查询 (v2)
    按核算主体和会计日期查询总分平衡表。

    Args:
        accounting_entity: 核算主体code。必填。
        accounting_date: 会计日期，格式YYYYMMDD。可选，默认昨天。
        balance_relation: 平衡关系筛选。默认 0（全部）。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.totalsub.query.list"

    if accounting_date is None:
        yesterday = datetime.now() - timedelta(days=1)
        accounting_date = yesterday.strftime("%Y%m%d")

    payload = {
        "accountingEntity": accounting_entity,
        "accountingDate": accounting_date,
        "balanceRelation": balance_relation,
    }

    return client.post(url, payload)
