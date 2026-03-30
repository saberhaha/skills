"""
收银台支付工具列表查询(v3) — 收银台支付工具列表查询(v3)
来源：schemas/商户域/v3_收银台支付工具列表.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# v3版本参数包装在 singleParam 对象中
PARAM_SCHEMA = {
    "singleParam.partnerId": {
        "type": "string",
        "required": True,
        "description": "合作商商户号（必填）"
    },
    "singleParam.userNo": {
        "type": "string",
        "required": True,
        "description": "子商户ID（必填）"
    },
    "singleParam.buyerUserNo": {
        "type": "string",
        "required": False,
        "default": "0",
        "description": "买家商户号（可选，默认'0'）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
# 无分页
DISPLAY_COLUMNS = [
    {"title": "序号", "dataIndex": "id"},
    {"title": "支付方式", "dataIndex": "payment"},
    {"title": "bizSubTypeCode", "dataIndex": "bizSubTypeCode"},
    {"title": "余额（分）", "dataIndex": "balance"},
]


def execute(
    partner_id: str,
    user_no: str,
    buyer_user_no: Optional[str] = "0",
) -> dict:
    """收银台支付工具列表查询（v3）
    查询指定商户的收银台支付工具列表及余额（单位：分）。
    v3版本参数包装在singleParam对象中，与v1相同后端接口。无分页，返回全量结果。

    Args:
        partner_id: 合作商商户号（必填）。
        user_no: 子商户ID（必填）。
        buyer_user_no: 买家商户号。可选。默认='0'。
    """
    url = f"{BASE_URL}/dispatcher/pay.payToolConfig.list/"

    payload = {
        "singleParam": {
            "partnerId": partner_id,
            "userNo": user_no,
            "buyerUserNo": buyer_user_no if buyer_user_no is not None else "0",
        }
    }

    return client.post(url, payload)
