"""
产品规则配置
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "product": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "产品常量 key（空=全部）"
    },
    "namespace": {
        "type": "string",
        "required": True,
        "default": "yz-settle-center",
        "description": "命名空间"
    }
}

# 数据展示类型（来源：步骤 1.2 提取的前端 display）
# 卡片展示：item_fields 为 ruleConfigNo 和 desc
DISPLAY_TYPE = "cards"
DISPLAY_ITEM_FIELDS = ["ruleConfigNo", "desc"]


def execute(
    product: str = "",
    namespace: str = "yz-settle-center",
) -> dict:
    """产品规则配置查询
    查询产品规则配置列表，以卡片形式展示规则编号和描述。

    Args:
        product: 产品常量 key。空=全部。默认=""。
        namespace: 命名空间。默认=yz-settle-center。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.list"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "product": product,
        "namespace": namespace,
    }

    return client.post(url, payload)
