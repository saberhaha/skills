"""
会员操作记录查询 — 会员操作记录查询
来源：schemas/商户域/v3_操作记录.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "memId": {
        "type": "string",
        "required": True,
        "description": "会员号"
    },
    "operateTypeList": {
        "type": "array<string>",
        "required": True,
        "default": ["FREEZE", "VALID"],
        "description": "操作类型列表（固定传冻结和解冻：FREEZE=冻结, VALID=解冻）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
# 无分页
DISPLAY_COLUMNS = [
    {"title": "操作时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "操作人", "dataIndex": "operatorName"},
    {"title": "操作项", "dataIndex": "operateTypeDesc"},
]


def execute(
    mem_id: str,
    operate_type_list: list = None,
) -> dict:
    """会员操作记录查询（v3）
    查询指定会员的操作记录（冻结/解冻记录）。无分页，返回全量结果。
    通常在会员详情页通过Dialog弹窗展示。

    Args:
        mem_id: 会员号（必填）。
        operate_type_list: 操作类型列表。可选。默认=['FREEZE', 'VALID']（冻结和解冻）。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.operate.queryOperateLogsByMemId"

    payload = {
        "memId": mem_id,
        "operateTypeList": operate_type_list if operate_type_list is not None else ["FREEZE", "VALID"],
    }

    return client.get(url, payload)
