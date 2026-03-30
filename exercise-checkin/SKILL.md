---
name: exercise-checkin
description: 运动打卡技能。当用户说"打卡"并上传运动照片时，自动解析图片获取运动数据并验证，然后自动填写飞书表单完成提交。触发条件：用户发送"打卡"并附上运动截图（如华为运动健康、悦跑圈等APP的骑行/跑步/健走等运动记录截图）。

---

# 运动打卡技能

## 打卡表单地址

https://qima.feishu.cn/share/base/form/shrcnRMkIRAcx9Gbo8jKd05OObe

## 工作流程

严格按照以下顺序执行：

### 第一步：解析图片

使用 `image` 工具分析用户发送的运动截图，提取以下3个信息：
- **总距离**（公里，如有）
- **运动时间**（格式如 "03:48:41" 表示3小时48分41秒）
- **日期**（格式如 "2026年3月25日" 或 "2026-03-25"）

### 第二步：时间转换

将获取的运动时间转换为**分钟**（取整数）：

```
总分钟数 = 小时 × 60 + 分钟 + 秒/60
```

转换后，如果总分钟数 **大于90**，则按 **90** 计算。

### 第三步：内容约束验证

必须同时满足以下两个条件，缺一不可：

1. **运动时间**：总分钟数必须在 **30到90之间**（包含30和90）
   - 公式：30 ≤ 分钟数 ≤ 90

2. **日期**：必须是**今天**（用 session_status 获取当前日期）
   - 与图片中的日期对比，必须完全一致

**验证失败**：直接告知用户原因，不继续执行后续步骤。

### 第四步：询问用户信息（如未知）

如果 MEMORY.md 或 USER.md 中没有记录以下信息，询问用户：

- **性别**：男 / 女
- **BASE地**：杭州 / 北京 / 广州 / 深圳 / 上海 / 成都 / 其他

记住后写入 `memory/YYYY-MM-DD.md`，下次打卡直接复用。

### 第五步：确认打卡照片

**重要**：打卡照片必须同时包含：
1. 运动时长/数据截图（APP记录）
2. 本人运动过程照片

如果用户只发了一张纯数据截图（无本人），必须要求用户补发包含本人的合图或第二张照片。  
**绝对不能用纯数据截图提交打卡！**

### 第六步：保存图片到本地

用户通过飞书发来的图片已保存在 `/Users/yzpay/.openclaw/media/inbound/` 目录，找到**最新的、包含本人的**图片文件，复制到上传目录：

```bash
cp /Users/yzpay/.openclaw/media/inbound/<最新文件> /tmp/openclaw/uploads/checkin-YYYYMMDD.jpg
```

### 第七步：用浏览器填写并提交表单

使用 `browser` 工具（profile="user"）打开打卡表单，**严格按以下顺序**操作：

#### 1. 打开表单（每次必须重新打开，确保是全新未提交状态）

```json
{
  "action": "navigate",
  "profile": "user",
  "url": "https://qima.feishu.cn/share/base/form/shrcnRMkIRAcx9Gbo8jKd05OObe"
}
```

#### 2. ⚡ 上传打卡照片（优先第一步，时序关键）

> ⚠️ **时序关键：先 upload 注入 → 再点按钮**，顺序反了 React 不响应（图片名字显示但实际内容为空）

**第零步：上传前先清空残留**

```json
{"kind": "evaluate", "fn": "() => { const items = document.querySelectorAll('.bitable-53ec4a__attach-editor__item'); if (items.length === 0) return 'clean'; items.forEach(item => { item.dispatchEvent(new MouseEvent('mouseenter', {bubbles: true})); const delBtn = item.querySelector('.delete-img'); if (delBtn) delBtn.click(); }); return `cleared ${items.length} items`; }"}
```

返回 `clean` 直接跳过，否则截图确认已清空。

**第一步：先 upload 注入**（还没点按钮）

```json
{"action": "upload", "profile": "user", "selector": "input[type=file]", "paths": ["/tmp/openclaw/uploads/checkin-YYYYMMDD.jpg"]}
```

**第二步：再点「Choose File」按钮触发**

```json
{"kind": "click", "ref": "<snapshot 中 Choose File 的 ref>"}
```

