---
name: daily-review-feishu
description: 每日执行日总结，每周执行周复盘。将结果存入飞书文档，周评分写入本 agent 的多维表格。触发时间由 config.yml 的 schedule 字段配置。
config: ./config.yml
---

# 日总结+周复盘技能

> 📦 **首次使用**：请先阅读 `./INSTALL.md` 完成环境初始化，再使用本 Skill。

> 🔁 **元规则**：每次修改本 Skill 后必须通读全文，检查是否有重复、矛盾、废话，自行发现并修正，不等人工指出。

## 配置文件

所有 token / ID 从配置文件读取，**不在本文件硬编码**：

路径：`./config.yml`（与 SKILL.md 同目录）

字段说明：
- 用户称呼：从 agent workspace 根目录下的 `USER.md` 的 `What to call them` 字段读取，**不在 config.yml 配置**
- `schedule.daily` / `schedule.weekly`：cron 触发时间
- `storage.backend`：存储后端，当前支持 `feishu`
- `storage.daily_summary_folder_token`：每日总结文件夹 token
- `storage.weekly_review_folder_token`：每周复盘文件夹 token
- `storage.domain`：飞书域名（如 https://qima.feishu.cn）
- `score_table.enabled`：是否启用周评分表，默认且推荐 `true`；设为 `false` 则跳过第八步
- `score_table.app_token`：周评分多维表格 app token
- `score_table.table_id`：周评分表 table id

---

## 触发时间与覆盖范围

从 `./config.yml` 的 `schedule` 字段读取：
- **日总结**：每天 `schedule.daily` 触发（默认 `50 23 * * *`），覆盖当天 00:00 至触发时刻
- **周复盘**：每周 `schedule.weekly` 触发（默认 `10 0 * * 1`），覆盖上周一 00:00 至上周日 23:59

---

## 日总结流程（触发时间：schedule.daily）

### 第一步：读取记忆来源

1. **记忆文件**
   - `memory/YYYY-MM-DD.md`（当天的记忆文件）
   - `MEMORY.md`（扫描是否有与今天工作相关的规则或上下文，不需要全读）

2. **Session 历史（含飞书消息）**
   - `sessions_list` 获取今天所有活跃 session
   - `sessions_history` 逐一获取对话内容
   - 区分两类 session：
     - **飞书 session**：只取与我相关的部分（私聊、群聊中 @我/回复我的上下文），不读取我没参与的群聊内容
     - **内部操作 session**：记录我执行的任务、工具调用结果

### 第二步：归纳、总结、分类

**事件筛选标准——只记以下三类：**
1. **有结果产出的**：完成了某个功能、新建了某个东西
2. **有教训的**：出了问题、踩了坑（哪怕最终解决了）
3. **有决策的**：做了某个重要选择，值得日后追溯

**不记的**：查资料、看文档（无重要发现）、例行小操作、中间过程（只记结果和关键节点）、纯探讨没有产出结论的对话

**💼 支持类的额外筛选**：只有支持类中有价值产出才值得记（得出结论/决策/重要发现），纯聊天探讨没有产出的不记

**分类说明：**
- 🆕 **新建**：从无到有创建的东西（Skill、功能、规则、文档）
- 🔧 **修复**：bug、失误、配置错误
- ⚡ **优化**：对已有东西的改进、迭代、完善
- 💼 **支持**：业务查询、数据分析、协助 <USER.md: What to call them> 完成的具体任务

**主要事件格式：**

    🆕/🔧/⚡/💼 分类名
      N. 事件名称（HH:MM）
      - 具体做了什么
      - 结果 / 根因 / 修复方向（按实际情况选择）

**日总结文档固定模板（结构不可随意调整）：**

    ## 一、今日概览
    一句话总结今天的主题或状态。

    ## 二、主要事件
    （按上方筛选标准 + 分类格式填写）

    ## 三、系统变更记录
    只记对系统有持久影响的变更（Skill/配置/规则的具体改动内容），不重复主要事件的经过。
    格式：`文件名 | 变更类型 | 改动内容 | 原因`

    ## 四、问题与阻塞
    今天遇到的问题：
    - 问题描述
    - 当前状态（已解决 / 未解决 / 待跟进）

    ## 五、关键教训
    今天踩的坑或发现的经验，及时记录，不等周复盘。

    ## 六、待办事项（次日）
    今天没完成、明天要跟进的事。

    ## 七、今日心情
    一句话。

