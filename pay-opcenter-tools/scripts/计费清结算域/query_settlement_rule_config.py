"""
结算规则配置列表查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Literal
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "mchId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "服务商商户号（筛选条件）"
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 枚举定义（来源：Schema 中的 enums）
ENUM_SETTLE_TYPE = {"1": "实时结算", "2": "担保结算"}
ENUM_IN_OUT_TYPE = {"1": "收入", "2": "支出"}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "服务商商户号", "dataIndex": "userNo"},
    {"title": "结算类型", "dataIndex": "settleType", "note": "枚举: 1=实时结算, 2=担保结算"},
    {"title": "结算账户类型", "dataIndex": "accountTypeDesc"},
    {"title": "收入/支出", "dataIndex": "inOut", "note": "枚举: 1=收入, 2=支出"},
    {"title": "产品类型", "dataIndex": "bizProd", "note": "显示: bizProdDesc(bizProd)"},
    {"title": "业务模式", "dataIndex": "bizModel", "note": "显示: bizModelDesc(bizModel)"},
    {"title": "动作", "dataIndex": "bizTotalType", "note": "显示: bizTotalTypeDesc(bizTotalType)"},
    {"title": "支付工具", "dataIndex": "bizType", "note": "显示: bizTypeDesc(bizType)"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
]

def execute(
    mch_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """结算规则配置列表查询
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        mch_id: 服务商商户号。可选。筛选条件。默认为空。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.clearing.clear.getSettleRule"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "mchId": mch_id if mch_id is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
