---
name: skill-vetter
description: Security-first skill vetting for AI agents. Use before installing any skill from ClawHub, GitHub, or other sources. Checks for red flags, permission scope, and suspicious patterns. Use when asked to install, evaluate, or review any agent skill.
---

# Skill Vetter 🔒

Security-first vetting protocol for AI agent skills. Never install a skill without vetting it first.

## When to Use
- Before installing any skill from ClawHub
- Before running skills from GitHub repos
- When evaluating skills shared by other agents
- Anytime you're asked to install unknown code

## Vetting Protocol

### Step 1: Source Check
Questions to answer:
- [ ] Where did this skill come from?
- [ ] Is the author known/reputable?
- [ ] How many downloads/stars does it have?
- [ ] When was it last updated?
- [ ] Are there reviews from other agents?

### Step 2: Code Review (MANDATORY)

Read ALL files in the skill. Check for these RED FLAGS:

🚨 REJECT IMMEDIATELY IF YOU SEE:
─────────────────────────────────────────
• curl/wget to unknown URLs
• Sends data to external servers
• Requests credentials/tokens/API keys
• Reads ~/.ssh, ~/.aws, ~/.config without clear reason
• Accesses MEMORY.md, USER.md, SOUL.md, IDENTITY.md
• Uses base64 decode on anything
• Uses eval() or exec() with external input
• Modifies system files outside workspace
• Installs packages without listing them
• Network calls to IPs instead of domains
• Obfuscated code (compressed, encoded, minified)
• Requests elevated/sudo permissions
• Accesses browser cookies/sessions
• Touches credential files
─────────────────────────────────────────

### Step 3: Permission Scope
Evaluate:
- [ ] What files does it need to read?
- [ ] What files does it need to write?
- [ ] What commands does it run?
- [ ] Does it need network access? To where?
- [ ] Is the scope minimal for its stated purpose?

### Step 4: Risk Classification

| Risk Level | Examples | Action |
|-----------|----------|--------|
| 🟢 LOW | Notes, weather, formatting | Basic review, install OK |
| 🟡 MEDIUM | File ops, browser, APIs | Full code review required |
| 🔴 HIGH | Credentials, trading, system | Human approval required |
| ⛔ EXTREME | Security configs, root access | Do NOT install |

## Output Format

After vetting, produce this report:

```
SKILL VETTING REPORT
═══════════════════════════════════════
Skill: [name]
Source: [ClawHub / GitHub / other]
Author: [username]
Version: [version]
Downloads: [count] | Stars: [count]

RISK LEVEL: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ EXTREME

RED FLAGS FOUND: None / [list issues]

PERMISSION SCOPE:
- Reads: [files/dirs]
- Writes: [files/dirs]
- Executes: [commands]
- Network: [domains/none]

RECOMMENDATION: ✅ INSTALL / ⚠️ REVIEW FIRST / ❌ REJECT

NOTES: [any additional context]
═══════════════════════════════════════
```

## Quick Vetting (Low-Risk Skills)

For simple instruction-only skills with no scripts:
1. Check author reputation and download count
2. Scan description for suspicious scope
3. Confirm no bundled scripts or external calls
4. Install if all clear

## Remember

- A skill that looks useful can still be malicious
- Popular skills can be compromised after initial publish
- When in doubt, reject and find an alternative
- Always prefer skills with high download counts and security scan badges
