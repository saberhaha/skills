"""
记账查询 — 记账查询
来源：schemas/会计域/v1_记账查询.json

# TODO: 源码未找到真实查询 API。页面为静态表格壳，查询按钮仅 alert，无真实后端请求。
#       需人工补全真实接口路径后方可使用。
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_记账查询.json）
PARAM_SCHEMA = {
    "accountingDate": {
        "type": "string",
        "required": False,
        "description": "记账日期（页面选择）",
    },
    "inOut": {
        "type": "enum",
        "required": False,
        "enum_values": {"1": "收入", "2": "支出"},
        "description": "收支类型",
    },
    "dealType": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "1": "提现",
            "2": "充值",
            "3": "退款",
            "4": "退手续费",
            "5": "应用订购",
        },
        "description": "交易类型",
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "description": "订单号",
    },
    "receiptNo": {
        "type": "string",
        "required": False,
        "description": "收单号",
    },
    "accountNo": {
        "type": "string",
        "required": False,
        "description": "账号",
    },
}

# 数据展示列（来源：schemas/会计域/v1_记账查询.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "交易时间", "dataIndex": "dealTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "收单号", "dataIndex": "receiptNo"},
    {"title": "订单号", "dataIndex": "orderNo"},
    {"title": "外部子业务号", "dataIndex": "outChildBIZNo"},
    {"title": "账户号", "dataIndex": "accountNo"},
    {"title": "收入/支出", "dataIndex": "inOut"},
    {"title": "交易类型", "dataIndex": "dealType"},
    {"title": "交易金额", "dataIndex": "dealBalance"},
    {"title": "备注", "dataIndex": "remark"},
]


def execute(
    accounting_date: Optional[str] = None,
    in_out: Optional[Literal["1", "2"]] = None,
    deal_type: Optional[Literal["1", "2", "3", "4", "5"]] = None,
    order_no: Optional[str] = None,
    receipt_no: Optional[str] = None,
    account_no: Optional[str] = None,
) -> dict:
    """查询记账数据。
    # TODO: 源码未找到真实查询 API，需人工补全接口路径后方可使用。

    Args:
        accounting_date: 记账日期。可选。
        in_out: 收支类型。可选。枚举：1=收入, 2=支出。
        deal_type: 交易类型。可选。枚举：1=提现, 2=充值, 3=退款, 4=退手续费, 5=应用订购。
        order_no: 订单号。可选。
        receipt_no: 收单号。可选。
        account_no: 账号。可选。
    """
    # TODO: 源码未找到真实查询 API，需人工补全
    raise NotImplementedError(
        "记账查询：页面为静态表格壳，查询按钮仅 alert，无真实后端请求。"
        "请人工补全真实接口路径后再使用本 Skill。"
    )
