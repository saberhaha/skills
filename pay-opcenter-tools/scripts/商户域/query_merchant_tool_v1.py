"""
kdtId与userNo互转查询 — kdtId与userNo互转查询
来源：schemas/商户域/v1_商户工具.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 支持两个查询方向：
#   1) kdtId → userNo：调用 getUserNoByKdtId，sentData传kdtId
#   2) userNo → kdtId：调用 getKdtIdByUserNo，sentData传userNo
PARAM_SCHEMA = {
    "sentData": {
        "type": "string",
        "required": True,
        "description": "kdtId→userNo模式传kdtId，userNo→kdtId模式传userNo（直接作为sentData传递，非对象包装）"
    }
}

# 数据展示（text类型，Input+TextArea展示转换结果与商户详情）
DISPLAY_COLUMNS = []  # text类型，无表格列


def execute(
    sent_data: str,
    direction: str = "kdtId_to_userNo",
) -> dict:
    """kdtId与userNo互转查询（v1）
    支持两个方向查询：
      - kdtId→userNo：传入kdtId，返回对应的userNo（mchId）
      - userNo→kdtId：传入userNo，返回对应的kdtId
    查询结果后自动调用商户详情接口获取完整信息。

    Args:
        sent_data: 查询值（必填）。kdtId→userNo模式传kdtId；userNo→kdtId模式传userNo。
        direction: 查询方向。可选值：'kdtId_to_userNo'（默认）或 'userNo_to_kdtId'。
    """
    if direction == "userNo_to_kdtId":
        convert_url = f"{BASE_URL}/dispatcher/pay.fullInfo.getKdtIdByUserNo"
    else:
        convert_url = f"{BASE_URL}/dispatcher/pay.fullInfo.getUserNoByKdtId"

    convert_result = client.post(convert_url, sent_data)

    # 辅助接口：获取商户完整信息
    detail_url = f"{BASE_URL}/dispatcher/pay.customer.getFullMerchantInfo"
    detail_result = client.post(detail_url, sent_data)

    return {
        "convert_result": convert_result,
        "merchant_detail": detail_result,
    }
