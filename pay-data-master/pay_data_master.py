#!/usr/bin/env python3
"""
pay-data-master 主入口
支付数据大师 - 理解支付业务语义，将自然语言转化为SQL查询

集成 zan-dp-platform 的全部能力 + 支付业务知识库

用法:
    # 查询模式 - 执行 SQL
    python3 pay_data_master.py query --sql "SELECT * FROM ods.pay_order LIMIT 10"

    # 搜索模式 - 按关键词搜索相关表
    python3 pay_data_master.py search --keyword "GMV"

    # 表信息 - 查看表详情
    python3 pay_data_master.py table --name dev.dm_all_pay_recharge_22_now

    # 自然语言 - 解析业务需求并生成 SQL
    python3 pay_data_master.py nl --text "查询店铺117301428的2026年PMV"

    # DP 平台能力 - 表结构、分区等
    python3 pay_data_master.py table-schema --db ods --table pay_order
    python3 pay_data_master.py table-columns --db dev --table dm_all_pay_recharge_22_now
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# 技能根目录
SKILL_DIR = Path(__file__).parent
DOMAIN_DIR = SKILL_DIR / "domain"
TABLES_JSON = DOMAIN_DIR / "tables.json"
CONCEPTS_JSON = DOMAIN_DIR / "concepts.json"
WORKFLOWS_DIR = SKILL_DIR / "workflows"
SCRIPTS_DIR = SKILL_DIR / "scripts"

# 导入 dp_client
sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from dp_client import DpClient
except ImportError:
    DpClient = None


def print_json(data):
    """美化打印 JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def load_json(filepath) -> dict:
    """加载 JSON 文件"""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_dp_client() -> Optional[DpClient]:
    """获取 DP 客户端"""
    if DpClient:
        return DpClient()
    return None


# ============================================================================
# 搜索功能
# ============================================================================

def search_tables(keyword: str) -> List[dict]:
    """搜索表知识库"""
    tables = load_json(TABLES_JSON)
    results = []
    keyword_lower = keyword.lower()

    for table_key, table_info in tables.items():
        search_text = f"{table_key} {table_info.get('name', '')} {table_info.get('description', '')}"
        for field in table_info.get('fields', []):
            if isinstance(field, dict):
                search_text += f" {field.get('column_name', '')} {field.get('comment', '')}"
            elif isinstance(field, str):
                search_text += f" {field}"

        if keyword_lower in search_text.lower():
            results.append({
                'table': table_key,
                'name': table_info.get('name', ''),
                'description': table_info.get('description', ''),
                'enums': list(table_info.get('enums', {}).keys())
            })

    return results


def search_concepts(keyword: str) -> List[dict]:
    """搜索概念知识库"""
    concepts = load_json(CONCEPTS_JSON)
    results = []
    keyword_lower = keyword.lower()

    for concept_key, concept_info in concepts.get('concepts', {}).items():
        search_text = f"{concept_key} {concept_info.get('name', '')} {concept_info.get('definition', '')}"
        if keyword_lower in search_text.lower():
            results.append({
                'type': 'concept',
                'key': concept_key,
                'name': concept_info.get('name', ''),
                'definition': concept_info.get('definition', '')
            })

    return results


def search_workflows(keyword: str) -> List[dict]:
    """搜索工作流"""
    results = []
    keyword_lower = keyword.lower()

    for workflow_file in WORKFLOWS_DIR.glob("*.json"):
        workflow = load_json(workflow_file)
        workflow_info = workflow.get('workflow', {})

        search_text = f"{workflow_info.get('name', '')} {workflow_info.get('description', '')} {workflow_info.get('pattern_type', '')}"
        if keyword_lower in search_text.lower():
            results.append({
                'file': workflow_file.stem,
                'name': workflow_info.get('name', ''),
                'description': workflow_info.get('description', ''),
                'pattern_type': workflow_info.get('pattern_type', ''),
                'steps': len(workflow_info.get('steps', [])) if 'steps' in workflow_info else 0
            })

    return results


