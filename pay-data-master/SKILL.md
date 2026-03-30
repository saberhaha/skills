---
name: pay-data-master
description: 支付数据大师 - 理解支付业务语义，将自然语言转化为SQL查询并执行。支持GMV/PMV查询、退款分析、分账明细、手续费统计、充值提现、商户数据等。触发：提及GMV/PMV、支付表名(ods.pay_*/dm_pay.*)、kdt_id/user_no、支付业务术语(退款/分账/手续费/充值/提现)时使用。默认金融云。触发：提及数仓表名、dp 平台、SQL 查询、数据血缘/任务、或用业务术语描述数据需求时使用。
tags: payment, sql, data-query, fintech, natural-language, gmv, pmv
author: huangzhenxin
created: 2026-03-10T00:00:00.000Z
updated: 2026-03-11T10:30:00.000Z
---
# pay-data-master

## 技能调用方式

**直接调用**：
```
请 pay-data-master 帮我查询...
```

**触发条件**（满足任一即自动调用）：
- 提到支付业务术语：GMV、PMV、退款、分账、手续费、充值、提现、转账
- 提到支付业务表名：`ods.pay_*`、`dm_pay.*`、`dev.pay_*` 等
- 提到店铺/商户相关：kdt_id、user_no、有赞商户号
- 需要查询支付相关数据
- 触发：提及数仓表名、dp 平台、SQL 查询、数据血缘/任务、或用业务术语描述数据需求时使用。

**命令行直接调用**：
```bash
# 进入技能目录
cd "/Users/huangzhenxin/Documents/youzan/鑫一笔记/支付数据助手/pay-data-master"

# 搜索知识库
python3 pay_data_master.py search --keyword "GMV"

# 执行 SQL
python3 pay_data_master.py query --sql "SELECT * FROM ods.pay_order LIMIT 10"

# 自然语言解析（自动分析是否值得沉淀为工作流）
python3 pay_data_master.py nl --text "查询店铺117301428的PMV"

# 自然语言 + 执行 + 自动保存工作流
python3 pay_data_master.py nl --text "查询店铺117301428的2026年PMV" --execute --save-workflow

# 工作流管理
python3 pay_data_master.py workflow list
python3 pay_data_master.py workflow analyze --sql "..." --text "描述"
python3 pay_data_master.py workflow save --sql "..." --text "描述" --name "my_pattern"
python3 pay_data_master.py workflow delete --name "my_pattern"
```

## 概述

支付数据大师：理解支付业务，说人话查数据。

用户用自然语言描述数据需求，skill 自动完成：
1. **理解意图** — 解析业务术语，映射到具体的数据库表和字段
2. **生成 SQL** — 根据意图生成安全、高效的 SQL 查询
3. **执行查询** — 通过 DP 平台执行 SQL 并返回结果
4. **自动沉淀** — 分析查询模式，自动识别并保存可复用的工作流
5. **知识积累** — 在对话中持续积累支付业务知识

## 技能执行前置说明

每次技能执行前，必须执行以下步骤：

1. 每次技能执行前，必须先执行以下命令（位于当前技能目录）：
```bash
bash scripts/pre-execute.sh pay-data-master
```
2. 这是强制命令，AI 不得跳过
3. 若脚本输出检测到新版本并完成自动更新，在本次技能结束回复中明确告知用户：已检测到新版本并完成自动更新

## 统一入口

`python3 scripts/dp.py <子命令> [参数]`

每个子命令支持：`--site fin|main`（默认 fin 金融云），`--format json|table|csv|markdown`
`query` 和 `export` 还支持：`--engine SPARK|PRESTO|HIVE`（可选，默认 SPARK）

## 认证

Token 存储在 `~/.config/dp-platform/token.json`。Token 失效（401 错误）时：
```bash
# 金融云 dp（访问 https://dp.fin.qima-inc.com 登录后复制 Cookie）
python3 scripts/token_manager.py --save "YOUR_COOKIE"
# 主站 dp
python3 scripts/token_manager.py --save-main "YOUR_COOKIE"
```

