"""
网关API详情查询 — 网关API详情查询
来源：schemas/网关域/v1_网关编辑.json
注意：该 Schema 文件名含"编辑"，但其核心接口为 gateway.admin.api.query（详情查询），
     页面加载时调用以获取指定 API 的完整配置，属于查询类功能。
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：schemas/网关域/v1_网关编辑.json）
PARAM_SCHEMA = {
    "apiId": {
        "type": "string",
        "required": True,
        "description": "网关API的ID（从网关列表页点击编辑时通过路由参数 params.apiId 传入）"
    },
}

# 数据展示列（来源：schemas/网关域/v1_网关编辑.json display，detail 类型，多 section）
# 返回结构为多段详情，各 section 字段定义如下：
DISPLAY_SECTIONS = [
    {
        "section": "API基本信息（apiBaseInfoVO）",
        "fields": [
            {"title": "java类全名",   "dataIndex": "apiBaseInfoVO.interfaceName"},
            {"title": "java方法名",   "dataIndex": "apiBaseInfoVO.method"},
            {"title": "对外service",  "dataIndex": "apiBaseInfoVO.service"},
            {"title": "对外method",   "dataIndex": "apiBaseInfoVO.method"},
            {"title": "应用名称",     "dataIndex": "apiBaseInfoVO.applicationName"},
            {"title": "版本",         "dataIndex": "apiBaseInfoVO.version"},
            {"title": "Owner",        "dataIndex": "apiBaseInfoVO.owner"},
            {"title": "描述",         "dataIndex": "apiBaseInfoVO.description"},
            {"title": "是否对外开放", "dataIndex": "apiBaseInfoVO.open"},
            {"title": "Session校验",  "dataIndex": "apiBaseInfoVO.needSession"},
            {"title": "入参日志",     "dataIndex": "apiBaseInfoVO.inputLog"},
            {"title": "出参日志",     "dataIndex": "apiBaseInfoVO.outputLog"},
            {"title": "ApiId",        "dataIndex": "apiBaseInfoVO.apiId"},
        ],
    },
    {
        "section": "入参列表（apiParamInfoVOS[]）",
        "fields": [
            {"title": "对外变量名", "dataIndex": "outerParamName"},
            {"title": "对内变量名", "dataIndex": "paramName"},
            {"title": "参数类型",   "dataIndex": "paramType"},
            {"title": "位置",       "dataIndex": "pos"},
            {"title": "描述",       "dataIndex": "description"},
        ],
    },
    {
        "section": "类型信息（apiTypeInfoVOS[]）",
        "fields": [
            {"title": "类型全名", "dataIndex": "typeName"},
            {"title": "名称",     "dataIndex": "name"},
            {"title": "字段信息", "dataIndex": "apiFieldInfoVOS"},
        ],
    },
    {
        "section": "映射关系（transferFieldMapVOS[]）",
        "fields": [
            {"title": "转换类型",         "dataIndex": "transferType"},
            {"title": "源字段类型",       "dataIndex": "srcFieldType"},
            {"title": "对内源字段名",     "dataIndex": "innerSrcFieldName"},
            {"title": "对外源字段名",     "dataIndex": "outerSrcFieldName"},
            {"title": "目的字段上级类型", "dataIndex": "superClassName"},
            {"title": "对内目的字段名",   "dataIndex": "innerDstFieldName"},
            {"title": "上级类型字段名",   "dataIndex": "superFieldName"},
        ],
    },
    {
        "section": "返回类型（apiReturnTypeInfoVO）",
        "fields": [
            {"title": "返回类型名", "dataIndex": "apiReturnTypeInfoVO.typeName"},
            {"title": "备注",       "dataIndex": "apiReturnTypeInfoVO.desc"},
        ],
    },
    {
        "section": "返回类型详情（returnTypeInfoVOS[]）",
        "fields": [
            {"title": "类型全名", "dataIndex": "typeName"},
            {"title": "备注",     "dataIndex": "desc"},
            {"title": "字段信息", "dataIndex": "fieldsInfoVOS"},
        ],
    },
]

# DISPLAY_COLUMNS 保留为空列表，详情结构见 DISPLAY_SECTIONS
DISPLAY_COLUMNS = []


def execute(
    api_id: str,
) -> dict:
    """查询网关API完整配置详情。
    返回指定网关API的基本信息、入参列表、类型信息、映射关系及返回类型等完整配置。

    Args:
        api_id: 网关API的ID。必填。可从 query_gateway_list 的返回结果中获取 apiId 字段。
    """
    url = f"{BASE_URL}/dispatcher/gateway.admin.api.query"

    payload: dict = {
        "apiId": api_id,
    }

    return client.post(url, payload)
