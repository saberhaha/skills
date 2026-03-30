"""
科目余额调整 — 科目余额调整
来源：schemas/会计域/v2_科目余额调整.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v2_科目余额调整.json）
PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "enum",
        "required": False,
        "default": 0,
        "enum_values": {"0": "全部", "1": "高汇通支付", "2": "有赞平台"},
        "description": "核算主体（0=全部为前端附加选项；枚举由后端接口动态下发）",
    },
    "voucherId": {
        "type": "string",
        "required": False,
        "description": "凭证号",
    },
    "applyStartDate": {
        "type": "string",
        "format": "timestamp_ms",
        "required": False,
        "default": "now-7d",
        "description": "申请开始时间（毫秒时间戳），默认近7天",
    },
    "applyEndDate": {
        "type": "string",
        "format": "timestamp_ms",
        "required": False,
        "default": "now",
        "description": "申请结束时间（毫秒时间戳），默认当前时间",
    },
    "applier": {
        "type": "string",
        "required": False,
        "description": "申请人",
    },
    "auditStartDate": {
        "type": "string",
        "format": "timestamp_ms",
        "required": False,
        "description": "审核开始时间（毫秒时间戳）",
    },
    "auditEndDate": {
        "type": "string",
        "format": "timestamp_ms",
        "required": False,
        "description": "审核结束时间（毫秒时间戳）",
    },
    "auditor": {
        "type": "string",
        "required": False,
        "description": "审核人",
    },
    "voucherState": {
        "type": "array",
        "required": False,
        "default": [1, 2, 3],
        "enum_values": {
            "0": "申请中",
            "1": "审批通过",
            "2": "已驳回",
            "3": "全部成功",
            "4": "全部失败",
            "5": "部分成功",
        },
        "description": "凭证状态数组（可多选）。列表页默认[1,2,3]=审批通过/已驳回/全部成功，复核页固定[0]=申请中",
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
        "default": 10,
        "description": "每页条数",
    },
}

# 数据展示列（来源：schemas/会计域/v2_科目余额调整.json display.columns，去重后保留列表页主要列）
DISPLAY_COLUMNS = [
    {"title": "核算主体", "dataIndex": "accountingEntity"},
    {"title": "凭证号", "dataIndex": "voucherId"},
    {"title": "科目代码", "dataIndex": "subjectCode"},
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "调账方向", "dataIndex": "adjustDir"},
    {"title": "调整金额(元)", "dataIndex": "amount"},
    {"title": "调账说明", "dataIndex": "remark"},
    {"title": "凭证状态", "dataIndex": "voucherStatus"},
    {"title": "申请人", "dataIndex": "applier"},
    {"title": "申请时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "复核人", "dataIndex": "auditor"},
    {"title": "复核时间", "dataIndex": "auditAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    accounting_entity: Optional[Literal["0", "1", "2"]] = None,
    voucher_id: Optional[str] = None,
    apply_start_date: Optional[int] = None,
    apply_end_date: Optional[int] = None,
    applier: Optional[str] = None,
    audit_start_date: Optional[int] = None,
    audit_end_date: Optional[int] = None,
    auditor: Optional[str] = None,
    voucher_state: Optional[list] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询科目余额调整记录。
    用户只需提供核算主体、凭证号等筛选条件，其余参数自动使用页面默认值。

    Args:
        accounting_entity: 核算主体。可选。枚举：0=全部, 1=高汇通支付, 2=有赞平台。默认=0(全部)。
        voucher_id: 凭证号。可选。
        apply_start_date: 申请开始时间（毫秒时间戳）。可选，默认=近7天。
        apply_end_date: 申请结束时间（毫秒时间戳）。可选，默认=当前时间。
        applier: 申请人。可选。
        audit_start_date: 审核开始时间（毫秒时间戳）。可选。
        audit_end_date: 审核结束时间（毫秒时间戳）。可选。
        auditor: 审核人。可选。
        voucher_state: 凭证状态数组（可多选）。枚举：0=申请中,1=审批通过,2=已驳回,3=全部成功,4=全部失败,5=部分成功。
                       默认=[1,2,3](审批通过/已驳回/全部成功)。
        page: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.adjust.query.queryList"

    now = datetime.now()
    # 默认近7天 → 毫秒时间戳
    default_start = int((now - timedelta(days=7)).timestamp() * 1000)
    default_end = int(now.timestamp() * 1000)

    payload: dict = {
        "page": page,
        "pageSize": page_size,
        "accountingEntity": int(accounting_entity) if accounting_entity is not None else 0,  # 默认：全部
        "applyStartDate": apply_start_date if apply_start_date is not None else default_start,
        "applyEndDate": apply_end_date if apply_end_date is not None else default_end,
        "voucherState": voucher_state if voucher_state is not None else [1, 2, 3],  # 默认：审批通过/已驳回/全部成功
    }
    if voucher_id is not None:
        payload["voucherId"] = voucher_id
    if applier is not None:
        payload["applier"] = applier
    if audit_start_date is not None:
        payload["auditStartDate"] = audit_start_date
    if audit_end_date is not None:
        payload["auditEndDate"] = audit_end_date
    if auditor is not None:
        payload["auditor"] = auditor

    return client.post(url, payload)
