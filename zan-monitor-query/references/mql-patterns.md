# MQL 查询模式参考

本文档提供 MQL (Monitoring Query Language) 的常用模式和最佳实践。

MQL 用来描述对监控数据执行的计算，以派生出新指标。MQL 将计算逻辑组织成一个算子序列，前一个算子的输出作为后一个算子的输入（通过管道操作符 `|` 连接）。

## 基础语法

### MQL 结构

**标准格式**（硬编码时间）：
```
metric_name{tag_filters}[startSec-endSec]
  | time_aggr<window, function>
  | tag_aggr<[keep_tags], function>
  | post_processing
```

**推荐格式**（使用变量占位符）：
```
metric_name{tag_filters}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, function>
  | tag_aggr<[keep_tags], function>
```

**查询结构**：
- `selector`：选择指标和过滤条件（metric + conditions + time_range）
- `unary_func`：一元函数，接收一个数据流输入
- `binary_func`：二元函数，接收两个数据流输入（如 tseries_div、change_ratio）
- `AS output_name`：为查询结果命名

### 变量占位符

MQL 模板使用占位符表达式使查询可复用。占位符语法：`${varName:varType}` 或 `#{varName:varType}`

- `${...}`：动态占位符，运行时由程序替换
- `#{...}`：静态占位符，配置时由用户替换

所有 MQL 查询必须使用变量占位符。底层标准注入方式是 `params.others`；其中 typed value 必须保留 JSON 原生类型。单条查询通过 `query --others '<JSON对象>'` 传入，批量查询在配置中通过 `others` 映射到 `params.others`：

| 占位符类型 | 语法 | 示例 | 说明 |
|-----------|------|------|------|
| STRING | `${varName:STRING}` | `${app:STRING}`, `${topic:STRING}` | 字符串变量；通过 `params.others` 注入 |
| INT | `${varName:INT}` | `${threshold:INT}` | 整数变量；通过 `params.others` 保留 JSON 数值类型 |
| DOUBLE | `${varName:DOUBLE}` | `${threshold:DOUBLE}` | 浮点数变量；通过 `params.others` 保留 JSON 数值类型 |
| BOOL | `${varName:BOOL}` | `${enabled:BOOL}` | 布尔变量；通过 `params.others` 保留 JSON 布尔类型 |
| TIME_RANGE | `${timeRange:TIME_RANGE}` | 固定写法 | 时间范围 `[start_us-end_us]`，由服务端替换 |
| PERIOD | `${period:PERIOD}` | `[:5m]`, `[1w:5m]` | 时间段 `[offset:duration]` |
| SLIDING_WINDOW | `${granularity:SLIDING_WINDOW}` | 固定写法 | 滑动窗口 `[window_size^step]`，由服务端替换 |
| DURATION | `${duration:DURATION}` | `15s`, `5m`, `1w` | 持续时间 |
| METRIC | `#{metric:METRIC}` | 指定指标名 | 指标名称（不要使用 STRING 类型） |
| CONDITION_LIST | `${conditions:CONDITION_LIST}` | `{app="x", status=~"2.."}` | 过滤条件列表 |
| TAG_LIST | `${tags:TAG_LIST}` | `["host", "service"]` | 标签名列表 |
| PERCENTILE_LIST | `${percentiles:PERCENTILE_LIST}` | `[95, 99, 99.9]` | 百分位数列表 |
| BUCKET_LIST | `${buckets:BUCKET_LIST}` | `[50, 100, 150]` | 分桶边界列表 |
| FUNC | `${func:FUNC}` | `sum`, `max` | 函数实例 |

**正确用法**：
```bash
python3 scripts/skynet.py query \
  --mql 'rpc_server_qpm_in_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum>' \
  --others '{"app":"pay-payment-core"}' \
  --granularity 1m \          # LLM 根据意图传入合适粒度
  --time 1h
```

```json
[
  {
    "mql": "rpc_server_qpm_in_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum> | div<${divisor:INT}>",
    "alias": "qps",
    "others": {
      "app": "pay-payment-core",
      "divisor": 60
    }
  }
]
```
上面的 `divisor` 必须保持为 JSON 数值，不能写成 `"60"`。
对 `INT`/`DOUBLE`/`BOOL` 等 typed value，单条查询也应通过 `--others` 传入 JSON 原生类型。

