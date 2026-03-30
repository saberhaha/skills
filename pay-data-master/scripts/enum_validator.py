#!/usr/bin/env python3
"""枚举值完整性校验 - 检测表中枚举字段的实际值是否被知识库完整覆盖"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dp_client import DpClient
from domain_manager import _load, _save

# 枚举值最大数量阈值 - 超过此值认为不是枚举字段
MAX_ENUM_VALUES = 50

# 明确不需要校验枚举的字段名模式
SKIP_PATTERNS = [
    r'.*_id$', r'.*_no$', r'.*_code$',  # ID/编号类
    r'.*_name$', r'.*_title$', r'.*_desc$',  # 名称/标题/描述类
    r'.*_url$', r'.*_path$', r'.*_link$',  # 链接类
    r'.*_email$', r'.*_phone$', r'.*_tel$',  # 联系方式类
    r'.*_ext$', r'.*_extra$', r'.*_json$', r'.*_data$',  # 扩展字段类
    r'.*_at$', r'.*_time$', r'.*_date$',  # 时间类
    r'.*amount.*', r'.*money.*', r'.*fee$', r'.*price.*', r'.*cost.*',  # 金额类
    r'.*_count$', r'.*_num$', r'.*_size$', r'.*_rate$', r'.*_ratio$',  # 数量/比例类
    r'^id$', r'^par$', r'^extra$', r'^memo$', r'^remark$', r'^note$',  # 通用字段
    r'^created_at$', r'^updated_at$', r'^appid$', r'^customer_id$',
    r'^principal_', r'^contact_', r'^merchant_', r'^user_',  # 主体/联系方式类
    r'^biz_ext$', r'^extend_',  # 扩展字段
]

# 明确需要校验枚举的字段名模式
ENUM_NAME_PATTERNS = [
    r'^type$', r'.*_type$', r'^status$', r'^state$', r'.*_status$', r'.*_state$',
    r'^is_.*', r'^has_.*', r'^can_.*',
    r'^channel$', r'^inst$', r'.*_mode$', r'.*_method$',
    r'.*_level$', r'.*_scene.*', r'.*_tag$', r'.*_category$',
    r'^role$', r'.*_role$', r'.*_property$', r'^env$',
    r'^in_out$', r'^biz_prod$', r'^biz_action$', r'^biz_mode$',
    r'.*_flag$', r'^source$', r'.*_source$',
    r'^offline_tag', r'^yz_product', r'^pay_env',
]

# 适合做枚举校验的数据类型
ENUM_TYPES = ['tinyint', 'smallint', 'int', 'integer', 'bigint', 'varchar', 'string']


def is_skip_field(col_name):
    """判断字段是否明确不需要校验"""
    for p in SKIP_PATTERNS:
        if re.match(p, col_name, re.IGNORECASE):
            return True
    return False


def is_enum_candidate(col_name, col_type, col_comment):
    """判断字段是否可能是枚举字段（第一轮筛选）"""
    # 1. 明确排除的字段
    if is_skip_field(col_name):
        return False

    # 2. 字段名匹配枚举模式
    for p in ENUM_NAME_PATTERNS:
        if re.match(p, col_name, re.IGNORECASE):
            return True

    # 3. 注释中包含枚举描述模式（如 "0:xxx 1:xxx" 或 "0=xxx,1=xxx"）
    if col_comment and re.search(r'\d+[:=：]', col_comment):
        return True

    # 4. tinyint/smallint 类型通常是枚举
    if col_type in ('tinyint', 'smallint'):
        return True

    return False


def extract_documented_values(comment):
    """从注释中提取已文档化的枚举值"""
    if not comment:
        return set()
    values = set()
    # 匹配 "0:xxx" "1：xxx" "0=xxx" 等模式
    for m in re.finditer(r'(\d+)\s*[:=：]', comment):
        values.add(m.group(1))
    # 匹配 "WXPAY:xxx" "ONLINE:xxx" 等模式
    for m in re.finditer(r'([A-Z_]+)\s*[:=：]', comment):
        values.add(m.group(1))
    return values


def validate_table(db, table, par=None, site="fin", time_field=None):
    """校验一张表的枚举字段完整性

    Args:
        db: 数据库名
        table: 表名
        par: 指定分区值（如 20260309），不指定则自动判断
        site: 环境站点
        time_field: 非分区表的时间过滤字段（如 pay_day）
    """
    dp = DpClient(site)

    # 1. 获取表结构
    print(f"[1/3] 获取 {db}.{table} 表结构...", file=sys.stderr)
    col_result = dp.execute_sql(f"DESC {db}.{table}")
    col_data = col_result.get("data", {})
    meta = col_data.get("metaData", [])
    rows = col_data.get("queryResult", [])

    if not rows:
        print(json.dumps({"error": "无法获取表结构"}, ensure_ascii=False))
        return

    # 解析列信息: DESC 返回 [Column, Type, Extra, Comment] 四列
    # comment 在 index 3（第 4 列）
    columns = []
    has_par = False
    for row in rows:
        col_name = row[0] if len(row) > 0 else ""
        col_type = row[1] if len(row) > 1 else ""
        col_comment = row[3] if len(row) > 3 else (row[2] if len(row) > 2 else "")
        if col_name == "par":
            has_par = True
            continue  # 不把 par 作为普通列处理
        if col_name:
            columns.append({
                "name": col_name,
                "type": col_type.strip().lower(),
                "comment": col_comment.strip() if col_comment else "",
            })

    # 确定分区/时间条件
    if has_par:
        # 有 par 分区：快照分区，每天一份全量
        if par:
            par_condition = f"par='{par}'"
        else:
            # 默认取最近数据（前一天）
            par_condition = "par='${DP_1_DAYS_AGO_Ymd}'"
        partition_type = "snapshot"
    elif time_field:
        # 无 par 分区，但指定了时间字段
        par_condition = f"{time_field} >= DATE_FORMAT(CURRENT_DATE - INTERVAL '7' DAY, '%Y-%m-%d')"
        partition_type = "time_field"
    else:
        # 无分区，尝试自动检测时间字段
        time_candidates = ['pay_day', 'trade_day', 'created_day', 'dt', 'day']
        detected_field = None
        for col in columns:
            if col['name'] in time_candidates:
                detected_field = col['name']
                break
        if detected_field:
            par_condition = f"{detected_field} >= DATE_FORMAT(CURRENT_DATE - INTERVAL '7' DAY, '%Y-%m-%d')"
            partition_type = f"auto_detected({detected_field})"
        else:
            par_condition = "1=1"  # 无任何过滤条件，可能超时
            partition_type = "none"
            print(f"警告: 表 {db}.{table} 无 par 分区且未检测到时间字段，查询可能超时", file=sys.stderr)

    # 2. 筛选枚举候选字段
    enum_fields = []
    for col in columns:
        if is_skip_field(col["name"]):
            continue
        if col["type"] not in ENUM_TYPES:
            continue
        if is_enum_candidate(col["name"], col["type"], col["comment"]):
            enum_fields.append(col)

    if not enum_fields:
        print(json.dumps({"table": f"{db}.{table}", "enum_fields": 0, "message": "未发现枚举候选字段"}, ensure_ascii=False))
        return

    print(f"[2/3] 发现 {len(enum_fields)} 个枚举候选字段: {[f['name'] for f in enum_fields]}", file=sys.stderr)

    # 3. 查询每个枚举字段的实际去重值（两步验证：先查数量，再查值）
    results = []
    for f in enum_fields:
        print(f"  检查 {f['name']}...", file=sys.stderr)

        # 第一步：查询 distinct 值数量
        count_sql = f"SELECT COUNT(DISTINCT CAST({f['name']} AS VARCHAR)) AS cnt FROM {db}.{table} WHERE {par_condition}"
        try:
            count_result = dp.execute_sql(count_sql, max_wait=15)
            count_rows = count_result.get("data", {}).get("queryResult") or []
            distinct_count = int(count_rows[0][0]) if count_rows and count_rows[0] else 0
        except Exception as e:
            print(f"    警告: 查询 distinct 数量失败: {e}", file=sys.stderr)
            distinct_count = 0

        # 超过阈值，跳过此字段
        if distinct_count > MAX_ENUM_VALUES:
            print(f"    ✗ 非枚举字段: distinct值过多({distinct_count}个 > {MAX_ENUM_VALUES})", file=sys.stderr)
            results.append({
                "field": f["name"],
                "type": f["type"],
                "comment": f["comment"],
                "distinct_count": distinct_count,
                "is_enum": False,
                "skip_reason": f"distinct值过多({distinct_count}个)",
                "documented_values": [],
                "actual_values": [],
                "undocumented_values": [],
                "is_complete": True,  # 非枚举字段无需校验
            })
            continue

        # 第二步：查询实际值
        sql = f"SELECT DISTINCT CAST({f['name']} AS VARCHAR) AS val FROM {db}.{table} WHERE {par_condition} LIMIT {MAX_ENUM_VALUES + 1}"
        try:
            query_result = dp.execute_sql(sql, max_wait=15)
            actual_rows = query_result.get("data", {}).get("queryResult") or []
            actual_values = []
            for r in actual_rows:
                val = str(r[0]) if r[0] is not None else "NULL"
                actual_values.append(val)
        except Exception as e:
            actual_values = [f"_error: {e}"]

        documented = extract_documented_values(f["comment"])
        actual_keys = set(actual_values) - {"_error", "NULL", "None", "null", ""}
        undocumented = actual_keys - documented

        print(f"    ✓ 是枚举字段，{len(actual_values)} 个值", file=sys.stderr)

        results.append({
            "field": f["name"],
            "type": f["type"],
            "comment": f["comment"],
            "distinct_count": distinct_count,
            "is_enum": True,
            "documented_values": sorted(documented),
            "actual_values": sorted(actual_values),
            "undocumented_values": sorted(undocumented),
            "is_complete": len(undocumented) == 0,
        })

    print(f"[3/3] 校验完成", file=sys.stderr)

    # 输出结果
    output = {
        "table": f"{db}.{table}",
        "has_par_partition": has_par,
        "partition_type": partition_type,
        "filter_condition": par_condition,
        "total_enum_fields": len(enum_fields),
        "incomplete_fields": sum(1 for r in results if not r["is_complete"]),
        "fields": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="枚举值完整性校验")
    parser.add_argument("--db", required=True, help="数据库名")
    parser.add_argument("--table", required=True, help="表名")
    parser.add_argument("--par", help="指定分区值（如 20260309），不指定则取 par='${DP_1_DAYS_AGO_Ymd}'")
    parser.add_argument("--time-field", help="非分区表的时间过滤字段（如 pay_day）")
    parser.add_argument("--site", default="fin", choices=["fin", "main"])
    args = parser.parse_args()
    validate_table(args.db, args.table, args.par, args.site, args.time_field)


if __name__ == "__main__":
    main()
