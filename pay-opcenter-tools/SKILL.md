---
name: pay-opcenter-tools
description: |
  【仅当用户消息中明确包含"支付运营平台"或"opc"关键词时才使用本技能。】
  支付运营平台工具集，涵盖 20 个业务域、共 182 个核心功能点。
  触发条件：用户输入必须包含"支付运营平台"或"opc"，例如：
  - "在支付运营平台查询路由规则"
  - "查询opc的路由规则"
  - "帮我查一下支付运营平台的商户信息"
  - "帮我查一下opc的商户信息"
  - "支付运营平台的对账报表"
  - "支付运营平台切到QA环境"
  注意：若用户输入不含"支付运营平台"或"opc"，即使涉及查询/账单/商户等词汇，也不得使用本技能。
user-invocable: true
created: 2026-03-12T16:00:00.000Z
updated: 2026-03-16T12:00:00.000Z
author: ai-agent
---

# pay-opcenter-tools — 支付运营平台工具集

支付运营平台 AI 智能体基座，将复杂的传统界面功能原子化封装为标准化代理工具（AI Skills）。

## 快速开始

所有的底层 Python 将暴露给上层 AI LLM 进行自动化调用。用户无需手动触发 Python 脚本，直接通过自然语言即可完成操作。

**自然语言调用示例：**

1. "帮我查询一下微信支付的路由规则，灰度码是 test001"
2. "查询最近一个月状态为可用的通讯模板"
3. "查询合作商户是'大润发'的切路由配置"
4. "查询店铺 12345 的商户信息"
5. "查询近7天的退款异常记录"
6. "查询2026年3月的对账报表"

**环境切换（自然语言）：**

用户可通过自然语言快速切换环境：
- "帮我把支付运营平台的环境切到QA" → 切换到 QA 环境
- "切到线上" → 切换到 Prod 环境
- "切到预发" → 切换到 Pre 环境
- "查看当前环境配置" → 显示当前环境信息

**CLI 手动调试配置 Token:**
首次使用需配置测试环境的 Cookie `OAuth_TOKEN` 以完成认证授权。

```bash
cd skills/pay-opcenter-tools/

# 配置 Token
python3 shared/base_client.py config --token <你的_OAuth_TOKEN_内容>

# 环境切换
python3 shared/env_config.py switch qa     # 切换到 QA 环境
python3 shared/env_config.py switch pre    # 切换到预发环境
python3 shared/env_config.py switch prod   # 切换到线上环境
python3 shared/env_config.py show          # 查看当前配置
```

Token 获取方式：打开对应环境页面 → F12 → Application → Cookies → OAuth_TOKEN

## 核心术语

| 术语 | 别名 | 说明 |
|------|------|------|
| **userNo** | mchId、商户号 | 商户的唯一标识号，如 `230814102245000000` |
| **kdtId** | 店铺ID | 有赞店铺的唯一标识，如 `12345678` |

## 功能域划分：渠道域

共 14 个功能点（v1/v2/v3）：

### v3 版本
- `query_route_rule`：路由规则管理
- `query_route_channel`：路由渠道管理
- `query_channel_account`：渠道账户管理
- `query_comm_template`：通讯模板管理
- `query_comm_chain`：通讯链管理
- `query_comm_template_switch`：通讯模板开关管理
- `query_comm_relation`：通讯关联管理
- `query_comm_item`：通讯项管理
- `query_comm_actor`：通讯角色管理

### v2 版本
- `query_withdraw_channel`：提现渠道管理

### v1 版本
- `query_switch_route`：切路由配置
- `query_merchant_info`：商户信息配置
- `query_wechat_sub_mch`：微信子商户管理
- `query_withdraw_status`：提现状态详情

## 功能域划分：权限域

共 14 个功能点（v1/v3）：

### v3 版本
- `query_permission_list`：权限列表
- `query_permission_detail`：权限详情
- `query_role_list`：角色列表
- `query_role_detail`：角色详情
- `query_group_list`：分组列表
- `query_group_detail`：分组详情
- `query_user_list`：用户列表
- `query_user_detail`：用户详情
- `query_permission_view`：权限视图

