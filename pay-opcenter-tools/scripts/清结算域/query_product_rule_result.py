"""
产品规则结果查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "ruleConfigNo": {
        "type": "string",
        "required": True,
        "description": "规则编号（路由 query 参数）"
    },
    "namespace": {
        "type": "string",
        "required": True,
        "default": "yz-settle-center",
        "description": "命名空间"
    }
}

# 数据展示类型（来源：步骤 1.2 提取的前端 display）
# 复合展示：规则因子详情 + 付款方优先级表(3列) + 收款方优先级表(3列)
DISPLAY_TYPE = "composite"
DISPLAY_BLOCKS = [
    "规则因子详情",
    "付款方优先级表(3列)",
    "收款方优先级表(3列)"
]


def execute(
    rule_config_no: str,
    namespace: str = "yz-settle-center",
) -> dict:
    """产品规则结果查询
    根据规则编号查询产品规则配置结果，包含规则因子详情、付款方优先级和收款方优先级。

    Args:
        rule_config_no: 规则编号。必填。
        namespace: 命名空间。默认=yz-settle-center。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.query"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "ruleConfigNo": rule_config_no,
        "namespace": namespace,
    }

    return client.post(url, payload)
