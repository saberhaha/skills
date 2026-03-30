"""
模型信息管理 — 根据模型ID查询模型详情信息
来源：schemas/数据中心域/v1_模型信息管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "modelId": {
        "type": "string",
        "required": True,
        "description": "模型ID（路由参数，后端会转换为Long类型）"
    }
}

# 数据展示字段（详情页）
DISPLAY_FIELDS = [
    {"label": "ID", "dataIndex": "id"},
    {"label": "名称", "dataIndex": "name"},
    {"label": "描述", "dataIndex": "description"},
    {"label": "类型", "dataIndex": "type", "enum_values": {"COMMON": "通用", "ORIGIN": "原始", "CUSTOM": "自定义"}},
    {"label": "状态", "dataIndex": "state", "enum_values": {"CREATE": "草稿", "ON": "已开启", "OFF": "已关闭", "PAUSE": "已暂停"}},
    {"label": "API信息", "dataIndex": "api"},
    {"label": "字段信息", "dataIndex": "attributes"},
    {"label": "数据源信息", "dataIndex": "dataSourceConfigList"}
]

def execute(
    model_id: str
) -> dict:
    """查询模型详情信息

    根据模型ID获取模型的完整信息，包括名称、描述、类型、状态、API配置、字段信息等。

    Args:
        model_id: 模型ID。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.data.center.getModel"

    # 前端使用 singleParam 包装参数
    payload = {"singleParam": model_id}

    return client.post(url, payload)
