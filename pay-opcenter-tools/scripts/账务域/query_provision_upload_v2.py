"""
备付金上传记录查询 (v2)
来源：schemas/账务域/v2_备付金核对与文件.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "channelType": {
        "type": "enum", "required": False, "default": " ",
        "enum_values": {" ": "全部", "1": "银联备付金", "2": "网联备付金"},
        "description": "渠道类型（默认空格字符串=全部）"
    },
    "uploadDate": {
        "type": "string", "format": "unix_timestamp_s",
        "required": False,
        "description": "上传日期（秒级unix时间戳的字符串形式）"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "渠道类型", "dataIndex": "channelType"},
    {"title": "上传日期", "dataIndex": "uploadDate", "format": "YYYY-MM-DD"},
    {"title": "批次号", "dataIndex": "seq"},
    {"title": "校验结果", "dataIndex": "result"},
    {"title": "操作人", "dataIndex": "operator"}
]


def execute(
    channel_type: Literal[" ", "1", "2"] = " ",
    upload_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """备付金上传记录查询（v2）
    查询备付金核对文件的上传记录列表。

    Args:
        channel_type: 渠道类型。枚举：" "=全部,"1"=银联备付金,"2"=网联备付金。默认 " "。
        upload_date: 上传日期。可选。需传秒级unix时间戳的字符串形式（如 "1741824000"）。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.pcp.generate.queryAll"

    # 前端使用 Number(channelType) 转换，空格字符串转为 0
    channel_type_num = 0 if channel_type == " " else int(channel_type)

    payload = {
        "channelType": channel_type_num,
        "page": page,
        "pageSize": page_size
    }
    if upload_date:
        payload["uploadDate"] = upload_date

    return client.post(url, payload)
