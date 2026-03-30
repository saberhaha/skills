"""
页面证书管理 — 查询页面证书列表
来源：schemas/收银台域/v3_页面证书管理.json
"""
import sys
import os
import time
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_页面证书管理.json）
PARAM_SCHEMA = {
    "biz": {
        "type": "enum",
        "required": True,
        "enum_values": {
            "wsc": "微商城",
            "wxd": "微小店",
            "aiguangshop": "爱逛买手店",
            "wangxiaodian": "旺小店",
            "beauty": "美业",
        },
        "description": "业务线类型。注：也可能包含服务端动态下发的其他业务线key"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "status": {
        "type": "enum",
        "required": False,
        "default": 0,
        "enum_values": {"0": "全部", "1": "未发布", "2": "已发布", "3": "历史版本"},
        "description": "发布状态筛选；默认0=全部"
    },
    "t": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "description": "时间戳（前端用于防缓存，值为 Date.now()）"
    },
}

# 数据展示列（来源：v3_页面证书管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "页面标题", "dataIndex": "pageName"},
    {"title": "页面标识", "dataIndex": "pageId"},
    {"title": "业务线id", "dataIndex": "sourceAppCode"},
    {"title": "业务类型", "dataIndex": "bizType"},
    {"title": "所属功能", "dataIndex": "productId", "format": "enum_render: 1→入网认证"},
    {"title": "发布状态", "dataIndex": "status", "format": "enum_render: 1→未发布; 2→已发布; 3→历史版本"},
    {"title": "业务场景", "dataIndex": "bizScene"},
    {"title": "操作端", "dataIndex": "terminalType", "format": "enum_render: 1→PC; 3→H5; 4→小程序"},
    {"title": "版本", "dataIndex": "version"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作人", "dataIndex": "opName"},
]


def execute(
    biz: Literal["wsc", "wxd", "aiguangshop", "wangxiaodian", "beauty"],
    page: int = 1,
    status: int = 0,
) -> dict:
    """查询页面证书列表
    按业务线查询页面证书，可按发布状态筛选。

    Args:
        biz: 业务线类型。必填。枚举：wsc=微商城, wxd=微小店, aiguangshop=爱逛买手店, wangxiaodian=旺小店, beauty=美业。
        page: 当前页码。可选。默认=1。
        status: 发布状态。可选。枚举：0=全部, 1=未发布, 2=已发布, 3=历史版本。默认=0（全部）。
    """
    url = f"{BASE_URL}/v3/api/cert-manage/pages"
    params = {
        "biz": biz,
        "page": page,
        "status": status,
        "t": int(time.time() * 1000),  # 防缓存时间戳（毫秒）
    }
    return client.get(url, params)
