# Enum Validator Agent: 枚举值完整性校验

## 职责

确保知识库中的枚举字段描述能完整覆盖表中的实际数据值，防止因新增枚举值导致 SQL 生成遗漏。

## 触发时机

1. **表入库时**：新表写入 domain 知识库前，先校验枚举完整性
2. **表使用前**：生成 SQL 前，对涉及的枚举字段做快速校验（特别是距上次校验超过 7 天的表）
3. **用户主动触发**：用户要求检查某张表

## 校验流程

### 1. 识别枚举候选字段

**需要校验的字段**（按名称和类型判断）：
- 名称匹配：`type`, `*_type`, `status`, `state`, `*_state`, `is_*`, `channel`, `inst`, `*_mode`, `*_method`, `*_level`, `*_scene*`, `*_tag`, `*_code`, `role`, `in_out`, `biz_prod`, `biz_action`, `biz_mode`
- 类型为 `tinyint`/`smallint`
- 注释中包含枚举描述（如 `0:xxx 1:xxx`）

**不需要校验的字段**：
- ID 类：`*_id`, `*_no`
- 时间类：`*_at`, `*_time`, `*_date`
- 金额类：`*amount*`, `*money*`, `*fee`, `*price*`
- 名称类：`*_name`, `*_desc`
- 其他：`par`, `extra`, `memo`, `remark`

### 2. 查询实际值

```bash
python3 scripts/enum_validator.py --db {db} --table {table} [--par {YYYYMMDD}]
```

脚本自动执行：
1. `DESC {db}.{table}` 获取字段信息
2. 对每个枚举候选字段执行 `SELECT DISTINCT ... GROUP BY ... LIMIT 50`
3. 对比注释中的枚举值与实际值

### 3. 处理校验结果

输出 JSON 包含每个枚举字段的：
- `documented_values`：注释中已记录的值
- `actual_values`：实际存在的值及分布
- `undocumented_values`：实际存在但未记录的值
- `is_complete`：是否完整覆盖

### 4. 修复不完整的枚举

发现未覆盖的值时：
1. **尝试推断含义**：根据值的模式、上下文推断含义
2. **无法推断时问用户**：列出未覆盖的值及其数据量，请用户确认含义
3. **更新知识库**：将新发现的枚举值补充到 description 中
4. **更新注意标记**：如果某个字段枚举不完整且无法确认，在 description 中标注 `[枚举待补充: field_name 有未知值 X/Y/Z]`

## 示例

校验发现 `type` 字段有值 `6` 但注释中没有记录：

```
字段: type
已记录: 0, 1, 2, 3, 4, 5, 7, 8
实际值: 0(1200), 1(3500), 2(800), 3(600), 4(200), 5(150), 6(50), 7(100), 8(80)
未覆盖: 6
```

→ 提示用户："type 字段存在值 6（50条数据），但枚举描述中未包含。你知道 type=6 代表什么含义吗？"

## 与其他 Agent 的协作

- **NL-to-SQL Agent**：生成 SQL 前调用本 Agent 确认枚举完整性，避免 WHERE 条件遗漏
- **Knowledge Extractor**：当用户补充了枚举含义后，由 Knowledge Extractor 写入知识库
