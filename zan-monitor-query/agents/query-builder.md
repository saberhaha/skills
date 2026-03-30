# 查询构建 Agent

需构建 MQL 时，参考 @references/mql-patterns.md

## MQL 变量注入规则（必读）

**所有 MQL 查询中的动态参数必须使用变量占位符，禁止硬编码，避免生成不可复用、不可注入的查询模板。**

### 变量类型

| 占位符格式 | 用途 | 注入方式 |
|-----------|------|---------|
| `${varName:STRING}` | 字符串变量（应用名、topic 等） | `params.others`；单条查询用 `--others '<JSON对象>'` |
| `${varName:INT}` | 整数变量 | `params.others`（保留 JSON 数值类型）；批量查询在配置中使用 `others` 传入 |
| `${timeRange:TIME_RANGE}` | 时间范围 | `--time 1h` 或 `--start/--end` |
| `${granularity:SLIDING_WINDOW}` | 聚合粒度 | 自动根据时间跨度计算 |

### 正确示例

```bash
# ✅ 正确：使用变量占位符
python3 scripts/skynet.py query \
  --mql 'nsq_channel_depth_by_app_topic_partition_idc_env_cluster{app=${app:STRING},topic=${topic:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum>' \
  --others '{"app":"pay-xtrans","topic":"tp_clearing_product_acct"}' \
  --time 1h

# ❌ 错误：禁止硬编码动态参数
python3 scripts/skynet.py query \
  --mql 'nsq_channel_depth_by_app_topic_partition_idc_env_cluster{app="pay-xtrans",topic="tp_clearing_product_acct"}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum>' \
  --time 1h
```

补充说明：
- 本技能工作流中，应用名、topic、service、method 等动态参数一律通过占位符注入
- `params.others` 保留 JSON 原生类型，是 typed value 的标准注入方式
- 单条查询的标准 CLI 入口是 `query --others '<JSON对象>'`
- `multi-query` 的 `others` 会稳定映射到 `params.others`
- 即使某些带引号字面量在服务端可执行，也不允许作为 Agent 输出或文档推荐写法
- 不带引号的字符串写法会触发 MQL 解析错误，例如 `appReporter=pay-payment-core`

### Tag 命名规则

详见 `references/mql-patterns.md` 中的 Tag 选择规则。核心要点：NSQ 指标使用 `app` tag，其他大部分指标使用 `appReporter` tag。

---

将结构化意图 + 搜索结果转换为可执行的 MQL 查询。

## 输入 → 输出

输入：结构化意图 + Dashboard/指标搜索候选结果

输出：执行请求（JSON），至少包含查询列表、参数和构建来源。

```json
{
  "build_mode": "dashboard_reuse|self_build",
  "queries": [
    {
      "queryId": "Q1",
      "mql": "rpc_server_error_ratio_by_app{appReporter=${appReporter:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum>",
      "initialInputMetric": "rpc_server_error_ratio_by_app"
    }
  ],
  "params": {
    "timeRange": {"startTimeSecond": 1710770200, "endTimeSecond": 1710772000},
    "granularity": {"len": 60, "unit": "s"},
    "others": {"appReporter": "pay-payment-core"}
  }
}
```

## 构建模式

优先级：模式A > 模式B

### 模式 A：Dashboard 驱动（优先）

搜索结果中找到匹配面板时，复用其 MQL 并注入应用参数：
- `${appReporter:STRING}` → 通过 params.others 传入
- `${app_name:STRING}` / `${es_app_name:STRING}` → 通过 params.others 传入
- `${timeRange:TIME_RANGE}` → API 自动替换
- `${granularity:SLIDING_WINDOW}` → 根据时间范围计算
- 硬编码的应用名 → 替换为目标应用名

只要用途匹配、变量可替换，就优先复用 Dashboard MQL。

### 模式 B：自主构建（fallback）

当 Dashboard 搜索无候选或候选无法注入目标应用参数时，通过以下步骤自主构建：

1. **先用 appname 查询已定义的业务指标**：
   - 使用 `list-metrics --app <app_name> --bu <bu>`
   - 返回应用的 derived metrics（业务监控，优先级高）+ raw metrics（底层指标）
   - 这些指标是人工定义过告警规则的业务指标，比通用指标更贴合实际监控场景

2. **再用意图关键词补充搜索**：`list-metrics --keyword "关键词" --bu <bu>`（如 `list-metrics --keyword "rpc error" --bu main`），覆盖通用指标

3. **基于搜索到的指标 + MQL 语法规则构建查询**

**业务指标命令示例**：
```bash
# 查询应用的所有指标（derived + raw）
python3 scripts/skynet.py list-metrics --app video-channels-flow --bu main

# 关键词全局搜索
python3 scripts/skynet.py list-metrics --keyword "rpc error" --bu main
```

若非 Dashboard 复用路径，输出需说明降级原因（如 `no_dashboard_candidates` / `dashboard_not_parameterizable`）。

## MQL 语法速查

```
metric_name{tag_filters}[startSec,endSec]
  | time_aggr<window, function>
  | tag_aggr<[keep_tags], function>
  | post_processing
```

**时间范围**：`[startSec, endSec]` 或 `${timeRange:TIME_RANGE}`

**时间聚合**：`time_aggr<{len:60,unit:s}, sum>`

**标签聚合**：
- `tag_aggr<[], sum>` — 聚合所有标签
- `tag_aggr<["method","service"], sum>` — 保留指定标签

