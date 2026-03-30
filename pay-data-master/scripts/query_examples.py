#!/usr/bin/env python3
"""
SQL 查询示例管理器 - 存储、管理和执行常用 SQL 查询模板
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
import subprocess

sys.path.insert(0, str(Path(__file__).parent))
from dp_client import DpClient

# 示例存储文件
EXAMPLES_FILE = Path(__file__).parent.parent / "examples" / "query_examples.json"


class QueryExampleManager:
    def __init__(self, site="fin"):
        self.site = site
        self.examples = self._load_examples()

    def _load_examples(self):
        """加载查询示例"""
        if EXAMPLES_FILE.exists():
            with open(EXAMPLES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "_meta": {
                "description": "SQL 查询示例库",
                "total_examples": 0
            },
            "examples": []
        }

    def _save_examples(self):
        """保存查询示例"""
        EXAMPLES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(EXAMPLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.examples, f, ensure_ascii=False, indent=2)

    def list_examples(self, tag=None, table=None):
        """列出所有示例"""
        examples = self.examples.get("examples", [])

        # 过滤
        if tag:
            examples = [e for e in examples if tag in e.get("tags", [])]
        if table:
            examples = [e for e in examples if table in e.get("tables", [])]

        # 输出
        if not examples:
            print("未找到匹配的示例")
            return

        print(f"\n总计 {len(examples)} 个示例:\n")
        for i, ex in enumerate(examples, 1):
            print(f"{i}. {ex['name']}")
            print(f"   描述: {ex['description'][:60]}...")
            print(f"   标签: {', '.join(ex.get('tags', []))}")
            print(f"   涉及表: {', '.join(ex.get('tables', [])[:3])}")
            print(f"   ID: {ex['id']}")
            print()

    def show_example(self, example_id):
        """显示示例详情"""
        example = self._find_example(example_id)
        if not example:
            print(f"未找到 ID 为 '{example_id}' 的示例")
            return

        print(f"\n{'='*60}")
        print(f"示例: {example['name']}")
        print(f"{'='*60}")
        print(f"ID: {example['id']}")
        print(f"描述: {example['description']}")
        print(f"标签: {', '.join(example.get('tags', []))}")
        print(f"涉及表: {', '.join(example.get('tables', []))}")
        if example.get('params'):
            print(f"参数:")
            for param in example['params']:
                print(f"  - {param['name']}: {param['description']} (默认值: {param.get('default', '无')})")
        print(f"\nSQL 语句:")
        print(f"{'-'*60}")
        print(example['sql'])
        print(f"{'='*60}\n")

    def run_example(self, example_id, param_values=None, preview=True):
        """运行示例"""
        example = self._find_example(example_id)
        if not example:
            print(f"未找到 ID 为 '{example_id}' 的示例")
            return

        sql = example['sql']

        # 替换参数
        if param_values:
            for param_name, param_value in param_values.items():
                placeholder = f"{{{{{param_name}}}}}"
                sql = sql.replace(placeholder, param_value)

        if preview:
            print(f"\n{'='*60}")
            print(f"预览 SQL (示例: {example['name']})")
            print(f"{'='*60}")
            print(sql)
            print(f"{'='*60}\n")

            confirm = input("确认执行? (y/n): ")
            if confirm.lower() != 'y':
                print("已取消")
                return

        # 执行 SQL
        print(f"\n正在执行...")
        dp = DpClient(self.site)
        try:
            result = dp.execute_sql(sql)
            print("执行成功!")
            return result
        except Exception as e:
            print(f"执行失败: {e}")
            return None

    def add_example(self, name, description, sql, tags=None, tables=None, params=None):
        """添加新示例"""
        example_id = self._generate_id(name)

        # 自动提取涉及的表
        if not tables:
            tables = self._extract_tables_from_sql(sql)

        example = {
            "id": example_id,
            "name": name,
            "description": description,
            "sql": sql,
            "tags": tags or [],
            "tables": tables or [],
            "params": params or []
        }

        # 检查是否已存在
        if self._find_example(example_id):
            print(f"示例 ID '{example_id}' 已存在")
            return

        self.examples["examples"].append(example)
        self.examples["_meta"]["total_examples"] = len(self.examples["examples"])
        self._save_examples()

        print(f"已添加示例: {name}")
        print(f"ID: {example_id}")
        print(f"涉及表: {', '.join(tables)}")

    def delete_example(self, example_id):
        """删除示例"""
        example = self._find_example(example_id)
        if not example:
            print(f"未找到 ID 为 '{example_id}' 的示例")
            return

        self.examples["examples"].remove(example)
        self.examples["_meta"]["total_examples"] = len(self.examples["examples"])
        self._save_examples()

        print(f"已删除示例: {example['name']}")

    def _find_example(self, example_id):
        """查找示例"""
        for ex in self.examples.get("examples", []):
            if ex['id'] == example_id:
                return ex
        return None

    def _generate_id(self, name):
        """生成示例 ID"""
        # 将名称转换为小写，用下划线连接
        id_str = re.sub(r'[^\w\s]', '', name.lower())
        id_str = re.sub(r'\s+', '_', id_str)
        return id_str[:50]

    def _extract_tables_from_sql(self, sql):
        """从 SQL 中提取表名"""
        # 匹配 FROM 和 JOIN 后的表名
        patterns = [
            r'FROM\s+(\w+\.\w+)',
            r'JOIN\s+(\w+\.\w+)',
            r',\s*(\w+\.\w+)'
        ]

        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.update(matches)

        return sorted(list(tables))


def main():
    parser = argparse.ArgumentParser(description="SQL 查询示例管理器")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有示例")
    list_parser.add_argument("--tag", help="按标签过滤")
    list_parser.add_argument("--table", help="按表名过滤")
    list_parser.add_argument("--site", default="fin", choices=["fin", "main"])

    # show 命令
    show_parser = subparsers.add_parser("show", help="显示示例详情")
    show_parser.add_argument("id", help="示例 ID")
    show_parser.add_argument("--site", default="fin", choices=["fin", "main"])

    # run 命令
    run_parser = subparsers.add_parser("run", help="运行示例")
    run_parser.add_argument("id", help="示例 ID")
    run_parser.add_argument("--param", action="append", help="参数值 (格式: key=value)")
    run_parser.add_argument("--yes", "-y", action="store_true", help="跳过预览直接执行")
    run_parser.add_argument("--site", default="fin", choices=["fin", "main"])

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加示例")
    add_parser.add_argument("name", help="示例名称")
    add_parser.add_argument("description", help="描述")
    add_parser.add_argument("sql", help="SQL 语句 (用引号括起来)")
    add_parser.add_argument("--tag", action="append", help="标签")
    add_parser.add_argument("--table", action="append", help="涉及表 (会自动检测)")
    add_parser.add_argument("--site", default="fin", choices=["fin", "main"])

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除示例")
    delete_parser.add_argument("id", help="示例 ID")
    delete_parser.add_argument("--site", default="fin", choices=["fin", "main"])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = QueryExampleManager(site=args.site)

    if args.command == "list":
        manager.list_examples(tag=args.tag, table=args.table)

    elif args.command == "show":
        manager.show_example(args.id)

    elif args.command == "run":
        # 解析参数
        param_values = {}
        if args.param:
            for p in args.param:
                key, value = p.split('=', 1)
                param_values[key] = value
        manager.run_example(args.id, param_values=param_values, preview=not args.yes)

    elif args.command == "add":
        # 交互式输入参数信息
        print("\n添加 SQL 查询示例")
        print("=" * 60)
        name = args.name
        description = args.description
        sql = args.sql
        tags = args.tag or []
        tables = args.table or []

        # 询问参数信息
        params = []
        has_params = input("\nSQL 是否包含参数? (y/n): ").lower() == 'y'
        if has_params:
            print("\n请定义参数 (格式: {param_name}):")
            print("例如: WHERE par='{{date}}' → 参数名: date")
            while True:
                param_name = input("\n参数名 (留空结束): ").strip()
                if not param_name:
                    break
                param_desc = input(f"  - {param_name} 描述: ").strip()
                param_default = input(f"  - {param_name} 默认值 (可选): ").strip()
                param = {
                    "name": param_name,
                    "description": param_desc
                }
                if param_default:
                    param["default"] = param_default
                params.append(param)

        manager.add_example(
            name=name,
            description=description,
            sql=sql,
            tags=tags,
            tables=tables,
            params=params
        )

    elif args.command == "delete":
        manager.delete_example(args.id)


if __name__ == "__main__":
    main()
