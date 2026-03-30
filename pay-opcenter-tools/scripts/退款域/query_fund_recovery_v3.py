"""
资金追回管理查询
来源：schemas/退款域/v3_资金追回管理.json
"""
import sys
import os
from typing import Optional, Literal
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "kdtId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺ID"
    },
    "kdtName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺名称"
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "订单编号"
    },
    "outBizNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "处置业务单"
    },
    "actionNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "追偿业务单"
    },
    "recoveryState": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "WAITED": "待追偿",
            "DISCARD": "已废弃",
            "BAD_DEBT": "挂坏账",
            "SUCCESS": "追偿成功",
        },
        "description": "追偿单状态（空字符串=全部）"
    },
    "bizType": {
        "type": "string",
        "required": False,
        # UNRESOLVED: 枚举值由后端 riskcase.fundshandling.oldquick.list.type.action 动态返回
        "description": "业务方（枚举值动态返回，无法静态枚举）"
    },
    "startDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "申请开始时间（格式：YYYY-MM-DD HH:mm:ss）"
    },
    "endDate": {
        "type": "string",
        "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "申请结束时间（格式：YYYY-MM-DD HH:mm:ss）"
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
    },
    "desc": {
        "type": "boolean",
        "required": False,
        "description": "排序是否降序"
    },
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "追偿业务单", "dataIndex": "recoveryNo"},
    {"title": "店铺名称", "dataIndex": "kdtName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "订单编号", "dataIndex": "orderNo"},
    {"title": "订单状态", "dataIndex": "orderState"},
    {"title": "处置业务单", "dataIndex": "outBizNo"},
    {"title": "业务方", "dataIndex": "bizSystem"},
    {"title": "待追偿金额", "dataIndex": "recoveryAmount"},
    {"title": "追偿业务单状态", "dataIndex": "recoveryState"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    kdt_id: Optional[str] = None,
    kdt_name: Optional[str] = None,
    order_no: Optional[str] = None,
    out_biz_no: Optional[str] = None,
    action_no: Optional[str] = None,
    recovery_state: Optional[Literal["WAITED", "DISCARD", "BAD_DEBT", "SUCCESS"]] = None,
    biz_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    desc: Optional[bool] = None,
) -> dict:
    """查询资金追回管理列表（v3）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        kdt_id: 店铺ID。可选。
        kdt_name: 店铺名称。可选。
        order_no: 订单编号。可选。
        out_biz_no: 处置业务单。可选。
        action_no: 追偿业务单。可选。
        recovery_state: 追偿单状态。可选。枚举：WAITED=待追偿, DISCARD=已废弃, BAD_DEBT=挂坏账, SUCCESS=追偿成功。空=全部。
        biz_type: 业务方。可选。枚举值由后端动态返回，无法静态枚举。
        start_date: 申请开始时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        end_date: 申请结束时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        desc: 排序是否降序。可选。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/compensate.center.queryHandlingRecoveryInfos"

    payload = {
        "kdtId": kdt_id if kdt_id is not None else "",
        "kdtName": kdt_name if kdt_name is not None else "",
        "orderNo": order_no if order_no is not None else "",
        "outBizNo": out_biz_no if out_biz_no is not None else "",
        "actionNo": action_no if action_no is not None else "",
        "recoveryState": recovery_state if recovery_state is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    if biz_type is not None:
        payload["bizType"] = biz_type
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date
    if desc is not None:
        payload["desc"] = desc

    return client.post(url, payload)
