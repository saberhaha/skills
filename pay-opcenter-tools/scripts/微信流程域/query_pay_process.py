"""
支付流程详情（进件状态查询） — 查询进件状态列表
来源：schemas/微信流程域/支付流程详情.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "userNo": {
        "type": "string",
        "required": False,
        "description": "商户号（与kdtId二选一，不可同时填写）"
    },
    "kdtId": {
        "type": "string",
        "required": False,
        "description": "店铺id（与userNo二选一，不可同时填写）"
    },
    "bizType": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "REG_WX_APPLET": "微信小程序代销",
            "WX_PUBLIC_ACCOUNT": "微信公众号代销",
            "ALIPAY_JSAPI_PROXY": "支付宝（公众号）",
            "REG_ALI_APPLET": "支付宝小程序代销",
            "ALIPAY_JS": "支付宝(js)"
        },
        "description": "进件类型"
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "当前页码"
    },
    "size": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
}

DISPLAY_COLUMNS = [
    {"title": "商户号", "dataIndex": "userNo"},
    {"title": "appId", "dataIndex": "appId"},
    {"title": "进件类型", "dataIndex": "bizType"},
    {"title": "状态", "dataIndex": "state"},
    {"title": "其他", "dataIndex": "desc", "note": "render函数实际渲染record.ext字段内容"},
    {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    user_no: Optional[str] = None,
    kdt_id: Optional[str] = None,
    biz_type: Optional[Literal[
        "REG_WX_APPLET",
        "WX_PUBLIC_ACCOUNT",
        "ALIPAY_JSAPI_PROXY",
        "REG_ALI_APPLET",
        "ALIPAY_JS",
    ]] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """支付流程详情 — 进件状态查询（v1）

    Args:
        user_no: 商户号。可选（与kdt_id二选一，不可同时填写）。
        kdt_id: 店铺id。可选（与user_no二选一，不可同时填写）。
        biz_type: 进件类型。可选。枚举：REG_WX_APPLET=微信小程序代销, WX_PUBLIC_ACCOUNT=微信公众号代销, ALIPAY_JSAPI_PROXY=支付宝（公众号）, REG_ALI_APPLET=支付宝小程序代销, ALIPAY_JS=支付宝(js)。
        current_page: 当前页码。默认=1。
        size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.customer.process.queryRegProcess"

    payload: dict = {
        "currentPage": current_page,
        "size": size,
    }

    if user_no is not None:
        payload["userNo"] = user_no
    if kdt_id is not None:
        payload["kdtId"] = kdt_id
    if biz_type is not None:
        payload["bizType"] = biz_type

    return client.post(url, payload)
