"""
微信子商户管理 — 查询微信子商户配置 (v1)
来源：schemas/渠道域/v1_微信子商户管理.json
"""
import sys
import os
from typing import Optional, Literal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v1_微信子商户管理.json）
PARAM_SCHEMA = {
    "proxyId": {
        "type": "enum", "required": True,
        "description": "服务商标识（作为数组第0位传入）",
        "enum_values": {
            "wx_citic_h_online": "服务商-中信总行-线上费率",
            "wx_citic_h_offline": "服务商-中信总行-线下费率",
        },
    },
    "subMchId": {
        "type": "string", "required": False,
        "description": "子商户标识（作为数组第1位传入）",
    },
}

# 数据展示列（来源：v1_微信子商户管理.json → display.columns）
DISPLAY_COLUMNS = [
    {"title": "支付目录", "dataIndex": "paths"},
    {"title": "绑定关系(subAppId - subscribeAppId)", "dataIndex": "configs"},
]


def execute(
    proxy_id: Literal['wx_citic_h_online', 'wx_citic_h_offline'],
    sub_mch_id: Optional[str] = None,
) -> dict:
    """查询微信子商户配置 (v1)
    用户需提供服务商标识，可选提供子商户标识。
    入参以数组形式传入：[proxyId, subMchId]。

    Args:
        proxy_id: 服务商标识。必填。枚举：
            wx_citic_h_online=服务商-中信总行-线上费率,
            wx_citic_h_offline=服务商-中信总行-线下费率。
        sub_mch_id: 子商户标识。可选。
    """
    url = f"{BASE_URL}/dispatcher/channel.wechatSubMchConfig.query"

    # 入参以数组形式传入，proxyId 为第0位，subMchId 为第1位
    multi_param = [proxy_id]
    if sub_mch_id is not None:
        multi_param.append(sub_mch_id)

    payload = {"multiParam": multi_param}

    return client.post(url, payload)