def search_all(keyword: str) -> dict:
    """综合搜索"""
    return {
        'tables': search_tables(keyword),
        'concepts': search_concepts(keyword),
        'workflows': search_workflows(keyword)
    }


def get_table_info(table_name: str) -> Optional[dict]:
    """获取表详细信息"""
    tables = load_json(TABLES_JSON)
    return tables.get(table_name)


# ============================================================================
# 智能自然语言解析
# ============================================================================

def extract_params(text: str) -> dict:
    """从文本中提取参数"""
    params = {
        'kdt_id': None,
        'user_no': None,
        'year': None,
        'date_range': None,
        'offline_only': False,
        'online_only': False,
        'need_shop_info': False,
        'need_gmv': False,
        'need_pmv': False,
        'need_refund': False,
        'cert_category': None
    }

    text_lower = text.lower()

    # 提取 kdt_id
    kdt_match = re.search(r'kdt[_\s]?id[=:\s]*(\d+)', text_lower)
    if kdt_match:
        params['kdt_id'] = kdt_match.group(1)

    # 提取年份
    year_match = re.search(r'(\d{4})\s*年', text)
    if year_match:
        params['year'] = year_match.group(1)

    # 检测线上线下
    if '线下' in text:
        params['offline_only'] = True
    elif '线上' in text:
        params['online_only'] = True

    # 检测需求关键词
    if any(w in text for w in ['店铺信息', '店铺名称', 'team_name', 'hq_']):
        params['need_shop_info'] = True

    if 'gmv' in text_lower:
        params['need_gmv'] = True

    if 'pmv' in text_lower:
        params['need_pmv'] = True

    if '退款' in text:
        params['need_refund'] = True

    # 提取 cert_category
    if 'cert_category' in text_lower or '认证类目' in text:
        category_match = re.search(r'认证类目[：:]\s*([^\s，,]+)', text)
        if category_match:
            params['cert_category'] = category_match.group(1)

    return params


def match_workflow(text: str, params: dict) -> Optional[dict]:
    """匹配工作流模式"""
    workflows_data = []

    for workflow_file in WORKFLOWS_DIR.glob("*.json"):
        workflow = load_json(workflow_file)
        workflow_info = workflow.get('workflow', {})
        workflow_info['_file'] = workflow_file.stem
        workflows_data.append(workflow_info)

    # 按场景匹配

    # 场景1: 店铺 PMV 分析 + 店铺信息
    if params['kdt_id'] and params['need_pmv'] and params['need_shop_info']:
        for wf in workflows_data:
            if 'shop_pmv_analysis' in wf.get('id', '') or 'shop' in wf.get('name', '').lower():
                return {
                    'matched_workflow': wf.get('name'),
                    'workflow_file': wf.get('_file'),
                    'pattern': 'shop_pmv_with_info',
                    'explanation': '匹配到"店铺PMV分析"工作流，需要 JOIN 店铺信息表'
                }

    # 场景2: ID 转换
    if 'user_no' in text.lower() or '有赞商户号' in text:
        for wf in workflows_data:
            if 'id_conversion' in wf.get('id', ''):
                return {
                    'matched_workflow': wf.get('name'),
                    'workflow_file': wf.get('_file'),
                    'pattern': 'id_conversion',
                    'explanation': '匹配到"ID转换"工作流，需要通过 ods.pay_funds_user 转换'
                }

    # 场景3: 认证类目筛选
    if params['cert_category'] or 'cert_category' in text.lower():
        for wf in workflows_data:
            if 'category' in wf.get('id', '') or '类目' in wf.get('name', ''):
                return {
                    'matched_workflow': wf.get('name'),
                    'workflow_file': wf.get('_file'),
                    'pattern': 'category_filter',
                    'explanation': '匹配到"类目筛选"工作流'
                }

    return None


