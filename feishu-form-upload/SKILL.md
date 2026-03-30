---
name: feishu-form-upload
description: 飞书表单图片上传助手。给定一个飞书表单 URL，自动识别所有需要上传照片的字段，提醒用户发图片，然后帮用户把图片上传到表单对应字段。触发条件：用户提供飞书表单链接并需要上传图片/照片时使用。
---

# 飞书表单图片上传

## 核心原理（必读）

飞书 Bitable 表单的附件组件是 React 受控组件，**Playwright `upload` / `setInputFiles` / 直接写 `input.files` 全部无效**，因为 React 拦截了底层 DOM 操作。

**唯一有效的方法（2026-03-31 验证）**：

1. 用 CDP `Page.setInterceptFileChooserDialog(true)` 提前拦截文件选择器
2. 用 CDP `Input.dispatchMouseEvent` 向上传区域发送真实鼠标点击
3. Chrome 触发 `fileChooserOpened` 事件，CDP 拦截并获取 `backendNodeId`
4. 用 `DOM.setFileInputFiles(backendNodeId, files)` 写入文件

这套流程走的是 Chrome 内核路径（`backendNodeId` 是 Chrome 内部节点 ID，不经过 React），React 无法拦截。

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

### 3. 上传图片（CDP FileChooser 方法）

**完整 Python 脚本**（每次上传调用一次，替换 `FILE_PATH` 和 `PAGE_ID`）：

