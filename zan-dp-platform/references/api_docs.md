# dp 平台 API 完整文档

## 基础信息

- **Base URL (金融云)**: `https://dp.fin.qima-inc.com`
- **Base URL (主站)**: `https://data.qima-inc.com/garden-api-request/dp`
- **认证方式**: Cookie
- **响应格式**: JSON

## 认证机制

所有 API 请求需要在 Header 中携带 Cookie 认证信息：

```
Cookie: YOUR_COOKIE_STRING_HERE
```

### 获取 Cookie

```bash
python3 scripts/token_manager.py --save "YOUR_COOKIE_STRING"
```

## 通用响应格式

```json
{
  "code": 0,        // 0=成功, 非0=失败
  "data": {},       // 响应数据
  "msg": ""         // 错误信息（成功时为空）
}
```

## API 端点详情

### 1. 数据库管理

#### 1.1 获取数据库列表

```http
GET /v1/hive/dbs-read
```

**响应示例**：
```json
{
  "code": 0,
  "data": [
    "bi", "dev", "dm_acct", "dm_biz", "dw",
    "ods", "dwd", "dws", "ads", "tmp"
  ],
  "msg": ""
}
```

#### 1.2 获取表列表

```http
GET /v1/hive/meta/getTables?db={db_name}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| db | string | 是 | 数据库名称 |

**响应示例**：
```json
{
  "code": 0,
  "data": [
    "table1", "table2", "table3"
  ],
  "msg": ""
}
```

#### 1.3 获取表元数据
  ```http
  GET /garden-api-request/dp/v1/hive/meta/getColumns?db={db}&table={table}
  ```

  **参数**：
  | 参数 | 类型 | 必填 | 说明 |
  |------|------|------|------|
  | db | string | 是 | 数据库名称 |
  | table | string | 是 | 表名称 |


### 2. SQL 查询

#### 2.1 提交查询

```http
POST /v1/sql/run
Content-Type: application/json
```

**请求体**：
```json
{
  "sql": "SELECT * FROM ods.table LIMIT 10",
  "engine": "",           // 空=自动选择, hive/spark/presto
  "confirm": false,       // 是否需要确认
  "limitSize": 1000       // 最大返回行数
}
```

**响应**：
```json
{
  "code": 0,
  "data": {
    "engine": "PRESTO",
    "msg": "",
    "normal": true,
    "runResult": [
      {
        "key": "202603060100096a16a315",  // 查询 UUID
        "value": "SELECT * FROM ods.table LIMIT 10"
      }
    ],
    "type": "normal"
  },
  "msg": ""
}
```

> **重要**: `runResult[0].key` 是查询 UUID，用于后续获取结果

#### 2.2 获取查询结果

```http
GET /v1/sql/history/{uuid}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uuid | string | 是 | 查询 UUID |

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "columns": 3,
    "completed": true,
    "engine": "PRESTO",
    "executeEndTime": 1772732965389,
    "executeStartTime": 1772732965379,
    "hasResult": true,
    "metaData": [
      {
        "columnName": "id",
        "columnType": "BIGINT",
        "comment": "主键ID",
        "partitionColumn": false
      },
      {
        "columnName": "name",
        "columnType": "VARCHAR",
        "comment": "名称",
        "partitionColumn": false
      },
      {
        "columnName": "par",
        "columnType": "STRING",
        "comment": "分区字段",
        "partitionColumn": true
      }
    ],
    "queryResult": [
      [1, "Alice", "20260101"],
      [2, "Bob", "20260101"]
    ],
    "rows": 2,
    "sql": "SELECT * FROM ods.table WHERE par='20260101' LIMIT 10",
    "success": true
  },
  "msg": ""
}
```

**字段说明**：
- `metaData`: 列元数据信息
  - `columnName`: 列名
  - `columnType`: 数据类型
  - `comment`: 列注释
  - `partitionColumn`: 是否为分区字段
- `queryResult`: 数据行数组
- `rows`: 总行数
- `completed`: 是否完成
- `success`: 是否成功

### 3. 任务管理

#### 3.1 搜索任务

```http
GET /v1/jobs/search-job?desc={keyword}
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| desc | string | 是 | 搜索关键词 |

