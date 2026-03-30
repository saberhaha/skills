"""
权限配置-用户管理列表（v1）
来源：schemas/权限域/v1_权限配置_用户管理.json
"""
import sys
import os
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v1_权限配置_用户管理.json）
PARAM_SCHEMA = {
    "userName": {
        "type": "string",
        "required": False,
        "description": "用户名（不传表示查全部）"
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

# 数据展示列（来源：schemas/权限域/v1_权限配置_用户管理.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "用户名", "dataIndex": "userName"},
    {"title": "姓名", "dataIndex": "realName"},
    {"title": "用户邮箱", "dataIndex": "email"},
    {"title": "花名", "dataIndex": "aliasName"},
    {"title": "性别", "dataIndex": "gender"}
]


def get_user_roles(user_name: str) -> dict:
    """查询用户下的角色信息（编辑时使用）
    辅助接口：POST /dispatcher/pay.opcenter.permission.queryRoleInfo
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.permission.queryRoleInfo"
    return client.post(url, {"userName": user_name})


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /dispatcher/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    user_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询权限配置-用户管理列表（v1）
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        user_name: 用户名。可选。不传表示查全部。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.permission.queryUserInfoByPage"

    payload = {
        "page": page,
        "pageSize": page_size,
    }
    if user_name is not None:
        payload["userName"] = user_name

    return client.post(url, payload)
