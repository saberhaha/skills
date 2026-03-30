"""
支付信息查询 — 根据订单号查询支付信息（含交易、支付、退款、优惠、手续费）
来源：前端组件 pay-platform-core/payment-info-query.js
版本：v1
页面路由：/page/paymentInfo
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：前端组件 payment-info-query.js 的 doQuery 方法）
PARAM_SCHEMA = {
    "orderNo": {"type": "string", "required": True, "description": "订单号（支持订单号、收单号、支付流水号等）"}
}

# 数据展示列（来源：前端组件 payment-info-query.js 的多个 columns 定义）
# 多表格展示：支付信息、交易信息、退款信息、优惠详情、手续费信息
DISPLAY_TABLES = {
    "支付信息": [
        {"title": "支付单号", "dataIndex": "payOrderNo"},
        {"title": "支付明细号", "dataIndex": "payDetailNo"},
        {"title": "三方支付流水号", "dataIndex": "sidesPaySerialNo"},
        {"title": "状态", "dataIndex": "payStatus"},
        {"title": "标记", "dataIndex": "sign"},
        {"title": "支付方式", "dataIndex": "paymentMode"},
        {"title": "自有支付", "dataIndex": "selfPay"},
        {"title": "备注", "dataIndex": "remark"},
        {"title": "支付金额", "dataIndex": "payBalance"},
        {"title": "渠道商户号", "dataIndex": "channelMerchantNo"},
        {"title": "支付时间", "dataIndex": "completeTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
    ],
    "交易信息": [
        {"title": "收单号", "dataIndex": "collectNo"},
        {"title": "业务单号", "dataIndex": "businessNo"},
        {"title": "商户号", "dataIndex": "merchantNo"},
        {"title": "状态", "dataIndex": "businessStatus"},
        {"title": "交易金额", "dataIndex": "dealBalance"},
        {"title": "交易描述", "dataIndex": "dealDesc"},
        {"title": "合作方", "dataIndex": "partnerId"},
        {"title": "业务标识", "dataIndex": "businessIdentification"},
        {"title": "过期时间", "dataIndex": "overdueTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
    ],
    "退款信息": [
        {"title": "退款单号", "dataIndex": "refundNo"},
        {"title": "退款金额", "dataIndex": "refundBalance"},
        {"title": "退款方式", "dataIndex": "refundChannel"},
        {"title": "支付方式", "dataIndex": "originPayChannel"},
        {"title": "状态", "dataIndex": "refundStatus"},
        {"title": "扩展信息", "dataIndex": "extensionInfo"},
        {"title": "业务退款单号", "dataIndex": "businessRefundNo"},
        {"title": "退款明细号", "dataIndex": "refundDetailNo"},
        {"title": "支付明细号", "dataIndex": "payDetailNo"},
        {"title": "三方支付流水号", "dataIndex": "outerSerialNo"},
        {"title": "创建时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
    ],
    "优惠详情": [
        {"title": "支付明细", "dataIndex": "key"},
        {"title": "支付状态", "dataIndex": "payState"},
        {"title": "商家结算金额", "dataIndex": "settleAmt"},
        {"title": "用户实际付款", "dataIndex": "customerPayAmt"},
        {"title": "用户实际退款", "dataIndex": "customerRefundAmt"},
        {"title": "全额抵扣", "dataIndex": "fullDeduction"},
        {"title": "总优惠", "dataIndex": "totalDiscountAmt"},
        {"title": "总免充优惠(非入账)", "dataIndex": "totalDiscountUnAccountAmt"},
        {"title": "总预充优惠(入账)", "dataIndex": "totalDiscountAccountAmt"},
        {"title": "总退优惠", "dataIndex": "totalRefundDiscountAmt"},
        {"title": "总退免充优惠", "dataIndex": "totalRefundUnDiscountAccountAmt"},
        {"title": "总退预充优惠", "dataIndex": "totalRefundDiscountAccountAmt"}
    ],
    "手续费信息": [
        {"title": "主业务单号", "dataIndex": "bizNo"},
        {"title": "子业务单号", "dataIndex": "bizSubNo"},
        {"title": "交易结算金额", "dataIndex": "bizAmount"},
        {"title": "收费包编号", "dataIndex": "packNo"},
        {"title": "收费类型", "dataIndex": "feeType"},
        {"title": "收费金额", "dataIndex": "feeAmount"},
        {"title": "费率", "dataIndex": "packRatio"},
        {"title": "商户号", "dataIndex": "mchId"},
        {"title": "合作方", "dataIndex": "partnerId"},
        {"title": "业务交易场景", "dataIndex": "bizPdCodeDesc"},
        {"title": "计费包交易场景", "dataIndex": "packPdCodeDesc"},
        {"title": "来源线上｜线下", "dataIndex": "marketChannel"},
        {"title": "结算状态", "dataIndex": "settleStatus"}
    ]
}


def execute(
    order_no: str,
) -> dict:
    """查询支付信息（对应页面路由 /page/paymentInfo）

    根据订单号查询完整的支付信息，包括支付信息、交易信息、退款信息、优惠详情和手续费信息。
    支持多种订单号类型：订单号、收单号、支付流水号等。

    Args:
        order_no: 订单号。必填。支持订单号、收单号、支付流水号等。
    """
    # v1 版本使用 /dispatcher/ 前缀
    # API: pay.assetcenter.queryPayInfoList（前端源码 payment-info-query.js 第1425行）
    url = f"{BASE_URL}/dispatcher/pay.assetcenter.queryPayInfoList"

    # 前端使用 singleParam 字符串参数（sentData 直接传字符串，会被 dispatcher 包装）
    payload = {
        "singleParam": order_no
    }

    return client.post(url, payload)
