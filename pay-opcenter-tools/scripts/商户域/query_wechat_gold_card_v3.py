"""
微信点金计划分页查询 — 微信点金计划分页查询
来源：schemas/商户域/v3_微信金卡查询.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# inst=ALL 或 channel=ALL 时删除该字段不传给后端
PARAM_SCHEMA = {
    "userNo": {
        "type": "string",
        "required": False,
        "description": "商户号"
    },
    "subMchId": {
        "type": "string",
        "required": False,
        "description": "子商户号"
    },
    "inst": {
        "type": "enum",
        "required": False,
        "default": "ALL",
        "enum_values": {"ALL": "全部", "UNIONPAY": "银联", "NETPAY": "网联"},
        "description": "机构标识（ALL时不传此字段）"
    },
    "channel": {
        "type": "enum",
        "required": False,
        "default": "ALL",
        "enum_values": {"ALL": "全部", "WXPAY": "微信", "ALIPAY": "支付宝"},
        "description": "渠道标识（ALL时不传此字段）"
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
    {"title": "类型", "dataIndex": "type"},                  # enum: 0=公众号自有支付,...
    {"title": "机构", "dataIndex": "inst"},                  # UNIONPAY=银联, NETPAY=网联
    {"title": "渠道", "dataIndex": "channel"},               # WXPAY=微信, ALIPAY=支付宝
    {"title": "场景", "dataIndex": "bizSceneType"},          # ONLINE=线上, 其他=线下
    {"title": "子商户号", "dataIndex": "subMchId"},
    {"title": "商户号", "dataIndex": "userNo"},
    {"title": "点金计划", "dataIndex": "goldPlanStatus"},    # enum: 0=关闭,1=开启,2=申请中,3=发生错误
    {"title": "商家小票", "dataIndex": "customerPageStatus"},# enum: 0=关闭,1=开启,2=申请中,3=发生错误
    {"title": "广告展示", "dataIndex": "advertisementStatus"},# enum: 0=关闭,1=开启,2=申请中,3=发生错误
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "timestamp_ms"},
    {"title": "最近操作人", "dataIndex": "opUser"},
]


def execute(
    user_no: Optional[str] = None,
    sub_mch_id: Optional[str] = None,
    inst: Optional[Literal["ALL", "UNIONPAY", "NETPAY"]] = "ALL",
    channel: Optional[Literal["ALL", "WXPAY", "ALIPAY"]] = "ALL",
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """微信点金计划分页查询（v3）
    查询微信点金计划配置列表，支持按商户号、子商户号、机构、渠道筛选。

    Args:
        user_no: 商户号。可选。
        sub_mch_id: 子商户号。可选。
        inst: 机构标识。可选。枚举：'ALL'=全部, 'UNIONPAY'=银联, 'NETPAY'=网联。默认='ALL'（不传）。
        channel: 渠道标识。可选。枚举：'ALL'=全部, 'WXPAY'=微信, 'ALIPAY'=支付宝。默认='ALL'（不传）。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/gold.plan.page.query"

    payload: dict = {
        "currentPage": current_page,
        "size": size,
    }

    # 过滤空值
    if user_no:
        payload["userNo"] = user_no
    if sub_mch_id:
        payload["subMchId"] = sub_mch_id
    # inst/channel 为 ALL 时不传
    if inst and inst != "ALL":
        payload["inst"] = inst
    if channel and channel != "ALL":
        payload["channel"] = channel

    return client.post(url, payload)
