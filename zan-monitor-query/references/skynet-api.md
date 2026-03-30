# Skynet API 参考

## 基础信息

- **Skynet API Base**: `https://ops.qima-inc.com/v3/skynet`
- **Grafana API Base**: `https://skynet-grafana.prod.qima-inc.com`
- **Content-Type**: `application/json`

### 请求头

```
Cookie: cas=<CAS_TOKEN>; TSID=<TSID>; cas_username=<username>; access_user=<user_id>; XIAOLV_SESSION_ID_prod=<session_id>
x-yz-bu: fincloud | main          # 业务线：金融云 / 主站
x-yz-env: qa | pre | prod          # 环境
```

### Grafana 数据源

| uid | name | type | 用途 |
|-----|------|------|------|
| ohBeg1n7z | Query Skynet | query-skynet-query-skynet | Skynet MQL 查询 |
| NqTRM25Iz | ClickHouse | grafana-clickhouse-datasource | 告警/TopN SQL 查询 |
| Y_ycvUJ7z | main-prod-prometheus | prometheus | 主站 Prometheus |
| 8A-HSxvHk | fin-container-prod | prometheus | 金融云容器 Prometheus |
| NHplyu_nk | fin-skynet | query-skynet-query-skynet | 金融云 Skynet |
| lHbhD8J7z | fincloud-prod-prometheus | prometheus | 金融云 Prometheus |
| lB_gz177z | List Apps | apps-list-apps | 应用列表数据源 |
| oEZRz17nz | List Tag Options | tags-list-tag-options | Tag 筛选项数据源 |
| zZAgkJn7z | List Granularity Options | granularity-options-list-granularity-options | 聚合粒度选项 |
| IAI3JEInz | main-nsq-ops | prometheus | NSQ OPS Prometheus |

## 核心 API

### 1. MQL 执行 (核心接口)

执行监控查询，获取时间序列数据。

**请求**
```bash
POST /v3/skynet/v2/mql:execute
Headers: x-yz-bu, x-yz-env
Content-Type: application/json

{
  "queries": [{
    "queryId": "Q1",
    "mql": "rpc_server_error_ratio_by_app{appReporter=${appReporter:STRING}}${timeRange:TIME_RANGE} | time_aggr<${granularity:SLIDING_WINDOW}, sum> | tag_aggr<[], sum>",
    "initialInputMetric": "rpc_server_error_ratio_by_app"
  }],
  "params": {
    "timeRange": {
      "startTimeSecond": 1710770200,
      "endTimeSecond": 1710772000
    },
    "granularity": {"len": 60, "unit": "s"},
    "others": {
      "appReporter": "pay-payment-core",
      "env": "prod"
    }
  }
}
```

说明：
- 文档和 Agent 工作流统一要求：动态参数使用变量占位符 + `params.others`
- 应用名、topic、service、method 等字段不要硬编码到 MQL 模板中
- `params.others` 中的 typed value 需保留 JSON 原生类型；`INT`/`DOUBLE`/`BOOL` 不要统一写成字符串
- 不带引号的字符串写法（如 `appReporter=pay-payment-core`）会触发 MQL 解析错误

**响应**
```json
{
  "results": [{
    "queryId": "Q1",
    "timeSeries": [{
      "tagSet": {"appReporter": "pay-payment-core", "host": "xxx-pod-name"},
      "dataPoints": [
        {"timestamp": 1710770200000000, "value": 0.003},
        {"timestamp": 1710770260000000, "value": 0.004}
      ]
    }]
  }]
}
```

**字段说明**: tagSet-标签集合, dataPoints-时间序列数据点(时间戳为微秒)

### 2. Dashboard 搜索

获取 Grafana Dashboard 列表，用于增量同步。

**请求**
```bash
GET https://skynet-grafana.prod.qima-inc.com/api/search?limit=200
Cookie: grafana_session=xxx
```

**响应**
```json
[
  {
    "id": 1,
    "uid": "rOTyWB7nz",
    "title": "RPC 监控",
    "type": "dash-db",
    "version": 12,
    "modified": "2026-03-15T08:30:00Z"
  }
]
```

### 3. Dashboard 详情

获取单个 Dashboard 的完整配置，提取 MQL。

**请求**
```bash
GET https://skynet-grafana.prod.qima-inc.com/api/dashboards/uid/{uid}
Cookie: grafana_session=xxx
```

**响应**
```json
{
  "dashboard": {
    "uid": "rOTyWB7nz",
    "title": "RPC 监控",
    "panels": [{
      "title": "Server 总 QPS",
      "targets": [{
        "mql": "rpc_server_qpm_in_app{appReporter=${appReporter}}..."
      }]
    }]
  }
}
```

### 4. Tag 值查询

获取指标 tag 的可能值，用于参数补全和验证。

**请求**
```bash
GET /v3/skynet/v2/metrics/{metricName}/tags/{tagName}/values?filter=(key=value)
Headers: x-yz-bu, x-yz-env
```

