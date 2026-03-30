"""
内部对账-平台 — v3 内部对账平台页面
来源：schemas/对账域/v3_内部对账_平台.json

# TODO: 该页面为占位页面，无独立查询接口，无法通过 API 调用获取数据。
# Schema 标注：api = [UNRESOLVED: 占位页面无独立查询接口]
# 本文件保留为占位 Skill，如后续补充接口请人工更新。
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

PARAM_SCHEMA = {}

DISPLAY_COLUMNS = []


def execute() -> dict:
    """内部对账-平台（v3）- 该页面为平台级占位页面，当前无独立查询接口。

    Returns:
        提示信息字典。
    """
    # TODO: 源码未找到独立查询接口，需人工补全
    return {
        "error": "内部对账-平台页面暂无独立查询接口，请直接访问运营平台页面查看。",
        "page_url": f"{BASE_URL}/check-web/inner/platform"
    }
