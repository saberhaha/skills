"""
账户管理费查询
来源：schemas/账务域/v1_账户管理费.json
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "merchantNo": {"type": "string", "required": True, "description": "店铺商户号"},
    "accountType": {
        "type": "number", "required": True, "default": 10,
        "description": "账户类型（固定值10=静默账户管理费枚举值）"
    },
    "inoutLogType": {
        "type": "number", "required": True, "default": 161,
        "description": "收支记录类型（固定值161）"
    },
    "pageNo": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = {
    "list": [
        {"title": "流水号", "dataIndex": "waterNo"},
        {"title": "账户管理费实收金额", "dataIndex": "amount"},
        {"title": "账户管理费标准额度", "dataIndex": "balance"},
        {"title": "收费时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "费用明细", "dataIndex": "remark"}
    ],
    "sum": [
        {"title": "账户管理费累计收取", "dataIndex": "totalFee"}
    ],
    "merchantInfo": [
        {"title": "店铺名称", "dataIndex": "merchantShortName"}
    ]
}


def execute(
    merchant_no: str,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """账户管理费查询（v1）
    查询商户的账户管理费明细列表、累计收取金额及店铺信息。
    accountType 固定为 10，inoutLogType 固定为 161。

    Args:
        merchant_no: 店铺商户号。必填。
        page_no: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    # 固定业务参数（来源 Schema 默认值）
    account_type = 10
    inout_log_type = 161

    # 接口1：管理费明细列表
    list_url = f"{BASE_URL}/dispatcher/pay.acctrans.getPageList"
    list_payload = {
        "merchantNo": merchant_no,
        "accountType": account_type,
        "inoutLogType": inout_log_type,
        "pageNo": page_no,
        "pageSize": page_size
    }
    list_res = client.post(list_url, list_payload)

    # 接口2：管理费累计收取查询
    sum_url = f"{BASE_URL}/dispatcher/pay.acctrans.inoutlog.sum"
    sum_payload = {
        "merchantNo": merchant_no,
        "accountType": account_type,
        "inoutLogType": inout_log_type
    }
    sum_res = client.post(sum_url, sum_payload)

    # 接口3：店铺信息查询（sentData 需要包装成 singleParam）
    merchant_url = f"{BASE_URL}/dispatcher/pay.customer.getFullMerchantInfo"
    merchant_res = client.post(merchant_url, {"singleParam": merchant_no})

    return {
        "merchantInfo": merchant_res,
        "totalFee": sum_res,
        "detailList": list_res
    }
