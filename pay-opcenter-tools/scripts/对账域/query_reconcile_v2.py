"""
核对查询 — v2 银行备付金核对查询
来源：schemas/对账域/v2_核对查询.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
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
    },
    "clearingStartDate": {
        "type": "number",
        "format": "YYYYMMDD",
        "required": False,
        "default": "now-3M",
        "description": "银行清算开始日期（格式：YYYYMMDD，如 20260101）"
    },
    "clearingEndDate": {
        "type": "number",
        "format": "YYYYMMDD",
        "required": False,
        "default": "now",
        "description": "银行清算结束日期（格式：YYYYMMDD）"
    },
    "channelCode": {
        "type": "string",
        "required": False,
        "description": "资金渠道"
    },
    "merchantNo": {
        "type": "string",
        "required": False,
        "description": "商户号"
    },
    "bankAccount": {
        "type": "string",
        "required": False,
        "description": "银行账号"
    },
    "remark": {
        "type": "string",
        "required": False,
        "description": "关联要素"
    },
    "bizType": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "0": "待对账",
            "1": "对账成功",
            "2": "待添加",
            "3": "待提交",
            "4": "待审核"
        },
        "description": "业务状态"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "银行清算日期", "dataIndex": "clearingDate"},
    {"title": "资金渠道", "dataIndex": "channelName"},
    {"title": "商户号", "dataIndex": "merchantNo"},
    {"title": "应清算金额(元)", "dataIndex": "needClearingAmount"},
    {"title": "交易笔数", "dataIndex": "tradeCount"},
    {"title": "银行账号", "dataIndex": "bankAccount"},
    {"title": "借方金额(元)", "dataIndex": "debitAmount"},
    {"title": "贷方金额(元)", "dataIndex": "creditAmount"},
    {"title": "关联要素", "dataIndex": "remark"},
    {"title": "业务状态", "dataIndex": "bizTypeName"},
    {"title": "操作记录", "dataIndex": "opDate"},
]


def execute(
    page: int = 1,
    page_size: int = 10,
    clearing_start_date: Optional[int] = None,
    clearing_end_date: Optional[int] = None,
    channel_code: Optional[str] = None,
    merchant_no: Optional[str] = None,
    bank_account: Optional[str] = None,
    remark: Optional[str] = None,
    biz_type: Optional[Literal["0", "1", "2", "3", "4"]] = None,
) -> dict:
    """核对查询（v2）- 查询银行备付金核对记录列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        clearing_start_date: 银行清算开始日期，格式 YYYYMMDD（如 20260101）。默认近 3 个月。
        clearing_end_date: 银行清算结束日期，格式 YYYYMMDD。默认今天。
        channel_code: 资金渠道编码。可选。
        merchant_no: 商户号。可选。
        bank_account: 银行账号。可选。
        remark: 关联要素。可选。
        biz_type: 业务状态。枚举：0=待对账, 1=对账成功, 2=待添加, 3=待提交, 4=待审核。可选。
    """
    url = f"{BASE_URL}/dispatcher/com.youzan.pay.check.channel.api.bankdepositservice.getdepositco/"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    # clearingStartDate / clearingEndDate 格式：YYYYMMDD（整型）
    default_start = int(three_months_ago.strftime("%Y%m%d"))
    default_end = int(now.strftime("%Y%m%d"))

    payload = {
        "page": page,
        "pageSize": page_size,
        "clearingStartDate": clearing_start_date if clearing_start_date is not None else default_start,
        "clearingEndDate": clearing_end_date if clearing_end_date is not None else default_end,
    }

    if channel_code is not None:
        payload["channelCode"] = channel_code
    if merchant_no is not None:
        payload["merchantNo"] = merchant_no
    if bank_account is not None:
        payload["bankAccount"] = bank_account
    if remark is not None:
        payload["remark"] = remark
    if biz_type is not None:
        payload["bizType"] = biz_type

    return client.post(url, payload)
