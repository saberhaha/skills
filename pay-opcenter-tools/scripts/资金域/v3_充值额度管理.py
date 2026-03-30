"""
商家充值限额信息查询
来源：schemas/资金域/v3_充值额度管理.json
功能：查询商家充值限额信息，包含商家信息和限额配置
"""
import sys
import os
from typing import Optional, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema
PARAM_SCHEMA = {
    "kdtIdOrMchId": {
        "type": "string",
        "required": True,
        "description": "店铺ID(kdtId)或支付商户号(mchId)"
    },
    "rechargeType": {
        "type": "enum",
        "required": True,
        "default": 17,
        "enum_values": {"17": "店铺余额"},
        "description": "充值类型（当前仅支持店铺余额=17）"
    }
}

# 数据展示配置
DISPLAY_CONFIG = {
    "type": "detail",
    "sections": [
        {
            "title": "商家信息",
            "fields": [
                {"label": "店铺ID", "field": "kdtId"},
                {"label": "店铺名称", "field": "shopName", "note": "源字段: merchantShortName"},
                {"label": "店铺类型", "field": "businessType", "note": "源字段: partnerId"},
                {"label": "支付商户号", "field": "payMchId"},
                {"label": "经营主体类型", "field": "businessEntityType", "note": "枚举: 1=个人, 2=企业, 3=个体工商户, 4=其他组织, 5=政府及事业单位"}
            ]
        },
        {
            "title": "限额信息",
            "fields": [
                {"label": "账户类型", "field": "accountTypeDesc"},
                {"label": "限额规则", "field": "limitBelongType", "note": "源字段: limitBelongEnum"},
                {"label": "限额周期", "field": "quotaCycleType", "note": "源字段: quotaCycleEnum"},
                {"label": "充值限额（元）", "field": "limit", "note": "分→元: limit/100"},
                {"label": "已用额度（元）", "field": "useAmount", "note": "分→元: useAmount/100"},
                {"label": "可用额度（元）", "field": "available", "note": "分→元: available/100"}
            ]
        }
    ]
}


def _get_user_no_by_kdt_id(kdt_id: str) -> Optional[str]:
    """kdtId → mchId转换（辅助函数）

    Args:
        kdt_id: 店铺ID

    Returns:
        返回支付商户号(mchId)，失败返回None
    """
    url = f"{BASE_URL}/dispatcher/pay.fullInfo.getUserNoByKdtId"
    payload = {"singleParam": kdt_id}
    try:
        result = client.post(url, payload)
        return result.get("data")
    except:
        return None


def _get_kdt_id_by_user_no(mch_id: str) -> Optional[str]:
    """mchId → kdtId转换（辅助函数）

    Args:
        mch_id: 支付商户号

    Returns:
        返回店铺ID(kdtId)，失败返回None
    """
    url = f"{BASE_URL}/dispatcher/pay.fullInfo.getKdtIdByUserNo"
    payload = {"singleParam": mch_id}
    try:
        result = client.post(url, payload)
        return result.get("data")
    except:
        return None


def _get_merchant_info(mch_id: str) -> Optional[Dict[str, Any]]:
    """获取商家详细信息（辅助函数）

    Args:
        mch_id: 支付商户号

    Returns:
        返回商家详细信息
    """
    url = f"{BASE_URL}/dispatcher/pay.customer.getFullMerchantInfoForOpCenter"
    payload = {"singleParam": mch_id}
    try:
        result = client.post(url, payload)
        return result.get("data")
    except:
        return None


def execute(
    kdt_id_or_mch_id: str,
    recharge_type: int = 17
) -> Dict[str, Any]:
    """查询商家充值限额信息

    Args:
        kdt_id_or_mch_id: 店铺ID(kdtId)或支付商户号(mchId)。必填
        recharge_type: 充值类型。可选。枚举：17=店铺余额。默认：17

    Returns:
        返回商家信息和限额信息。
        查询流程：
        1. 输入kdtId或mchId，先尝试转换为mchId
        2. 获取商家详细信息
        3. 查询限额信息
    """
    # 步骤1：确定mchId
    mch_id = None
    kdt_id = None

    # 尝试作为kdtId转换
    mch_id = _get_user_no_by_kdt_id(kdt_id_or_mch_id)
    if mch_id:
        kdt_id = kdt_id_or_mch_id
    else:
        # 尝试作为mchId转换
        kdt_id = _get_kdt_id_by_user_no(kdt_id_or_mch_id)
        if kdt_id:
            mch_id = kdt_id_or_mch_id
        else:
            # 无法识别，直接使用输入值作为mchId
            mch_id = kdt_id_or_mch_id

    # 步骤2：获取商家信息
    merchant_info = None
    if mch_id:
        merchant_info = _get_merchant_info(mch_id)

    # 步骤3：查询限额信息
    # v1版本API路径（虽然标注为v3，但实际使用/dispatcher/前缀）
    url = f"{BASE_URL}/dispatcher/pay.recharge.ops.quota.queryPrincipalRechargeQuotaInfo"

    payload = {
        "mchId": mch_id,
        "rechargeType": str(recharge_type)
    }

    quota_result = client.post(url, payload)

    # 组装返回结果
    result = {
        "merchantInfo": merchant_info,
        "quotaInfo": quota_result.get("data") if quota_result else None
    }

    return result