def nl_to_sql(text: str) -> dict:
    """自然语言转 SQL（智能实现）"""
    params = extract_params(text)

    # 1. 先匹配工作流
    workflow_match = match_workflow(text, params)

    if workflow_match:
        pattern = workflow_match['pattern']

        # 模式1: 店铺 PMV + 店铺信息
        if pattern == 'shop_pmv_with_info':
            kdt_id = params['kdt_id']
            year = params.get('year', '2026')

            offline_filter = "offline_tag = '线下'" if params['offline_only'] else ""
            online_filter = "offline_tag = '线上'" if params['online_only'] else ""

            sql = f"""SELECT
  a.kdt_id,
  a.team_name,
  a.hq_kdt_id,
  a.hq_team_name,
  a.shop_role_name,
  a.product,
  a.open_status_name,
  b.offline_tag,
  SUM(b.gmv_amount) / 100 AS gmv_yuan,
  SUM(b.pmv_amount) / 100 AS pmv_yuan
FROM dev.kk_mch_shop_info a
JOIN dev.dm_all_pay_recharge_22_now b ON a.kdt_id = b.kdt_id
WHERE a.kdt_id = {kdt_id}
  AND b.pay_day >= '{year}-01-01'"""

            if offline_filter:
                sql += f"\n  AND {offline_filter}"
            elif online_filter:
                sql += f"\n  AND {online_filter}"

            sql += "\nGROUP BY a.kdt_id, a.team_name, a.hq_kdt_id, a.hq_team_name, a.shop_role_name, a.product, a.open_status_name, b.offline_tag"
            sql += "\nLIMIT 1000"

            return {
                'detected_intent': 'shop_pmv_with_info',
                'matched_workflow': workflow_match['matched_workflow'],
                'params': params,
                'sql': sql,
                'explanation': workflow_match['explanation']
            }

        # 模式2: ID 转换
        if pattern == 'id_conversion':
            kdt_id = params['kdt_id']
            if kdt_id:
                # target_id 是 varchar 类型，需要加引号
                sql = f"SELECT user_no, target_id as kdt_id FROM ods.pay_funds_user WHERE type = 10 AND target_id = '{kdt_id}' LIMIT 1000"
                return {
                    'detected_intent': 'id_conversion',
                    'matched_workflow': workflow_match['matched_workflow'],
                    'params': params,
                    'sql': sql,
                    'explanation': '通过 ods.pay_funds_user 表将 kdt_id 转换为 user_no'
                }

    # 2. 兜底：简单关键词匹配

    # ID 转换
    if ('user_no' in text.lower() or '有赞商户号' in text) and params['kdt_id']:
        kdt_id = params['kdt_id']
        return {
            'detected_intent': 'id_conversion',
            'params': params,
            'sql': f"SELECT user_no, target_id as kdt_id FROM ods.pay_funds_user WHERE type = 10 AND target_id = '{kdt_id}' LIMIT 1000",
            'explanation': '检测到 kdt_id，需要通过 ods.pay_funds_user 表转换为 user_no'
        }

    # GMV/PMV 查询
    if params['need_gmv'] or params['need_pmv']:
        if params['kdt_id']:
            kdt_id = params['kdt_id']
            year = params.get('year', '2026')

            select_clauses = []
            if params['need_gmv']:
                select_clauses.append("SUM(gmv_amount) / 100 AS gmv_yuan")
            if params['need_pmv']:
                select_clauses.append("SUM(pmv_amount) / 100 AS pmv_yuan")

            sql = f"""SELECT
  kdt_id,
  offline_tag,
  {', '.join(select_clauses)}
FROM dev.dm_all_pay_recharge_22_now
WHERE kdt_id = {kdt_id}
  AND pay_day >= '{year}-01-01'
GROUP BY kdt_id, offline_tag
LIMIT 1000"""

            return {
                'detected_intent': 'shop_pmv_query',
                'params': params,
                'sql': sql,
                'explanation': f'查询店铺 {year} 年 GMV/PMV，按线上线下分组'
            }

    # 3. 默认：返回搜索建议
    return {
        'detected_intent': 'search_required',
        'params': params,
        'suggestion': '无法直接解析，尝试搜索相关资源',
        'search_results': search_all(text)
    }


