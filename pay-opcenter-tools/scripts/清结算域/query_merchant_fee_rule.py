"""
商户费率规则
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Literal
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "idType": {
        "type": "enum",
        "required": False,
        "default": "kdtId",
        "enum_values": {"kdtId": "店铺kdtid", "mchId": "商户号"},
        "description": "标识类型（默认kdtId）"
    },
    "idValue": {
        "type": "string",
        "required": False,
        "description": "标识值"
    },
    "feeProductCode": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "计费产品编码"
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

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "计费产品编码", "dataIndex": "feeProductCode"},
    {"title": "计费产品名称", "dataIndex": "feeProductName"},
    {"title": "店铺kdtid", "dataIndex": "kdtId"},
    {"title": "商户号", "dataIndex": "mchId"},
    {"title": "创建人", "dataIndex": "creator"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "模板类型", "dataIndex": "packageType", "enum_values": {"COMMON": "通用", "CUSTOM": "个性化"}},
    {"title": "模板名称", "dataIndex": "packName"},
    {"title": "规则状态", "dataIndex": "ruleState", "enum_values": {"INVALID": "失效", "VALID": "已生效", "WAITING": "待生效"}}
]


def execute(
    id_type: Literal["kdtId", "mchId"] = "kdtId",
    id_value: Optional[str] = None,
    fee_product_code: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """商户费率规则查询
    查询商户费率规则列表，支持按店铺kdtid或商户号筛选。

    Args:
        id_type: 标识类型。枚举：kdtId=店铺kdtid, mchId=商户号。默认=kdtId。
        id_value: 标识值。可选。
        fee_product_code: 计费产品编码。空=全部。默认=""。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/feecenter.ops.feerule.list"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "page": page,
        "pageSize": page_size,
        "feeProductCode": fee_product_code,
    }

    # 动态 key 映射：idType 作为 key 映射到 idValue
    if id_value is not None:
        payload[id_type] = id_value

    return client.post(url, payload)
