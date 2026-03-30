"""
银行及卡信息维护（总行列表） — 银行及卡信息维护（总行列表）
来源：schemas/商户域/v3_银行卡管理.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 主接口无入参，一次加载全部总行列表
# 搜索bankName为前端客户端过滤，不发请求
PARAM_SCHEMA = {}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
# 无分页
DISPLAY_COLUMNS = [
    {"title": "序号", "dataIndex": "auto"},
    {"title": "总行名称", "dataIndex": "bankName"},
]


def execute(
    bank_name_filter: Optional[str] = None,
) -> dict:
    """银行及卡信息维护（总行列表）查询（v3）
    加载全量总行列表（无入参，一次返回全部）。
    支持查询指定总行的支行列表（需提供银行名称）。

    Args:
        bank_name_filter: 总行名称。可选。传入时额外查询该总行的支行列表。
    """
    # 主接口：无入参，查询全部总行列表
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.customercore.bank.query"
    result = client.post(url, {})

    if bank_name_filter:
        # 辅助接口：查询支行列表
        branch_url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.customercore.bankcode.query"
        branch_result = client.post(branch_url, {"bankName": bank_name_filter})
        return {
            "bank_list": result,
            "branch_list": branch_result,
        }

    return result
