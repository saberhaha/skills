"""
kdtId与userNo互转查询(v3) — kdtId与userNo互转查询(v3)
来源：schemas/商户域/v3_KdtId_UserNo互查.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# v3版本参数包装在 singleParam 中
PARAM_SCHEMA = {
    "singleParam": {
        "type": "string",
        "required": True,
        "description": "kdtId→userNo模式传kdtId；userNo→kdtId模式传userNo（包装在singleParam字段中）"
    }
}

# 数据展示（text类型，无表格列）
DISPLAY_COLUMNS = []  # text类型


def execute(
    single_param: str,
    direction: str = "kdtId_to_userNo",
) -> dict:
    """kdtId与userNo互转查询（v3）
    v3版本，参数包装在singleParam中。
    支持两个方向查询：
      - kdtId→userNo：传入kdtId，返回对应的userNo
      - userNo→kdtId：传入userNo，返回对应的kdtId
    查询结果后自动调用商户详情接口获取完整信息。

    Args:
        single_param: 查询值（必填）。kdtId→userNo传kdtId；userNo→kdtId传userNo。
        direction: 查询方向。可选值：'kdtId_to_userNo'（默认）或 'userNo_to_kdtId'。
    """
    if direction == "userNo_to_kdtId":
        convert_url = f"{BASE_URL}/dispatcher/pay.fullInfo.getKdtIdByUserNo/"
    else:
        convert_url = f"{BASE_URL}/dispatcher/pay.fullInfo.getUserNoByKdtId/"

    convert_result = client.post(convert_url, {"singleParam": single_param})

    # 辅助接口：获取商户完整信息（v3使用ForOpCenter后缀接口）
    detail_url = f"{BASE_URL}/dispatcher/pay.customer.getFullMerchantInfoForOpCenter/"
    detail_result = client.post(detail_url, {"singleParam": single_param})

    return {
        "convert_result": convert_result,
        "merchant_detail": detail_result,
    }
