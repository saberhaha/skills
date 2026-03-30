"""
计费产品管理
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
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
    "feeProductCode": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "计费产品编码（空=全部）"
    },
    "industryCode": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "行业编码（空=全部）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "计费产品编码", "dataIndex": "feeProductCode"},
    {"title": "计费产品名称", "dataIndex": "feeProductName"},
    {"title": "是否有协议", "dataIndex": "hasProtocol"},
    {"title": "业务方", "dataIndex": "partnerName"},
    {"title": "行业", "dataIndex": "industryName"},
    {"title": "通用规则", "dataIndex": "commonRule"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "状态", "dataIndex": "state"}
]


def execute(
    page: int = 1,
    page_size: int = 10,
    fee_product_code: str = "",
    industry_code: str = "",
) -> dict:
    """计费产品管理查询
    查询计费产品列表，支持按计费产品编码和行业编码筛选。

    Args:
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        fee_product_code: 计费产品编码。空=全部。默认=""。
        industry_code: 行业编码。空=全部。默认=""。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.product.list"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "page": page,
        "pageSize": page_size,
        "feeProductCode": fee_product_code,
        "industryCode": industry_code,
    }

    return client.post(url, payload)


def query_factor_batch() -> dict:
    """计费因子批量查询（辅助接口）
    获取产品和行业分组的因子列表。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.factor.batch.query?groupKey=product&groupKey=industry"

    return client.get(url)
