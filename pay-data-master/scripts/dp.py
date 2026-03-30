#!/usr/bin/env python3
"""dp 平台统一 CLI 入口"""

import argparse
import json
import sys
import csv
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dp_client import DpClient, AirflowClient


def output(data, fmt="json"):
    """输出结果，支持 json/table/csv/markdown"""
    if fmt == "json" or not isinstance(data, dict):
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    query_data = data.get("data", {})
    meta = query_data.get("metaData") or []
    rows = query_data.get("queryResult") or []
    if not meta or not rows:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    columns = [m["columnName"] for m in meta]

    if fmt == "csv":
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(columns)
        w.writerows(rows)
        print(buf.getvalue())
    elif fmt == "markdown":
        print("| " + " | ".join(columns) + " |")
        print("| " + " | ".join("---" for _ in columns) + " |")
        for row in rows:
            print("| " + " | ".join(str(row[i] if i < len(row) else "") for i in range(len(columns))) + " |")
    elif fmt == "table":
        widths = [max(len(c), max((len(str(r[i] if i < len(r) else "")) for r in rows), default=0)) for i, c in enumerate(columns)]
        widths = [min(w, 50) for w in widths]
        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        def row_str(vals):
            return "| " + " | ".join(str(vals[i] if i < len(vals) else "").ljust(widths[i])[:widths[i]] for i in range(len(columns))) + " |"
        print(sep)
        print(row_str(columns))
        print(sep)
        for row in rows:
            print(row_str(row))
        print(sep)
        print(f"{len(rows)} rows", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="dp 平台 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 为每个子命令添加公共参数的辅助函数
    def add_common(p):
        p.add_argument("--site", default="fin", choices=["fin", "main"])
        p.add_argument("--format", default="json", choices=["json", "table", "csv", "markdown"])
        return p

    # --- 数据查询 ---
    add_common(sub.add_parser("list-dbs"))
    p = add_common(sub.add_parser("list-tables")); p.add_argument("--db", required=True)
    p = add_common(sub.add_parser("query")); p.add_argument("--sql", required=True); p.add_argument("--engine", default="SPARK", choices=["SPARK", "PRESTO", "HIVE"], help="查询引擎（默认 SPARK）")
    p = add_common(sub.add_parser("get-result")); p.add_argument("--uuid", required=True)

    # --- 表元数据 ---
    p = add_common(sub.add_parser("table-schema")); p.add_argument("--db", required=True); p.add_argument("--table", required=True)
    p = add_common(sub.add_parser("table-columns")); p.add_argument("--db", required=True); p.add_argument("--table", required=True)
    p = add_common(sub.add_parser("table-partitions")); p.add_argument("--db", required=True); p.add_argument("--table", required=True)
    p = add_common(sub.add_parser("table-stats")); p.add_argument("--db", required=True); p.add_argument("--table", required=True)
    p = add_common(sub.add_parser("table-sample")); p.add_argument("--db", required=True); p.add_argument("--table", required=True); p.add_argument("--limit", type=int, default=10)

    # --- 血缘 ---
    p = add_common(sub.add_parser("lineage-upstream")); p.add_argument("--db", required=True); p.add_argument("--table", required=True); p.add_argument("--par")
    p = add_common(sub.add_parser("lineage-downstream")); p.add_argument("--db", required=True); p.add_argument("--table", required=True); p.add_argument("--par")
    p = add_common(sub.add_parser("lineage-column")); p.add_argument("--db", required=True); p.add_argument("--table", required=True); p.add_argument("--column"); p.add_argument("--par")
    p = add_common(sub.add_parser("lineage-to-bi")); p.add_argument("--db", required=True); p.add_argument("--table", required=True); p.add_argument("--par")

    # --- 任务管理 ---
    p = add_common(sub.add_parser("task-search")); p.add_argument("--keyword", required=True)
    p = add_common(sub.add_parser("task-workflow")); p.add_argument("--job-id", required=True)
    p = add_common(sub.add_parser("task-detail")); p.add_argument("--job-id", required=True); p.add_argument("--job-type", default="code-hive")
    p = add_common(sub.add_parser("task-list")); p.add_argument("--page", type=int, default=1); p.add_argument("--page-size", type=int, default=10); p.add_argument("--all", action="store_true")

    # --- 数据导出 ---
    p = add_common(sub.add_parser("export")); p.add_argument("--sql", required=True); p.add_argument("--filetype", default="excel", choices=["excel", "csv"]); p.add_argument("--output", help="输出文件路径")
    p = add_common(sub.add_parser("export-by-uuid")); p.add_argument("--uuid", required=True); p.add_argument("--filetype", default="excel", choices=["excel", "csv"]); p.add_argument("--output", help="输出文件路径")

    # --- Airflow ---
    p = add_common(sub.add_parser("airflow-status")); p.add_argument("--dag-id", required=True); p.add_argument("--execution-date")
    p = add_common(sub.add_parser("airflow-task-detail")); p.add_argument("--dag-id", required=True); p.add_argument("--execution-date", required=True); p.add_argument("--task-id")
    p = add_common(sub.add_parser("airflow-runs")); p.add_argument("--dag-id", required=True)
    p = add_common(sub.add_parser("airflow-log")); p.add_argument("--dag-id", required=True); p.add_argument("--task-id", required=True); p.add_argument("--execution-date", required=True)

    args = parser.parse_args()

    try:
        dp = DpClient(args.site)
        af = AirflowClient(args.site)

        cmd = args.cmd
        if cmd == "list-dbs": result = dp.list_databases()
        elif cmd == "list-tables": result = dp.list_tables(args.db)
        elif cmd == "query": result = dp.query(args.sql)
        elif cmd == "get-result": result = dp.get_result(args.uuid)
        elif cmd == "table-schema": result = dp.table_schema(args.db, args.table)
        elif cmd == "table-columns": result = dp.table_columns(args.db, args.table)
        elif cmd == "table-partitions": result = dp.table_partitions(args.db, args.table)
        elif cmd == "table-stats": result = dp.table_stats(args.db, args.table)
        elif cmd == "table-sample": result = dp.table_sample(args.db, args.table, args.limit)
        elif cmd == "lineage-upstream": result = dp.lineage_upstream(args.db, args.table, args.par)
        elif cmd == "lineage-downstream": result = dp.lineage_downstream(args.db, args.table, args.par)
        elif cmd == "lineage-column": result = dp.lineage_column(args.db, args.table, args.column, args.par)
        elif cmd == "lineage-to-bi": result = dp.lineage_to_bi(args.db, args.table, args.par)
        elif cmd == "task-search": result = dp.task_search(args.keyword)
        elif cmd == "task-workflow": result = dp.task_workflow_detail(args.job_id)
        elif cmd == "task-detail": result = dp.task_single_detail(args.job_id, args.job_type)
        elif cmd == "task-list": result = dp.task_list(args.page, args.page_size, not getattr(args, 'all', False))
        elif cmd == "export": result = dp.export_dump(args.sql, args.filetype, args.output)
        elif cmd == "export-by-uuid": result = dp.export_by_uuid(args.uuid, args.filetype, args.output)
        elif cmd == "airflow-status": result = af.dag_status(args.dag_id, args.execution_date)
        elif cmd == "airflow-task-detail": result = af.task_detail(args.dag_id, args.execution_date, args.task_id)
        elif cmd == "airflow-runs": result = af.dag_runs(args.dag_id)
        elif cmd == "airflow-log": result = af.task_log(args.dag_id, args.task_id, args.execution_date)
        else:
            parser.print_help()
            sys.exit(1)

        output(result, args.format)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
