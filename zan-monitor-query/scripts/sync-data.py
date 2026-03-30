#!/usr/bin/env python3
"""统一数据同步脚本（apps + dashboards → data.json）

用法：
  python sync-data.py --init                    # 全量初始化（apps + dashboards）
  python sync-data.py --init --only apps        # 只初始化 apps
  python sync-data.py --init --only dashboards  # 只初始化 dashboards
  python sync-data.py --update                  # 增量更新全部
  python sync-data.py --update --only apps      # 只更新 apps
  python sync-data.py --update --dry-run        # 预览变更
  python sync-data.py --check                   # 检查同步状态
  python sync-data.py --list apps               # 列出已同步的应用
  python sync-data.py --list dashboards         # 列出已同步的 dashboard
  python sync-data.py --search apps "支付"      # 搜索应用
  python sync-data.py --search dashboards "RPC" # 搜索 dashboard
  python sync-data.py --set-bu pay-xxx main     # 手动设置应用 BU
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# 配置
DOMAIN_DIR = Path(__file__).parent.parent / "domain"
DATA_FILE = DOMAIN_DIR / "data.json"

sys.path.insert(0, str(Path(__file__).parent))
from skynet import get_client

# ============================================================
# BU 自动标注规则
# ============================================================

# pay-* 系列 → fincloud（金融云）
# 其他所有应用 → main（有赞云）
BU_RULES: list[tuple[str, str]] = [
    (r"^pay-", "fincloud"),
]
DEFAULT_BU = "main"


def detect_bu(app_name: str) -> str:
    """按规则推断应用 BU"""
    for pattern, bu in BU_RULES:
        if re.match(pattern, app_name):
            return bu
    return DEFAULT_BU


# ============================================================
# data.json 读写
# ============================================================

def load_data() -> dict:
    """加载 data.json，不存在则返回空结构"""
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "apps": {"synced_at": None, "total_count": 0, "items": []},
        "dashboards": {"synced_at": None, "total_count": 0, "success_count": 0, "error_count": 0, "items": []},
    }


def save_data(data: dict) -> None:
    """保存 data.json"""
    DOMAIN_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n>> 数据已保存: {DATA_FILE}")


# ============================================================
# Apps 同步
# ============================================================

def fetch_apps() -> list[dict]:
    """从 /v1/apps 拉取全量应用列表"""
    client = get_client("fincloud", "prod")
    apps = client.list_apps()
    if not isinstance(apps, list):
        print(f"  ERROR: /v1/apps 返回异常: {type(apps)}")
        return []
    return apps


def normalize_app(raw: dict) -> dict:
    """将 API 返回的应用数据标准化，并自动标注 BU"""
    name = raw.get("name", "")
    return {
        "id": raw.get("id"),
        "name": name,
        "type": raw.get("type"),
        "bu": detect_bu(name),
    }


def sync_apps(data: dict, *, dry_run: bool = False) -> dict:
    """同步 apps 数据"""
    print("\n== Apps 同步 ==")

    print("  拉取 /v1/apps ...")
    raw_apps = fetch_apps()
    if not raw_apps:
        print("  ERROR: 未获取到任何应用")
        return data

    items = [normalize_app(a) for a in raw_apps]
    print(f"  获取到 {len(items)} 个应用")

    if dry_run:
        existing = {a["name"] for a in data.get("apps", {}).get("items", [])}
        new_names = {a["name"] for a in items}
        added = new_names - existing
        removed = existing - new_names
        print(f"  [dry-run] 新增: {len(added)}, 删除: {len(removed)}")
        if added:
            for n in sorted(added)[:5]:
                print(f"    + {n}")
        if removed:
            for n in sorted(removed)[:5]:
                print(f"    - {n}")
        return data

    data.setdefault("apps", {})
    data["apps"]["synced_at"] = datetime.now().isoformat()
    data["apps"]["total_count"] = len(items)
    data["apps"]["items"] = items
    return data


# ============================================================
# Dashboards 同步（复用 sync-dashboards.py 全部逻辑）
# ============================================================

def fetch_dashboard_list(env: str = "prod", limit: int = 1000) -> list[dict]:
    """获取 Dashboard 列表"""
    client = get_client("fincloud", env)
    try:
        dashboards = client.list_dashboards(limit=limit)
        return [
            {
                "uid": d.get("uid"),
                "title": d.get("title"),
                "type": d.get("type"),
                "folderId": d.get("folderId"),
                "folderTitle": d.get("folderTitle"),
                "folderUid": d.get("folderUid"),
                "uri": d.get("uri"),
                "url": d.get("url"),
                "slug": d.get("slug"),
                "version": d.get("version"),
                "modified": d.get("modified"),
            }
            for d in dashboards
            if d.get("uid")
        ]
    except Exception as e:
        print(f"  ERROR: 获取 dashboard 列表失败: {e}")
        return []


def fetch_dashboard_detail(uid: str, env: str = "prod") -> dict | None:
    """获取 Dashboard 详情"""
    client = get_client("fincloud", env)
    try:
        detail = client.get_dashboard(uid)
        if detail and "dashboard" in detail:
            dashboard = detail["dashboard"]
            meta = detail.get("meta", {})
            return {
                "uid": dashboard.get("uid"),
                "title": dashboard.get("title"),
                "description": dashboard.get("description"),
                "tags": dashboard.get("tags", []),
                "timezone": dashboard.get("timezone"),
                "schemaVersion": dashboard.get("schemaVersion"),
                "version": dashboard.get("version"),
                "refresh": dashboard.get("refresh"),
                "folderId": meta.get("folderId"),
                "folderTitle": meta.get("folderTitle"),
                "folderUid": meta.get("folderUid"),
                "created": meta.get("created"),
                "createdBy": meta.get("createdBy"),
                "updated": meta.get("updated"),
                "updatedBy": meta.get("updatedBy"),
                "panels": _extract_panels(dashboard.get("panels", [])),
                "metrics": _extract_metrics(dashboard.get("panels", [])),
            }
    except Exception as e:
        print(f"  ERROR: 获取 dashboard {uid}: {e}")
    return None


def _extract_panels(panels: list[dict]) -> list[dict]:
    return [
        {
            "id": p.get("id"),
            "title": p.get("title"),
            "type": p.get("type"),
            "description": p.get("description"),
            "targets": len(p.get("targets", [])),
        }
        for p in panels
    ]


def _extract_metrics(panels: list[dict]) -> list[dict]:
    metrics: list[dict] = []
    for panel in panels:
        for target in panel.get("targets", []):
            info: dict = {
                "panel_id": panel.get("id"),
                "panel_title": panel.get("title"),
                "ref_id": target.get("refId"),
            }
            if "mql" in target:
                info["type"] = "mql"
                info["query"] = target["mql"]
                info["metric_name"] = _extract_metric_name(target["mql"])
            elif "expr" in target:
                info["type"] = "promql"
                info["query"] = target["expr"]
            elif "rawSql" in target:
                info["type"] = "sql"
                info["query"] = target["rawSql"]
            elif "query" in target:
                info["type"] = "query"
                info["query"] = target["query"]
            else:
                continue
            metrics.append(info)
    return metrics


def _extract_metric_name(mql: str) -> str | None:
    if not mql:
        return None
    if "{" in mql:
        return mql.split("{")[0].strip()
    if "[" in mql:
        return mql.split("[")[0].strip()
    return mql.strip()


def sync_dashboards_init(data: dict, env: str = "prod", max_workers: int = 5) -> dict:
    """全量同步 Dashboards"""
    print("\n== Dashboards 全量同步 ==")
    print("  获取 Dashboard 列表...")
    remote_list = fetch_dashboard_list(env, limit=1000)
    print(f"  发现 {len(remote_list)} 个 Dashboard")

    if not remote_list:
        return data

    print(f"  获取详情（并发 {max_workers}）...")
    details: list[dict] = []
    errors: list[str] = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(fetch_dashboard_detail, d["uid"], env): d["uid"]
            for d in remote_list
        }
        for future in as_completed(future_map):
            uid = future_map[future]
            try:
                detail = future.result()
                if detail:
                    details.append(detail)
                else:
                    errors.append(uid)
            except Exception:
                errors.append(uid)

    print(f"  成功 {len(details)}, 失败 {len(errors)}")

    data.setdefault("dashboards", {})
    data["dashboards"]["synced_at"] = datetime.now().isoformat()
    data["dashboards"]["total_count"] = len(remote_list)
    data["dashboards"]["success_count"] = len(details)
    data["dashboards"]["error_count"] = len(errors)
    data["dashboards"]["items"] = details
    return data


def sync_dashboards_update(
    data: dict, env: str = "prod", max_workers: int = 5, *, dry_run: bool = False
) -> dict:
    """增量更新 Dashboards"""
    print("\n== Dashboards 增量更新 ==")
    existing = data.get("dashboards", {}).get("items", [])
    if not existing:
        print("  本地数据为空，请先 --init")
        return data

    print("  获取远程列表...")
    remote_list = fetch_dashboard_list(env, limit=1000)
    if not remote_list:
        print("  ERROR: 获取远程列表失败")
        return data
    print(f"  远程 {len(remote_list)} 个")

    # 比对
    remote_map = {d["uid"]: d for d in remote_list}
    local_map = {d["uid"]: d for d in existing}

    to_add = [uid for uid in remote_map if uid not in local_map]
    to_update = [
        uid
        for uid, r in remote_map.items()
        if uid in local_map and r.get("version") != local_map[uid].get("version")
    ]
    to_delete = [uid for uid in local_map if uid not in remote_map]

    print(f"  新增: {len(to_add)}, 更新: {len(to_update)}, 删除: {len(to_delete)}")

    if dry_run:
        for uid in to_add[:5]:
            print(f"    + {remote_map[uid].get('title', uid)}")
        for uid in to_update[:5]:
            print(f"    ~ {remote_map[uid].get('title', uid)}")
        for uid in to_delete[:5]:
            print(f"    - {local_map[uid].get('title', uid)}")
        return data

    if not to_add and not to_update and not to_delete:
        print("  已是最新，无需更新")
        return data

    # 拉取变更详情
    changed = to_add + to_update
    new_map: dict[str, dict] = {}
    errors: list[str] = []
    if changed:
        print(f"  拉取变更详情（{len(changed)} 个）...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(fetch_dashboard_detail, uid, env): uid for uid in changed
            }
            for future in as_completed(future_map):
                uid = future_map[future]
                try:
                    detail = future.result()
                    if detail:
                        new_map[uid] = detail
                    else:
                        errors.append(uid)
                except Exception:
                    errors.append(uid)

    # 合并
    merged_map = {d["uid"]: d for d in existing}
    for uid in to_delete:
        merged_map.pop(uid, None)
    for uid, detail in new_map.items():
        merged_map[uid] = detail
    merged = list(merged_map.values())

    data.setdefault("dashboards", {})
    data["dashboards"]["synced_at"] = datetime.now().isoformat()
    data["dashboards"]["total_count"] = len(remote_list)
    data["dashboards"]["success_count"] = len(merged)
    data["dashboards"]["error_count"] = len(errors)
    data["dashboards"]["items"] = merged

    print(f"  合并后: {len(merged)} 个 (失败: {len(errors)})")
    return data


# ============================================================
# 查看 / 搜索 / BU 管理
# ============================================================

def check_status(data: dict) -> None:
    """检查同步状态"""
    apps = data.get("apps", {})
    dbs = data.get("dashboards", {})

    apps_ok = bool(apps.get("synced_at"))
    dbs_ok = bool(dbs.get("synced_at"))
    overall_status = "OK" if (apps_ok and dbs_ok) else "NEEDS_INIT"

    print(f"STATUS: {overall_status}")
    print(f"\n== 同步状态 ==\n")
    print(f"数据文件: {DATA_FILE}")
    if DATA_FILE.exists():
        print(f"文件大小: {DATA_FILE.stat().st_size / 1024:.0f} KB")
    print()

    print(f"Apps: {'OK' if apps_ok else 'NEEDS_INIT'}")
    print(f"  同步时间: {apps.get('synced_at') or '未同步'}")
    print(f"  应用数:   {apps.get('total_count', 0)}")
    print()

    print(f"Dashboards: {'OK' if dbs_ok else 'NEEDS_INIT'}")
    print(f"  同步时间: {dbs.get('synced_at') or '未同步'}")
    print(f"  总数:     {dbs.get('total_count', 0)}")
    print(f"  成功:     {dbs.get('success_count', 0)}")
    print(f"  失败:     {dbs.get('error_count', 0)}")


def list_items(data: dict, section: str, limit: int = 20) -> None:
    """列出已同步的数据"""
    items = data.get(section, {}).get("items", [])
    if not items:
        print(f"\n{section}: 暂无数据")
        return

    print(f"\n== {section} 列表 (前 {limit} 个，共 {len(items)}) ==\n")
    if section == "apps":
        for a in items[:limit]:
            app_name = a.get("name", "?")
            bu = a.get("bu", "?")
            print(f"  {app_name:40s}  type={a.get('type', '?'):6s}  bu={bu}")
    elif section == "dashboards":
        for d in items[:limit]:
            print(f"  [{d.get('uid', '?'):12s}] {d.get('title', 'N/A')[:50]}")
            print(f"    Folder: {d.get('folderTitle', 'N/A')}  Panels: {len(d.get('panels', []))}  Metrics: {len(d.get('metrics', []))}")


def search_items(data: dict, section: str, keyword: str) -> None:
    """搜索数据"""
    items = data.get(section, {}).get("items", [])
    kw = keyword.lower()

    if section == "apps":
        results = [a for a in items if kw in a.get("name", "").lower()]
    elif section == "dashboards":
        results = [
            d for d in items
            if kw in d.get("title", "").lower()
            or kw in d.get("uid", "").lower()
            or kw in (d.get("folderTitle") or "").lower()
        ]
    else:
        results = []

    print(f"\n搜索 '{keyword}' 在 {section} 中找到 {len(results)} 条\n")
    for item in results[:20]:
        if section == "apps":
            app_name = item.get("name", "?")
            bu = item.get("bu", "?")
            print(f"  {app_name:40s}  bu={bu}")
        else:
            print(f"  [{item.get('uid', '?'):12s}] {item.get('title', 'N/A')[:50]}")


def set_bu(data: dict, app_name: str, bu: str) -> dict:
    """直接修改应用列表中的应用 BU"""
    if bu not in ("main", "fincloud"):
        print(f"ERROR: bu 必须是 main 或 fincloud，实际为: {bu}")
        return data
    items = data.get("apps", {}).get("items", [])
    found = False
    for app in items:
        if app.get("name") == app_name:
            app["bu"] = bu
            found = True
            print(f"已设置 {app_name} → {bu}")
            break
    if not found:
        print(f"WARNING: 未找到应用 {app_name}，将创建新记录")
        data.setdefault("apps", {}).setdefault("items", [])
        data["apps"]["items"].append({
            "name": app_name,
            "bu": bu,
            "type": "unknown",
        })
        print(f"已添加 {app_name} → {bu}")
    return data


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="统一数据同步工具（apps + dashboards → data.json）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--init", action="store_true", help="全量初始化")
    parser.add_argument("--update", action="store_true", help="增量更新")
    parser.add_argument("--check", action="store_true", help="检查同步状态")
    parser.add_argument("--list", metavar="SECTION", choices=["apps", "dashboards"], help="列出数据")
    parser.add_argument("--search", nargs=2, metavar=("SECTION", "KEYWORD"), help="搜索数据")
    parser.add_argument("--set-bu", nargs=2, metavar=("APP", "BU"), help="手动设置应用 BU")
    parser.add_argument("--only", choices=["apps", "dashboards"], help="仅同步指定部分")
    parser.add_argument("--dry-run", action="store_true", help="预览变更")
    parser.add_argument("--env", default="prod", help="环境 (默认 prod)")
    parser.add_argument("--limit", type=int, default=20, help="列出数量限制")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    data = load_data()

    if args.init:
        only = args.only
        if not only or only == "apps":
            data = sync_apps(data, dry_run=args.dry_run)
        if not only or only == "dashboards":
            if args.dry_run:
                print("\n[dry-run] dashboards 全量同步跳过")
            else:
                data = sync_dashboards_init(data, args.env)
        if not args.dry_run:
            save_data(data)

    elif args.update:
        only = args.only
        if not only or only == "apps":
            data = sync_apps(data, dry_run=args.dry_run)
        if not only or only == "dashboards":
            data = sync_dashboards_update(data, args.env, dry_run=args.dry_run)
        if not args.dry_run:
            save_data(data)

    elif args.check:
        check_status(data)

    elif args.list:
        list_items(data, args.list, args.limit)

    elif args.search:
        section, keyword = args.search
        if section not in ("apps", "dashboards"):
            print(f"ERROR: section 必须是 apps 或 dashboards")
            sys.exit(1)
        search_items(data, section, keyword)

    elif args.set_bu:
        app_name, bu = args.set_bu
        data = set_bu(data, app_name, bu)
        save_data(data)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