## 命令速查

### 数据查询
```bash
python3 scripts/dp.py query --sql "SELECT * FROM ods.pay_order LIMIT 10"
python3 scripts/dp.py query --sql "SELECT * FROM ods.pay_order LIMIT 10" --format markdown
python3 scripts/dp.py get-result --uuid "UUID"
```

### 表元数据
```bash
python3 scripts/dp.py table-columns --db ods --table pay_order
python3 scripts/dp.py table-sample --db ods --table pay_order --limit 5
```

### Domain 知识库管理

#### 表翻译工具（推荐）
自动从数据库获取表结构、枚举值，并写入知识库：

```bash
# 基本用法 - 自动翻译表
python3 scripts/translate_table.py dev.dm_all_pay_recharge_22_now

# 指定表名和描述
python3 scripts/translate_table.py dm_pay.pay_merchant_pay_config \
  --name "子商户号配置表" \
  --desc "商户的子商户号配置，包括类型、状态、费率、渠道等" \
  --business "商户配置"
```

#### 手动管理
```bash
python3 scripts/domain_manager.py search --keyword "充值"
python3 scripts/domain_manager.py get --type table --key "ods.pay_order"
python3 scripts/domain_manager.py list --type table
python3 scripts/domain_manager.py upsert --type table --key "ods.pay_order" \
  --fields '{"name":"支付订单","description":"记录所有支付订单明细"}'
```

## 核心工作流程

### 第零步：【强制】检查 Workflow 增强理解

**在生成任何 SQL 之前，必须先执行：**

```bash
python3 pay_data_master.py workflow list
```

**检查 workflow 的目的**：
1. **理解业务语义** — workflow 解释了业务场景（如"大额支付"是 channel_name=185，而非金额大）
2. **理解表关系** — steps 展示了表之间如何关联
3. **参考 SQL 写法** — 学习类似场景的 SQL 模式
4. **检查是否有匹配模板** — 意图匹配时直接使用

**⚠️ 跳过此步骤会导致业务语义理解偏差、表关系遗漏、过滤条件错误！**

### 第一步：理解用户意图

收到自然语言查询后，读取 `agents/nl-to-sql.md`，按照以下流程处理：

1. **识别业务实体** — 从用户输入中提取业务关键词（如"GMV"、"退款"、"分账"、"手续费"、"充值"等）
2. **查询知识库** — 用 `domain_manager.py search` 搜索相关表，确定目标表
3. **枚举完整性校验** — 对涉及的表执行枚举校验（见下方"枚举值校验"章节），确保 SQL 条件不会遗漏
4. **确认表结构** — 如果知识库描述不够详细，用 `table-columns` 查询字段信息
5. **生成 SQL** — 基于表结构和用户意图生成 SQL（但如果第一步找到了 workflow，优先用 workflow）

### 第二步：生成并执行 SQL

SQL 生成必须遵循安全约束：
- **必须包含 LIMIT**（默认 LIMIT 1000）
- **分区表必须带 par 条件**
- **禁止 DROP/DELETE/TRUNCATE**
- **需要统计结论时用 SQL 聚合**，禁止拉取全量数据后本地分析
- **金额字段注意单位**：大部分表金额单位为"分"，展示时需除以100转为"元"

#### 分区字段说明

**par 分区（快照分区）**：
- 含义：每天落一份全量快照，例如 par='20260301' 表示 2026年3月1日 的数据快照
- 用法：查询时必须带 `par='${DP_1_DAYS_AGO_Ymd}'` 取前一天（最新）数据
- 示例：`SELECT * FROM dm_pay.pay_merchant_pay_config WHERE par='${DP_1_DAYS_AGO_Ymd}' LIMIT 10`
- 常见表：dm_pay.pay_merchant_pay_config、dw.dim_team_biz_extend、dm_pay.yz_to_fin_shop_type_for_pay_pmv

**非快照分区（事件时间分区）**：
- 有些表按事件时间分区，如 par='20260301' 表示当天发生的交易
- 需要根据业务需求选择日期范围

