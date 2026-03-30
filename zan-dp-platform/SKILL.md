---
name: zan-dp-platform
description: 有赞大数据平台(dp)工具，执行 Hive/Spark/Presto SQL 查询、表元数据与血缘分析、任务管理、Airflow 调度查看，通过业务知识库将业务术语映射为数据表。默认金融云。触发：提及数仓表名、dp 平台、SQL 查询、数据血缘/任务、或用业务术语描述数据需求时使用。
tags: data-pipeline, python, sql, fintech
author: liuzhiyu
created: 2026-03-09T02:32:33.577Z
updated: 2026-03-09T02:32:33.577Z
---
# zan-dp-platform

## 技能执行前置说明

每次技能执行前，必须执行以下步骤：

1. 记录本次执行使用的本地 `updated`（来自当前 `SKILL.md` frontmatter）
2. 通过 Helm 获取远程 `zan-dp-platform` 的最新 `updated`（例如先执行 `helm skill pull zan-dp-platform` 同步本地缓存，再读取对应 `SKILL.md` 的 `updated`）
3. 比较远程 `updated` 与本地 `updated`：
   - 一致：结束流程
   - 不一致：将远程最新版本拉取并覆盖更新到当前技能目录
4. 若自动更新成功，在本次技能结束回复中明确告知用户：已检测到新版本并完成自动更新
5. 使用数据上报（每次执行都必须调用）：
   - 优先执行脚本（位于当前技能目录）：
```bash
bash scripts/report-usage.sh zan-dp-platform 1
```
   - 其中 `zan-dp-platform` 为当前执行的技能名（必传）。

统一入口：`python3 scripts/dp.py <子命令> [参数]`

每个子命令支持：`--site fin|main`（默认 fin 金融云），`--format json|table|csv|markdown`

`query` 和 `export` 还支持：`--engine SPARK|PRESTO|HIVE`（可选，默认 SPARK）

## 认证

Token 存储在 `~/.config/dp-platform/token.json`。Token 失效（401 错误）时：
```bash
# 金融云 dp（访问 https://dp.fin.qima-inc.com 登录后复制 Cookie）
python3 scripts/token_manager.py --save "YOUR_COOKIE"
# 主站 dp
python3 scripts/token_manager.py --save-main "YOUR_COOKIE"
# Airflow（访问 https://airflow.prod.fin.qima-inc.com 登录后复制 Cookie）
python3 scripts/token_manager.py --save-airflow "YOUR_COOKIE"
```

## 命令速查

### 数据查询
```bash
python3 scripts/dp.py list-dbs
python3 scripts/dp.py list-tables --db ods
python3 scripts/dp.py query --sql "SELECT * FROM ods.pay_order LIMIT 10"
python3 scripts/dp.py get-result --uuid "202603060100096a16a315"
```

### 表元数据
```bash
python3 scripts/dp.py table-schema --db ods --table pay_order
python3 scripts/dp.py table-columns --db ods --table pay_order
python3 scripts/dp.py table-partitions --db ods --table pay_order
python3 scripts/dp.py table-stats --db ods --table pay_order
python3 scripts/dp.py table-sample --db ods --table pay_order --limit 5
```

### 数据血缘
```bash
python3 scripts/dp.py lineage-upstream --db ods --table pay_order
python3 scripts/dp.py lineage-downstream --db ods --table pay_order
python3 scripts/dp.py lineage-column --db dm_pay --table pay_fee_mch_strategy_danbao --column fee_cycle_mode
python3 scripts/dp.py lineage-to-bi --db dm_pay --table pay_fee_mch_strategy_danbao
# 以上命令均支持可选参数 --par YYYYMMDD 指定血缘分区日期
```

### 数据导出
```bash
python3 scripts/dp.py export --sql "SELECT * FROM ods.pay_order WHERE par='20260306' LIMIT 100"
python3 scripts/dp.py export --sql "..." --filetype csv --output /tmp/result.csv
python3 scripts/dp.py export-by-uuid --uuid "2026030713001403a7b92d"
```

### 任务管理
```bash
python3 scripts/dp.py task-search --keyword "订单同步"
python3 scripts/dp.py task-workflow --job-id 1261
python3 scripts/dp.py task-detail --job-id 5613 --job-type code-hive
python3 scripts/dp.py task-list --page 1 --page-size 20
python3 scripts/dp.py task-list --all
```

### Airflow 调度状态
```bash
python3 scripts/dp.py airflow-status --dag-id WORKFLOW_imp_ga_account_log_inc
# airflow-status 支持可选 --execution-date 指定执行日期
python3 scripts/dp.py airflow-runs --dag-id WORKFLOW_imp_ga_account_log_inc
python3 scripts/dp.py airflow-task-detail --dag-id WORKFLOW_imp_ga_account_log_inc --execution-date "2026-03-06T01:00:00"
# airflow-task-detail 支持可选 --task-id 过滤特定任务
python3 scripts/dp.py airflow-log --dag-id WORKFLOW_imp_ga_account_log_inc --task-id hql_pay_tc_trade_idc_for_pay --execution-date "2026-03-06T01:00:00"
```

## Domain 业务知识库

`domain/` 目录存储表/任务/工作流与业务语义的映射关系，是 skill 的核心记忆。

管理入口：`python3 scripts/domain_manager.py <子命令> [参数]`