**错误用法**（禁止硬编码）：
```bash
# ❌ 错误：硬编码应用名
--mql 'rpc_server_qpm_in_app{appReporter=pay-payment-core}...'

# ❌ 错误：硬编码时间范围
--mql 'rpc_server_qpm_in_app{...}[1710770200,1710772000]...'
```

### 时间相关元素

| 元素 | 语法 | 示例 | 说明 |
|------|------|------|------|
| **时间单位** | `s/m/h/d/w/y` | `s`=秒, `m`=分钟, `h`=小时, `d`=天, `w`=周, `y`=年 | - |
| **持续时间** | `<数字><时间单位>` | `15s`, `5m`, `1w` | 表示一段时间长度 |
| **时间范围** | `[<start_us>-<end_us>]` | `[1622520000000000-1622521800000000]` | 绝对时间戳（微秒），包含 start 和 end |
| **时间段** | `[<offset>:<duration>]` | `[1w:5m]`, `[:5m]` | offset 可选，表示相对当前时间的偏移 |
| **滑动窗口** | `[<window_size>^<step>]` | `[1m^1m]`, `[3m^1m]` | step 可选，省略时等于 window_size |

### 过滤条件

过滤条件用于筛选时序数据，语法：

| 操作符 | 语法 | 说明 | 示例 |
|--------|------|------|------|
| **精确匹配** | `tag="value"` | 等于 | `app="pay-core"`, `env="prod"` |
| **不等于** | `tag!="value"` | 不等于 | `app!="devops"` |
| **正则匹配** | `tag=~"pattern"` | 匹配正则表达式 | `job=~"job:.+"`, `env=~"staging\|testing"` |
| **正则排除** | `tag!~"pattern"` | 不匹配正则表达式 | `status!~"2.."`, `status=~"5.."` |

**过滤条件列表**：
```
{condition1, condition2, ...}
```

**示例**：
```
# 单条件
rpc_server_qpm_in_app{appReporter="some-app"}...

# 多条件
rpc_server_qpm_in_app{appReporter="some-app", env="prod"}...

# 使用正则
http_server_requests{status=~"2..", method!~"OPTIONS|HEAD"}...

# 在 MQL 模板中使用变量
rpc_server_qpm_in_app{appReporter=${app:STRING}, env=${env:STRING}}...
```

## Tag 选择规则

不同指标使用不同的应用标识 tag，必须遵循以下规则：

### 使用 `appReporter` 的指标

- **RPC 指标**: `rpc_server_*`, `rpc_client_*`
- **HTTP 指标**: `http_server_*`, `http_client_*`
- **MySQL 指标**: `druid-db-pool.*`, `mysql-client.*`
- **JVM 指标**: `jvm_*`
- **未知指标**: fallback 到 `appReporter`

**MQL 示例**：
```
rpc_server_qpm_in_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, sum>
  | tag_aggr<[], sum>
  | div<${divisor:INT}>
```

### 使用 `app` 的指标

- **NSQ 指标**: `nsq_channel_*`, `nsq-consume-*`

**MQL 示例**：
```
nsq_channel_depth_by_app_topic_partition_idc_env_cluster{app=${app:STRING},topic=${topic:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, sum>
  | tag_aggr<["channel"], sum>
```

### 自动选择逻辑

`scripts/skynet.py` 中的 `_get_app_tag_name()` 方法按硬编码规则自动选择：
1. 如果指标名包含 `nsq`（不区分大小写）→ 返回 `app`
2. 其他情况 → 返回 `appReporter`

## 常见查询模式

### 1. RPC QPS 查询

```
rpc_server_qpm_in_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, sum>
  | tag_aggr<[], sum>
  | div<${divisor:INT}>
```

**说明**：
- `time_aggr<..., sum>`: 时间维度求和
- `tag_aggr<[], sum>`: 所有 tag 聚合（不保留任何 tag）
- `div<${divisor:INT}>`: 除以变量 `divisor` 转换为 QPS，推荐通过 `others.divisor=60` 注入

