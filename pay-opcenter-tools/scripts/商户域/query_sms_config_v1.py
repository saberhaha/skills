"""
短信验证码配置列表查询 — 短信验证码配置列表查询
来源：schemas/商户域/v1_短信配置.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 使用 offset/limit 分页模式（非 page/pageSize）
PARAM_SCHEMA = {
    "offset": {
        "type": "number",
        "required": False,
        "default": 0,
        "description": "偏移量（计算公式: Math.min(total, (page-1)*pageSize)）"
    },
    "limit": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "业务标识", "dataIndex": "bizCode"},
    {"title": "业务中文名", "dataIndex": "bizName"},
    {"title": "限制条数", "dataIndex": "limitNum"},
    {"title": "周期,小时", "dataIndex": "limitPeriodH"},
    {"title": "间隔,秒", "dataIndex": "limitIntervalS"},
    {"title": "有效时长,分", "dataIndex": "ttlCodeMin"},
    {"title": "状态", "dataIndex": "status"},   # enum: 0=有效, 1=无效
    {"title": "创建时间", "dataIndex": "createdAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "修改时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    offset: int = 0,
    limit: int = 10,
    biz_code: Optional[str] = None,
) -> dict:
    """短信验证码配置列表查询（v1）
    查询短信验证码配置列表。支持按业务标识精确查询单条，或分页查询全量列表。

    Args:
        offset: 偏移量。可选。默认=0（第1页）。
        limit: 每页条数。可选。默认=10。
        biz_code: 业务标识。可选。传入时使用精确查询接口（findOne）。
    """
    if biz_code:
        # 精确查询单条配置
        url = f"{BASE_URL}/dispatcher/customercore.univerifyCode.findOne"
        payload = {"bizCode": biz_code}
    else:
        # 分页查询全量列表
        url = f"{BASE_URL}/dispatcher/customercore.univerifyCode.findList"
        payload = {
            "offset": offset,
            "limit": limit,
        }

    return client.post(url, payload)
