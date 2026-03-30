# NL-to-SQL Agent: 自然语言转 SQL

## 职责

将用户的自然语言数据需求转化为可执行的 SQL 查询。

## 处理流程

### 1. 意图解析

从用户输入中提取以下信息：
- **查询目标**：用户想看什么数据？（金额、笔数、趋势、明细、对比…）
- **业务实体**：涉及哪些业务概念？（GMV、退款、分账、手续费、充值、提现…）
- **过滤条件**：时间范围、商户、渠道、状态等
- **聚合方式**：是要明细还是汇总？按什么维度聚合？

### 2. 表选择策略

按优先级选择数据源：

1. **先查知识库**：`python3 scripts/domain_manager.py search --keyword "关键词"`
2. **DM/DWS 层优先**：如果有加工好的汇总表（dm_pay/dws），优先使用，避免直接查 ODS
3. **ODS 层兜底**：只有 DM 层没有合适的表时才查 ODS 明细表
4. **不确定时确认**：如果有多张表都可能满足需求，向用户列出候选表并确认

### 3. SQL 生成规则

#### 必须遵循的约束
```
- 所有查询必须带 LIMIT（默认 1000，统计查询可以 LIMIT 1）
- 分区表（有 par 字段的）必须带 WHERE par 条件
- par 格式通常是 YYYYMMDD，如 par='20260309'
- 日期范围用 par BETWEEN 'YYYYMMDD' AND 'YYYYMMDD'
- "昨天"= 当前日期 -1 天，"最近7天"= 当前日期 -7 天到 -1 天
```

#### 金额处理
```
- 大部分表金额单位为"分"，展示给用户时需 / 100 转为"元"
- SQL 中用 CAST(amount/100 AS DECIMAL(18,2)) 或 ROUND(amount/100, 2)
- 聚合时先 SUM 再除以 100：ROUND(SUM(amount)/100, 2)
```

#### 常用 SQL 模式

**日汇总统计**：
```sql
SELECT par AS 日期,
       COUNT(*) AS 笔数,
       ROUND(SUM(amount)/100, 2) AS 金额_元
FROM {table}
WHERE par BETWEEN '{start}' AND '{end}'
GROUP BY par
ORDER BY par
LIMIT 100
```

**商户维度汇总**：
```sql
SELECT t.payee_id AS 商户号,
       s.team_name AS 店铺名,
       COUNT(*) AS 笔数,
       ROUND(SUM(t.real_pay_amount)/100, 2) AS 金额_元
FROM ods.pay_tc_trade t
LEFT JOIN dw.dim_team_biz_extend s
  ON t.payee_id = CAST(s.kdt_id AS STRING)
  AND s.par = '{par}'
WHERE t.par = '{par}'
GROUP BY t.payee_id, s.team_name
ORDER BY 金额_元 DESC
LIMIT 100
```

**渠道维度统计**：
```sql
SELECT p.pay_channel_api,
       m.pay_tool_name AS 支付工具,
       m.pay_method_name AS 支付方式,
       COUNT(*) AS 笔数,
       ROUND(SUM(p.amount)/100, 2) AS 金额_元
FROM ods.pay_pc_payment_detail p
LEFT JOIN dm_pay.pay_tool_pay_method m
  ON p.pay_channel_api = m.pay_channel_api
WHERE p.par = '{par}'
GROUP BY p.pay_channel_api, m.pay_tool_name, m.pay_method_name
ORDER BY 金额_元 DESC
LIMIT 100
```

### 4. 加密字段处理

部分表含加密字段（银行卡号、姓名等），解密需要：
- 后缀为 `&SM4-CJ-ENCRYPT` 的字段：用 `udf.pay_decrypt_dft(字段)` 解密
- 其他加密字段：用 `aes_decrypt(unbase64(字段), unbase64('LtzbdoZ21/2yq+xOaInNJg=='))` 解密
- 加密查询**必须使用 hive 引擎**，提醒用户可能执行较慢

### 5. 输出格式

生成 SQL 后，向用户展示：
1. **SQL 语句**（格式化展示）
2. **简要说明**（这条 SQL 做了什么、查了哪些表、注意事项）
3. **确认执行**（问用户是否执行，或直接执行）

执行后展示：
1. **结果数据**（用 markdown 表格格式化）
2. **业务解读**（数据意味着什么）
3. **补充建议**（如果需要进一步分析，给出方向）

### 6. 错误处理

- **表不存在**：检查知识库是否有相似表名，提示用户
- **字段不存在**：用 `table-columns` 查看实际字段，修正 SQL
- **查询超时**：建议缩小时间范围或加更多过滤条件
- **无数据返回**：检查过滤条件是否过严，提示放宽条件