# ============================================================================
# 工作流自动创建
# ============================================================================

def analyze_sql_for_workflow(sql: str, params: dict, text: str) -> dict:
    """分析 SQL 是否值得沉淀为工作流"""
    reasons = []
    score = 0

    # 检查是否涉及多表 JOIN (+2分)
    join_count = len(re.findall(r'\bJOIN\b', sql, re.IGNORECASE))
    if join_count > 0:
        reasons.append({
            'reason': 'multi_table_join',
            'description': f'涉及 {join_count} 个表 JOIN，表关联规则值得沉淀'
        })
        score += 2

    # 检查是否涉及特殊转换（如 ID 转换）(+2分)
    # 情况1: pay_funds_user + type=10（kdt_id与user_no转换）
    # 情况2: pay_funds_user 表参与 JOIN（ID 转换桥接表）
    # 情况3: mch_id/user_no/payee_id 等商户ID关联
    id_conversion_patterns = [
        ('pay_funds_user' in sql and 'type = 10' in sql, '涉及 ID 转换规则（type=10）'),
        ('pay_funds_user' in sql and re.search(r'\bJOIN\b', sql, re.IGNORECASE), '涉及 pay_funds_user ID 转换桥接表'),
        (re.search(r'mch_id\s*=\s*user_no|user_no\s*=\s*mch_id', sql, re.IGNORECASE), '涉及 mch_id 与 user_no 关联'),
        (re.search(r'payee_id\s*=\s*user_no|user_no\s*=\s*payee_id', sql, re.IGNORECASE), '涉及 payee_id 与 user_no 关联'),
    ]
    for pattern_match, pattern_desc in id_conversion_patterns:
        if pattern_match:
            reasons.append({
                'reason': 'id_conversion',
                'description': pattern_desc
            })
            score += 2
            break

    # 检查是否有复杂过滤条件 (+1分)
    conditions = len(re.findall(r'\bAND\b', sql, re.IGNORECASE))
    if conditions >= 2:
        reasons.append({
            'reason': 'complex_filter',
            'description': f'包含 {conditions} 个过滤条件'
        })
        score += 1

    # 检查是否涉及枚举值过滤 (+1分)
    enum_fields = ['offline_tag', 'gmv_type', 'cert_category', 'biz_type', 'product',
                   'wx_low_sub', 'alipay_low_sub', 'status', 'type', 'tag']
    for field in enum_fields:
        if field in sql:
            reasons.append({
                'reason': 'enum_filter',
                'description': f'涉及枚举字段 {field} 的过滤'
            })
            score += 1
            break

    # 检查是否涉及聚合计算 (+1分)
    if re.search(r'\bSUM\b|\bAVG\b|\bCOUNT\b', sql, re.IGNORECASE):
        reasons.append({
            'reason': 'aggregation',
            'description': '涉及聚合计算（SUM/AVG/COUNT）'
        })
        score += 1

    # 检查是否涉及时间范围过滤 (+1分)
    if re.search(r'pay_day|pay_month|create_time', sql):
        reasons.append({
            'reason': 'time_filter',
            'description': '涉及时间范围过滤'
        })
        score += 1

    # 判断是否值得沉淀（分数 >= 3）
    worth_saving = score >= 3

    return {
        'worth_saving': worth_saving,
        'score': score,
        'reasons': reasons,
        'recommendation': '建议沉淀为工作流' if worth_saving else '简单查询，无需沉淀'
    }


def extract_tables_from_sql(sql: str) -> List[str]:
    """从 SQL 中提取表名"""
    # 匹配 FROM table 和 JOIN table
    pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)'
    matches = re.findall(pattern, sql, re.IGNORECASE)
    return list(set(matches))


