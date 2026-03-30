"""
权限配置-角色管理列表（v1）
来源：schemas/权限域/v1_权限配置_角色管理.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v1_权限配置_角色管理.json）
PARAM_SCHEMA = {
    "applicationName": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "PAY_OPCENTER": "支付运营平台",
            "PAY_OPCENTER_FAKE": "支付运营平台（新域名）",
            "PAY_CHECK": "对账平台",
            "CARD_GAOHUITONG": "多卡运营系统"
        },
        "description": "系统名称（空字符串=全部）"
    },
    "roleDesc": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "角色描述（模糊搜索）"
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 数据展示列（来源：schemas/权限域/v1_权限配置_角色管理.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "角色名称", "dataIndex": "roleName"},
    {"title": "系统", "dataIndex": "applicationName"},
    {"title": "描述", "dataIndex": "roleDesc"}
]


def get_permission_info(
    application_name: Optional[Literal["PAY_OPCENTER", "PAY_CHECK", "CARD_GAOHUITONG"]] = None,
    role_names: Optional[list] = None,
) -> dict:
    """查询权限列表（查询某系统或角色下的权限）
    辅助接口：POST /dispatcher/pay.opcenter.permission.queryPermissionInfo
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.permission.queryPermissionInfo"
    payload = {}
    if application_name is not None:
        payload["applicationName"] = application_name
    if role_names is not None:
        payload["roleNames"] = role_names
    return client.post(url, payload)


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /dispatcher/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    application_name: Optional[Literal["PAY_OPCENTER", "PAY_OPCENTER_FAKE", "PAY_CHECK", "CARD_GAOHUITONG"]] = "",
    role_desc: Optional[str] = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询权限配置-角色管理列表（v1）
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        application_name: 系统名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_OPCENTER_FAKE=支付运营平台（新域名）,
                          PAY_CHECK=对账平台, CARD_GAOHUITONG=多卡运营系统。默认空字符串（全部）。
        role_desc: 角色描述（模糊搜索）。可选。默认空字符串。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.permission.queryRoleInfoByPage"

    payload = {
        "applicationName": application_name,
        "roleDesc": role_desc,
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
