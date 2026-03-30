"""
商家计费规则 — 查询商家计费规则列表
来源：schemas/计费规则域/v2_商家计费规则.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "kdtId": {"type": "string", "required": False, "description": "店铺kdtID"},
    "kdtName": {"type": "string", "required": False, "description": "店铺名称"},
    "feeType": {"type": "string", "required": False, "description": "计费产品名称或代码"},
    "protocolNo": {"type": "string", "required": False, "description": "协议号"},
    "contractNo": {"type": "string", "required": False, "description": "合同号"},
    "ruleNo": {"type": "string", "required": False, "description": "算账规则码"},
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"},
}

DISPLAY_COLUMNS = [
    {"title": "算账规则码", "dataIndex": "ruleNo"},
    {"title": "计费产品代码", "dataIndex": "feeType"},
    {"title": "计费产品名称", "dataIndex": "feeName"},
    {"title": "店铺kdtID", "dataIndex": "kdtId"},
    {"title": "店铺名称", "dataIndex": "kdtName"},
    {"title": "算账规则", "dataIndex": "discount"},
    {"title": "创始人", "dataIndex": "creator"},
    {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "规则开启时间", "dataIndex": "effectTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "规则停用时间", "dataIndex": "expireTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "关联协议号", "dataIndex": "protocolNo"},
    {"title": "关联合同号", "dataIndex": "contractNo"},
    {"title": "规则状态", "dataIndex": "state"},
]


def execute(
    kdt_id: Optional[str] = None,
    kdt_name: Optional[str] = None,
    fee_type: Optional[str] = None,
    protocol_no: Optional[str] = None,
    contract_no: Optional[str] = None,
    rule_no: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询商家计费规则列表

    Args:
        kdt_id: 店铺kdtID。可选。
        kdt_name: 店铺名称。可选。
        fee_type: 计费产品名称或代码。可选。
        protocol_no: 协议号。可选。
        contract_no: 合同号。可选。
        rule_no: 算账规则码。可选。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/finance.fee.rule.kdt.query.list"

    payload = {
        "page": page,
        "pageSize": page_size,
    }

    if kdt_id is not None:
        payload["kdtId"] = kdt_id
    if kdt_name is not None:
        payload["kdtName"] = kdt_name
    if fee_type is not None:
        payload["feeType"] = fee_type
    if protocol_no is not None:
        payload["protocolNo"] = protocol_no
    if contract_no is not None:
        payload["contractNo"] = contract_no
    if rule_no is not None:
        payload["ruleNo"] = rule_no

    return client.post(url, payload)