def generate_workflow_id(text: str, sql: str) -> str:
    """生成工作流 ID"""
    # 基于关键词生成 ID
    keywords = []

    if 'pmv' in text.lower():
        keywords.append('pmv')
    if 'gmv' in text.lower():
        keywords.append('gmv')
    if '退款' in text:
        keywords.append('refund')
    if '转换' in text or 'user_no' in text.lower():
        keywords.append('conversion')
    if '店铺' in text:
        keywords.append('shop')
    if '类目' in text or 'category' in text.lower():
        keywords.append('category')

    if keywords:
        return '_'.join(keywords) + '_pattern'

    # 基于 SQL 表名生成
    tables = extract_tables_from_sql(sql)
    if tables:
        # 取最后一个表名（通常是主表）
        main_table = tables[-1].split('.')[-1]
        return f"{main_table}_query"

    return 'custom_pattern'


def template_sql(sql: str, params: dict) -> str:
    """将 SQL 参数化，生成模板"""
    template = sql

    # 替换 kdt_id
    if params.get('kdt_id'):
        template = re.sub(
            r"kdt_id\s*=\s*['\"]?" + re.escape(params['kdt_id']) + r"['\"]?",
            "kdt_id = '{{kdt_id}}'",
            template
        )
        template = re.sub(
            r"target_id\s*=\s*['\"]?" + re.escape(params['kdt_id']) + r"['\"]?",
            "target_id = '{{kdt_id}}'",
            template
        )

    # 替换年份
    if params.get('year'):
        template = template.replace(f"'{params['year']}-01-01'", "'{{year}}-01-01'")
        template = template.replace(f"{params['year']}-01-01", "{{year}}-01-01")

    # 替换月份
    month_match = re.search(r"'(\d{4}-\d{2})'", sql)
    if month_match:
        template = template.replace(f"'{month_match.group(1)}'", "'{{pay_month}}'")

    return template


def create_workflow(text: str, sql: str, params: dict, analysis: dict) -> dict:
    """创建工作流定义"""
    import datetime

    workflow_id = generate_workflow_id(text, sql)
    tables = extract_tables_from_sql(sql)
    template = template_sql(sql, params)

    # 确定模式类型
    pattern_type = '单步查询模式'
    if len(tables) > 1:
        pattern_type = '多表关联模式'
    if 'pay_funds_user' in sql:
        pattern_type = '转换模式'

    workflow = {
        '_meta': {
            'description': f'自动生成的工作流：{text[:50]}...',
            'version': '1.0',
            'auto_generated': True,
            'created_at': datetime.datetime.now().isoformat()
        },
        'workflow': {
            'id': workflow_id,
            'name': text[:30] if len(text) > 30 else text,
            'description': text,
            'pattern_type': pattern_type,
            'business_scenario': text,
            'source_tables': tables,
            'analysis': analysis,
            'input': {},
            'output': {
                'fields': [],
                'unit': '元（金额字段已除以100）'
            },
            'sql_template': template,
            'key_concepts': {}
        }
    }

    # 提取输入参数
    if params.get('kdt_id'):
        workflow['workflow']['input']['kdt_id'] = {
            'description': '店铺ID',
            'required': True
        }
    if params.get('year'):
        workflow['workflow']['input']['year'] = {
            'description': '年份，如 2026',
            'default': '2026'
        }

    return workflow


def save_workflow(workflow: dict, filename: str = None) -> dict:
    """保存工作流到文件"""
    if filename is None:
        filename = workflow['workflow']['id']

    filepath = WORKFLOWS_DIR / f"{filename}.json"

    # 检查是否已存在
    if filepath.exists():
        return {
            'success': False,
            'message': f'工作流已存在: {filename}',
            'filepath': str(filepath)
        }

    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, ensure_ascii=False, indent=2)

    return {
        'success': True,
        'message': f'工作流已保存: {filename}',
        'filepath': str(filepath),
        'workflow_id': workflow['workflow']['id']
    }


