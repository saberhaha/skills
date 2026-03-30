"""
GHT出款记录查询 (v2)
来源：schemas/账务域/v2_GHT出款.json
"""
import sys
import os
from datetime import datetime
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "merchantNo": {
        "type": "string", "required": False,
        "description": "商户号（下拉选择，默认为 MchList 第一个商户号）"
    },
    "instructionId": {"type": "string", "required": False, "description": "提现流水号"},
    "status": {
        "type": "enum", "required": False,
        "enum_values": {
            "0": "申请中", "1": "申请成功", "2": "申请失败", "3": "提现处理中",
            "4": "风控拦截", "5": "提现异常转人工处理", "6": "提现失败", "7": "提现成功"
        },
        "description": "提现状态"
    },
    "startTime": {
        "type": "string", "format": "YYYY-MM-DD HH:mm:ss",
        "required": False, "default": "today_00:00:00",
        "description": "提现申请开始时间（默认当天 00:00:00）"
    },
    "endTime": {
        "type": "string", "format": "YYYY-MM-DD HH:mm:ss",
        "required": False, "default": "today_23:59:59",
        "description": "提现申请结束时间（默认当天 23:59:59）"
    },
    "gmtStartTime": {
        "type": "string", "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "提现完成开始时间"
    },
    "gmtEndTime": {
        "type": "string", "format": "YYYY-MM-DD HH:mm:ss",
        "required": False,
        "description": "提现完成结束时间"
    },
    "accountType": {
        "type": "string", "required": True, "default": "10",
        "description": "账户余额类型（固定传 '10'）"
    },
    "currentPage": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "提现流水号", "dataIndex": "withdrawNo"},
    {"title": "提现金额(元)", "dataIndex": "withdrawAmount"},
    {"title": "商户号", "dataIndex": "merchantNo"},
    {"title": "提现账号", "dataIndex": "instAccountNo"},
    {"title": "提现账户名称", "dataIndex": "instAccountName"},
    {"title": "提现账户类型", "dataIndex": "instAccountType"},
    {"title": "提现状态", "dataIndex": "statusDesc"},
    {"title": "提现操作人", "dataIndex": "adminName"},
    {"title": "提现申请时间", "dataIndex": "applyTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "提现完成时间", "dataIndex": "finishTime", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "备注", "dataIndex": "memo"}
]


def execute(
    merchant_no: Optional[str] = None,
    instruction_id: Optional[str] = None,
    status: Optional[Literal[0, 1, 2, 3, 4, 5, 6, 7]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    gmt_start_time: Optional[str] = None,
    gmt_end_time: Optional[str] = None,
    current_page: int = 1,
    page_size: int = 10,
) -> dict:
    """GHT出款记录查询（v2）
    查询 GHT 出款记录列表，支持按商户号、流水号、状态及时间范围查询。
    默认查询当天申请记录。

    Args:
        merchant_no: 商户号。可选。
        instruction_id: 提现流水号。可选。
        status: 提现状态。可选。枚举：0=申请中,1=申请成功,2=申请失败,3=提现处理中,
                4=风控拦截,5=提现异常转人工处理,6=提现失败,7=提现成功。
        start_time: 提现申请开始时间。可选。格式 YYYY-MM-DD HH:mm:ss。默认当天 00:00:00。
        end_time: 提现申请结束时间。可选。格式 YYYY-MM-DD HH:mm:ss。默认当天 23:59:59。
        gmt_start_time: 提现完成开始时间。可选。格式 YYYY-MM-DD HH:mm:ss。
        gmt_end_time: 提现完成结束时间。可选。格式 YYYY-MM-DD HH:mm:ss。
        current_page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/assetcenter.withdraw.list"

    now = datetime.now()
    # 默认值：当天 00:00:00 / 23:59:59（来源 Schema default）
    default_start = now.strftime("%Y-%m-%d 00:00:00")
    default_end = now.strftime("%Y-%m-%d 23:59:59")

    payload = {
        "currentPage": current_page,
        "pageSize": page_size,
        "accountType": "10",  # 固定值
        "startTime": start_time if start_time else default_start,
        "endTime": end_time if end_time else default_end
    }
    if merchant_no:
        payload["merchantNo"] = merchant_no
    if instruction_id:
        payload["instructionId"] = instruction_id
    if status is not None:
        payload["status"] = status
    if gmt_start_time:
        payload["gmtStartTime"] = gmt_start_time
    if gmt_end_time:
        payload["gmtEndTime"] = gmt_end_time

    return client.post(url, payload)


def get_acct_info(
    user_no: str,
    acct_type: int = 10,
) -> dict:
    """查询账户余额信息（辅助查询）
    用于出款前查询账户余额，展示在出款操作表单中。

    Args:
        user_no: 商户号。必填。
        acct_type: 账户类型。固定传 10。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.account.getAcctInfo"
    payload = {
        "userNo": user_no,
        "acctType": acct_type
    }
    return client.post(url, payload)


def get_bindcard(
    user_no: str,
) -> dict:
    """查询账户绑定银行卡列表（辅助查询）
    用于出款操作时选择收款银行卡下拉列表。

    Args:
        user_no: 商户号。必填。
    """
    url = f"{BASE_URL}/dispatcher/youzan.pay.customer.api.bankcardservice.getbindcard"
    payload = {
        "userNo": user_no
    }
    return client.post(url, payload)
