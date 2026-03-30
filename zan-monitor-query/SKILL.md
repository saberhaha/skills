---
name: zan-monitor-query
description: 智能监控指标查询与系统告警分析专家。用于理解业务人员的自然语言描述，自动转换为精确的监控指标查询（MQL），并提供专业的数据分析和根因推断。当用户询问监控指标、告警信息、查询应用性能数据、分析系统异常、排查故障系统信息时使用。
---

# zan-monitor-query 智能监控 Agent

## 前置条件

首次使用前需初始化本地数据：
```bash
python3 scripts/sync-data.py --check    # 检查状态
python3 scripts/sync-data.py --init     # 全量初始化
python3 scripts/sync-data.py --update   # 增量更新（建议每周）
```

主流程启动时自动检测：若 data.json 中 synced_at 为 null，提示并自动执行初始化。

## 工作流程

```
用户输入 → [URL? → skynet.py resolve]
         → intent-planner（意图理解 + 搜索指令生成）
         → 主流程执行搜索（search_dashboard.py / skynet.py list-metrics）
         → query-builder（基于搜索结果构建 MQL）  ← 引用 @references/mql-patterns.md
         → skynet.py query 执行
         → analyst（数据分析）
```

### 执行步骤

1. **URL 预解析**（如有）：输入含 `j.youzan.com` 时，先 `skynet.py resolve` 获取结构化数据作为上下文
2. **意图理解**：调用 `intent-planner`，输出结构化意图 + `search_commands`（要执行的搜索命令列表）
3. **执行搜索**：主流程按 `search_commands` 逐条执行以下搜索，收集候选结果：
   - `search_dashboard.py` - Dashboard 面板搜索
   - `skynet.py list-metrics` - 应用指标查询（统一接口：--app 按应用查询，--keyword 全局搜索）
4. **构建查询**：将意图 + 搜索结果传给 `query-builder`，构建可执行的 MQL
5. **执行 & 分析**：`skynet.py query` 执行查询，结果交给 `analyst` 输出分析报告

关键原则：
- Dashboard 搜索按**监控用途/指标语义**召回，不按应用名；应用名用于搜索后的参数注入

## Agent 文件

| Agent | 文件 | 职责 |
|-------|------|------|
| intent-planner | agents/intent-planner.md | 理解意图、识别应用/指标、生成搜索命令 |
| query-builder | agents/query-builder.md | 基于搜索结果构建 MQL |
| analyst | agents/analyst.md | 分析查询结果数据 |

## 数据文件

| 文件 | 用途 | 加载方式 |
|------|------|---------|
| domain/data.json | 应用列表 + Dashboard 面板数据 | apps: 直接读取；dashboards: 通过 search_dashboard.py 搜索。需 `sync-data.py --init` 初始化 |
| references/mql-patterns.md | MQL 常用模式、Tag 选择规则 | 仅 query-builder 构建 MQL 时引用 |
| references/skynet-api.md | Skynet API 参考 | 需调 API 时加载 |

## Scripts 工具库

> **重要**：MQL 查询中的动态参数必须使用 `${varName:TYPE}` 占位符，禁止硬编码。标准注入方式是底层 `params.others` 保留 JSON 原生类型；单条查询使用 `query --others '<JSON对象>'`，批量查询在配置中使用 `others`。

### BU/ENV 参数说明

**所有 skynet.py 命令（除 token_manager.py 和 sync-data.py 外）都需要指定 `--bu` 参数：**

| 参数 | 可选值 | 说明 |
|------|--------|------|
| `--bu` | `fincloud`（默认）/ `main` | **金融云应用**（pay- 开头）用 fincloud；**主站应用**用 main |
| `--env` | `qa` / `pre` / `prod`（默认 prod） | 环境筛选 |

**BU 自动检测规则**：`^pay-` 开头通常为 fincloud，其余应用通常为 main；但这只是启发式规则，必须以 `domain/data.json`、`list-monitors`、`alarms`、`resolve`、真实查询结果为准。像 `yz-settle-center` 这样的应用就可能不符合简单前缀规则。

