"""
累计属性配置列表查询 — 累计属性配置列表查询
来源：schemas/产品域/v1_属性列表.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：对应 JSON Schema）
PARAM_SCHEMA = {
    "propertyName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "累计属性名（搜索关键词，模糊匹配）"
    },
    "pageParam.page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码（嵌套在pageParam对象中传递）"
    },
}

# 数据展示列（来源：对应 JSON Schema display.columns）
# 注意：pageSize 仅前端Table组件使用（pagination.pageSize=10），不通过API传递
DISPLAY_COLUMNS = [
    {"title": "累计属性值", "dataIndex": "attributeValue"},
    {"title": "累计属性名", "dataIndex": "attributeName"},
    {"title": "记账标识码", "dataIndex": "identificationCode"},
    {"title": "映射位置", "dataIndex": "attributePos"},
    {"title": "创建时间", "dataIndex": "createTime", "format": "yyyy-MM-dd HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "modifyTime", "format": "yyyy-MM-dd HH:mm:ss"},
    {"title": "备注", "dataIndex": "remark"},
]


def execute(
    property_name: Optional[str] = None,
    page: int = 1,
) -> dict:
    """累计属性配置列表查询（v1）。
    查询产品域累计属性配置，支持按属性名模糊筛选。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        property_name: 累计属性名（搜索关键词，模糊匹配）。可选。默认为空（查全部）。
        page: 页码。可选。默认=1。
    """
    url = f"{BASE_URL}/dispatcher/prodtrans.property.findList"

    payload = {
        "propertyName": property_name if property_name is not None else "",
        "pageParam": {
            "page": page,
        },
    }

    return client.post(url, payload)
