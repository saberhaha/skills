#!/usr/bin/env bash
set -euo pipefail

INTERFACE=""
METHOD=""
SC=""
DATA=""
ENV="qa"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --interface) INTERFACE="${2:-}"; shift 2 ;;
    --method)    METHOD="${2:-}"; shift 2 ;;
    --sc)        SC="${2:-}"; shift 2 ;;
    --data)      DATA="${2:-}"; shift 2 ;;
    --env)       ENV="${2:-}"; shift 2 ;;
    -h|--help)
      echo "用法: dubbo_invoke.sh --interface <fqn> --method <method> --data '<json-array>' [--env qa|pre|prod] [--sc <prjxxx>]"
      exit 0 ;;
    *) echo "不支持的参数: $1" >&2; exit 2 ;;
  esac
done

[[ -z "$INTERFACE" ]] && { echo "缺少 --interface" >&2; exit 2; }
[[ -z "$METHOD" ]]    && { echo "缺少 --method" >&2; exit 2; }
[[ -z "$DATA" ]]      && { echo "缺少 --data" >&2; exit 2; }
[[ "${DATA:0:1}" != "[" ]] && { echo "--data 必须是 JSON 数组（以 [ 开头）" >&2; exit 2; }

case "$ENV" in
  qa)   GATEWAY="http://tether-qa.s.fin.qima-inc.com:8680/soa" ;;
  pre)  GATEWAY="http://tether-pre.s.fin.qima-inc.com:8680/soa" ;;
  prod) GATEWAY="http://tether.s.fin.qima-inc.com:8680/soa" ;;
  *)    echo "不支持的环境: $ENV（可选: qa, pre, prod）" >&2; exit 2 ;;
esac

# 构造 curl 命令
CURL_STR="curl --location --request POST '${GATEWAY}/${INTERFACE}/${METHOD}' \\
  --header 'X-Request-Protocol: dubbo' \\
  --header 'Content-Type: application/json'"

[[ -n "$SC" ]] && CURL_STR="${CURL_STR} \\
  --header 'X-Service-Chain: {\"name\": \"${SC}\"}'"

CURL_STR="${CURL_STR} \\
  --data '${DATA}'"

if [[ "$ENV" == "qa" ]]; then
  # QA 环境直接执行
  eval "$CURL_STR"
else
  # pre/prod 环境仅输出 curl 命令
  echo "⚠️  ${ENV} 环境因网络隔离无法本地调用，请到对应环境的容器或跳板机上执行以下命令："
  echo ""
  echo "$CURL_STR"
fi