**响应示例**：
```json
{
  "code": 0,
  "data": [
    {
      "id": 5493,
      "job-name": "订单同步任务",
      "job-state": "运行中",
      "job-type": "code-hive",
      "owner": {
        "casId": 20289,
        "email": "user@example.com",
        "nickname": "张三"
      },
      "updateTime": 1772732965000
    }
  ],
  "msg": ""
}
```

#### 3.2 获取任务列表

```http
GET /v1/jobs?filter-by-self=true&page-num=1&page-size=10&sort-field=updateTime&sort-order=desc
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filter-by-self | boolean | 否 | 是否只看自己的任务 |
| page-num | int | 否 | 页码 |
| page-size | int | 否 | 每页数量 |
| sort-field | string | 否 | 排序字段 |
| sort-order | string | 否 | 排序方向 (asc/desc) |

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 5493,
        "name": "订单同步任务",
        "state": "RUNNING",
        "type": "code-hive",
        "schedule": "0 0 * * *",
        "lastRunTime": 1772732965000,
        "nextRunTime": 1772819365000
      }
    ],
    "total": 50,
    "pageNum": 1,
    "pageSize": 10
  },
  "msg": ""
}
```

#### 3.3 获取工作流详情

```http
GET /v1/jobs/workflow/{job_id}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job_id | int | 是 | 工作流 ID |

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "id": 1146,
    "job-name": "pay_dm_data",
    "job-state": "已发布",
    "job-type": "workflow",
    "dag-state": "online",
    "description": "收单和支付域数据集市",
    "cron": "8 8 * * *",
    "nextScheduleTime": "2026-03-07 08:08:00",
    "create-time": 1702020661000,
    "update-time": 1770347109000,
    "owner": {
      "casId": 669,
      "username": "lixiukuan",
      "nickname": "宽哥",
      "email": "lixiukuan@youzan.com"
    },
    "alert-users": [
      {
        "casId": 669,
        "username": "lixiukuan",
        "nickname": "宽哥",
        "email": "lixiukuan@youzan.com"
      }
    ],
    "inner-jobs": [
      {
        "id": 5613,
        "job-name": "dm_all_pay_recharge_22_now",
        "job-type": "code-hive",
        "job-state": "已测试",
        "cron": "8 8 * * *",
        "global-priority": 4,
        "pre-jobs": [
          {
            "id": 5655,
            "job-name": "pay_team_product_info",
            "job-runtime": "today",
            "job-type": "code-hive"
          }
        ],
        "read-tables": [
          "dm_pay.dm_trading_pay_order_22_now",
          "ods.pay_tc_trade_relation"
        ],
        "write-tables": [
          "dev.dm_all_pay_recharge_22_now"
        ],
        "owner": {
          "casId": 669,
          "username": "lixiukuan"
        }
      }
    ],
    "node-relations": [
      {
        "nodeId": 20,
        "nodeType": "TASK",
        "jobId": 5557,
        "preNodeIds": [],
        "tableName": ""
      }
    ],
    "read-tables": ["ods.pay_settle_fee", "ods.pay_fee_bill_trade"],
    "write-tables": ["dev.dm_all_pay_recharge_22_now"]
  },
  "msg": ""
}
```

**字段说明**：
- `inner-jobs`: 工作流包含的子任务列表
  - `pre-jobs`: 前置依赖任务
  - `read-tables`: 读取的表
  - `write-tables`: 写入的表
- `node-relations`: 任务节点关系图
  - `nodeType`: 节点类型 (TASK/TABLE_DEP)
  - `preNodeIds`: 前置节点 ID 列表
- `alert-users`: 告警接收人列表
- `nextScheduleTime`: 下次调度时间

