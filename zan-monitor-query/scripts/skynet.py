#!/usr/bin/env python3
"""
Skynet API 统一 CLI — API 客户端 + CLI 工具合一。

子命令:
  query          MQL 统一查询（支持相对/绝对时间）
  multi-query    批量 MQL 查询（与 query-builder 输出兼容）
  list-metrics   列出应用指标（统一接口：--app 按应用查询，--keyword 全局搜索）
  search-app     搜索应用
  tag-values     获取指标 Tag 可能值
  alarm          查询单条 zan-alert 告警记录
  alarms         查询 zan-alert 告警记录列表
  resolve        统一短链解析（monitor/dashboard/log）
  list-monitors  按应用搜索监控项配置
  get-monitor    获取监控项 MQL + 告警阈值

用法:
  python3 scripts/skynet.py query --mql '...' --others '{"app":"pay-payment-core"}' --time 1h
  python3 scripts/skynet.py search-app "支付核心"
  python3 scripts/skynet.py resolve --id 9363 --type monitor
  python3 scripts/skynet.py alarms --page-size 5  # 不传 username 则自动从 token 获取
  python3 scripts/skynet.py list-monitors --app pay-payment-core
  python3 scripts/skynet.py get-monitor 13515
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _json_dumps_compact(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# 导入 token 管理器
sys.path.insert(0, str(Path(__file__).parent))
try:
    from token_manager import TokenManager, get_token
except ImportError:

    def get_token():
        return os.getenv("SKYNET_COOKIE", "")


# ===========================================================================
# SECTION 1: API Client
# ===========================================================================


class SkynetClient:
    """Skynet 监控平台客户端"""

    OPS_BU_ID_MAP = {
        "main": 1,
        "fincloud": 2,
    }

    # 应用 BU 映射（硬编码兜底）
    DEFAULT_APP_BU_MAP = {
        # 金融云应用 (fincloud)
        "pay-payment-core": "fincloud",
        "pay-acctrans": "fincloud",
        "pay-customer": "fincloud",
        "pay-payment-gateway": "fincloud",
        "pay-payment-channel": "fincloud",
        "pay-order": "fincloud",
        "pay-risk": "fincloud",
        "pay-marketing": "fincloud",
        "pay-reconcile": "fincloud",
        "pay-settlement": "fincloud",
    }

    # BU 检测规则
    BU_DETECTION_RULES = [
        ("^pay-", "fincloud"),  # 以 pay- 开头 -> 金融云
        ("^youzan-", "main"),  # 以 youzan- 开头 -> 主站
        ("^sc-", "main"),  # 以 sc- 开头 -> 主站
        ("^yz-", "main"),  # 以 yz- 开头 -> 主站
    ]

    def __init__(self, bu=None, env="prod", app_name=None):
        self.env = env
        self.app_name = app_name

        if bu:
            self.bu = bu
        elif app_name:
            self.bu = self._detect_bu(app_name)
        else:
            self.bu = "main"

        self.base_url = "https://ops.qima-inc.com/v3/skynet"
        self.ops_url = "https://ops.qima-inc.com"
        self.grafana_url = "https://skynet-grafana.prod.qima-inc.com"

        # 初始化 token 管理器
        self.token_manager = TokenManager()

    def _get_app_tag_name(self, metric_name):
        """根据指标名确定应用 tag 名称（app 或 appReporter）

        规则：NSQ 指标使用 app tag，其余使用 appReporter。
        """
        if "nsq" in metric_name.lower():
            return "app"
        return "appReporter"

    def _detect_bu(self, app_name):
        """根据应用名自动检测所属 BU

        优先级：data.json items > DEFAULT_APP_BU_MAP > 正则规则 > 默认 main
        """
        # 1. 从 data.json apps.items 列表查找
        bu = self._load_bu_from_data_json(app_name)
        if bu:
            return bu

        # 2. 硬编码兜底
        if app_name in self.DEFAULT_APP_BU_MAP:
            return self.DEFAULT_APP_BU_MAP[app_name]

        # 3. 正则规则
        for pattern, detected_bu in self.BU_DETECTION_RULES:
            if re.match(pattern, app_name):
                return detected_bu

        return "main"

    def _load_bu_from_data_json(self, app_name):
        """从 data.json 的 apps.items 列表加载 BU 信息"""
        try:
            data_file = Path(__file__).parent.parent / "domain" / "data.json"
            if data_file.exists():
                with open(data_file, "r") as f:
                    data = json.load(f)
                items = data.get("apps", {}).get("items", [])
                for app in items:
                    if app.get("name") == app_name:
                        return app.get("bu")
        except Exception:
            pass
        return None

    def _get_auth_cookie(self):
        """获取认证 Cookie"""
        token = self.token_manager.get_token()
        if not token:
            token = os.getenv("SKYNET_COOKIE", "")

        if not token:
            return {}

        if ";" in token:
            cookies = {}
            for part in token.split(";"):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    cookies[k.strip()] = v.strip()
            return cookies

        if token.startswith("eyJ"):
            return {"OPS_JWT_TOKEN": token}
        return {"cas": token}

    def _get_auth_cookie_header(self):
        """获取原始 Cookie 请求头值。"""
        token = self.token_manager.get_token()
        if not token:
            token = os.getenv("SKYNET_COOKIE", "")

        if not token:
            return None

        if ";" in token:
            return token

        if token.startswith("eyJ"):
            return f"OPS_JWT_TOKEN={token}"
        return f"cas={token}"

    def _headers(self, bu_id=None):
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "x-yz-bu": self.bu,
            "x-yz-env": self.env,
        }
        if bu_id is not None:
            headers["buid"] = str(bu_id)
        return headers

    def _check(self, resp):
        """检查响应状态"""
        if resp.status_code == 302:
            location = resp.headers.get("Location", "")
            raise RuntimeError(
                f"认证失败 (302 重定向到 {location}): Token 已过期\n"
                f"请更新 Token（共享 ~/.config/zan-tools/token.json）:\n"
                f"  python3 scripts/token_manager.py set '<OPS_JWT_TOKEN值>'"
            )

        try:
            data = resp.json()
        except json.JSONDecodeError:
            if "<html" in resp.text.lower()[:200]:
                raise RuntimeError(
                    f"认证失败: 返回登录页面，Token 已过期\n"
                    f"请更新 Token（共享 ~/.config/zan-tools/token.json）:\n"
                    f"  python3 scripts/token_manager.py set '<OPS_JWT_TOKEN值>'"
                )
            raise RuntimeError(f"响应解析失败: {resp.text[:200]}")

        if resp.status_code == 401:
            raise RuntimeError(
                f"认证失败 (401): Token 已过期\n"
                f"请更新 Token（共享 ~/.config/zan-tools/token.json）:\n"
                f"  python3 scripts/token_manager.py set '<OPS_JWT_TOKEN值>'"
            )

        if resp.status_code != 200:
            raise RuntimeError(f"HTTP错误 {resp.status_code}: {data}")

        return data

    def _get(self, path, params=None, use_grafana=False):
        """发送 GET 请求"""
        base = self.grafana_url if use_grafana else self.base_url
        url = f"{base}{path}"
        cookies = self._get_auth_cookie()
        return self._check(
            requests.get(
                url,
                headers=self._headers(),
                params=params,
                cookies=cookies,
                verify=False,
            )
        )

    def _post(self, path, payload=None):
        """发送 POST 请求"""
        url = f"{self.base_url}{path}"
        cookies = self._get_auth_cookie()
        return self._check(
            requests.post(
                url,
                headers=self._headers(),
                json=payload or {},
                cookies=cookies,
                verify=False,
            )
        )

    def _get_ops(self, path, params=None, bu_id=None):
        """发送 ops 根路径下的 GET 请求（非 /v3/skynet 接口）"""
        url = f"{self.ops_url}{path}"
        headers = self._headers(bu_id=bu_id)
        raw_cookie = self._get_auth_cookie_header()
        if raw_cookie:
            headers["Cookie"] = raw_cookie
        return self._check(
            requests.get(url, headers=headers, params=params, verify=False)
        )

    # === 应用管理 ===

    def list_apps(self):
        """获取所有应用列表"""
        return self._get("/v1/apps")

    def search_app(self, keyword):
        """搜索应用"""
        apps = self.list_apps()
        if isinstance(apps, list):
            return [
                app for app in apps if keyword.lower() in app.get("name", "").lower()
            ]
        return []

    def get_app_bu(self, app_name):
        """获取应用所属的 BU"""
        return self._detect_bu(app_name)

    # === 指标查询 ===

    def list_raw_metrics(self, page_size=100, page_number=1, id=None, name=None):
        """获取原始指标列表"""
        params = {"pageSize": page_size, "pageNumber": page_number}
        if id:
            params["id"] = id
        if name:
            params["name"] = name
        return self._get("/v2/rawMetrics", params)

    def list_derived_metrics(self, page_size=100, page_number=1, id=None):
        """获取派生指标列表"""
        params = {"pageSize": page_size, "pageNumber": page_number}
        if id:
            params["id"] = id
        return self._get("/v2/derivedMetrics", params)

    def search_metrics(self, keyword, metric_type="DERIVED_METRIC"):
        """搜索指标

        Args:
            keyword: 搜索关键词
            metric_type: 指标类型，DERIVED_METRIC / RAW_METRIC，或类型列表
        """
        if isinstance(metric_type, str):
            result = self._get(
                "/v2/mql/selectors", {"type": metric_type, "keyWords": keyword}
            )
            if isinstance(result, dict):
                items = result.get(metric_type)
                if isinstance(items, list):
                    return items
                items = result.get("items")
                if isinstance(items, list):
                    return items
            return result if isinstance(result, list) else []

        metric_types = []
        seen_types = set()
        for item in metric_type or []:
            if item and item not in seen_types:
                seen_types.add(item)
                metric_types.append(item)

        if not metric_types:
            return {}

        results = {}
        with ThreadPoolExecutor(max_workers=min(len(metric_types), 4)) as executor:
            future_map = {
                executor.submit(self.search_metrics, keyword, item): item
                for item in metric_types
            }
            for future in as_completed(future_map):
                item = future_map[future]
                results[item] = future.result()

        return {item: results.get(item, []) for item in metric_types}

    # === MQL 查询 ===

    def execute_mql(self, mql, start_time, end_time, granularity=None, others=None):
        """执行 MQL 查询"""
        gran = granularity or {"len": 60, "unit": "s"}

        # 替换 MQL 中的 ${granularity:SLIDING_WINDOW} 为实际滑动窗口格式
        # 注意：${timeRange:TIME_RANGE} 保留在 MQL 中，由 API 自动替换
        if "${granularity:SLIDING_WINDOW}" in mql:
            window_str = f"[{gran['len']}{gran['unit']}^{gran['len']}{gran['unit']}]"
            mql = mql.replace("${granularity:SLIDING_WINDOW}", window_str)

        # 提取 initialInputMetric：移除 timeRange 和 granularity 占位符后获取指标名
        mql_for_metric = mql.replace("${timeRange:TIME_RANGE}", "").replace(
            "${granularity:SLIDING_WINDOW}", ""
        )
        initial_metric = (
            mql_for_metric.split("{")[0].strip()
            if "{" in mql_for_metric
            else mql_for_metric.split("[")[0].strip()
        )

        query_payload = {
            "queryId": "Q1",
            "mql": mql,
            "initialInputMetric": initial_metric,
        }

        payload = {
            "queries": [query_payload],
            "params": {
                "timeRange": {"startTimeSecond": start_time, "endTimeSecond": end_time},
                "granularity": gran,
            },
        }

        if others:
            payload["params"]["others"] = others

        try:
            return self._post("/v2/mql:execute", payload)
        except RuntimeError as e:
            if "查询资源 Id 不存在" not in str(e):
                raise

            retry_query_payload = {"queryId": "Q1", "mql": mql}
            retry_payload = {
                "queries": [retry_query_payload],
                "params": payload["params"],
            }
            return self._post("/v2/mql:execute", retry_payload)

    def query_metric(self, metric_name, app, start_time, end_time, **tags):
        """简化版指标查询"""
        if app:
            detected_bu = self._detect_bu(app)
            if detected_bu != self.bu:
                new_client = SkynetClient(bu=detected_bu, env=self.env, app_name=app)
                return new_client.query_metric(
                    metric_name, app, start_time, end_time, **tags
                )

        app_tag = self._get_app_tag_name(metric_name)
        others = {app_tag: app}

        tag_parts = [f"{app_tag}=${{{app_tag}:STRING}}"]
        for k, v in tags.items():
            others[k] = v
            tag_parts.append(f"{k}=${{{k}:STRING}}")

        tag_filter = "{" + ",".join(tag_parts) + "}"

        mql = f"{metric_name}{tag_filter}${{timeRange:TIME_RANGE}} | time_aggr<${{granularity:SLIDING_WINDOW}}, sum> | tag_aggr<[], sum>"

        result = self.execute_mql(mql, start_time, end_time, others=others)

        if result and "results" in result:
            for r in result["results"]:
                if "timeSeries" in r:
                    series = r["timeSeries"]
                    if series and len(series) > 0:
                        return series[0].get("dataPoints", [])

        return []

    # === Tag 值查询 ===

    def get_tag_values(self, metric_name, tag_name, **filters):
        """获取指标 tag 的可能值"""
        filter_str = ""
        if filters:
            filter_parts = [f"({k}={v})" for k, v in filters.items()]
            filter_str = "?filter=" + "".join(filter_parts)

        path = f"/v2/metrics/{metric_name}/tags/{tag_name}/values{filter_str}"
        result = self._get(path)
        return result.get("items", []) if result else []

    # === Dashboard ===

    def list_folders(self):
        """获取 Grafana 文件夹列表"""
        return self._get("/api/folders", use_grafana=True)

    def list_dashboards(self, limit=200, folder_ids=None, query=None):
        """获取 Dashboard 列表"""
        params = {"limit": limit}
        if folder_ids:
            params["folderIds"] = ",".join(str(f) for f in folder_ids)
        if query:
            params["query"] = query
        return self._get("/api/search", params, use_grafana=True)

    def get_dashboard(self, uid):
        """获取 Dashboard 详情"""
        return self._get(f"/api/dashboards/uid/{uid}", use_grafana=True)

    def search_dashboards_by_app(self, app_name, folder_prefixes=None, limit=100):
        """按应用名搜索相关的 Dashboard"""
        search_terms = [
            app_name,
            app_name.replace("pay-", ""),
            app_name.replace("yz-", ""),
        ]

        try:
            folders = self.list_folders()
            folder_map = {f.get("id"): f for f in folders if isinstance(f, dict)}
        except Exception:
            folder_map = {}

        results = []
        seen_uids = set()

        for term in search_terms:
            if not term:
                continue

            try:
                dashboards = self.list_dashboards(query=term, limit=limit)

                for db in dashboards:
                    if not isinstance(db, dict):
                        continue

                    uid = db.get("uid")
                    if not uid or uid in seen_uids:
                        continue

                    folder_id = db.get("folderId")
                    if folder_prefixes and folder_id is not None:
                        folder = folder_map.get(folder_id, {})
                        folder_title = folder.get("title", "")
                        if not any(folder_title.startswith(p) for p in folder_prefixes):
                            continue

                    score = self._calc_dashboard_relevance(db, app_name, term)

                    seen_uids.add(uid)
                    results.append(
                        {
                            "uid": uid,
                            "title": db.get("title"),
                            "folderId": folder_id,
                            "folderTitle": db.get("folderTitle"),
                            "type": db.get("type"),
                            "url": db.get("url"),
                            "relevance_score": score,
                        }
                    )

            except Exception as e:
                print(f"Warning: 搜索 dashboard 失败 ({term}): {e}")

        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return results

    def _calc_dashboard_relevance(self, dashboard, app_name, search_term):
        """计算 dashboard 与应用的相关性分数"""
        score = 0
        title = dashboard.get("title", "").lower()
        lower_app = app_name.lower()
        lower_term = search_term.lower()

        if lower_app in title:
            score += 100
        elif lower_term in title:
            score += 80

        folder_title = dashboard.get("folderTitle", "").lower()
        if lower_app in folder_title or lower_term in folder_title:
            score += 50

        uri = dashboard.get("uri", "").lower()
        if lower_app in uri or lower_term in uri:
            score += 40

        return score

    def get_dashboard_metrics(self, uid):
        """获取 Dashboard 中的所有指标信息"""
        dashboard_data = self.get_dashboard(uid)

        if not dashboard_data or "dashboard" not in dashboard_data:
            return {"error": "Dashboard not found", "uid": uid}

        dashboard = dashboard_data["dashboard"]
        meta = dashboard_data.get("meta", {})

        result = {
            "uid": uid,
            "title": dashboard.get("title"),
            "description": dashboard.get("description"),
            "folderTitle": meta.get("folderTitle"),
            "folderUrl": meta.get("folderUrl"),
            "metrics": [],
        }

        for panel in dashboard.get("panels", []):
            panel_info = {
                "panel_id": panel.get("id"),
                "panel_title": panel.get("title"),
                "panel_type": panel.get("type"),
                "targets": [],
            }

            for target in panel.get("targets", []):
                target_info = {
                    "ref_id": target.get("refId"),
                    "datasource": target.get("datasource", {}).get("uid")
                    if isinstance(target.get("datasource"), dict)
                    else target.get("datasource"),
                }

                if "mql" in target:
                    target_info["type"] = "mql"
                    target_info["query"] = target["mql"]
                elif "expr" in target:
                    target_info["type"] = "promql"
                    target_info["query"] = target["expr"]
                elif "rawSql" in target:
                    target_info["type"] = "sql"
                    target_info["query"] = target["rawSql"]
                elif "query" in target:
                    target_info["type"] = "query"
                    target_info["query"] = target["query"]

                panel_info["targets"].append(target_info)

            if panel_info["targets"]:
                result["metrics"].append(panel_info)

        return result

    def extract_metrics_from_dashboard(self, uid):
        """从 Dashboard 中提取指标（简化版）"""
        metrics_info = self.get_dashboard_metrics(uid)

        if "error" in metrics_info:
            return []

        metrics = []
        for panel in metrics_info.get("metrics", []):
            for target in panel.get("targets", []):
                if "query" in target:
                    metrics.append(
                        {
                            "panel_title": panel.get("panel_title"),
                            "panel_type": panel.get("panel_type"),
                            "query_type": target.get("type"),
                            "query": target.get("query"),
                        }
                    )

        return metrics

    # === 双 BU 查询 ===

    def query_with_fallback(self, query_fn, *args, **kwargs):
        """双 BU 查询机制：先尝试当前 BU，如果失败或无数据则尝试另一个 BU"""
        primary_bu = self.bu
        fallback_bu = "main" if primary_bu == "fincloud" else "fincloud"

        result = {
            "success": False,
            "data": None,
            "source_bu": None,
            "fallback_used": False,
            "primary_result": None,
            "fallback_result": None,
        }

        try:
            primary_data = query_fn(self, *args, **kwargs)
            result["primary_result"] = {"success": True, "data": primary_data}

            has_data = self._check_has_data(primary_data)

            if has_data:
                result["success"] = True
                result["data"] = primary_data
                result["source_bu"] = primary_bu
                return result

        except Exception as e:
            result["primary_result"] = {"success": False, "error": str(e)}

        try:
            fallback_client = SkynetClient(bu=fallback_bu, env=self.env)
            fallback_data = query_fn(fallback_client, *args, **kwargs)
            result["fallback_result"] = {"success": True, "data": fallback_data}

            has_data = self._check_has_data(fallback_data)

            if has_data:
                result["success"] = True
                result["data"] = fallback_data
                result["source_bu"] = fallback_bu
                result["fallback_used"] = True
                return result

        except Exception as e:
            result["fallback_result"] = {"success": False, "error": str(e)}

        result["success"] = True
        result["data"] = (
            result["primary_result"].get("data") if result["primary_result"] else None
        )
        result["source_bu"] = primary_bu
        return result

    def _check_has_data(self, data):
        """检查查询结果是否包含有效数据"""
        if data is None:
            return False
        if isinstance(data, list):
            return len(data) > 0
        if isinstance(data, dict):
            if "dataPoints" in data:
                return len(data["dataPoints"]) > 0
            if "timeSeries" in data:
                return len(data["timeSeries"]) > 0
            if "items" in data:
                return len(data["items"]) > 0
            return len(data) > 0
        return bool(data)

    def query_metric_dual_bu(self, metric_name, app, start_time, end_time, **tags):
        """双 BU 指标查询，自动尝试 main 和 fincloud"""

        def do_query(client, metric, app_name, start, end, **query_tags):
            return client.query_metric(metric, app_name, start, end, **query_tags)

        return self.query_with_fallback(
            do_query, metric_name, app, start_time, end_time, **tags
        )

    def search_app_dual_bu(self, keyword):
        """双 BU 应用搜索"""

        def do_search(client, kw):
            return client.search_app(kw)

        return self.query_with_fallback(do_search, keyword)

    # === 监控项 ===

    def list_monitors(self, page_size=100, page_number=1, owning_app=None):
        """获取监控项列表"""
        params = {"pageSize": page_size, "pageNumber": page_number, "view": "CONFIG"}
        if owning_app:
            params["owningApp"] = owning_app
        return self._get("/v2/monitors", params)

    def get_monitor(self, monitor_id):
        """获取监控项详情"""
        return self._get(f"/v2/monitorWithNotifyingSettings/{monitor_id}")

    def get_alarm_record(self, record_id, bu_id=None):
        """获取 zan-alert 单条告警记录详情"""
        if bu_id is None:
            bu_id = self.OPS_BU_ID_MAP.get(self.bu, 2)

        result = self._get_ops(
            f"/api/v1.0/zan-alert/alarm/record/{record_id}",
            {"buId": bu_id},
            bu_id=bu_id,
        )

        if not isinstance(result, dict):
            raise RuntimeError(f"告警记录响应格式异常: {result}")

        if result.get("code") != 0 or result.get("success") is False:
            raise RuntimeError(
                f"查询告警记录失败: code={result.get('code')} message={result.get('message')}"
            )

        return result.get("data")

    def list_alarm_records(self, params=None, bu_id=None):
        """查询 zan-alert 告警记录列表"""
        if bu_id is None:
            bu_id = self.OPS_BU_ID_MAP.get(self.bu, 2)

        query_params = dict(params or {})
        query_params["buId"] = bu_id

        result = self._get_ops(
            "/api/v1.0/zan-alert/alarm/records",
            query_params,
            bu_id=bu_id,
        )

        if not isinstance(result, dict):
            raise RuntimeError(f"告警记录列表响应格式异常: {result}")

        if result.get("code") != 0 or result.get("success") is False:
            raise RuntimeError(
                f"查询告警记录列表失败: code={result.get('code')} message={result.get('message')}"
            )

        return result.get("data")


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------


def get_client(bu=None, env="prod", app_name=None):
    """获取 SkynetClient 实例"""
    return SkynetClient(bu, env, app_name)


def get_client_for_app(app_name, env="prod"):
    """根据应用名自动获取对应 BU 的客户端"""
    client = SkynetClient(env=env)
    bu = client._detect_bu(app_name)
    return SkynetClient(bu=bu, env=env, app_name=app_name)


def detect_app_bu(app_name):
    """检测应用所属 BU"""
    client = SkynetClient()
    return client._detect_bu(app_name)


def time_range(relative="1h"):
    """计算时间范围，返回 (start, end) Unix 时间戳秒"""
    end = int(time.time())

    unit = relative[-1]
    value = int(relative[:-1])

    if unit == "m":
        delta = value * 60
    elif unit == "h":
        delta = value * 3600
    elif unit == "d":
        delta = value * 86400
    else:
        delta = 3600

    start = end - delta
    return start, end


def query_both_bu(app_name, query_fn, env="prod", **kwargs):
    """双 BU 查询工具函数：自动尝试 main 和 fincloud 两个 BU，返回有数据的那个"""
    result = {
        "success": False,
        "data": None,
        "source_bu": None,
        "both_have_data": False,
        "main_data": None,
        "fincloud_data": None,
        "errors": [],
    }

    main_client = SkynetClient(bu="main", env=env, app_name=app_name)
    fincloud_client = SkynetClient(bu="fincloud", env=env, app_name=app_name)

    main_has_data = False
    fincloud_has_data = False

    try:
        result["main_data"] = query_fn(main_client, app_name, **kwargs)
        main_has_data = bool(result["main_data"])
        if isinstance(result["main_data"], list):
            main_has_data = len(result["main_data"]) > 0
    except Exception as e:
        result["errors"].append(f"main BU error: {e}")

    try:
        result["fincloud_data"] = query_fn(fincloud_client, app_name, **kwargs)
        fincloud_has_data = bool(result["fincloud_data"])
        if isinstance(result["fincloud_data"], list):
            fincloud_has_data = len(result["fincloud_data"]) > 0
    except Exception as e:
        result["errors"].append(f"fincloud BU error: {e}")

    result["both_have_data"] = main_has_data and fincloud_has_data

    if main_has_data and fincloud_has_data:
        result["success"] = True
        result["data"] = result["fincloud_data"]
        result["source_bu"] = "fincloud"
    elif fincloud_has_data:
        result["success"] = True
        result["data"] = result["fincloud_data"]
        result["source_bu"] = "fincloud"
    elif main_has_data:
        result["success"] = True
        result["data"] = result["main_data"]
        result["source_bu"] = "main"
    else:
        result["success"] = True
        result["data"] = result["main_data"] or result["fincloud_data"]
        result["source_bu"] = "main"

    return result


def get_client_dual_bu(app_name, env="prod"):
    """获取双 BU 客户端，返回 (main_client, fincloud_client)"""
    return (
        SkynetClient(bu="main", env=env, app_name=app_name),
        SkynetClient(bu="fincloud", env=env, app_name=app_name),
    )


# ===========================================================================
# SECTION 2: CLI Utilities
# ===========================================================================


def _parse_granularity(gran_str: str) -> dict[str, int | str]:
    """解析粒度字符串为 granularity 格式。

    支持格式：30s, 1m, 5m, 1h, 10m 等
    返回：{"len": 30, "unit": "s"}
    """
    if not gran_str:
        return None

    gran_str = gran_str.strip().lower()
    if gran_str.endswith("s"):
        return {"len": int(gran_str[:-1]), "unit": "s"}
    elif gran_str.endswith("m"):
        return {"len": int(gran_str[:-1]) * 60, "unit": "s"}
    elif gran_str.endswith("h"):
        return {"len": int(gran_str[:-1]) * 3600, "unit": "s"}
    else:
        # 默认为秒
        return {"len": int(gran_str), "unit": "s"}


def _compute_granularity(duration_seconds: int) -> dict[str, int | str]:
    """根据查询跨度推算合理的 granularity。

    注意：部分指标（如 NSQ）的 Metric 采集窗口为 60s，
    因此 short 粒度（30s）可能导致与 time_aggr 窗口不匹配。
    为保证兼容性，short 查询默认使用 60s。
    """
    if duration_seconds <= 600:
        g = 60  # 10m 以内使用 60s，避免与 Metric 60s 窗口冲突
    elif duration_seconds <= 1800:
        g = 60
    elif duration_seconds <= 7200:
        g = 60
    elif duration_seconds <= 21600:
        g = 300
    elif duration_seconds <= 86400:
        g = 600
    else:
        g = 3600
    return {"len": g, "unit": "s"}


def _parse_absolute_time(time_str: str) -> int:
    """解析绝对时间字符串为 Unix 时间戳（秒）。"""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return int(datetime.strptime(time_str, fmt).timestamp())
        except ValueError:
            continue
    try:
        return int(time_str)
    except ValueError:
        print(f"错误: 无法解析时间 '{time_str}'", file=sys.stderr)
        sys.exit(2)


def _parse_others(others_json: str) -> dict:
    """解析 --others 传入的 JSON 对象。"""
    try:
        data = json.loads(others_json)
    except json.JSONDecodeError as e:
        print(f"错误: --others 必须是合法 JSON 对象: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, dict):
        print(
            '错误: --others 必须是 JSON 对象，例如 \'{"app":"pay-payment-core","divisor":60}\'',
            file=sys.stderr,
        )
        sys.exit(2)

    return data


def _resolve_time_args(args: argparse.Namespace) -> tuple[int, int]:
    """从 --start/--end 或 --time 解析出 (start, end) 时间戳。"""
    if getattr(args, "start", None) and getattr(args, "end", None):
        start = _parse_absolute_time(args.start)
        end = _parse_absolute_time(args.end)
        if start >= end:
            print("错误: --start 必须早于 --end", file=sys.stderr)
            sys.exit(2)
        return start, end
    if getattr(args, "start", None) or getattr(args, "end", None):
        print("错误: --start 和 --end 必须同时指定", file=sys.stderr)
        sys.exit(2)
    relative = getattr(args, "time", None) or "1h"
    return time_range(relative)


def _enrich_timestamps(data: dict) -> dict:
    """为 dataPoints 添加人类可读 time 字段（HH:MM:SS）。"""
    results = data.get("results", [])
    for result in results:
        for series in result.get("timeSeries", []):
            for dp in series.get("dataPoints", []):
                ts = dp.get("timestamp", 0)
                if ts > 1e15:
                    ts_sec = ts / 1_000_000
                elif ts > 1e12:
                    ts_sec = ts / 1_000
                else:
                    ts_sec = ts
                dp["time"] = datetime.fromtimestamp(ts_sec).strftime("%H:%M:%S")
    return data


def _output(data: object) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _error_exit(e: Exception) -> None:
    print(json.dumps({"error": str(e)}, indent=2, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _metric_name(item: dict) -> str:
    return str(
        item.get("name")
        or item.get("metricName")
        or item.get("metric")
        or item.get("label")
        or ""
    )


def _metric_identity(item: dict) -> tuple[str, str, str]:
    metric_type = str(
        item.get("metric_type") or item.get("metricType") or item.get("type") or ""
    ).lower()
    metric_id = str(item.get("id") or item.get("metricId") or item.get("value") or "")
    metric_name = _metric_name(item)

    if metric_type or metric_id or metric_name:
        return metric_type, metric_id, metric_name

    return (
        metric_type,
        "",
        json.dumps(item, sort_keys=True, ensure_ascii=False, default=str),
    )


def _extract_items(result: object) -> list[dict]:
    if isinstance(result, dict):
        items = result.get("items")
        if isinstance(items, list):
            return [item for item in items if isinstance(item, dict)]
        return []
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]
    return []


def _merge_metric_batches(batches: list[dict]) -> tuple[list[dict], dict]:
    merged: dict[tuple[str, str, str], dict] = {}
    counts = {"derived": 0, "raw": 0}

    for batch in batches:
        metric_type = batch["metric_type"]
        source = batch["source"]
        priority_rank = batch["priority_rank"]
        priority_label = batch["priority_label"]

        for raw_item in batch["items"]:
            item = dict(raw_item)
            item["metric_type"] = metric_type
            key = _metric_identity(item)
            existing = merged.get(key)

            if not existing:
                item["priority"] = priority_label
                item["_priority_rank"] = priority_rank
                item["match_sources"] = [source]
                merged[key] = item
                counts[metric_type] += 1
                continue

            if source not in existing["match_sources"]:
                existing["match_sources"].append(source)

            if priority_rank < existing["_priority_rank"]:
                keep_sources = existing["match_sources"][:]
                keep_type = existing["metric_type"]
                existing.update(item)
                existing["metric_type"] = keep_type
                existing["priority"] = priority_label
                existing["_priority_rank"] = priority_rank
                existing["match_sources"] = keep_sources

    metrics = sorted(
        merged.values(),
        key=lambda item: (
            item["_priority_rank"],
            item.get("metric_type", ""),
            _metric_name(item),
            str(item.get("id") or item.get("metricId") or ""),
        ),
    )

    for item in metrics:
        item["match_count"] = len(item["match_sources"])
        item.pop("_priority_rank", None)

    return metrics, counts


def _str_bool(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return "true"
    if lowered in {"false", "0", "no", "n"}:
        return "false"
    raise argparse.ArgumentTypeError(f"布尔参数仅支持 true/false，实际为: {value}")


# ===========================================================================
# SECTION 3: CLI Commands
# ===========================================================================

# --- query ----------------------------------------------------------------


def cmd_query(args: argparse.Namespace) -> None:
    start, end = _resolve_time_args(args)

    # 优先使用用户传入的粒度，否则根据时间范围自动计算
    if args.granularity:
        granularity = _parse_granularity(args.granularity)
    else:
        granularity = _compute_granularity(end - start)

    others: dict | None = None
    if args.others:
        others = _parse_others(args.others)

    client = get_client(args.bu, args.env)
    try:
        data = client.execute_mql(
            args.mql, start, end, granularity=granularity, others=others
        )
        if isinstance(data, dict):
            data = _enrich_timestamps(data)
        _output(
            {
                "mql": args.mql,
                "start": start,
                "end": end,
                "start_time": datetime.fromtimestamp(start).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "end_time": datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S"),
                "granularity": granularity,
                "data_points": len(data) if isinstance(data, list) else 1,
                "data": data,
            }
        )
    except Exception as e:
        _error_exit(e)


# --- multi-query ----------------------------------------------------------


def cmd_multi_query(args: argparse.Namespace) -> None:
    try:
        with open(args.config) as f:
            queries: list[dict] = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"读取配置文件失败: {e}"}), file=sys.stderr)
        sys.exit(1)
    try:
        start, end = time_range(args.time)
        granularity = _compute_granularity(end - start)
        client = get_client(args.bu, args.env)

        results: dict[str, dict] = {}
        errors: dict[str, dict] = {}

        used_aliases: dict[str, int] = {}

        for idx, query in enumerate(queries, start=1):
            mql = query["mql"]
            base_alias = (
                query.get("alias")
                or query.get("queryId")
                or query.get("name")
                or f"query_{idx}"
            )
            alias = str(base_alias)
            if alias in used_aliases:
                used_aliases[alias] += 1
                alias = f"{alias}_{used_aliases[alias]}"
            else:
                used_aliases[alias] = 1
            others_dict = query.get("others")
            if others_dict is not None and not isinstance(others_dict, dict):
                raise RuntimeError(f"multi-query 配置中的 'others' 必须是对象: {alias}")
            try:
                data = client.execute_mql(
                    mql, start, end, granularity=granularity, others=others_dict
                )
                if isinstance(data, dict):
                    data = _enrich_timestamps(data)
                results[alias] = {
                    "mql": mql,
                    "data_points": len(data) if isinstance(data, list) else 1,
                    "data": data,
                }
            except Exception as e:
                errors[alias] = {"mql": mql, "error": str(e)}

        output: dict = {
            "time_range": args.time,
            "start_time": datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.fromtimestamp(end).strftime("%Y-%m-%d %H:%M:%S"),
            "queries_count": len(queries),
            "success_count": len(results),
            "error_count": len(errors),
            "results": results,
        }
        if errors:
            output["errors"] = errors
        _output(output)
    except Exception as e:
        _error_exit(e)


# --- list-metrics (统一接口) -----------------------------------------------


def cmd_list_metrics(args: argparse.Namespace) -> None:
    """统一指标查询接口：支持按应用名或关键词查询

    - app：既参与 id 查询，也参与 keyword 查询
    - keyword：仅参与 keyword 查询
    - 最终结果做并发查询、合集去重
    """
    client = get_client(args.bu, args.env)

    try:
        if not args.app and not args.keyword:
            print("错误: 必须指定 --app 或 --keyword 参数", file=sys.stderr)
            sys.exit(2)

        warnings = []
        tasks = []

        if args.app:
            tasks.extend(
                [
                    {
                        "source": "derived_id",
                        "metric_type": "derived",
                        "priority_rank": 0,
                        "priority_label": "high",
                        "query": lambda: _extract_items(
                            client.list_derived_metrics(
                                page_size=args.page_size,
                                page_number=1,
                                id=args.app,
                            )
                        ),
                    },
                    {
                        "source": "app_keyword_derived",
                        "metric_type": "derived",
                        "priority_rank": 1,
                        "priority_label": "high",
                        "query": lambda: _extract_items(
                            client.search_metrics(args.app, "DERIVED_METRIC")
                        ),
                    },
                    {
                        "source": "raw_id",
                        "metric_type": "raw",
                        "priority_rank": 2,
                        "priority_label": "normal",
                        "query": lambda: _extract_items(
                            client.list_raw_metrics(
                                page_size=args.page_size,
                                page_number=1,
                                id=args.app,
                            )
                        ),
                    },
                    {
                        "source": "app_keyword_raw",
                        "metric_type": "raw",
                        "priority_rank": 3,
                        "priority_label": "normal",
                        "query": lambda: _extract_items(
                            client.search_metrics(args.app, "RAW_METRIC")
                        ),
                    },
                ]
            )

        if args.keyword:
            tasks.extend(
                [
                    {
                        "source": "keyword_derived",
                        "metric_type": "derived",
                        "priority_rank": 4 if args.app else 0,
                        "priority_label": "high",
                        "query": lambda: _extract_items(
                            client.search_metrics(args.keyword, "DERIVED_METRIC")
                        ),
                    },
                    {
                        "source": "keyword_raw",
                        "metric_type": "raw",
                        "priority_rank": 5 if args.app else 1,
                        "priority_label": "normal",
                        "query": lambda: _extract_items(
                            client.search_metrics(args.keyword, "RAW_METRIC")
                        ),
                    },
                ]
            )

        batches = []
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            future_map = {executor.submit(task["query"]): task for task in tasks}
            for future in as_completed(future_map):
                task = future_map[future]
                try:
                    batches.append({**task, "items": future.result()})
                except Exception as e:
                    warning = f"{task['source']} 查询失败: {e}"
                    warnings.append(warning)
                    print(f"Warning: {warning}", file=sys.stderr)

        if not batches and warnings:
            raise RuntimeError("; ".join(warnings))

        metrics, counts = _merge_metric_batches(batches)
        source_counts = {
            batch["source"]: len(batch["items"])
            for batch in sorted(batches, key=lambda item: item["priority_rank"])
        }

        query_type = (
            "by_app_and_keyword"
            if args.app and args.keyword
            else "by_app"
            if args.app
            else "by_keyword"
        )
        output = {
            "query_type": query_type,
            "app": args.app,
            "keyword": args.keyword,
            "bu": args.bu,
            "env": args.env,
            "derived_count": counts["derived"],
            "raw_count": counts["raw"],
            "total_count": len(metrics),
            "source_counts": source_counts,
            "metrics": metrics if args.app else metrics[:50],
            "note": "app 同时按 id 和 keyword 查询；keyword 仅按 keyword 查询；最终结果已做合集去重，derived metrics 优先排在前面",
        }
        if not args.app:
            output["count"] = len(metrics)
        _output(output)

    except Exception as e:
        _error_exit(e)


# --- search-app -----------------------------------------------------------


def cmd_search_app(args: argparse.Namespace) -> None:
    client = get_client(args.bu, args.env)
    try:
        apps = client.search_app(args.keyword)
        _output({"keyword": args.keyword, "count": len(apps), "apps": apps[:20]})
    except Exception as e:
        _error_exit(e)


# --- tag-values -----------------------------------------------------------


def cmd_tag_values(args: argparse.Namespace) -> None:
    client = get_client(args.bu, args.env)
    try:
        filter_candidates: list[dict[str, str]] = []

        if args.app:
            primary_tag = client._get_app_tag_name(args.metric)
            for filter_dict in (
                {primary_tag: args.app},
                {"appReporter": args.app},
                {"app": args.app},
                {},
            ):
                if filter_dict not in filter_candidates:
                    filter_candidates.append(filter_dict)
        else:
            filter_candidates.append({})

        errors: list[dict[str, str]] = []
        values = []
        selected_filter: dict[str, str] = {}

        for filter_dict in filter_candidates:
            try:
                current_values = client.get_tag_values(
                    args.metric, args.tag, **filter_dict
                )
                if current_values:
                    values = current_values
                    selected_filter = filter_dict
                    break
                if not values:
                    selected_filter = filter_dict
            except Exception as e:
                errors.append(
                    {
                        "filter": _json_dumps_compact(filter_dict),
                        "error": str(e),
                    }
                )

        _output(
            {
                "metric": args.metric,
                "tag": args.tag,
                "app": args.app,
                "filter_used": selected_filter,
                "attempted_filters": filter_candidates,
                "count": len(values),
                "values": values,
                "warnings": errors,
            }
        )
    except Exception as e:
        _error_exit(e)


# --- alarm ----------------------------------------------------------------


def cmd_alarm(args: argparse.Namespace) -> None:
    client = get_client(args.bu, args.env)
    try:
        data = client.get_alarm_record(args.id, bu_id=args.bu_id)
        _output(
            {
                "record_id": int(args.id),
                "bu_id": args.bu_id
                if args.bu_id is not None
                else client.OPS_BU_ID_MAP.get(args.bu, 2),
                "data": data,
            }
        )
    except Exception as e:
        _error_exit(e)


# --- alarms ---------------------------------------------------------------


def cmd_alarms(args: argparse.Namespace) -> None:
    client = get_client(args.bu, args.env)

    username = args.username
    if not username:
        try:
            tm = TokenManager()
            token_info = tm.list_tokens()
            username = token_info.get("username")
        except Exception:
            pass

    params: dict = {"page_index": args.page_index, "page_size": args.page_size}
    optional_fields = {
        "username": username,
        "begin_time": args.begin_time,
        "end_time": args.end_time,
        "env": args.alarm_env,
        "level": args.level,
        "isFd": args.is_fd,
        "fdTypeKey": args.fd_type_key,
        "sendSuccess": args.send_success,
        "app": args.app,
    }
    for key, value in optional_fields.items():
        if value is not None:
            params[key] = value
    try:
        data = client.list_alarm_records(params=params, bu_id=args.bu_id)
        _output(
            {
                "bu_id": args.bu_id
                if args.bu_id is not None
                else client.OPS_BU_ID_MAP.get(args.bu, 2),
                "query": params,
                "data": data,
            }
        )
    except Exception as e:
        _error_exit(e)


# --- resolve --------------------------------------------------------------


def _resolve_short_url(url: str) -> str:
    result = subprocess.run(["curl", "-sI", "-L", url], capture_output=True, text=True)
    final_url = None
    for line in result.stdout.splitlines():
        if line.lower().startswith("location:"):
            final_url = line.split(":", 1)[1].strip()
    final_url = final_url or url

    if "l_special=" in final_url:
        parsed = urlparse(final_url)
        for qs_str in [
            parsed.query,
            parsed.fragment.split("?", 1)[-1] if "?" in parsed.fragment else "",
        ]:
            params = parse_qs(qs_str)
            if "l_special" in params:
                inner_url = unquote(params["l_special"][0])
                if "j.youzan.com" in inner_url:
                    return _resolve_short_url(inner_url)
                return inner_url
    return final_url


def _detect_url_type(url: str) -> str | None:
    decoded = unquote(url)
    if "monitor/items/update" in decoded:
        return "monitor"
    if "/i/d/" in decoded:
        return "dashboard"
    if "log/search" in decoded:
        return "log"
    return None


def _extract_monitor_info(url: str) -> tuple[str | None, str | None, str | None]:
    m = re.search(r"skynet/#/([^/]+)/([^/]+)/monitor/items/update/(\d+)", unquote(url))
    if not m:
        return None, None, None
    return m.group(3), m.group(1), m.group(2)


def _fetch_monitor_data(monitor_id: str, bu: str, env: str) -> dict:
    client = get_client(bu, env)
    data = client.get_monitor(monitor_id)
    return {
        "id": monitor_id,
        "bu": bu,
        "env": env,
        "name": data.get("name"),
        "owningApp": data.get("owningApp"),
        "enabled": data.get("enabled"),
        "metricQueries": [
            {
                "name": q.get("name"),
                "mql": q.get("rawQuery"),
                "detectionMethod": q.get("detectionMethod"),
            }
            for q in data.get("metricQueries", [])
        ],
        "triggers": {
            "notice": data.get("noticeTrigger"),
            "warning": data.get("warningTrigger"),
            "critical": data.get("criticalTrigger"),
        },
        "notifyGroups": data.get("notifyingSettings", {}).get("notifyGroupMap"),
        "notifyingLinks": data.get("notifyingLinks"),
        "description": data.get("description"),
    }


def _extract_dashboard_info(
    url: str,
) -> tuple[str | None, str | None, str | None, dict]:
    decoded = unquote(url)
    m = re.search(r"skynet/#/([^/]+)/([^/]+)/i/d/([^/?#]+)", decoded)
    if not m:
        return None, None, None, {}
    bu, env, uid = m.group(1), m.group(2), m.group(3)
    variables: dict = {}
    frag_idx = decoded.find("#")
    if frag_idx != -1:
        frag = decoded[frag_idx + 1 :]
        q_idx = frag.find("?")
        if q_idx != -1:
            qs = parse_qs(frag[q_idx + 1 :])
            for k, v in qs.items():
                variables[k] = v[0] if len(v) == 1 else v
    return uid, bu, env, variables


def _fetch_dashboard_data(
    uid: str, bu: str, env: str, variables: dict | None = None
) -> dict:
    client = get_client(bu, env)
    dashboard_data = client.get_dashboard(uid)
    title = None
    if isinstance(dashboard_data, dict):
        db = dashboard_data.get("dashboard", dashboard_data)
        title = db.get("title")
    panels = client.extract_metrics_from_dashboard(uid)
    return {
        "uid": uid,
        "bu": bu,
        "env": env,
        "title": title,
        "variables": variables or {},
        "panels": panels,
        "grafana_url": f"https://ops.qima-inc.com/v3/skynet/#/{bu}/{env}/i/d/{uid}",
    }


def _parse_log_params(url: str) -> dict:
    parsed = urlparse(url)
    fragment = parsed.fragment
    path_match = re.match(r"^/?([^/]+)/([^/]+)/log/search/", fragment)
    bu = path_match.group(1) if path_match else None
    env = path_match.group(2) if path_match else None
    if "?" not in fragment:
        return {"error": f"URL fragment 中无查询参数: {url}", "bu": bu, "env": env}
    qs_str = fragment.split("?", 1)[1]
    params = parse_qs(qs_str, keep_blank_values=True)
    result: dict = {}
    if bu:
        result["bu"] = bu
    if env:
        result["env"] = env
    if "appName" in params:
        result["app"] = params["appName"][0]
    if "timeRange" in params:
        time_parts = params["timeRange"][0].split(",")
        if len(time_parts) == 2:
            result["timestampBeginMs"] = int(time_parts[0])
            result["timestampEndMs"] = int(time_parts[1])
    if "hostname" in params:
        result["hostname"] = params["hostname"][0]
    if "levelArray" in params:
        result["levelArray"] = params["levelArray"][0].split(",")
    if "tags" in params:
        try:
            result["tagConditions"] = json.loads(params["tags"][0])
        except (json.JSONDecodeError, IndexError):
            result["tagConditions_raw"] = params["tags"][0]
    if "queryString" in params:
        result["queryString"] = params["queryString"][0]
    if "direction" in params:
        result["direction"] = params["direction"][0]
    if "limit" in params:
        result["limit"] = int(params["limit"][0])
    if "order" in params:
        result["order"] = params["order"][0]
    return result


def _resolve(
    url: str | None = None,
    *,
    url_type: str | None = None,
    monitor_id: str | None = None,
    dashboard_uid: str | None = None,
    bu: str | None = None,
    env: str | None = None,
) -> dict:
    if monitor_id:
        return {
            "type": "monitor",
            "resolved_url": None,
            "data": _fetch_monitor_data(monitor_id, bu or "fincloud", env or "prod"),
        }
    if dashboard_uid:
        return {
            "type": "dashboard",
            "resolved_url": None,
            "data": _fetch_dashboard_data(
                dashboard_uid, bu or "fincloud", env or "prod"
            ),
        }
    if not url:
        return {"error": "必须提供 --url 或 --id/--uid"}

    resolved_url = _resolve_short_url(url) if "j.youzan.com" in url else url
    detected = url_type or _detect_url_type(resolved_url)
    if not detected:
        return {
            "error": f"无法识别 URL 类型: {resolved_url}",
            "resolved_url": resolved_url,
        }

    if detected == "monitor":
        mid, extracted_bu, extracted_env = _extract_monitor_info(resolved_url)
        if not mid:
            return {"error": f"无法从 URL 提取 monitor_id: {resolved_url}"}
        return {
            "type": "monitor",
            "resolved_url": resolved_url,
            "data": _fetch_monitor_data(
                mid, bu or extracted_bu, env or extracted_env or "prod"
            ),
        }

    if detected == "dashboard":
        uid, extracted_bu, extracted_env, variables = _extract_dashboard_info(
            resolved_url
        )
        if not uid:
            return {"error": f"无法从 URL 提取 dashboard UID: {resolved_url}"}
        return {
            "type": "dashboard",
            "resolved_url": resolved_url,
            "data": _fetch_dashboard_data(
                uid, bu or extracted_bu, env or extracted_env or "prod", variables
            ),
        }

    if detected == "log":
        return {
            "type": "log",
            "resolved_url": resolved_url,
            "data": _parse_log_params(resolved_url),
        }

    return {"error": f"不支持的类型: {detected}"}


def cmd_resolve(args: argparse.Namespace) -> None:
    try:
        result = _resolve(
            url=args.url,
            url_type=args.type,
            monitor_id=args.id,
            dashboard_uid=args.uid,
            bu=args.bu,
            env=args.env,
        )
        _output(result)
        if "error" in result:
            sys.exit(1)
    except Exception as e:
        _error_exit(e)


# --- list-monitors --------------------------------------------------------


def cmd_list_monitors(args: argparse.Namespace) -> None:
    """按应用搜索监控项配置"""
    client = get_client(args.bu, args.env)
    try:
        data = client.list_monitors(
            page_size=args.page_size,
            page_number=args.page_number,
            owning_app=args.app,
        )
        items = data.get("items", []) if isinstance(data, dict) else []

        if args.app:
            items = [
                m
                for m in items
                if args.app.lower() in (m.get("owningApp") or "").lower()
                or args.app.lower() in (m.get("name") or "").lower()
            ]

        _output(
            {
                "app_filter": args.app,
                "page_number": args.page_number,
                "page_size": args.page_size,
                "total_size": data.get("totalSize") if isinstance(data, dict) else None,
                "count": len(items),
                "monitors": items,
            }
        )
    except Exception as e:
        _error_exit(e)


# --- get-monitor ----------------------------------------------------------


def cmd_get_monitor(args: argparse.Namespace) -> None:
    """获取监控项 MQL + 告警阈值"""
    client = get_client(args.bu, args.env)
    try:
        data = client.get_monitor(args.monitor_id)
        _output(
            {
                "monitor_id": args.monitor_id,
                "name": data.get("name"),
                "owningApp": data.get("owningApp"),
                "enabled": data.get("enabled"),
                "description": data.get("description"),
                "metricQueries": [
                    {
                        "name": q.get("name"),
                        "mql": q.get("rawQuery"),
                        "detectionMethod": q.get("detectionMethod"),
                    }
                    for q in data.get("metricQueries", [])
                ],
                "triggers": {
                    "notice": data.get("noticeTrigger"),
                    "warning": data.get("warningTrigger"),
                    "critical": data.get("criticalTrigger"),
                },
                "notifyGroups": data.get("notifyingSettings", {}).get("notifyGroupMap"),
                "notifyingLinks": data.get("notifyingLinks"),
            }
        )
    except Exception as e:
        _error_exit(e)


# ===========================================================================
# SECTION 4: CLI Entry Point
# ===========================================================================


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--bu", default="fincloud", help="业务线: fincloud/main（默认 fincloud）"
    )
    parser.add_argument("--env", default="prod", help="环境: qa/pre/prod（默认 prod）")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Skynet API 统一 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subs = parser.add_subparsers(dest="command", required=True)

    # query
    p = subs.add_parser("query", help="MQL 统一查询")
    p.add_argument("--mql", required=True, help="MQL 查询语句")
    p.add_argument("--time", default=None, help="相对时间范围，如 30m, 1h, 6h, 1d")
    p.add_argument("--start", default=None, help="绝对开始时间")
    p.add_argument("--end", default=None, help="绝对结束时间")
    p.add_argument(
        "--others",
        default=None,
        help='MQL 变量 JSON 对象，直接映射到 params.others，如 \'{"app":"pay-trading-query","divisor":60}\'',
    )
    p.add_argument(
        "--granularity",
        default=None,
        help="聚合粒度，如 30s, 1m, 5m, 1h。不指定则根据时间范围自动计算",
    )
    _add_common_args(p)

    # multi-query
    p = subs.add_parser("multi-query", help="批量 MQL 查询")
    p.add_argument("--config", required=True, help="查询配置文件路径（JSON）")
    p.add_argument("--time", default="1h", help="时间范围")
    _add_common_args(p)

    # list-metrics (统一接口)
    p = subs.add_parser(
        "list-metrics",
        help="列出应用指标（统一接口：--app 按应用查询，--keyword 全局搜索）",
    )
    p.add_argument(
        "--app",
        default=None,
        help="应用名（优先返回 derived metrics，再返回 raw metrics）",
    )
    p.add_argument("--keyword", default=None, help="关键词全局搜索")
    p.add_argument("--page-size", type=int, default=100, help="每页条数（默认 100）")
    _add_common_args(p)

    # search-app
    p = subs.add_parser("search-app", help="搜索应用")
    p.add_argument("keyword", help="搜索关键词")
    _add_common_args(p)

    # tag-values
    p = subs.add_parser("tag-values", help="获取指标 Tag 值")
    p.add_argument("--metric", required=True, help="指标名称")
    p.add_argument("--tag", required=True, help="Tag 名称")
    p.add_argument("--app", required=False, help="应用名（可选，用于自动补过滤条件）")
    _add_common_args(p)

    # alarm
    p = subs.add_parser("alarm", help="查询单条告警记录")
    p.add_argument("--id", required=True, help="告警记录 ID")
    p.add_argument("--bu-id", type=int, default=None, help="zan-alert buId")
    _add_common_args(p)

    # alarms
    p = subs.add_parser("alarms", help="查询告警记录列表")
    p.add_argument(
        "--username",
        help="用户名（可选，不传则自动从 token 获取）",
    )
    p.add_argument("--begin-time", type=int, help="开始时间戳（秒）")
    p.add_argument("--end-time", type=int, help="结束时间戳（秒）")
    p.add_argument("--page-index", type=int, default=0, help="分页起始页")
    p.add_argument("--page-size", type=int, default=10, help="每页条数")
    p.add_argument("--alarm-env", help="告警环境筛选")
    p.add_argument("--level", help="告警级别")
    p.add_argument("--is-fd", type=_str_bool, help="是否只看 fd 告警")
    p.add_argument("--fd-type-key", help="fd 类型")
    p.add_argument("--send-success", type=_str_bool, help="发送是否成功")
    p.add_argument("--app", help="应用名筛选")
    p.add_argument("--bu-id", type=int, default=None, help="zan-alert buId")
    _add_common_args(p)

    # resolve
    p = subs.add_parser("resolve", help="统一短链解析")
    p.add_argument("--url", help="短链接或完整 ops URL")
    p.add_argument("--type", choices=["monitor", "dashboard", "log"], help="指定类型")
    p.add_argument("--id", help="监控项 ID")
    p.add_argument("--uid", help="Dashboard UID")
    p.add_argument("--bu", default=None, help="业务线")
    p.add_argument("--env", default=None, help="环境")

    # list-monitors
    p = subs.add_parser("list-monitors", help="按应用搜索监控项配置")
    p.add_argument(
        "--app", default=None, help="应用名过滤（模糊匹配 owningApp 或 name）"
    )
    p.add_argument("--page-size", type=int, default=100, help="每页条数（默认 100）")
    p.add_argument("--page-number", type=int, default=1, help="页码（默认 1）")
    _add_common_args(p)

    # get-monitor
    p = subs.add_parser("get-monitor", help="获取监控项 MQL + 告警阈值")
    p.add_argument("monitor_id", help="监控项 ID")
    _add_common_args(p)

    return parser


_DISPATCH = {
    "query": cmd_query,
    "multi-query": cmd_multi_query,
    "list-metrics": cmd_list_metrics,
    "search-app": cmd_search_app,
    "tag-values": cmd_tag_values,
    "alarm": cmd_alarm,
    "alarms": cmd_alarms,
    "resolve": cmd_resolve,
    "list-monitors": cmd_list_monitors,
    "get-monitor": cmd_get_monitor,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    handler = _DISPATCH.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
