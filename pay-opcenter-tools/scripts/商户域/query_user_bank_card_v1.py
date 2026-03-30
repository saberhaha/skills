"""
用户快捷支付绑定银行卡查询 — 用户快捷支付绑定银行卡查询
来源：schemas/商户域/v1_用户绑卡列表.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "phone": {
        "type": "string",
        "required": True,
        "description": "银行卡绑定手机号（必填，数字）"
    },
    "bankCardLastFour": {
        "type": "string",
        "required": True,
        "description": "银行卡后四位（必填，数字）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
# 无分页
DISPLAY_COLUMNS = [
    {"title": "序号", "dataIndex": "id"},
    {"title": "绑卡ID", "dataIndex": "cardBindId"},
    {"title": "发卡行", "dataIndex": "bankName"},
    {"title": "后四位", "dataIndex": "cardNoLastFour"},
    {"title": "手机号", "dataIndex": "mobile"},
    {"title": "绑卡时间", "dataIndex": "updated"},
]


def execute(
    phone: str,
    bank_card_last_four: str,
) -> dict:
    """用户快捷支付绑定银行卡查询（v1）
    根据手机号和银行卡后四位查询用户绑定的银行卡列表。无分页，返回全量结果。

    Args:
        phone: 银行卡绑定手机号（必填）。
        bank_card_last_four: 银行卡后四位（必填）。
    """
    url = f"{BASE_URL}/dispatcher/merchant.userBindCard.list"

    payload = {
        "phone": phone,
        "bankCardLastFour": bank_card_last_four,
    }

    return client.post(url, payload)
