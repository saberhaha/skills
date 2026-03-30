"""
网关API测试参数查询 — 网关API测试参数查询
来源：schemas/网关域/v1_网关测试.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/网关域/v1_网关测试.json）
PARAM_SCHEMA = {
    "apiId": {
        "type": "string",
        "required": True,
        "description": "网关API的ID（从网关列表页点击'测试'跳转时通过路由参数传入）"
    },
}

# 数据展示列（来源：schemas/网关域/v1_网关测试.json display，dynamic_form 类型）
# 返回 paraList 数组，每条记录的字段如下
DISPLAY_COLUMNS = [
    {"title": "参数名称", "dataIndex": "name"},
    {"title": "数据类型", "dataIndex": "type"},
    {"title": "描述",     "dataIndex": "desc"},
    {"title": "是否必须", "dataIndex": "required"},
    {"title": "测试值",   "dataIndex": "value"},
]


def execute(
    api_id: str,
) -> dict:
    """查询网关API测试参数元信息。
    加载指定 API 的入参定义（参数名、类型、描述、是否必须），供用户填写测试值后执行测试。
    注意：执行测试本身（doTest）为操作类接口，不在此 Skill 范围内。

    Args:
        api_id: 网关API的ID。必填。可从 query_gateway_list 的返回结果中获取 apiId 字段。
    """
    url = f"{BASE_URL}/dispatcher/gateway.admin.api.testParam"

    payload: dict = {
        "apiId": api_id,
    }

    return client.post(url, payload)
