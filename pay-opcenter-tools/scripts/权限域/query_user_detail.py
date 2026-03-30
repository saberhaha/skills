"""
用户详情
来源：schemas/权限域/v3_用户详情.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_用户详情.json）
PARAM_SCHEMA = {
    "userName": {
        "type": "string",
        "required": True,
        "description": "用户名"
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
        "description": "系统"
    }
}

# 数据展示列（来源：schemas/权限域/v3_用户详情.json display.columns，type=detail）
DISPLAY_COLUMNS = [
    {"title": "用户名", "dataIndex": "userName"},
    {"title": "id", "dataIndex": "id"},
    {"title": "邮箱", "dataIndex": "email"},
    {"title": "性别", "dataIndex": "gender"},
    {"title": "手机号", "dataIndex": "phone"},
    {"title": "真名", "dataIndex": "realName"},
    {"title": "花名", "dataIndex": "aliasName"},
    {"title": "系统", "dataIndex": "applicationName"},
    {"title": "关联角色", "dataIndex": "roles"},
    {"title": "状态", "dataIndex": "status"}
]


def get_role_list(
    user_name: Optional[str] = None,
    application_name: Optional[str] = None,
) -> dict:
    """查询角色列表（不分页，用于展示用户关联角色）
    辅助接口：GET /v3/api/authority/role/list
    """
    url = f"{BASE_URL}/v3/api/authority/role/list"
    params = {}
    if user_name is not None:
        params["userName"] = user_name
    if application_name is not None:
        params["applicationName"] = application_name
    return client.get(url, params=params)


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /v3/api/dispatch/invoke/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    user_name: str,
    application_name: Literal["PAY_OPCENTER", "PAY_CHECK", "CARD_GAOHUITONG", "PAY_OPCENTER_FAKE"] = "PAY_OPCENTER",
) -> dict:
    """查询用户详情
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        user_name: 用户名。必填。
        application_name: 系统名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_CHECK=对账平台,
                          CARD_GAOHUITONG=多卡运营系统, PAY_OPCENTER_FAKE=支付-运营平台。默认 PAY_OPCENTER。
    """
    url = f"{BASE_URL}/v3/api/authority/detail"

    payload = {
        "userName": user_name,
        "applicationName": application_name,
    }

    return client.get(url, params=payload)
