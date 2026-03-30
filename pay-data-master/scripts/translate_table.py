#!/usr/bin/env python3
"""
表翻译工具 - 将数据库表翻译为结构化的业务知识，写入知识库

功能：
1. 获取表结构（字段名、类型、注释）
2. 自动检测分区类型（par快照/时间字段/无分区）
3. 识别枚举字段并查询实际值
4. 生成表的完整描述信息
5. 写入 domain/tables.json 知识库

用法：
    python3 scripts/translate_table.py <db>.<table> [--name "表名称"] [--desc "表描述"] [--business "业务域"]

示例：
    python3 scripts/translate_table.py dev.dm_all_pay_recharge_22_now
    python3 scripts/translate_table.py dm_pay.pay_merchant_pay_config --name "子商户号配置表"
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dp_client import DpClient

# 知识库文件
TABLES_FILE = Path(__file__).parent.parent / "domain" / "tables.json"


# 枚举值最大数量阈值 - 超过此值认为不是枚举字段
MAX_ENUM_VALUES = 50

# 明确不需要枚举检测的字段名模式
SKIP_ENUM_PATTERNS = [
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

# 明确是枚举的字段名模式
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


class TableTranslator:
    def __init__(self, site="fin"):
        self.site = site
        self.dp = DpClient(site)
        self.tables = self._load_tables()

    def _load_tables(self):
        """加载知识库"""
        if TABLES_FILE.exists():
            with open(TABLES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"entries": {}}

    def _save_tables(self):
        """保存知识库"""
        TABLES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TABLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tables, f, ensure_ascii=False, indent=2)

    def _execute_sql(self, sql):
        """执行 SQL 查询"""
        result = self.dp.execute_sql(sql)
        if result.get("code") == 0:
            return result["data"]
        raise Exception(f"SQL执行失败: {result.get('msg', 'Unknown error')}")

    def get_table_structure(self, db, table):
        """获取表结构"""
        sql = f"DESC {db}.{table}"
        data = self._execute_sql(sql)

        columns = []
        for row in data.get("queryResult", []):
            columns.append({
                "name": row[0],
                "type": row[1],
                "comment": row[3] if len(row) > 3 else ""
            })

        return columns

    def detect_partition_type(self, db, table, columns):
        """检测分区类型"""
        column_names = [col["name"] for col in columns]

        # 1. 检查是否有 par 分区
        if "par" in column_names:
            return {
                "type": "snapshot",
                "time_field": "par",
                "filter_condition": "par='${DP_1_DAYS_AGO_Ymd}'",
                "description": "快照分区，每天全量快照"
            }

        # 2. 检测常见时间字段
        time_field_patterns = [
            "day", "pay_day", "trade_day", "create_time", "created_at",
            "dt", "date", "log_date", "biz_date"
        ]

        for pattern in time_field_patterns:
            if pattern in column_names:
                return {
                    "type": "time_field",
                    "time_field": pattern,
                    "filter_condition": f"{pattern} >= DATE_FORMAT(CURRENT_DATE - INTERVAL '7' DAY, '%Y-%m-%d')",
                    "description": f"时间分区，使用 {pattern} 字段"
                }

        # 3. 无分区
        return {
            "type": "none",
            "time_field": None,
            "filter_condition": "LIMIT 1000",
            "description": "无分区，查询务必加限制条件"
        }

    def is_skip_field(self, col_name):
        """判断字段是否明确不需要枚举检测"""
        for p in SKIP_ENUM_PATTERNS:
            if re.match(p, col_name, re.IGNORECASE):
                return True
        return False

    def is_enum_name_pattern(self, col_name):
        """判断字段名是否匹配枚举模式"""
        for p in ENUM_NAME_PATTERNS:
            if re.match(p, col_name, re.IGNORECASE):
                return True
        return False

    def is_enum_candidate(self, column, partition_info):
        """判断是否为枚举候选字段（第一轮筛选：基于字段名和类型）"""
        col_type = column["type"].lower()
        col_name = column["name"].lower()

        # 1. 明确排除的字段
        if self.is_skip_field(col_name):
            return False

        # 2. 字段名匹配枚举模式 - 高优先级
        if self.is_enum_name_pattern(col_name):
            return True

        # 3. tinyint/smallint 类型通常是枚举
        if col_type in ('tinyint', 'smallint'):
            return True

        # 4. 注释中包含枚举描述模式（如 "0:xxx 1:xxx" 或 "0=xxx,1=xxx"）
        comment = column.get("comment", "")
        if comment and re.search(r'\d+[:=：]', comment):
            return True

        return False

    def check_enum_values_count(self, db, table, column, partition_info):
        """检查字段的 distinct 值数量，判断是否真的是枚举

        Returns:
            tuple: (is_enum, values, distinct_count)
        """
        col_name = column["name"]

        # 构建查询条件
        if partition_info["type"] == "snapshot":
            where = "par='${DP_1_DAYS_AGO_Ymd}'"
        elif partition_info["type"] == "time_field":
            time_field = partition_info["time_field"]
            where = f"{time_field} >= DATE_FORMAT(CURRENT_DATE - INTERVAL '7' DAY, '%Y-%m-%d')"
        else:
            where = "1=1"

        # 先查 distinct 值数量
        count_sql = f"SELECT COUNT(DISTINCT CAST({col_name} AS VARCHAR)) AS cnt FROM {db}.{table} WHERE {where}"

        try:
            data = self._execute_sql(count_sql)
            rows = data.get("queryResult", [])
            if rows and rows[0]:
                distinct_count = int(rows[0][0])
            else:
                distinct_count = 0
        except Exception as e:
            print(f"  警告: 查询 {col_name} distinct 数量失败: {e}")
            return False, [], 0

        # 超过阈值，不是枚举字段
        if distinct_count > MAX_ENUM_VALUES:
            return False, [], distinct_count

        # 在阈值内，获取实际值
        values_sql = f"SELECT DISTINCT CAST({col_name} AS VARCHAR) AS val FROM {db}.{table} WHERE {where} LIMIT {MAX_ENUM_VALUES + 1}"
        try:
            data = self._execute_sql(values_sql)
            values = [row[0] for row in data.get("queryResult", []) if row[0] is not None and row[0] != ""]
            return True, values, distinct_count
        except Exception as e:
            print(f"  警告: 查询 {col_name} 实际值失败: {e}")
            return False, [], distinct_count

    def generate_table_description(self, db, table, columns, partition_info, enum_values):
        """生成表的描述信息"""
        # 统计信息
        total_fields = len(columns)
        enum_field_names = list(enum_values.keys())

        # 构建字段描述
        fields_desc = []
        for col in columns:
            col_name = col["name"]
            col_type = col["type"]

            # 如果是枚举字段，添加枚举值说明
            comment = col["comment"]
            if col_name in enum_values:
                values = enum_values[col_name]
                if len(values) <= 20:
                    enum_str = "/".join(values)
                    if comment:
                        comment = f"{comment}，枚举: {enum_str}"
                    else:
                        comment = f"枚举: {enum_str}"
                else:
                    if comment:
                        comment = f"{comment}，枚举值较多({len(values)}个)"
                    else:
                        comment = f"枚举值较多({len(values)}个)"

            fields_desc.append(f"- `{col_name}` ({col_type}): {comment or '无注释'}")

        # 生成完整描述
        desc_parts = [
            f"**{db}.{table}** 表结构说明：",
            f"",
            f"**分区类型**: {partition_info['description']}",
            f"**字段数量**: {total_fields} 个",
            f"**枚举字段**: {len(enum_field_names)} 个",
            f"",
            f"**字段列表**:"
        ]

        desc_parts.extend(fields_desc)

        return "\n".join(desc_parts)

    def translate(self, db_table, name=None, description=None, business=None):
        """翻译表：从数据库获取信息并写入知识库"""
        # 解析 db.table
        parts = db_table.split(".", 1)
        if len(parts) != 2:
            raise ValueError(f"无效的表名格式，应为 db.table: {db_table}")

        db, table = parts[0], parts[1]

        print(f"\n{'='*60}")
        print(f"翻译表: {db}.{table}")
        print(f"{'='*60}\n")

        # Step 1: 获取表结构
        print("[1/5] 获取表结构...")
        columns = self.get_table_structure(db, table)
        print(f"  发现 {len(columns)} 个字段")

        # Step 2: 检测分区类型
        print("\n[2/5] 检测分区类型...")
        partition_info = self.detect_partition_type(db, table, columns)
        print(f"  分区类型: {partition_info['type']} ({partition_info['description']})")

        # Step 3: 识别枚举字段并获取值
        print(f"\n[3/5] 识别枚举字段...")
        enum_candidates = [col for col in columns if self.is_enum_candidate(col, partition_info)]
        print(f"  发现 {len(enum_candidates)} 个枚举候选字段")

        enum_values = {}
        non_enum_fields = []  # 记录被排除的字段

        for i, col in enumerate(enum_candidates, 1):
            col_name = col["name"]
            print(f"  检查 {col_name}... ({i}/{len(enum_candidates)})")

            # 使用新的方法检查是否真的是枚举
            is_enum, values, distinct_count = self.check_enum_values_count(db, table, col, partition_info)

            if is_enum and values:
                enum_values[col_name] = values
                print(f"    ✓ 是枚举字段，{len(values)} 个值: {', '.join(str(v) for v in values[:5])}{'...' if len(values) > 5 else ''}")
            else:
                non_enum_fields.append({
                    "name": col_name,
                    "distinct_count": distinct_count,
                    "reason": f"distinct值过多({distinct_count}个)" if distinct_count > MAX_ENUM_VALUES else "查询失败"
                })
                print(f"    ✗ 非枚举字段: {non_enum_fields[-1]['reason']}")

        if non_enum_fields:
            print(f"\n  排除的非枚举字段: {', '.join(f['name'] for f in non_enum_fields)}")

        # Step 4: 生成描述
        print(f"\n[4/5] 生成表描述...")

        # 构建字段数组
        fields_array = []
        for col in columns:
            col_name = col["name"]
            col_type = col["type"]
            comment = col["comment"] or ""

            # 只有通过 distinct 值数量验证的才添加枚举值到注释
            if col_name in enum_values:
                values = enum_values[col_name]
                if len(values) <= 20:
                    enum_str = "/".join(str(v) for v in values)
                    comment = f"{comment}，枚举: {enum_str}" if comment else f"枚举: {enum_str}"
                else:
                    comment = f"{comment}，枚举值较多({len(values)}个)" if comment else f"枚举值较多({len(values)}个)"

            fields_array.append({
                "name": col_name,
                "type": col_type,
                "comment": comment
            })

        # 使用用户提供的名称和描述，或生成默认值
        table_name = name or table.replace("_", " ").title()
        table_desc = description or f"{table_name}，{partition_info['description']}，{len(columns)}个字段。"

        # Step 5: 写入知识库
        print(f"\n[5/5] 写入知识库...")

        entry = {
            "name": table_name,
            "description": table_desc,
            "business": business or "",
            "fields": fields_array,
            "partition_type": partition_info["type"],
            "time_field": partition_info["time_field"],
            "data_range": "",
            "row_count": "",
            "enums": enum_values
        }

        # 保留原有的 updated_at 或新建
        key = f"{db}.{table}"
        if key in self.tables["entries"]:
            if "updated_at" in self.tables["entries"][key]:
                entry["updated_at"] = self.tables["entries"][key]["updated_at"]

        self.tables["entries"][key] = entry
        self._save_tables()

        print(f"\n{'='*60}")
        print(f"✅ 翻译完成!")
        print(f"{'='*60}")
        print(f"表名: {db}.{table}")
        print(f"中文名: {table_name}")
        print(f"字段数: {len(columns)}")
        print(f"枚举字段: {len(enum_values)} 个")
        print(f"分区类型: {partition_info['type']}")
        print(f"\n已写入: {TABLES_FILE}")

        return entry


def main():
    parser = argparse.ArgumentParser(
        description="表翻译工具 - 将数据库表翻译为结构化的业务知识",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python3 scripts/translate_table.py dev.dm_all_pay_recharge_22_now

  # 指定表名和描述
  python3 scripts/translate_table.py dm_pay.pay_merchant_pay_config \\
    --name "子商户号配置表" \\
    --desc "商户的子商户号配置，包括类型、状态、费率、渠道等" \\
    --business "商户配置"

  # 切换站点
  python3 scripts/translate_table.py ods.pay_order --site main
        """
    )

    parser.add_argument("table", help="表名，格式: db.table")
    parser.add_argument("--name", help="表中文名")
    parser.add_argument("--desc", help="表描述")
    parser.add_argument("--business", help="业务域")
    parser.add_argument("--site", default="fin", choices=["fin", "main"], help="DP站点")

    args = parser.parse_args()

    try:
        translator = TableTranslator(site=args.site)
        translator.translate(
            db_table=args.table,
            name=args.name,
            description=args.desc,
            business=args.business
        )
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
