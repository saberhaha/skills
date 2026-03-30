# INSTALL.md - 安装与初始化指南

本文件描述首次使用 `daily-review-feishu` Skill 前需要完成的环境准备工作。
**安装只需做一次**，完成后正常使用 SKILL.md 即可。

---

## 前置条件

- 已安装 OpenClaw，agent 可正常运行
- 有飞书账号，bot 已获得云文档读写权限
- 准备一个飞书 Bitable 多维表格（用于周评分记录）

---

## 第一步：自动创建飞书目录结构

**由 agent 自动执行，无需人工操作。**

### 目录结构

在飞书应用根目录下自动创建以下结构：

```
飞书根目录/
└── {agent名} 工作目录/     ← 从 IDENTITY.md 的 Name 字段读取，未填则用 daily-review-feishu
    ├── 每日总结/            ← 存放每天的日总结文档
    └── 每周复盘/            ← 存放每周的周复盘文档
```

### 执行步骤

按以下顺序执行，每步优先用内置工具，失败则降级用飞书 API：

**1. 读取 agent 名称**
```
从 workspace 根目录 IDENTITY.md 的 Name 字段读取 agent 名
未填写则使用 daily-review-feishu 作为目录名
构造工作目录名：「{agent名} 工作目录」
```

**2. 创建工作目录**（在飞书根目录下）
```
# 优先
feishu_drive(action="create_folder", name="{agent名} 工作目录")

# 降级：飞书 API（空 folder_token 表示根目录）
tenant_access_token = POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
  body: { app_id, app_secret }  # 从 ~/.openclaw/openclaw.json 读取

POST https://open.feishu.cn/open-apis/drive/v1/files/create_folder
  headers: Authorization: Bearer <tenant_access_token>
  body: { name: "{agent名} 工作目录", folder_token: "" }

→ 记录返回的 token 为 root_folder_token
```

**3. 创建「每日总结」子文件夹**
```
# 优先
feishu_drive(action="create_folder", name="每日总结", folder_token=<root_folder_token>)

# 降级：飞书 API
POST https://open.feishu.cn/open-apis/drive/v1/files/create_folder
  body: { name: "每日总结", folder_token: "<root_folder_token>" }

→ 记录返回的 token 为 daily_summary_folder_token
```

**4. 创建「每周复盘」子文件夹**
```
# 优先
feishu_drive(action="create_folder", name="每周复盘", folder_token=<root_folder_token>)

# 降级：飞书 API
POST https://open.feishu.cn/open-apis/drive/v1/files/create_folder
  body: { name: "每周复盘", folder_token: "<root_folder_token>" }

→ 记录返回的 token 为 weekly_review_folder_token
```

**5. 将两个 token 自动写入 config.yml**
```
storage.daily_summary_folder_token  ← daily_summary_folder_token
storage.weekly_review_folder_token  ← weekly_review_folder_token
```

**6. 向用户发送确认消息**（见「验证安装」章节）

---

## 第二步：创建周评分 Bitable

创建一个 Bitable 多维表格，记录每周四维得分，包含以下字段：

| 字段名 | 类型 |
|--------|------|
| 周期 | 文本 |
| 执行力 | 数字 |
| 主动性 | 数字 |
| 稳定性 | 数字 |
| 进化速度 | 数字 |
| 核心改进 | 文本 |
| 周复盘链接 | 超链接 |

创建后从 URL 中获取 `app_token`（`/base/XXX` 中的 `XXX`）和 `table_id`（`?table=YYY` 中的 `YYY`），填入第三步的 config.yml。

---

## 第三步：填写 config.yml

第一步会自动填入两个 token，其余字段手动补充：

```yaml
# 触发时间（修改后需重新注册 cron，且 cron 命令中的 --schedule 必须与此保持一致）
schedule:
  daily: "50 23 * * *"       # 日总结执行时间，默认每天 23:50
  weekly: "10 0 * * 1"       # 周复盘执行时间，默认每周一 00:10

# 飞书存储配置（daily_summary_folder_token / weekly_review_folder_token 由第一步自动填入）
storage:
  backend: feishu
  daily_summary_folder_token: ""   # 第一步自动填入
  weekly_review_folder_token: ""   # 第一步自动填入
  domain: "https://xxx.feishu.cn"  # 你的飞书域名（手动填写）

# 周评分 Bitable（必填）
score_table:
  enabled: true
  app_token: ""   # 第二步创建的 Bitable app_token
  table_id: ""    # 第二步创建的 table_id
```

---

## 第四步：填写 USER.md

在 agent workspace 根目录的 `USER.md` 中填写用户信息，Skill 会从中读取称呼：

```markdown
- **What to call them:** 你的名字/称呼
- **Timezone:** Asia/Shanghai
```

---

## 第五步：注册 cron 任务

在 OpenClaw 中注册两个定时任务（时间以 config.yml 中的 schedule 为准）：

```bash
# --task daily 触发「日总结流程」，--task weekly 触发「周复盘流程」

# 日总结（--schedule 时间需与 config.yml 中 schedule.daily 一致）
openclaw cron add --schedule "50 23 * * *" --skill daily-review-feishu --task daily

# 周复盘（--schedule 时间需与 config.yml 中 schedule.weekly 一致）
openclaw cron add --schedule "10 0 * * 1" --skill daily-review-feishu --task weekly
```

---

## 验证安装

第一步执行完成后，agent 会自动发送以下确认消息，请点击链接确认目录已创建：

```
飞书目录已创建：
- 工作目录：<storage.domain>/drive/folder/<root_folder_token>
- 每日总结：<storage.domain>/drive/folder/<daily_summary_folder_token>
- 每周复盘：<storage.domain>/drive/folder/<weekly_review_folder_token>
```

完成所有步骤后，检查清单：

- [ ] 确认三个飞书目录链接可正常访问（见上方链接）
- [ ] config.yml 中 `storage.domain` 已填写
- [ ] USER.md 中 `What to call them` 已填写
- [ ] cron 任务已注册（`openclaw cron list` 可查看），且 `--schedule` 时间与 config.yml 中 `schedule.*` 一致
- [ ] 周评分 Bitable 已创建，app_token 和 table_id 已填入 config.yml

安装完成，Skill 将在设定时间自动执行。
