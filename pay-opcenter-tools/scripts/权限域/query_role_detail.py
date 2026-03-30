"""
角色详情
来源：schemas/权限域/v3_角色详情.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_角色详情.json）
PARAM_SCHEMA = {
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
    },
    "roleId": {
        "type": "number",
        "required": True,
        "description": "角色ID"
    }
}

# 数据展示列（来源：schemas/权限域/v3_角色详情.json display.columns，type=detail）
DISPLAY_COLUMNS = [
    {"title": "id", "dataIndex": "roleId"},
    {"title": "角色名", "dataIndex": "roleName"},
    {"title": "系统", "dataIndex": "applicationName"},
    {"title": "角色描述", "dataIndex": "roleDesc"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "关联形式", "dataIndex": "relationType"},
    {"title": "关联人员", "dataIndex": "userNames"},
    {"title": "关联分组", "dataIndex": "groupIds"},
    {"title": "关联权限", "dataIndex": "permissions"}
]


def get_role_list(
    application_name: Optional[str] = None,
    user_name: Optional[str] = None,
) -> dict:
    """查询角色列表（不分页，用于角色关联展示）
    辅助接口：GET /v3/api/authority/role/list
    """
    url = f"{BASE_URL}/v3/api/authority/role/list"
    params = {}
    if application_name is not None:
        params["applicationName"] = application_name
    if user_name is not None:
        params["userName"] = user_name
    return client.get(url, params=params)


def get_role_users(
    role_id: int,
    application_name: Optional[str] = None,
) -> dict:
    """查询角色下关联的用户列表
    辅助接口：GET /v3/api/authority/role/users
    """
    url = f"{BASE_URL}/v3/api/authority/role/users"
    params = {"roleId": role_id}
    if application_name is not None:
        params["applicationName"] = application_name
    return client.get(url, params=params)


def get_user_list(application_name: Optional[str] = None) -> dict:
    """查询用户列表（不分页，用于用户选择）
    辅助接口：GET /v3/api/authority/user/list
    """
    url = f"{BASE_URL}/v3/api/authority/user/list"
    params = {}
    if application_name is not None:
        params["applicationName"] = application_name
    return client.get(url, params=params)


def get_group_info(
    application_name: Optional[str] = None,
    group_id: Optional[int] = None,
) -> dict:
    """查询分组信息
    辅助接口：GET /v3/api/authority/group/info
    """
    url = f"{BASE_URL}/v3/api/authority/group/info"
    params = {}
    if application_name is not None:
        params["applicationName"] = application_name
    if group_id is not None:
        params["groupId"] = group_id
    return client.get(url, params=params)


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /v3/api/dispatch/invoke/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    role_id: int,
    application_name: Literal["PAY_OPCENTER", "PAY_CHECK", "CARD_GAOHUITONG", "PAY_OPCENTER_FAKE"] = "PAY_OPCENTER",
) -> dict:
    """查询角色详情（含角色关联权限）
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        role_id: 角色ID。必填。
        application_name: 应用名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_CHECK=对账平台,
                          CARD_GAOHUITONG=多卡运营系统, PAY_OPCENTER_FAKE=支付-运营平台。默认 PAY_OPCENTER。
    """
    url = f"{BASE_URL}/v3/api/authority/role/permissions"

    payload = {
        "roleId": role_id,
        "applicationName": application_name,
    }

    return client.get(url, params=payload)
