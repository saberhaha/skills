"""
微信支付实名认证超时查询 — 微信支付实名认证超时查询
来源：schemas/商户域/v3_微信证书过期管理.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "userNo": {
        "type": "string",
        "required": True,
        "description": "支付商户号"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
# 无分页，返回单条商户实名认证信息
# 时间字段格式为 timestamp_ms（new Date(ts).toLocaleString()）
DISPLAY_COLUMNS = [
    {"title": "创建时间", "dataIndex": "createdAt", "format": "timestamp_ms"},
    {"title": "状态", "dataIndex": "status"},       # enum: 0=初始化, 10=超时, 20=完成
    {"title": "支付商户号", "dataIndex": "userNo"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "timestamp_ms"},
    {"title": "实名认证开始时间", "dataIndex": "wxAuthStartTime", "format": "timestamp_ms"},
    {"title": "实名认证完成时间", "dataIndex": "wxAuthFinishTime", "format": "timestamp_ms"},
    {"title": "实名认证超时时间", "dataIndex": "wxAuthOverTime", "format": "timestamp_ms"},
]


def execute(
    user_no: str,
) -> dict:
    """微信支付实名认证超时查询（v3）
    查询指定支付商户号的微信实名认证超时信息。返回单条记录，无分页。
    时间字段均为毫秒时间戳（timestamp_ms），负值显示'-'。

    Args:
        user_no: 支付商户号（必填）。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.ucert.overtime.query"

    params = {"userNo": user_no}

    return client.get(url, params)
