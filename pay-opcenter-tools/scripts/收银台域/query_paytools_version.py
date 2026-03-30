"""
PayTools版本 — 查询PayTools版本列表
来源：schemas/收银台域/v3_PayTools版本.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_PayTools版本.json）
PARAM_SCHEMA = {
    "type": {
        "type": "enum",
        "required": False,
        "default": 1,
        "enum_values": {1: "PayTools全局匹配(PayListGlobal)", 2: "PayTools优先匹配(PayListPriotiry)"},
        "description": "版本类型，默认为1（全局匹配）"
    },
    "current": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "size": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
    "desc": {"type": "string", "required": False, "description": "关键字搜索（按版本描述/备注过滤）"},
}

# 数据展示列（来源：v3_PayTools版本.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "id", "dataIndex": "id"},
    {"title": "类型", "dataIndex": "rollbackFrom", "format": "enum_render: rollbackFrom>0→回滚; published=1→发布; else→保存"},
    {"title": "描述", "dataIndex": "desc"},
    {"title": "创建者", "dataIndex": "creator"},
    {"title": "创建于", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改于", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "发布于", "dataIndex": "publishAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    type: int = 1,
    current: int = 1,
    size: int = 10,
    desc: Optional[str] = None,
) -> dict:
    """查询PayTools版本列表
    用户可按版本类型（全局匹配/优先匹配）查询版本历史，其余参数使用页面默认值。

    Args:
        type: 版本类型。可选。枚举：1=PayTools全局匹配, 2=PayTools优先匹配。默认=1。
        current: 当前页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
        desc: 关键字搜索（按版本描述/备注过滤）。可选。
    """
    url = f"{BASE_URL}/v3/api/cashier-biz-manage/shared/group/type/{type}/list"
    params = {
        "current": current,
        "size": size,
    }
    if desc is not None:
        params["desc"] = desc
    return client.get(url, params)
