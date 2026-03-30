"""
外部账户查询（资金账户查询）(v2)
来源：schemas/账户查询域/v2_外部账户查询.json
"""
import sys
import os
from typing import Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "idType": {
        "type": "enum", "required": True, "default": "userNo",
        "enum_values": {"kdtId": "店铺KdtId", "userNo": "商户号/会员号"},
        "description": "查询类型"
    },
    "queryId": {
        "type": "string", "required": True,
        "description": "查询ID值（商户号/会员号/kdtId，纯数字，8-10位）"
    },
}

DISPLAY_COLUMNS = {
    "payment": [
        {"title": "账户类型", "dataIndex": "acctTypeName"},
        {"title": "资金账号", "dataIndex": "acctNo"},
        {"title": "总余额(元)", "dataIndex": "balance"},
        {"title": "不可用余额(元)", "dataIndex": "freeze"},
        {"title": "可用余额(元)", "dataIndex": "available"},
    ],
    "microaccount": [
        {"title": "账户类型", "dataIndex": "acctTypeName"},
        {"title": "资金账号", "dataIndex": "cardNo"},
        {"title": "本金（元）", "dataIndex": "principalDenomination"},
        {"title": "赠送金（元）", "dataIndex": "bonusDenomination"},
        {"title": "总余额（元）", "dataIndex": "denomination"},
    ],
}


def execute(
    query_id: str,
    id_type: Literal["kdtId", "userNo"] = "userNo",
) -> dict:
    """外部账户查询（资金账户查询）(v2)
    根据商户号/会员号或店铺KdtId查询支付账户信息和微账户信息。

    Args:
        query_id: 查询ID值（商户号/会员号/kdtId，纯数字，8-10位）。必填。
        id_type: 查询类型。枚举：'kdtId'=店铺KdtId, 'userNo'=商户号/会员号。默认 'userNo'。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.account.getAllAccountNotMerge"

    # 接口使用singleParam包装参数，直接传递query_id
    payload = {"singleParam": query_id}

    return client.post(url, payload)
