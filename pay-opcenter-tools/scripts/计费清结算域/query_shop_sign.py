"""
店铺计费包签约列表查询
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Literal
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
# 每个字段记录：类型、格式、枚举值、默认值、业务含义
PARAM_SCHEMA = {
    "kdtId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺ID"
    },
    "mchId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "商户ID"
    },
    "packNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "计费包编号（下拉选择，数据来自selectPackNoList辅助接口）"
    },
    "state": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {"1": "生效", "2": "过期", "4": "待审核"},
        "description": "签约状态（空=全部）"
    },
    "userName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "操作人"
    },
    "operateStartTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "default": "",
        "description": "操作开始时间（从RangePicker选取，拼接 00:00:00）"
    },
    "operateEndTime": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "default": "",
        "description": "操作结束时间（从RangePicker选取，拼接 23:59:59）"
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

# 枚举定义（来源：Schema 中的 enum_values）
ENUM_STATE = {"1": "生效", "2": "过期", "4": "待审核"}

# 数据展示列（来源：步骤 1.2 提取的前端 columns / 信息字段）
DISPLAY_COLUMNS = [
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "商户ID", "dataIndex": "mchId"},
    {"title": "计费包", "dataIndex": "packName", "note": "渲染: packNo(packName)，链接跳转到 /v3/page/billingRuleConfig?packNo=xxx"},
    {"title": "生效时间段", "dataIndex": "timeRange", "format": "YYYY-MM-DD 至 YYYY-MM-DD", "note": "后端返回预格式化字符串"},
    {"title": "操作人", "dataIndex": "createUser"},
    {"title": "操作时间", "dataIndex": "updateTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "生效人", "dataIndex": "verifyUser"},
    {"title": "生效时间", "dataIndex": "beginEffectTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "备注", "dataIndex": "remark"}
]

def execute(
    kdt_id: Optional[str] = None,
    mch_id: Optional[str] = None,
    pack_no: Optional[str] = None,
    state: Optional[Literal["1", "2", "4"]] = None,
    user_name: Optional[str] = None,
    operate_start_time: Optional[str] = None,
    operate_end_time: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """店铺计费包签约列表查询
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        kdt_id: 店铺ID。可选。默认为空。
        mch_id: 商户ID。可选。默认为空。
        pack_no: 计费包编号。可选。下拉选择。默认为空。
        state: 签约状态。可选。枚举: 1=生效, 2=过期, 4=待审核。空=全部。默认为空。
        user_name: 操作人。可选。默认为空。
        operate_start_time: 操作开始时间。可选。格式: YYYY-MM-DD HH:mm:ss。默认为空。
        operate_end_time: 操作结束时间。可选。格式: YYYY-MM-DD HH:mm:ss。默认为空。
        page: 页码。可选。默认=1。
        page_size: 每页条数。可选。默认=10。
    """

    url = f"{BASE_URL}/dispatcher/pay.fee.mch.signOps.queryKdtSignList"

    # 默认值还原（来源：步骤 1.2 Schema 中的 default）
    payload = {
        "kdtId": kdt_id if kdt_id is not None else "",
        "mchId": mch_id if mch_id is not None else "",
        "packNo": pack_no if pack_no is not None else "",
        "state": state if state is not None else "",
        "userName": user_name if user_name is not None else "",
        "operateStartTime": operate_start_time if operate_start_time is not None else "",
        "operateEndTime": operate_end_time if operate_end_time is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    return client.post(url, payload)
