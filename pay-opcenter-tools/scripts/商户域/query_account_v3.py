"""
通用资产账号查询 — 通用资产账号查询
来源：schemas/商户域/v3_账户查询.json
"""
import sys
import os
from typing import Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 注意：bizType 枚举值在 qa 和 prod 环境不同
PARAM_SCHEMA = {
    "bizUserId": {
        "type": "string",
        "required": True,
        "description": "业务账户"
    },
    "bizType": {
        "type": "enum",
        "required": True,
        # prod 环境枚举值
        "enum_values_prod": {
            "810006729200": "有赞客",
            "810006902200": "爱逛",
            "810007616600": "爱逛买手店达人",
            "810007535300": "爱逛CPM广告主"
        },
        # qa 环境枚举值
        "enum_values_qa": {
            "810006829499": "有赞客",
            "810007131999": "爱逛",
            "810007849100": "爱逛买手店达人",
            "810007778499": "爱逛CPM广告主"
        },
        "description": "业务类型（qa和prod环境枚举值不同，请根据环境选择对应值）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
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
    biz_type: str,
) -> dict:
    """通用资产账号查询（v3）
    查询通用资产账号信息。

    Args:
        biz_user_id: 业务账户（必填）。
        biz_type: 业务类型（必填）。
            prod环境枚举：
              '810006729200'=有赞客, '810006902200'=爱逛,
              '810007616600'=爱逛买手店达人, '810007535300'=爱逛CPM广告主
            qa环境枚举：
              '810006829499'=有赞客, '810007131999'=爱逛,
              '810007849100'=爱逛买手店达人, '810007778499'=爱逛CPM广告主
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.dragonfly.user.account.query.account.by.biz/"

    # filterParams 过滤空值
    payload = {k: v for k, v in {
        "bizUserId": biz_user_id,
        "bizType": biz_type,
    }.items() if v is not None and v != ""}

    return client.post(url, payload)
