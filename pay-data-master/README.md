# Pay Super Brain

> 在 AI 时代，拥抱 AI，让智能成为我们的超能力。

## 愿景

这是有赞支付团队沉淀 AI 实践成果的技能仓库。

我们相信，AI 不是替代者，而是协作者。每一次与 AI 的对话，都是一次思维的碰撞；每一个沉淀下来的技能，都是一次经验的结晶。

在这里，我们：
- **沉淀** — 将经验转化为可复用的技能
- **共享** — 让知识流动，让智慧传递
- **进化** — 与 AI 共同成长，持续迭代

## 目录结构

```
pay-super-brain/
├── skills/                    # 技能存放目录
│   └── skill-name/           # 技能文件夹
│       ├── SKILL.md          # 技能描述文件（必需）
│       ├── scripts/          # 可执行脚本（可选）
│       ├── references/       # 参考文档（可选）
│       └── assets/           # 资源文件（可选）
├── install_skill.sh           # 技能安装脚本
└── README.md
```

### 目录说明

| 目录 | 用途 | 示例 |
|------|------|------|
| `scripts/` | 可执行脚本，用于需要确定性执行的任务 | `scripts/validate.sh`、`scripts/parse.py` |
| `references/` | 参考文档，按需加载到上下文 | `references/schema.md`、`references/api-docs.md` |
| `assets/` | 输出资源文件，用于生成最终产物 | `assets/template.html`、`assets/logo.png` |

## 如何提交 Skill

### 1. 创建 Skill 目录

```bash
mkdir -p skills/my-awesome-skill/{scripts,references,assets}
```

### 2. 编写 SKILL.md

每个技能必须包含 `SKILL.md` 文件：

```markdown
---
name: my-awesome-skill
description: This skill should be used when the user asks to "触发词1", "触发词2", "触发词3". 详细描述技能用途。
---

# 技能名称

## 功能概述

简要描述技能的核心功能和适用场景。

## 使用方式

描述如何使用这个技能：
- 触发条件
- 执行步骤
- 注意事项

## 资源文件

### Scripts
- `scripts/validate.sh` - 验证脚本说明

### References
- `references/schema.md` - Schema 文档说明

### Assets
- `assets/template.html` - 模板文件说明

## 示例

提供具体的使用示例。
```

### 3. SKILL.md 编写规范

**Frontmatter 元数据：**

```yaml
---
name: skill-name              # 必需：技能名称
description: This skill should be used when the user asks to "触发词1", "触发词2".  # 必需：第三人称描述
---
```

**编写风格：**
- 使用**祈使语气**（动词开头），不要用第二人称
- ✅ 正确：`创建配置文件并添加以下内容`
- ❌ 错误：`你应该创建配置文件`

**Description 规范：**
- 使用**第三人称**：`This skill should be used when...`
- 包含**具体触发词**：用户会说的具体短语
- ❌ 错误：`用于处理支付`（太模糊）
- ✅ 正确：`This skill should be used when the user asks to "查询支付流水", "分析退款原因", "排查支付失败"`

### 4. Skill 命名规范

- 使用小写字母和连字符：`my-skill-name`
- 语义化命名，能体现技能用途
- 建议格式：`{业务域}-{功能}` 如 `payment-refund-analyzer`

### 5. 提交代码

```bash
# 添加文件
git add skills/my-awesome-skill/

# 提交
git commit -m "feat: 添加 my-awesome-skill 技能"

# 推送
git push origin master
```

## 如何安装 Skill

### 使用安装脚本

安装脚本会自动检测你本地已安装的 IDE，并将技能安装到对应的目录。

**支持的 IDE：**
- Windsurf
- Cursor
- Claude Code
- Trae
- Codex
- Antigravity

**安装方式：**

```bash
# 查看可用的 skills
./install_skill.sh

# 安装指定技能
./install_skill.sh skill-name
```

脚本会自动：
1. 检测本地已安装的 IDE
2. 将技能复制到对应 IDE 的 skills 目录
3. 如已存在则覆盖安装

## Skill 编写最佳实践

### 渐进式加载原则

Skill 采用三级加载机制，合理分配内容：

| 级别 | 内容 | 加载时机 | 建议字数 |
|------|------|----------|----------|
| 元数据 | name + description | 始终加载 | ~100 词 |
| SKILL.md 主体 | 核心流程和概念 | Skill 触发时 | 1,500-2,000 词 |
| 资源文件 | 详细文档、脚本、资源 | 按需加载 | 无限制 |

**内容分配建议：**
- `SKILL.md`：核心概念、主要流程、快速参考
- `references/`：详细文档、API 说明、高级用法
- `scripts/`：可重复执行的脚本
- `assets/`：模板、图片等输出资源

### DO ✅

- **单一职责**：每个 Skill 只做一件事
- **触发词具体**：description 包含用户会说的具体短语
- **保持精简**：SKILL.md 控制在 1,500-2,000 词
- **渐进式加载**：详细内容放 references/
- **引用资源**：在 SKILL.md 中说明各资源文件用途

### DON'T ❌

- **避免模糊描述**：`description: 提供支付帮助` ❌
- **避免内容臃肿**：SKILL.md 超过 3,000 词 ❌
- **避免第二人称**：`你应该...` ❌
- **避免敏感信息**：不要硬编码密钥、密码 ❌

## 常见问题

**Q: scripts/、references/、assets/ 有什么区别？**

A:
- `scripts/`：可执行脚本，用于确定性任务（如验证、解析）
- `references/`：参考文档，按需加载到上下文（如 Schema、API 文档）
- `assets/`：资源文件，用于生成输出（如模板、图片）

**Q: SKILL.md 应该写多长？**

A: 建议控制在 1,500-2,000 词。详细内容移到 `references/` 目录。

**Q: description 怎么写才容易被触发？**

A: 使用第三人称，包含用户会说的具体触发词：
```yaml
description: This skill should be used when the user asks to "查询支付", "分析退款", "排查交易失败"
```

**Q: 如何更新已安装的 Skill？**

A: 重新执行安装脚本即可覆盖安装。

## 贡献者

感谢所有为 Pay Super Brain 贡献技能的小伙伴们！

---

## 许可证

本仓库仅供有赞内部使用。未经授权，严禁将本仓库内容复制、分发或披露给有赞以外的任何第三方。

---

*让 AI 成为我们的第二大脑，让技能成为我们的超能力。*
