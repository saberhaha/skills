"""
场景KV-运行时名单 — 查询场景KV运行时名单列表
来源：schemas/收银台域/v3_场景KV运行时.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_场景KV运行时.json）
PARAM_SCHEMA = {
    "current": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "size": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
    "text": {"type": "string", "required": False, "description": "关键字搜索（按Key或文案过滤）"},
}

# 数据展示列（来源：v3_场景KV运行时.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "Key", "dataIndex": "name"},
    {"title": "文案", "dataIndex": "text"},
    {"title": "创建者", "dataIndex": "creator"},
    {"title": "创建于", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改于", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    current: int = 1,
    size: int = 10,
    text: Optional[str] = None,
) -> dict:
    """查询场景KV-运行时名单列表

    Args:
        current: 当前页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
        text: 关键字搜索（按Key或文案过滤）。可选。
    """
    url = f"{BASE_URL}/v3/api/cashier-biz-manage/scenariokvs/type/runtime/names"
    params = {"current": current, "size": size}
    if text is not None:
        params["text"] = text
    return client.get(url, params)