### v1 版本
- `query_permission_view_v1`：权限视图（v1）
- `query_permission_config_auth`：权限配置-权限管理
- `query_permission_config_user`：权限配置-用户管理
- `query_permission_config_role`：权限配置-角色管理
- `query_permission_config_resource`：权限配置-资源管理

## 功能域划分：账务域

共 10 个功能点（v1/v2/v3）：

### v3 版本
- `query_inoutlog_v3`：出入账记录查询
- `query_inout_config_v3`：收支配置管理
- `query_release_order_v3`：释放冻结订单
- `query_microaccount_v3`：预存款账户查询

### v2 版本
- `query_ght_withdraw_v2`：GHT出款记录查询
- `query_provision_upload_v2`：备付金上传记录查询
- `query_adjust_bill_v2`：调账单列表查询
- `query_cross_settlement_v2`：跨境结算批次查询

### v1 版本
- `query_inoutlog_v1`：出入账日志查询
- `query_account_manage_fee_v1`：账户管理费查询

## 功能域划分：产品域

共 2 个功能点（v1）：

### v1 版本
- `query_attribute_list`：累计属性配置列表查询
- `query_strategy_list`：累计策略配置列表查询

## 功能域划分：会计域

共 16 个功能点（v1/v2），3个存根（源码无真实API）：

### v2 版本
- `query_accounting_code`：会计码管理
- `query_accounting_subject_management`：会计科目管理
- `query_subject_balance_adjust`：科目余额调整
- `query_bookkeeping_rule_management`：记账规则管理

### v1 版本
- `query_profit_report`：利润报表
- `query_liabilities_report`：负债报表
- `query_daily_summary_report`：日汇总报表
- `query_subject_daily_summary`：科目日汇总
- `query_trial_balance`：试算查询
- `query_rule_info_report`：规则信息报表
- `query_bookkeeping_error`：记账错误查询
- `query_accounting_subject_config`：会计科目配置
- `query_bookkeeping_rule_config`：记账规则配置
- `query_accounting_params`：参数维护（存根，源码无真实API）
- `query_bookkeeping_query`：记账查询（存根，源码无真实API）
- `query_single_order`：单笔订单查询（存根，源码无真实API）

## 功能域划分：网关域

共 3 个功能点（v1）：

### v1 版本
- `query_gateway_list`：网关列表
- `query_gateway_test_param`：网关测试参数元信息
- `query_gateway_detail`：网关详情

## 功能域划分：财务域

共 9 个功能点（v1/v3）：

### v3 版本
- `query_quick_payment_invoice`：快捷回款-发票查询
- `query_quick_payment_channel`：快捷回款-渠道账户余额查询
- `query_customer_rate`：客户费率列表查询
- `query_customer_rate_detail`：客户费率详情查询

### v1 版本
- `query_monitor_config`：监控配置查询
- `query_finance_withdraw`：财务提现记录查询
- `query_finance_refund`：财务回款（退款）记录查询
- `query_finance_provision`：财务备付金记录查询
- `query_unionpay_balance`：银联备付金余额查询

## 功能域划分：退款域

共 13 个功能点（v1/v2/v3）：

### v3 版本
- `query_quick_refund_close_v3`：快捷退款-关闭扣款查询
- `query_compensation_v3`：赔付管理查询
- `query_invoice_reversal_v3`：发票红冲管理查询
- `query_fund_disposal_v3`：资金处置管理查询
- `query_fund_recovery_v3`：资金追回管理查询
- `query_refund_rollback_v3`：退款回退查询
- `query_refund_rule_v3`：退款规则管理查询
- `query_refund_order_v3`：退款订单管理查询

### v2 版本
- `query_refund_exception_v2`：退款异常查询
- `query_abnormal_refund_v2`：异常退款单/追偿单查询
- `query_refund_exception_history_v2`：退款异常历史查询

### v1 版本
- `query_refund_exception_v1`：退款异常记录查询
- `query_refund_detail_v1`：退款详情查询

## 功能域划分：备付金额度域

共 1 个功能点（v2）：

### v2 版本
- `query_provision_limit_mapping`：备付金额度映射查询

## 功能域划分：商户域

共 19 个功能点（v1/v3）：