### 2. RPC 错误率查询

```
rpc_server_error_ratio_by_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, max>
  | tag_aggr<[], max>
```

**说明**：
- 错误率指标已经是比率（0-1 或 0-100），使用 `max` 聚合获取峰值

### 3. RPC 延迟（P95/P99）

```
rpc_server_centroid_in_app_service_method{appReporter=${app:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, centroid<20>>
  | tag_aggr<[], quantile<[95,99]>>
```

**说明**：
- `centroid<20>`: 保留 20 个代表性数据点
- `quantile<[95,99]>`: 计算 P95 和 P99 百分位

### 4. NSQ 堆积查询

```
nsq_channel_depth_by_app_topic_partition_idc_env_cluster{app=${app:STRING},topic=${topic:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, sum>
  | tag_aggr<["channel"], sum>
```

**说明**：
- 注意使用 `app` 而非 `appReporter`
- `tag_aggr<["channel"], sum>`: 保留 channel 维度，按 channel 聚合

### 5. NSQ 消费延迟

```
nsq_channel_delay_time_s_by_topic_app_cluster_idc_env_partition{app=${app:STRING},topic=${topic:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, max>
  | tag_aggr<[], max>
```

**说明**：
- 延迟使用 `max` 聚合获取最大延迟

### 6. MySQL 连接池

```
druid-db-pool.activeCount_max{appReporter=${app:STRING}}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, max>
  | tag_aggr<["url"], max>
```

**说明**：
- `tag_aggr<["url"], max>`: 保留 url 维度，按数据库 URL 分组

### 7. JVM 内存使用

```
jvm_guage_latest{appReporter=${app:STRING},type="memory.used"}${timeRange:TIME_RANGE}
  | time_aggr<${granularity:SLIDING_WINDOW}, max>
  | tag_aggr<[], max>
```

### 8. 多指标比率计算

```
tseries_div(
  rpc_server_error_count{appReporter=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum> as errorCount,
  rpc_server_total_count{appReporter=${app:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum> as totalCount
)
```

**说明**：
- `tseries_div(A, B)`: 两个时间序列相除
- `as varName`: 给查询结果命名

### 9. RPC 吞吐量（QPS）

```
# Metric 计算阶段：计算每 15 秒的请求数
rpc_rt | time_aggr<[15s^15s], count> | tag_aggr<["appReporter"], sum> as rpc_qpm

# 查询阶段：按应用统计最近 1 小时的 QPS
rpc_qpm[:1h] | tag_aggr<["appReporter"], sum>
```

### 10. GAUGE 类型指标（CPU 使用率）

```
# Metric 计算阶段：采集最新的 CPU 使用率
cpu_usage | time_aggr<[15s^15s], latest> | echo as cpu_usage_last

# 查询阶段：按主机统计最近 1 小时的平均 CPU 使用率
cpu_usage_last[:1h] | time_aggr<[15s^15s], avg> | tag_aggr<["host"], avg>
```

### 11. COUNTER 类型指标增长量

```
# Metric 计算阶段：采集最新的 RPC 请求总次数
rpc_request_total | time_aggr<[15s^15s], latest> | echo as rpc_request_total_count

# 查询阶段：按应用统计最近 1 小时每分钟的请求增长量
rpc_request_total_count[:1h] | time_aggr<[1m^1m], delta> | tag_aggr<["appReporter"], sum>
```

### 12. 延迟分布（Histogram）

```
# 统计 RPC RT 在 0~50ms、50~100ms、100~150ms、150ms+ 的分布
rpc_rt | time_aggr<[15s^15s], histogram<[50,100,150]>> | tag_aggr<["appReporter","_bucket"], sum>
```

**说明**：
- `_bucket` 是 histogram 派生的 tag，用于标示统计的区间
- buckets 定义区间边界：`[50, 100, 150]` 表示 `[0-50)`, `[50-100)`, `[100-150)`, `[150-∞)`

### 13. 百分位数完整示例