**分工原则**：
- 一～四：事实陈述，只记发生了什么，不加判断
- 五：当天教训，及时沉淀，比等周复盘更准确
- 六：明天的输入
- 七：给这一天定调

### 第三步：生成日总结文档

> 当前仅实现了 `feishu` backend，其他 backend（如 Notion、local）待扩展。

1. **检查文档是否存在**
   - folder_token 从 config.yml 读取：`storage.daily_summary_folder_token`
   - 标题：`xxxx年xx月xx日-总结`
   - **判断方式**：`feishu_drive(action="list", folder_token=<storage.daily_summary_folder_token>)`，看是否有当天标题的文档，不依赖记忆文件判断

2. **文档规则**
   - 每天只有一个文档
   - 多次执行**覆盖**原内容
   - 如果当天内容过少（少于3条事件），可以跳过创建，在次日总结中补记「昨日补记」

3. **操作**
   ```
   # 文档不存在则创建
   feishu_doc(action="create", title="xxxx年xx月xx日-总结", folder_token=<storage.daily_summary_folder_token>)
   # 文档存在则覆盖（用已有 doc_token）
   feishu_doc(action="write", doc_token=<daily_doc_token>, content=总结内容)
   ```

### 第四步：更新周复盘文档

1. **获取本周日期范围**（周一 ~ 周日）

2. **检查/创建周复盘文档**
   - folder_token 从 config.yml 读取：`storage.weekly_review_folder_token`
   - 标题：`xxxx年xx月xx日-xxxx年xx月xx日-周复盘总结`（周一日期-周日日期）
   - **判断方式（按顺序降级）**：
     1. 优先查当天或本周任意一天的记忆文件（`memory/YYYY-MM-DD.md`），找「本周周复盘 doc_token」字段
     2. 记忆文件中没有 → 尝试 `feishu_drive(action="list", folder_token=<storage.weekly_review_folder_token>)` 列出文件夹
     3. feishu_drive 报错（权限不足）→ 直接创建新文档
   - 找到或创建后，将 doc_token 写入当天记忆文件，供本周后续日子复用

   ```
   # 文档不存在则创建
   feishu_doc(action="create", title="xxxx年xx月xx日-xxxx年xx月xx日-周复盘总结",
     folder_token=<storage.weekly_review_folder_token>)
   # 创建后立即写入记忆文件
   memory/YYYY-MM-DD.md → 本周周复盘 doc_token: <weekly_doc_token>
   ```

3. **追加日总结链接（严禁覆盖）**

   > ⚠️ **周复盘文档只能 append，绝对不能 write/覆盖！**
   > 每天只追加当天这一条，不能清空或重写整个文档。

   ```
   feishu_doc(action="append", doc_token=<weekly_doc_token>,
     content="- [xxxx年xx月xx日-总结](<storage.domain>/docx/<daily_doc_token>)")
   ```

   `<weekly_doc_token>` 直接使用步骤2查找/创建结果中得到的 token。

---

## 周复盘流程（触发时间：schedule.weekly）

### 第一步：找到本周周复盘文档

1. 列出「每周复盘」文件夹内的文件：`feishu_drive(action="list", folder_token=<storage.weekly_review_folder_token>)`
2. 找到本周标题（`xxxx年xx月xx日-xxxx年xx月xx日-周复盘总结`）对应的文档
3. 找不到则新建（极少发生，正常情况日总结流程已维护该文档）

### 第二步：获取所有日总结链接

```
feishu_doc(action="read", doc_token=<weekly_doc_token>)
# 从返回内容中解析以 "- [" 开头的行，提取每条日总结的 doc_token
```

### 第三步：逐一读取日总结内容

```
对于每个日总结链接：
  feishu_doc(action="read", doc_token=<daily_doc_token>)
  提取「二、主要事件」和「三、系统变更记录」两章内容
```

> ⚠️ **降级处理**：某天链接找不到或文档读取失败 → 跳过该天，在周复盘中标注「XX月XX日无记录」，不因单天缺失中断整个周复盘。

### 第四步：深度分析

数据来源：各日总结的「二、主要事件」+ 「三、系统变更记录」合并汇总。

按**事情性质**分类汇总：

- 🆕 **新建**：本周从无到有创建的东西
- 🔧 **修复**：本周发现并解决的 bug、失误、配置错误
- ⚡ **优化**：本周对已有东西的改进、迭代、完善
- 💼 **支持**：本周协助 <USER.md: What to call them> 完成的有价值任务（无产出的对话不计入）

