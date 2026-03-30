"""
快速提额 - 人工提额
来源：schemas/资金域/v3_快速提额.json
页面包含两个Tab，此为Tab2：人工提额记录查询（支持分页）
"""
import sys
import os
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "kdtId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺ID"
    },
    "kdtName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺名称"
    },
    "state": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "": "全部",
            "WAIT_ACT": "未生效",
            "VALID": "生效",
            "INVALID": "已失效",
            "USED": "已使用"
        },
        "description": "提额状态（空=全部）"
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

# 数据展示列
DISPLAY_COLUMNS = [
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "店铺名称", "dataIndex": "kdtName"},
    {"title": "当前额度（元）", "dataIndex": "originQuota", "note": "format(money)"},
    {"title": "当前保证金（元）", "dataIndex": "originDeposit", "note": "format(money)"},
    {"title": "提升后额度（元）", "dataIndex": "afterQuota", "note": "format(money)"},
    {"title": "提升后保证金（元）", "dataIndex": "afterDeposit", "note": "format(money)"},
    {"title": "提额状态", "dataIndex": "state", "note": "枚举: WAIT_ACT=未生效, VALID=生效, INVALID=已失效, USED=已使用"},
    {"title": "操作人", "dataIndex": "operatorName"},
    {"title": "操作时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"}
]


def execute(
    kdt_id: Optional[str] = None,
    kdt_name: Optional[str] = None,
    state: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """查询人工提额记录列表

    Args:
        kdt_id: 店铺ID。可选
        kdt_name: 店铺名称。可选
        state: 提额状态。可选。枚举：空=全部, WAIT_ACT=未生效, VALID=生效, INVALID=已失效, USED=已使用
        page: 页码。默认：1
        page_size: 每页条数。默认：10

    Returns:
        返回人工提额记录列表，包含店铺信息、额度变化、状态、操作人等
    """
    # v3版本API路径
    url = f"{BASE_URL}/v3/api/dispatch/invoke/youzan.pay.fin.OpQueryService.pageQueryIncreaseList"

    # 构造payload，过滤空值
    payload = {
        "page": page,
        "pageSize": page_size
    }

    if kdt_id:
        payload["kdtId"] = kdt_id
    if kdt_name:
        payload["kdtName"] = kdt_name
    if state is not None:
        payload["state"] = state

    # 过滤空字符串和None值
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}

    return client.post(url, payload)


def query_quota(kdt_id: str) -> Dict[str, Any]:
    """查询单店铺额度（辅助API）

    Args:
        kdt_id: 店铺ID

    Returns:
        返回该店铺的当前额度信息
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/com.youzan.pay.OpQueryService.quotaQuery"
    payload = {"kdtId": kdt_id}
    return client.post(url, payload)
