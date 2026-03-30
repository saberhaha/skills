"""
支付完整信息 — 根据多种查询类型获取完整支付信息
来源：schemas/内部支付域/v1_支付完整信息.json
版本：v1
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "queryType": {
        "type": "enum",
        "required": True,
        "description": "查询类型",
        "enum_values": {
            "receiveNo": "收单号",
            "orderNo": "定单号",
            "userNo": "商户号",
            "childUserNo": "子商户识别码",
            "kdtId": "kdtId"
        }
    },
    "queryValue": {"type": "string", "required": True, "description": "查询字段值"}
}

# 数据展示类型（来源：步骤 1.2 提取的前端展示）
# 展示多个数据卡片：支付信息、退款信息、交易信息、优惠详情等
DISPLAY_TYPE = "cards"


def execute(
    query_type: Literal["receiveNo", "orderNo", "userNo", "childUserNo", "kdtId"],
    query_value: str,
) -> dict:
    """查询支付完整信息

    根据指定的查询类型和值获取完整的支付信息。
    返回多个数据卡片，包括支付信息、退款信息、交易信息、优惠详情等。

    Args:
        query_type: 查询类型。必填。枚举：receiveNo=收单号, orderNo=定单号, userNo=商户号, childUserNo=子商户识别码, kdtId=kdtId。
        query_value: 查询字段值。必填。与 query_type 对应的值。
    """
    # v1 版本使用 /dispatcher/ 前缀
    # 注意：此功能为组合查询，可能需要调用多个接口
    # 根据 queryType 调用不同的查询接口
    url = f"{BASE_URL}/dispatcher/pay.center.payInfo.queryPayInfo"

    # 根据 queryType 映射到对应的请求参数
    param_mapping = {
        "receiveNo": "acquireNo",
        "orderNo": "outBizNo",
        "userNo": "mchId",
        "childUserNo": "customerId",
        "kdtId": "kdtId"
    }

    payload = {
        param_mapping.get(query_type, query_type): query_value
    }

    return client.post(url, payload)
