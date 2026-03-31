---
name: git-ai-ratio
description: 统计 GitHub 仓库中 AI 生成代码与人工代码的占比。当用户说"统计 AI 代码占比"、"分析团队 AI 使用情况"、"GitHub AI 代码比例"时触发。输出每人每月的 AI 代码占比和团队整体趋势。
---

# Git AI Ratio — AI 代码占比分析

## 工作流程

### 第一步：收集配置

询问用户：
1. **GitHub Personal Access Token**（需要 `repo` read 权限）
2. **GitHub Organization 名称**（如 `yourcompany`）
3. **要扫描的 repo**：全 org 所有 repo，还是指定列表
4. **统计时间范围**：默认最近1个月（YYYY-MM-DD 格式）
5. **主要编程语言**：用于设置文件过滤规则
6. **大模型 API Key**（Claude 或 OpenAI，用于打分）

配置收齐后执行脚本，不要分批询问。

### 第二步：执行分析脚本

```bash
python3 ~/.openclaw/skills/git-ai-ratio/scripts/analyze.py \
  --token <GITHUB_TOKEN> \
  --org <ORG_NAME> \
  --since <YYYY-MM-DD> \
  --until <YYYY-MM-DD> \
  --api-key <LLM_API_KEY> \
  [--repos repo1,repo2]  # 可选，不传则扫全 org
```

### 第三步：解读结果

脚本输出 CSV 和控制台摘要，格式见 `references/output-format.md`。

向用户汇报：
- 团队整体 AI 占比
- 各成员占比排名
- 月度趋势（如有多月数据）
- 高置信度 commit 样本

---

## 注意事项

- **占比是估算值**，非精确数字——AI 审查修改过的代码无法区分
- **过滤自动生成文件**：lock 文件、proto、generated 等不参与统计
- **采样策略**：每人每月超过 50 个 commit 时随机采样 50 个，控制成本
- **成本参考**：20人/月约 $0.5-2（Claude Haiku）