**示例**
```bash
GET /v3/skynet/v2/metrics/rpc_server_qpm_in_app_service_method/tags/service/values?filter=(appReporter=pay-payment-core)
Headers: x-yz-bu: fincloud, x-yz-env: prod
```

**响应**
```json
{
  "items": [
    "com.youzan.pay.payment.core.api.PaymentCoreService",
    "com.youzan.pay.order.api.OrderService"
  ]
}
```

### 5. zan-alert 告警记录详情

查询某次具体告警事件的发送详情、通知对象和原始告警内容。

**请求**
```bash
GET https://ops.qima-inc.com/api/v1.0/zan-alert/alarm/record/{recordId}?buId={buId}
Headers: buid, x-yz-bu, x-yz-env
```

**示例**
```bash
GET https://ops.qima-inc.com/api/v1.0/zan-alert/alarm/record/208386506?buId=2
Headers:
  buid: 2
  x-yz-bu: fincloud
  x-yz-env: prod
```

`buid` 映射：
- `fincloud` -> `2`
- `main` -> `1`

**响应**
```json
{
  "message": "success",
  "code": 0,
  "data": {
    "id": 208386506,
    "app": "pay-trading-query",
    "item": "消息depth高t:binlog_pay_tc_trade，c:pay_trading_query|CRITICAL",
    "level": "critical",
    "env": "fin",
    "notify_groups": ["应用默认告警组", "支付核心"],
    "receivers": ["liuzhiyu", "youzanalert"],
    "channels": ["phone", "wechat"],
    "date": 1774079638000,
    "status": "发送成功",
    "content": "发生时间：03-21 15:48:00 ~ 03-21 15:51:00 ..."
  },
  "success": true
}
```

**用途**:
- 根据 `recordId` 直接查看某次告警事件内容
- 核对通知对象、触达渠道、发送状态
- 提取 `app`、`content`、告警时间窗，再回查对应监控指标

### 5.1 zan-alert 告警记录列表

按用户名、时间范围、应用、级别等维度查询告警记录列表。

**请求**
```bash
GET https://ops.qima-inc.com/api/v1.0/zan-alert/alarm/records?buId={buId}&username={username}&page_index=0&page_size=10
Headers: buid, x-yz-bu, x-yz-env
```

**可选参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| username | string | 用户名，如 liuzhiyu |
| begin_time | int | 开始时间戳（秒） |
| end_time | int | 结束时间戳（秒） |
| env | string | 告警环境筛选，如 prod/pre/qa |
| level | string | 告警级别，如 critical/warning |
| isFd | string | 是否只看 fd 告警，true/false |
| fdTypeKey | string | fd 类型，如 "应用问题\|预发" |
| sendSuccess | string | 发送是否成功，true/false |
| app | string | 应用名筛选 |
| page_index | int | 分页起始页，默认 0 |
| page_size | int | 每页条数，默认 10 |

**响应**
```json
{
  "message": "success",
  "code": 0,
  "data": {
    "total": 42,
    "list": [
      {
        "id": 208386506,
        "app": "pay-trading-query",
        "item": "消息depth高...|CRITICAL",
        "level": "critical",
        "env": "fin",
        "date": 1774079638000,
        "status": "发送成功"
      }
    ]
  },
  "success": true
}
```

### 6. 指标搜索

通过关键词搜索指标。

**请求**
```bash
GET /v3/skynet/v2/mql/selectors?type=DERIVED_METRIC|RAW_METRIC&keyWords={keywords}
Headers: x-yz-bu, x-yz-env
```

**示例**
```bash
GET /v3/skynet/v2/mql/selectors?keyWords=rpc+error
Headers: x-yz-bu: fincloud, x-yz-env: prod
```

**响应**
```json
{
  "items": [
    {
      "name": "rpc_server_error_ratio_by_app",
      "description": "RPC Server 错误率"
    }
  ]
}
```

说明：
- `type=DERIVED_METRIC` 用于搜索派生指标
- `type=RAW_METRIC` 用于搜索原始指标

## 指标列表 API

### 1. 获取所有应用列表

```bash
GET /v3/skynet/v1/apps
Headers: x-yz-bu, x-yz-env
```

**响应**:
```json
[
  {"id": 73, "name": "websocketgw", "type": "", "level": 1, "cmdbProductId": 2, "enName": ""},
  {"id": 74, "name": "deploy", "type": "JAVA", "level": 3, "cmdbProductId": 13, "enName": ""}
]
```

**字段说明**: id-应用ID, name-应用名, type-应用类型(JAVA/GO/NODEJS/Generic等)

### 2. 原始指标列表 (重要)

```bash
GET /v3/skynet/v2/rawMetrics?id={id}&name={name}&pageSize=100&pageNumber=1
Headers: x-yz-bu, x-yz-env
```

- **总数**: 约 1222 个
- **用途**: 获取用户自定义指标，包含指标定义、标签、描述

