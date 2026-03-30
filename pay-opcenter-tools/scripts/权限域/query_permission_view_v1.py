"""
权限视图（v1）
来源：schemas/权限域/v1_权限视图.json
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v1_权限视图.json）
# 接口无需传参，自动取当前登录用户的 Session 信息查询其权限
PARAM_SCHEMA = {}

# 数据展示列（来源：schemas/权限域/v1_权限视图.json display.columns，type=detail）
# 后端返回结构包含 userInfo / rolesInfo / permissionsInfo 三个对象
# 页面展示角色时取 roleDesc 字段，权限时取 permissionDesc 字段
DISPLAY_COLUMNS = [
    {"title": "用户名", "dataIndex": "userInfo.username"},
    {"title": "邮箱", "dataIndex": "userInfo.email"},
    {"title": "支付运营平台-角色", "dataIndex": "rolesInfo.PAY_OPCENTER"},
    {"title": "支付运营平台-权限", "dataIndex": "permissionsInfo.PAY_OPCENTER"},
    {"title": "对账平台-角色", "dataIndex": "rolesInfo.PAY_CHECK"},
    {"title": "对账平台-权限", "dataIndex": "permissionsInfo.PAY_CHECK"}
]


def execute() -> dict:
    """查询权限视图（v1）
    接口无需传参，自动取当前登录用户的 Session 信息查询其在各系统下的角色与权限。
    后端返回结构包含 userInfo / rolesInfo / permissionsInfo 三个对象。
    """
    url = f"{BASE_URL}/query/user/permission"

    return client.post(url, {})