#### 3.4 获取单个任务详情

```http
GET /v1/jobs/single/{job_id}?job-type={job_type}
```

**路径参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job_id | int | 是 | 任务 ID |

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| job-type | string | 是 | 任务类型 (code-hive/code-spark/export-hive-bitable) |

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "id": 5613,
    "job-name": "dm_all_pay_recharge_22_now",
    "job-type": "code-hive",
    "job-state": "已测试",
    "description": "22年至今新老支付系统的支付、充值明细",
    "cron": "8 8 * * *",
    "code": "-- SQL 代码内容",
    "code-args": {
      "runEngine": "SPARK"
    },
    "pre-jobs": [
      {
        "id": 5655,
        "job-name": "pay_team_product_info",
        "job-runtime": "today",
        "job-type": "code-hive"
      }
    ],
    "read-tables": [
      "dm_pay.dm_trading_pay_order_22_now",
      "ods.pay_tc_trade_relation"
    ],
    "write-tables": [
      "dev.dm_all_pay_recharge_22_now"
    ],
    "owner": {
      "casId": 669,
      "username": "lixiukuan",
      "nickname": "宽哥"
    }
  },
  "msg": ""
}
```

**字段说明**：
- `code`: 任务的 SQL 代码或脚本内容
- `code-args`: 代码执行参数（如运行引擎）
- `pre-jobs`: 前置依赖任务列表
- `read-tables`: 读取的数据表
- `write-tables`: 写入的数据表


### 4. 数据血缘

> 血缘信息通过查询 ODS 元数据表获取。
> 所有血缘表按 `par` 字段分区，查询时必须带分区条件。

#### 4.1 表级血缘 - `ods.md_lineage_table_table`

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| parent_db_name | varchar | 上游表的数据库名 |
| parent_table_name | varchar | 上游表名 |
| parent_table_id | integer | 上游表 ID |
| child_db_name | varchar | 下游表的数据库名 |
| child_table_name | varchar | 下游表名 |
| child_table_id | integer | 下游表 ID |
| task_url | varchar | 关联的 dp 任务 URL |
| task_id | varchar | 关联的 dp 任务 ID |
| task_owner | varchar | 任务负责人 |
| par | varchar | 分区键 (YYYYMMDD) |

查询上游示例：
```sql
SELECT parent_db_name, parent_table_name, child_db_name, child_table_name, task_id, task_owner, task_url
FROM ods.md_lineage_table_table
WHERE par = '20260306'
  AND child_db_name = 'ods' AND child_table_name = 'pay_order'
```

查询下游示例：
```sql
SELECT parent_db_name, parent_table_name, child_db_name, child_table_name, task_id, task_owner, task_url
FROM ods.md_lineage_table_table
WHERE par = '20260306'
  AND parent_db_name = 'ods' AND parent_table_name = 'pay_order'
```

#### 4.2 字段级血缘 - `ods.md_lineage_column_column`

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| child_table_db_name | varchar | 下游表数据库 |
| child_table_name | varchar | 下游表名 |
| child_table_type | varchar | 下游表类型 (hive/rdb) |
| child_column_name | varchar | 下游字段名 |
| parent_table_db_name | varchar | 上游表数据库（格式可能为 db.schema） |
| parent_table_name | varchar | 上游表名 |
| parent_table_type | varchar | 上游表类型 |
| parent_column_name | varchar | 上游字段名 |
| relation_type | varchar | 关系类型 (TRANSFER 等) |
| project_name | varchar | 关联的项目/工作流名称 |
| project_url | varchar | 项目 URL |
| par | varchar | 分区键 (YYYYMMDD) |

> 注意：同一分区内可能存在多个 `current_day` 的快照数据，建议用 GROUP BY 去重。

#### 4.3 表到 BI 血缘 - `ods.md_lineage_table_bi`

| 字段 | 类型 | 说明 |
|------|------|------|
| table_id | integer | 表 ID（需与其他表关联获取表名） |
| child_bi_id | integer | BI 报表 ID |
| bi_sql_id | integer | BI SQL ID |
| par | varchar | 分区键 |

> 注意：此表只有 ID 字段，没有表名和 BI 名称，实用性有限。

#### 4.4 工作流读写表（补充血缘来源）

通过工作流详情 API `GET /v1/jobs/workflow/{job_id}` 返回的 `read-tables` 和 `write-tables` 字段也能获得任务级别的表血缘关系。

### 5. Airflow 调度执行状态

> Airflow 地址: `https://airflow.prod.fin.qima-inc.com`
> 认证方式: Cookie（与 dp 平台独立，需单独配置）
> dp 平台工作流对应 Airflow DAG，命名规则通常为 `WORKFLOW_{工作流名称}`

