"""
规则信息管理 — 根据规则ID查询规则详情信息
来源：schemas/数据中心域/v1_规则信息管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "ruleId": {
        "type": "string",
        "required": True,
        "description": "规则ID（路由参数）"
    }
}

# 数据展示字段（详情页）
DISPLAY_FIELDS = [
    {"label": "ID", "dataIndex": "id"},
    {"label": "名称", "dataIndex": "name"},
    {"label": "描述", "dataIndex": "desc"},
    {"label": "负责人", "dataIndex": "principal"},
    {"label": "状态", "dataIndex": "state", "enum_values": {"CREATE": "草稿", "ON": "已开启", "OFF": "已关闭", "PAUSE": "已暂停"}},
    {"label": "Nsq信息（驱动类型）", "dataIndex": "nsqSources[].sourceDrive", "enum_values": {"EVENT": "事件驱动", "DATA": "数据驱动", "BINLOG": "binlog驱动", "FIXDATA": "修复驱动"}},
    {"label": "Nsq信息（环境）", "dataIndex": "nsqSources[].env", "enum_values": {"prod": "生产环境", "pre": "预发环境", "qa": "测试环境", "daily": "daily环境", "dev": "开发环境"}},
    {"label": "事件信息", "dataIndex": "eventTypes"},
    {"label": "行为过程", "dataIndex": "actionGroup"}
]

def execute(
    rule_id: str
) -> dict:
    """查询规则详情信息

    根据规则ID获取规则的完整信息，包括名称、描述、负责人、状态、NSQ配置、事件类型、行为组等。

    Args:
        rule_id: 规则ID。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.data.center.getRule"

    # 前端使用 singleParam 包装参数
    payload = {"singleParam": rule_id}

    return client.post(url, payload)
