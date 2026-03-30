"""
担保交易查询 - 还款查询
来源：schemas/资金域/v3_担保交易查询.json
页面包含两个Tab，此为Tab2：还款查询（输入还款单号返回详情+两个表格）
"""
import sys
import os
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "no": {
        "type": "string",
        "required": True,
        "description": "还款单号"
    }
}

# 数据展示配置
DISPLAY_CONFIG = {
    "type": "detail_and_multi_table",
    "detail_fields": [
        {"label": "信贷产品编号", "field": "creditProdNo"},
        {"label": "到期日", "field": "endTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"label": "贷款编号", "field": "loanNo"},
        {"label": "应还本金", "field": "normalPrincipal", "note": "format(money)"},
        {"label": "应还利息", "field": "normalInterest", "note": "format(money)"},
        {"label": "应还逾期罚息", "field": "normalOverdue", "note": "format(money)"},
        {"label": "还款计划编号", "field": "repaymentPlanNo"},
        {"label": "主体id", "field": "subjectId"},
        {"label": "是否结清", "field": "settle"},
        {"label": "总期数", "field": "totalPeriod"},
        {"label": "商户号、会员号", "field": "userNo"}
    ],
    "tables": [
        {
            "title": "详细列表",
            "data_source": "planDetailList",
            "columns": [
                {"title": "还款计划编号", "dataIndex": "repaymentPlanNo"},
                {"title": "应还利息", "dataIndex": "normalInterest", "note": "format(money)"},
                {"title": "应还逾期罚息", "dataIndex": "normalOverdue", "note": "format(money)"},
                {"title": "应还本金", "dataIndex": "normalPrincipal", "note": "format(money)"},
                {"title": "已还利息", "dataIndex": "selInterest", "note": "format(money)"},
                {"title": "已还逾期罚息", "dataIndex": "selOverdue", "note": "format(money)"},
                {"title": "期号", "dataIndex": "period"},
                {"title": "状态", "dataIndex": "planDetailState"},
                {"title": "已还本金", "dataIndex": "selPrincipal", "note": "format(money)"},
                {"title": "是否结清", "dataIndex": "settle"},
                {"title": "到期日", "dataIndex": "endTime", "format": "YYYY-MM-DD HH:mm:ss"}
            ]
        },
        {
            "title": "还款记录",
            "data_source": "recordList",
            "columns": [
                {"title": "还款计划编号", "dataIndex": "repaymentPlanNo"},
                {"title": "还款单号", "dataIndex": "repaymentNo"},
                {"title": "还款申请金额", "dataIndex": "applyAmount", "note": "format(money)"},
                {"title": "还款利息", "dataIndex": "interest", "note": "format(money)"},
                {"title": "还款本金", "dataIndex": "principal", "note": "format(money)"},
                {"title": "还款逾期罚息", "dataIndex": "overdue", "note": "format(money)"},
                {"title": "期号", "dataIndex": "period"},
                {"title": "还款状态", "dataIndex": "repaymentState"},
                {"title": "还款完成时间", "dataIndex": "finishTime", "format": "YYYY-MM-DD HH:mm:ss"},
                {"title": "失败原因", "dataIndex": "failReason"}
            ]
        }
    ]
}


def execute(no: str) -> Dict[str, Any]:
    """查询还款详情、还款计划明细及还款记录

    Args:
        no: 还款单号。必填。如：RP202301010001

    Returns:
        返回还款详情（detail_fields）、还款计划明细（planDetailList）和还款记录（recordList）
    """
    # v3版本API路径
    url = f"{BASE_URL}/v3/api/dispatch/invoke/youzan.pay.fin.credit.OpQueryService.repayQuery"

    payload = {"no": no}

    return client.post(url, payload)