#### 5.1 获取任务实例详情（JSON API）

```http
GET /admin/airflow/object/task_instances?dag_id={dag_id}&execution_date={execution_date}
```

返回 JSON 格式的任务实例数据，每个任务包含：

| 字段 | 说明 |
|------|------|
| task_id | 任务名称 |
| state | 状态: success/failed/running/queued/retry/upstream_failed |
| operator | 算子类型: SparkSQLBashOperator/MysqlToHivePythonOperator/YzHiveTableSensor/DummyOperator |
| start_date | 开始时间 |
| end_date | 结束时间 |
| duration | 耗时（秒） |
| try_number | 重试次数 |
| hostname | 执行节点 |
| pool | 资源池: k8s/sensor/datax |
| queued_dttm | 入队时间 |

#### 5.2 Graph View 页面（HTML，含嵌入 JSON）

```http
GET /admin/airflow/graph?dag_id={dag_id}&execution_date={execution_date}&arrange=LR&task_state=All
```

页面 HTML 中嵌入了以下 JavaScript 变量（JSON 格式）：
- `var nodes = [...]` — DAG 节点列表
- `var edges = [...]` — 依赖关系 `{u: "task_a", v: "task_b"}`
- `var tasks = {...}` — 任务元数据（task_type, dag_id）
- `var task_instances = {...}` — 任务实例详情（同 5.1）
- `<select id="execution_date">` — 可用的执行日期列表

#### 5.3 其他 Airflow 页面

| 页面 | URL | 用途 |
|------|-----|------|
| Tree View | `/admin/airflow/tree?dag_id={dag_id}` | 树状历史视图 |
| Gantt | `/admin/airflow/gantt?dag_id={dag_id}` | 甘特图 |
| Task Log | `/admin/airflow/log?dag_id={dag_id}&task_id={task_id}&execution_date={date}` | 任务日志 |
| DAG Runs | `/admin/dagrun/?flt2_dag_id_equals={dag_id}` | 运行记录列表 |

### 6. 数据导出

#### 6.1 提交导出请求

```http
POST /v1/sql/dump
Content-Type: application/json
```

**请求体**：
```json
{
  "sql": "SELECT * FROM ods.table LIMIT 100",
  "uuid": "202603060100096a16a315",
  "engine": "sparksql",
  "filetype": "excel"
}
```

**参数说明**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| sql | string | 是 | 要导出的 SQL 语句 |
| uuid | string | 是 | 查询 UUID（来自 /v1/sql/run 的 runResult[0].key） |
| engine | string | 是 | 查询引擎（hive/spark/sparksql/presto），小写 |
| filetype | string | 是 | 导出文件类型：excel 或 csv |

> **前置条件**: 需要先通过 `/v1/sql/run` 执行查询获取 UUID，再用该 UUID 提交导出请求。

#### 6.2 查询导出审批状态

```http
GET /v1/apply/getApplyByType?isAdmin=false&isGroup=false&pageNum=1&pageSize=10
```

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| isAdmin | boolean | 否 | 是否管理员视角，默认 false |
| isGroup | boolean | 否 | 是否组视角，默认 false |
| pageNum | int | 否 | 页码 |
| pageSize | int | 否 | 每页数量 |