**非分区表**：
- 无 par 字段，需要用业务时间字段过滤，如 `pay_day >= '2026-03-01'`
- 示例：dev.dm_all_pay_recharge_22_now 使用 `WHERE pay_day >= '2026-03-01'`
- 注意：非分区大表查询务必带时间条件，否则可能超时

### 第三步：呈现结果

- 用清晰的格式展示查询结果
- 对数据做简要的业务解读
- 主动标注数据的可靠性和局限性

### 第四步：知识沉淀

任务完成后，读取 `agents/knowledge-extractor.md`，判断对话中是否产生了新的业务知识：
- 用户提到了某张表的业务含义
- 发现了新的表间关系
- 纠正了之前的理解
- 新的枚举值含义、字段单位等

如有值得沉淀的知识，用 `domain_manager.py upsert/batch-upsert` 更新知识库。

### 第五步：工作流自动沉淀

每次执行自然语言查询后，自动分析 SQL 是否值得沉淀为工作流：

**沉淀评分标准**：

| 特征 | 分数 | 说明 |
|------|------|------|
| 多表 JOIN | +2 | 表关联规则值得沉淀 |
| ID 转换规则 | +2 | 涉及 pay_funds_user type=10 |
| 复杂过滤（≥2个 AND） | +1 | 过滤条件多 |
| 枚举字段过滤 | +1 | offline_tag/gmv_type 等 |
| 聚合计算 | +1 | SUM/AVG/COUNT |
| 时间范围过滤 | +1 | pay_day/pay_month 等 |

**阈值：分数 ≥ 3 分建议沉淀**

**自动沉淀流程**：
1. 执行 `nl` 命令时自动分析 SQL
2. 如果分数 ≥ 3，提示用户可以保存
3. 用户使用 `--save-workflow` 参数确认保存
4. 自动生成工作流文件到 `workflows/` 目录

```bash
# 查看分析结果
python3 pay_data_master.py nl --text "查询店铺PMV"

# 确认保存
python3 pay_data_master.py nl --text "查询店铺PMV" --save-workflow
```

## 常见查询场景快速参考

### GMV/PMV 相关
- 核心表：`dev.pay_gmv_pmv_mch_22_now`（按商户+日维度汇总）
- 上游：`dev.all_pay_recharge_22_now` → `dev.dm_tc_trade_pay_recharge_22_now`
- BI 原始表：`dm_pay.dm_all_pay_recharge_22_now`

### 交易/支付相关
- 交易主表：`ods.pay_tc_trade`（一笔交易一条记录）
- 支付明细：`ods.pay_pc_payment_detail`（通道层支付明细）
- 新收单订单：`ods.pay_new_pay_order`
- 旧收单订单：`ods.pay_order`
- 全量支付成功明细：`dm_pay.all_pay_succ_payment_detail`

### 退款相关
- 退款明细：`ods.pay_pc_refund_detail`
- 退款合约：`ods.pay_pc_refund_contract`

### 分账相关
- 分账账单：`ods.pay_profit_sharing_bill`
- 分账渠道明细：`dm_pay.profit_sharing_channel_trade_detail`
- 分账对账差异：`dm_pay.profit_sharing_bills_check_error_detail`

### 手续费相关
- 手续费账单：`ods.pay_fee_bill_trade`
- 结算手续费：`ods.pay_settle_fee`

### 充值相关
- 充值明细：`dwd.dwd_pay_recharge_detail_df`
- 凭证充值：`ods.pay_pc_payment_voucher`

### 提现/转账相关
- 提现指令：`ods.pay_pc_withdraw_instruction`
- 转账明细：`ods.pay_pc_transfer_detail`
- 出金渠道流水：`ods.pay_withdraw_channel_trans_flow_main`
- 转账成功明细：`dev.pay_transfer_success_items`
- 提现统计：`dev.pay_withdraw_mch_date_22_now`

### 商户/店铺相关
- 店铺维度：`dw.dim_team_biz_extend`
- 店铺认证：`dw.dim_team_cert_info`
- 资金用户：`ods.pay_funds_user`