def list_workflows() -> List[dict]:
    """列出所有工作流"""
    workflows = []
    for workflow_file in WORKFLOWS_DIR.glob("*.json"):
        workflow = load_json(workflow_file)
        workflow_info = workflow.get('workflow', {})
        workflows.append({
            'id': workflow_info.get('id', workflow_file.stem),
            'file': workflow_file.stem,
            'name': workflow_info.get('name', ''),
            'pattern_type': workflow_info.get('pattern_type', ''),
            'auto_generated': workflow.get('_meta', {}).get('auto_generated', False)
        })
    return workflows


def delete_workflow(filename: str) -> dict:
    """删除工作流"""
    filepath = WORKFLOWS_DIR / f"{filename}.json"

    if not filepath.exists():
        return {
            'success': False,
            'message': f'工作流不存在: {filename}'
        }

    filepath.unlink()
    return {
        'success': True,
        'message': f'工作流已删除: {filename}'
    }


# ============================================================================
# DP 平台能力封装
# ============================================================================

def query_sql(sql: str, format: str = 'table') -> dict:
    """执行 SQL 查询"""
    client = get_dp_client()
    if not client:
        return {'error': 'DpClient not available'}

    try:
        result = client.query(sql)
        return result
    except Exception as e:
        return {'error': str(e)}


def get_table_schema(db: str, table: str) -> dict:
    """获取表结构"""
    client = get_dp_client()
    if not client:
        return {'error': 'DpClient not available'}

    try:
        return client.table_schema(db, table)
    except Exception as e:
        return {'error': str(e)}


