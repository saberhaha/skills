"""
网关API列表查询 — 网关API列表查询
来源：schemas/网关域/v1_网关列表.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/网关域/v1_网关列表.json）
PARAM_SCHEMA = {
    "applicationName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "应用名称（模糊搜索）"
    },
    "version": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "版本号"
    },
    "interfaceName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "java接口名（不包含方法名）"
    },
    "service": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "API service部分（从api全称按最后一个'.'拆分取前半段）"
    },
    "method": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "API method部分（从api全称按最后一个'.'拆分取后半段）"
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "size": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
}

# 数据展示列（来源：schemas/网关域/v1_网关列表.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "ApiId",   "dataIndex": "apiId"},
    {"title": "Api名称", "dataIndex": "api"},
    {"title": "描述",    "dataIndex": "desc"},
    {"title": "版本",    "dataIndex": "version"},
    {"title": "应用名称","dataIndex": "appName"},
]


def execute(
    application_name: Optional[str] = None,
    version: Optional[str] = None,
    interface_name: Optional[str] = None,
    api_full_name: Optional[str] = None,
    service: Optional[str] = None,
    method: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> dict:
    """查询网关API列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        application_name: 应用名称，支持模糊搜索。可选。
        version: 版本号。可选。
        interface_name: java接口名（不含方法名）。可选。
        api_full_name: API完整名称（如 gateway.admin.api.list），前端按最后一个'.'拆分为
                       service 和 method 两个字段传给后端。若同时传入 service/method 则优先
                       使用 service/method；否则自动拆分 api_full_name。可选。
        service: API service部分（api全称最后一个'.'前的部分）。可选。
        method: API method部分（api全称最后一个'.'后的部分）。可选。
        page: 页码。默认=1。
        size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/gateway.admin.api.list"

    # 若用户传入 api_full_name，则自动拆分为 service + method
    resolved_service = service
    resolved_method = method
    if api_full_name and not service and not method:
        dot_idx = api_full_name.rfind(".")
        if dot_idx != -1:
            resolved_service = api_full_name[:dot_idx]
            resolved_method = api_full_name[dot_idx + 1:]
        else:
            resolved_service = api_full_name
            resolved_method = ""

    payload: dict = {
        "applicationName": application_name if application_name is not None else "",
        "version": version if version is not None else "",
        "interfaceName": interface_name if interface_name is not None else "",
        "service": resolved_service if resolved_service is not None else "",
        "method": resolved_method if resolved_method is not None else "",
        "page": page,
        "size": size,
    }

    return client.post(url, payload)
