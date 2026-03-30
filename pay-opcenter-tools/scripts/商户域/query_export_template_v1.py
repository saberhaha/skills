"""
导出平台模板列表查询 — 导出平台模板列表查询
来源：schemas/商户域/v1_导出模板管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "templateId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "模板ID"
    },
    "templateName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "模板名称"
    },
    "appName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "接入方应用名称"
    },
    "currentPage": {
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
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "模板号", "dataIndex": "templateId"},
    {"title": "模板名称", "dataIndex": "templateName"},
    {"title": "接入方应用", "dataIndex": "appName"},
    {"title": "模板文件预览", "dataIndex": "templateUrl"},
]


def execute(
    template_id: Optional[str] = None,
    template_name: Optional[str] = None,
    app_name: Optional[str] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """导出平台模板列表查询（v1）
    查询导出平台模板列表，支持按模板ID、模板名称、接入方应用名称筛选。

    Args:
        template_id: 模板ID。可选。
        template_name: 模板名称。可选。
        app_name: 接入方应用名称。可选。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/exportplatform.template.queryPageExportTemplate"

    payload = {
        "templateId": template_id if template_id is not None else "",
        "templateName": template_name if template_name is not None else "",
        "appName": app_name if app_name is not None else "",
        "currentPage": current_page,
        "size": size,
    }

    return client.post(url, payload)
