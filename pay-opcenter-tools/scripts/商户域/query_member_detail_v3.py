"""
支付会员信息查询 — 支付会员信息查询
来源：schemas/商户域/v3_会员详情查询.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "memId": {
        "type": "string",
        "required": True,
        "description": "会员号（可通过userId转换获得）"
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "size": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "会员号", "dataIndex": "memId"},
    {"title": "外部业务方账号", "dataIndex": "userId"},
    {"title": "来源标识", "dataIndex": "sourceId"},  # BIZTYPE枚举，qa/prod环境值不同
    {"title": "会员昵称", "dataIndex": "nickname"},
    {"title": "会员账户状态", "dataIndex": "memState"},  # enum: 0=无效,1=有效,2=冻结,3=注销
    {"title": "会员特殊标记", "dataIndex": "mark"},       # enum: 0=普通,...,13=有赞客
    {"title": "手机号", "dataIndex": "phone"},
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "账户状态", "dataIndex": "acctStatus"},   # enum: 0=无效,1=有效
]


def execute(
    mem_id: Optional[str] = None,
    user_id: Optional[str] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """支付会员信息查询（v3）
    查询支付会员详细信息。支持通过memId或userId查询（传userId时自动转换为memId）。

    Args:
        mem_id: 会员号（与user_id二选一）。
        user_id: 用户ID（与mem_id二选一）。传入时自动调用转换接口获取memId。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    resolved_mem_id = mem_id

    if user_id and not mem_id:
        # 辅助接口：通过userId查询memId
        convert_url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.user.queryMemIdByUserId"
        convert_result = client.get(convert_url, {"userId": user_id, "sourceId": "1"})
        resolved_mem_id = convert_result

    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.usercore.queryMemberInfo"

    params = {k: v for k, v in {
        "memId": resolved_mem_id,
        "currentPage": current_page,
        "size": size,
    }.items() if v is not None}

    return client.get(url, params)
