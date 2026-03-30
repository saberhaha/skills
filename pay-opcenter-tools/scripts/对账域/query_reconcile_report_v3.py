"""
对账报表 — v3 渠道对账汇总报表查询
来源：schemas/对账域/v3_对账报表.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    },
    "startBizDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now-3M",
        "description": "交易开始日期（格式：YYYY-MM-DD）"
    },
    "endBizDate": {
        "type": "string",
        "format": "YYYY-MM-DD",
        "required": False,
        "default": "now",
        "description": "交易结束日期（格式：YYYY-MM-DD）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "交易日期", "dataIndex": "bizDate"},
    {"title": "间联收单笔数", "dataIndex": "indirectCount"},
    {"title": "间联交易金额", "dataIndex": "indirectPayAmount"},
    {"title": "间联退款金额", "dataIndex": "indirectRefundAmount"},
    {"title": "间联手续费", "dataIndex": "indirectTxnFeeAmount"},
    {"title": "直连收单笔数", "dataIndex": "directCount"},
    {"title": "直连交易金额", "dataIndex": "directPayAmount"},
    {"title": "直连退款金额", "dataIndex": "directRefundAmount"},
    {"title": "直连转账金额", "dataIndex": "directTransferAmount"},
    {"title": "直连手续费", "dataIndex": "directTxnFeeAmount"},
    {"title": "网联提现笔数", "dataIndex": "netUnionWithDrawCount"},
    {"title": "网联提现金额", "dataIndex": "netUnionWithDrawAmount"},
    {"title": "银联提现笔数", "dataIndex": "unionWithDrawCount"},
    {"title": "银联提现金额", "dataIndex": "unionWithDrawAmount"},
    {"title": "微信提现笔数", "dataIndex": "weChatWithDrawCount"},
    {"title": "微信提现金额", "dataIndex": "weChatWithDrawAmount"},
    {"title": "平安提现笔数", "dataIndex": "pabWithDrawCount"},
    {"title": "平安提现金额", "dataIndex": "pabWithDrawAmount"},
    {"title": "易宝提现笔数", "dataIndex": "yeePayWithDrawCount"},
    {"title": "易宝提现金额", "dataIndex": "yeePayWithDrawAmount"},
    {"title": "间连收单笔数占比", "dataIndex": "indirectCountPercent"},
    {"title": "间连收单金额占比", "dataIndex": "indirectAmountPercent"},
    {"title": "直连收单笔数占比", "dataIndex": "directCountPercent"},
    {"title": "直连收单金额占比", "dataIndex": "directAmountPercent"},
    {"title": "汇总-收单笔数", "dataIndex": "acquireCount"},
    {"title": "汇总-收单交易额", "dataIndex": "acquirePayAmount"},
    {"title": "汇总-提现总额", "dataIndex": "withDrawAmount"},
]


def execute(
    page: int = 1,
    page_size: int = 10,
    start_biz_date: Optional[str] = None,
    end_biz_date: Optional[str] = None,
) -> dict:
    """对账报表（v3）- 查询渠道对账汇总报表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        start_biz_date: 交易开始日期，格式 "YYYY-MM-DD"（如 "2026-01-01"）。默认近 3 个月。
        end_biz_date: 交易结束日期，格式 "YYYY-MM-DD"。默认今天。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/check.channel.api.ReportApiService.queryCheckReport"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    payload = {
        "page": page,
        "pageSize": page_size,
        "startBizDate": start_biz_date if start_biz_date else three_months_ago.strftime("%Y-%m-%d"),
        "endBizDate": end_biz_date if end_biz_date else now.strftime("%Y-%m-%d"),
    }

    return client.post(url, payload)
