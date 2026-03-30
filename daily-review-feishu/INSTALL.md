# INSTALL.md - 安装与初始化指南

本文件描述首次使用 `daily-review-feishu` Skill 前需要完成的环境准备工作。
**安装只需做一次**，完成后正常使用 SKILL.md 即可。

---

## 前置条件

- 已安装 OpenClaw，agent 可正常运行
- 有飞书账号，且有一个用于存放文档的工作目录（任意文件夹即可）
- （可选）如需周评分表，准备一个 Bitable 多维表格

---

## 第一步：在飞书创建目录结构

在你的飞书云文档中，创建以下两个文件夹。推荐使用默认名，也可以自定义：

```
你的工作目录/
├── 每日总结/      ← 默认名，存放每天的日总结文档
└── 每周复盘/      ← 默认名，存放每周的周复盘文档
```

**获取文件夹 token 的方法**：
1. 在飞书网页端打开文件夹
2. 地址栏 URL 格式为：`https://xxx.feishu.cn/drive/folder/XXXXXX`
3. 末尾的 `XXXXXX` 就是该文件夹的 `folder_token`

---

## 第二步：（可选）创建周评分 Bitable

如需启用周评分表（记录每周四维得分），创建一个 Bitable 多维表格，包含以下字段：

| 字段名 | 类型 |
|--------|------|
| 周期 | 文本 |
| 执行力 | 数字 |
| 主动性 | 数字 |
| 稳定性 | 数字 |
| 进化速度 | 数字 |
| 核心改进 | 文本 |
| 周复盘链接 | 超链接 |

创建后从 URL 中获取 `app_token`（`/base/XXX` 中的 `XXX`）和 `table_id`（`?table=YYY` 中的 `YYY`）。

不需要评分表则跳过此步，后续 config.yml 中设置 `score_table.enabled: false` 即可。

---

## 第三步：填写 config.yml

复制以下模板，填入实际值，保存为 `./config.yml`（与 SKILL.md 同目录）：

```yaml
# 触发时间（修改后需重新注册 cron，且 cron 命令中的 --schedule 必须与此保持一致）
schedule:
  daily: "50 23 * * *"       # 日总结执行时间，默认每天 23:50
  weekly: "10 0 * * 1"       # 周复盘执行时间，默认每周一 00:10

# 飞书存储配置
storage:
  backend: feishu
  daily_summary_folder_token: ""   # 第一步创建的「每日总结」文件夹 token
  weekly_review_folder_token: ""   # 第一步创建的「每周复盘」文件夹 token
  domain: "https://xxx.feishu.cn"  # 你的飞书域名

# 周评分 Bitable（不需要则设 enabled: false）
score_table:
  enabled: false
  app_token: ""
  table_id: ""
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
# 日总结（--schedule 时间需与 config.yml 中 schedule.daily 一致）
openclaw cron add --schedule "50 23 * * *" --skill daily-review-feishu --task daily

# 周复盘（--schedule 时间需与 config.yml 中 schedule.weekly 一致）
openclaw cron add --schedule "10 0 * * 1" --skill daily-review-feishu --task weekly
```

---

## 验证安装

完成以上步骤后，检查清单：

- [ ] 飞书「每日总结」文件夹已创建，token 已填入 config.yml
- [ ] 飞书「每周复盘」文件夹已创建，token 已填入 config.yml
- [ ] 飞书域名已填入 config.yml
- [ ] USER.md 中 `What to call them` 已填写
- [ ] cron 任务已注册（`openclaw cron list` 可查看），且 `--schedule` 时间与 config.yml 中 `schedule.*` 一致
- [ ] （可选）周评分 Bitable 已创建，token 已填入 config.yml

安装完成，Skill 将在设定时间自动执行。
