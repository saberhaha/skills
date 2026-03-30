"""
内部对账-差异详情 — v3 内部对账差异详情查询
来源：schemas/对账域/v3_内部对账_差异详情.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "taskResultId": {
        "type": "string",
        "required": True,
        "description": "差异结果ID（路由参数，必填）"
    },
}

# 数据展示列
# [UNRESOLVED: 返回 srcData/targetData 为 JSON 字符串，前端动态解析为列，需人工确认字段全集]
DISPLAY_COLUMNS = []


def execute(
    task_result_id: str,
) -> dict:
    """内部对账-差异详情（v3）- 查询内部对账差异明细。
    返回 srcData 和 targetData 字段为 JSON 字符串，需进一步解析。

    Args:
        task_result_id: 差异结果ID（必填）。

    Note:
        展示列 [UNRESOLVED]: 返回 srcData/targetData 为 JSON 字符串，前端动态解析为列，
        需人工确认字段全集后补全 DISPLAY_COLUMNS。
    """
    url = f"{BASE_URL}/v3/api/check-web-inner/payCheck/getDiffDetail"

    payload = {
        "taskResultId": task_result_id,
    }

    return client.post(url, payload)