```bash
# Dashboard 本地搜索
python3 scripts/search_dashboard.py --metric "rpc_server_error_ratio_by_app"
python3 scripts/search_dashboard.py --keyword "RPC 错误率" --compact --top 5
python3 scripts/search_dashboard.py --keyword "NSQ 堆积" --compact --top 5

# Dashboard 列表（供 LLM 语义选择，~496 条，~15KB）
python3 scripts/search_dashboard.py --list
python3 scripts/search_dashboard.py --list --folder "支付技术"

# 指定 Dashboard 的 MQL metrics 详情
python3 scripts/search_dashboard.py --metrics <uid>
python3 scripts/search_dashboard.py --metrics <uid> --compact

# MQL 统一查询（支持相对时间和绝对时间，--bu 必须指定）
python3 scripts/skynet.py query --mql 'nsq_channel_depth_by_app_topic_partition_idc_env_cluster{app=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum>' --others '{"app":"pay-trading-query"}' --time 1h --bu fincloud
python3 scripts/skynet.py query --mql 'rpc_server_error_ratio_by_app{appReporter=${appReporter:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, max>' --others '{"appReporter":"video-channels-flow"}' --time 30m --bu main --env prod

# 注意：不要写 `time_aggr<24h, sum>` 这类 Duration 用法
# 看趋势：`time_aggr<${granularity:SLIDING_WINDOW}, ...>` + `--granularity 1h/5m/...`
# 看整个时间范围汇总：`time_aggr<sum>`

# 粒度控制（大模型应根据意图选择合适的粒度，不指定则自动计算）
python3 scripts/skynet.py query --granularity 1m ...   # 每分钟粒度：查看波动详情、尖峰识别
python3 scripts/skynet.py query --granularity 5m ...   # 5分钟粒度：日常监控、趋势观察
python3 scripts/skynet.py query --granularity 1h ...   # 每小时粒度：容量规划、长时间趋势
python3 scripts/skynet.py query --time 1h ...          # 不指定粒度则自动根据时间范围计算

# 搜索应用（--bu 必须指定）
python3 scripts/skynet.py search-app "支付" --bu fincloud
python3 scripts/skynet.py search-app "video-channels-flow" --bu main

# 列出应用指标（统一接口，--bu 必须指定）
# 已知应用名：优先返回 derived metrics（业务监控），再返回 raw metrics（底层指标）
python3 scripts/skynet.py list-metrics --app video-channels-flow --bu main
python3 scripts/skynet.py list-metrics --app pay-payment-core --bu fincloud

# 不知道应用名：通过关键词全局搜索
python3 scripts/skynet.py list-metrics --keyword "rpc error" --bu main
python3 scripts/skynet.py list-metrics --keyword "nsq" --bu fincloud

# 获取 Tag 值（--bu 必须指定；--app 可选，用于自动补过滤条件和回退）
python3 scripts/skynet.py tag-values --metric rpc_server_qpm_in_app_service_method --tag appReporter --app video-channels-flow --bu main
python3 scripts/skynet.py tag-values --metric yz-settle-center.nsq_build_model_rt --tag success --app yz-settle-center --bu fincloud

# 批量 MQL 查询（--bu 必须指定）
python3 scripts/skynet.py multi-query --config /tmp/queries.json --time 1h --bu fincloud

# Token 管理
python3 scripts/token_manager.py set '<OPS_JWT_TOKEN值>'
python3 scripts/token_manager.py list
python3 scripts/token_manager.py validate

# 查询告警记录（--bu 必须指定；alarms 命令会自动从 token 获取 username）
python3 scripts/skynet.py alarm --id 208386506 --bu fincloud
python3 scripts/skynet.py alarms --page-size 10 --alarm-env prod --level critical --bu main --app pay-customer
python3 scripts/skynet.py alarms --page-size 10 --bu main --app video-channels-flow
python3 scripts/skynet.py alarms --username liuzhiyu --page-size 10 --bu fincloud  # 显式指定 username

# 统一短链解析（--bu/--env 可选，不指定则自动从 URL 解析）
python3 scripts/skynet.py resolve --url "https://j.youzan.com/xxx"
python3 scripts/skynet.py resolve --id 9363 --type monitor --bu main
python3 scripts/skynet.py resolve --uid SUrYoHrVz --type dashboard --bu main

# 数据同步（无需 --bu 参数）
python3 scripts/sync-data.py --init                    # 全量初始化
python3 scripts/sync-data.py --update                  # 增量更新
python3 scripts/sync-data.py --check                   # 检查同步状态
python3 scripts/sync-data.py --set-bu pay-xxx main     # 手动设置应用 BU

# 监控项查询（--bu 必须指定）
python3 scripts/skynet.py list-monitors --app video-channels-flow --bu main
python3 scripts/skynet.py get-monitor 44902 --bu main
```

### skynet.py resolve 输出说明

统一返回 `{"type": "...", "resolved_url": "...", "data": {...}}` 结构，`type` 决定 `data` 的内容：

| type | data 内容 | 用途 |
|------|----------|------|
| **monitor** | 告警配置：name, owningApp, metricQueries(MQL+检测方式), triggers | 理解告警规则、复用 MQL 查询实际数据 |
| **dashboard** | 面板信息：title, panels(MQL), variables | 获取面板 MQL 用于 query-builder 注入参数 |
| **log** | 日志查询参数：app, bu, env, timestampBeginMs/EndMs | 传给 zan-log-query 技能执行日志查询 |

