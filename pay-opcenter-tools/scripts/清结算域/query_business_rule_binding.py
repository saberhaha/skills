"""
业务规则绑定查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Literal
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "bindKey": {
        "type": "enum",
        "required": False,
        "enum_values": {"kdtId": "店铺kdtid", "mchId": "商户号"},
        "description": "绑定键（有idValue时必填）"
    },
    "bindContent": {
        "type": "string",
        "required": False,
        "description": "绑定值"
    },
    "factorQueryList[0].factorKey": {
        "type": "string",
        "required": False,
        "default": "product",
        "description": "产品因子 key"
    },
    "factorQueryList[0].content": {
        "type": "string",
        "required": False,
        "description": "产品因子值"
    },
    "namespace": {
        "type": "string",
        "required": True,
        "default": "yz-settle-center",
        "description": "命名空间"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "结算产品码", "dataIndex": "product"},
    {"title": "结算产品名称", "dataIndex": "productName"},
    {"title": "店铺kdtid", "dataIndex": "kdtId"},
    {"title": "商户号", "dataIndex": "bindContent"},
    {"title": "创建人", "dataIndex": "creator"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "模板类型", "dataIndex": "packageType", "enum_values": {"COMMON": "通用", "CUSTOM": "个性化"}},
    {"title": "模板名称", "dataIndex": "ruleConfigDesc"},
    {"title": "绑定状态", "dataIndex": "ruleState", "enum_values": {"INVALID": "失效", "VALID": "生效", "WAITING": "待生效", "CREATE": "未生效"}}
]


def execute(
    bind_key: Optional[Literal["kdtId", "mchId"]] = None,
    bind_content: Optional[str] = None,
    factor_key: str = "product",
    factor_content: Optional[str] = None,
    namespace: str = "yz-settle-center",
) -> dict:
    """业务规则绑定查询
    查询业务规则绑定列表，支持按绑定键和产品因子筛选。

    Args:
        bind_key: 绑定键。枚举：kdtId=店铺kdtid, mchId=商户号。有 bind_content 时必填。
        bind_content: 绑定值。可选。
        factor_key: 产品因子 key。默认=product。
        factor_content: 产品因子值。可选。
        namespace: 命名空间。默认=yz-settle-center。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.binder.list"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "namespace": namespace,
        "factorQueryList": [
            {
                "factorKey": factor_key,
            }
        ],
    }

    # 可选参数填充
    if bind_key is not None:
        payload["bindKey"] = bind_key
    if bind_content is not None:
        payload["bindContent"] = bind_content
    if factor_content is not None:
        payload["factorQueryList"][0]["content"] = factor_content

    return client.post(url, payload)
