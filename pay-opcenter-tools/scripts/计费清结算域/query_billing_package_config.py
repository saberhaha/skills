"""
商户收费包配置列表查询
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

# 枚举定义（来源：Schema 中的 enums）
ENUM_MCH_ROLE = {"1": "合作方", "2": "商户号"}
ENUM_STATUS = {"1": "启用", "2": "停用"}
ENUM_WHITE_LIST_TYPE = {"1": "默认规则", "2": "优先规则"}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "商户ID", "dataIndex": "mchId"},
    {"title": "商户角色", "dataIndex": "mchRoleDesc"},
    {"title": "收费包编号", "dataIndex": "packNo", "note": "渲染为链接，跳转到计费规则配置页面 /v3/page/billingRuleConfig?packNo=xxx"},
    {"title": "启用/停用", "dataIndex": "stateDesc"},
    {"title": "白名单类型", "dataIndex": "type", "note": "枚举: 1=默认规则, 2=优先规则"},
    {"title": "计费类型", "dataIndex": "feeTypeDesc"},
    {"title": "生效时间", "dataIndex": "range", "note": "由effectTime和expireTime拼接，format: YYYY-MM-DD 至 YYYY-MM-DD"},
    {"title": "更新时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"}
]

def execute(
    mch_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """商户收费包配置列表查询
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        mch_id: 商户ID。可选。筛选条件。默认为空。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.fee.mchConfigPack.getConfigPackList"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "mchId": mch_id if mch_id is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
