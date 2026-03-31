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
  "url": "https://qima.feishu.cn/share/base/form/shrcnRMkIRAcx9Gbo8jKd05OObe",
  "loadState": "networkidle"
}
```

#### 2. ⚡ 上传打卡照片（Playwright connect_over_cdp 方法）

> ⚠️ **重要**：飞书表单附件组件是 React 受控组件。`browser upload`、`drag/drop` **全部无效**。
> **有效方法（2026-03-31 验证）**：用 Playwright `connect_over_cdp` 连接已有 Chrome，调用 `page.set_input_files()`。
> 安装：`pip3 install playwright`（一次性，已安装则跳过）

执行公共上传脚本：

```bash
python3 ~/.openclaw/scripts/feishu_upload.py \
  /tmp/openclaw/uploads/checkin-YYYYMMDD.jpg \
  shrcnRMkIRAcx9Gbo8jKd05OObe
```

参数说明：
- 参数1：本地图片路径
- 参数2：表单 URL 的唯一片段（用于定位已打开的 Chrome 标签页）

**验证方法（截图目视，不用 JS）**：
- 执行后用 `browser screenshot` 截图
- ✅ 成功：截图中上传区域出现图片**缩略图预览**（1张图）
- ❌ 失败：仍显示「添加本地文件」文字 → 重新 navigate 表单后重试，最多 2 次

> ⚠️ **不要用 JS `hasImg` 验证**：飞书缩略图的类名不固定，JS 选择器容易误判，截图目视最可靠。
> ⚠️ **重试前必须重新 navigate 页面**：不刷新直接重试会导致图片叠加（多张图）。

#### 3. 选择性别与 BASE 地

> **注意**：snapshot ref 不可靠，统一用 snapshot 找到选项文字后用 JS click，提交前截图确认蓝色圆点。

先用 `snapshot` 查看当前表单的选项结构，再根据实际 ref 点击对应选项。
性别（男）和 BASE 地（杭州）都通过 snapshot ref 点击——不要用硬编码索引，因为选项渲染顺序可能随表单结构变化。

点击方式：
```json
{"kind": "click", "ref": "<snapshot 中对应选项的 ref>"}
```

若 ref 点击无效（选中状态未出现蓝色圆点），改用文字匹配的 JS click：
```js
// 性别-男
Array.from(document.querySelectorAll('[class*=select-list] [class*=row], [class*=radio] label'))
  .find(el => el.textContent.trim() === '男')?.click()

// BASE地-杭州
Array.from(document.querySelectorAll('[class*=select-list] [class*=row], [class*=radio] label'))
  .find(el => el.textContent.trim() === '杭州')?.click()
```

#### 4. 填写运动时长

用 snapshot 获取当前数字输入框 ref，再用 `type` 填入**第二步计算出的实际分钟数**：

```json
{"kind": "type", "ref": "<snapshot 中数字输入框的 ref>", "text": "<实际分钟数>"}
```

若 snapshot ref 失效，用 JS 动态注入（注意：`<实际分钟数>` 需在执行前替换为具体数字字符串）：
```js
(function(minutes) {
  const input = document.querySelector('input[type=number]')
               || Array.from(document.querySelectorAll('input')).find(i => i.placeholder && (i.placeholder.includes('分钟') || i.placeholder.includes('时长')));
  if (!input) return 'not found';
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
  setter.call(input, String(minutes));
  input.dispatchEvent(new Event('input', { bubbles: true }));
  return 'ok: ' + input.value;
})(39)  // ← 替换为实际分钟数
```

#### 5. 截图确认所有字段

提交前截图，确认：
- ✅ 性别已选中（蓝色圆点，显示「男」）
- ✅ BASE地已选中（蓝色圆点，显示「杭州」）
- ✅ 运动时长已填写（显示实际分钟数）
- ✅ 照片已上传（缩略图可见，仅1张）

#### 6. 提交表单

用 JS evaluate 点击，不依赖硬编码 ref：

```json
{
  "kind": "evaluate",
  "fn": "() => { const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '提交'); if (btn) { btn.click(); return 'clicked'; } return 'not found'; }"
}
```

#### 7. 确认提交成功

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

### 图片上传（已解决，2026-03-31）
- **根本原因**：飞书表单附件组件是 React 受控组件
- **无效方法**（不要重复尝试）：`browser upload`、`DOM.setFileInputFiles`、`dispatch change event`、`drag/drop DragEvent`
- **有效方法**：Playwright `connect_over_cdp` + `page.set_input_files()`，见第七步脚本
- **验证标准**：截图目视看到图片缩略图（不用 JS hasImg，类名不稳定易误判）
- **多图问题根因**：重试前未刷新页面，导致图片叠加 → **重试前必须重新 navigate**

### 选项点击无效
- **原因**：飞书表单的单选框用自定义 React 组件，普通 ref 点击可能不触发状态更新
- **解决方案**：用文字匹配的 JS click，例如 `Array.from(document.querySelectorAll('[class*=select-list] [class*=row]')).find(el => el.textContent.trim() === '男')?.click()`
- **验证**：提交前截图确认蓝色圆点出现

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
