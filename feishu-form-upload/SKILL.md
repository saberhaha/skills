---
name: feishu-form-upload
description: 飞书表单图片上传助手。给定一个飞书表单 URL，自动识别所有需要上传照片的字段，提醒用户发图片，然后帮用户把图片上传到表单对应字段。触发条件：用户提供飞书表单链接并需要上传图片/照片时使用。
---

# 飞书表单图片上传

## 流程

### 1. 打开表单，识别图片字段

```json
{"action": "navigate", "profile": "user", "url": "<表单URL>"}
```

用 `snapshot` 找出所有附件上传区域（含 `input[type=file]` 或「Choose File」按钮），记录字段名和 ref。

告知用户：「表单中有 X 个需要上传图片的字段：[字段名]，请把图片发给我。」

### 2. 收图，复制到上传目录

用户通过飞书发来的图片保存在 `/Users/yzpay/.openclaw/media/inbound/`：

```bash
# 找最新文件
ls -lt /Users/yzpay/.openclaw/media/inbound/ | head -3
# 复制到上传目录
cp /Users/yzpay/.openclaw/media/inbound/<最新文件> /tmp/openclaw/uploads/<字段名>-<YYYYMMDD>.jpg
```

### 3. 上传图片

> ⚠️ **时序关键：先 upload 注入 → 再点按钮**，顺序反了 React 不响应（图片名字显示但实际内容为空）

**第零步：上传前先清空残留**

```json
{
  "kind": "evaluate",
  "fn": "() => { const items = document.querySelectorAll('.bitable-53ec4a__attach-editor__item'); if (items.length === 0) return 'clean'; items.forEach(item => { item.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true})); const delBtn = item.querySelector('.delete-img'); if (delBtn) delBtn.click(); }); return `cleared ${items.length} items`; }"
}
```

如果返回 `clean` 直接跳过，否则再截图确认已清空。

**第一步：先 upload 注入**（还没点按钮）

```json
{
  "action": "upload",
  "profile": "user",
  "selector": "input[type=file]",
  "paths": ["/tmp/openclaw/uploads/<文件名>.jpg"]
}
```

**第二步：再点「Choose File」按钮触发**

```json
{"kind": "click", "ref": "<Choose File 的 ref>"}
```

**第三步：用 JS 确认上传状态（比截图可靠）**

```json
{
  "kind": "evaluate",
  "fn": "() => { const items = document.querySelectorAll('.bitable-53ec4a__attach-editor__item'); const result = []; items.forEach((item, i) => { const img = item.querySelector('img'); const title = item.querySelector('.attach-item-title')?.textContent?.trim(); result.push({ index: i, filename: title, hasImg: !!img, imgSrc: img?.src?.slice(0, 80) }); }); return result; }"
}
```

**判断标准**：
- `filename` 与刚才上传的文件名一致，且 `hasImg: true` → ✅ 上传成功，继续下一步
- `hasImg: false` 或 `filename` 不匹配 → ❌ 上传失败，**立即重试**（见重试机制）
- 有多个 item → ⚠️ 有残留，逐一核对 filename，删掉不匹配的（hover 找 `.delete-img`），再确认

**重试机制**（JS 确认失败时自动触发，最多重试 2 次）：

1. 重新加载表单（`navigate` 到同一 URL，确保全新状态）
2. 重新执行第零步清空残留
3. 重新执行上传流程（先 upload → 再点按钮）
4. 再次 JS 确认状态

2 次重试后仍失败 → 截图告知用户当前状态，说明哪一步卡住了，请用户协助排查。

**额外验证**：上传成功后 JS 验证通过即可，继续提交流程。

### 4. 截图确认，等用户下令

截图展示当前表单完整状态，**不自动提交**，等用户明确说「提交」才执行：

```json
{"kind": "click", "ref": "<提交按钮 ref>"}
```

提交后截图确认成功页面。