### v3 版本
- `query_id_cross_v3`：ID互查
- `query_kdtid_userno_v3`：KdtId/UserNo互查
- `query_operation_record_v3`：操作记录查询
- `query_account_v3`：通用资产账号查询
- `query_bank_card_v3`：银行卡管理查询
- `query_member_detail_v3`：会员详情查询
- `query_wechat_gold_card_v3`：微信金卡查询
- `query_user_info_v3`：用户信息查询
- `query_user_bank_card_v3`：用户绑卡列表查询（v3）
- `query_wechat_whitelist_v3`：微信白名单管理查询
- `query_wechat_cert_v3`：微信证书过期管理查询
- `query_cashier_tool_v3`：收银台支付工具列表查询（v3）

### v1 版本
- `query_contract_v1`：合同管理查询
- `query_merchant_tool_v1`：商户工具查询
- `query_merchant_v1`：商户管理查询
- `query_sms_config_v1`：短信配置查询
- `query_export_template_v1`：导出模板管理查询
- `query_user_bank_card_v1`：用户绑卡列表查询（v1）
- `query_cashier_tool_v1`：收银台支付工具列表查询（v1）

## 功能域划分：对账域

共 16 个功能点（v2/v3），1个占位存根：

### v3 版本
- `query_actual_reconcile_v3`：实收核对查询
- `query_reconcile_report_v3`：对账报表查询
- `query_error_diagnosis_v3`：差错诊断查询
- `query_account_reconcile_v3`：账户核对查询
- `query_internal_reconcile_unit_v3`：内部对账-单元查询
- `query_internal_reconcile_platform_v3`：内部对账-平台（占位，无独立接口）
- `query_internal_reconcile_task_v3`：内部对账-任务详情查询
- `query_internal_reconcile_diff_v3`：内部对账-差异详情查询
- `query_error_biz_ops_v3`：差错诊断-业务操作记录
- `query_error_channel_ops_v3`：差错诊断-渠道操作记录
- `query_suspicious_data_v3`：存疑数据查询
- `query_reconcile_file_v3`：对账文件管理查询
- `query_reconcile_result_v3`：对账结果查询
- `query_bill_detail_v3`：账单明细查询

### v2 版本
- `query_reconcile_v2`：核对查询
- `query_bill_v2`：账单查询

## 功能域划分：计费清结算域

共 7 个功能点（v1）：

### v1 版本
- `query_billing_rule_config`：计费规则配置列表查询
- `query_billing_package_config`：商户收费包配置列表查询
- `query_package_guarantee_config`：大客套餐有赞担保5W封顶列表查询
- `query_shop_sign`：店铺计费包签约列表查询
- `query_voucher_audit`：凭证审核列表查询
- `query_billing_check`：计费清结算对账查询
- `query_settlement_rule_config`：结算规则配置列表查询

## 功能域划分：清结算域

共 9 个功能点（v2/v3）：

### v3 版本
- `query_business_rule_binding`：业务规则绑定查询
- `query_merchant_fee_rule`：商户费率规则查询
- `query_product_rule_result`：产品规则结果查询
- `query_product_rule_config`：产品规则配置查询
- `query_product_config_master`：产品配置主数据查询
- `query_fee_ratio_template`：费率模板管理查询
- `query_fee_product`：计费产品管理查询
- `query_inner_merchant`：内部商户结算查询

### v2 版本
- `query_settlement_record`：清结算记录查询（含清算明细、银行信息）

## 功能域划分：内部支付域

共 6 个功能点（v1/v3）：

### v1 版本
- `query_payment_info`：支付信息查询（对应/page/paymentInfo，需提供订单号，返回支付信息、交易信息、退款信息、优惠详情、手续费信息等多区块）
- `query_pay_info`：商户支付信息查询（对应/page/payInfo，支持按商户名称/号、客户号、订单号、收单号、渠道订单号、支付方式、业务类型、业务状态、创建/更新时间筛选）
- `query_mistake_detail`：差错详情查询（需提供业务ID bizId，返回退款流水列表含退款状态/账号/失败原因等）
- `query_full_payment_info`：支付完整信息查询（支持按收单号/订单号/商户号/子商户识别码/kdtId查询，返回支付信息、退款信息、交易信息、优惠详情等多卡片）

