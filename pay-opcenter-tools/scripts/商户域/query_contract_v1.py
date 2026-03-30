"""
合约文件URL查询 — 合约文件URL查询
来源：schemas/商户域/v1_合同管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "cosKey": {
        "type": "string",
        "required": True,
        "description": "文件查询key（需带上文件前缀CONTRACT_PROTOCOL/路径）"
    },
    "deadLineDays": {
        "type": "string",
        "required": False,
        "default": "1",
        "description": "过期时间（天），默认1天"
    }
}

# 数据展示（来源：步骤 1.2 提取的前端信息字段）
# 非表格场景：返回文件URL字符串，通过TextArea展示
DISPLAY_COLUMNS = []  # text类型，无表格列


def execute(
    cos_key: str,
    dead_line_days: Optional[str] = "1",
) -> dict:
    """合约文件URL查询（v1）
    查询合约文件的临时访问URL。用户输入cosKey（含前缀路径），返回可访问的URL。

    Args:
        cos_key: 文件查询key（必填）。需带上文件前缀，如 CONTRACT_PROTOCOL/xxx。
        dead_line_days: 过期时间（天）。可选。默认=1（1天后过期）。
    """
    url = f"{BASE_URL}/dispatcher/customercenter.contractservice.queryContractFileUrl"

    payload = {
        "cosKey": cos_key,
        "deadLineDays": dead_line_days if dead_line_days is not None else "1",
    }

    return client.post(url, payload)
