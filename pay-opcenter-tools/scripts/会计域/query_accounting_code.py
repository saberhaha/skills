"""
会计码管理 — 会计码管理
来源：schemas/会计域/v2_会计码管理.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v2_会计码管理.json）
PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "enum",
        "required": True,
        "default": "1",
        "enum_values": {"1": "高汇通支付", "2": "有赞平台"},
        "description": "核算主体（必填，默认=1高汇通支付）",
    },
    "channelCode": {
        "type": "string",
        "required": False,
        "description": "渠道码",
    },
    "channelMerchantNo": {
        "type": "string",
        "required": False,
        "description": "渠道商户号",
    },
    "accountingCode": {
        "type": "string",
        "required": False,
        "description": "会计码",
    },
    "approveFlag": {
        "type": "enum",
        "required": False,
        "default": 2,
        "enum_values": {"2": "审核通过", "1": "待审核", "3": "审核驳回"},
        "description": "审核状态，默认=2(审核通过)",
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码",
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 20,
        "description": "每页条数",
    },
}

# 数据展示列（来源：schemas/会计域/v2_会计码管理.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "核算主体", "dataIndex": "accountingEntity"},
    {"title": "会计码", "dataIndex": "accountingCode"},
    {"title": "记账规则名称", "dataIndex": "remark"},
    {"title": "渠道码", "dataIndex": "channelCode"},
    {"title": "渠道商户号", "dataIndex": "mchId"},
    {"title": "内部户方向", "dataIndex": "configType"},
    {"title": "借方科目", "dataIndex": "debtSubject"},
    {"title": "借方账号", "dataIndex": "debtAcct"},
    {"title": "贷方科目", "dataIndex": "creditSubject"},
    {"title": "贷方账号", "dataIndex": "creditAcct"},
    {"title": "是否生效", "dataIndex": "ableFlag"},
    {"title": "创建人", "dataIndex": "createUser"},
    {"title": "审核人", "dataIndex": "approveUser"},
    {"title": "审核指令", "dataIndex": "approveInstruction"},
    {"title": "审核通过时间", "dataIndex": "approveTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    accounting_entity: Literal["1", "2"] = "1",
    channel_code: Optional[str] = None,
    channel_merchant_no: Optional[str] = None,
    accounting_code: Optional[str] = None,
    approve_flag: Optional[Literal["1", "2", "3"]] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """查询会计码管理列表。
    用户只需提供核算主体、渠道码等筛选条件，其余参数自动使用页面默认值。

    Args:
        accounting_entity: 核算主体。必填。枚举：1=高汇通支付, 2=有赞平台。默认=1(高汇通支付)。
        channel_code: 渠道码。可选。
        channel_merchant_no: 渠道商户号。可选。
        accounting_code: 会计码。可选。
        approve_flag: 审核状态。可选。枚举：2=审核通过, 1=待审核, 3=审核驳回。默认=2(审核通过)。
        page: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=20。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.rule.query.list"

    payload: dict = {
        "page": page,
        "pageSize": page_size,
        "accountingEntity": int(accounting_entity),  # 必填
        "approveFlag": int(approve_flag) if approve_flag is not None else 2,  # 默认：审核通过
    }
    if channel_code is not None:
        payload["channelCode"] = channel_code
    if channel_merchant_no is not None:
        payload["channelMerchantNo"] = channel_merchant_no
    if accounting_code is not None:
        payload["accountingCode"] = accounting_code

    return client.post(url, payload)
