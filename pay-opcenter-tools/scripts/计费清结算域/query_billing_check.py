"""
计费清结算对账查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "searchValue": {
        "type": "string",
        "required": True,
        "description": "收单号（直接作为sentData传递给两个API，即请求体就是这个字符串值）"
    }
}

# 数据展示列 - 合并对账表（来源：步骤 1.2 提取的前端 columns）
MERGED_TABLE_COLUMNS = [
    {"title": "收单号", "dataIndex": "acquireNo"},
    {"title": "手续费", "dataIndex": "serviceCharge"},
    {"title": "结算金额", "dataIndex": "settleCharge"},
    {"title": "交易金额", "dataIndex": "amount"}
]

# 数据展示列 - 清结算日志表（来源：步骤 1.2 提取的前端 columns）
CLEARING_LOG_COLUMNS = [
    {"title": "交易金额", "dataIndex": "dealAmount", "note": "源字段: tradeAmt"},
    {"title": "结算金额", "dataIndex": "settleAmount", "note": "源字段: settleAmt"},
    {"title": "外部流水号", "dataIndex": "outWaterNo"},
    {"title": "外部业务号", "dataIndex": "outBizNo"},
    {"title": "收单号", "dataIndex": "acquireNo", "note": "源字段: outTradeNo"},
    {"title": "状态", "dataIndex": "status"},
    {"title": "收入/支出", "dataIndex": "inOut"},
    {"title": "流水号", "dataIndex": "waterNo"}
]

# 数据展示列 - 计费明细表（来源：步骤 1.2 提取的前端 columns）
FEE_DETAIL_COLUMNS = [
    {"title": "收费账单号", "dataIndex": "feeNo"},
    {"title": "有赞商户号", "dataIndex": "mchId"},
    {"title": "合作方Id", "dataIndex": "partnerId"},
    {"title": "支付渠道", "dataIndex": "payChannel"},
    {"title": "服务包编号", "dataIndex": "packNo"},
    {"title": "产品交易识别码", "dataIndex": "packPdCode"},
    {"title": "收入/支出", "dataIndex": "inOut"},
    {"title": "套餐扣费费率(万几)", "dataIndex": "packRatio"},
    {"title": "扣费补贴费率(万几)", "dataIndex": "packRatioSubsidy"},
    {"title": "业务方交易识别码", "dataIndex": "bizPdCode"},
    {"title": "业务来源", "dataIndex": "bizSource"},
    {"title": "主业务单号", "dataIndex": "bizNo"},
    {"title": "子业务单号", "dataIndex": "subBizNo", "note": "源字段: bizSubNo"},
    {"title": "业务交易金额", "dataIndex": "bizAmount"},
    {"title": "收费类型", "dataIndex": "feeType"},
    {"title": "收费金额", "dataIndex": "feeAmount"},
    {"title": "收费补贴金额", "dataIndex": "feeAmountSubsidy"},
    {"title": "收费日期", "dataIndex": "feeDate"},
    {"title": "创建时间", "dataIndex": "createTime"},
    {"title": "扩展字段", "dataIndex": "extra", "note": "源字段: extension，JSON格式化展示"}
]

def execute(
    search_value: str,
) -> dict:
    """计费清结算对账查询
    根据收单号同时查询清结算日志和计费明细，返回关联合并结果。
    两个API使用相同的入参（收单号）串行调用，返回结果通过identify字段关联合并。

    Args:
        search_value: 收单号。必填。直接作为sentData传递给两个API。
    """

    # API 1: 清结算日志查询
    clearing_url = f"{BASE_URL}/dispatcher/pay.clearing.queryFundsClearingLog"

    # API 2: 计费明细查询
    fee_url = f"{BASE_URL}/dispatcher/pay.fee.queryFeeDetail"

    # 前端通过 Request.fetch 将 sentData 包装成 { singleParam: searchValue }
    payload = {"singleParam": search_value}

    clearing_result = client.post(clearing_url, payload)
    fee_result = client.post(fee_url, payload)

    return {
        "clearingLog": clearing_result,
        "feeDetail": fee_result,
        "note": "payClearing和payFee数据通过identify字段关联合并"
    }
