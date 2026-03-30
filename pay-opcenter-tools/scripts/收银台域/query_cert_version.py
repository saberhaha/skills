"""
页面证书版本 — 查询页面证书版本历史
来源：schemas/收银台域/v3_页面证书版本.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_页面证书版本.json）
PARAM_SCHEMA = {
    "pageId": {
        "type": "string",
        "required": True,
        "description": "页面标识（IPageData.pageId，从页面证书列表获取）"
    },
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
        "description": "业务线类型（从页面证书列表的sourceAppCode映射而来）"
    },
    "bizScene": {
        "type": "string",
        "required": False,
        "default": "default",
        "description": "业务场景，默认值为 \"default\""
    },
    "terminalType": {
        "type": "enum",
        "required": False,
        "default": "3",
        "enum_values": {"1": "PC", "3": "H5", "4": "小程序"},
        "description": "操作端类型，默认值为 \"3\"(H5)"
    },
    "productId": {
        "type": "string",
        "required": False,
        "default": "1",
        "description": "所属功能ID，默认为 \"1\"(入网认证)"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "pageSize": {"type": "number", "required": False, "default": 20, "description": "每页条数"},
}

# 数据展示列（来源：v3_页面证书版本.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "页面标题", "dataIndex": "pageName"},
    {"title": "页面标识", "dataIndex": "pageId"},
    {"title": "业务线", "dataIndex": "sourceAppCode", "format": "map via sourceAppMap"},
    {"title": "所属功能", "dataIndex": "productId", "format": "enum_render: 1→入网认证"},
    {"title": "发布状态", "dataIndex": "status", "format": "enum_render: 1→未发布; 2→已发布; 3→历史版本"},
    {"title": "业务场景", "dataIndex": "bizScene"},
    {"title": "操作端", "dataIndex": "terminalType", "format": "enum_render: 1→PC; 3→H5; 4→小程序"},
    {"title": "版本", "dataIndex": "version"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作人", "dataIndex": "opName"},
]


def execute(
    page_id: str,
    biz: Literal["wsc", "wxd", "aiguangshop", "wangxiaodian", "beauty"],
    biz_scene: str = "default",
    terminal_type: str = "3",
    product_id: str = "1",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """查询页面证书版本历史

    Args:
        page_id: 页面标识。必填。从页面证书列表（query_cert_manage_pages）中获取 pageId 字段。
        biz: 业务线类型。必填。枚举：wsc=微商城, wxd=微小店, aiguangshop=爱逛买手店, wangxiaodian=旺小店, beauty=美业。
        biz_scene: 业务场景。可选。默认="default"。
        terminal_type: 操作端类型。可选。枚举：1=PC, 3=H5, 4=小程序。默认="3"(H5)。
        product_id: 所属功能ID。可选。默认="1"(入网认证)。
        page: 当前页码。可选。默认=1。
        page_size: 每页条数。可选。默认=20。
    """
    url = f"{BASE_URL}/v3/api/cert-manage/page/version"
    params = {
        "pageId": page_id,
        "biz": biz,
        "bizScene": biz_scene,
        "terminalType": terminal_type,
        "productId": product_id,
        "page": page,
        "pageSize": page_size,
    }
    return client.get(url, params)