### 命令速查
```bash
# 搜索 - 按业务关键词跨类型搜索
python3 scripts/domain_manager.py search --keyword "充值"
python3 scripts/domain_manager.py search --keyword "手续费" --type table

# 查看
python3 scripts/domain_manager.py get --type table --key "ods.pay_order"
python3 scripts/domain_manager.py list --type table

# 新增/更新
python3 scripts/domain_manager.py upsert --type table --key "ods.pay_order" \
  --fields '{"name":"支付订单","description":"记录所有支付订单明细"}'

# 批量更新
python3 scripts/domain_manager.py batch-upsert --type table \
  --entries '{"ods.pay_order":{"name":"支付订单","description":"记录所有支付订单明细"}}'

# 删除
python3 scripts/domain_manager.py delete --type table --key "ods.pay_order"

# 导出全部
python3 scripts/domain_manager.py export
```

### domain 文件结构
```
domain/
├── tables.json      # 表 → 业务语义映射
├── tasks.json       # 任务 → 业务语义映射
└── workflows.json   # 工作流 → 业务语义映射
```

每条记录包含以下字段：
- `job_name` — 平台技术名称（任务/工作流在 dp 平台上的英文名，如 `pay_dm_data`、`pay_transfer_success_items`），用于与 Airflow DAG ID、任务搜索等关联
- `name` — 中文业务名
- `description` — 业务描述，自由文本，包含所有有价值的业务信息

注：tables.json 的 key 本身就是 `db.table` 格式，不需要额外的技术名称字段。

## 整体工作方式

这个 skill 的核心思路是：用户用业务语言说需求，你通过 domain 知识库把业务语言翻译成技术操作，执行后把新发现的业务知识沉淀回 domain。这样 skill 会越用越聪明。

具体来说，你需要判断用户处于以下哪种情况，然后跳进去帮忙：

**用户说的是业务术语**（如"查一下充值明细"、"看看手续费策略"）— 这是最有价值的场景。读取 `agents/business-resolver.md`，按照里面的流程把模糊的业务意图解析成具体的表/任务/工作流。解析过程中可能需要搜索 domain 知识库、反问用户确认、展示候选列表。解析清楚后再决定怎么查。

**用户明确指定了表名或 SQL** — 直接执行就行。但在决定用哪个命令、SQL 怎么写时，读取 `agents/query-advisor.md` 获取策略建议，特别是分区条件检查、数据量评估、导出 vs 查询的选择。这些约束很重要，因为大数据平台上一个不带 LIMIT 的查询可能跑几十分钟。

**呈现分析结论时** — 涉及数据聚合、多表关联、字段语义推断、枚举值解读等场景时，读取 `agents/data-reliability.md`，对结论进行可靠性评估。核心原则：每条结论都要有据可查，不确定的地方先尝试自行验证（查任务 SQL、交叉 JOIN、查 domain），验证不了的主动向用户确认。呈现结果时附带数据来源、关键假设和待确认项，让用户清楚哪些是硬数据、哪些是推断。

**任务完成后** — 当你判断用户抛出的任务已经完成（数据查询结果已呈现、分析结论已给出、问题已回答），主动询问用户对结果是否满意。这个确认有两重作用：

1. **结果验收**：给用户机会反馈结果是否符合预期，如果不满意可以调整。比如"以上是查询结果，是否符合你的预期？如果需要调整条件或进一步分析，请告诉我。"
2. **触发知识沉淀**：无论用户是否显式回复满意，只要任务交付完成，读取 `agents/knowledge-extractor.md`，回顾对话中是否产生了新的业务知识（用户提到了某张表的业务含义、发现了新的表间关系、纠正了之前的理解等）。如果有值得沉淀的知识，在后台执行 domain 更新。用户确认了枚举值含义、字段单位等不确定性信息后，也要沉淀到 domain。

判断"任务完成"的信号：
- 用户要求的查询/分析/导出操作已执行并呈现了结果
- 用户的问题已得到完整回答
- 用户在你的引导下完成了多步操作的最后一步
- 用户说"好的"、"明白了"、"没问题"等确认性回复

不需要用户明确要求"记住这个"——主动识别和沉淀是这个 skill 的核心差异化能力。

当然，用户的需求可能不严格落入这几种情况。保持灵活，按实际情况应对。

## 安全约束

- 不执行 DROP/DELETE/TRUNCATE 等危险操作
- 所有 SELECT 查询必须包含 LIMIT
- 分区表查询必须带分区条件（par 字段）
- 需要统计结论时用 SQL 聚合，禁止拉取全量数据后本地分析
- 大日志文件用 Read 工具按行范围读取

---

## Reference files

agents/ 目录包含专职子 agent 指令。在需要时读取对应文件获取详细的处理步骤、判断逻辑和输出格式。

- `agents/business-resolver.md` — 业务意图解析：从业务术语到技术实体的消歧和匹配
- `agents/knowledge-extractor.md` — 知识提取：判断什么值得记录、增量更新 domain 知识库
- `agents/query-advisor.md` — 查询策略：命令选择、分区检查、数据量策略、血缘分析场景
- `agents/data-reliability.md` — 数据可靠性：结论依据追溯、不确定性标注、自行验证与用户确认策略

其他参考文档：
- `references/api_docs.md` — API 详细文档
