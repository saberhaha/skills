"""
用户列表
来源：schemas/权限域/v3_用户列表.json
"""
import sys
import os
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_用户列表.json）
PARAM_SCHEMA = {
    "email": {
        "type": "string",
        "required": False,
        "description": "邮箱"
    },
    "userName": {
        "type": "string",
        "required": False,
        "description": "用户名"
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

# 数据展示列（来源：schemas/权限域/v3_用户列表.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "id", "dataIndex": "id"},
    {"title": "用户名", "dataIndex": "userName"},
    {"title": "花名", "dataIndex": "aliasName"},
    {"title": "性别", "dataIndex": "gender"},
    {"title": "邮箱", "dataIndex": "email"},
    {"title": "手机号", "dataIndex": "phone"},
    {"title": "真实姓名", "dataIndex": "realName"},
    {"title": "状态", "dataIndex": "status"}
]


def execute(
    email: Optional[str] = None,
    user_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询用户列表
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        email: 邮箱。可选。
        user_name: 用户名。可选。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/v3/api/authority/user"

    payload = {
        "page": page,
        "pageSize": page_size,
    }
    if email is not None:
        payload["email"] = email
    if user_name is not None:
        payload["userName"] = user_name

    return client.get(url, params=payload)
