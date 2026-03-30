"""
出入账记录查询 (v3)
来源：schemas/账务域/v3_出入账记录查询.json
"""
import sys
import os
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "orderNo": {
        "type": "string", "required": False,
        "description": "订单号（和收单号至少填一个）"
    },
    "acquireNo": {
        "type": "string", "required": False,
        "description": "收单号（和订单号至少填一个）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = {
    "inoutLog": [
        {"title": "收支流水号", "dataIndex": "waterNo"},
        {"title": "商户号", "dataIndex": "userNo"},
        {"title": "账号类型", "dataIndex": "accountType"},
        {"title": "账号类型名称", "dataIndex": "accountTypeDesc"},
        {"title": "账号", "dataIndex": "acctNo"},
        {"title": "发生额(元)", "dataIndex": "amountWithDirection"},
        {"title": "余额(元)", "dataIndex": "balanceAmount"},
        {"title": "收支类型", "dataIndex": "inoutLogType"},
        {"title": "收支类型名称", "dataIndex": "inoutLogTypeDesc"},
        {"title": "渠道编号", "dataIndex": "payChannel"},
        {"title": "渠道名称", "dataIndex": "payChannelDesc"},
        {"title": "备注", "dataIndex": "remark"},
        {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "业务子单号", "dataIndex": "subOutBizNo"},
        {"title": "收单号", "dataIndex": "acquireNo"},
        {"title": "交易订单号", "dataIndex": "orderNo"}
    ],
    "accounting": [
        {"title": "核算主体", "dataIndex": "accountingEntityName"},
        {"title": "记账码", "dataIndex": "accountingCode"},
        {"title": "科目名称", "dataIndex": "subjectName"},
        {"title": "借贷", "dataIndex": "recordDirDesc"},
        {"title": "金额(元)", "dataIndex": "amount"},
        {"title": "外部流水号", "dataIndex": "outerWaterNo"},
        {"title": "会计日期", "dataIndex": "accountingDate", "format": "YYYYMMDD"},
        {"title": "科目编号", "dataIndex": "subjectCode"},
        {"title": "账户号", "dataIndex": "acctNo"},
        {"title": "币种", "dataIndex": "currencyDesc"},
        {"title": "备注", "dataIndex": "remark"},
        {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "收单号", "dataIndex": "acquireNo"},
        {"title": "交易订单号", "dataIndex": "orderNo"}
    ]
}


def execute(
    order_no: Optional[str] = None,
    acquire_no: Optional[str] = None,
) -> dict:
    """出入账记录查询（v3）
    按订单号或收单号同时查询账户收支明细和会计明细，至少提供一个查询条件。
    无分页参数。

    Args:
        order_no: 订单号。可选（和收单号至少填一个）。
        acquire_no: 收单号。可选（和订单号至少填一个）。
    """
    if not order_no and not acquire_no:
        return {"error": "orderNo 和 acquireNo 不能同时为空，至少提供一个。"}

    payload = {}
    if order_no:
        payload["orderNo"] = order_no
    if acquire_no:
        payload["acquireNo"] = acquire_no

    # 接口1：账户收支明细查询（GET）
    inout_url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.acctrans.inoutlog.query"
    inout_res = client.get(inout_url, params=payload)

    # 接口2：会计明细查询（GET）
    accounting_url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.accounting.record.query"
    accounting_res = client.get(accounting_url, params=payload)

    return {
        "inoutLog": inout_res,
        "accountingRecord": accounting_res
    }
