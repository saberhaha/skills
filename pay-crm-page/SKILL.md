# Skill: pay-crm-page（具体页面开发）

## 描述
根据输入的页面名称、组件清单和数据文件，生成有赞支付运营CRM系统的具体功能页面。
依赖脚手架 skill（pay-crm-scaffold）已完成。

## 触发条件
用户说"开发某某页面"、"生成具体页面内容"、"实现XXX功能页"时使用。

## 输入参数
- **页面名称**：如 dashboard、merchant-list、crm-leads 等
- **面包屑路径**：如 ["首页"]、["商家管理", "商家列表"]
- **组件列表**：如 [kpi-card, table, filter-bar, pagination]
- **数据文件**：如 /data/merchants.json

---

## 页面开发规范

### HTML 页面模板结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>{页面标题}</title>
  <link rel="stylesheet" href="/css/global.css">
  <link rel="stylesheet" href="/css/layout.css">
  <link rel="stylesheet" href="/css/components.css">
</head>
<body>
<div class="page-container">
  <!-- 面包屑 -->
  <div class="breadcrumb" id="breadcrumb"></div>

  <!-- 页面头部：标题 + 操作按钮 -->
  <div class="page-header">
    <h1 class="page-title">{页面标题}</h1>
    <div class="flex gap-8">{操作按钮}</div>
  </div>

  <!-- 筛选栏（有筛选需求时）-->
  <div class="filter-bar">{筛选组件}</div>

  <!-- 核心内容区 -->
  {核心内容}

  <!-- 分页（有列表时）-->
  <div class="pagination" id="pagination"></div>
