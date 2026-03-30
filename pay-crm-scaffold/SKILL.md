# Skill: pay-crm-scaffold（系统脚手架）

## 描述
搭建有赞支付运营CRM系统的完整工程架子，包括 Node.js 服务、目录结构、完整首页、占位子页面、全局 CSS、公共 JS 组件库。

## 触发条件
用户说"搭建脚手架"、"初始化工程"、"创建pay-crm项目"时使用。

---

## 执行步骤

### Step 1：创建目录结构
```bash
mkdir -p ~/Desktop/pay-crm/server
mkdir -p ~/Desktop/pay-crm/website/{html,css,js,data,assets/icons}
```

### Step 2：创建 Node.js 服务

**server/package.json**
```json
{
  "name": "pay-crm-server",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": { "start": "node app.js" },
  "dependencies": { "express": "^4.18.2" }
}
```

**server/app.js**
```javascript
const express = require('express');
const path = require('path');
const os = require('os');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, '../website')));
app.get('/', (_, res) => res.sendFile(path.join(__dirname, '../website/html/index.html')));
app.get('/health', (_, res) => res.json({ status: 'ok' }));

app.listen(PORT, '0.0.0.0', () => {
  let ip = 'localhost';
  Object.values(os.networkInterfaces()).flat().forEach(a => {
    if (a.family === 'IPv4' && !a.internal) ip = a.address;
  });
  console.log(`✅ Pay-CRM 启动: http://localhost:${PORT}`);
  console.log(`📡 局域网: http://${ip}:${PORT}`);
});
```

### Step 3：全局样式

**website/css/global.css**
```css
:root {
  --primary:#1664FF; --primary-light:#E8F0FF; --primary-dark:#1040CC;
  --success:#00B96B; --warning:#FF8800; --danger:#F53F3F; --danger-light:#FFF0F0;
  --text-primary:#1D2129; --text-secondary:#4E5969; --text-placeholder:#86909C; --text-disabled:#C9CDD4;
  --border:#E5E8EB; --border-strong:#C9CDD4;
  --bg-page:#F2F3F5; --bg-card:#FFFFFF;
  --shadow-card:0 2px 8px rgba(0,0,0,0.08);
  --radius-card:8px; --radius-btn:6px; --radius-tag:4px;
  --font-base:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;
  --font-size-sm:12px; --font-size-base:14px; --font-size-lg:16px;
  --font-size-xl:20px; --font-size-xxl:28px;
  --transition:0.2s ease;
  --header-height:56px; --footer-height:44px; --menu-width:220px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;font-family:var(--font-base);font-size:var(--font-size-base);color:var(--text-primary);background:var(--bg-page);-webkit-font-smoothing:antialiased}
