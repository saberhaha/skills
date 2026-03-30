"""
大客套餐有赞担保5W封顶列表查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "kdtId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺ID（筛选条件）"
    },
    "mchId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "商户ID（筛选条件）"
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

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "商户ID", "dataIndex": "mchId"},
    {"title": "套餐版本", "dataIndex": "version"},
    {"title": "时间段", "dataIndex": "range", "note": "由effectTime和expireTime拼接，format: YYYY-MM-DD 至 YYYY-MM-DD"},
    {"title": "备注", "dataIndex": "remark"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
]

def execute(
    kdt_id: Optional[str] = None,
    mch_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """大客套餐有赞担保5W封顶列表查询
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        kdt_id: 店铺ID。可选。筛选条件。默认为空。
        mch_id: 商户ID。可选。筛选条件。默认为空。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.fee.feeStrategy.queryGuaranteeStrategy"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "kdtId": kdt_id if kdt_id is not None else "",
        "mchId": mch_id if mch_id is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
