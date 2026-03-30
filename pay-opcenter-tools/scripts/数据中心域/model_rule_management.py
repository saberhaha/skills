"""
模型规则管理 — 根据查询类型（Model/Rule/Action）查询数据中心模型、规则、事件列表
来源：schemas/数据中心域/v1_模型规则管理.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "searchType": {
        "type": "enum",
        "required": False,
        "default": "Model",
        "enum_values": {"Model": "模型", "Rule": "规则", "Action": "事件"},
        "description": "查询类型（决定API调用）"
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
    },
    "id": {
        "type": "string",
        "required": False,
        "description": "ID（可选）"
    },
    "name": {
        "type": "string",
        "required": False,
        "description": "名称（可选）"
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "description": "创建开始时间（可选）"
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "description": "创建结束时间（可选）"
    },
    "modelId": {
        "type": "string",
        "required": False,
        "description": "模型ID（仅Action类型查询时使用）"
    }
}

# 数据展示列（根据searchType动态变化）
DISPLAY_COLUMNS = {
    "Model": [
        {"title": "ID", "dataIndex": "id"},
        {"title": "名称", "dataIndex": "name"},
        {"title": "描述", "dataIndex": "description"},
        {"title": "状态", "dataIndex": "state", "enum_values": {"CREATE": "草稿", "ON": "已开启", "OFF": "已关闭", "PAUSE": "已暂停"}},
        {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY/MM/DD hh:mm:ss"}
    ],
    "Rule": [
        {"title": "ID", "dataIndex": "id"},
        {"title": "名称", "dataIndex": "name"},
        {"title": "负责人", "dataIndex": "principal"},
        {"title": "描述", "dataIndex": "desc"},
        {"title": "状态", "dataIndex": "state", "enum_values": {"CREATE": "草稿", "ON": "已开启", "OFF": "已关闭", "PAUSE": "已暂停"}},
        {"title": "创建时间", "dataIndex": "createAt", "format": "YYYY/MM/DD hh:mm:ss"}
    ],
    "Action": [
        {"title": "ID", "dataIndex": "id"},
        {"title": "名称", "dataIndex": "name"},
        {"title": "规则ID", "dataIndex": "ruleId"},
        {"title": "描述", "dataIndex": "description"},
        {"title": "输入模型ID", "dataIndex": "inputModelId"},
        {"title": "输出模型ID", "dataIndex": "outputModelId"},
        {"title": "父节点ID", "dataIndex": "parentIds"},
        {"title": "状态", "dataIndex": "state", "enum_values": {"CREATE": "草稿", "ON": "已开启", "OFF": "已关闭", "PAUSE": "已暂停"}},
        {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY/MM/DD hh:mm:ss"}
    ]
}

# API 映射
API_MAPPING = {
    "Model": "pay.data.center.modelList",
    "Rule": "pay.data.center.ruleList",
    "Action": "pay.data.center.actionList"
}

def execute(
    search_type: Optional[Literal["Model", "Rule", "Action"]] = None,
    page: int = 1,
    page_size: int = 10,
    id: Optional[str] = None,
    name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    model_id: Optional[str] = None
) -> dict:
    """查询数据中心模型/规则/事件列表

    根据查询类型返回对应的列表数据。用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        search_type: 查询类型。枚举：Model=模型, Rule=规则, Action=事件。默认=Model(模型)。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        id: ID筛选。可选。
        name: 名称筛选。可选。
        start_date: 创建开始时间。格式：YYYY-MM-DD。可选。
        end_date: 创建结束时间。格式：YYYY-MM-DD。可选。
        model_id: 模型ID。仅Action类型查询时使用。可选。
    """
    # 处理默认值
    if search_type is None:
        search_type = "Model"

    # 根据 search_type 选择 API
    api = API_MAPPING[search_type]
    url = f"{BASE_URL}/dispatcher/{api}"

    # 构建请求参数
    payload = {
        "page": page,
        "pageSize": page_size,
    }

    # 添加可选参数（过滤空值）
    if id is not None and id != "":
        payload["id"] = id
    if name is not None and name != "":
        payload["name"] = name
    if start_date is not None and start_date != "":
        payload["startDate"] = start_date
    if end_date is not None and end_date != "":
        payload["endDate"] = end_date
    if model_id is not None and model_id != "":
        payload["modelId"] = model_id

    return client.post(url, payload)
