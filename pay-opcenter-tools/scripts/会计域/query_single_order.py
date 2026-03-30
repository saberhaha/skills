"""
单笔订单查询 — 单笔订单查询
来源：schemas/会计域/v1_单笔订单查询.json

# TODO: 源码未找到真实查询 API。页面为静态表格壳，doQuery 未发起任何 Request.fetch 请求。
#       需人工补全真实接口路径后方可使用。
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_单笔订单查询.json）
PARAM_SCHEMA = {
    "orderNo": {
        "type": "string",
        "required": False,
        "description": "订单号（页面查询输入）",
    },
}

# 数据展示列（来源：schemas/会计域/v1_单笔订单查询.json display.columns，已去重）
DISPLAY_COLUMNS = [
    {"title": "订单号", "dataIndex": "orderNo"},
    {"title": "收单号", "dataIndex": "receiptNo"},
    {"title": "渠道码", "dataIndex": "channelCode"},
    {"title": "交易方式", "dataIndex": "dealMode"},
    {"title": "资金流向", "dataIndex": "fundsDirection"},
    {"title": "交易类型", "dataIndex": "dealType"},
    {"title": "交易时间", "dataIndex": "dealTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "交易金额", "dataIndex": "dealBalance"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "备注", "dataIndex": "remark"},
    {"title": "记账码", "dataIndex": "bookkeepingCode"},
    {"title": "外部订单号", "dataIndex": "outOrderNo"},
    {"title": "账号", "dataIndex": "account"},
    {"title": "收支类型", "dataIndex": "inoutType"},
    {"title": "会计日期", "dataIndex": "accountingDate", "format": "YYYY-MM-DD"},
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "借贷方向", "dataIndex": "borrowLoanDirection"},
]


def execute(
    order_no: Optional[str] = None,
) -> dict:
    """查询单笔订单的记账信息。
    # TODO: 源码未找到真实查询 API，需人工补全接口路径后方可使用。

    Args:
        order_no: 订单号。可选。
    """
    # TODO: 源码未找到真实查询 API，需人工补全
    raise NotImplementedError(
        "单笔订单查询：页面为静态表格壳，doQuery 未发起任何 Request.fetch 请求。"
        "请人工补全真实接口路径后再使用本 Skill。"
    )
