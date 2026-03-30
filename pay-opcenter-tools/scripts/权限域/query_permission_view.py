"""
权限视图（v3）
来源：schemas/权限域/v3_权限视图.json
"""
import sys
import os
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_权限视图.json）
PARAM_SCHEMA = {
    "username": {
        "type": "string",
        "required": True,
        "description": "用户名（前端自动取当前登录用户 window._global.user.username）"
    }
}

# 数据展示列（来源：schemas/权限域/v3_权限视图.json display.columns，type=detail）
DISPLAY_COLUMNS = [
    {"title": "用户名", "dataIndex": "username"},
    {"title": "邮箱", "dataIndex": "email"},
    {"title": "支付运营平台角色", "dataIndex": "PAY_OPCENTER_ROLES"},
    {"title": "支付运营平台权限", "dataIndex": "PAY_OPCENTER_PERMISSIONS"},
    {"title": "对账平台角色", "dataIndex": "PAY_CHECK_ROLES"},
    {"title": "对账平台权限", "dataIndex": "PAY_CHECK_PERMISSIONS"}
]


def execute(
    username: str,
) -> dict:
    """查询权限视图（v3）
    返回当前用户（或指定用户）在各个系统下的关联角色与权限详情。

    Args:
        username: 用户名。必填。前端自动从登录 Session 获取。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.opcenter.permission.queryAllUserInfo"

    payload = {
        "username": username
    }

    return client.get(url, params=payload)
