"""
内部商户管理
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "createDateStart": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "申请开始时间"
    },
    "createDateEnd": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "申请结束时间"
    },
    "userNo": {
        "type": "string",
        "required": False,
        "description": "商户号"
    },
    "settleSequenceNo": {
        "type": "string",
        "required": False,
        "description": "结算流水号"
    },
    "curIdx": {
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
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "结算申请时间", "dataIndex": "settleTransCreateTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "结算完成时间", "dataIndex": "settleTransFinishTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "商户号", "dataIndex": "userNo"},
    {"title": "结算状态", "dataIndex": "settleState"},
    {"title": "结算金额", "dataIndex": "settleAmount"},
    {"title": "结算流水号", "dataIndex": "settleSequenceNo"}
]


def execute(
    create_date_start: Optional[str] = None,
    create_date_end: Optional[str] = None,
    user_no: Optional[str] = None,
    settle_sequence_no: Optional[str] = None,
    cur_idx: int = 1,
    page_size: int = 10,
) -> dict:
    """内部商户管理查询
    查询内部商户结算记录列表。

    Args:
        create_date_start: 申请开始时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        create_date_end: 申请结束时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        user_no: 商户号。可选。
        settle_sequence_no: 结算流水号。可选。
        cur_idx: 页码。默认=1。
        page_size: 每页条数。默认=10。
    """

    url = f"{BASE_URL}/v3/api/dispatch/invoke/inner_merchant_settled_v1/"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "curIdx": cur_idx,
        "pageSize": page_size,
    }

    # 可选参数填充
    if create_date_start is not None:
        payload["createDateStart"] = create_date_start
    if create_date_end is not None:
        payload["createDateEnd"] = create_date_end
    if user_no is not None:
        payload["userNo"] = user_no
    if settle_sequence_no is not None:
        payload["settleSequenceNo"] = settle_sequence_no

    return client.get(url, params=payload)