def get_table_columns(db: str, table: str) -> dict:
    """获取表字段"""
    client = get_dp_client()
    if not client:
        return {'error': 'DpClient not available'}

    try:
        return client.table_columns(db, table)
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='pay-data-master: 支付数据大师',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询模式
  python3 pay_data_master.py query --sql "SELECT * FROM ods.pay_order LIMIT 10"

  # 搜索知识库
  python3 pay_data_master.py search --keyword "GMV"

  # 表信息
  python3 pay_data_master.py table --name dev.dm_all_pay_recharge_22_now

  # 表结构（DP 平台能力）
  python3 pay_data_master.py table-schema --db ods --table pay_order
  python3 pay_data_master.py table-columns --db dev --table dm_all_pay_recharge_22_now

  # 自然语言解析
  python3 pay_data_master.py nl --text "查询店铺117301428的2026年PMV"
  python3 pay_data_master.py nl --text "查询kdt_id=117301428的店铺信息和PMV" --execute
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # query 命令
    query_parser = subparsers.add_parser('query', help='执行 SQL 查询')
    query_parser.add_argument('--sql', required=True, help='SQL 语句')
    query_parser.add_argument('--format', default='table', choices=['json', 'table', 'csv', 'markdown'])

    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索知识库')
    search_parser.add_argument('--keyword', required=True, help='搜索关键词')

    # table 命令
    table_parser = subparsers.add_parser('table', help='查看本地表信息（知识库）')
    table_parser.add_argument('--name', required=True, help='表名')

    # table-schema 命令（DP 平台）
    schema_parser = subparsers.add_parser('table-schema', help='获取表结构（DP 平台）')
    schema_parser.add_argument('--db', required=True, help='数据库名')
    schema_parser.add_argument('--table', required=True, help='表名')

    # table-columns 命令（DP 平台）
    columns_parser = subparsers.add_parser('table-columns', help='获取表字段（DP 平台）')
    columns_parser.add_argument('--db', required=True, help='数据库名')
    columns_parser.add_argument('--table', required=True, help='表名')

    # nl 命令
    nl_parser = subparsers.add_parser('nl', help='自然语言解析')
    nl_parser.add_argument('--text', required=True, help='自然语言输入')
    nl_parser.add_argument('--execute', action='store_true', help='直接执行查询')
    nl_parser.add_argument('--save-workflow', action='store_true', help='自动保存为新工作流（如果值得沉淀）')

    # workflows 命令组
    wf_parser = subparsers.add_parser('workflow', help='工作流管理')
    wf_subparsers = wf_parser.add_subparsers(dest='workflow_command', help='工作流子命令')

    # workflow list
    wf_list = wf_subparsers.add_parser('list', help='列出所有工作流')

    # workflow analyze
    wf_analyze = wf_subparsers.add_parser('analyze', help='分析 SQL 是否值得沉淀')
    wf_analyze.add_argument('--sql', required=True, help='SQL 语句')
    wf_analyze.add_argument('--text', required=True, help='原始自然语言描述')

    # workflow save
    wf_save = wf_subparsers.add_parser('save', help='保存工作流')
    wf_save.add_argument('--sql', required=True, help='SQL 语句')
    wf_save.add_argument('--text', required=True, help='原始自然语言描述')
    wf_save.add_argument('--name', help='工作流文件名（可选）')

    # workflow delete
    wf_delete = wf_subparsers.add_parser('delete', help='删除工作流')
    wf_delete.add_argument('--name', required=True, help='工作流文件名')

    args = parser.parse_args()

    # query 命令
    if args.command == 'query':
        result = query_sql(args.sql, args.format)
        print_json(result)

    # search 命令
    elif args.command == 'search':
        result = search_all(args.keyword)
        print_json(result)

    # table 命令（本地知识库）
    elif args.command == 'table':
        result = get_table_info(args.name)
        if result:
            print_json(result)
        else:
            print(f"Table not found: {args.name}", file=sys.stderr)
            sys.exit(1)

    # table-schema 命令（DP 平台）
    elif args.command == 'table-schema':
        result = get_table_schema(args.db, args.table)
        print_json(result)

    # table-columns 命令（DP 平台）
    elif args.command == 'table-columns':
        result = get_table_columns(args.db, args.table)
        print_json(result)

    # nl 命令
    elif args.command == 'nl':
        result = nl_to_sql(args.text)
        print_json(result)

        if args.execute and 'sql' in result:
            print("\n--- Executing SQL ---")
            query_result = query_sql(result['sql'])
            print_json(query_result)

        # 分析是否值得沉淀为工作流
        if 'sql' in result:
            analysis = analyze_sql_for_workflow(result['sql'], result.get('params', {}), args.text)
            print("\n--- Workflow Analysis ---")
            print_json(analysis)

            if analysis['worth_saving']:
                if args.save_workflow:
                    # 自动保存
                    workflow = create_workflow(args.text, result['sql'], result.get('params', {}), analysis)
                    save_result = save_workflow(workflow)
                    print("\n--- Workflow Saved ---")
                    print_json(save_result)
                else:
                    print("\n💡 这个查询值得沉淀为工作流！使用 --save-workflow 参数保存")

    # workflow 命令组
    elif args.command == 'workflow':
        if args.workflow_command == 'list':
            workflows = list_workflows()
            print_json({'total': len(workflows), 'workflows': workflows})

        elif args.workflow_command == 'analyze':
            params = extract_params(args.text)
            analysis = analyze_sql_for_workflow(args.sql, params, args.text)
            print_json(analysis)

        elif args.workflow_command == 'save':
            params = extract_params(args.text)
            analysis = analyze_sql_for_workflow(args.sql, params, args.text)
            workflow = create_workflow(args.text, args.sql, params, analysis)
            save_result = save_workflow(workflow, args.name)
            print_json(save_result)

        elif args.workflow_command == 'delete':
            delete_result = delete_workflow(args.name)
            print_json(delete_result)

        else:
            print("用法: pay_data_master.py workflow [list|analyze|save|delete]")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
