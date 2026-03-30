"""
权限配置-资源管理列表（v1）
来源：schemas/权限域/v1_权限配置_资源管理.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v1_权限配置_资源管理.json）
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
    "resourceIdentification": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "资源名称（模糊搜索）"
    },
    "resourceDesc": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "资源描述（模糊搜索）"
    },
    "resourceType": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "action": "action（请求类资源）",
            "menu": "menu（菜单类资源）"
        },
        "description": "资源类型（空字符串=全部）"
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

# 数据展示列（来源：schemas/权限域/v1_权限配置_资源管理.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "资源名称", "dataIndex": "identification"},
    {"title": "系统", "dataIndex": "applicationName"},
    {"title": "类型", "dataIndex": "resourceType"},
    {"title": "描述", "dataIndex": "resourceDesc"},
    {"title": "内容", "dataIndex": "resourceContent"}
]


def get_dubbo_config(http_path: str) -> dict:
    """查询资源的 Dubbo 配置信息
    辅助接口：POST /dispatcher/pay.opcenter.dubbo.queryDubboConfigByHttpPath
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.dubbo.queryDubboConfigByHttpPath"
    return client.post(url, {"httpPath": http_path})


def get_permission_info(
    application_name: Optional[str] = None,
    resource_identification: Optional[str] = None,
) -> dict:
    """查询资源关联的权限信息
    辅助接口：POST /dispatcher/pay.opcenter.permission.queryPermissionInfo
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.permission.queryPermissionInfo"
    payload = {}
    if application_name is not None:
        payload["applicationName"] = application_name
    if resource_identification is not None:
        payload["resourceIdentification"] = resource_identification
    return client.post(url, payload)


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /dispatcher/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    application_name: Optional[Literal["PAY_OPCENTER", "PAY_OPCENTER_FAKE", "PAY_CHECK", "CARD_GAOHUITONG"]] = "",
    resource_identification: Optional[str] = "",
    resource_desc: Optional[str] = "",
    resource_type: Optional[Literal["action", "menu"]] = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询权限配置-资源管理列表（v1）
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        application_name: 系统名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_OPCENTER_FAKE=支付运营平台（新域名）,
                          PAY_CHECK=对账平台, CARD_GAOHUITONG=多卡运营系统。默认空字符串（全部）。
        resource_identification: 资源名称（模糊搜索）。可选。默认空字符串。
        resource_desc: 资源描述（模糊搜索）。可选。默认空字符串。
        resource_type: 资源类型。可选。枚举："action"=请求类资源, "menu"=菜单类资源。默认空字符串（全部）。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.opcenter.permission.queryResourceInfoByPage"

    payload = {
        "applicationName": application_name,
        "resourceIdentification": resource_identification,
        "resourceDesc": resource_desc,
        "resourceType": resource_type,
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
