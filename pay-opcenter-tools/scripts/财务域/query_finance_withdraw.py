"""
财务提现 — 财务提现
来源：schemas/财务域/v1_财务提现.json
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
    "startDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "提现申请开始时间（毫秒时间戳）"
    },
    "endDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "提现申请结束时间（毫秒时间戳）"
    },
    "finishStartDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "提现完成开始时间（毫秒时间戳）"
    },
    "finishEndDate": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "提现完成结束时间（毫秒时间戳）"
    },
    "transNo": {
        "type": "string",
        "required": False,
        "description": "提现流水号"
    },
    "merId": {
        "type": "string",
        "required": False,
        "description": "商户号"
    },
    "payeeAcctNo": {
        "type": "string",
        "required": False,
        "description": "提现账号"
    },
    "settlementAccount": {
        "type": "enum",
        "required": False,
        "enum_values": {"1": "银行卡", "2": "微信", "3": "支付宝"},
        "description": "入金账户类型（传入整数）"
    },
    "transStatus": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "0": "已受理",
            "1": "交易成功",
            "2": "交易失败",
            "3": "等待渠道受理",
            "4": "渠道处理中",
            "5": "交易异常转人工"
        },
        "description": "提现状态（传入整数）"
    },
    "partnerId": {
        "type": "string",
        "required": False,
        "description": "业务线（bizLine），传partnerId，如 '820000000004' 对应美业"
    },
    "upstreamCode": {
        "type": "enum",
        "required": False,
        "enum_values": {"TRANSFER": "转账", "ASSETCENTER": "提现"},
        "description": "业务类型（bizType）"
    },
    "channelCode": {
        "type": "enum",
        "required": False,
        "enum_values": {"1": "银联", "2": "网联", "5": "易宝", "6": "平安银行", "7": "易付通", "8": "苏商银行"},
        "description": "渠道类型"
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
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "提现流水号", "dataIndex": "withdrawNo"},
    {"title": "网联提现流水号", "dataIndex": "netpayTxnNo"},
    {"title": "渠道类型", "dataIndex": "channelName"},
    {"title": "提现金额", "dataIndex": "withdrawAmount"},
    {"title": "业务线", "dataIndex": "bizLine"},
    {"title": "商户号", "dataIndex": "withdrawMerchantNo"},
    {"title": "提现账号", "dataIndex": "withdrawAccount"},
    {"title": "提现账户名称", "dataIndex": "withdrawAccountName"},
    {"title": "入金账户类型", "dataIndex": "inAccountType"},
    {"title": "到账银行编码", "dataIndex": "withdrawBankCode"},
    {"title": "到账银行名称", "dataIndex": "withdrawBankName"},
    {"title": "提现状态描述", "dataIndex": "withdrawStatusDesc"},
    {"title": "是否退票", "dataIndex": "isRefundTick"},
    {"title": "失败原因", "dataIndex": "failDesc"},
    {"title": "提现申请时间", "dataIndex": "withdrawApplyTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "提现完成时间", "dataIndex": "withdrawFinishTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作描述（提示文案）", "dataIndex": "actionDesc"},
]


def execute(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    finish_start_date: Optional[int] = None,
    finish_end_date: Optional[int] = None,
    trans_no: Optional[str] = None,
    mer_id: Optional[str] = None,
    payee_acct_no: Optional[str] = None,
    settlement_account: Optional[Literal["1", "2", "3"]] = None,
    trans_status: Optional[Literal["0", "1", "2", "3", "4", "5"]] = None,
    partner_id: Optional[str] = None,
    upstream_code: Optional[Literal["TRANSFER", "ASSETCENTER"]] = None,
    channel_code: Optional[Literal["1", "2", "5", "6", "7", "8"]] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询财务提现记录列表。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        start_date: 提现申请开始时间。可选。格式：毫秒时间戳（timestamp_ms）。
        end_date: 提现申请结束时间。可选。格式：毫秒时间戳（timestamp_ms）。
        finish_start_date: 提现完成开始时间。可选。格式：毫秒时间戳（timestamp_ms）。
        finish_end_date: 提现完成结束时间。可选。格式：毫秒时间戳（timestamp_ms）。
        trans_no: 提现流水号。可选。
        mer_id: 商户号。可选。
        payee_acct_no: 提现账号。可选。
        settlement_account: 入金账户类型。可选。枚举："1"=银行卡, "2"=微信, "3"=支付宝。
        trans_status: 提现状态。可选。枚举："0"=已受理, "1"=交易成功, "2"=交易失败, "3"=等待渠道受理, "4"=渠道处理中, "5"=交易异常转人工。
        partner_id: 业务线（bizLine），传 partnerId。可选。
        upstream_code: 业务类型。可选。枚举："TRANSFER"=转账, "ASSETCENTER"=提现。
        channel_code: 渠道类型。可选。枚举："1"=银联, "2"=网联, "5"=易宝, "6"=平安银行, "7"=易付通, "8"=苏商银行。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.queryPager"

    now = datetime.now()
    payload: dict = {
        "page": page,
        "pageSize": page_size,
    }

    # startDate 格式：timestamp_ms（毫秒时间戳）
    if start_date is not None:
        payload["startDate"] = start_date
    # endDate 格式：timestamp_ms
    if end_date is not None:
        payload["endDate"] = end_date
    # finishStartDate 格式：timestamp_ms
    if finish_start_date is not None:
        payload["finishStartDate"] = finish_start_date
    # finishEndDate 格式：timestamp_ms
    if finish_end_date is not None:
        payload["finishEndDate"] = finish_end_date
    if trans_no is not None:
        payload["transNo"] = trans_no
    if mer_id is not None:
        payload["merId"] = mer_id
    if payee_acct_no is not None:
        payload["payeeAcctNo"] = payee_acct_no
    if settlement_account is not None:
        payload["settlementAccount"] = int(settlement_account)
    if trans_status is not None:
        payload["transStatus"] = int(trans_status)
    if partner_id is not None:
        payload["partnerId"] = partner_id
    if upstream_code is not None:
        payload["upstreamCode"] = upstream_code
    if channel_code is not None:
        payload["channelCode"] = int(channel_code)

    return client.post(url, payload)
