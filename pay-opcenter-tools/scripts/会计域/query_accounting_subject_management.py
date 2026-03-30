"""
会计科目管理 — 会计科目管理
来源：schemas/会计域/v2_会计科目管理.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/会计域/v2_会计科目管理.json）
PARAM_SCHEMA = {
    "accountingEntity": {
        "type": "enum",
        "required": False,
        "default": 0,
        "enum_values": {"0": "全部", "1": "高汇通支付", "2": "有赞平台"},
        "description": "核算主体（0=全部为前端附加选项；枚举由后端接口动态下发）",
    },
    "level": {
        "type": "enum",
        "required": False,
        "default": 1,
        "enum_values": {"1": "一级科目", "2": "二级科目", "3": "三级科目"},
        "description": "科目级别，默认=1(一级科目)",
    },
    "subjectCode": {
        "type": "string",
        "required": False,
        "description": "科目编码",
    },
    "subjectName": {
        "type": "string",
        "required": False,
        "description": "科目名称",
    },
    "activeFlag": {
        "type": "enum",
        "required": False,
        "default": "1",
        "enum_values": {"1": "可用", "2": "不可用"},
        "description": "可用标识，默认='1'(可用)；注：源码中默认值为字符串 '1'",
    },
    "approveFlag": {
        "type": "enum",
        "required": False,
        "default": 1,
        "enum_values": {"1": "审核通过", "2": "待审核", "3": "审核驳回"},
        "description": "审核状态，默认=1(审核通过)",
    },
    "page": {
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
}

# 数据展示列（来源：schemas/会计域/v2_会计科目管理.json display.columns）
DISPLAY_COLUMNS = [
    {"title": "核算主体", "dataIndex": "accountingEntity"},
    {"title": "科目类别", "dataIndex": "type"},
    {"title": "科目级别", "dataIndex": "level"},
    {"title": "科目编码", "dataIndex": "code"},
    {"title": "科目名称", "dataIndex": "name"},
    {"title": "科目方向", "dataIndex": "balanceDir"},
    {"title": "上级科目编码", "dataIndex": "parentsCode"},
    {"title": "可用标识", "dataIndex": "activeFlag"},
    {"title": "是否可透支", "dataIndex": "overFlag"},
    {"title": "创建人", "dataIndex": "createUser"},
    {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD"},
    {"title": "审核人", "dataIndex": "approveUser"},
    {"title": "审核时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD"},
    {"title": "审核指令", "dataIndex": "approveInstruction"},
]


def execute(
    accounting_entity: Optional[Literal["0", "1", "2"]] = None,
    level: Optional[Literal["1", "2", "3"]] = None,
    subject_code: Optional[str] = None,
    subject_name: Optional[str] = None,
    active_flag: Optional[Literal["1", "2"]] = None,
    approve_flag: Optional[Literal["1", "2", "3"]] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """查询会计科目管理列表。
    用户只需提供科目编码、名称等筛选条件，其余参数自动使用页面默认值。

    Args:
        accounting_entity: 核算主体。可选。枚举：0=全部, 1=高汇通支付, 2=有赞平台。默认=0(全部)。
        level: 科目级别。可选。枚举：1=一级科目, 2=二级科目, 3=三级科目。默认=1(一级科目)。
        subject_code: 科目编码。可选。
        subject_name: 科目名称。可选。
        active_flag: 可用标识。可选。枚举：1=可用, 2=不可用。默认='1'(可用)。
        approve_flag: 审核状态。可选。枚举：1=审核通过, 2=待审核, 3=审核驳回。默认=1(审核通过)。
        page: 页码。可选，默认=1。
        page_size: 每页条数。可选，默认=10。
    """
    url = f"{BASE_URL}/dispatcher/pay.accounting.subject.query.list"

    payload: dict = {
        "page": page,
        "pageSize": page_size,
        "accountingEntity": int(accounting_entity) if accounting_entity is not None else 0,  # 默认：全部
        "level": int(level) if level is not None else 1,       # 默认：一级科目
        "activeFlag": active_flag if active_flag is not None else "1",   # 默认：可用
        "approveFlag": int(approve_flag) if approve_flag is not None else 1,  # 默认：审核通过
    }
    if subject_code is not None:
        payload["subjectCode"] = subject_code
    if subject_name is not None:
        payload["subjectName"] = subject_name

    return client.post(url, payload)
