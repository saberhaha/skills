---
name: daily-news
description: 每日早上8点推送资讯简报。抓取百度热搜 + Tavily 搜索，整理成6大分类发送到飞书，并写入飞书文档存档。
---

# 每日资讯简报

## 触发
每天 08:00（cron: `0 8 * * *`）

## 执行流程

### 第一步：获取今日日期
用 `session_status` 获取当前日期，格式：`YYYY年MM月DD日`

### 第二步：抓取百度实时热搜
用 `browser`（profile="user"）打开 `https://top.baidu.com/board?tab=realtime`，执行：
```json
{"kind": "evaluate", "fn": "() => { const items = document.querySelectorAll('.content_1YWBm'); return [...items].slice(0,15).map(el => el.querySelector('.c-single-text-ellipsis')?.textContent?.trim()).filter(Boolean); }"}
```
过滤规则：只保留 社会/财经/科技/政治/军事 类，去掉娱乐八卦、体育赛事、明星八卦。

### 第三步：Tavily 搜索6类资讯

使用环境变量 `TAVILY_API_KEY`，路径：`~/.openclaw/skills/tavily-search/scripts/search.mjs`

```bash
# 国际 AI
node ~/.openclaw/skills/tavily-search/scripts/search.mjs "OpenAI Anthropic Claude Google Meta AI news" --topic news -n 5

# 军事政治
node ~/.openclaw/skills/tavily-search/scripts/search.mjs "military war Iran Russia Middle East China US Taiwan politics" --topic news -n 5

# 经济财报
node ~/.openclaw/skills/tavily-search/scripts/search.mjs "US stock market Tesla Google Apple earnings oil gold economy" --topic news -n 5

# 国内 AI
node ~/.openclaw/skills/tavily-search/scripts/search.mjs "中国 AI 人工智能 大模型 字节 阿里 华为 百度 政策" --topic news -n 5

# A股
node ~/.openclaw/skills/tavily-search/scripts/search.mjs "A股 人工智能 科技股 行情" --topic news -n 4

# 国内热点补充（如热搜内容不足）
node ~/.openclaw/skills/tavily-search/scripts/search.mjs "中国 今日 热点 社会 财经" --topic news -n 3
```

### 第四步：整理成简报并发送飞书消息

格式模板：
```
📰 **每日简报 · YYYY年MM月DD日**

---

🔥 **今日热点**（百度实时热搜）

**1. 热点标题**
一句话描述。

**2. 热点标题** - [来源](url)
一句话描述。

...

---

🌍 **国际动态**

🤖 **AI 资讯**

**1. 标题** - [来源](url)
一句话摘要。

...

⚔️ **军事政治**
...

💵 **经济财报**
...

---

🇨🇳 **国内动态**

🤖 **AI 资讯**
...

📈 **A 股要闻**
...
```

每分类 3-4 条，全文控制在 20 条以内。

发送：
```
message(action="send", channel="feishu", to="ou_fd3df39b5a00787f454fe0a856059bdb", message=简报内容)
```

### 第五步：写入飞书文档存档

1. 在「AI 助手文档库」下找或创建「每日简报」文件夹（folder_token: `CnIFfuRPmlifEydSzhMcVRUwnkh`）
2. 创建文档，标题：`YYYY年MM月DD日-每日简报`
3. 将完整简报内容写入文档

```
feishu_doc(action="create", title="YYYY年MM月DD日-每日简报", folder_token="CnIFfuRPmlifEydSzhMcVRUwnkh")
feishu_doc(action="write", doc_token=xxx, content=简报内容)
```

## 注意事项
- 热点过滤：娱乐/体育/明星相关一律不要，聚焦社会/财经/科技/政治
- 来源链接：标题后跟 ` - [来源](url)`，不要把链接放在加粗标题内部
- 摘要要精炼：每条不超过50字，说清楚"发生了什么、为什么重要"
- TAVILY_API_KEY：`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`