```
# Metric 计算阶段：计算质心数
rpc_rt | time_aggr<[15s^15s], centroid<20>> | tag_aggr<["appReporter"], centroid<20>> as rpc_rt_centroid

# 查询阶段：按应用统计 P99.99、P99、P95
rpc_rt_centroid[:1h] | time_aggr<[15s^15s], centroid<20>> | tag_aggr<["appReporter"], quantile<[99.99,99,95]>>
```

**说明**：
- 百分位数需要通过 centroid 计算
- Metric 阶段先计算质心数
- 查询阶段对质心数应用 quantile 得到百分位

## 聚合函数

### time_aggr（时间维度聚合）

在时间维度上对时序数据进行聚合。有两种形式：

1. **滑动窗口聚合**：`time_aggr<sliding_window, func>`
2. **全时间聚合**：`time_aggr<func>`（将所有数据点聚合为一个点）

| 函数 | 语法 | 用途 | 示例 |
|------|------|------|------|
| **sum** | `time_aggr<[15s^15s], sum>` | 求和 | 计算 RPC RT 总和、请求数总和 |
| **count** | `time_aggr<[15s^15s], count>` | 计数 | 统计样本数量，常用于计算吞吐量 |
| **avg** | `time_aggr<[15s^15s], avg>` | 平均值 | 统计 GAUGE 类型指标（CPU 使用率等） |
| **max** | `time_aggr<[15s^15s], max>` | 最大值 | 延迟峰值、资源使用峰值 |
| **min** | `time_aggr<[15s^15s], min>` | 最小值 | 较少使用 |
| **stddev** | `time_aggr<[15s^15s], stddev>` | 标准差 | 数据波动性分析 |
| **centroid&lt;N&gt;** | `time_aggr<[15s^15s], centroid<20>>` | 质心压缩 | 百分位数计算的前置步骤（T-Digest 算法） |
| **latest** | `time_aggr<[15s^15s], latest>` | 最新值 | GAUGE/COUNTER 类型指标（CPU 使用率、总请求数） |
| **delta** | `time_aggr<[15s^15s], delta>` | 差值 | COUNTER 类型指标的增长量（最新值 - 最旧值） |

### tag_aggr（标签维度聚合）

根据指定的维度（tag）对多条时序进行分组，再使用统计函数对每组数据进行聚合。类似 SQL 的 `GROUP BY`。

语法：`tag_aggr<[tag_list], func>`

| 函数 | 语法 | 用途 | 示例场景 |
|------|------|------|----------|
| **sum** | `tag_aggr<[], sum>` | 求和 | 所有实例的请求总数 |
| **avg** | `tag_aggr<["host"], avg>` | 平均 | 按主机统计平均延迟 |
| **max** | `tag_aggr<["service"], max>` | 最大 | 按服务统计最大错误率 |
| **min** | `tag_aggr<[], min>` | 最小 | 全局最小值 |
| **count** | `tag_aggr<[], count>` | 计数 | 时序数量 |
| **stddev** | `tag_aggr<["app"], stddev>` | 标准差 | 按应用统计波动性 |
| **centroid&lt;N&gt;** | `tag_aggr<["app"], centroid<20>>` | 质心聚合 | 多实例百分位数聚合 |
| **quantile&lt;list&gt;** | `tag_aggr<[], quantile<[95,99]>>` | 百分位 | 计算 P95/P99（需配合 centroid 使用） |
| **histogram&lt;buckets&gt;** | `tag_aggr<["app","_bucket"], sum>` | 直方图 | 延迟分布统计 |

**keep_tags 参数**：
- `[]`: 不保留任何 tag，全部聚合为一条时序
- `["tag1", "tag2"]`: 保留指定 tag，按这些 tag 分组聚合（输出时序仅包含这些 tag）

## 二元函数（Binary Functions）

接收两个数据流输入的函数。

### tseries_div

按时间对齐两个输入数据流，将同一时间点的两个数据值相除。常用于计算比率（如平均 RT = RT 总和 / 请求数）。