**响应**:
```json
{
  "totalSize": 1222,
  "pageSize": 20,
  "pageNumber": 1,
  "items": [
    {
      "topic": "monitoring.metric.apps.default",
      "id": "mall-trade-buyer.appointment.create",
      "owningApp": "mall-trade-buyer",
      "name": "预约单创建业务监控",
      "tagDescriptors": [
        {"name": "error_code", "comment": "错误码", "type": "USER_DEFINED"},
        {"name": "success", "comment": "是否成功", "type": "USER_DEFINED"}
      ],
      "description": "统计预约单成功率"
    }
  ]
}
```

### 3. 派生指标列表 (重要)

```bash
GET /v3/skynet/v2/derivedMetrics?pageSize=100&pageNumber=1
Headers: x-yz-bu, x-yz-env
```

- **总数**: 约 8311 个
- **用途**: 获取 MQL 计算的指标，包含完整 MQL 表达式

**响应**:
```json
{
  "totalSize": 8311,
  "items": [
    {
      "id": "mall-trade-buyer.appointment.create.success.rate",
      "owningApp": "mall-trade-buyer",
      "name": "预约单生成成功率",
      "srcMetricId": "mall-trade-buyer.appointment.create",
      "rawMql": "tseries_div(mall-trade-buyer.appointment.create{success=\"1\"} | time_aggr<[1m^1m], count> | tag_aggr<[\"channel\", \"env\", \"symbol\"], sum> as metricA, mall-trade-buyer.appointment.create{} | time_aggr<[1m^1m], count> | tag_aggr<[\"channel\", \"env\", \"symbol\"], sum> as metricB)"
    }
  ]
}
```

### 4. 监控项列表 (重要)

```bash
GET /v3/skynet/v2/monitors?pageSize=100&pageNumber=1&view=CONFIG
Headers: x-yz-bu, x-yz-env
```

- **总数**: 约 9151 个
- **用途**: 获取监控配置，用于根据业务描述查找指标

**响应**:
```json
{
  "totalSize": 9151,
  "items": [
    {
      "id": 13515,
      "name": "ipaas-coding-proxy Tsp定时任务执行失败数过高",
      "description": "Tsp定时任务执行失败数过高",
      "monitoredMetricNames": "fromV1.Tsp客户端各任务类型失败数",
      "owningApp": "ipaas-coding-proxy",
      "levels": ["WARNING"]
    }
  ]
}
```

### 5. 监控项详细配置

```bash
GET /v3/skynet/v2/monitorWithNotifyingSettings/{id}
Headers: x-yz-bu, x-yz-env
```

**用途**: 获取监控项完整配置，包含 MQL 查询、告警规则

**响应**:
```json
{
  "id": 13515,
  "name": "xxx",
  "metricQueries": [
    {
      "name": "监控项名称",
      "rawQuery": "xxx {app=\"xxx\"} ${timeRange:TIME_RANGE} | time_aggr<${slidingWindow:SLIDING_WINDOW}, max>"
    }
  ],
  "warningTrigger": {
    "level": "WARNING",
    "continuingTimes": 3,
    "comparisons": [{"operator": "GT", "value": {"end": 0.0}}]
  }
}
```

## MQL 语法

### 基本结构

```
metric_name{tag_filters}[startSec,endSec]
  | time_aggr<window, function>
  | tag_aggr<[keep_tags], function>
  | post_processing
```

### 操作符

| 操作符 | 语法 | 说明 |
|--------|------|------|
| time_aggr | `time_aggr<{len:60,unit:s}, sum>` | 时间维度聚合 |
| tag_aggr | `tag_aggr<[], sum>` | 标签维度聚合 |
| div | `div<${divisor:INT}>` | 除法运算；推荐通过 `params.others.divisor` 注入 |
| top | `top<20>` | Top N |
| quantile | `quantile<[95,99]>` | 百分位计算 |
| tseries_div | `tseries_div(A, B)` | 时间序列相除 |

### 过滤器

| 类型 | 语法 | 示例 |
|------|------|------|
| 精确匹配 | `tag="value"` | `appReporter="some-app"` |
| 正则匹配 | `tag=~"pattern"` | `appReporter=~"pay-payment.*"` |
| 排除匹配 | `tag!~"pattern"` | `status!~"success.*"` |

## 同步策略

### 首次启动同步

1. 获取 Dashboard 列表（/api/search）
2. 遍历每个 Dashboard 获取详情
3. 提取 panels 中的 MQL
4. 解析指标元数据
5. 保存到本地 `domain/data.json`

### 增量更新

1. 获取 Dashboard 列表（仅元数据）
2. 比对 version/modified 时间戳
3. 仅拉取变更的 Dashboard
4. 更新本地指标库
5. 记录同步元数据

### 日常查询

- 指标搜索：本地 grep 检索
- 数据查询：直接调用 MQL 执行 API
- Tag 补全：按需调用 Tag 值 API
