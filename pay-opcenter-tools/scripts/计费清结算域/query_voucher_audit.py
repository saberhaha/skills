"""
凭证审核列表查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Literal
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "auditStartTime": {
        "type": "number",
        "format": "timestamp_s",
        "required": False,
        "default": None,
        "description": "审核开始时间（Unix时间戳，秒级）"
    },
    "auditEndTime": {
        "type": "number",
        "format": "timestamp_s",
        "required": False,
        "default": None,
        "description": "审核结束时间（Unix时间戳，秒级）"
    },
    "mchId": {
        "type": "string",
        "required": False,
        "default": "0",
        "description": "商户号（默认传'0'代表不限）"
    },
    "accountName": {
        "type": "string",
        "required": False,
        "default": None,
        "description": "付款方户名"
    },
    "usedType": {
        "type": "enum",
        "required": False,
        "default": None,
        "enum_values": {"1": "入账到余额(凭证充值)", "6": "商业化订购", "7": "人工冻结凭证"},
        "description": "用途类型（null=全部）"
    },
    "status": {
        "type": "enum",
        "required": False,
        "default": None,
        "enum_values": {"1": "待审核", "2": "审核通过", "3": "审核失败"},
        "description": "审核状态（null=全部）"
    },
    "innerTransactionNumber": {
        "type": "string",
        "required": False,
        "default": None,
        "description": "支付流水号"
    },
    "loginName": {
        "type": "string",
        "required": True,
        "description": "当前登录用户ID（自动从GlobalStore获取）"
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "当前页码"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 枚举定义（来源：Schema 中的 enum_values）
ENUM_USED_TYPE = {"1": "入账到余额(凭证充值)", "6": "商业化订购", "7": "人工冻结凭证"}
ENUM_STATUS = {"1": "待审核", "2": "审核通过", "3": "审核失败"}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "商户号", "dataIndex": "mchId"},
    {"title": "提交时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "用途类型", "dataIndex": "usedType", "note": "枚举映射: 1=凭证充值, 6=商业化订购, 7=人工冻结凭证, 8=订购预付款凭证充值"},
    {"title": "支付流水号", "dataIndex": "innerTransactionNumber"},
    {"title": "缴纳金额", "dataIndex": "amount", "note": "分→元: amount/100"},
    {"title": "付款户名", "dataIndex": "accountName"},
    {"title": "付款账号", "dataIndex": "accountNo"},
    {"title": "付款日期", "dataIndex": "payTime", "format": "YYYYMMDD"},
    {"title": "审核时间", "dataIndex": "auditTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "状态", "dataIndex": "state", "note": "枚举: 1=待审核, 2=通过, 3=驳回"},
    {"title": "原因", "dataIndex": "rejectReason"},
    {"title": "操作人", "dataIndex": "opInfo"}
]

# 汇总卡片
SUMMARY_CARDS = [
    {"label": "待审核订单数", "field": "collectStat[0].total"},
    {"label": "已审核订单数", "field": "collectStat[1].total"},
    {"label": "待审核订单总金额（元）", "field": "collectStat[0].amount", "note": "分→元: amount/100"},
    {"label": "已审核订单总金额（元）", "field": "collectStat[1].amount", "note": "分→元: amount/100"}
]

def execute(
    login_name: str,
    audit_start_time: Optional[int] = None,
    audit_end_time: Optional[int] = None,
    mch_id: Optional[str] = None,
    account_name: Optional[str] = None,
    used_type: Optional[Literal["1", "6", "7"]] = None,
    status: Optional[Literal["1", "2", "3"]] = None,
    inner_transaction_number: Optional[str] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """凭证审核列表查询
    用户只需提供核心查询条件，其余参数自动使用页面默认值。
    支持审核时间快捷选择（今日/昨日/近7天/近30天）。

    Args:
        login_name: 当前登录用户ID。必填。自动从GlobalStore获取。
        audit_start_time: 审核开始时间。可选。Unix时间戳（秒级）。默认为空。
        audit_end_time: 审核结束时间。可选。Unix时间戳（秒级）。默认为空。
        mch_id: 商户号。可选。默认传'0'代表不限。
        account_name: 付款方户名。可选。默认为空。
        used_type: 用途类型。可选。枚举: 1=入账到余额(凭证充值), 6=商业化订购, 7=人工冻结凭证。null=全部。
        status: 审核状态。可选。枚举: 1=待审核, 2=审核通过, 3=审核失败。null=全部。
        inner_transaction_number: 支付流水号。可选。默认为空。
        current_page: 当前页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/assetcenter.voucherPayAssist.query"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "loginName": login_name,
        "mchId": mch_id if mch_id is not None else "0",
        "currentPage": current_page,
        "pageSize": page_size,
    }

    # 可选参数：仅当非 None 时添加
    if audit_start_time is not None:
        payload["auditStartTime"] = audit_start_time
    if audit_end_time is not None:
        payload["auditEndTime"] = audit_end_time
    if account_name is not None:
        payload["accountName"] = account_name
    if used_type is not None:
        payload["usedType"] = used_type
    if status is not None:
        payload["status"] = status
    if inner_transaction_number is not None:
        payload["innerTransactionNumber"] = inner_transaction_number

    return client.post(url, payload)
