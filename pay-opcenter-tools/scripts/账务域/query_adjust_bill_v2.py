"""
调账单列表查询 (v2)
来源：schemas/账务域/v2_调账单列表.json
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "enum", "required": False, "default": 1,
        "enum_values": {"1": "高汇通支付", "2": "有赞平台"},
        "description": "核算主体（默认1=高汇通支付，Index页首次加载时传1）"
    },
    "voucherNo": {"type": "string", "required": False, "description": "凭证号"},
    "applyBeginTime": {
        "type": "number", "format": "unix_timestamp_s",
        "required": False, "default": "now-1month",
        "description": "申请开始时间（秒级unix时间戳，默认1个月前）"
    },
    "applyEndTime": {
        "type": "number", "format": "unix_timestamp_s",
        "required": False, "default": "now",
        "description": "申请结束时间（秒级unix时间戳，默认当前）"
    },
    "approveBeginTime": {
        "type": "number", "format": "unix_timestamp_s",
        "required": False,
        "description": "审核开始时间（秒级unix时间戳，展开筛选后可用）"
    },
    "approveEndTime": {
        "type": "number", "format": "unix_timestamp_s",
        "required": False,
        "description": "审核结束时间（秒级unix时间戳，展开筛选后可用）"
    },
    "userName": {"type": "string", "required": False, "description": "申请人"},
    "approveUser": {"type": "string", "required": False, "description": "审核人"},
    "status": {
        "type": "array", "required": False, "default": "all_status_codes",
        "description": "凭证状态列表（数组，默认传所有状态code）。枚举: 0=申请中,1=审批通过,2=已驳回,3=全部成功,4=全部失败,5=部分成功"
    },
    "remark": {"type": "string", "required": False, "description": "调账说明"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 默认所有状态码（来源 Schema default = all_status_codes）
ALL_STATUS_CODES = [0, 1, 2, 3, 4, 5]

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "申请日期", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "审核日期", "dataIndex": "approveTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "核算主体", "dataIndex": "accountingEntity"},
    {"title": "凭证号", "dataIndex": "outVoucherNo"},
    {"title": "申请人", "dataIndex": "applyUser"},
    {"title": "审核人", "dataIndex": "approveUser"},
    {"title": "总借记金额(元)", "dataIndex": "debitMoney"},
    {"title": "总贷记金额(元)", "dataIndex": "creditMoney"},
    {"title": "调账说明", "dataIndex": "remark"},
    {"title": "审核状态", "dataIndex": "auditStatusDTO"},
    {"title": "备注", "dataIndex": "message"}
]


def execute(
    accounting_entity: Literal[1, 2] = 1,
    voucher_no: Optional[str] = None,
    apply_begin_time: Optional[int] = None,
    apply_end_time: Optional[int] = None,
    approve_begin_time: Optional[int] = None,
    approve_end_time: Optional[int] = None,
    user_name: Optional[str] = None,
    approve_user: Optional[str] = None,
    status: Optional[List[int]] = None,
    remark: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """调账单列表查询（v2）
    查询调账单列表，默认查询最近一个月高汇通支付的所有状态调账单。

    Args:
        accounting_entity: 核算主体。枚举：1=高汇通支付,2=有赞平台。默认 1。
        voucher_no: 凭证号。可选。
        apply_begin_time: 申请开始时间。可选。秒级unix时间戳，默认近1个月前。
        apply_end_time: 申请结束时间。可选。秒级unix时间戳，默认当前时间。
        approve_begin_time: 审核开始时间。可选。秒级unix时间戳。
        approve_end_time: 审核结束时间。可选。秒级unix时间戳。
        user_name: 申请人。可选。
        approve_user: 审核人。可选。
        status: 凭证状态列表。可选。如 [0,1,2,3,4,5]。默认传所有状态。
        remark: 调账说明。可选。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.queryAuditList/"

    now = datetime.now()
    # 默认值：近1个月（来源 Schema default = now-1month）
    if apply_begin_time is None:
        apply_begin_time = int((now - timedelta(days=30)).timestamp())
    if apply_end_time is None:
        apply_end_time = int(now.timestamp())

    payload = {
        "accountingEntity": accounting_entity,
        "applyBeginTime": apply_begin_time,
        "applyEndTime": apply_end_time,
        "status": status if status is not None else ALL_STATUS_CODES,
        "page": page,
        "pageSize": page_size
    }
    if voucher_no:
        payload["voucherNo"] = voucher_no
    if approve_begin_time is not None:
        payload["approveBeginTime"] = approve_begin_time
    if approve_end_time is not None:
        payload["approveEndTime"] = approve_end_time
    if user_name:
        payload["userName"] = user_name
    if approve_user:
        payload["approveUser"] = approve_user
    if remark:
        payload["remark"] = remark

    return client.post(url, payload)


def get_accounting_entity_list() -> dict:
    """查询核算实体列表（辅助查询）
    用于筛选下拉选项，无入参。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.queryAllAccountingEntity"
    return client.post(url, {})


def get_audit_status_list() -> dict:
    """查询审核状态列表（辅助查询）
    用于凭证状态下拉选项，返回 [{code, name}]。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.queryAuditStatusList"
    return client.post(url, {})


def get_adjust_detail(
    voucher_no: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询调账申请明细列表（辅助查询）
    用于调账详情页：按凭证号查询调账明细条目列表。

    Args:
        voucher_no: 凭证号。必填。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.queryDetail"
    payload = {
        "voucherNo": voucher_no,
        "page": page,
        "pageSize": page_size
    }
    return client.post(url, payload)


def get_by_voucher_no(
    voucher_no: str,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """按凭证号查询调账明细（带分页，辅助查询）
    用于详情页分页加载明细。

    Args:
        voucher_no: 凭证号。必填。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.queryByVoucherNo"
    payload = {
        "voucherNo": voucher_no,
        "page": page,
        "pageSize": page_size
    }
    return client.post(url, payload)


def get_inner_acct_balance(
    acct_no: str,
) -> dict:
    """查询内部户账户余额（辅助查询）
    用于调账创建页面查询内部户余额，返回数值（单位：分）。
    sentData 直接传 acctNo 字符串。

    Args:
        acct_no: 内部户账号。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.queryInnerAcctBalance"
    return client.post(url, acct_no)


def get_all_inner_acct_no(
    accounting_entity: Literal[1, 2],
) -> dict:
    """查询所有内部户列表（辅助查询）
    用于调账创建页面内部户下拉选项。

    Args:
        accounting_entity: 核算主体。枚举：1=高汇通支付,2=有赞平台。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.query.queryAllInnerAcctNo"
    return client.post(url, accounting_entity)


def get_all_account_type() -> dict:
    """获取所有账户类型（辅助查询）
    无入参，返回 [{accountTypeCode, accountTypeDesc}] 用于账户类型下拉选项。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.adjust.queryAllAccountType"
    return client.post(url, {})
