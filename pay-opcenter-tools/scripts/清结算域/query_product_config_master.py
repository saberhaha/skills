"""
产品配置主数据
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "templateNo": {
        "type": "string",
        "required": True,
        "description": "模板编号（路由 query 参数）"
    },
    "namespace": {
        "type": "string",
        "required": True,
        "default": "yz-settle-center",
        "description": "命名空间"
    },
    "ruleConfigNo": {
        "type": "string",
        "required": False,
        "description": "编辑态规则编号（路由 query 参数）"
    }
}

# 数据展示类型（来源：步骤 1.2 提取的前端 display）
# 表单展示：包含产品码配置、结算模板配置、付款方资产优先级、收款方资产优先级
DISPLAY_TYPE = "form"
DISPLAY_SECTIONS = [
    "产品码配置",
    "结算模板配置",
    "付款方资产优先级",
    "收款方资产优先级"
]


def execute(
    template_no: str,
    namespace: str = "yz-settle-center",
    rule_config_no: Optional[str] = None,
) -> dict:
    """产品配置主数据查询
    根据模板编号查询产品配置主数据，包含产品码配置、结算模板配置、资产优先级等。

    Args:
        template_no: 模板编号。必填。
        namespace: 命名空间。默认=yz-settle-center。
        rule_config_no: 编辑态规则编号。可选，用于编辑场景。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.template.query"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "templateNo": template_no,
        "namespace": namespace,
    }

    # 可选参数填充
    if rule_config_no is not None:
        payload["ruleConfigNo"] = rule_config_no

    return client.post(url, payload)


def query_rule_config(
    rule_config_no: str,
    namespace: str = "yz-settle-center",
) -> dict:
    """规则配置查询（辅助接口）
    根据规则编号查询规则配置详情。

    Args:
        rule_config_no: 规则编号。必填。
        namespace: 命名空间。默认=yz-settle-center。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.query"

    payload = {
        "ruleConfigNo": rule_config_no,
        "namespace": namespace,
    }

    return client.post(url, payload)
