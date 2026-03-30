"""
业务规则绑定查询 — 查询业务规则绑定列表
来源：schemas/计费规则域/v3_业务规则绑定查询.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "bindKey": {
        "type": "enum", "required": False,
        "enum_values": {"kdtId": "店铺kdtid", "mchId": "商户号"},
        "description": "绑定key类型，有 bindContent 时必填",
    },
    "bindContent": {"type": "string", "required": False, "description": "绑定内容值"},
    "factorQueryList": {"type": "array", "required": False, "description": "因子查询列表"},
    "namespace": {"type": "string", "required": True, "default": "yz-settle-center", "description": "命名空间，固定值"},
}

DISPLAY_COLUMNS = [
    {"title": "结算产品码", "dataIndex": "product"},
    {"title": "结算产品名称", "dataIndex": "productName"},
    {"title": "店铺kdtid", "dataIndex": "kdtId"},
    {"title": "商户号", "dataIndex": "bindContent"},
    {"title": "创建人", "dataIndex": "creator"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "模板类型", "dataIndex": "packageType"},
    {"title": "模板名称", "dataIndex": "ruleConfigDesc"},
    {"title": "绑定状态", "dataIndex": "bindState", "enum_values": {"INVALID": "失效", "VALID": "生效", "WAITING": "待生效", "CREATE": "未生效"}},
]


def execute(
    bind_key: Optional[Literal["kdtId", "mchId"]] = None,
    bind_content: Optional[str] = None,
    factor_key: Optional[str] = None,
    factor_content: Optional[str] = None,
    namespace: str = "yz-settle-center",
) -> dict:
    """查询业务规则绑定列表

    Args:
        bind_key: 绑定key类型。枚举：kdtId=店铺kdtid, mchId=商户号。有 bind_content 时必填。
        bind_content: 绑定内容值。可选。
        factor_key: 因子key。可选。
        factor_content: 因子内容值。可选。
        namespace: 命名空间，固定值。默认=yz-settle-center。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/rule.config.binder.list"

    payload = {
        "namespace": namespace,
    }

    if bind_key is not None:
        payload["bindKey"] = bind_key
    if bind_content is not None:
        payload["bindContent"] = bind_content

    if factor_key is not None:
        factor_item = {"factorKey": factor_key}
        if factor_content is not None:
            factor_item["content"] = factor_content
        payload["factorQueryList"] = [factor_item]

    return client.post(url, payload)