**示例：计算 RPC 平均延迟**
```
# Metric 计算阶段（仅声明，不实际计算）
tseries_div(
  rpc_rt | time_aggr<[15s^15s], sum> | tag_aggr<["appReporter"], sum> as rpc_rt_sum,
  rpc_rt | time_aggr<[15s^15s], count> | tag_aggr<["appReporter"], sum> as rpc_total_count
)

# 查询阶段（实际计算）
tseries_div(
  rpc_rt_sum[:1h] | tag_aggr<["appReporter"], sum>,
  rpc_total_count[:1h] | tag_aggr<["appReporter"], sum>
)
```

### change_ratio

计算 b 相对于 a 的变化率。公式：`(b - a) / a`

**示例：同环比监控**
```
change_ratio(
  #{metric:METRIC}${timeRange:TIME_RANGE} | time_aggr<${slidingWindow:SLIDING_WINDOW}, sum> | tag_aggr<["host"], sum>,
  #{metric:METRIC}${compareWithTimeRange:TIME_RANGE} | time_aggr<${slidingWindow:SLIDING_WINDOW}, sum> | tag_aggr<["host"], sum>
)
```

## 其他函数

### echo

将输入时序原样输出，用于 GAUGE 类型指标（如 CPU/内存使用率）。无参数。

```
cpu_usage | time_aggr<[15s^15s], latest> | echo
```

### top

计算 Top K。输入数据流应包含多条时序，但每条时序中仅有一个数据点。

```
rpc_server_qpm_in_app{...}${timeRange:TIME_RANGE}
  | time_aggr<sum>
  | tag_aggr<["appReporter"], sum>
  | top<20>
```

### div / add

一元运算，将数据点除以或加上指定数值。

```
# QPM 转 QPS
rpc_server_qpm_in_app{...} | ... | div<${divisor:INT}>

# 温度单位转换
temperature_celsius{...} | ... | add<273.15>
```

## 后处理操作

| 操作 | 语法 | 用途 | 示例 |
|------|------|------|------|
| 除法 | `div<N>` | QPM 转 QPS | `div<${divisor:INT}>` |
| 加法 | `add<N>` | 数值偏移 | `add<100>` |
| Top N | `top<N>` | 获取前 N 个最大值 | `top<20>` |
| 排序 | `sort` | 结果排序 | `sort` |
| Echo | `echo` | 原样输出（GAUGE） | `echo` |

## 常见错误

### 1. 硬编码变量值

❌ **错误**：
```
rpc_server_qpm_in_app{appReporter=pay-payment-core}[1710770200,1710772000]
```

✅ **正确**：
```
rpc_server_qpm_in_app{appReporter=${app:STRING}}${timeRange:TIME_RANGE}
```

### 2. NSQ 指标使用错误的 tag

❌ **错误**：
```
nsq_channel_depth_by_app_topic_partition_idc_env_cluster{appReporter=${app:STRING}}...
```

✅ **正确**：
```
nsq_channel_depth_by_app_topic_partition_idc_env_cluster{app=${app:STRING}}...
```

### 3. 时间聚合粒度错误

❌ **错误**：
```
... | time_aggr<60, sum> ...
```

✅ **正确**：
```
... | time_aggr<{len:60,unit:s}, sum> ...
或
... | time_aggr<${granularity:SLIDING_WINDOW}, sum> ...
```

**易错点**：
- `24h` / `5m` / `60s` 这类值是 **Duration**，不能直接写成 `time_aggr<24h, sum>`
- 想看**趋势**：使用 `time_aggr<${granularity:SLIDING_WINDOW}, sum>`，并通过 `--granularity 1h/5m/...` 指定粒度
- 想看**整个时间范围汇总**：使用 `time_aggr<sum>`，不要手写 `24h`

**示例**：
```bash
# ❌ 错误：把 Duration 当成 SlidingWindow
... | time_aggr<24h, sum> | tag_aggr<["errorCode"], sum>

# ✅ 正确：查询最近24小时按小时趋势
...${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<["errorCode"], sum>
# 搭配参数：--time 24h --granularity 1h

# ✅ 正确：查询最近24小时总汇总
...${timeRange:TIME_RANGE} | time_aggr<sum> | tag_aggr<["errorCode"], sum>
# 搭配参数：--time 24h
```

