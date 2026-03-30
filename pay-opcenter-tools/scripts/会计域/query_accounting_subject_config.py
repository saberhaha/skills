"""
会计科目配置 — 会计科目配置
来源：schemas/会计域/v1_会计科目配置.json
"""
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v1_会计科目配置.json）
PARAM_SCHEMA = {
    "pageNo": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码",
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数",
    },
    "code": {
        "type": "string",
        "required": False,
        "description": "科目代码（搜索）",
    },
    "type": {
        "type": "number",
        "required": False,
        "default": 0,
        "description": "科目属性，0=全部",
    },
    "level": {
        "type": "number",
        "required": False,
        "default": 0,
        "description": "科目级别，0=全部",
    },
}

# 数据展示列（来源：schemas/会计域/v1_会计科目配置.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "科目代码", "dataIndex": "subjectCode"},
    {"title": "科目属性", "dataIndex": "subjectClassValue"},
    {"title": "科目级别", "dataIndex": "subjectRankValue"},
    {"title": "科目名称", "dataIndex": "subjectName"},
    {"title": "科目方向", "dataIndex": "subjectDirection"},
    {"title": "上级科目", "dataIndex": "fatherSubject"},
    {"title": "启用日期", "dataIndex": "enableDate", "format": "YYYY-MM-DD"},
    {"title": "透支标识", "dataIndex": "overdraftLogo"},
    {"title": "可用标识", "dataIndex": "availableLogo"},
    {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    code: Optional[str] = None,
    type: Optional[int] = None,
    level: Optional[int] = None,
    page_no: int = 1,
    page_size: int = 10,
) -> dict:
    """查询会计科目配置列表。
    用户只需提供科目代码等筛选条件，其余参数自动使用页面默认值。

    Args:
        code: 科目代码（模糊搜索）。可选。
        type: 科目属性。可选，默认=0（全部）。
        level: 科目级别。可选，默认=0（全部）。
        page_no: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/accounting.subject.list"

    payload = {
        "pageNo": page_no,
        "pageSize": page_size,
        "type": int(type) if type is not None else 0,    # 默认：全部
        "level": int(level) if level is not None else 0,  # 默认：全部
    }
    if code is not None and code != "":
        payload["code"] = code

    return client.post(url, payload)
