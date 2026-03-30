"""
资金处置管理查询
来源：schemas/退款域/v3_资金处置管理.json
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
    "caseType": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "有赞担保维权争议赔付": "有赞担保维权争议赔付",
            "有赞担保运费争议补偿": "有赞担保运费争议补偿",
            "多平台维权争议仲裁": "多平台维权争议仲裁",
            "有赞维权争议仲裁": "有赞维权争议仲裁",
            "平台体验赔付": "平台体验赔付",
            "有赞有责赔付": "有赞有责赔付",
            "舆情风险赔付": "舆情风险赔付",
            "多平台维权争议赔付": "多平台维权争议赔付",
        },
        "description": "业务方（空字符串=全部）"
    },
    "fundsHandlingStatus": {
        "type": "enum",
        "required": False,
        "default": "",
        "enum_values": {
            "WAITED": "待处置",
            "SUCCESS": "处置成功",
            "DISCARD": "已废弃",
        },
        "description": "业务单状态（空字符串=全部）"
    },
    "kdtId": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺ID"
    },
    "orderNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "订单编号"
    },
    "shopName": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "店铺名称"
    },
    "actionNo": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "业务单号"
    },
    "payerMch": {
        "type": "string",
        "required": False,
        "default": "",
        "description": "出金账户"
    },
    "amountMin": {
        "type": "number",
        "required": False,
        "description": "金额下限（元，提交时转换为分）"
    },
    "amountMax": {
        "type": "number",
        "required": False,
        "description": "金额上限（元，提交时转换为分）"
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
    {"title": "业务单号", "dataIndex": "handlingNo"},
    {"title": "店铺名称", "dataIndex": "shopName"},
    {"title": "店铺ID", "dataIndex": "kdtId"},
    {"title": "订单编号", "dataIndex": "orderNo"},
    {"title": "订单状态", "dataIndex": "eStatus"},
    {"title": "业务方", "dataIndex": "caseType"},
    {"title": "出金账户", "dataIndex": "depositAccount"},
    {"title": "金额", "dataIndex": "amount"},
    {"title": "目标账户", "dataIndex": "targetAccount"},
    {"title": "业务单状态", "dataIndex": "fundsHandlingStatus"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
]


def execute(
    case_type: Optional[Literal[
        "有赞担保维权争议赔付",
        "有赞担保运费争议补偿",
        "多平台维权争议仲裁",
        "有赞维权争议仲裁",
        "平台体验赔付",
        "有赞有责赔付",
        "舆情风险赔付",
        "多平台维权争议赔付",
    ]] = None,
    funds_handling_status: Optional[Literal["WAITED", "SUCCESS", "DISCARD"]] = None,
    kdt_id: Optional[str] = None,
    order_no: Optional[str] = None,
    shop_name: Optional[str] = None,
    action_no: Optional[str] = None,
    payer_mch: Optional[str] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    desc: Optional[bool] = None,
) -> dict:
    """查询资金处置管理列表（v3）。
    用户只需提供核心查询条件，其余参数自动使用页面默认值。

    Args:
        case_type: 业务方。可选。枚举：有赞担保维权争议赔付, 有赞担保运费争议补偿, 多平台维权争议仲裁,
                   有赞维权争议仲裁, 平台体验赔付, 有赞有责赔付, 舆情风险赔付, 多平台维权争议赔付。空=全部。
        funds_handling_status: 业务单状态。可选。枚举：WAITED=待处置, SUCCESS=处置成功, DISCARD=已废弃。空=全部。
        kdt_id: 店铺ID。可选。
        order_no: 订单编号。可选。
        shop_name: 店铺名称。可选。
        action_no: 业务单号。可选。
        payer_mch: 出金账户。可选。
        amount_min: 金额下限（元）。可选。
        amount_max: 金额上限（元）。可选。
        start_date: 申请开始时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        end_date: 申请结束时间。格式：YYYY-MM-DD HH:mm:ss。可选。
        page: 页码。默认=1。
        page_size: 每页条数。默认=10。
        desc: 排序是否降序。可选。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/compensate.center.queryFundsHandlingInfos"

    payload = {
        "caseType": case_type if case_type is not None else "",
        "fundsHandlingStatus": funds_handling_status if funds_handling_status is not None else "",
        "kdtId": kdt_id if kdt_id is not None else "",
        "orderNo": order_no if order_no is not None else "",
        "shopName": shop_name if shop_name is not None else "",
        "actionNo": action_no if action_no is not None else "",
        "payerMch": payer_mch if payer_mch is not None else "",
        "page": page,
        "pageSize": page_size,
    }

    # 金额需要转换为分（乘以100）
    if amount_min is not None:
        payload["amountMin"] = int(amount_min * 100)
    if amount_max is not None:
        payload["amountMax"] = int(amount_max * 100)
    if start_date is not None:
        payload["startDate"] = start_date
    if end_date is not None:
        payload["endDate"] = end_date
    if desc is not None:
        payload["desc"] = desc

    return client.post(url, payload)
