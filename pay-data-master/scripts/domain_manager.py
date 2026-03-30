#!/usr/bin/env python3
"""domain 知识管理 - 管理表/任务/工作流与业务语义的映射"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DOMAIN_DIR = Path(__file__).parent.parent / "domain"

VALID_TYPES = {"table": "tables.json", "task": "tasks.json", "workflow": "workflows.json"}


def _load(entity_type):
    path = DOMAIN_DIR / VALID_TYPES[entity_type]
    if not path.exists():
        return {"_meta": {}, "entries": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(entity_type, data):
    path = DOMAIN_DIR / VALID_TYPES[entity_type]
    DOMAIN_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def upsert(entity_type, key, fields_json):
    """新增或更新一条记录"""
    data = _load(entity_type)
    fields = json.loads(fields_json)
    fields["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if key in data["entries"]:
        data["entries"][key].update(fields)
    else:
        data["entries"][key] = fields
    _save(entity_type, data)
    print(json.dumps({"status": "ok", "action": "upsert", "key": key}, ensure_ascii=False))


def delete(entity_type, key):
    """删除一条记录"""
    data = _load(entity_type)
    if key in data["entries"]:
        del data["entries"][key]
        _save(entity_type, data)
        print(json.dumps({"status": "ok", "action": "deleted", "key": key}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "not_found", "key": key}, ensure_ascii=False))


def get(entity_type, key):
    """获取一条记录"""
    data = _load(entity_type)
    entry = data["entries"].get(key)
    if entry:
        print(json.dumps({"key": key, **entry}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "not_found", "key": key}, ensure_ascii=False))


def list_all(entity_type):
    """列出所有记录的摘要"""
    data = _load(entity_type)
    entries = data.get("entries", {})
    result = []
    for key, val in entries.items():
        entry = {
            "key": key,
            "name": val.get("name", ""),
            "description": val.get("description", ""),
        }
        if val.get("job_name"):
            entry["job_name"] = val["job_name"]
        result.append(entry)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def search(keyword, entity_type=None):
    """按关键词搜索（跨类型或指定类型），匹配 business_name/description/tags/key"""
    types = [entity_type] if entity_type else list(VALID_TYPES.keys())
    results = []
    kw = keyword.lower()
    for t in types:
        data = _load(t)
        for key, val in data.get("entries", {}).items():
            searchable = " ".join([
                key,
                val.get("name", ""),
                val.get("job_name", ""),
                val.get("description", ""),
            ]).lower()
            if kw in searchable:
                result_entry = {
                    "type": t,
                    "key": key,
                    "name": val.get("name", ""),
                    "description": val.get("description", ""),
                }
                if val.get("job_name"):
                    result_entry["job_name"] = val["job_name"]
                results.append(result_entry)
    print(json.dumps(results, ensure_ascii=False, indent=2))


def batch_upsert(entity_type, entries_json):
    """批量新增或更新"""
    data = _load(entity_type)
    entries = json.loads(entries_json)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    for key, fields in entries.items():
        fields["updated_at"] = now
        if key in data["entries"]:
            data["entries"][key].update(fields)
        else:
            data["entries"][key] = fields
        count += 1
    _save(entity_type, data)
    print(json.dumps({"status": "ok", "action": "batch_upsert", "count": count}, ensure_ascii=False))


def export_all():
    """导出所有 domain 知识为单个 JSON"""
    result = {}
    for t in VALID_TYPES:
        data = _load(t)
        result[t] = data.get("entries", {})
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="domain 知识管理")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # upsert
    p = sub.add_parser("upsert", help="新增或更新记录")
    p.add_argument("--type", required=True, choices=VALID_TYPES.keys())
    p.add_argument("--key", required=True, help="记录键（如 ods.pay_order）")
    p.add_argument("--fields", required=True, help="JSON 字段")

    # delete
    p = sub.add_parser("delete", help="删除记录")
    p.add_argument("--type", required=True, choices=VALID_TYPES.keys())
    p.add_argument("--key", required=True)

    # get
    p = sub.add_parser("get", help="获取记录")
    p.add_argument("--type", required=True, choices=VALID_TYPES.keys())
    p.add_argument("--key", required=True)

    # list
    p = sub.add_parser("list", help="列出所有记录摘要")
    p.add_argument("--type", required=True, choices=VALID_TYPES.keys())

    # search
    p = sub.add_parser("search", help="按关键词搜索")
    p.add_argument("--keyword", required=True)
    p.add_argument("--type", choices=VALID_TYPES.keys(), help="限定搜索类型")

    # batch-upsert
    p = sub.add_parser("batch-upsert", help="批量新增或更新")
    p.add_argument("--type", required=True, choices=VALID_TYPES.keys())
    p.add_argument("--entries", required=True, help="JSON: {key: fields, ...}")

    # export
    sub.add_parser("export", help="导出所有 domain 知识")

    args = parser.parse_args()

    if args.cmd == "upsert":
        upsert(args.type, args.key, args.fields)
    elif args.cmd == "delete":
        delete(args.type, args.key)
    elif args.cmd == "get":
        get(args.type, args.key)
    elif args.cmd == "list":
        list_all(args.type)
    elif args.cmd == "search":
        search(args.keyword, args.type)
    elif args.cmd == "batch-upsert":
        batch_upsert(args.type, args.entries)
    elif args.cmd == "export":
        export_all()


if __name__ == "__main__":
    main()
