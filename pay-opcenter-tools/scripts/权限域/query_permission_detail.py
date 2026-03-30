"""
权限详情
来源：schemas/权限域/v3_权限详情.json
"""
import sys
import os
from typing import Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_权限详情.json）
PARAM_SCHEMA = {
    "permissionId": {
        "type": "number",
        "required": True,
        "description": "权限ID"
    },
    "applicationName": {
        "type": "enum",
        "enum_values": {
            "PAY_OPCENTER": "支付运营平台",
            "PAY_CHECK": "对账平台",
            "CARD_GAOHUITONG": "多卡运营系统",
            "PAY_OPCENTER_FAKE": "支付-运营平台"
        },
        "required": False,
        "default": "PAY_OPCENTER",
        "description": "应用名称"
    }
}

# 数据展示列（来源：schemas/权限域/v3_权限详情.json，type=tree，columns=[UNRESOLVED]）
DISPLAY_COLUMNS = "[UNRESOLVED: 无表格列定义，请人工补全]"


def execute(
    permission_id: int,
    application_name: Literal["PAY_OPCENTER", "PAY_CHECK", "CARD_GAOHUITONG", "PAY_OPCENTER_FAKE"] = "PAY_OPCENTER",
) -> dict:
    """查询权限详情
    用户只需提供核心查询条件，其余参数自动使用页面默认值。
    注意：该接口返回树形结构权限数据，展示列定义待人工补全。

    Args:
        permission_id: 权限ID。必填。
        application_name: 应用名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_CHECK=对账平台,
                          CARD_GAOHUITONG=多卡运营系统, PAY_OPCENTER_FAKE=支付-运营平台。默认 PAY_OPCENTER。
    """
    url = f"{BASE_URL}/v3/api/authority/detail"

    payload = {
        "permissionId": permission_id,
        "applicationName": application_name,
    }

    return client.get(url, params=payload)
