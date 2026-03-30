"""
支付配置详情（进件配置查询） — 查询进件配置列表
来源：schemas/微信流程域/支付配置详情.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "userNo": {
        "type": "number",
        "required": False,
        "default": 0,
        "description": "商户号（无值时传0表示不限）"
    },
    "inst": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"UNIONPAY": "银联", "NETPAY": "网联"},
        "description": "机构标识（空字符串表示全部）"
    },
    "channel": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"WXPAY": "微信支付", "ALIPAY": "支付宝支付", "WX_AND_ALI": "微信和支付宝"},
        "description": "渠道标识（空字符串表示全部）"
    },
    "type": {
        "type": "enum",
        "required": False,
        "enum_values": {
            "0": "公众号自有支付",
            "1": "小程序自有",
            "2": "微信小程序代销",
            "3": "微信公众号代销",
            "5": "支付宝公众号代销",
            "6": "line支付",
            "7": "支付宝小程序代销",
            "8": "支付宝（js）代销",
            "9": "支付宝通用备份代销",
            "10": "微信信用分代销",
            "11": "微信收付通支付账号",
            "12": "平安银行资金账号",
            "13": "平安付",
            "14": "云直通-江苏银行",
        },
        "description": "业务类型"
    },
    "appId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "appId"
    },
    "subMchId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "子商户号"
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
    {"title": "类型", "dataIndex": "type", "enum_values": {
        "0": "公众号自有支付", "1": "小程序自有", "2": "微信小程序代销",
        "3": "微信公众号代销", "5": "支付宝公众号代销", "6": "line支付",
        "7": "支付宝小程序代销", "8": "支付宝（js）", "9": "支付宝通用备份代销",
        "10": "微信信用分代销", "11": "微信收付通支付账号", "12": "平安银行资金账号",
        "13": "平安付", "14": "云直通-江苏银行",
    }},
    {"title": "机构", "dataIndex": "inst", "enum_values": {"UNIONPAY": "银联", "NETPAY": "网联"}},
    {"title": "渠道", "dataIndex": "channel", "enum_values": {"WXPAY": "微信支付", "ALIPAY": "支付宝"}},
    {"title": "场景", "dataIndex": "bizSceneType", "enum_values": {"ONLINE": "线上", "OFFLINE": "线下"}},
    {"title": "商户号", "dataIndex": "userNo"},
    {"title": "appId", "dataIndex": "appId"},
    {"title": "子商户号", "dataIndex": "subMchId"},
    {"title": "settleId", "dataIndex": "settleId"},
    {"title": "settleIdType", "dataIndex": "highFee", "enum_values": {"1": "high", "2": "low"}},
    # status: 页面中 status > 0 表示「被封/禁用」，展示「启用」按钮；status <= 0 表示「正常使用」，展示「禁用」按钮
    {"title": "状态", "dataIndex": "status", "enum_values": {"0": "正常使用（可禁用）", ">0": "已封禁（可启用）"}},
    {"title": "超额收入", "dataIndex": "excessIncome"},
    {"title": "其他(ext)", "dataIndex": "ext"},  # 注意：后端字段名为 ext，非 desc
    {"title": "微信支付开户意愿状态确认", "dataIndex": "isRealName", "enum_values": {"1": "已确认", "0": "未确认"}},
    {"title": "主体名称", "dataIndex": "name"},
]


def execute(
    user_no: int = 0,
    inst: Optional[Literal["UNIONPAY", "NETPAY"]] = None,
    channel: Optional[Literal["WXPAY", "ALIPAY", "WX_AND_ALI"]] = None,
    type_: Optional[Literal[
        "0", "1", "2", "3", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"
    ]] = None,
    app_id: Optional[str] = None,
    sub_mch_id: Optional[str] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """支付配置详情 — 进件配置查询（v1）

    Args:
        user_no: 商户号。无值时传0表示不限。默认=0。
        inst: 机构标识。可选。枚举：UNIONPAY=银联, NETPAY=网联。空字符串表示全部。
        channel: 渠道标识。可选。枚举：WXPAY=微信支付, ALIPAY=支付宝支付, WX_AND_ALI=微信和支付宝。空字符串表示全部。
        type_: 业务类型。可选。枚举：0=公众号自有支付, 1=小程序自有, 2=微信小程序代销, 3=微信公众号代销, 5=支付宝公众号代销, 6=line支付, 7=支付宝小程序代销, 8=支付宝（js）代销, 9=支付宝通用备份代销, 10=微信信用分代销, 11=微信收付通支付账号, 12=平安银行资金账号, 13=平安付, 14=云直通-江苏银行。
        app_id: appId。可选。
        sub_mch_id: 子商户号。可选。
        current_page: 当前页码。默认=1。
        size: 每页条数。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/customercore.process.queryPageConfigInfoByParam"

    payload: dict = {
        "userNo": user_no,
        "inst": inst if inst is not None else "",
        "channel": channel if channel is not None else "",
        "appId": app_id if app_id is not None else "",
        "subMchId": sub_mch_id if sub_mch_id is not None else "",
        "currentPage": current_page,
        "size": size,
    }

    if type_ is not None:
        payload["type"] = type_

    return client.post(url, payload)
