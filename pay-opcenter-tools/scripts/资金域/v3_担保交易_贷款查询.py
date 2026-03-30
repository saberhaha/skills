"""
担保交易查询 - 贷款查询
来源：schemas/资金域/v3_担保交易查询.json
页面包含两个Tab，此为Tab1：贷款查询（输入贷款合同单号返回详情+订单列表）
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
        "description": "贷款合同单号"
    }
}

# 数据展示配置
DISPLAY_CONFIG = {
    "type": "detail_and_table",
    "detail_fields": [
        {"label": "信贷产品编号", "field": "creditProdNo"},
        {"label": "贷款合同申请金额", "field": "contractApplyAmount", "note": "format(money)"},
        {"label": "合同本金", "field": "contractPrincipalAmount", "note": "format(money)"},
        {"label": "合同到期日", "field": "contractEndTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"label": "合同开始日", "field": "contractStartTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"label": "贷款合同状态", "field": "contractState"},
        {"label": "贷款失败原因", "field": "failReason"},
        {"label": "贷款合同编号", "field": "loanContractNo"},
        {"label": "主体id", "field": "subjectId"},
        {"label": "是否结清", "field": "settle"},
        {"label": "签约合同编号", "field": "signContractNo"},
        {"label": "结清日期", "field": "settleTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"label": "期限类型", "field": "termType"},
        {"label": "期限", "field": "term"},
        {"label": "商户号、会员号", "field": "userNo"}
    ],
    "table": {
        "data_source": "listOrder",
        "columns": [
            {"title": "贷款编号", "dataIndex": "loanNo"},
            {"title": "订单号", "dataIndex": "orderNo"},
            {"title": "贷款申请金额", "dataIndex": "loanApplyAmount", "note": "format(money)"},
            {"title": "贷款本金", "dataIndex": "loanPrincipalAmount", "note": "format(money)"},
            {"title": "贷款失败原因", "dataIndex": "failReason"},
            {"title": "贷款状态", "dataIndex": "loanState"},
            {"title": "是否结清", "dataIndex": "settle"},
            {"title": "结清日期", "dataIndex": "settleTime", "format": "YYYY-MM-DD HH:mm:ss"}
        ]
    }
}


def execute(no: str) -> Dict[str, Any]:
    """查询贷款合同详情及关联订单列表

    Args:
        no: 贷款合同单号。必填。如：LC202301010001

    Returns:
        返回贷款合同详情（detail_fields）和订单列表（listOrder）
    """
    # v3版本API路径
    url = f"{BASE_URL}/v3/api/dispatch/invoke/youzan.pay.fin.credit.OpQueryService.loanQuery"

    payload = {"no": no}

    return client.post(url, payload)
