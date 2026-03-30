#!/usr/bin/env python3
"""dp 平台客户端 - 封装所有 API 交互的基础类"""

import requests
import json
import sys
import time
import re
from datetime import datetime, timedelta
from pathlib import Path

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, str(Path(__file__).parent))
from token_manager import get_site_config, get_site_auth_header, get_airflow_site_config


class DpClient:
    """dp 大数据平台客户端"""

    def __init__(self, site="fin"):
        self.site = site
        self._config = None

    @property
    def config(self):
        if not self._config:
            self._config = get_site_config(self.site)
            if not self._config:
                site_label = "主站" if self.site == "main" else "金融云"
                flag = "--save-main" if self.site == "main" else "--save"
                raise RuntimeError(
                    f"未找到{site_label} token 配置，"
                    f'请先运行: python3 scripts/token_manager.py {flag} "YOUR_COOKIE"'
                )
        return self._config

    def _headers(self):
        h = get_site_auth_header(self.site) or {}
        h["Content-Type"] = "application/json"
        return h

    def _check(self, resp):
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise RuntimeError(f"响应解析失败: {resp.text[:200]}")
        if data.get("code") != 0:
            raise RuntimeError(f"API错误: {data.get('msg', '未知错误')}")
        return data

    def _get(self, path, params=None):
        url = f"{self.config['base_url']}{path}"
        return self._check(requests.get(url, headers=self._headers(), params=params, verify=False))

    def _post(self, path, payload=None):
        url = f"{self.config['base_url']}{path}"
        return self._check(requests.post(url, headers=self._headers(), json=payload or {}, verify=False))

    def _run_query(self, sql, max_wait=10, limit_size=1000, engine="SPARK"):
        """提交 SQL 并轮询等待结果，返回 (uuid, engine, data)

        engine: 查询引擎，可选 SPARK/PRESTO/HIVE，默认 SPARK。传空字符串由服务端自动选择。
        """
        result = self._post("/v1/sql/run", {"sql": sql, "engine": engine, "confirm": False, "limitSize": limit_size})
        run_data = result.get("data", {})
        run_result = run_data.get("runResult", [])
        if not run_result:
            raise RuntimeError("查询提交失败")
        uuid = run_result[0]["key"]
        engine = run_data.get("engine", "PRESTO")
        for _ in range(max_wait):
            time.sleep(2)
            data = self._get(f"/v1/sql/history/{uuid}")
            if data.get("data", {}).get("completed", False):
                return uuid, engine, data
        raise RuntimeError(f"查询超时（等待 {max_wait * 2} 秒），UUID: {uuid}")

    def execute_sql(self, sql, max_wait=10, limit_size=1000, engine="SPARK"):
        """提交 SQL 并轮询等待结果"""
        _, _, data = self._run_query(sql, max_wait, limit_size, engine=engine)
        return data

    # === 数据查询 ===

    def list_databases(self):
        return self._get("/v1/hive/dbs-read")

    def list_tables(self, db):
        return self._get("/v1/hive/meta/getTables", {"db": db})

    def query(self, sql, engine="SPARK"):
        """执行 SQL 查询（提交 + 自动获取结果）"""
        return self.execute_sql(sql, engine=engine)

    def get_result(self, uuid):
        return self._get(f"/v1/sql/history/{uuid}")

    # === 表元数据 ===

    def table_schema(self, db, table):
        return self.execute_sql(f"DESC FORMATTED {db}.{table}")

    def table_columns(self, db, table):
        return self.execute_sql(f"DESC {db}.{table}")

    def table_partitions(self, db, table):
        return self.execute_sql(f"SHOW PARTITIONS {db}.{table}")

    def table_stats(self, db, table):
        return self.execute_sql(f"SELECT COUNT(*) as row_count FROM {db}.{table} LIMIT 1", max_wait=15, limit_size=1)

    def table_sample(self, db, table, limit=10):
        return self.execute_sql(f"SELECT * FROM {db}.{table} LIMIT {limit}", limit_size=limit)

    # === 数据血缘 ===

    @staticmethod
    def _yesterday():
        return (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    def lineage_upstream(self, db, table, par=None):
        par = par or self._yesterday()
        return self.execute_sql(f"""SELECT parent_db_name, parent_table_name, child_db_name, child_table_name, task_id, task_owner, task_url
                                FROM ods.md_lineage_table_table
                                WHERE par='{par}' AND child_db_name='{db}' AND child_table_name='{table}' LIMIT 100""")

    def lineage_downstream(self, db, table, par=None):
        par = par or self._yesterday()
        return self.execute_sql(f"""SELECT parent_db_name, parent_table_name, child_db_name, child_table_name, task_id, task_owner, task_url
                                FROM ods.md_lineage_table_table
                                WHERE par='{par}' AND parent_db_name='{db}' AND parent_table_name='{table}' LIMIT 100""")

    def lineage_column(self, db, table, column=None, par=None):
        par = par or self._yesterday()
        col_filter = f"AND child_column_name='{column}'" if column else ""
        return self.execute_sql(f"""SELECT parent_table_db_name, parent_table_name, parent_column_name,
                                child_table_db_name, child_table_name, child_column_name, relation_type, project_name,
                                MAX(updated_at) AS updated_at
                                FROM ods.md_lineage_column_column
                                WHERE par='{par}' AND child_table_db_name='{db}' AND child_table_name='{table}' {col_filter}
                                GROUP BY parent_table_db_name, parent_table_name, parent_column_name,
                                        child_table_db_name, child_table_name, child_column_name, relation_type, project_name
                                LIMIT 100""")

    def lineage_to_bi(self, db, table, par=None):
        par = par or self._yesterday()
        id_result = self.execute_sql(f"""SELECT DISTINCT parent_table_id
                                    FROM ods.md_lineage_column_column
                                    WHERE par='{par}' AND parent_table_db_name='{db}' AND parent_table_name='{table}' LIMIT 1""")
        id_data = id_result.get("data", {}).get("queryResult", [])
        if not id_data:
            id_result = self.execute_sql(f"""SELECT DISTINCT child_table_id
                                    FROM ods.md_lineage_column_column
                                    WHERE par='{par}' AND child_table_db_name='{db}' AND child_table_name='{table}' LIMIT 1""")
            id_data = id_result.get("data", {}).get("queryResult", [])
        if not id_data:
            return {"code": 0, "data": {"queryResult": [], "rows": 0}, "msg": "未找到该表的 table_id"}
        table_id = id_data[0][0]
        return self.execute_sql(f"""SELECT table_id, child_bi_id, bi_sql_id, created_at, updated_at
                                FROM ods.md_lineage_table_bi WHERE par='{par}' AND table_id={table_id} LIMIT 100""")

    # === 任务管理 ===

    def task_search(self, keyword):
        return self._get("/v1/jobs/search-job", {"desc": keyword})

    def task_workflow_detail(self, job_id):
        return self._get(f"/v1/jobs/workflow/{job_id}")

    def task_single_detail(self, job_id, job_type="code-hive"):
        return self._get(f"/v1/jobs/single/{job_id}", {"job-type": job_type})

    def task_list(self, page=1, page_size=10, filter_by_self=True):
        return self._get("/v1/jobs", {
            "filter-by-self": str(filter_by_self).lower(),
            "page-num": page, "page-size": page_size,
            "sort-field": "updateTime", "sort-order": "desc",
        })

    # === 数据导出 ===

    def _poll_apply(self, uuid, max_poll=30):
        """轮询导出审批状态，返回匹配的 apply 记录或 None

        判断逻辑：有 downloadUrl → 导出完成，再看 state 决定能否下载
        - 有 downloadUrl + AUTO/SUCCESS → 可下载
        - 有 downloadUrl + 其他状态 → 需人工审核
        - 无 downloadUrl → 还在处理中，继续轮询
        """
        for _ in range(max_poll):
            time.sleep(2)
            apply_result = self._get("/v1/apply/getApplyByType", {
                "isAdmin": "false", "isGroup": "false",
                "pageNum": 1, "pageSize": 10,
            })
            for item in apply_result.get("data", {}).get("items", []):
                details = item.get("applyDetails", {})
                if details.get("uuid") != uuid:
                    continue
                if details.get("downloadUrl"):
                    # 有下载链接 → 导出已完成
                    return item
                # 无下载链接 → 还在处理中，继续轮询
        return None

    def _handle_apply_result(self, item, output_path, filetype, rows):
        """根据审批状态决定下载或提示用户"""
        state = item.get("state")
        details = item.get("applyDetails", {})

        if state in ("AUTO", "SUCCESS"):
            download_url = details.get("downloadUrl")
            if download_url:
                return self._download_file(download_url, output_path, filetype, rows)
            raise RuntimeError("审批已通过但未获取到下载链接")

        # 需要人工审核
        site_label = "主站" if self.site == "main" else "金融云"
        base = "https://data.qima-inc.com" if self.site == "main" else "https://dp.fin.qima-inc.com"
        return {
            "status": "need_approval",
            "state": state,
            "rows": rows,
            "message": f"导出需要人工审核（{rows} 行），请到 dp 平台({site_label})手动审批后下载",
            "platform_url": base,
        }

    def export_dump(self, sql, filetype="excel", output_path=None, max_wait_dump=30, engine="SPARK"):
        """导出 SQL 查询结果为 Excel/CSV 文件

        流程：执行查询 → 提交导出 → 轮询审批状态 → 自动通过则下载，需审核则提示用户
        """
        # 1. 执行查询获取 uuid、engine 和行数
        uuid, engine, query_result = self._run_query(sql, max_wait=15, engine=engine)
        query_data = query_result.get("data", {})

        if not query_data.get("success"):
            raise RuntimeError(f"查询执行失败: {query_data.get('msg', query_result.get('msg', ''))}")

        rows = query_data.get("rows", 0)

        # 2. 提交导出请求
        self._post("/v1/sql/dump", {
            "sql": sql,
            "uuid": uuid,
            "engine": engine.lower(),
            "filetype": filetype,
        })

        # 3. 轮询审批状态
        item = self._poll_apply(uuid, max_poll=max_wait_dump)
        if not item:
            raise RuntimeError(f"导出超时（等待 {max_wait_dump * 2} 秒），UUID: {uuid}")

        return self._handle_apply_result(item, output_path, filetype, rows)

    def export_by_uuid(self, uuid, filetype="excel", output_path=None):
        """通过已有查询 UUID 导出（跳过查询步骤，直接查找下载链接）"""
        # 先获取查询结果信息
        query_result = self._get(f"/v1/sql/history/{uuid}")
        query_data = query_result.get("data", {})
        rows = query_data.get("rows", 0)
        sql = query_data.get("sql", "")
        engine = query_data.get("engine", "PRESTO")

        # 先检查是否已有现成的导出记录（有 downloadUrl 说明导出已完成）
        apply_result = self._get("/v1/apply/getApplyByType", {
            "isAdmin": "false", "isGroup": "false",
            "pageNum": 1, "pageSize": 10,
        })
        for item in apply_result.get("data", {}).get("items", []):
            details = item.get("applyDetails", {})
            if details.get("uuid") == uuid and details.get("downloadUrl"):
                ft = details.get("fileType", "").lower()
                if ft == filetype:
                    return self._handle_apply_result(item, output_path, filetype, rows)

        # 没有现成的，提交导出请求
        self._post("/v1/sql/dump", {
            "sql": sql, "uuid": uuid,
            "engine": engine.lower(), "filetype": filetype,
        })

        # 轮询审批状态
        item = self._poll_apply(uuid)
        if not item:
            raise RuntimeError(f"导出超时，UUID: {uuid}")

        return self._handle_apply_result(item, output_path, filetype, rows)

    def _download_file(self, url, output_path, filetype, rows):
        """下载文件到本地

        downloadUrl 的域名 (dp-download.prod.fin.qima-inc.com) 与 dp 平台不同，
        直接访问会被重定向到 SSO 登录页。需要提取路径部分，通过 dp 平台 base URL 代理下载。
        """
        if not output_path:
            ext = "xlsx" if filetype == "excel" else "csv"
            output_path = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

        # 提取下载路径，通过 dp 平台代理访问
        from urllib.parse import urlparse
        parsed = urlparse(url)
        download_path = parsed.path  # e.g. /v1/dump/center/download/20435
        proxy_url = f"{self.config['base_url']}{download_path}"

        resp = requests.get(proxy_url, headers=self._headers(), verify=False, stream=True)
        if resp.status_code != 200:
            raise RuntimeError(f"下载失败: HTTP {resp.status_code}")

        output_file = Path(output_path).resolve()
        with open(output_file, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return {
            "file": str(output_file),
            "size_bytes": output_file.stat().st_size,
            "rows": rows,
            "filetype": filetype,
        }


class AirflowClient:
    """Airflow 调度状态查询客户端"""

    def __init__(self, site="fin"):
        self.site = site
        self._config = None

    @property
    def config(self):
        if not self._config:
            self._config = get_airflow_site_config(self.site)
            if not self._config:
                site_label = "主站" if self.site == "main" else "金融云"
                raise RuntimeError(
                    f"未找到{site_label} Airflow cookie 配置，"
                    f'请先运行: python3 scripts/token_manager.py --save-airflow "YOUR_COOKIE"'
                )
        return self._config

    def _get_html(self, path, params=None):
        url = f"{self.config['base_url']}{path}"
        resp = requests.get(url, headers={"Cookie": self.config["cookie"]}, params=params, verify=False)
        if resp.status_code != 200:
            raise RuntimeError(f"Airflow 请求失败: HTTP {resp.status_code}")
        return resp.text

    def _get_json(self, path, params=None):
        url = f"{self.config['base_url']}{path}"
        resp = requests.get(url, headers={"Cookie": self.config["cookie"]}, params=params, verify=False)
        if resp.status_code == 200:
            try:
                return json.loads(resp.text)
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _extract_js_var(html, var_name):
        pattern = rf"var\s+{var_name}\s*=\s*(\[[\s\S]*?\]);|var\s+{var_name}\s*=\s*(\{{[\s\S]*?\}});"
        m = re.search(pattern, html)
        if m:
            try:
                return json.loads(m.group(1) or m.group(2))
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _extract_runs(html):
        return re.findall(r'<option\s+(?:selected\s+)?value="([^"]+)">[^<]*</option>', html)

    @staticmethod
    def _extract_schedule(html):
        m = re.search(r'schedule:\s*([^<]+)</a>', html)
        return m.group(1).strip() if m else None

    @staticmethod
    def _fmt_duration(seconds):
        if seconds is None: return "-"
        if seconds < 60: return f"{seconds:.1f}s"
        if seconds < 3600: return f"{seconds / 60:.1f}min"
        return f"{seconds / 3600:.1f}h"

    def dag_status(self, dag_id, execution_date=None):
        params = {"dag_id": dag_id, "arrange": "LR", "task_state": "All", "root": "", "filter": ""}
        if execution_date:
            params["execution_date"] = execution_date
        html = self._get_html("/admin/airflow/graph", params)

        task_instances = self._extract_js_var(html, "task_instances") or {}
        tasks = self._extract_js_var(html, "tasks") or {}
        edges = self._extract_js_var(html, "edges") or []
        runs = self._extract_runs(html)

        result = {
            "dag_id": dag_id,
            "schedule": self._extract_schedule(html),
            "execution_date": execution_date or (runs[0] if runs else None),
            "recent_runs": runs[:10],
        }

        task_list, state_summary = [], {}
        for tid, ti in task_instances.items():
            state = ti.get("state", "no_status")
            state_summary[state] = state_summary.get(state, 0) + 1
            task_list.append({
                "task_id": tid,
                "operator": ti.get("operator", tasks.get(tid, {}).get("task_type", "")),
                "state": state,
                "start_date": ti.get("start_date"),
                "end_date": ti.get("end_date"),
                "duration": self._fmt_duration(ti.get("duration")),
                "try_number": ti.get("try_number", 1),
                "hostname": ti.get("hostname"),
                "pool": ti.get("pool"),
            })
        task_list.sort(key=lambda x: x.get("start_date") or "")

        result["state_summary"] = state_summary
        result["tasks"] = task_list
        result["total_tasks"] = len(task_list)
        result["dependencies"] = [{"from": e["u"], "to": e["v"]} for e in edges]
        return result

    def task_detail(self, dag_id, execution_date, task_id=None):
        instances = self._get_json("/admin/airflow/object/task_instances", {"dag_id": dag_id, "execution_date": execution_date})
        if instances is None:
            params = {"dag_id": dag_id, "arrange": "LR", "task_state": "All", "root": "", "filter": "", "execution_date": execution_date}
            html = self._get_html("/admin/airflow/graph", params)
            instances = self._extract_js_var(html, "task_instances") or {}
        if task_id and isinstance(instances, dict):
            ti = instances.get(task_id)
            return {task_id: ti} if ti else {"error": f"任务 {task_id} 未找到"}
        return instances

    def dag_runs(self, dag_id):
        params = {"dag_id": dag_id, "arrange": "LR", "task_state": "All", "root": "", "filter": ""}
        html = self._get_html("/admin/airflow/graph", params)
        runs = self._extract_runs(html)
        return {"dag_id": dag_id, "schedule": self._extract_schedule(html), "total_runs": len(runs), "runs": runs}

    def task_log(self, dag_id, task_id, execution_date):
        """获取任务执行日志，保存到临时文件并返回路径"""
        import html as html_mod
        import tempfile
        params = {"dag_id": dag_id, "task_id": task_id, "execution_date": execution_date}
        page = self._get_html("/admin/airflow/log", params)
        m = re.search(r'<h4>Log</h4>\s*.*?<pre[^>]*>(.*?)</pre>', page, re.DOTALL)
        if not m:
            return {"error": "未找到日志内容"}
        log_text = html_mod.unescape(m.group(1)).strip()
        log_file = Path(tempfile.gettempdir()) / f"airflow_log_{dag_id}_{task_id}_{execution_date.replace(':', '-')}.log"
        log_file.write_text(log_text, encoding="utf-8")
        lines = log_text.splitlines()
        return {
            "dag_id": dag_id, "task_id": task_id, "execution_date": execution_date,
            "log_file": str(log_file), "total_lines": len(lines),
            "hint": "日志已保存到临时文件，使用 Read 工具读取文件分析关键信息",
        }
