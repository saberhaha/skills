"""
跨境结算批次查询 (v2)
来源：schemas/账务域/v2_跨境结算.json
"""
import sys
import os
from typing import Optional, Literal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.base_client import client, env_config

BASE_URL = env_config.opcenter_base_url

# 入参 Schema（来源：步骤 1.2 提取的 JSON Schema）
PARAM_SCHEMA = {
    "payeeId": {"type": "string", "required": False, "description": "商户号"},
    "batchId": {"type": "string", "required": False, "description": "结算批次号"},
    "state": {
        "type": "enum", "required": False, "default": 0,
        "enum_values": {
            "0": "待结算", "1": "待审核", "2": "审核通过", "3": "审核驳回",
            "4": "待申报", "5": "结算撤销", "6": "待境外购汇", "7": "待境外汇款",
            "8": "境外汇款处理中", "10": "结算成功", "11": "待订单推送",
            "12": "订单推送失败", "13": "待订单核销", "14": "待ACS汇款",
            "15": "待PIA汇款", "16": "待国际收支申报", "17": "待人民币还原申报",
            "99": "结算失败", "@all": "全部"
        },
        "description": "结算状态（默认0=待结算，'@all'=全部时不传此字段）"
    },
    "batchDate": {
        "type": "string", "format": "YYYYMMDD",
        "required": False, "description": "结算日期"
    },
    "page": {"type": "number", "required": False, "default": 1, "description": "页码"},
    "pageSize": {"type": "number", "required": False, "default": 10, "description": "每页条数"}
}