### v3 版本
- `query_user_membill`：用户支付记录查询（需提供用户编号，返回用户支付账单列表）
- `query_old_orders`：历史订单查询（支持按订单号/手机号/店铺ID查询历史订单）

## 功能域划分：数据中心域

共 4 个功能点（v3）：

### v3 版本
- `query_model_rule_management`：模型规则管理查询（支持分页查询模型规则列表）
- `query_model_info_management`：模型信息管理查询（支持按模型ID/名称查询模型配置）
- `query_rule_info_management`：规则信息管理查询（支持按规则ID/类型查询规则详情）
- `query_log_record_list`：日志记录列表查询（支持按时间/操作人/操作类型筛选日志）

## 功能域划分：资金域

共 7 个功能点（v3）：

### v3 版本
- `query_secured_trade_loan`：担保交易-贷款查询（需提供贷款合同单号，返回贷款详情及订单列表）
- `query_secured_trade_repay`：担保交易-还款查询（需提供还款单号，返回还款详情、还款计划明细及还款记录）
- `query_payment_voucher`：支付凭证查询（电子回单，需提供转账交易单号，支持权限验证）
- `query_batch_transfer`：批量转账记录查询（支持按申请时间/审核人/状态/批次号筛选，默认近7天执行成功）
- `query_quick_increase_quota`：快速提额-自有渠道额度评估（无入参，返回昨日额度不足Top30店铺）
- `query_quick_increase_manual`：快速提额-人工提额记录（支持按店铺ID/名称/状态筛选）
- `query_recharge_quota`：商家充值限额信息查询（需提供店铺ID或商户号，支持ID双向转换）
## 功能域划分：微信流程域

共 5 个功能点（v1）：

### v1 版本
- `query_pay_process`：支付流程详情（进件状态查询）
- `query_pay_config`：支付配置详情（进件配置查询）
- `query_pay_config_task`：支付配置详情-任务记录查询
- `query_pay_config_log`：支付配置详情-操作日志查询
- `query_wx_settle_rate`：微信结算费率配置查询

## 功能域划分：计费规则域

共 14 个功能点（v1/v2/v3）：

### v3 版本
- `query_fee_product_v3`：计费产品管理查询
- `query_fee_ratio_template_v3`：费率模板管理查询
- `query_merchant_fee_rule_v3`：商户费率规则查询
- `query_product_rule_config_v3`：产品规则配置查询
- `query_product_rule_result_v3`：产品规则结果查询
- `query_business_rule_binding_v3`：业务规则绑定查询

### v2 版本
- `query_general_fee_rule_v2`：通用计费规则查询
- `query_merchant_fee_rule_v2`：商家计费规则查询
- `query_settlement_assets_v2`：结算资产规则查询

### v1 版本
- `query_billing_rule_config_v1`：计费规则配置查询
- `query_billing_package_config_v1`：计费套餐配置查询
- `query_package_guarantee_v1`：套餐保证金配置查询
- `query_shop_sign_v1`：店铺签约查询
- `query_settlement_rule_config_v1`：结算规则配置查询

## 功能域划分：账户查询域

共 8 个功能点（v2/v3）：

### v3 版本
- `query_account_v3`：通用资产账号查询

### v2 版本
- `query_outer_account_v2`：外部账户查询（资金账户查询）
- `query_outer_account_detail_v2`：外部账户明细查询
- `query_outer_account_frozen_v2`：外部账户冻结明细查询
- `query_inner_account_v2`：内部账户查询（内部资金账户查询）
- `query_inner_account_detail_v2`：内部账户明细查询
- `query_fin_report_v2`：会计报表查询（科目总账表）
- `query_total_report_v2`：总分平衡表查询

## 功能域划分：收银台域

共 21 个功能点（v3）：

