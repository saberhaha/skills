"""
分组列表
来源：schemas/权限域/v3_分组列表.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/权限域/v3_分组列表.json）
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
        "description": "应用名称"
    },
    "groupName": {
        "type": "string",
        "required": False,
        "description": "分组名称"
    },
    "status": {
        "type": "enum",
        "enum_values": {
            "0": "禁用",
            "6": "启用"
        },
        "required": False,
        "description": "状态"
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

# 数据展示列（来源：schemas/权限域/v3_分组列表.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "id", "dataIndex": "id"},
    {"title": "组描述", "dataIndex": "groupDesc"},
    {"title": "组名", "dataIndex": "groupName"},
    {"title": "父分组名", "dataIndex": "parentName"},
    {"title": "应用名称", "dataIndex": "applicationName"},
    {"title": "状态", "dataIndex": "status"}
]


def get_applications() -> dict:
    """获取所有系统列表（applicationName 下拉选项）
    辅助接口：POST /v3/api/dispatch/invoke/pay.opcenter.get.applications
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.opcenter.get.applications"
    return client.post(url, {})


def execute(
    application_name: Optional[Literal["PAY_OPCENTER", "PAY_CHECK", "CARD_GAOHUITONG", "PAY_OPCENTER_FAKE"]] = None,
    group_name: Optional[str] = None,
    status: Optional[Literal["0", "6"]] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询分组列表
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        application_name: 应用名称。可选。枚举：PAY_OPCENTER=支付运营平台, PAY_CHECK=对账平台,
                          CARD_GAOHUITONG=多卡运营系统, PAY_OPCENTER_FAKE=支付-运营平台。
        group_name: 分组名称。可选。
        status: 状态。可选。枚举："0"=禁用, "6"=启用。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/v3/api/authority/group/page"

    payload = {
        "page": page,
        "pageSize": page_size,
    }
    if application_name is not None:
        payload["applicationName"] = application_name
    if group_name is not None:
        payload["groupName"] = group_name
    if status is not None:
        payload["status"] = status

    return client.get(url, params=payload)