</div>
<script src="/js/common.js"></script>
<script src="/js/{页面}.js"></script>
</body>
</html>
```

### JS 页面脚本模板结构
```javascript
// 页面初始化
document.addEventListener('DOMContentLoaded', async () => {
  // 1. 渲染面包屑
  renderBreadcrumb(['{父级}', '{当前页}']);

  // 2. 加载数据
  const data = await fetchData('/data/{数据文件}.json');

  // 3. 渲染内容
  render(data);

  // 4. 绑定交互事件
  bindEvents();
});
```

---

## 各页面实现规格

### 1. dashboard.html（首页看板）
- **面包屑**：["首页"]
- **组件**：5个KPI卡片、GMV折线图、产品线饼图、亏损预警列表
- **数据**：/data/dashboard.json
- **特殊**：引入 Chart.js CDN 渲染图表

### 2. merchant-list.html（商家列表）
- **面包屑**：["商家管理", "商家列表"]
- **组件**：搜索输入框、来源筛选、状态筛选、数据表格、分页
- **数据**：/data/merchants.json
- **表格列**：商家ID | 商家名称 | 来源 | 认证 | 支付方式数 | 本月GMV | 毛利率 | 状态 | 操作
- **特殊**：毛利率<0 整行标红，点击"详情"跳转 merchant-detail.html

### 3. merchant-detail.html（商家详情）
- **面包屑**：["商家管理", "商家列表", "商家详情"]
- **组件**：5个Tab（基础档案/开户信息/费率成本/交易数据/跟进记录）
- **数据**：/data/merchants.json（根据URL参数 ?id=xxx 筛选）
- **特殊**：
  - 费率成本 Tab：对客<上游时该行标红 + 显示 loss-badge
  - 交易数据 Tab：近6月趋势折线图（Chart.js）
  - 跟进记录 Tab：timeline 组件

### 4. crm-leads.html（线索管理）
- **面包屑**：["CRM销售管理", "线索管理"]
- **组件**：看板视图（Kanban）+ 列表视图切换、状态流转按钮
- **数据**：/data/crm-leads.json
- **Kanban列**：新线索 → 跟进中 → 报价中 → 赢单 | 输单

### 5. crm-funnel.html（销售漏斗）
- **面包屑**：["CRM销售管理", "销售漏斗"]
- **组件**：漏斗图（SVG实现）、转化率统计卡片、销售员业绩表格
- **数据**：/data/crm-leads.json（聚合计算）

### 6. integration.html（对接进展）
- **面包屑**：["对接进展", "对接任务列表"]
- **组件**：筛选栏、表格（含进度条）、卡点标记
- **数据**：/data/integration.json
- **表格列**：商家名 | 对接阶段 | 进度 | 卡点 | 负责人 | 预计上线 | 实际上线 | 状态

### 7. report-product.html（产品线报表）
- **面包屑**：["数据分析", "产品线报表"]
- **组件**：时间范围选择、产品线筛选、KPI卡片、柱状图、数据表格
- **数据**：/data/transactions.json（按 productLine 聚合）

### 8. report-channel.html（渠道报表）
- **面包屑**：["数据分析", "渠道报表"]
- **组件**：时间范围选择、渠道筛选、KPI卡片、饼图+折线图、数据表格
- **数据**：/data/transactions.json（按 channel 聚合）

### 9. order-query.html（订单查询）
- **面包屑**：["订单查询"]
- **组件**：多条件搜索栏（商家ID/时间段/支付方式/金额范围）、表格、详情弹窗
- **数据**：/data/orders.json
- **表格列**：订单号 | 商家 | 金额 | 支付方式 | 渠道 | 状态 | 时间 | 操作

---

## 数据文件规格（JSON Schema）

### /data/merchants.json
```json
{
  "merchants": [{
    "id": "kdt_10001",
    "name": "示例商家A",
    "source": "saas",
    "industry": "零售",
    "signDate": "2024-06-01",
    "status": "normal",
    "kyc": "verified",
    "bindCard": true,
    "payMethods": ["wechat","alipay","unionpay"],
    "payChannels": ["四方-汇付","直连-微信"],
    "monthlyGmv": 1200000,
    "monthlyOrders": 8500,
    "grossMarginRate": 0.0013,
    "rates": [
      {"method":"微信支付","customerRate":0.0038,"upstreamRate":0.0025},
      {"method":"支付宝","customerRate":0.0035,"upstreamRate":0.0025},
      {"method":"银联","customerRate":0.0020,"upstreamRate":0.0022}
    ],
    "followups": [
      {"time":"2026-03-20 14:30","content":"已发送报价单，等待回复","author":"销售小王"}
    ]
  }]
}
```

### /data/crm-leads.json
```json
{
  "leads": [{
    "id": "lead_001",
    "merchantName": "待签约商家B",
    "source": "主动拓展",
    "stage": "报价中",
    "owner": "销售小王",
    "quotedRate": 0.0038,
    "expectedGmv": 500000,
    "followups": [
      {"time":"2026-03-20","content":"已发报价单"}
    ]
  }]
}
```

### /data/integration.json
```json
{
  "tasks": [{
    "id": "int_001",
    "merchantName": "对接商家C",
    "stage": "联调测试",
    "progress": 60,
    "blocker": "沙箱环境签名错误",
    "owner": "技术小李",
    "expectedDate": "2026-04-15",
    "actualDate": null,
    "status": "in_progress"
  }]
}
```

### /data/transactions.json
```json
{
  "summary": {
    "totalGmv": 45600000,
    "totalOrders": 312000,
    "totalProfit": 89000,
    "activeMerchants": 186,
    "pmv": 142,
    "lossMerchants": 12
  },
  "monthly": [
    {"month":"2025-10","gmv":3200000,"orders":21000,"profit":6200},
    {"month":"2025-11","gmv":3800000,"orders":25000,"profit":7400},
    {"month":"2025-12","gmv":5100000,"orders":33000,"profit":9800},
    {"month":"2026-01","gmv":4200000,"orders":28000,"profit":8100},
    {"month":"2026-02","gmv":3900000,"orders":26000,"profit":7600},
    {"month":"2026-03","gmv":4800000,"orders":31000,"profit":9200}
  ],
  "byProductLine": [
    {"name":"SaaS收款","gmv":22000000,"orders":150000,"profit":43000},
    {"name":"支付开放","gmv":15000000,"orders":100000,"profit":29000},
    {"name":"服务商","gmv":8600000,"orders":62000,"profit":17000}
  ],
  "byChannel": [
    {"name":"微信支付","gmv":20000000,"orders":140000,"profit":38000,"marginRate":0.0019},
    {"name":"支付宝","gmv":15000000,"orders":100000,"profit":28000,"marginRate":0.0019},
    {"name":"银联","gmv":6000000,"orders":42000,"profit":9000,"marginRate":0.0015},
    {"name":"境外卡","gmv":4600000,"orders":30000,"profit":14000,"marginRate":0.0030}
  ]
}
```

### /data/orders.json
```json
{
  "orders": [{
    "id": "PAY20260301001",
    "merchantId": "kdt_10001",
    "merchantName": "示例商家A",
    "amount": 299.00,
    "method": "微信支付",
    "channel": "四方-汇付",
    "status": "success",
    "customerRate": 0.0038,
    "actualFee": 1.14,
    "time": "2026-03-01 10:23:45"
  }]
}
```

---

## 执行说明

1. 每次调用本 skill，指定目标页面名称
2. 创建对应的 `website/html/{page}.html` 文件（完整内容）
3. 创建对应的 `website/js/{page}.js` 文件（完整逻辑）
4. 如数据文件不存在，同步创建 `website/data/{file}.json`
5. 页面顶部必须有面包屑，引用 `common.js`
6. 亏损/预警逻辑必须有视觉标红

## 质量标准
- 所有交互功能可用（筛选、分页、Tab切换、弹窗）
- 数据从 JSON 文件异步加载，页面与数据解耦
- 视觉风格与 global.css 设计规范一致
- 无 JS 报错，页面可独立在浏览器中正常渲染
