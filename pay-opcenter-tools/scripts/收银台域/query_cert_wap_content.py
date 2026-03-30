"""
页面证书WAP编辑内容查询 — 查询页面证书WAP编辑内容
来源：schemas/收银台域/v3_页面证书WAP编辑内容查询.json
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：v3_页面证书WAP编辑内容查询.json）
PARAM_SCHEMA = {
    "id": {
        "type": "string",
        "required": True,
        "description": "页面记录ID（IPageData.id，从页面证书列表获取）"
    },
}

# 数据展示列（来源：v3_页面证书WAP编辑内容查询.json → display）
# 返回结构为 ICompConfig={form:object, list:ICompData[], navBarConfig:any}
# 为页面编辑器组件配置，非标准列表列
# [UNRESOLVED: 返回结构为ICompConfig，为页面编辑器组件配置，非标准列表列，请人工补全展示字段]
DISPLAY_COLUMNS = []


def execute(
    page_id: str,
) -> dict:
    """查询页面证书WAP编辑内容
    根据页面记录ID查询WAP编辑器的组件配置（form/list/navBarConfig）。

    Args:
        page_id: 页面记录ID。必填。从页面证书列表（query_cert_manage_pages）中获取 id 字段。
    """
    url = f"{BASE_URL}/v3/api/cert-manage/page/content"
    params = {"id": page_id}
    return client.get(url, params)
