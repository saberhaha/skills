#!/usr/bin/env bash

set -u

ENDPOINT="${REPORT_USAGE_ENDPOINT:-https://zode.qa.qima-inc.com/api/skill/report-usage}"
SKILL_NAME="${1:-}"
CALL_COUNT="${2:-1}"

if [ -z "${SKILL_NAME}" ]; then
  echo "Usage: bash scripts/report-usage.sh <skill-name> [call-count]" >&2
  exit 1
fi

detect_call_source() {
  if [ -n "${CURSOR_TRACE_ID:-}" ] || [ -n "${CURSOR_AGENT:-}" ] || [ -n "${CURSOR_SESSION_ID:-}" ]; then
    echo "cursor"
    return
  fi

  if [ -n "${CLAUDECODE:-}" ] || [ -n "${CLAUDE_CODE_ENTRYPOINT:-}" ] || [ -n "${CLAUDE_SESSION_ID:-}" ]; then
    echo "claude-code"
    return
  fi

  if [ -n "${CODEX_HOME:-}" ] || [ -n "${CODEX_ENV:-}" ] || [ -n "${OPENAI_CODEX_ENV:-}" ]; then
    echo "codex"
    return
  fi

  echo "unknown"
}

extract_git_owner_from_remote() {
  local remote_url path owner
  remote_url="$(git remote get-url origin 2>/dev/null || true)"
  [ -z "${remote_url}" ] && return 1

  case "${remote_url}" in
    git@*:* )
      path="${remote_url#*:}"
      ;;
    http://*|https://* )
      path="${remote_url#*://}"
      path="${path#*/}"
      ;;
    * )
      path="${remote_url}"
      ;;
  esac

  path="${path%.git}"
  owner="${path%%/*}"
  [ -n "${owner}" ] || return 1
  echo "${owner}"
}

detect_git_username() {
  if [ -n "${REPORT_GIT_USERNAME:-}" ]; then
    echo "${REPORT_GIT_USERNAME}"
    return
  fi

  if [ -n "${GITLAB_USER_LOGIN:-}" ]; then
    echo "${GITLAB_USER_LOGIN}"
    return
  fi

  if [ -n "${GITLAB_USERNAME:-}" ]; then
    echo "${GITLAB_USERNAME}"
    return
  fi

  local email user
  email="$(git config --get user.email 2>/dev/null || true)"
  if [ -n "${email}" ]; then
    user="${email%@*}"
    if [ -n "${user}" ]; then
      echo "${user}"
      return
    fi
  fi

  user="$(git config --get user.name 2>/dev/null || true)"
  if [ -n "${user}" ]; then
    echo "${user}"
    return
  fi

  local owner
  owner="$(extract_git_owner_from_remote 2>/dev/null || true)"
  if [ -n "${owner}" ]; then
    echo "${owner}"
    return
  fi

  echo "unknown"
}

CALL_SOURCE="$(detect_call_source)"
GIT_USERNAME="$(detect_git_username)"
CALLED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

if ! [[ "${CALL_COUNT}" =~ ^[0-9]+$ ]]; then
  CALL_COUNT="1"
fi

read -r -d '' PAYLOAD <<EOF || true
{
  "callSource": "${CALL_SOURCE}",
  "gitUsername": "${GIT_USERNAME}",
  "events": [
    {
      "skillName": "${SKILL_NAME}",
      "callCount": ${CALL_COUNT},
      "calledAt": "${CALLED_AT}"
    }
  ]
}
EOF

if curl --silent --show-error --fail \
  --location "${ENDPOINT}" \
  --header 'Content-Type: application/json' \
  --data "${PAYLOAD}" >/dev/null; then
  echo "[report-usage] reported: skill=${SKILL_NAME}, source=${CALL_SOURCE}, gitUsername=${GIT_USERNAME}"
  exit 0
fi

echo "[report-usage] warning: failed to report usage to ${ENDPOINT}" >&2
exit 0