### v3 版本
- `query_cashier_type_manage`：收银台类型配置规则查询
- `query_cashier_type_version`：收银台类型版本列表查询
- `query_payinfos_global`：PayInfos全局配置规则查询
- `query_payinfos_priority`：PayInfos优先级配置规则查询
- `query_payinfos_version`：PayInfos版本列表查询
- `query_paytools_global`：PayTools全局配置规则查询
- `query_paytools_priority`：PayTools优先级配置规则查询
- `query_paytools_version`：PayTools版本列表查询
- `query_paytools_preview`：PayTools支付工具列表预览
- `query_scenariokv_paytool`：场景KV-支付工具名单查询
- `query_scenariokv_biz`：场景KV-业务名单查询
- `query_scenariokv_hostapp`：场景KV-HostApp名单查询
- `query_scenariokv_runtime`：场景KV-运行时名单查询
- `query_scenariokv_protocol`：场景KV-协议名单查询
- `query_scenariokv_cashier_type`：场景KV-收银台类型名单查询
- `query_scenariokv_partner_id`：场景KV-合作方ID名单查询
- `query_scenariokv_sdk`：场景KV-SDK名单查询
- `query_cashier_plugin_latest`：收银台插件最新版本查询
- `query_cert_manage_pages`：页面证书列表查询
- `query_cert_wap_content`：页面证书WAP编辑内容查询
- `query_cert_version`：页面证书版本历史查询

## 输出规则

工具脚本中定义了三种展示结构，必须严格按对应格式输出，**所有定义的字段/列都必须出现在输出中，禁止遗漏**。

### 1. `DISPLAY_COLUMNS`（列表表格）

适用于返回多条记录的列表查询。输出为 Markdown 表格，表头和列顺序严格按 `DISPLAY_COLUMNS` 定义。

```
| 商户名称 | 商户号 | 支付方式 | 业务状态 | 创建时间 |
|---------|-------|---------|---------|---------|
| xxx商户 | 12345 | WX_JS   | 支付成功 | 2026-03-16 19:51:35 |
```

### 2. `DISPLAY_TABLES`（多区块混合展示）

适用于单条记录包含多个维度信息的场景（如交易支付信息查询、结算资产规则查询）。每个区块独立输出，根据数据特征选择格式：

**字典格式的 DISPLAY_TABLES**（key 为区块名，value 为 columns 数组或描述字符串）：
- 单条记录区块 → 输出为 KV 竖排列表：
```
### 交易信息
- 业务单号：2603161951352621740237
- 状态：交易失败
- 交易描述：碰碰贴交易-担保交易
```

- 多条记录区块 → 输出为 Markdown 表格：
```
### 支付信息
| 支付金额 | 支付时间 | 状态 | 支付明细号 |
|---------|---------|------|-----------|
| 0.01 | 2026-03-16 19:51:35 | 支付中 | 260316... |
```

- value 为描述字符串的区块（如 `"退款信息": "展示退款列表"`）→ 根据实际返回数据结构输出表格或 KV 列表。

**数组格式的 DISPLAY_TABLES**（每项含 name + columns）：
- 每个 name 作为区块标题，按 columns 字段输出 Markdown 表格。

- 空数据区块 → 输出 `（无数据）`，不省略区块标题。

### 3. `DISPLAY_SECTIONS`（KV 详情分区）

适用于详情页查询，返回单个实体的多维度属性。每个 section 输出为 KV 竖排列表：

```
### API基本信息
- java类全名：com.xxx.Service
- java方法名：queryList
- 应用名称：pay-gateway
- Owner：zhangsan
```

若 section 内的 fields 对应的数据为数组（如"入参列表"、"类型信息"），则该 section 输出为 Markdown 表格。

### 通用强制规则

1. **字段完整性**：展示结构中定义的每一个字段/列都必须出现在输出中。接口返回值为空时输出 `—`，不得直接省略该字段
2. **枚举翻译**：如果脚本中 `PARAM_SCHEMA` 或代码注释定义了枚举映射（如 `payState: {"0": "初始化", "1": "支付中"}`），输出时必须翻译为中文含义，不输出原始枚举值
3. **时间格式化**：带 `format` 属性的时间字段，按指定格式输出；接口返回时间戳的，转换为可读时间
4. **额外业务字段**：接口返回了展示结构之外的关键业务字段（如订单号、用户编号、合作方ID等），追加在对应区块末尾以 KV 形式补充展示，不得用表格

## 汇总图规则

当用户的查询意图命中以下任意场景时，**必须在明细表格之后额外输出一张汇总图**，以直观呈现资金走向、数量分布或趋势变化。

