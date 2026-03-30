"""
费率模板管理
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "feeProductCode": {
        "type": "string",
        "required": True,
        "description": "计费产品编码"
    },
    "industryCode": {
        "type": "string",
        "required": True,
        "description": "行业编码"
    }
}

# 数据展示类型（来源：步骤 1.2 提取的前端 display）
# 卡片展示：包含标准算账费率（单模板）和个性化算账费率（模板列表）
DISPLAY_TYPE = "cards"
DISPLAY_SECTIONS = [
    "标准算账费率（单模板）",
    "个性化算账费率（模板列表）"
]


def execute(
    fee_product_code: str,
    industry_code: str,
) -> dict:
    """费率模板管理查询
    根据计费产品编码和行业编码查询费率模板，包含标准算账费率和个性化算账费率。

    Args:
        fee_product_code: 计费产品编码。必填。
        industry_code: 行业编码。必填。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.feepackage.list"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "feeProductCode": fee_product_code,
        "industryCode": industry_code,
    }

    return client.post(url, payload)
