"""
用户信息列表查询 — 用户信息列表查询
来源：schemas/商户域/v3_用户信息查询.json
"""
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "userName": {
        "type": "string",
        "required": False,
        "description": "用户姓名（中文或拼音）"
    },
    "phone": {
        "type": "string",
        "required": False,
        "description": "手机号（合规平台必须输入phone或memId）"
    },
    "paperNo": {
        "type": "string",
        "required": False,
        "description": "证件号（数字或字母）"
    },
    "memId": {
        "type": "string",
        "required": False,
        "description": "会员号（数字）"
    },
    "currentPage": {
        "type": "number",
        "required": False,
        "default": 1,
        "description": "页码"
    },
    "size": {
        "type": "number",
        "required": False,
        "default": 10,
        "description": "每页条数"
    }
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "用户姓名", "dataIndex": "userName"},
    {"title": "手机号", "dataIndex": "phone"},
    {"title": "证件类型", "dataIndex": "paperType"},
    {"title": "证件号", "dataIndex": "paperNo"},
    {"title": "证件有效期", "dataIndex": "validTime"},
    {"title": "性别", "dataIndex": "sex"},
    {"title": "职业", "dataIndex": "profession"},
    {"title": "住址", "dataIndex": "address"},
    {"title": "国籍", "dataIndex": "nationality"},
    {"title": "会员号", "dataIndex": "memId"},
    {"title": "账户状态", "dataIndex": "accountStatus"},
    {"title": "账户等级", "dataIndex": "accountLevel"},
    {"title": "业务来源", "dataIndex": "bizSource"},
    {"title": "开户时间", "dataIndex": "openTime"},
    {"title": "开通业务", "dataIndex": "openBiz"},
]


def execute(
    user_name: Optional[str] = None,
    phone: Optional[str] = None,
    paper_no: Optional[str] = None,
    mem_id: Optional[str] = None,
    current_page: int = 1,
    size: int = 10,
) -> dict:
    """用户信息列表查询（v3）
    查询用户信息列表，支持按姓名、手机号、证件号、会员号筛选。
    合规平台要求必须输入手机号或会员号之一。

    Args:
        user_name: 用户姓名。可选。中文或拼音。
        phone: 手机号。可选（合规平台必填之一）。
        paper_no: 证件号。可选。
        mem_id: 会员号。可选（合规平台必填之一）。
        current_page: 页码。可选。默认=1。
        size: 每页条数。可选。默认=10。
    """
    url = f"{BASE_URL}/v3/api/dispatch/invoke/pay.user.info.op.search"

    # filterParams 过滤空值
    payload = {k: v for k, v in {
        "userName": user_name,
        "phone": phone,
        "paperNo": paper_no,
        "memId": mem_id,
        "currentPage": current_page,
        "size": size,
    }.items() if v is not None and v != ""}

    return client.post(url, payload)