### 触发场景映射

| 触发关键词 / 查询意图 | 推荐图类型 | 适用工具示例 |
|---|---|---|
| 资金流、资金走向、资金路径 | 文本资金流向图（缩进箭头格式） | `query_batch_transfer`、`query_payment_voucher`、`query_inoutlog_v3` |
| 出入账、收支汇总、账务汇总 | 文本收支占比列表 | `query_inoutlog_v3`、`query_inoutlog_v1` |
| 对账报表、对账结果、差错诊断 | 文本核对状态分布列表 | `query_reconcile_report_v3`、`query_reconcile_result_v3` |
| 清结算、结算记录、清算汇总 | ASCII 金额横向柱状图 | `query_settlement_record`、`query_inner_merchant` |
| 退款汇总、退款异常统计 | 文本退款状态分布列表 | `query_refund_exception_v2`、`query_refund_order_v3` |
| 会计报表、科目余额、试算 | ASCII 纵向余额柱状图 | `query_fin_report_v2`、`query_trial_balance` |
| 批量转账、转账记录 | 文本转账路径图（缩进箭头格式） | `query_batch_transfer` |
| Top N / 排行 / 额度不足 | ASCII 横向 Top-N 排名图 | `query_quick_increase_quota` |

---

### 图类型规范

#### 1. 资金流向图（文本缩进箭头格式）

适用于展示资金在商户、渠道、备付金账户、银行之间的流转路径。使用纯文本缩进+箭头表示流向，金额标注在每阶段下方。

```
== 资金流转全景图 ==

[用户支付 ¥8.00]
    |
    v
① 支付阶段 (记账码: ZF001)  时间: 2026-03-16 09:54:12
    借: 其他应收账款-机构入款待清算-微信银联1508210161  ¥8.00
    贷: 其他应付账款-结算过渡户-新商户担保户            ¥8.00
    |
    | (担保交易等待确认)
    v
② 结算阶段 (记账码: JS001)  时间: 2026-03-16 10:02:59
    借: 其他应付账款-结算过渡户-新商户担保户            ¥8.00
    贷: 其他应付款-客户余额-店铺余额                    ¥8.00
      -> 商户账户: 260307155534262399
    |
    v
③ 手续费扣款 (记账码: ZZ001)  时间: 2026-03-16 10:02:59
    借: 其他应付款-客户余额-店铺余额                  ¥0.02
    贷: 其他应付款-客户余额-店铺余额 (平台)            ¥0.02
      -> 平台账户: 180709101906000067
```


#### 2. 状态 / 类型占比图（文本百分比列表）

适用于展示对账状态、退款原因、渠道分布等离散类别的比例。用纯文本列表+百分比+进度条呈现。

```
== 对账结果分布 ==

核对一致    ████████████████████  85%  (85笔)
差错待处理  ████                  10%  (10笔)
存疑数据    ██                     5%  (5笔)
```

#### 3. 金额 / 数量柱状图（ASCII）

适用于展示多维度金额对比或批次数量趋势，优先用于数值较多的清结算、会计科目场景。

```
结算金额分布（万元）
渠道A  ██████████████████  180.5
渠道B  ████████████        120.0
渠道C  ██████              60.3
渠道D  ███                 30.1
       └──────────────────────▶
```

#### 4. Top-N 排名图（ASCII）

适用于展示 Top N 店铺/商户排行，每行含排名、名称、核心指标。

```
昨日额度不足 Top 5
#1  店铺A（ID:11111）  缺口 ¥500,000
#2  店铺B（ID:22222）  缺口 ¥320,000
#3  店铺C（ID:33333）  缺口 ¥210,000
#4  店铺D（ID:44444）  缺口 ¥180,000
#5  店铺E（ID:55555）  缺口 ¥90,000
```

---

### 输出顺序

1. 执行工具调用，获取原始数据
2. 输出 **明细 Markdown 表格**（`DISPLAY_COLUMNS` 结构）
3. 输出分隔线 `---`
4. 输出 **汇总图**，并在图上方加标题注释（如 `> 📊 资金流向汇总`）
5. 若数据量不足以作图（如仅1条记录），跳过汇总图，改为输出纯文本摘要一句话。