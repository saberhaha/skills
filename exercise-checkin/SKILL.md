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

#### 2. ⚡ 上传打卡照片（CDP FileChooser 方法）

> ⚠️ **重要**：飞书表单附件组件是 React 受控组件。`browser upload`、`setInputFiles`、`dispatch event`、`drag/drop` **全部无效**。
> 唯一有效方法：CDP `Page.setInterceptFileChooserDialog` + 真实鼠标事件 + `DOM.setFileInputFiles(backendNodeId)`。

将以下脚本保存为 `/tmp/feishu_upload.py`，替换 `PAGE_ID` 和 `FILE_PATH` 后执行：

```python
#!/usr/bin/env python3
import socket, base64, struct, json, time

HOST = '127.0.0.1'
PORT = 9222
PAGE_ID = '<browser open/navigate 返回的 targetId>'
FILE_PATH = '/tmp/openclaw/uploads/checkin-YYYYMMDD.jpg'

def ws_frame(data, opcode=1):
    data = data if isinstance(data, bytes) else data.encode()
    length = len(data)
    mask = b'\x01\x02\x03\x04'
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    if length < 126: header = bytes([0x80|opcode, 0x80|length]) + mask
    elif length < 65536: header = bytes([0x80|opcode, 0x80|126]) + struct.pack('>H',length) + mask
    else: header = bytes([0x80|opcode, 0x80|127]) + struct.pack('>Q',length) + mask
    return header + masked

def ws_recv(s, timeout=3):
    frames = []; s.settimeout(timeout)
    while True:
        try:
            h = b''
            while len(h)<2: c=s.recv(2-len(h)); h+=c if c else b'\x00'
            if len(h)<2: break
            l = h[1]&0x7f
            if l==126: e=b''; [e:=e+s.recv(2-len(e)) for _ in range(10) if len(e)<2]; l=struct.unpack('>H',e)[0]
            elif l==127: e=b''; [e:=e+s.recv(8-len(e)) for _ in range(10) if len(e)<8]; l=struct.unpack('>Q',e)[0]
            d=b''
            while len(d)<l: c=s.recv(min(8192,l-len(d))); d+=c if c else b''
            try: frames.append(json.loads(d.decode()))
            except: pass
        except socket.timeout: break
    return frames

def send(s, i, m, p=None): s.send(ws_frame(json.dumps({"id":i,"method":m,"params":p or {}})))
def wait(s, i, t=5):
    st=time.time()
    while time.time()-st<t:
        for f in ws_recv(s,1):
            if f.get('id')==i: return f
    return None

key = base64.b64encode(b'checkin_upload_1').decode()
s = socket.socket(); s.connect((HOST, PORT))
hs = f"GET /devtools/page/{PAGE_ID} HTTP/1.1\r\nHost:{HOST}:{PORT}\r\nUpgrade:websocket\r\nConnection:Upgrade\r\nSec-WebSocket-Key:{key}\r\nSec-WebSocket-Version:13\r\n\r\n"
s.send(hs.encode()); s.settimeout(3)
buf=b''
while b'\r\n\r\n' not in buf: buf+=s.recv(1024)

# 1. 启用 Page + 拦截 fileChooser
send(s,1,'Page.enable'); time.sleep(0.2); ws_recv(s)
send(s,2,'Page.setInterceptFileChooserDialog',{'enabled':True}); wait(s,2,3)

# 2. 获取上传区域坐标
send(s,3,'Runtime.evaluate',{'expression':'''(function(){
    var el=document.querySelector('.attach-editor-upload,[class*=attach-editor-upload],.attache-upload-text');
    if(!el) el=Array.from(document.querySelectorAll('[class*=attach] *')).find(e=>e.textContent.trim()==='添加本地文件'&&!e.querySelector('*'));
    if(!el) return null;
    var r=el.getBoundingClientRect();
    return {x:r.left+r.width/2,y:r.top+r.height/2};
})()''','returnByValue':True})
r=wait(s,3,3); coords=r.get('result',{}).get('result',{}).get('value') if r else None
if not coords: print('ERROR:找不到上传区域'); s.close(); exit(1)
x,y=int(coords['x']),int(coords['y'])

# 3. 真实鼠标点击（触发 fileChooser）
for ev in ['mouseMoved','mousePressed','mouseReleased']:
    send(s,40,'Input.dispatchMouseEvent',{'type':ev,'x':x,'y':y,'button':'left','clickCount':1,'modifiers':0})
    time.sleep(0.05); ws_recv(s,0.2)

# 4. 等待 fileChooserOpened 事件
backend_node_id=None; st=time.time()
while time.time()-st<3:
    for f in ws_recv(s,0.5):
        if f.get('method')=='Page.fileChooserOpened':
            backend_node_id=f.get('params',{}).get('backendNodeId'); break
    if backend_node_id: break
if not backend_node_id: print('ERROR:fileChooserOpened未触发'); s.close(); exit(1)

# 5. 用 backendNodeId 写入文件（绕过 React）
send(s,5,'DOM.setFileInputFiles',{'backendNodeId':backend_node_id,'files':[FILE_PATH]}); wait(s,5,5)

# 6. 验证
time.sleep(3)
send(s,6,'Runtime.evaluate',{'expression':'''(function(){
    var items=document.querySelectorAll('[class*="attach"][class*="item"]');
    return {count:items.length,hasImg:items.length>0?!!items[0].querySelector('img'):false};
})()''','returnByValue':True})
r=wait(s,6,5); result=r.get('result',{}).get('result',{}).get('value') if r else None
print(f'上传结果:{result}')
# hasImg:true = 成功，false = 失败需重试
s.close()
```

执行：
```bash
python3 /tmp/feishu_upload.py
```

**验证标准**：
- 输出 `hasImg: true` → ✅ 上传成功，继续填其他字段
- 输出 `hasImg: false` → ❌ 失败，重新 navigate 表单后重试，最多 2 次

**截图确认（脚本成功后）**：

```json
{"action": "screenshot", "profile": "user", "targetId": "<PAGE_ID>"}
```

确认附件区域显示图片缩略图。

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

### 图片上传（已解决，2026-03-31）
- **根本原因**：飞书表单附件组件是 React 受控组件，所有外部写 `input.files` 的方法都被 React 拦截
- **无效方法**（不要重复尝试）：`browser upload`、`DOM.setFileInputFiles(nodeId)`、`dispatch change event`、`drag/drop DragEvent`
- **有效方法**：CDP `Page.setInterceptFileChooserDialog` + `Input.dispatchMouseEvent` + `DOM.setFileInputFiles(backendNodeId)`，见第七步脚本
- **验证标准**：截图看到图片缩略图 + `hasImg: true`

### 选项点击无效
- **原因**：飞书表单的单选框用自定义 React 组件，普通 ref 点击可能不触发状态更新
- **解决方案**：用 JS evaluate + `querySelectorAll('.base-component-select-list-editor-row')[index].click()`
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
