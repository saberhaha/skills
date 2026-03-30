"""
账户查询 (v3)
来源：schemas/账户查询域/v3_账户查询.json
"""
import sys
import os
from typing import Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {
    "bizUserId": {
        "type": "string", "required": True,
        "description": "业务账户"
    },
    "bizType": {
        "type": "enum", "required": True,
        "enum_values": {
            "810006729200": "有赞客",
            "810006902200": "爱逛",
            "810007616600": "爱逛买手店达人",
            "810007535300": "爱逛CPM广告主",
        },
        "description": "业务类型（生产环境枚举值）"
    },
}

DISPLAY_COLUMNS = [
    {"title": "支付用户号", "dataIndex": "userNo"},
    {"title": "支付用户类型", "dataIndex": "userType"},
    {"title": "通用资产号", "dataIndex": "accountNo"},
    {"title": "业务类型", "dataIndex": "bizType"},
    {"title": "业务账号", "dataIndex": "bizUserId"},
    {"title": "账号绑定状态", "dataIndex": "bindStatus"},
    {"title": "手机号", "dataIndex": "phone"},
    {"title": "通用账号状态", "dataIndex": "status"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    biz_user_id: str,
    biz_type: Literal["810006729200", "810006902200", "810007616600", "810007535300"],
) -> dict:
    """账户查询 (v3)
    根据业务账户和业务类型查询通用资产账号信息。

    Args:
        biz_user_id: 业务账户。必填。
        biz_type: 业务类型（生产环境枚举值）。必填。
            枚举：'810006729200'=有赞客, '810006902200'=爱逛,
                  '810007616600'=爱逛买手店达人, '810007535300'=爱逛CPM广告主。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.dragonfly.user.account.query.account.by.biz/"

    payload = {
        "bizUserId": biz_user_id,
        "bizType": biz_type,
    }

    return client.post(url, payload)
