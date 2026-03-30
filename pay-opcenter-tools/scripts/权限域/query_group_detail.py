"""
分组详情
来源：schemas/权限域/v3_分组详情.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_分组详情.json）
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
    "groupId": {
        "type": "number",
        "required": True,
        "description": "分组ID (API中可能叫id)"
    }
}

# 数据展示列（来源：schemas/权限域/v3_分组详情.json display.columns，type=detail）
DISPLAY_COLUMNS = [
    {"title": "分组ID", "dataIndex": "id"},
    {"title": "组名", "dataIndex": "groupName"},
    {"title": "分组描述", "dataIndex": "groupDesc"},
    {"title": "父级分组", "dataIndex": "parentId"},
    {"title": "系统", "dataIndex": "applicationName"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "组员", "dataIndex": "userNames"}
]


def get_users_in_group(
    application_name: Optional[str] = None,
    group_id: Optional[int] = None,
) -> dict:
    """查询分组下的用户列表（不分页）
    辅助接口：GET /v3/api/authority/user/list
    """
    url = f"{BASE_URL}/v3/api/authority/user/list"
    params = {}
    if application_name is not None:
        params["applicationName"] = application_name
    if group_id is not None:
        params["groupId"] = group_id
    return client.get(url, params=params)


def get_group_list(application_name: Optional[str] = None) -> dict:
    """查询分组列表（不分页，用于父分组树展示）
    辅助接口：GET /v3/api/authority/group/list
    """
    url = f"{BASE_URL}/v3/api/authority/group/list"
    params = {}
    if application_name is not None:
        params["applicationName"] = application_name
    return client.get(url, params=params)


def get_role_permissions(
    application_name: Optional[str] = None,
    role_id: Optional[int] = None,
) -> dict:
    """查询角色的权限列表
    辅助接口：GET /v3/api/authority/role/permissions
    """
    url = f"{BASE_URL}/v3/api/authority/role/permissions"
    params = {}
    if application_name is not None:
        params["applicationName"] = application_name
    if role_id is not None:
        params["roleId"] = role_id
    return client.get(url, params=params)


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /v3/api/dispatch/invoke/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    group_id: int,
    application_name: Literal["PAY_OPCENTER", "PAY_CHECK", "CARD_GAOHUITONG", "PAY_OPCENTER_FAKE"] = "PAY_OPCENTER",
) -> dict:
    """查询分组详情
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        group_id: 分组ID（API传参中可能叫id）。必填。
        application_name: 应用名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_CHECK=对账平台,
                          CARD_GAOHUITONG=多卡运营系统, PAY_OPCENTER_FAKE=支付-运营平台。默认 PAY_OPCENTER。
    """
    url = f"{BASE_URL}/v3/api/authority/group/info"

    payload = {
        "groupId": group_id,
        "applicationName": application_name,
    }

    return client.get(url, params=payload)
