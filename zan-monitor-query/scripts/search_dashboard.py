#!/usr/bin/env python3
"""
Dashboard 本地搜索脚本

从 domain/data.json 中搜索匹配的面板和 MQL 查询。
纯本地搜索，无 API 调用，毫秒级响应。

用法:
  # 按指标名搜索
  python scripts/search_dashboard.py --metric "rpc_server_error_ratio_by_app"

  # 按用途关键词搜索（面板标题 + MQL）
  python scripts/search_dashboard.py --keyword "RPC 错误率"

  # 应用名仅作为弱排序辅助，不是首轮过滤条件
  python scripts/search_dashboard.py --keyword "error" --app "pay-payment-core"

  # 限制结果数量
  python scripts/search_dashboard.py --keyword "NSQ" --top 3

  # 列出所有含 MQL panel 的 dashboard（供 LLM 语义选择）
  python scripts/search_dashboard.py --list
  python scripts/search_dashboard.py --list --folder "支付技术"

  # 获取指定 dashboard 的 MQL metrics 详情
  python scripts/search_dashboard.py --metrics aVQuM8nIz
  python scripts/search_dashboard.py --metrics aVQuM8nIz --compact
"""

import argparse
import json
import re
import sys
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "domain" / "data.json"

# 中文关键词到英文的常见映射，辅助搜索（含反向映射）
KEYWORD_ALIASES = {
    # 中文 → 英文
    "错误率": ["error_ratio", "error", "fail", "错误"],
    "错误": ["error", "fail", "exception"],
    "延迟": ["latency", "duration", "centroid", "p99", "p95", "rt", "响应时间"],
    "堆积": ["depth", "backlog", "积压", "积压队列深度", "queue"],
    "积压": ["depth", "backlog", "堆积", "积压队列深度", "queue"],
    "消费": ["consumer", "channel", "消费者"],
    "连接池": ["pool", "druid", "activeCount", "maxActive", "connection"],
    "内存": ["memory", "heap", "jvm", "gc"],
    "线程": ["thread", "线程池"],
    "QPS": ["qpm", "qps", "throughput"],
    "流量": ["qpm", "qps", "count", "traffic"],
    "成功率": ["succ", "success", "成功"],
    "超时": ["timeout", "timed out"],
    "重试": ["retry", "requeue"],
    "健康": ["health", "healthy", "概览", "overview"],
    "概览": ["overview", "health", "健康", "总览"],
    "慢查询": ["slow", "slow_query", "慢sql"],
    "GC": ["gc", "garbage", "jvm", "内存"],
    # 英文 → 中文（反向映射）
    "error": ["错误", "错误率", "fail", "exception"],
    "latency": ["延迟", "rt", "响应时间", "centroid"],
    "RT": ["延迟", "latency", "centroid", "响应时间", "duration"],
    "timeout": ["超时", "timed out"],
    "depth": ["堆积", "积压", "backlog", "queue"],
    "backlog": ["堆积", "积压", "depth", "queue"],
    "pool": ["连接池", "druid", "activeCount"],
    "memory": ["内存", "heap", "jvm"],
    "thread": ["线程", "线程池"],
    "health": ["健康", "概览", "overview"],
    "overview": ["概览", "健康", "总览"],
}


