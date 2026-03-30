"""
释放冻结订单查询 (v3)
来源：schemas/账务域/v3_释放冻结订单.json
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "userNo": {"type": "string", "required": True, "description": "商户号"},
    "targetId": {"type": "string", "required": True, "description": "订单号"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
# freezeType 映射：{1:'提现', 4:'退款', 16:'维权', 99:'其他'}
DISPLAY_COLUMNS = [
    {"title": "业务类型", "dataIndex": "freezeType"},
    {"title": "单号", "dataIndex": "targetId"},
    {"title": "金额", "dataIndex": "freeze"}
]


def execute(
    user_no: str,
    target_id: str,
) -> dict:
    """释放冻结订单查询（v3）
    查询指定商户和订单号下的冻结订单详情。
    无分页参数，两个入参均为必填。
    返回结果为单条记录（空对象时表示无数据）。

    freezeType 枚举：1=提现, 4=退款, 16=维权, 99=其他
    freezeStateMap 枚举：1=默认正在冻结中的, 2=正常解冻

    Args:
        user_no: 商户号。必填。
        target_id: 订单号。必填。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.acctrans.unfreeze.freezeDetails"

    payload = {
        "userNo": user_no,
        "targetId": target_id
    }

    return client.post(url, payload)
