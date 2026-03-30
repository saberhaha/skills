"""
费率模板管理 — 查询费率模板
来源：schemas/计费规则域/v3_费率模板管理.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "feeProductCode": {"type": "string", "required": True, "description": "计费产品编码，必填"},
    "industryCode": {"type": "string", "required": True, "description": "行业编码，必填"},
}

DISPLAY_TYPE = "card"
DISPLAY_NOTE = "非表格页面：展示标准算账费率和个性化算账费率模板卡片"


def execute(
    fee_product_code: str,
    industry_code: str,
) -> dict:
    """查询费率模板

    Args:
        fee_product_code: 计费产品编码。必填。
        industry_code: 行业编码。必填。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.feepackage.list"

    payload = {
        "feeProductCode": fee_product_code,
        "industryCode": industry_code,
    }

    return client.post(url, payload)