```python
#!/usr/bin/env python3
import socket, base64, struct, json, time

HOST = '127.0.0.1'
PORT = 9222
PAGE_ID = '<从 browser open/navigate 返回的 targetId>'
FILE_PATH = '/tmp/openclaw/uploads/<文件名>.jpg'

def ws_frame(data, opcode=1):
    data = data if isinstance(data, bytes) else data.encode()
    length = len(data)
    mask = b'\x01\x02\x03\x04'
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    if length < 126:
        header = bytes([0x80 | opcode, 0x80 | length]) + mask
    elif length < 65536:
        header = bytes([0x80 | opcode, 0x80 | 126]) + struct.pack('>H', length) + mask
    else:
        header = bytes([0x80 | opcode, 0x80 | 127]) + struct.pack('>Q', length) + mask
    return header + masked

def ws_recv(s, timeout=3):
    frames = []
    s.settimeout(timeout)
    while True:
        try:
            header = b''
            while len(header) < 2:
                c = s.recv(2 - len(header))
                if not c: break
                header += c
            if len(header) < 2: break
            length = header[1] & 0x7f
            if length == 126:
                ext = b''
                while len(ext) < 2: ext += s.recv(2 - len(ext))
                length = struct.unpack('>H', ext)[0]
            elif length == 127:
                ext = b''
                while len(ext) < 8: ext += s.recv(8 - len(ext))
                length = struct.unpack('>Q', ext)[0]
            data = b''
            while len(data) < length:
                c = s.recv(min(8192, length - len(data)))
                if not c: break
                data += c
            try:
                frames.append(json.loads(data.decode('utf-8')))
            except:
                pass
        except socket.timeout:
            break
    return frames

def send(s, msg_id, method, params=None):
    cmd = json.dumps({"id": msg_id, "method": method, "params": params or {}})
    s.send(ws_frame(cmd))

def wait_for(s, msg_id, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        for frame in ws_recv(s, 1):
            if frame.get('id') == msg_id:
                return frame
    return None

# 连接 CDP
key = base64.b64encode(b'upload_img_12345').decode()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
hs = (f"GET /devtools/page/{PAGE_ID} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n"
      f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
      f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
s.send(hs.encode())
s.settimeout(3)
resp = b''
while b'\r\n\r\n' not in resp:
    resp += s.recv(1024)

# 步骤1：启用 Page domain + 拦截 fileChooser
send(s, 1, 'Page.enable')
time.sleep(0.2); ws_recv(s)
send(s, 2, 'Page.setInterceptFileChooserDialog', {'enabled': True})
wait_for(s, 2, 3)

# 步骤2：获取上传区域坐标
send(s, 3, 'Runtime.evaluate', {
    'expression': '''(function() {
        var el = document.querySelector('.attach-editor-upload') 
            || document.querySelector('[class*=attach-editor-upload]')
            || document.querySelector('.attache-upload-text');
        if (!el) el = Array.from(document.querySelectorAll('[class*=attach] *'))
            .find(e => e.textContent.trim() === '添加本地文件' && !e.querySelector('*'));
        if (!el) return null;
        var r = el.getBoundingClientRect();
        return {x: r.left + r.width/2, y: r.top + r.height/2};
    })()''',
    'returnByValue': True
})
r = wait_for(s, 3, 3)
coords = r.get('result', {}).get('result', {}).get('value') if r else None
if not coords:
    print('ERROR: 找不到上传区域')
    s.close(); exit(1)

x, y = int(coords['x']), int(coords['y'])

# 步骤3：发送真实鼠标点击（触发 fileChooser）
for evt in ['mouseMoved', 'mousePressed', 'mouseReleased']:
    send(s, 40, 'Input.dispatchMouseEvent',
        {'type': evt, 'x': x, 'y': y, 'button': 'left', 'clickCount': 1, 'modifiers': 0})
    time.sleep(0.05); ws_recv(s, 0.2)

# 步骤4：等待 fileChooserOpened 事件
backend_node_id = None
start = time.time()
while time.time() - start < 3:
    for frame in ws_recv(s, 0.5):
        if frame.get('method') == 'Page.fileChooserOpened':
            backend_node_id = frame.get('params', {}).get('backendNodeId')
            break
    if backend_node_id: break

if not backend_node_id:
    print('ERROR: fileChooserOpened 未触发'); s.close(); exit(1)

# 步骤5：用 backendNodeId 写入文件
send(s, 5, 'DOM.setFileInputFiles', {'backendNodeId': backend_node_id, 'files': [FILE_PATH]})
wait_for(s, 5, 5)

# 步骤6：等待并验证
time.sleep(3)
send(s, 6, 'Runtime.evaluate', {
    'expression': '''(function() {
        var items = document.querySelectorAll('[class*="attach"][class*="item"]');
        return {
            count: items.length,
            hasImg: items.length > 0 ? !!items[0].querySelector('img') : false,
            imgSrc: items.length > 0 ? (items[0].querySelector('img') || {}).src : null
        };
    })()''',
    'returnByValue': True
})
r = wait_for(s, 6, 5)
result = r.get('result', {}).get('result', {}).get('value') if r else None
print(f'上传结果: {result}')
# hasImg: true = 上传成功; false = 失败需重试

s.close()
```

**验证标准**：
- `hasImg: true` → ✅ 上传成功，继续填其他字段
- `hasImg: false` → ❌ 失败，重新 navigate 表单后重试，最多 2 次

### 4. 截图确认，等用户下令

截图展示当前表单完整状态，**不自动提交**，等用户明确说「提交」才执行：

```json
{"kind": "click", "ref": "<提交按钮 ref>"}
```

提交后截图确认成功页面。

---

## ⚠️ 已知无效方法（不要再用）

以下方法在飞书 Bitable 表单上**全部无效**，不要重复尝试：

- `browser upload action`（Playwright `page.setInputFiles`）→ React 拦截，`input.files` 写入但 React 不感知
- `DOM.setFileInputFiles(nodeId)` → 同上，走 DOM 路径被 React 拦截
- `dispatch change/input event` → React 不响应合成事件的 files 变化
- `drag/drop DragEvent` → `isTrusted=false` 被飞书检测并忽略
- `fetch/XHR 直接调上传 API` → 需要 CSRF token + 登录态，且不知道 app_token
