"""
计费规则配置列表查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "packNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "服务包编号（支持URL参数packNo传入，也可在筛选区手动输入）"
    },
    "page": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码（从Store.getPageInfo获取）"
    },
    "pageSize": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数（从Store.getPageInfo获取）"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "服务包编号", "dataIndex": "packNo"},
    {"title": "服务包名称", "dataIndex": "packName"},
    {"title": "收费类型", "dataIndex": "feeTypeDesc"},
    {"title": "生效时间", "dataIndex": "range", "note": "由effectTime和expireTime拼接，format: YYYY-MM-DD 至 YYYY-MM-DD"},
    {"title": "费率", "dataIndex": "ratio", "note": "format(value, true, false) + '%'，无值显示'0.00%'"},
    {"title": "费率补贴", "dataIndex": "ratioSubsidy", "note": "format(value, true, false) + '%'，无值显示'0.00%'"},
    {"title": "交易下限金额(元)", "dataIndex": "amountLower", "note": "zan-utils/money/format，无值显示'0.00'"},
    {"title": "交易上限金额(元)", "dataIndex": "amountUpper", "note": "zan-utils/money/format，无值显示'0.00'"},
    {"title": "最低收费金额(元)", "dataIndex": "feeMin", "note": "zan-utils/money/format，无值显示'0.00'"},
    {"title": "最高收费金额(元)", "dataIndex": "feeMax", "note": "zan-utils/money/format，无值显示'0.00'"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
]

def execute(
    pack_no: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """计费规则配置列表查询
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        pack_no: 服务包编号。可选。支持URL参数packNo传入，也可在筛选区手动输入。默认为空。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.fee.pack.getFeePackageDetail"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "packNo": pack_no if pack_no is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