a{text-decoration:none;color:inherit} ul,ol{list-style:none}
button{cursor:pointer;border:none;background:none;font-family:inherit}
input,select,textarea{font-family:inherit;outline:none}
.flex{display:flex}.flex-center{display:flex;align-items:center;justify-content:center}
.flex-between{display:flex;align-items:center;justify-content:space-between}
.gap-8{gap:8px}.gap-12{gap:12px}.gap-16{gap:16px}
.text-primary{color:var(--primary)}.text-success{color:var(--success)}
.text-warning{color:var(--warning)}.text-danger{color:var(--danger)}
.text-secondary{color:var(--text-secondary)}.text-sm{font-size:var(--font-size-sm)}.font-bold{font-weight:600}
.mt-16{margin-top:16px}.mb-16{margin-bottom:16px}
.card{background:var(--bg-card);border-radius:var(--radius-card);box-shadow:var(--shadow-card);padding:20px 24px}
.btn{display:inline-flex;align-items:center;gap:6px;padding:7px 16px;border-radius:var(--radius-btn);font-size:var(--font-size-base);font-weight:500;transition:all var(--transition);line-height:1.5;cursor:pointer}
.btn-primary{background:var(--primary);color:#fff;border:1px solid var(--primary)}.btn-primary:hover{background:var(--primary-dark)}
.btn-default{background:#fff;color:var(--text-primary);border:1px solid var(--border-strong)}.btn-default:hover{border-color:var(--primary);color:var(--primary)}
.btn-sm{padding:4px 12px;font-size:var(--font-size-sm)}
.tag{display:inline-flex;align-items:center;padding:2px 8px;border-radius:var(--radius-tag);font-size:var(--font-size-sm);font-weight:500}
.tag-success{background:#E8F9F2;color:var(--success)}.tag-warning{background:#FFF4E5;color:var(--warning)}
.tag-danger{background:var(--danger-light);color:var(--danger)}.tag-primary{background:var(--primary-light);color:var(--primary)}
.tag-default{background:var(--bg-page);color:var(--text-secondary)}
.table-wrap{overflow-x:auto}
.table{width:100%;border-collapse:collapse;font-size:var(--font-size-base)}
.table th,.table td{padding:12px 16px;text-align:left;border-bottom:1px solid var(--border);white-space:nowrap}
.table th{background:var(--bg-page);color:var(--text-secondary);font-weight:500;font-size:var(--font-size-sm)}
.table tbody tr:hover{background:#F8F9FF}
.table .loss-row td{color:var(--danger);background:var(--danger-light)}
.input,.select{padding:8px 12px;border:1px solid var(--border-strong);border-radius:var(--radius-btn);font-size:var(--font-size-base);color:var(--text-primary);background:#fff;transition:border-color var(--transition)}
.input:focus,.select:focus{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary-light)}
.input::placeholder{color:var(--text-placeholder)}
.breadcrumb{display:flex;align-items:center;gap:6px;font-size:var(--font-size-sm);color:var(--text-secondary);margin-bottom:16px}
.breadcrumb .sep{color:var(--text-disabled)}.breadcrumb .current{color:var(--text-primary);font-weight:500}
.pagination{display:flex;align-items:center;justify-content:flex-end;gap:4px;padding:16px 0}
.page-btn{width:32px;height:32px;border-radius:4px;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:var(--font-size-sm);cursor:pointer;transition:all var(--transition)}
.page-btn:hover{border-color:var(--primary);color:var(--primary)}.page-btn.active{background:var(--primary);color:#fff;border-color:var(--primary)}
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 20px;color:var(--text-placeholder)}
.empty-icon{font-size:48px;margin-bottom:12px}
.spinner{width:24px;height:24px;border:3px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin 0.8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}
.kpi-card{background:var(--bg-card);border-radius:var(--radius-card);box-shadow:var(--shadow-card);padding:20px 24px}
.kpi-label{font-size:var(--font-size-sm);color:var(--text-secondary);margin-bottom:8px}
.kpi-value{font-size:var(--font-size-xxl);font-weight:700;color:var(--text-primary)}
.kpi-sub{font-size:var(--font-size-sm);color:var(--text-placeholder);margin-top:4px}
.kpi-card.danger .kpi-value{color:var(--danger)}.kpi-card.success .kpi-value{color:var(--success)}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;z-index:1000;opacity:0;pointer-events:none;transition:opacity var(--transition)}
.modal-overlay.active{opacity:1;pointer-events:all}
.modal{background:#fff;border-radius:var(--radius-card);box-shadow:0 4px 16px rgba(0,0,0,0.12);width:560px;max-width:90vw;max-height:80vh;overflow-y:auto;padding:24px;transform:translateY(-20px);transition:transform var(--transition)}
.modal-overlay.active .modal{transform:translateY(0)}
.modal-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.modal-title{font-size:var(--font-size-lg);font-weight:600}
.wip-container{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:400px;color:var(--text-placeholder)}
.wip-icon{font-size:64px;margin-bottom:16px}
.wip-title{font-size:var(--font-size-xl);font-weight:600;color:var(--text-secondary);margin-bottom:8px}
```

**website/css/layout.css**
```css
.app-layout{display:grid;grid-template-rows:var(--header-height) 1fr var(--footer-height);grid-template-columns:var(--menu-width) 1fr;grid-template-areas:"header header" "menu content" "footer footer";height:100vh;overflow:hidden}
.app-header{grid-area:header;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:#fff;border-bottom:1px solid var(--border);box-shadow:0 1px 4px rgba(0,0,0,0.06);z-index:100}
.header-logo{display:flex;align-items:center;gap:10px}
.logo-mark{width:32px;height:32px;background:var(--primary);border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:16px}
.logo-text{font-size:16px;font-weight:600;color:var(--text-primary)}.logo-text span{color:var(--primary)}
.header-right{display:flex;align-items:center;gap:16px;color:var(--text-secondary);font-size:var(--font-size-sm)}
.header-avatar{width:32px;height:32px;border-radius:50%;background:var(--primary-light);color:var(--primary);display:flex;align-items:center;justify-content:center;font-weight:600;font-size:13px;cursor:pointer}
.app-menu{grid-area:menu;background:#fff;border-right:1px solid var(--border);overflow-y:auto;padding:12px 0}
.menu-item{display:flex;align-items:center;gap:10px;padding:9px 20px;font-size:var(--font-size-base);color:var(--text-secondary);cursor:pointer;transition:all var(--transition);user-select:none}
.menu-item:hover{background:var(--bg-page);color:var(--text-primary)}
.menu-item.active{background:var(--primary-light);color:var(--primary);font-weight:500;border-right:3px solid var(--primary)}
.menu-icon{font-size:16px;width:20px;text-align:center;flex-shrink:0}
.menu-sub .menu-item{padding-left:36px;font-size:var(--font-size-sm)}
.menu-group-toggle{display:flex;align-items:center;justify-content:space-between;padding:9px 20px;color:var(--text-primary);font-weight:500;cursor:pointer;transition:all var(--transition)}
.menu-group-toggle:hover{background:var(--bg-page)}
.menu-arrow{transition:transform var(--transition);font-size:12px;color:var(--text-secondary)}
.menu-group.collapsed .menu-arrow{transform:rotate(-90deg)}.menu-group.collapsed .menu-sub{display:none}
.app-content{grid-area:content;overflow:hidden;background:var(--bg-page)}
.app-content iframe{width:100%;height:100%;border:none;display:block}
.app-footer{grid-area:footer;display:flex;align-items:center;justify-content:center;background:#fff;border-top:1px solid var(--border);font-size:var(--font-size-sm);color:var(--text-placeholder)}
.page-container{padding:24px;min-height:100vh;background:var(--bg-page)}
.page-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.page-title{font-size:var(--font-size-xl);font-weight:600}
.filter-bar{display:flex;align-items:center;flex-wrap:wrap;gap:12px;background:#fff;padding:16px 20px;border-radius:var(--radius-card);box-shadow:var(--shadow-card);margin-bottom:16px}
.section-title{font-size:var(--font-size-lg);font-weight:600;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid var(--border)}
```

**website/css/components.css**
```css
.tabs{display:flex;border-bottom:2px solid var(--border);margin-bottom:20px}
.tab-item{padding:10px 20px;font-size:var(--font-size-base);color:var(--text-secondary);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all var(--transition);font-weight:500}
.tab-item:hover{color:var(--primary)}.tab-item.active{color:var(--primary);border-bottom-color:var(--primary)}
.tab-panel{display:none}.tab-panel.active{display:block}
.progress-bar{background:var(--border);border-radius:4px;height:6px;overflow:hidden}
.progress-fill{height:100%;border-radius:4px;background:var(--primary);transition:width 0.3s ease}
.timeline{position:relative;padding-left:20px}
.timeline::before{content:'';position:absolute;left:7px;top:0;bottom:0;width:2px;background:var(--border)}
.timeline-item{position:relative;padding:0 0 20px 20px}
.timeline-dot{position:absolute;left:-20px;top:4px;width:14px;height:14px;border-radius:50%;background:var(--primary);border:2px solid #fff;box-shadow:0 0 0 2px var(--primary-light)}
.timeline-time{font-size:var(--font-size-sm);color:var(--text-placeholder);margin-bottom:4px}
.timeline-content{background:var(--bg-page);border-radius:var(--radius-btn);padding:10px 14px;font-size:var(--font-size-sm)}
.kanban-board{display:flex;gap:16px;overflow-x:auto;padding-bottom:8px}
.kanban-col{flex:0 0 260px;background:var(--bg-page);border-radius:var(--radius-card);padding:12px}
.kanban-col-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;padding:0 4px}
.kanban-col-title{font-weight:600;font-size:var(--font-size-base)}
.kanban-col-count{font-size:var(--font-size-sm);color:var(--text-secondary);background:#fff;padding:2px 8px;border-radius:10px}
.kanban-card{background:#fff;border-radius:var(--radius-btn);padding:14px;margin-bottom:10px;box-shadow:var(--shadow-card);border-left:3px solid var(--primary);cursor:pointer;transition:box-shadow var(--transition)}
.kanban-card:hover{box-shadow:0 4px 16px rgba(0,0,0,0.12)}
.kanban-card.win{border-left-color:var(--success)}.kanban-card.loss{border-left-color:var(--danger)}
.kanban-card-title{font-weight:600;margin-bottom:6px;font-size:var(--font-size-base)}
.kanban-card-meta{font-size:var(--font-size-sm);color:var(--text-secondary)}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin-bottom:20px}
.stat-card{background:#fff;border-radius:var(--radius-card);padding:16px;box-shadow:var(--shadow-card)}
.stat-label{font-size:var(--font-size-sm);color:var(--text-secondary)}
.stat-value{font-size:24px;font-weight:700;margin:4px 0}
.stat-trend{font-size:var(--font-size-sm);display:flex;align-items:center;gap:4px}
.trend-up{color:var(--success)}.trend-down{color:var(--danger)}
.chart-container{position:relative;width:100%}
.chart-title{font-size:var(--font-size-base);font-weight:600;margin-bottom:12px}
.info-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}
.info-label{font-size:var(--font-size-sm);color:var(--text-secondary);margin-bottom:4px}
.info-value{font-size:var(--font-size-base);font-weight:500}
.loss-badge{display:inline-flex;align-items:center;gap:4px;background:var(--danger-light);color:var(--danger);padding:3px 8px;border-radius:4px;font-size:var(--font-size-sm);font-weight:600}
```

### Step 4：公共 JS

**website/js/common.js**
```javascript
function renderBreadcrumb(items, id='breadcrumb') {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = items.map((item,i) => i === items.length-1
    ? `<span class="current">${item}</span>`
    : `<span>${item}</span><span class="sep">›</span>`
  ).join('');
}
function formatMoney(v) {
  if (v>=1e8) return (v/1e8).toFixed(2)+'亿元';
  if (v>=1e4) return (v/1e4).toFixed(2)+'万元';
  return v.toLocaleString()+'元';
}
function formatRate(v) { return (v*100).toFixed(2)+'%'; }
function formatNum(v) { return v>=1e4?(v/1e4).toFixed(1)+'万':v.toLocaleString(); }
const STATUS_MAP = {
  normal:{text:'正常',cls:'tag-success'}, frozen:{text:'冻结',cls:'tag-warning'},
  closed:{text:'注销',cls:'tag-default'}, verified:{text:'已认证',cls:'tag-success'},
  pending:{text:'审核中',cls:'tag-warning'}, unverified:{text:'未认证',cls:'tag-default'},
};
function statusTag(key) {
  const s = STATUS_MAP[key]||{text:key,cls:'tag-default'};
  return `<span class="tag ${s.cls}">${s.text}</span>`;
}
function marginClass(r) { return r<0?'text-danger':r<0.001?'text-warning':'text-success'; }
function initTabs(tabsEl) {
  tabsEl.querySelectorAll('.tab-item').forEach(item => {
    item.addEventListener('click', () => {
      tabsEl.querySelectorAll('.tab-item').forEach(t=>t.classList.remove('active'));
      item.classList.add('active');
      const wrapper = tabsEl.closest('.tab-wrapper');
      wrapper?.querySelectorAll('.tab-panel').forEach(p=>p.classList.toggle('active',p.id===item.dataset.tab));
    });
  });
}
function renderPagination(id, total, page, pageSize, fn) {
  const el = document.getElementById(id); if(!el) return;
  const tp = Math.ceil(total/pageSize);
  let h = `<button class="page-btn" onclick="${fn}(${page-1})" ${page<=1?'disabled':''}>‹</button>`;
  for(let i=1;i<=tp;i++){
    if(i===1||i===tp||Math.abs(i-page)<=1) h+=`<button class="page-btn ${i===page?'active':''}" onclick="${fn}(${i})">${i}</button>`;
    else if(Math.abs(i-page)===2) h+=`<span style="padding:0 4px;color:var(--text-disabled)">…</span>`;
  }
  h+=`<button class="page-btn" onclick="${fn}(${page+1})" ${page>=tp?'disabled':''}>›</button>`;
  h+=`<span style="font-size:12px;color:var(--text-secondary);margin-left:8px">共${total}条</span>`;
  el.innerHTML=h;
}
function openModal(id){document.getElementById(id)?.classList.add('active');}
function closeModal(id){document.getElementById(id)?.classList.remove('active');}
async function fetchData(url){const r=await fetch(url);if(!r.ok)throw new Error('加载失败:'+url);return r.json();}
function debounce(fn,ms=300){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms);};}
```

### Step 5：主框架页 index.html

**website/html/index.html**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>有赞支付运营管理中心</title>
  <link rel="stylesheet" href="/css/global.css">
  <link rel="stylesheet" href="/css/layout.css">
</head>
<body>
<div class="app-layout">
  <header class="app-header">
    <div class="header-logo">
      <div class="logo-mark">赞</div>
      <div class="logo-text">有赞<span>支付运营</span>管理中心</div>
    </div>
    <div class="header-right">
      <span>📅 <span id="today-date"></span></span>
      <span style="cursor:pointer">🔔</span>
      <div class="header-avatar">运</div>
      <span>运营管理员</span>
    </div>
  </header>

  <nav class="app-menu">
    <div class="menu-item active" data-page="/html/dashboard.html">
      <span class="menu-icon">🏠</span>首页看板
    </div>

    <div class="menu-group" id="group-merchant">
      <div class="menu-group-toggle" onclick="toggleGroup('group-merchant')">
        <span style="display:flex;align-items:center;gap:10px"><span class="menu-icon">🏪</span>商家管理</span>
        <span class="menu-arrow">▾</span>
      </div>
      <div class="menu-sub">
        <div class="menu-item" data-page="/html/merchant-list.html">商家列表</div>
        <div class="menu-item" data-page="/html/merchant-detail.html">商家详情</div>
      </div>
    </div>

    <div class="menu-group" id="group-crm">
      <div class="menu-group-toggle" onclick="toggleGroup('group-crm')">
        <span style="display:flex;align-items:center;gap:10px"><span class="menu-icon">📋</span>CRM销售管理</span>
        <span class="menu-arrow">▾</span>
      </div>
      <div class="menu-sub">
        <div class="menu-item" data-page="/html/crm-leads.html">线索管理</div>
        <div class="menu-item" data-page="/html/crm-funnel.html">销售漏斗</div>
      </div>
    </div>

    <div class="menu-group" id="group-int">
      <div class="menu-group-toggle" onclick="toggleGroup('group-int')">
        <span style="display:flex;align-items:center;gap:10px"><span class="menu-icon">🔗</span>对接进展</span>
        <span class="menu-arrow">▾</span>
      </div>
      <div class="menu-sub">
        <div class="menu-item" data-page="/html/integration.html">对接任务列表</div>
      </div>
    </div>

    <div class="menu-group" id="group-report">
      <div class="menu-group-toggle" onclick="toggleGroup('group-report')">
        <span style="display:flex;align-items:center;gap:10px"><span class="menu-icon">📊</span>数据分析</span>
        <span class="menu-arrow">▾</span>
      </div>
      <div class="menu-sub">
        <div class="menu-item" data-page="/html/report-product.html">产品线报表</div>
        <div class="menu-item" data-page="/html/report-channel.html">渠道报表</div>
      </div>
    </div>

    <div class="menu-item" data-page="/html/order-query.html">
      <span class="menu-icon">🔍</span>订单查询
    </div>
  </nav>

  <main class="app-content">
    <iframe id="main-iframe" src="/html/dashboard.html"></iframe>
  </main>

  <footer class="app-footer">
    © 2026 有赞支付运营 · 内部系统 · <span id="server-time"></span>
  </footer>
</div>

<script>
const iframe = document.getElementById('main-iframe');
// 日期
document.getElementById('today-date').textContent = new Date().toLocaleDateString('zh-CN');
// 时间
function tick() { document.getElementById('server-time').textContent = new Date().toLocaleTimeString('zh-CN'); }
tick(); setInterval(tick, 1000);

// 菜单组折叠
function toggleGroup(id) {
  document.getElementById(id).classList.toggle('collapsed');
}

// 菜单切换
document.querySelectorAll('.menu-item[data-page]').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
    item.classList.add('active');
    iframe.src = item.dataset.page;
    localStorage.setItem('lastPage', item.dataset.page);
  });
});

// 恢复上次页面
const last = localStorage.getItem('lastPage');
if (last) {
  iframe.src = last;
  document.querySelectorAll('.menu-item').forEach(m => {
    m.classList.toggle('active', m.dataset.page === last);
  });
}
</script>
</body>
</html>
```

### Step 6：占位子页面模板

以下每个页面复用同一模板，仅改面包屑和标题。

**通用占位页结构（示例 crm-leads.html）：**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>线索管理</title>
  <link rel="stylesheet" href="/css/global.css">
  <link rel="stylesheet" href="/css/layout.css">
  <link rel="stylesheet" href="/css/components.css">
</head>
<body>
<div class="page-container">
  <div class="breadcrumb" id="breadcrumb"></div>
  <div class="page-header">
    <h1 class="page-title">线索管理</h1>
  </div>
  <div class="card wip-container">
    <div class="wip-icon">🚧</div>
    <div class="wip-title">开发中</div>
    <div class="wip-desc text-secondary">CRM 线索管理页