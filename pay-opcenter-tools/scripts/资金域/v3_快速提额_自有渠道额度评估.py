"""
快速提额 - 自有渠道额度评估
来源：schemas/资金域/v3_快速提额.json
页面包含两个Tab，此为Tab1：自有渠道额度评估（无入参，返回昨日额度不足Top30）
"""
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "note": "无入参，首屏自动加载"
}

# 数据展示列
DISPLAY_COLUMNS = [
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "店铺名称", "dataIndex": "kdtName"},
    {"title": "昨日不足金额", "dataIndex": "principal", "note": "format(money)"}
]


def execute() -> Dict[str, Any]:
    """查询自有渠道昨日额度不足Top30店铺

    无入参，返回自有渠道昨日额度不足的Top30店铺列表

    Returns:
        返回额度不足店铺列表，包含店铺ID、店铺名称、昨日不足金额
    """
    # v3版本API路径
    url = f"{BASE_URL}/v3/api/dispatch/invoke/com.youzan.pay.coOpQueryService.noEnoughQuery"

    # 无入参
    payload = {}

    return client.post(url, payload)
