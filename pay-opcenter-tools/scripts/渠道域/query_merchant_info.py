"""
商户信息配置 — 查询商户信息列表 (v1)
来源：schemas/渠道域/v1_商户信息配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v1_商户信息配置.json）
PARAM_SCHEMA = {
    "condition": {"type": "string", "required": False, "description": "终端序列号(posSn)"},
    "pageIndex": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

# 数据展示列（来源：v1_商户信息配置.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "通联商户号码", "dataIndex": "merchantNo"},
    {"title": "商户名称", "dataIndex": "merchantName"},
    {"title": "终端号", "dataIndex": "terminalNo"},
    {"title": "有赞商户号", "dataIndex": "youzanMerchantNo"},
    {"title": "终端序列号", "dataIndex": "terminalSerialNo"},
    {"title": "支付模式", "dataIndex": "payMode"},
    {"title": "渠道类型", "dataIndex": "modeType"},
    {"title": "状态", "dataIndex": "recordStatus"},
]


def execute(
    condition: Optional[str] = None,
    page_index: int = 1,
    page_size: int = 10,
) -> dict:
    """查询商户信息列表 (v1)
    用户只需提供终端序列号，其余参数自动使用页面默认值。

    Args:
        condition: 终端序列号(posSn)。可选。
        page_index: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/channel.merchantInfo.list"

    payload = {
        "pageIndex": page_index,
        "pageSize": page_size,
    }
    if condition is not None:
        payload["condition"] = condition

    return client.post(url, payload)
