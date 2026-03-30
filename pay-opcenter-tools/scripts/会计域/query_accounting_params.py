"""
参数维护 — 参数维护
来源：schemas/会计域/v1_参数维护.json

# TODO: 源码未找到真实查询 API。组件查询逻辑仅为本地 setTimeout，保存接口 url 为空串，
#       无可用于 Skill 化的真实查询 API。需人工补全真实接口路径后方可使用。
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_参数维护.json）
PARAM_SCHEMA = {
    "bookkeepingCode": {
        "type": "string",
        "required": False,
        "description": "记账码（页面查询输入）",
    },
}

# 数据展示列（来源：schemas/会计域/v1_参数维护.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "参数代码", "dataIndex": "paramCode"},
    {"title": "参数值", "dataIndex": "paramValue"},
    {"title": "描述", "dataIndex": "desc"},
]


def execute(
    bookkeeping_code: Optional[str] = None,
) -> dict:
    """查询参数维护列表。
    # TODO: 源码未找到真实查询 API，需人工补全接口路径后方可使用。

    Args:
        bookkeeping_code: 记账码。可选。
    """
    # TODO: 源码未找到真实查询 API，需人工补全
    raise NotImplementedError(
        "参数维护：源码中无真实查询接口（组件仅使用 setTimeout 模拟，保存接口 url 为空串）。"
        "请人工补全真实接口路径后再使用本 Skill。"
    )