**响应示例**：
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "applyDetails": {
          "downloadUrl": "http://dp-download.prod.fin.qima-inc.com/v1/dump/center/download/20461",
          "fileType": "EXCEL",
          "id": 20461,
          "rows": 1,
          "sql": "SELECT ...",
          "sqlEngine": "SPARKSQL",
          "userName": "liuzhiyu",
          "uuid": "2026030713001403a7b92d"
        },
        "applyPerson": "liuzhiyu",
        "applyType": "DUMP_APPLY",
        "createTime": 1772865654000,
        "id": 20461,
        "state": "AUTO",
        "title": "SELECT ..."
      }
    ],
    "total-size": 19
  },
  "msg": ""
}
```

**审批状态 (state)**：
| 状态 | 说明 |
|------|------|
| AUTO | 自动审批通过（少量数据） |
| SUCCESS | 人工审批通过 |
| INIT / PENDING | 等待人工审核（大数据量） |

> **关键字段**: 通过 `applyDetails.uuid` 匹配查询记录。`state` 为 AUTO 或 SUCCESS 时可直接下载；为 INIT/PENDING 时需要用户到 dp 平台手动审批后下载。

#### 6.3 下载导出文件

```http
GET {downloadUrl}
```

使用 `applyDetails.downloadUrl` 返回的地址下载文件。下载域名为 `dp-download.prod.fin.qima-inc.com`，需要携带 Cookie 认证。

## 常用 SQL 示例

### 查看表结构

```sql
DESC FORMATTED ods.pay_order
```

### 查看分区

```sql
SHOW PARTITIONS ods.pay_order
```

### 查看创建表语句

```sql
SHOW CREATE TABLE ods.pay_order
```

### 查看分区统计

```sql
ANALYZE TABLE ods.pay_order PARTITION(par='20260306') COMPUTE STATISTICS
```

## 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 0 | 成功 | - |
| 401 | 未授权 | 重新获取 Token |
| 403 | 无权限 | 检查权限配置 |
| 404 | 资源不存在 | 检查参数是否正确 |
| 20000 | 业务错误 | 查看 msg 字段 |
| 20001 | SQL 语法错误 | 检查 SQL 语法 |
| 20002 | 分区字段缺失 | 添加分区条件 |
| 20003 | 查询超时 | 优化 SQL 或增加 LIMIT |

## 最佳实践


### 1. 异步查询

对于耗时查询：
1. 提交查询获取 UUID
2. 轮询查询状态
3. 获取最终结果

```python
# 1. 提交查询
result = submit_query(sql)
uuid = result['data']['runResult'][0]['key']

# 2. 等待完成
time.sleep(2)

# 3. 获取结果
final_result = get_query_result(uuid)
```

## 参考链接
- https://daas.qima-inc.com/docs/dp/
- https://qima.feishu.cn/wiki/wikcnYwjBwqSSBvDLfDUlTHm5pf?from=from_lark_index_search&ccm_open_type=from_lark_index_search&disposable_login_token=eyJ1c2VyX2lkIjoiNzU2ODY3MzAxMjExNjUwNDU3OCIsImRldmljZV9sb2dpbl9pZCI6Ijc1Njg3NDI0NDQ2ODMxNjU3MjQiLCJ0aW1lc3RhbXAiOjE3NzI4MDMzNDQsInVuaXQiOiJldV9uYyIsInB3ZF9sZXNzX2xvZ2luX2F1dGgiOiIxIiwidmVyc2lvbiI6InYzIiwidGVuYW50X2JyYW5kIjoiZmVpc2h1IiwicGtnX2JyYW5kIjoi6aOe5LmmIn0%3D.6304fd4f8ca8d826e68d6046eb2f77d75121bd493796302858ca28f0fa51627d
- https://qima.feishu.cn/wiki/SjtqwWWYVixigEkZPX5caMPgnJg
