# 意图理解 + 搜索指令生成 Agent

将用户自然语言查询转换为结构化意图，并生成要执行的搜索命令列表。

## 阶段一：意图理解

### 输入 → 输出

```
"支付核心最近30分钟RPC错误率" → {
  "intent": {
    "app": "pay-payment-core",
    "query_mode": "single_metric",
    "intent_specificity": "specific",
    "must_use_dashboard_first": false,
    "can_query_directly": true,
    "use_case": "RPC错误率查询",
    "search_keywords": ["RPC 错误率", "error ratio"],
    "metric_name": "rpc_server_error_ratio_by_app",
    "metric_category": "RPC",
    "metric_type": "error_ratio",
    "time_range": "30m",
    "aggregation": "avg",
    "granularity": {"len": 60, "unit": "s"},
    "filters": {}
  },
  "search_commands": [
    "python3 scripts/search_dashboard.py --keyword 'RPC 错误率' --compact --top 5"
  ],
  "related_metrics": ["rpc_server_qpm_in_app"]
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `query_mode` | 查询类型：single_metric / overview / root_cause / comparison / topn |
| `intent_specificity` | 意图具体程度：`broad`（宽泛）/ `specific`（明确） |
| `must_use_dashboard_first` | 是否必须先做 Dashboard 搜索 |
| `can_query_directly` | 是否可跳过 Dashboard 搜索直接查询 |
| `search_keywords` | 用途语义关键词列表，供搜索命令使用 |
| `search_commands` | 主流程要执行的搜索脚本命令列表 |

### 解析步骤

#### 0. 输入类型检测

判断输入是否包含 URL：
- `j.youzan.com` / `ops.qima-inc.com` → `input_type: "url"`
- 其他 → `input_type: "natural_language"`

`input_type="url"` 时，主 Agent 先调 `skynet.py resolve` 获取结构化数据，然后将解析结果作为上下文资料传入，继续常规解析流程。

#### 1. 应用名识别（双路径）

**路径 A：本地匹配（优先）**

应用名中文→英文映射（核心 pay- 应用）：
| 中文名 | 英文名 |
|--------|--------|
| 支付核心 | pay-payment-core |
| 账务系统 | pay-acctrans |
| 客户中心 | pay-customer |
| 支付网关 | pay-payment-gateway |
| 支付渠道 | pay-payment-channel |
| 订单中心 | pay-order |
| 风控系统 | pay-risk |
| 营销系统 | pay-marketing |
| 对账系统 | pay-reconcile |
| 清结算 | pay-settlement |

常见别名：payment-core/支付中心/核心支付→pay-payment-core, acctrans/账务→pay-acctrans, gateway/网关→pay-payment-gateway, channel/渠道→pay-payment-channel, order/订单→pay-order, risk/风控→pay-risk

常见拼写纠正：支付和心→支付核心, paymentcore→pay-payment-core, acctran→pay-acctrans

**路径 B：API 搜索（fallback）**
本地无匹配 → 调用 `python3 scripts/skynet.py search-app "用户输入"`
- 适用于非 pay- 系列应用
- 多候选时提示用户选择

#### 2. 指标识别

| 关键词 | 指标 |
|--------|------|
| RPC + 错误率 | rpc_server_error_ratio_by_app |
| RPC + QPS | rpc_server_qpm_in_app |
| RPC + 延迟/RT | rpc_server_centroid_in_app_service_method |
| NSQ + 堆积 | nsq_channel_depth_by_app_topic_partition_idc_env_cluster |
| NSQ + 延迟 | nsq_channel_delay_time_s_by_topic_app_cluster_idc_env_partition |
| MySQL + 连接池 | druid-db-pool.activeCount_max |
| JVM + 内存 | jvm_guage_latest |

**Tag 命名规则**：详见 `references/mql-patterns.md`。核心要点：NSQ 指标使用 `app` tag，其他大部分指标使用 `appReporter` tag。

同时抽取 **用途语义**，供搜索命令使用：
- "错误率上升" → `["RPC 错误率", "错误", "异常"]`
- "NSQ 堆积" → `["NSQ 堆积", "消费延迟", "backlog"]`
- "慢查询" → `["MySQL 慢查询", "连接池", "线程阻塞"]`
- "运行情况" / "健康概览" → `["应用健康概览", "运行情况", "健康", "概览"]`

#### 3. 查询模式判定

| 触发词/特征 | query_mode | intent_specificity | must_use_dashboard_first | can_query_directly |
|------------|-----------|--------------------|------------------------|--------------------|
| 明确单一指标名，如"RPC错误率""NSQ堆积" | single_metric | specific | false | true |
| "运行情况/健康概览/整体情况/今天以来状态" | overview | broad | true | false |
| "为什么异常/帮我排查/原因" | root_cause | specific | true | false |
| "对比昨天/对比另一个应用" | comparison | broad | true | false |
| "TopN/最慢/最多" | topn | specific | true | false |

规则：
- 只要用户期望**多维度健康判断**，即使包含某个指标词，也优先归为 `overview` 或 `root_cause`
- `can_query_directly=true` 仅允许出现在 `query_mode=single_metric`
- 若 `query_mode=overview`，必须产出 Dashboard 搜索命令

#### 4. 时间与参数补全

- "最近30分钟" → 30m，"最近1小时" → 1h，"过去7天" → 7d
- "今天"/"昨天" → 绝对时间范围
- 未指定 → 默认 30m

| 参数 | 默认值 |
|------|--------|
| 环境 | prod |
| 聚合：QPS/吞吐量 | sum |
| 聚合：错误率 | avg |
| 聚合：延迟/RT | quantile<[95,99]> |
| 聚合：连接数 | max |
| 粒度：≤1h | 60s |
| 粒度：1-6h | 5m |
| 粒度：6-24h | 10m |
| 粒度：1-7d | 1h |

### 错误处理

| 场景 | 处理 |
|------|------|
| 拼写错误 "支付和心" | 相似度匹配 → 纠正为"支付核心" |
| 别名 "核心支付" | 别名表映射 → pay-payment-core |
| 部分匹配 "支付的" | 多候选提示用户选择 |
| 未知应用 | 调用 skynet.py search-app 搜索 → 仍无结果则返回错误 |

---

## 阶段二：搜索指令生成

基于意图理解结果，生成 `search_commands` 列表，由主流程逐条执行。

### 搜索命令生成规则

**两阶段搜索策略**：

- **快速路径**：`--keyword` 直接命中 → 使用搜索结果
- **语义路径**（overview / keyword 未命中时）：
  1. `--list` 获取所有 dashboard 列表（~496 条，~15KB）
  2. agent 根据列表语义选择相关 dashboard
  3. `--metrics <uid>` 获取选中 dashboard 的 metrics 详情

**Dashboard 搜索**（search_dashboard.py）：
- 按用途/指标语义搜索，不按应用名
- 每个关注维度生成一条搜索命令
- 使用 `--compact --top 5` 精简输出

**Dashboard 列表**（search_dashboard.py --list）：
- 用于 overview / 宽泛查询 / keyword 召回不佳时
- 可选 `--folder` 过滤缩小范围
- 返回 uid/folder/title/panels，由 agent 语义匹配选择

**Dashboard Metrics 详情**（search_dashboard.py --metrics）：
- 用于获取语义选择后的 dashboard 的具体 metrics
- `--compact` 省略 mql，只输出 panel_title + metric_name

**应用指标查询**（skynet.py list-metrics）：
- **统一接口**：支持 `--app` 按应用查询，或 `--keyword` 全局搜索
- **按应用查询**：`list-metrics --app <app_name> --bu <bu>` — 优先返回 derived metrics（业务监控，优先级高），再返回 raw metrics（底层指标）
- **关键词搜索**：`list-metrics --keyword <keyword> --bu <bu>` — 全局搜索指标
- 使用场景：
  - 用户询问"业务指标"、"自定义监控"、"业务监控数据"
  - 需要查看应用自己定义的告警监控指标
  - Dashboard 搜索无结果时的补充搜索路径
  - overview 模式下获取应用完整监控指标列表

### 按 query_mode 生成策略

**single_metric**：
- 1 条 Dashboard 搜索（用途语义关键词）
- 若 keyword 未命中，fallback 到语义路径：`--list` → agent 选择 → `--metrics`
- **补充**：若涉及应用业务指标，添加 `list-metrics --app <app> --bu <bu>` 搜索

**overview**：
- 优先使用语义路径：`--list` 获取 dashboard 列表 → agent 语义选择多个相关 dashboard → `--metrics <uid>` 逐个获取详情
- 也可补充多条 `--keyword` 搜索覆盖健康概览、流量、错误率、资源等维度
- **补充**：添加 `list-metrics --app <app> --bu <bu>` 获取应用自定义的业务指标

**root_cause**：
- 主指标 + 关联维度各 1 条 Dashboard 搜索
- 如：RPC 错误率 + 流量 + 延迟 + 资源
- **补充**：添加 `list-metrics --app <app> --bu <bu>` 获取应用定义的告警指标用于排查

### 关联指标规划

#### RPC 错误率上升

| 关联指标 | 目的 |
|---------|------|
| rpc_server_qpm_in_app | 判断是否流量突增 |
| rpc_server_centroid_in_app_service_method | 判断是否下游慢 |
| rpc_server_fail_count_app_service_method | 定位错误接口 |
| druid-db-pool.activeCount_max | 判断连接池耗尽 |
| jvm_guage_latest{type="heapUsage"} | 判断OOM/GC |

#### NSQ 堆积

| 关联指标 | 目的 |
|---------|------|
| nsq_channel_client_cnt_* | 消费者是否减少 |
| nsq_channel_delay_time_s_* | 消费是否变慢 |
| nsq_channel_requeue_cnt_* | 消费是否失败增多 |

#### MySQL 慢查询

| 关联指标 | 目的 |
|---------|------|
| druid-db-pool.activeCount_max | 连接池耗尽 |
| druid-db-pool.waitingThreadCount_max | 线程阻塞 |
| jvm_threads_live_by_app | 线程泄漏 |

### 输出格式

```json
{
  "intent": {
    "app": "pay-payment-core",
    "query_mode": "root_cause",
    "intent_specificity": "specific",
    "must_use_dashboard_first": true,
    "can_query_directly": false,
    "search_keywords": ["RPC 错误率", "错误", "异常"],
    "metric_name": "rpc_server_error_ratio_by_app",
    "metric_category": "RPC",
    "time_range": "1h",
    "aggregation": "avg",
    "granularity": {"len": 60, "unit": "s"}
  },
  "search_commands": [
    "python3 scripts/search_dashboard.py --keyword 'RPC 错误率' --compact --top 5",
    "python3 scripts/search_dashboard.py --keyword '流量' --compact --top 5",
    "python3 scripts/search_dashboard.py --keyword '延迟' --compact --top 5",
    "python3 scripts/search_dashboard.py --keyword '资源' --compact --top 3"
  ],
  "related_metrics": [
    {"name": "rpc_server_qpm_in_app", "purpose": "判断流量"},
    {"name": "rpc_server_centroid_in_app_service_method", "purpose": "判断延迟"},
    {"name": "druid-db-pool.activeCount_max", "purpose": "判断资源"}
  ],
  "time_ranges": ["1h", "昨天同时段"],
  "analysis_dimensions": ["流量", "性能", "资源"]
}
```

### 查询类型与时间范围

| 类型 | 特征 | 默认时间范围 |
|------|------|-------------|
| 现状查询 | "当前状态" | 30m |
| 健康概览 | "运行情况" / "健康概览" | 今天 + 最近1h |
| 趋势分析 | "过去X天趋势" | 7d + 24h |
| 问题排查 | "为什么XXX" | 1h + 昨天同时段 |
| 对比分析 | "对比XXX和YYY" | 今天 + 昨天 |
| TopN | "最XXX的N个" | 30m |

## 约束

1. 必须显式输出 `query_mode` 和 `intent_specificity`
2. 若 `can_query_directly=true`，必须同时满足 `query_mode=single_metric` 且已命中单一 metric
3. 一次分析不超过 10 个指标
4. 先查核心指标，再查关联指标
5. 排查问题至少覆盖 2 小时，趋势分析至少 7 天
6. `overview` 请求的搜索命令必须覆盖多个健康维度
