"""
商户支付信息查询 — 根据多种条件查询商户支付信息列表
来源：schemas/内部支付域/v1_支付信息查询.json
版本：v1
页面路由：/page/payInfo
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "mchName": {"type": "string", "required": False, "description": "商户名称"},
    "mchId": {"type": "string", "required": False, "description": "商户号"},
    "customerId": {"type": "string", "required": False, "description": "客户号"},
    "outBizNo": {"type": "string", "required": False, "description": "商户订单号"},
    "outerId": {"type": "string", "required": False, "description": "支付订单号"},
    "acquireNo": {"type": "string", "required": False, "description": "收单号"},
    "channelNo": {"type": "string", "required": False, "description": "渠道订单号"},
    "payTool": {
        "type": "enum",
        "required": False,
        "description": "支付方式",
        "enum_values": {
            "WX_JS": "微信-公众号支付",
            "BANK_CARD": "银行卡支付",
            "WX_APPLET": "小程序支付"
        }
    },
    "bizAction": {
        "type": "enum",
        "required": False,
        "description": "业务类型",
        "enum_values": {
            "PAY": "支付",
            "REFUND": "退款",
            "RECHARGE": "充值"
        }
    },
    "payState": {
        "type": "enum",
        "required": False,
        "description": "业务状态",
        "enum_values": {
            "0": "已经创建（支付/充值）/ 申请中（退款）",
            "1": "成功（支付/充值）/ 申请失败（退款）",
            "2": "失败（支付/充值）/ 申请成功（退款）",
            "3": "退款处理中（退款专用）",
            "4": "处理中（支付/充值）/ 退款异常转人工处理（退款）",
            "5": "退款成功（退款专用）"
        }
    },
    "createStartTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "today_00:00:00",
        "description": "创建开始时间（毫秒时间戳）"
    },
    "createEndTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "today_23:59:59",
        "description": "创建结束时间（毫秒时间戳）"
    },
    "updateStartTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "now-30d_00:00:00",
        "description": "更新开始时间（毫秒时间戳）"
    },
    "updateEndTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "now_23:59:59",
        "description": "更新结束时间（毫秒时间戳）"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "商户名称", "dataIndex": "mchName"},
    {"title": "商户号", "dataIndex": "mchId"},
    {"title": "客户号", "dataIndex": "customerId"},
    {"title": "商户订单号", "dataIndex": "outBizNo"},
    {"title": "支付订单号", "dataIndex": "outerId"},
    {"title": "收单号", "dataIndex": "acquireNo"},
    {"title": "渠道订单号", "dataIndex": "channelNo"},
    {"title": "支付方式", "dataIndex": "payTool"},
    {"title": "业务类型", "dataIndex": "bizDescription"},
    {"title": "业务状态", "dataIndex": "payState"},
    {"title": "金额", "dataIndex": "payAmount"},
    {"title": "创建时间", "dataIndex": "createAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "更新时间", "dataIndex": "updateAt", "format": "YYYY-MM-DD HH:mm:ss"}
]


def execute(
    mch_name: Optional[str] = None,
    mch_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    out_biz_no: Optional[str] = None,
    outer_id: Optional[str] = None,
    acquire_no: Optional[str] = None,
    channel_no: Optional[str] = None,
    pay_tool: Optional[Literal["WX_JS", "BANK_CARD", "WX_APPLET"]] = None,
    biz_action: Optional[Literal["PAY", "REFUND", "RECHARGE"]] = None,
    pay_state: Optional[Literal["0", "1", "2", "3", "4", "5"]] = None,
    create_start_time: Optional[int] = None,
    create_end_time: Optional[int] = None,
    update_start_time: Optional[int] = None,
    update_end_time: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询商户支付信息列表

    根据多种条件查询商户支付信息（对应页面路由 /page/payInfo），支持按商户、订单号、状态等筛选。
    用户只需提供核心查询条件，时间等参数自动使用页面默认值。

    Args:
        mch_name: 商户名称。可选。
        mch_id: 商户号。可选。
        customer_id: 客户号。可选。
        out_biz_no: 商户订单号。可选。
        outer_id: 支付订单号。可选。
        acquire_no: 收单号。可选。
        channel_no: 渠道订单号。可选。
        pay_tool: 支付方式。可选。枚举：WX_JS=微信-公众号支付, BANK_CARD=银行卡支付, WX_APPLET=小程序支付。
        biz_action: 业务类型。可选。枚举：PAY=支付, REFUND=退款, RECHARGE=充值。
        pay_state: 业务状态。可选。枚举：0=已经创建/申请中, 1=成功/申请失败, 2=失败/申请成功, 3=退款处理中, 4=处理中/退款异常, 5=退款成功。
        create_start_time: 创建开始时间（毫秒时间戳）。可选。默认=今天00:00:00。
        create_end_time: 创建结束时间（毫秒时间戳）。可选。默认=今天23:59:59。
        update_start_time: 更新开始时间（毫秒时间戳）。可选。默认=近30天00:00:00。
        update_end_time: 更新结束时间（毫秒时间戳）。可选。默认=今天23:59:59。
        page: 当前页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    # v1 版本使用 /dispatcher/ 前缀
    url = f"{BASE_URL}/dispatcher/pay.center.payInfo.queryPayInfo"

    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
    thirty_days_ago_start = today_start - timedelta(days=30)

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "page": page,
        "pageSize": page_size,
        # createStartTime/createEndTime 格式：timestamp_ms（毫秒时间戳）
        "createStartTime": create_start_time if create_start_time is not None else int(today_start.timestamp() * 1000),
        "createEndTime": create_end_time if create_end_time is not None else int(today_end.timestamp() * 1000),
        # updateStartTime/updateEndTime 格式：timestamp_ms（毫秒时间戳）
        "updateStartTime": update_start_time if update_start_time is not None else int(thirty_days_ago_start.timestamp() * 1000),
        "updateEndTime": update_end_time if update_end_time is not None else int(today_end.timestamp() * 1000),
    }

    # 添加可选参数（过滤空值）
    if mch_name:
        payload["mchName"] = mch_name
    if mch_id:
        payload["mchId"] = mch_id
    if customer_id:
        payload["customerId"] = customer_id
    if out_biz_no:
        payload["outBizNo"] = out_biz_no
    if outer_id:
        payload["outerId"] = outer_id
    if acquire_no:
        payload["acquireNo"] = acquire_no
    if channel_no:
        payload["channelNo"] = channel_no
    if pay_tool:
        payload["payTool"] = pay_tool
    if biz_action:
        payload["bizAction"] = biz_action
    if pay_state:
        payload["payState"] = pay_state

    return client.post(url, payload)
