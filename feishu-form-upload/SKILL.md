---
name: feishu-form-upload
description: 飞书表单图片上传助手。给定一个飞书表单 URL，自动识别所有需要上传照片的字段，提醒用户发图片，然后帮用户把图片上传到表单对应字段。触发条件：用户提供飞书表单链接并需要上传图片/照片时使用。
---

# 飞书表单图片上传

## 核心原理（必读）

飞书 Bitable 表单的附件组件是 React 受控组件。

**有效方法（2026-03-31 验证）**：用 Playwright `connect_over_cdp` 连接已有 Chrome，调用 `page.set_input_files()`。

> **为什么 CDP 原始方法不够**：`DOM.setFileInputFiles(backendNodeId)` 可以触发 fileChooserOpened 事件，但 React 的 `input.files` 属性仍为 0，上传无效。Playwright 封装的 `set_input_files` 内部有额外处理，才是真正有效的。

---

## 流程

### 1. 打开表单，识别图片字段

```json
{"action": "navigate", "profile": "user", "url": "<表单URL>", "loadState": "networkidle"}
```

用 `snapshot` 找出所有附件上传区域（含 `input[type=file]` 或「Choose File」按钮），记录字段名。

告知用户：「表单中有 X 个需要上传图片的字段：[字段名]，请把图片发给我。」

### 2. 收图，复制到上传目录

用户通过飞书发来的图片保存在 `/Users/yzpay/.openclaw/media/inbound/`：

```bash
mkdir -p /tmp/openclaw/uploads
cp /Users/yzpay/.openclaw/media/inbound/<最新文件> /tmp/openclaw/uploads/<字段名>-<YYYYMMDD>.jpg
```

### 3. 上传图片（Playwright connect_over_cdp 方法）

**安装 Playwright**（一次性，已安装跳过）：
```bash
pip3 install playwright
```

执行公共上传脚本：

```bash
python3 ~/.openclaw/skills/feishu-form-upload/scripts/upload.py \
  /tmp/openclaw/uploads/<字段名>-<YYYYMMDD>.jpg \
  <表单URL的唯一片段>
```

参数说明：
- 参数1：本地图片路径
- 参数2：表单 URL 的唯一片段（用于定位已打开的 Chrome 标签页）

**验证方法（截图目视，不要用 JS hasImg）**：
- 执行后用 `browser screenshot` 截图
- ✅ 成功：上传区域出现**图片缩略图预览**（1张图）
- ❌ 失败：仍显示「添加本地文件」文字 → 重新 navigate 表单后重试，最多 2 次

> ⚠️ **重试前必须重新 navigate 页面**：不刷新直接重试会导致图片叠加（多张图）。

### 4. 截图确认，等用户下令

截图展示当前表单完整状态，**不自动提交**，等用户明确说「提交」才执行。

提交用 JS evaluate，不依赖硬编码 ref：

```json
{
  "kind": "evaluate",
  "fn": "() => { const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '提交'); if (btn) { btn.click(); return 'clicked'; } return 'not found'; }"
}
```

提交后截图确认成功页面。

---

## ⚠️ 已知无效方法（不要再用）

以下方法在飞书 Bitable 表单上**全部无效**，不要重复尝试：

- `browser upload action`（直接 Playwright upload）→ React 拦截
- `DOM.setFileInputFiles(backendNodeId)` → 可触发 fileChooserOpened，但 React `files` 属性仍为 0
- `dispatch change/input event` → React 不响应合成事件的 files 变化
- `drag/drop DragEvent` → `isTrusted=false` 被飞书检测并忽略
- `fetch/XHR 直接调上传 API` → 需要 CSRF token + 登录态