### 维度表
- 渠道类型：`dm_pay.pay_channel_type`
- 支付工具/方式：`dm_pay.pay_tool_pay_method`
- 合作方：`dm_pay.pay_partner_id_info`
- 业务产品：`dm_pay.pay_biz_prod_enum`
- 店铺类型(PMV)：`dm_pay.yz_to_fin_shop_type_for_pay_pmv`

## 枚举值校验

表写入知识库时或使用前，需要校验枚举字段的实际值是否被知识库描述完整覆盖。

```bash
# 有 par 分区的表（快照分区，默认 par='${DP_1_DAYS_AGO_Ymd}'）
python3 scripts/enum_validator.py --db dm_pay --table pay_merchant_pay_config
python3 scripts/enum_validator.py --db dm_pay --table pay_merchant_pay_config --par 20260309

# 无 par 分区的表（需指定时间字段或自动检测）
python3 scripts/enum_validator.py --db dev --table dm_all_pay_recharge_22_now --time-field pay_day
```

详细处理流程见 `agents/enum-validator.md`。

**触发时机**：
- 新表写入知识库前
- 生成涉及枚举字段的 SQL 前（特别是 WHERE 条件用到枚举值时）
- 用户主动要求检查时

**处理原则**：
- 发现未覆盖的值时，先尝试根据上下文推断含义
- 无法推断时向用户确认
- 确认后更新知识库的 description 字段

## 安全约束

- 不执行 DROP/DELETE/TRUNCATE 等危险操作
- 所有 SELECT 查询必须包含 LIMIT
- 分区表查询必须带分区条件（par 字段）
- 需要统计结论时用 SQL 聚合，禁止拉取全量数据后本地分析
- 涉及加密字段时提示用户需要 hive 引擎运行

## SQL 查询示例库

存储常用 SQL 查询模板，快速复用和理解表关系。

### 命令速查

```bash
# 列出所有示例
python3 scripts/query_examples.py list

# 按标签过滤
python3 scripts/query_examples.py list --tag GMV

# 按表名过滤
python3 scripts/query_examples.py list --table dev.dm_all_pay_recharge_22_now

# 查看示例详情
python3 scripts/query_examples.py show gmv_by_kdt_date

# 运行示例（带参数）
python3 scripts/query_examples.py run gmv_by_kdt_date \
  --param kdt_id=56789 \
  --param start_date=2026-03-01 \
  --param end_date=2026-03-10

# 跳过预览直接执行
python3 scripts/query_examples.py run gmv_by_kdt_date --param kdt_id=56789 -y

# 添加新示例（交互式）
python3 scripts/query_examples.py add "示例名称" "描述" "SELECT * FROM table WHERE id={{id}}"
```

### 示例结构

每个示例包含：
- **ID**: 唯一标识
- **名称**: 简短描述
- **描述**: 详细说明
- **SQL**: 查询语句（支持参数占位符 `{{param_name}}`）
- **标签**: 分类标签（如 GMV、退款、认证）
- **涉及表**: 自动提取或手动指定
- **参数**: 可替换的参数列表

### 查看示例

```bash
# 列出所有示例（会显示最新数量和详情）
python3 scripts/query_examples.py list

# 按标签过滤
python3 scripts/query_examples.py list --tag GMV

# 按表名过滤
python3 scripts/query_examples.py list --table dev.dm_all_pay_recharge_22_now
```

> 💡 示例库会持续扩充，使用 `list` 命令查看最新示例

## Reference files

- `agents/nl-to-sql.md` — 自然语言转 SQL 的核心处理流程
- `agents/enum-validator.md` — 枚举值完整性校验策略
- `agents/knowledge-extractor.md` — 知识提取与沉淀策略
- `scripts/translate_table.py` — 表翻译工具（自动获取表结构和枚举值）
- `scripts/query_examples.py` — SQL 查询示例管理器
- `examples/query_examples.json` — SQL 示例库数据
- `workflows/*.json` — **SQL 工作流模板（必须优先检查）**