**后处理**：
- `div<${divisor:INT}>` — QPM 转 QPS，推荐通过 `others.divisor=60` 注入
- `top<20>` — 取TopN
- `quantile<[95,99]>` — 百分位

**过滤**：
- 精确：`appReporter=${app:STRING}`
- 正则：`appReporter=~"pay-payment.*"`

## 粒度选择

**核心原则**：粒度应该匹配用户想查看的数据粒度，而不仅仅是时间范围。

### LLM 传入粒度的方式

大模型应根据用户意图选择合适的粒度，通过 `--granularity` 参数传入：

```bash
# LLM 应根据意图选择粒度并传入
python3 scripts/skynet.py query \
  --granularity 1m \                    # 精细粒度：查看每分钟波动
  --mql '...' \
  --others '{"app":"pay-xxx"}' --time 3h
```

**粒度参数格式**：`30s`, `1m`, `5m`, `1h`（不支持 `1d`）

### 根据意图选择粒度

| 用户意图 | 推荐粒度 | 说明 |
|---------|---------|------|
| 查看每分钟变化详情 | `1m`（60s） | 精细波动、尖峰识别 |
| 查看每5分钟趋势 | `5m` | 日常监控、趋势观察 |
| 查看每小时趋势 | `1h` | 容量规划、长时间趋势 |
| 查看每日规律 | `1h` 或更大 | 周期性分析 |

### ⚠️ 重要：不要用大粒度代替小粒度

**错误做法**：用户想看每分钟数据，但选了 5m 粒度
- 问题：5m 粒度下每个点是 5 分钟的聚合，无法看到单分钟的真实波动
- 后果：峰值被平滑掉，细粒度异常被掩盖

**正确做法**：根据用户意图选粒度
- 用户要看"每分钟变化" → 用 `1m` 粒度，即使查询 3 小时数据
- 用户要看"整体趋势" → 可用 `5m` 或更大粒度

### 粒度与聚合函数的配合

粒度选择影响聚合函数的选择：

| 粒度 | 聚合函数 | 适用场景 |
|------|---------|---------|
| 1m | `max` | 查每分钟峰值 |
| 5m | `max` | 查 5 分钟内峰值 |
| 1m | `sum` | 查每分钟累计量 |
| 5m | `sum` | 查 5 分钟累计量 |

**示例**：
- 用户想看"最近 3 小时每分钟的 NSQ 深度峰值" → 用 `time_aggr<60s, max>`
- 用户想看"最近 3 小时每 5 分钟的 NSQ 深度峰值" → 用 `time_aggr<5m, max>`

## 聚合函数选择（根据意图）

**重要**：不同分析意图应使用不同的 time_aggr 聚合函数。选错会导致数据解读错误。

### 意图 → 聚合函数映射

| 用户意图 | 聚合函数 | 说明 |
|---------|---------|------|
| 检查是否超过阈值/告警 | `max` | 取窗口内最大值，与阈值比较 |
| 分析峰值/尖峰 | `max` | 找最大点 |
| 统计总量/累计量 | `sum` | 窗口内求和 |
| 分析平均负载/利用率 | `avg` | 算术平均 |
| 查看当前状态 | `latest` | 最新值 |

## 复杂查询

**比率计算**：`tseries_div(metricA as a, metricB as b)`

**TopN**：`... | tag_aggr<["method","service"], sum> | top<20>`

**正则过滤**：`{appReporter=~"pay-payment.*"}`

## 变量替换

通过 `params.others` 传入变量值：
- `${appReporter:STRING}` → others.appReporter
- `${app_name:STRING}` → others.app_name
- `${service:STRING}` → others.service
- `${divisor:INT}` → others.divisor（JSON 数值）
- `${timeRange:TIME_RANGE}` → 自动替换
- `${granularity:SLIDING_WINDOW}` → 自动替换

详见 references/skynet-api.md

## 执行 API

```bash
POST /v3/skynet/v2/mql:execute
```

```json
{
  "queries": [{
    "queryId": "Q1",
    "mql": "rpc_server_error_ratio_by_app{appReporter=${appReporter:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum>",
    "initialInputMetric": "rpc_server_error_ratio_by_app"
  }],
  "params": {
    "timeRange": {"startTimeSecond": 1710770200, "endTimeSecond": 1710772000},
    "granularity": {"len": 60, "unit": "s"},
    "others": {"appReporter": "pay-payment-core"}
  }
}
```

## BU 查询

`yz-` 开头的应用可能跨 BU 部署；当不确定 app 对应哪个 BU 时，可使用 `skynet.py` 的双 BU 基础能力（如 `query_both_bu()` / `query_with_fallback()`）自动尝试 `main` 和 `fincloud`。

## 批量查询

当需要查询多个 MQL 时，使用 `skynet.py multi-query` 批量执行：

```bash
python3 scripts/skynet.py multi-query --config /tmp/queries.json --time 1h --bu fincloud
```

`queries.json` 中统一使用 `others` 字段映射到 `params.others`。

queries.json 格式：
```json
[
  {"mql": "rpc_server_error_ratio_by_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, max>", "alias": "error_rate", "others": {"app": "pay-payment-core"}},
  {"mql": "rpc_server_qpm_in_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | div<${divisor:INT}>", "alias": "qps", "others": {"app": "pay-payment-core", "divisor": 60}}
]
```

## 输出约束

返回的执行请求必须能说明来源：
- `build_mode=dashboard_reuse|self_build`
- 若 `self_build`，应传递 fallback reason（如 `no_dashboard_candidates` / `dashboard_not_parameterizable`）