### 4. tag_aggr 保留不存在的 tag

❌ **错误**：
```
rpc_server_qpm_in_app{...} | tag_aggr<["nonexistent_tag"], sum>
```

✅ **正确**：
```
rpc_server_qpm_in_app{...} | tag_aggr<[], sum>
或
rpc_server_centroid_in_app_service_method{...} | tag_aggr<["service"], max>
```

### 5. 延迟指标未使用 centroid

❌ **错误**：
```
rpc_server_centroid_in_app_service_method{...} | time_aggr<..., avg> | tag_aggr<[], quantile<[95,99]>>
```

✅ **正确**：
```
rpc_server_centroid_in_app_service_method{...} | time_aggr<..., centroid<20>> | tag_aggr<[], quantile<[95,99]>>
```

## 指标类型

理解指标类型有助于选择正确的聚合函数。

### GAUGE（仪表类型）

数值会上下波动，而非单调递增/减。就像从测量仪器上看测量值。

**特点**：
- 数值可增可减
- 直接反映当前状态

**示例**：
- CPU 使用率、内存使用率
- 连接池活跃连接数
- 队列深度

**推荐聚合**：
- `latest`：取最新值
- `avg`：取平均值
- `max/min`：取峰值/谷值

**MQL 示例**：
```
# 采集最新 CPU 使用率
cpu_usage | time_aggr<[15s^15s], latest> | echo

# 查询平均 CPU 使用率
cpu_usage_last[:1h] | time_aggr<[15s^15s], avg> | tag_aggr<["host"], avg>
```

### COUNTER（计数器类型）

数值单调递增，表示累计总量。

**特点**：
- 只增不减（除非重启归零）
- 需要计算差值才有意义

**示例**：
- RPC 总请求次数
- 总错误次数
- 总处理字节数

**推荐聚合**：
- `latest`：取最新值（Metric 阶段）
- `delta`：计算增长量（查询阶段）

**MQL 示例**：
```
# Metric 阶段：采集最新总次数
rpc_request_total | time_aggr<[15s^15s], latest> | echo as rpc_request_total_count

# 查询阶段：计算每分钟的增长量
rpc_request_total_count[:1h] | time_aggr<[1m^1m], delta> | tag_aggr<["appReporter"], sum>
```

### 普通采样类型

每次采样都是独立的数据点（如每次请求的延迟、每次调用的状态码）。

**示例**：
- RPC 延迟
- HTTP 状态码
- 消息堆积数量

**推荐聚合**：
- `sum`：求和（如总延迟、总请求数）
- `count`：计数（如请求量）
- `centroid + quantile`：百分位数（如 P95/P99 延迟）
- `histogram`：分布统计

**MQL 示例**：
```
# 总延迟
rpc_rt | time_aggr<[15s^15s], sum> | tag_aggr<["appReporter"], sum>

# 请求数
rpc_rt | time_aggr<[15s^15s], count> | tag_aggr<["appReporter"], sum>

# 平均延迟 = 总延迟 / 请求数
tseries_div(rpc_rt_sum, rpc_request_count)

# P95/P99 延迟
rpc_rt | time_aggr<[15s^15s], centroid<20>> | tag_aggr<[], quantile<[95,99]>>
```

## 何时使用自主构建 MQL

绝大部分查询应该复用 Dashboard 中已验证的 MQL 模板。只有在以下情况才需要自主构建：

1. **Dashboard 中没有对应的查询面板**
2. **需要特殊的 tag 过滤或聚合逻辑**
3. **需要组合多个指标进行计算**（如 tseries_div）
4. **Dashboard 的 MQL 无法注入目标应用参数**

自主构建时，遵循以下原则：
- 使用正确的 tag（NSQ 指标用 `app`，其余用 `appReporter`）
- 根据指标类型选择合适的聚合函数（GAUGE 用 latest/avg，COUNTER 用 delta）
- 使用变量占位符，不硬编码
- 验证查询结果的合理性

## 参考资料

- `references/skynet-api.md`: Skynet API 完整文档
- `scripts/skynet.py`: MQL 构建和执行的 Python 实现
