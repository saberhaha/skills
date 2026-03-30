"""
支付凭证查询（电子回单）
来源：schemas/资金域/v3_支付凭证查询.json
功能：通过转账交易单号查询支付凭证详情，用于生成电子回单
"""
import sys
import os
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "tradeNo": {
        "type": "string",
        "required": True,
        "description": "转账交易单号（从URL参数paymentNo获取）"
    },
    "requestId": {
        "type": "string",
        "required": False,
        "description": "请求ID（默认等于tradeNo）"
    }
}

# 枚举定义
ENUMS = {
    "settleState": {
        "CREATE": "已创建",
        "SETTLING": "结算中",
        "SUCCESS": "结算成功",
        "FAIL": "结算失败"
    }
}

# 数据展示配置
DISPLAY_CONFIG = {
    "type": "voucher",
    "title": "杭州有赞科技有限公司客户电子回单",
    "fields": [
        {"label": "仲裁单号", "field": "outerTradeNo"},
        {"label": "转账交易单号", "field": "tradeNo"},
        {"label": "结算状态", "field": "settleState", "note": "枚举: CREATE/SETTLING/SUCCESS/FAIL"},
        {"label": "金额", "field": "settledAmount", "note": "format(money) + ' 元'"},
        {"label": "付款账户", "field": "fixed", "note": "固定值: '商家店铺余额'"},
        {"label": "到账账户", "field": "eventResponse[0].payeeAccount", "note": "拼接: acctName-bankName-acctNo后4位"},
        {"label": "申请时间", "field": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
        {"label": "到账时间", "field": "settledTime", "format": "YYYY-MM-DD HH:mm:ss"}
    ]
}


def execute(
    trade_no: str,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """查询转账交易支付凭证详情（电子回单）

    Args:
        trade_no: 转账交易单号。必填。如：TF202301010001
        request_id: 请求ID。可选。默认等于trade_no

    Returns:
        返回支付凭证详情，包含交易单号、金额、结算状态、到账账户等信息
        注意：实际页面会先调用queryRelation验证权限，仅审批人及发起人有权限查看
    """
    # v3版本API路径
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.trading.core.transfer.trading.query"

    # 默认值：requestId等于tradeNo
    payload = {
        "tradeNo": trade_no,
        "requestId": request_id if request_id else trade_no
    }

    return client.post(url, payload)


def query_relation(ticket_id: str) -> Dict[str, Any]:
    """查询权限关系（辅助API）

    Args:
        ticket_id: 工单ID

    Returns:
        返回有权限查看该凭证的用户名列表
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/fin.shield.opsflow.OpsflowService.queryRelation"
    payload = {"ticketId": ticket_id}
    return client.post(url, payload)
