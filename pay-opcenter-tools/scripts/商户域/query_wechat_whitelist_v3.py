"""
微信白名单配置查询 — 微信白名单配置查询
来源：schemas/商户域/v3_微信白名单管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "bizId": {
        "type": "string",
        "required": True,
        "description": "业务ID（通常为kdtId）"
    },
    "bizCode": {
        "type": "string",
        "required": True,
        "default": "PAY_UCERT",
        "description": "业务码（默认=PAY_UCERT）"
    },
    "bizType": {
        "type": "string",
        "required": True,
        "description": "业务类型，如MERCHANT_NAME_MODIFY_WHITE"
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "size": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 数据展示：notification类型，查询结果通过Notify通知展示，无表格列
# UNRESOLVED: 无表格列定义，展示方式为 Notify.success/error 通知
DISPLAY_COLUMNS = []


def execute(
    biz_id: str,
    biz_type: str,
    biz_code: str = "PAY_UCERT",
    current_page: int = 1,
    size: int = 10,
    use_precise_query: bool = False,
) -> dict:
    """微信白名单配置查询（v3）
    查询微信白名单配置。支持通用查询和精确查询两种模式。
    查询结果通过Notify通知展示（非表格）。

    如需获取可用的bizCode/bizType选项，可先调用辅助接口 query_apollo_biz_config()。

    Args:
        biz_id: 业务ID（必填）。通常为kdtId。
        biz_type: 业务类型（必填）。如 'MERCHANT_NAME_MODIFY_WHITE'。
        biz_code: 业务码（必填）。默认='PAY_UCERT'。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
        use_precise_query: 是否使用精确查询。可选。默认=False（通用查询）。
    """
    if use_precise_query:
        url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.customercore.white.precise.query.config"
        params = {
            "bizId": biz_id,
            "bizCode": biz_code,
            "bizType": biz_type,
        }
    else:
        url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.customercore.white.query.config"
        params = {
            "bizId": biz_id,
            "bizCode": biz_code,
            "bizType": biz_type,
            "currentPage": current_page,
            "size": size,
        }

    return client.get(url, params)


def query_apollo_biz_config() -> dict:
    """获取Apollo业务配置列表（通用白名单业务选项）
    无入参，返回可用的bizCode/bizType选项列表，用于通用白名单子组件的业务场景下拉选项。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.customercore.white.extra.query.config"
    return client.get(url, {})
