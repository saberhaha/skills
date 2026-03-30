"""
PayInfos优先级配置 — 查询PayInfos优先级配置规则
来源：schemas/收银台域/v3_PayInfos优先级配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_PayInfos优先级配置.json）
PARAM_SCHEMA = {
    "type": {
        "type": "number",
        "required": True,
        "default": 3,
        "description": "数据类型固定值：CashierBizDataType.PayInfoPriority=3（页面固定，无需用户传入）"
    },
    "id": {
        "type": "number",
        "required": False,
        "description": "规则ID，传入时查询单条规则详情，不传则查询当前已发布规则列表"
    },
}

# 数据展示列（来源：v3_PayInfos优先级配置.json → display）
# 规则卡片视图，非标准表格，每条规则包含：
#   scenarios: 场景列表
#   value: PayInfo配置值
#   desc: 备注
#   priority: 优先级
DISPLAY_COLUMNS = [
    {"title": "规则ID", "dataIndex": "id"},
    {"title": "场景列表", "dataIndex": "scenarios"},
    {"title": "PayInfo配置值", "dataIndex": "value"},
    {"title": "备注", "dataIndex": "desc"},
    {"title": "优先级", "dataIndex": "priority"},
]


def execute(
    rule_id: Optional[int] = None,
) -> dict:
    """查询PayInfos优先级配置规则
    不传 rule_id 时返回当前已发布的优先级配置规则列表（status 接口）；
    传入 rule_id 时返回该规则的详情（detail 接口）。

    Args:
        rule_id: 规则ID。可选。不传则查询已发布规则列表，传入则查询单条规则详情。
    """
    TYPE = 3  # CashierBizDataType.PayInfoPriority = 3
    if rule_id is not None:
        url = f"{BASE_URL}/v3/api/cashier-biz-manage/shared/group/type/{TYPE}/detail/{rule_id}"
        return client.get(url)
    else:
        url = f"{BASE_URL}/v3/api/cashier-biz-manage/shared/group/type/{TYPE}/status"
        return client.get(url)