典型场景：
- 告警短链 → 解析出 MQL 和阈值 → `skynet.py query` 查实际数据 → analyst 分析
- Dashboard 链接 → 解析出面板 MQL → query-builder 注入参数 → 执行
- 日志链接 → 解析出查询参数 → 调用日志查询工具

### skynet.py query 输出说明

查询结果包含以下时间字段：
- 顶层 `start_time` / `end_time`：查询时间范围（`YYYY-MM-DD HH:MM:SS`）
- 每个 dataPoint 的 `time`：数据点时间（`HH:MM:SS`）
- 每个 dataPoint 的 `timestamp`：原始微秒级时间戳

在分析和展示数据时，直接使用 `time` 字段，不要手动转换 `timestamp`。

## BU 自动检测

| 规则 | BU |
|------|-----|
| `^pay-` 开头 | 通常为 fincloud |
| 其他 | 通常为 main |

**重要**：不同 BU 的数据完全隔离：
- **金融云（fincloud）**：pay- 开头的应用
- **主站（main）**：非 pay- 开头的应用（如 video-channels-flow、youzan-goods 等）

**主站应用必须显式指定 `--bu main`**，否则默认查询金融云会返回空数据；但应用归属不要只靠前缀猜测，必须用真实查询结果兜底修正。

### BU 关系主动修复

**强制要求**：运行过程中一旦发现应用与 BU 对应关系错误（如查询返回空数据、resolve/get-monitor 明确显示另一 BU、list-monitors/alarms/query 在另一 BU 有真实数据），agent **必须立即**调用 `sync-data.py --set-bu` 更新本地映射，不能只在回答里口头说明。

**必须执行的动作顺序**：
1. 用实际查询结果确认正确 BU。
2. 立即执行 `python3 scripts/sync-data.py --set-bu <app_name> <correct_bu>`。
3. 重新执行刚才失败或空数据的查询，确认修复后已返回数据。
4. 在最终回复中明确说明：发现了什么 BU 错误、执行了哪条 `--set-bu` 命令、复查结果是什么。

**禁止行为**：
- 只在答案中提示“建议手动执行 `--set-bu`”而不实际执行。
- 发现 BU 错误后继续沿用旧 BU 做后续查询。
- 未经复查就声称 BU 问题已修复。

```bash
# python3 scripts/sync-data.py --set-bu <app_name> <bu>
python3 scripts/sync-data.py --set-bu pay-xxx main
python3 scripts/sync-data.py --set-bu youzan-xxx fincloud
python3 scripts/sync-data.py --set-bu yz-settle-center fincloud
```

修复后，重新执行原查询验证；若后续同步把映射覆盖掉，agent 在再次发现错误时仍必须重复上述修复流程。

## 典型场景

**简单查询**：
```
用户："账务系统的 NSQ 堆积"
→ intent-planner: app=pay-acctrans, search_commands=["search_dashboard.py --keyword 'NSQ 堆积' --compact --top 5"]
→ 主流程执行搜索，返回候选面板
→ query-builder: 将 pay-acctrans 注入候选面板 MQL → 执行 → analyst 分析
```

**业务指标查询**：
```
用户："video-channels-flow 的业务监控指标"
→ intent-planner: app=video-channels-flow, search_commands=["list-metrics --app video-channels-flow --bu main"]
→ 主流程执行搜索，返回应用的 derived metrics（业务监控，优先级高）+ raw metrics（底层指标）
→ query-builder: 基于业务指标构建 MQL → 执行 → analyst 分析
```

**根因分析**：
```
用户："支付核心错误率突然上升，帮我排查"
→ intent-planner: app=pay-payment-core, search_commands=["search_dashboard.py --keyword 'RPC 错误率'", "search_dashboard.py --keyword '流量'", "list-metrics --app pay-payment-core --bu fincloud"]
→ 主流程逐条搜索，收集多维度候选 Dashboard + 应用业务指标
→ query-builder: 基于候选面板生成多个 MQL，统一注入 pay-payment-core → 批量执行
→ analyst: 关联分析 → 推断根因 → 输出报告
```

## 约束

1. **Dashboard 优先**：优先复用经过人工验证的 Dashboard MQL；overview 类请求必须先搜索 Dashboard
2. **脚本优先**：能用脚本直接获取的，不通过大模型生成代码
3. **本地优先**：日常查询使用本地数据，减少 API 调用
4. **用途优先于应用**：先按监控用途/指标语义找 Dashboard，再注入应用参数执行
5. **MQL 语法**：参考 references/skynet-api.md 和 references/mql-patterns.md