# 数据展示列（来源：步骤 1.2 提取的前端 columns）
DISPLAY_COLUMNS = [
    {"title": "结算批次号", "dataIndex": "batchId"},
    {"title": "结算商家商户号", "dataIndex": "payeeId"},
    {"title": "境外收款人名称", "dataIndex": "payeeAccountName"},
    {"title": "境外收款人账号", "dataIndex": "payeeAccountNo"},
    {"title": "境外收款人开户名称", "dataIndex": "payeeBankName"},
    {"title": "本次结算金额（元）", "dataIndex": "settleAmt"},
    {"title": "预留店铺余额（元）", "dataIndex": "reservedAmount"},
    {"title": "结算状态", "dataIndex": "state"},
    {"title": "实际结算金额（元）", "dataIndex": "realSettleAmt"},
    {"title": "结算手续费（元）", "dataIndex": "feeAmt"},
    {"title": "打款金额（元）", "dataIndex": "remitAmt"},
    {"title": "提现币种", "dataIndex": "currency"},
    {"title": "结算账户", "dataIndex": "settleAccountType"},
    {"title": "现汇卖出价", "dataIndex": "exchangeRate"},
    {"title": "结算渠道", "dataIndex": "settleChannel"},
    {"title": "买入外币金额（元）", "dataIndex": "incomeAmount"},
    {"title": "结算操作人", "dataIndex": "applyOperName"},
    {"title": "结算操作时间", "dataIndex": "applyOperAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "复合操作人", "dataIndex": "reviewOperName"},
    {"title": "结算完成时间", "dataIndex": "finishedAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "更新时间", "dataIndex": "updatedAt", "format": "YYYY-MM-DD HH:mm:ss"},
    {"title": "驳回原因", "dataIndex": "rejectReason"}
]


def execute(
    payee_id: Optional[str] = None,
    batch_id: Optional[str] = None,
    state: str = "0",
    batch_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """跨境结算批次查询（v2）
    查询跨境结算批次列表，支持按商户号、批次号、状态和结算日期查询。
    默认查询 state=0（待结算）状态的批次。

    Args:
        payee_id: 商户号。可选。
        batch_id: 结算批次号。可选。
        state: 结算状态。默认 "0"=待结算。传 "@all" 则不传此字段查全部。
        batch_date: 结算日期。可选。格式 YYYYMMDD（如 "20260313"）。
        page: 页码。默认 1。
        page_size: 每页条数。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.customs.declaration.settle.batch.query"

    payload = {
        "page": page,
        "pageSize": page_size
    }
    if payee_id:
        payload["payeeId"] = payee_id
    if batch_id:
        payload["batchId"] = batch_id
    # '@all' 时不传 state 字段
    if state != "@all":
        payload["state"] = state
    if batch_date:
        payload["batchDate"] = batch_date

    return client.post(url, payload)


def get_settle_details(
    batch_id: str,
    page: int = 1,
    page_size: Optional[int] = None,
) -> dict:
    """查询结算批次明细列表（辅助查询）
    详情弹窗中展示某批次下的结算明细列表。

    Args:
        batch_id: 结算批次号。必填。
        page: 页码。默认 1。
        page_size: 每页条数。可选。
    """
    url = f"{BASE_URL}/dispatcher/pay.customs.declaration.settle.batch.querySettleDetails"
    payload = {
        "batchId": batch_id,
        "page": page
    }
    if page_size is not None:
        payload["pageSize"] = page_size
    return client.post(url, payload)


def get_merchant_page(
    payee_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """跨境商户分页查询（辅助查询）
    查询跨境结算商户配置记录列表。

    Args:
        payee_id: 商户号。可选。
        page: 页码。默认 1。
        page_size: 每页条数。默认 20。
    """
    url = f"{BASE_URL}/dispatcher/pay.customs.declaration.settle.merchant.pageQuery"
    payload = {
        "page": page,
        "pageSize": page_size
    }
    if payee_id:
        payload["payeeId"] = payee_id
    return client.post(url, payload)


def get_merchant_single(
    payee_id: str,
) -> dict:
    """跨境商户单笔查询（辅助查询）
    根据商户号查询单个商户的跨境结算配置信息（如 kdtId）。

    Args:
        payee_id: 商户号。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.customs.declaration.settle.merchant.query"
    payload = {"payeeId": payee_id}
    return client.post(url, payload)


def get_remit_account_info(
    state: int = 1,
    remit_account_currency: Optional[str] = None,
    remit_account_type: Optional[int] = None,
) -> dict:
    """跨境购汇账户信息查询（辅助查询）
    建行打款操作时查询可用的购汇账户列表。

    Args:
        state: 账户状态。默认 1。
        remit_account_currency: 购汇货币。可选（state=2 时传 'CNY'）。
        remit_account_type: 账户类型。可选（state=2 时传 1）。
    """
    url = f"{BASE_URL}/dispatcher/pay.customs.declaration.settle.queryRemitAccountInfo"
    payload = {"state": state}
    if remit_account_currency:
        payload["remitAccountCurrency"] = remit_account_currency
    if remit_account_type is not None:
        payload["remitAccountType"] = remit_account_type
    return client.post(url, payload)


def get_voucher(
    batch_id: str,
) -> dict:
    """购汇凭证查询（辅助查询）
    香港转账场景（state=7）时查询购汇凭证信息。

    Args:
        batch_id: 结算批次号。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.customs.declaration.settle.queryVoucher"
    payload = {"batchId": batch_id}
    return client.post(url, payload)


def get_user_no_by_kdt_id(
    kdt_id: str,
) -> dict:
    """通过店铺id查询商户号（辅助查询）
    根据店铺 id 获取商户 payeeId。

    Args:
        kdt_id: 店铺ID。直接作为 data 传入。必填。
    """
    url = f"{BASE_URL}/dispatcher/pay.fullInfo.getUserNoByKdtId"
    return client.post(url, kdt_id)


def get_principal_msg(
    source_id: str,
    source_id_type: str = "KDT_ID",
    unified_cert_type: str = "PRINCIPAL",
) -> dict:
    """查询商户主体信息（辅助查询）
    商户注册/修改时查询境外主体名称。

    Args:
        source_id: 来源ID（如 kdtId）。必填。
        source_id_type: 来源ID类型。固定传 'KDT_ID'。默认 'KDT_ID'。
        unified_cert_type: 证书类型。固定传 'PRINCIPAL'。默认 'PRINCIPAL'。
    """
    url = f"{BASE_URL}/dispatcher/pay.ucert.queryPrincipalMsg"
    payload = {
        "sourceId": source_id,
        "sourceIdType": source_id_type,
        "unifiedCertType": unified_cert_type
    }
    return client.post(url, payload)


def get_valid_and_changing_cert(
    source_id: str,
    source_id_type: str = "KDT_ID",
) -> dict:
    """查询有效及变更中的证书（辅助查询）
    查询商户跨境贸易证书中的境外主体公司名称。

    Args:
        source_id: 来源ID（如 kdtId）。必填。
        source_id_type: 来源ID类型。固定传 'KDT_ID'。默认 'KDT_ID'。
    """
    url = f"{BASE_URL}/dispatcher/pay.ucert.queryValidAndChangingCert"
    payload = {
        "sourceId": source_id,
        "sourceIdType": source_id_type
    }
    return client.post(url, payload)


def get_acct_info(
    user_no: str,
    acct_type: int = 10,
) -> dict:
    """查询账户余额（辅助查询）
    申请结算前查询商户当前账户可用余额。

    Args:
        user_no: 商户号（payeeId）。必填。
        acct_type: 账户类型。固定传 10。默认 10。
    """
    url = f"{BASE_URL}/dispatcher/pay.acctrans.account.getAcctInfo"
    payload = {
        "userNo": user_no,
        "acctType": acct_type
    }
    return client.post(url, payload)
