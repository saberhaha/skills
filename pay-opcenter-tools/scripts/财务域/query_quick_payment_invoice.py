"""
快捷回款-发票 — 快捷回款-发票（商家发票查询）
来源：schemas/财务域/v3_快捷回款-发票.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "mchId": {
        "type": "string",
        "required": True,
        "description": "商户号（必填）"
    },
    "queryMonth": {
        "type": "string",
        "format": "YYYY-MM",
        "required": True,
        "default": "上个月（now-1M，格式 YYYY-MM）",
        "description": "发票月份（格式：YYYY-MM，默认为上个月）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "渠道", "dataIndex": "creditProd"},
    {"title": "月度发票总额", "dataIndex": "receiptAmt"},
]


def execute(
    mch_id: str,
    query_month: Optional[str] = None,
) -> dict:
    """查询商家发票信息（快捷回款-发票）。
    用户只需提供商户号，发票月份默认为上个月。

    Args:
        mch_id: 商户号。必填。
        query_month: 发票月份。可选。格式：YYYY-MM，如 "2026-02"。默认=上个月。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.fin.quick.queryreceiptinfo"

    now = datetime.now()
    # 默认为上个月（格式 YYYY-MM）
    if query_month is None:
        first_of_this_month = now.replace(day=1)
        last_month = first_of_this_month - timedelta(days=1)
        query_month = last_month.strftime("%Y-%m")

    payload = {
        "mchId": mch_id,
        "queryMonth": query_month,
    }

    return client.post(url, payload)
