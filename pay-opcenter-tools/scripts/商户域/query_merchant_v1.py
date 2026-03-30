"""
商户信息列表查询 — 商户信息列表查询
来源：schemas/商户域/v1_商户管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "mchName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "商户名称"
    },
    "mchId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "商户号（合规运营平台必填）"
    },
    "mchSource": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"": "全部", "0": "内部", "1": "外部"},
        "description": "商户来源（空=全部，传值时转为Number类型）"
    },
    "status": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"": "全部", "1": "正常", "2": "关停", "3": "注销"},
        "description": "商户状态（空=全部，传值时转为Number类型）"
    },
    "mchType": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"": "全部", "0": "服务商", "1": "普通商户", "2": "特约商户", "3": "一般商户"},
        "description": "商户类型（空=全部，传值时转为Number类型）"
    },
    "partnerName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "所属服务商"
    },
    "customerId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "客户号"
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

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "商户名称", "dataIndex": "mchName"},
    {"title": "商户号", "dataIndex": "mchId"},
    {"title": "客户号", "dataIndex": "customerId"},
    {"title": "商户类型", "dataIndex": "mchType"},
    {"title": "所属服务商", "dataIndex": "partnerName"},
    {"title": "服务商商户号", "dataIndex": "partnerId"},
    {"title": "商户状态", "dataIndex": "status"},
    {"title": "商户来源", "dataIndex": "mchSource"},
    {"title": "注册时间", "dataIndex": "createdTime"},
    {"title": "开户状态", "dataIndex": "mchStatus"},
    {"title": "经营类目", "dataIndex": "business"},
    {"title": "联系人/联系邮箱/联系电话", "dataIndex": "contractInfo"},
    {"title": "商户地址", "dataIndex": "address"},
]


def execute(
    mch_name: Optional[str] = None,
    mch_id: Optional[str] = None,
    mch_source: Optional[Literal["", "0", "1"]] = None,
    status: Optional[Literal["", "1", "2", "3"]] = None,
    mch_type: Optional[Literal["", "0", "1", "2", "3"]] = None,
    partner_name: Optional[str] = None,
    customer_id: Optional[str] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """商户信息列表查询（v1）
    查询商户信息列表，支持多条件筛选。

    Args:
        mch_name: 商户名称。可选。
        mch_id: 商户号。可选（合规运营平台必填）。
        mch_source: 商户来源。可选。枚举：''=全部, '0'=内部, '1'=外部。默认=全部。
        status: 商户状态。可选。枚举：''=全部, '1'=正常, '2'=关停, '3'=注销。默认=全部。
        mch_type: 商户类型。可选。枚举：''=全部, '0'=服务商, '1'=普通商户, '2'=特约商户, '3'=一般商户。默认=全部。
        partner_name: 所属服务商。可选。
        customer_id: 客户号。可选。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.merchant.info.search"

    payload: dict = {
        "currentPage": current_page,
        "size": size,
        "mchName": mch_name if mch_name is not None else "",
        "mchId": mch_id if mch_id is not None else "",
        "partnerName": partner_name if partner_name is not None else "",
        "customerId": customer_id if customer_id is not None else "",
    }

    # 枚举字段：空值时不传，非空时转为Number
    if mch_source is not None and mch_source != "":
        payload["mchSource"] = int(mch_source)
    if status is not None and status != "":
        payload["status"] = int(status)
    if mch_type is not None and mch_type != "":
        payload["mchType"] = int(mch_type)

    return client.post(url, payload)
