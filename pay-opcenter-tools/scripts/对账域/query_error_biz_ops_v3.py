"""
差错诊断-业务操作记录 — v3 差错诊断业务侧操作记录查询
来源：schemas/对账域/v3_差错诊断_业务操作记录.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "bizId": {
        "type": "string",
        "required": True,
        "description": "业务单号（路由参数，必填）"
    },
    "bizType": {
        "type": "string",
        "required": True,
        "description": "业务类型（路由参数，必填）"
    },
    "channelType": {
        "type": "string",
        "required": True,
        "description": "资金渠道（路由参数，必填）"
    },
    "mistakeAcctType": {
        "type": "string",
        "required": True,
        "description": "差错类型（路由参数，必填）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "操作时间", "dataIndex": "opsTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作", "dataIndex": "opsName"},
    {"title": "操作详情", "dataIndex": "opsDetail"},
    {"title": "操作状态", "dataIndex": "operateStatusDesc"},
    {"title": "操作人", "dataIndex": "operatorName"},
    {"title": "备注", "dataIndex": "extra"},
]


def execute(
    biz_id: str,
    biz_type: str,
    channel_type: str,
    mistake_acct_type: str,
) -> dict:
    """差错诊断-业务操作记录（v3）- 查询差错诊断业务侧操作记录。

    Args:
        biz_id: 业务单号（必填）。
        biz_type: 业务类型（必填）。
        channel_type: 资金渠道（必填）。
        mistake_acct_type: 差错类型（必填）。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/diagnosic/getOpsRecords"

    payload = {
        "bizId": biz_id,
        "bizType": biz_type,
        "channelType": channel_type,
        "mistakeAcctType": mistake_acct_type,
    }

    return client.post(url, payload)
