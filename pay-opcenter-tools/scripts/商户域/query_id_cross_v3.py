"""
userId与memId互转查询 — userId与memId互转查询
来源：schemas/商户域/v3_ID互查.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 支持两个查询方向：
#   1) userId → memId：先调用 memIdListQueryByUserId 转换
#   2) memId → 查详情：直接调用 queryMutilCardUserList
PARAM_SCHEMA = {
    "memIds": {
        "type": "array<string>",
        "required": True,
        "description": "会员号数组（单个也以数组形式传递）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "会员Id", "dataIndex": "memId"},
    {"title": "来源标识", "dataIndex": "sourceId"},   # 1=会员中心, 2=多卡会员
    {"title": "会员昵称", "dataIndex": "nickname"},
    {"title": "会员账户状态", "dataIndex": "memState"},  # enum: 0=无效,1=有效,2=冻结,3=注销
    {"title": "会员特殊标记", "dataIndex": "mark"},       # enum: 见schema
    {"title": "手机号", "dataIndex": "phone"},
    {"title": "地址", "dataIndex": "address"},
    {"title": "账户状态", "dataIndex": "acctStatus"},   # enum: 0=无效,1=有效
]


def execute(
    mem_ids: Optional[list] = None,
    user_id: Optional[str] = None,
) -> dict:
    """userId与memId互转查询（v3）
    支持两个查询方向：
      1) 通过userId查询：先将userId转换为memId列表，再查详情
      2) 直接通过memId列表查询详情

    Args:
        mem_ids: 会员号列表（与user_id二选一）。如 ["123456"]。
        user_id: 用户ID（与mem_ids二选一）。传入时自动转换为memId再查询。
    """
    if user_id:
        # 第一步：userId → memId列表
        convert_url = f"{BASE_URL}/v3/api/dispatch/invoke/memIdListQueryByUserId"
        convert_result = client.post(convert_url, {"userId": user_id})
        # 从转换结果中提取memId列表（假设返回数组）
        resolved_mem_ids = convert_result if isinstance(convert_result, list) else [convert_result]
    else:
        resolved_mem_ids = mem_ids or []

    url = f"{BASE_URL}/v3/api/dispatch/invoke/queryMutilCardUserList"
    payload = {"memIds": resolved_mem_ids}

    return client.post(url, payload)
