"""
监控配置 — 监控配置
来源：schemas/财务域/v1_监控配置.json
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
    "channelType": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"": "全部", "1": "银联", "2": "网联"},
        "description": "渠道类型"
    },
    "acctNo": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "": "全部",
            "0000300000000266": "北京高汇通商业管理有限公司备付金",
            "0000300000000265": "北京高汇通商业管理有限公司自有",
            "991100001624": "支付机构备付金账户"
        },
        "description": "预警账号"
    },
    "enable": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"": "全部", "1": "是", "0": "否"},
        "description": "是否预警"
    },
    "operator": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "操作人"
    },
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
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "预警账号", "dataIndex": "acctNo"},
    {"title": "渠道", "dataIndex": "channelType"},
    {"title": "是否预警", "dataIndex": "enable"},
    {"title": "预警金额(万元)", "dataIndex": "balance"},
    {"title": "时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作人", "dataIndex": "operator"},
]


def execute(
    channel_type: Optional[Literal["", "1", "2"]] = "",
    acct_no: Optional[str] = "",
    enable: Optional[Literal["", "1", "0"]] = "",
    operator: Optional[str] = "",
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询备付金余额预警监控配置列表。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        channel_type: 渠道类型。可选。枚举：""=全部, "1"=银联, "2"=网联。默认=""（全部）。
        acct_no: 预警账号。可选。枚举值见 PARAM_SCHEMA。默认=""（全部）。
        enable: 是否预警。可选。枚举：""=全部, "1"=是, "0"=否。默认=""（全部）。
        operator: 操作人。可选。默认=""。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.withdraw.channel.banlance.warn.query"

    payload = {
        "channelType": channel_type,
        "acctNo": acct_no,
        "enable": enable,
        "operator": operator,
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