**写作要求**：
- 每条事件必须带一句结论——说明它的影响或意义，不能只陈述事实
- 格式：`事件描述 → 所以/意味着/说明 + 判断`
- 每个分类末尾加一句**小结**：这个方向本周整体状态如何

### 第五步：KPT 复盘（进化核心）

这是最重要的一步，必须认真执行，不能走过场。

#### K — Keep（做得好的，继续保持）
- 具体描述做了什么
- 为什么值得保持

#### P — Problem（问题 + 根因 + 改进）
每条必须包含：
- **发生了什么**：具体描述
- **根本原因**：追问到底，不能只说"操作失误"
- **改进措施**：下次具体怎么做

#### T — Try（下周要落地的一件事）
从 Problem 里选最重要的一条，转化为具体可执行的改进动作。只选一件，必须具体。

#### Score — 四维评分

| 维度 | 本周得分 | 上周得分 | 趋势 |
|------|----------|----------|------|
| 执行力（按时完成任务） | ? | ? | ↑/↓/→ |
| 主动性（不等指令、自己发现问题） | ? | ? | ↑/↓/→ |
| 稳定性（失误次数和严重程度，分越高越稳） | ? | ? | ↑/↓/→ |
| 进化速度（踩坑后是否真的改了） | ? | ? | ↑/↓/→ |

**一句话总结**：本周比上周好在哪里，差在哪里。

### 第六步：Append 到周复盘文档

```
feishu_doc(action="append", doc_token=<weekly_doc_token>, content=深度分析+KPT复盘)
```

### 第七步：把经验落地到 .learnings/

> ⚠️ 进化闭环的关键，不能省略。写在飞书文档里只有"看到才有用"，写进 `.learnings/` 才是每次 session 启动都能读到的长期记忆。

从第五步 KPT 中提取：

1. **Problem 里的每个坑** → 写入 workspace 下的 `.learnings/ERRORS.md`
2. **Keep / Try 里的最佳实践** → 写入 workspace 下的 `.learnings/LEARNINGS.md`
3. **足够重要的经验**（影响所有 session 行为）→ 同时晋升到 `MEMORY.md` 的「经验教训」章节

格式参考 `self-improvement` Skill，ID 格式：`LRN-YYYYMMDD-XXX` / `ERR-YYYYMMDD-XXX`。

**判断标准**：
- 偶发问题 → ERRORS.md
- 反复出现的模式 → LEARNINGS.md + 考虑晋升 MEMORY.md
- 影响危险操作/核心行为 → 必须晋升 MEMORY.md

### 第八步：写入周评分记录表

> `score_table.enabled` 默认 `true`，无需改动。如需禁用，在 config.yml 中设置 `false` 后跳过本步。

```
feishu_bitable_create_record(
  app_token=<score_table.app_token>,        # 从 config.yml 读取
  table_id=<score_table.table_id>,          # 从 config.yml 读取
  fields={
    "周期": "YYYY年MM月DD日-MM月DD日",
    "执行力": <1-10>,
    "主动性": <1-10>,
    "稳定性": <1-10>,
    "进化速度": <1-10>,
    "核心改进": "下周 Try 的那一件事",
    "周复盘链接": {"text": "周复盘文档", "link": "<storage.domain>/docx/<weekly_doc_token>"}
  }
)
```

评分表地址：`<storage.domain>/base/<score_table.app_token>`

---

---

## 完成通知

日总结和周复盘执行完毕后，**必须发飞书私聊通知宽哥**，消息格式如下：

### 日总结完成通知

```
✅ 2026年XX月XX日 日总结已完成

📄 日总结：<storage.domain>/docx/<daily_doc_token>
📋 本周复盘：<storage.domain>/docx/<weekly_doc_token>

今日主线：<一句话概括今天最重要的事>
```

### 周复盘完成通知

```
✅ XXXX年XX月XX日-XX月XX日 周复盘已完成

📋 周复盘文档：<storage.domain>/docx/<weekly_doc_token>

本周评分：执行力X | 主动性X | 稳定性X | 进化速度X
下周 Try：<一件具体的改进动作>
```

**发送方式**：`message(action="send", channel="feishu", target="user:ou_fd3df39b5a00787f454fe0a856059bdb", message=<通知内容>)`

1. **日总结多次执行覆盖，周复盘只能追加**
2. **只获取与我相关的消息，不读取无关群聊**
3. **如果当天内容过少（少于3条事件），跳过创建，在次日总结中补记「昨日补记」**
4. **所有 token 从 config.yml 读取，不在 SKILL.md 内硬编码**
