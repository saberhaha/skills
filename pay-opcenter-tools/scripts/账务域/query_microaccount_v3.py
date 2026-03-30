"""
预存款账户查询 (v3)
来源：schemas/账务域/v3_预存款账户查询.json
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "mchId": {
        "type": "string", "required": False,
        "description": "预存金专户所属商户号（和 kdtId 不能同时为空，默认按 mchId 查询）"
    },
    "kdtId": {
        "type": "string", "required": False,
        "description": "预存金专户所属店铺号（和 mchId 不能同时为空）"
    },
    "beginTime": {
        "type": "string", "format": "YYYY-MM-DD HH:mm:ss",
        "required": False, "default": "now-7d",
        "description": "调整开始时间（默认近7天前 00:00:00）"
    },
    "endTime": {
        "type": "string", "format": "YYYY-MM-DD HH:mm:ss",
        "required": False, "default": "today_00:00:00",
        "description": "调整结束时间（默认当天 00:00:00）"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = {
    "list": [
        {"title": "商户号", "dataIndex": "mchId"},
        {"title": "账户类型", "dataIndex": "_hardcoded"},
        {"title": "资金账号", "dataIndex": "cardNo"},
        {"title": "调整方式", "dataIndex": "bizType"},
        {"title": "金额（元）", "dataIndex": "adjustmentBonus"},
        {"title": "申请人", "dataIndex": "operator"},
        {"title": "申请时间", "dataIndex": "createTime", "format": "YYYY-MM-DD HH:mm:ss"},
        {"title": "结果", "dataIndex": "status"}
    ],
    "microacct": [
        {"title": "预存金专户号", "dataIndex": "cardNo"}
    ]
}


def execute(
    mch_id: Optional[str] = None,
    kdt_id: Optional[str] = None,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """预存款账户查询（v3）
    查询预存金调账记录列表，同时查询预存金专户号信息。
    mch_id 和 kdt_id 至少提供一个。

    Args:
        mch_id: 商户号。可选（和 kdt_id 至少填一个）。
        kdt_id: 店铺号。可选（和 mch_id 至少填一个）。
        begin_time: 调整开始时间。可选。格式 YYYY-MM-DD HH:mm:ss。默认近7天前 00:00:00。
        end_time: 调整结束时间。可选。格式 YYYY-MM-DD HH:mm:ss。默认当天 00:00:00。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    if not mch_id and not kdt_id:
        return {"error": "mchId 和 kdtId 不能同时为空，至少提供一个。"}

    now = datetime.now()
    # 默认值：近7天前 00:00:00 / 当天 00:00:00（来源 Schema default）
    default_begin = (now - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    default_end = now.strftime("%Y-%m-%d 00:00:00")

    # 接口1：分页查询预存金调账记录（GET）
    list_url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.microacct.adjustquery"
    list_payload = {
        "page": page,
        "pageSize": page_size,
        "beginTime": begin_time if begin_time else default_begin,
        "endTime": end_time if end_time else default_end
    }
    if mch_id:
        list_payload["mchId"] = mch_id
    if kdt_id:
        list_payload["kdtId"] = kdt_id

    list_res = client.get(list_url, params=list_payload)

    # 接口2：预存金专户号查询（POST）
    acct_url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.microacct.query"
    acct_payload = {}
    if mch_id:
        acct_payload["mchId"] = mch_id
    if kdt_id:
        acct_payload["kdtId"] = kdt_id

    acct_res = client.post(acct_url, acct_payload)

    return {
        "adjustQueryList": list_res,
        "microAcctInfo": acct_res
    }
