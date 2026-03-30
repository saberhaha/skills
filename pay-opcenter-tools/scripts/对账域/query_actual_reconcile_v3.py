"""
实收核对 — v3 渠道实收核对日汇总查询
来源：schemas/对账域/v3_实收核对.json
"""
import sys
import os
from typing import Optional, List
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "currentPage": {
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
    "instTypeList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "机构列表（0=全部）"
    },
    "bizLineTypeList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "业务线列表（0=全部）"
    },
    "feeTypeList": {
        "type": "array",
        "required": False,
        "default": ["0"],
        "description": "费用类型列表（0=全部）"
    },
    "startBizDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "default": "now-3M",
        "description": "交易开始时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
    "endBizDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "default": "now",
        "description": "交易结束时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "交易日期", "dataIndex": "bizDate"},
    {"title": "机构", "dataIndex": "instName"},
    {"title": "业务线", "dataIndex": "bizLineName"},
    {"title": "支付账户", "dataIndex": "acctNoName"},
    {"title": "费用类型", "dataIndex": "feeName"},
    {"title": "E交易笔数/金额", "dataIndex": "orderCount"},
    {"title": "费用笔数/金额", "dataIndex": "leftCount"},
    {"title": "账务笔数/金额", "dataIndex": "rightCount"},
    {"title": "对账成功笔数/金额", "dataIndex": "successCount"},
    {"title": "存疑笔数/金额", "dataIndex": "bufferCount"},
    {"title": "差错笔数/金额", "dataIndex": "diff"},
]


def execute(
    current_page: int = 1,
    page_size: int = 10,
    inst_type_list: Optional[List[str]] = None,
    biz_line_type_list: Optional[List[str]] = None,
    fee_type_list: Optional[List[str]] = None,
    start_biz_date: Optional[str] = None,
    end_biz_date: Optional[str] = None,
) -> dict:
    """实收核对（v3）- 查询渠道实收对账日汇总列表。
    用户只需提供核心筛选条件，其余参数自动使用页面默认值。

    Args:
        current_page: 页码，默认 1。
        page_size: 每页条数，默认 10。
        inst_type_list: 机构列表，传具体机构编码；默认 ["0"]（全部）。
        biz_line_type_list: 业务线列表，传具体编码；默认 ["0"]（全部）。
        fee_type_list: 费用类型列表，传具体编码；默认 ["0"]（全部）。
        start_biz_date: 交易开始时间，格式 "YYYY-MM-DD HH:mm:ss"。默认近 3 个月。
        end_biz_date: 交易结束时间，格式 "YYYY-MM-DD HH:mm:ss"。默认当前时间。
    """
    url = f"{BASE_URL}/v3/api/check-web-channel/actual/queryDailySummary"

    now = datetime.now()
    three_months_ago = now - timedelta(days=90)

    payload = {
        "currentPage": current_page,
        "pageSize": page_size,
        "instTypeList": inst_type_list if inst_type_list is not None else ["0"],
        "bizLineTypeList": biz_line_type_list if biz_line_type_list is not None else ["0"],
        "feeTypeList": fee_type_list if fee_type_list is not None else ["0"],
        "startBizDate": start_biz_date if start_biz_date else three_months_ago.strftime("%Y-%m-%d %H:%M:%S"),
        "endBizDate": end_biz_date if end_biz_date else now.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return client.post(url, payload)
