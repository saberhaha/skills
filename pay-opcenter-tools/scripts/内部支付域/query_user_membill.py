"""
内部支付工具-用户支付 — 查询用户支付记录
来源：schemas/内部支付域/v3_内部支付工具-用户支付.json
版本：v3
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
    "memId": {"type": "string", "required": False, "description": "会员号（可从URL参数memId获取）"},
    "bizNo": {"type": "string", "required": False, "description": "业务单号"},
    "bizType": {
        "type": "enum",
        "required": False,
        "default": "ALL",
        "description": "业务类型（传空字符串表示查询全部，前端选ALL时后端实际传空）",
        "enum_values": {
            "ALL": "全部",
            "PAY": "支付",
            "WITHDRAW": "提现",
            "RECHARGE": "充值",
            "SHARE_PROFIT": "分润",
            "REFUND": "退款",
            "BOUNCE": "退票"
        }
    },
    "bizStartTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "now-29d_start",
        "description": "交易开始时间（毫秒时间戳，合规平台默认近1天）"
    },
    "bizEndTime": {
        "type": "number",
        "format": "timestamp_ms",
        "required": False,
        "default": "now_end",
        "description": "交易结束时间（毫秒时间戳）"
    },
    "currentPage": {"type": "number", "required": False, "default": 1, "description": "当前页码"},
    "size": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "会员号", "dataIndex": "memId"},
    {"title": "业务类型", "dataIndex": "bizType"},
    {"title": "支付方式", "dataIndex": "payTool"},
    {"title": "业务状态", "dataIndex": "status"},
    {"title": "交易时间", "dataIndex": "tradeTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "交易金额", "dataIndex": "tradeAmount"},
    {"title": "支付订单号", "dataIndex": "payOrderNo"},
    {"title": "外部订单号", "dataIndex": "outBizNo"},
    {"title": "退款单号", "dataIndex": "refundNo"},
    {"title": "退款完成时间", "dataIndex": "refundFinishTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "渠道订单号", "dataIndex": "channelOrderNo"}
]


def execute(
    mem_id: Optional[str] = None,
    biz_no: Optional[str] = None,
    biz_type: Optional[Literal["ALL", "PAY", "WITHDRAW", "RECHARGE", "SHARE_PROFIT", "REFUND", "BOUNCE"]] = "ALL",
    biz_start_time: Optional[int] = None,
    biz_end_time: Optional[int] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """查询用户支付记录

    查询指定会员的支付、提现、充值、分润、退款、退票等业务记录。
    用户只需提供会员号或业务单号，时间等参数自动使用页面默认值。

    Args:
        mem_id: 会员号。可选。
        biz_no: 业务单号。可选。
        biz_type: 业务类型。可选。枚举：ALL=全部, PAY=支付, WITHDRAW=提现, RECHARGE=充值, SHARE_PROFIT=分润, REFUND=退款, BOUNCE=退票。默认=ALL。
        biz_start_time: 交易开始时间（毫秒时间戳）。可选。默认=近29天。
        biz_end_time: 交易结束时间（毫秒时间戳）。可选。默认=当前时间。
        current_page: 当前页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    # v3 版本使用 /v3/api/dispatch/invoke/ 前缀
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.user.membill.query"

    now = datetime.now()
    twenty_nine_days_ago = now - timedelta(days=29)

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "currentPage": current_page,
        "size": size,
        # bizType: 前端选ALL时后端实际传空
        "bizType": "" if biz_type == "ALL" else biz_type,
        # bizStartTime/bizEndTime 格式：timestamp_ms（毫秒时间戳）
        "bizStartTime": biz_start_time if biz_start_time is not None else int(twenty_nine_days_ago.timestamp() * 1000),
        "bizEndTime": biz_end_time if biz_end_time is not None else int(now.timestamp() * 1000),
    }

    # 添加可选参数（过滤空值）
    if mem_id:
        payload["memId"] = mem_id
    if biz_no:
        payload["bizNo"] = biz_no

    return client.post(url, payload)