**第三步：JS 确认上传状态**

```json
{"kind": "evaluate", "fn": "() => { const items = document.querySelectorAll('.bitable-53ec4a__attach-editor__item'); const result = []; items.forEach((item, i) => { const img = item.querySelector('img'); const title = item.querySelector('.attach-item-title')?.textContent?.trim(); result.push({ index: i, filename: title, hasImg: !!img, imgSrc: img?.src?.slice(0, 80) }); }); return result; }"}
```

**判断标准**：
- `filename` 与上传文件名一致，且 `hasImg: true` → ✅ 上传成功，继续填其他字段
- `hasImg: false` 或 `filename` 不匹配 → ❌ 上传失败，**立即重试**（见重试机制）
- 有多个 item → 逐一核对 filename，删掉不匹配的（hover 找 `.delete-img`），再确认

**重试机制**（最多 2 次）：
1. `navigate` 重新加载表单（全新状态）
2. 重新执行第零步清空
3. 重新执行第一、二步上传
4. 再次执行第三步 JS 确认
2 次后仍失败 → 截图告知用户卡在哪一步，请协助排查

**第四步：确认通过，直接继续填写其他字段**

JS 验证通过即可，无需截图让用户确认。

#### 3. 选择性别

用坐标点击（JS MouseEvent）更可靠：
```json
{
  "kind": "evaluate",
  "fn": "() => { const rows = document.querySelectorAll('.base-component-select-list-editor-row'); rows[0].click(); }"
}
```
或直接用 ref 点击对应选项。

#### 4. 选择 BASE地

```json
{
  "kind": "evaluate", 
  "fn": "() => { const rows = document.querySelectorAll('.base-component-select-list-editor-row'); rows[2].click(); }"
}
```
（rows[0]=男, rows[1]=女, rows[2]=杭州, rows[3]=北京...）

> **注意**：snapshot 里的 ref 点击可能无选中效果，用坐标或 JS click 更可靠。提交前截图确认选中状态（蓝色圆点）。

#### 5. 填写运动时长

```json
{"kind": "type", "ref": "e186", "text": "67"}
```

#### 6. 截图确认所有字段

提交前截图，确认：
- ✅ 性别已选中（蓝色圆点）
- ✅ BASE地已选中（蓝色圆点）  
- ✅ 运动时长已填写
- ✅ 照片已上传（有文件名显示）

#### 7. 提交表单

```json
{"kind": "click", "ref": "e225"}
```

#### 8. 确认提交成功

截图确认页面出现「滴！健身卡」字样。

### 第八步：返回打卡结果

```
✅ 打卡成功！
📅 日期：{日期}
🏃 运动时间：{分钟}分钟
📍 总距离：{距离}公里（如有）
📋 表单已提交
```

---

## ⚠️ 已知问题与解决方案

### 图片上传失败（React 状态不更新）
- **根本原因**：飞书表单用 React 自定义附件组件，Playwright `upload` 只能写入 `input.files`，但不触发 React 的 onChange 事件，导致**文件名显示但内容实际为空**，提交后附件是空的
- **判断方法**：JS 查询有 `hasImg: true` 才算成功；只有文字文件名 = 失败
- **解决方案**：重新加载表单，清空残留后重试（最多2次）

### 选项点击无效
- **原因**：飞书表单的单选框用自定义 React 组件，普通 ref 点击可能不触发状态更新
- **解决方案**：用 JS evaluate + `querySelectorAll('.base-component-select-list-editor-row')[index].click()`
- **验证**：用坐标精确点击，提交前截图确认蓝色圆点出现

### 提交后无法编辑附件
- **原因**：飞书表单提交后附件字段只读，无法通过程序替换
- **解决方案**：删除整条记录，重新提交正确记录

---

## 注意事项

- 支持的运动APP截图：华为运动健康、悦跑圈、Keep、咕咚、Nike Run Club 等
- 运动类型：骑行、跑步、健走等均可
- 图片无法识别或信息不完整时，要求用户重新上传
- 每次打卡前确认日期是今天，避免补打卡
- **打卡照片必须有本人 + 运动数据，缺一不可**
