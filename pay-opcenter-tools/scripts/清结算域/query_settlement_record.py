"""
清结算记录
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Literal, Union
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "applyStartTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "申请开始时间"
    },
    "applyEndTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "申请结束时间"
    },
    "finishStartTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "完成开始时间"
    },
    "finishEndTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "完成结束时间"
    },
    "userNo": {
        "type": "string",
        "required": False,
        "description": "商户号"
    },
    "partnerId": {
        "type": "string",
        "required": False,
        "description": "服务商号"
    },
    "settleMode": {
        "type": "enum",
        "required": False,
        "enum_values": {"0": "实时", "1": "T+1"},
        "description": "结算周期"
    },
    "settleAccountType": {
        "type": "enum",
        "required": False,
        "enum_values": {"0": "银行卡", "1": "余额", "2": "收入户"},
        "description": "结算账户类型"
    },
    "settleAccountNo": {
        "type": "string",
        "required": False,
        "description": "结算流水号"
    },
    "status": {
        "type": "enum",
        "required": False,
        "enum_values": {"0": "初始化", "1": "结算中", "2": "结算失败", "3": "结算成功"},
        "description": "结算状态"
    },
    "isRefundTicket": {
        "type": "enum",
        "required": False,
        "enum_values": {"0": "否", "1": "是"},
        "description": "是否退票"
    },
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
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
# 清结算记录列表
DISPLAY_COLUMNS_SETTLE_RECORD = [
    {"title": "结算申请时间", "dataIndex": "applyTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "结算完成时间", "dataIndex": "finishTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "商户号", "dataIndex": "userNo"},
    {"title": "服务商号", "dataIndex": "partnerId"},
    {"title": "结算流水号", "dataIndex": "settleAccountNo"},
    {"title": "结算周期", "dataIndex": "settleMode"},
    {"title": "结算账户", "dataIndex": "settleAccountType"},
    {"title": "结算银行", "dataIndex": "settleBank"},
    {"title": "结算金额", "dataIndex": "amount"},
    {"title": "结算状态", "dataIndex": "status"},
    {"title": "是否退票", "dataIndex": "isRefundTicket"},
    {"title": "失败原因", "dataIndex": "errorMsg"}
]

# 清算明细
DISPLAY_COLUMNS_SETTLEMENT_DETAIL = [
    {"title": "渠道完成时间", "dataIndex": "channelFinishedTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "清算流水号", "dataIndex": "settlementNo"},
    {"title": "结算流水号", "dataIndex": "settleAccountNo"},
    {"title": "服务商号", "dataIndex": "partnerId"},
    {"title": "有赞商户号", "dataIndex": "userNo"},
    {"title": "外部订单号", "dataIndex": "bizNo"},
    {"title": "外部流水号", "dataIndex": "outWaterNo"},
    {"title": "交易单号", "dataIndex": "tradeNo"},
    {"title": "支付单号", "dataIndex": "payNo"},
    {"title": "结算模式", "dataIndex": "settleModeDesc"},
    {"title": "支付金额（元）", "dataIndex": "payAmount"},
    {"title": "手续费金额（元）", "dataIndex": "feeAmount"},
    {"title": "清算金额（元）", "dataIndex": "settlementAmount"},
    {"title": "清算收支", "dataIndex": "inOutDesc"},
    {"title": "币种", "dataIndex": "currency"},
    {"title": "渠道类型", "dataIndex": "channelDesc"},
    {"title": "交易类型", "dataIndex": "tradeTypeDesc"},
    {"title": "支付工具", "dataIndex": "payTool"},
    {"title": "对账状态", "dataIndex": "checkStatusDesc"}
]


def execute(
    apply_start_time: Optional[str] = None,
    apply_end_time: Optional[str] = None,
    finish_start_time: Optional[str] = None,
    finish_end_time: Optional[str] = None,
    user_no: Optional[str] = None,
    partner_id: Optional[str] = None,
    settle_mode: Optional[Literal["0", "1"]] = None,
    settle_account_type: Optional[Literal["0", "1", "2"]] = None,
    settle_account_no: Optional[str] = None,
    status: Optional[Literal["0", "1", "2", "3"]] = None,
    is_refund_ticket: Optional[Literal["0", "1"]] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """清结算记录查询
    查询清结算记录列表和清算明细信息。

    Args:
        apply_start_time: 申请开始时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        apply_end_time: 申请结束时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        finish_start_time: 完成开始时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        finish_end_time: 完成结束时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        user_no: 商户号。可选。
        partner_id: 服务商号。可选。
        settle_mode: 结算周期。枚举：0=实时, 1=T+1。可选。
        settle_account_type: 结算账户类型。枚举：0=银行卡, 1=余额, 2=收入户。可选。
        settle_account_no: 结算流水号。可选。
        status: 结算状态。枚举：0=初始化, 1=结算中, 2=结算失败, 3=结算成功。可选。
        is_refund_ticket: 是否退票。枚举：0=否, 1=是。可选。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.bs.settle.query.page/"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "page": page,
        "pageSize": page_size,
    }

    # 可选参数填充
    if apply_start_time is not None:
        payload["applyStartTime"] = apply_start_time
    if apply_end_time is not None:
        payload["applyEndTime"] = apply_end_time
    if finish_start_time is not None:
        payload["finishStartTime"] = finish_start_time
    if finish_end_time is not None:
        payload["finishEndTime"] = finish_end_time
    if user_no is not None:
        payload["userNo"] = user_no
    if partner_id is not None:
        payload["partnerId"] = partner_id
    if settle_mode is not None:
        payload["settleMode"] = settle_mode
    if settle_account_type is not None:
        payload["settleAccountType"] = settle_account_type
    if settle_account_no is not None:
        payload["settleAccountNo"] = settle_account_no
    if status is not None:
        payload["status"] = status
    if is_refund_ticket is not None:
        payload["isRefundTicket"] = is_refund_ticket

    return client.post(url, payload)


def query_settlement_detail(
    settle_account_no: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """清算明细查询
    根据结算流水号查询清算明细信息。

    Args:
        settle_account_no: 结算流水号。必填。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.bs.settlement.query.page/"

    payload = {
        "settleAccountNo": settle_account_no,
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)


def query_bank_info(
    settle_account_no: str,
    desensitized: bool = True,
) -> dict:
    """结算银行信息查询
    根据结算流水号查询银行账户信息。

    Args:
        settle_account_no: 结算流水号。必填。
        desensitized: 是否返回脱敏数据。默认=True。
    """

    if desensitized:
        url = f"{BASE_URL}/dispatcher/pay.bs.settle.bankInfo.query.desensitized/"
    else:
        url = f"{BASE_URL}/dispatcher/pay.bs.settle.bankInfo.query/"

    payload = {
        "settleAccountNo": settle_account_no,
    }

    return client.post(url, payload)