def load_dashboards():
    """从 data.json 加载 dashboards 列表"""
    if not DATA_PATH.exists():
        print(json.dumps({"error": "data.json 不存在，请先执行: python3 scripts/sync-data.py --init"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("dashboards", {}).get("items", [])
    if not items:
        synced_at = data.get("dashboards", {}).get("synced_at")
        if not synced_at:
            print(json.dumps({"error": "Dashboard 数据未初始化，请先执行: python3 scripts/sync-data.py --init"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
    return items


def calculate_relevance(metric_entry, dashboard, keyword=None, metric_name=None, app_name=None):
    """计算候选结果的相关性分数 (0-1)"""
    score = 0.0
    match_type = "none"

    panel_title = metric_entry.get("panel_title") or ""
    query = metric_entry.get("query") or ""
    m_name = metric_entry.get("metric_name") or ""
    dash_title = dashboard.get("title") or ""

    # 1. 精确指标名匹配 → 最高分
    if metric_name and m_name:
        if m_name == metric_name:
            score = 1.0
            match_type = "exact"
            # app 名出现在 query 中额外加分
            if app_name and app_name in query:
                score = 1.0
            return score, match_type
        elif metric_name.lower() in m_name.lower():
            score = max(score, 0.8)
            match_type = "metric_name"

    # 2. 关键词匹配
    if keyword:
        kw_lower = keyword.lower()
        search_fields = f"{panel_title} {dash_title} {m_name} {query}".lower()

        # 直接关键词匹配
        if kw_lower in search_fields:
            # 面板标题精确匹配得分最高
            if kw_lower in panel_title.lower():
                score = max(score, 0.85)
                match_type = "panel_title"
            elif kw_lower in dash_title.lower():
                score = max(score, 0.75)
                match_type = "panel_title"
            elif kw_lower in m_name.lower():
                score = max(score, 0.80)
                match_type = "metric_name"
            else:
                score = max(score, 0.60)
                match_type = "mql_content"

        # 中文关键词→英文别名匹配
        aliases = KEYWORD_ALIASES.get(keyword, [])
        for alias in aliases:
            if alias.lower() in search_fields:
                s = 0.70 if alias.lower() in m_name.lower() else 0.55
                if s > score:
                    score = s
                    match_type = "panel_title" if alias.lower() in panel_title.lower() else "mql_content"

        # 多词关键词：所有词都匹配加分
        words = re.split(r"[\s,，]+", keyword)
        if len(words) > 1:
            matched_words = sum(1 for w in words if w.lower() in search_fields)
            if matched_words == len(words):
                score = max(score, 0.80)
                match_type = "panel_title"
            elif matched_words > 0:
                partial = 0.40 + 0.20 * (matched_words / len(words))
                if partial > score:
                    score = partial
                    match_type = "mql_content"

    # 3. app 名仅做弱排序加分，不改变“用途优先召回”的原则
    if app_name:
        query_lower = query.lower()
        if app_name.lower() in query_lower:
            score = min(score + 0.10, 1.0)
        elif app_name.lower() in dash_title.lower():
            score = min(score + 0.05, 1.0)

    return score, match_type


def list_dashboards(folder_filter: str | None = None) -> list[dict]:
    """列出所有含 MQL panel 的 dashboard（紧凑格式，供 LLM 语义选择）"""
    dashboards = load_dashboards()
    result = []
    for d in dashboards:
        metrics = d.get("metrics", [])
        mql_count = sum(1 for m in metrics if m.get("type") == "mql")
        if mql_count == 0:
            continue
        folder = d.get("folder") or ""
        if folder_filter and folder_filter.lower() not in folder.lower():
            continue
        result.append({
            "uid": d.get("uid", ""),
            "folder": folder,
            "title": d.get("title") or "",
            "panels": mql_count,
        })
    return result


def get_dashboard_metrics(uid: str, compact: bool = False) -> dict | None:
    """获取指定 dashboard 下的 MQL metrics 列表"""
    dashboards = load_dashboards()
    for d in dashboards:
        if d.get("uid") != uid:
            continue
        metrics = d.get("metrics", [])
        mql_metrics = []
        for m in metrics:
            if m.get("type") != "mql":
                continue
            entry: dict = {
                "panel_title": m.get("panel_title") or "",
                "metric_name": m.get("metric_name") or "",
            }
            if not compact:
                entry["mql"] = m.get("query") or ""
            mql_metrics.append(entry)
        return {
            "dashboard_uid": uid,
            "dashboard_title": d.get("title") or "",
            "metrics": mql_metrics,
        }
    return None


def search(keyword=None, metric_name=None, app_name=None, top_n=10):
    """执行搜索"""
    dashboards = load_dashboards()
    candidates = []

    for dashboard in dashboards:
        metrics = dashboard.get("metrics", [])
        if not metrics:
            continue

        for m in metrics:
            # 仅搜索 mql 类型的查询
            if m.get("type") != "mql":
                continue

            score, match_type = calculate_relevance(
                m, dashboard, keyword=keyword, metric_name=metric_name, app_name=app_name
            )

            if score > 0:
                candidates.append({
                    "dashboard_uid": dashboard.get("uid", ""),
                    "dashboard_title": dashboard.get("title", ""),
                    "panel_id": m.get("panel_id"),
                    "panel_title": m.get("panel_title", ""),
                    "mql": m.get("query", ""),
                    "metric_name": m.get("metric_name", ""),
                    "relevance_score": round(score, 2),
                    "match_type": match_type,
                })

    # 去重：相同 metric_name + 相同 mql 只保留得分最高的
    seen = {}
    for c in candidates:
        key = (c["metric_name"], c["mql"])
        if key not in seen or c["relevance_score"] > seen[key]["relevance_score"]:
            seen[key] = c
    candidates = list(seen.values())

    # 按分数排序
    candidates.sort(key=lambda x: x["relevance_score"], reverse=True)

    # 截取 top N
    candidates = candidates[:top_n]

    # 判断是否需要用户确认
    need_user_confirm = True
    if len(candidates) == 1 and candidates[0]["relevance_score"] >= 0.9:
        need_user_confirm = False
    elif len(candidates) == 0:
        need_user_confirm = False

    # 确定整体 match_type
    overall_match_type = "none"
    if candidates:
        overall_match_type = candidates[0]["match_type"]

    return {
        "match_type": overall_match_type,
        "candidates": candidates,
        "total_found": len(candidates),
        "need_user_confirm": need_user_confirm,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Dashboard 本地搜索 - 从 data.json 中搜索面板和 MQL"
    )
    parser.add_argument("--metric", help="按指标名精确搜索")
    parser.add_argument("--keyword", help="按用途关键词搜索（面板标题 + MQL 内容）")
    parser.add_argument("--app", help="应用名，仅用于弱排序辅助，不做严格过滤")
    parser.add_argument("--top", type=int, default=10, help="返回结果数量（默认 10）")
    parser.add_argument(
        "--compact", action="store_true",
        help="精简模式：仅输出 dashboard_title + panel_title + metric_name"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="列出所有含 MQL panel 的 dashboard（uid/folder/title/panels）"
    )
    parser.add_argument("--metrics", metavar="UID", help="返回指定 dashboard UID 的 MQL metrics 列表")
    parser.add_argument("--folder", help="--list 模式下按 folder 名称过滤")

    args = parser.parse_args()

    # --list 模式
    if args.list:
        result = list_dashboards(folder_filter=args.folder)
        print(json.dumps(result, ensure_ascii=False))
        return

    # --metrics 模式
    if args.metrics:
        result = get_dashboard_metrics(args.metrics, compact=args.compact)
        if result is None:
            print(json.dumps({"error": f"未找到 UID 为 {args.metrics} 的 dashboard"}, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if not args.metric and not args.keyword:
        parser.error("至少需要提供 --metric、--keyword、--list 或 --metrics 参数")

    result = search(
        keyword=args.keyword,
        metric_name=args.metric,
        app_name=args.app,
        top_n=args.top,
    )

    if args.compact:
        compact_result = {
            "match_type": result["match_type"],
            "total_found": result["total_found"],
            "need_user_confirm": result["need_user_confirm"],
            "candidates": [
                {
                    "dashboard_title": c["dashboard_title"],
                    "panel_title": c["panel_title"],
                    "metric_name": c["metric_name"],
                    "relevance_score": c["relevance_score"],
                }
                for c in result["candidates"]
            ],
        }
        print(json.dumps(compact_result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
