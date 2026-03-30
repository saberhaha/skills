#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用数据上报脚本"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ENDPOINT = os.environ.get("REPORT_USAGE_ENDPOINT", "https://zode.qa.qima-inc.com/api/skill/report-usage")


def detect_call_source():
    """检测调用来源"""
    if any(os.environ.get(k) for k in ("CURSOR_TRACE_ID", "CURSOR_AGENT", "CURSOR_SESSION_ID")):
        return "cursor"
    if any(os.environ.get(k) for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_SESSION_ID")):
        return "claude-code"
    if any(os.environ.get(k) for k in ("CODEX_HOME", "CODEX_ENV", "OPENAI_CODEX_ENV")):
        return "codex"
    return "unknown"


def run_git(args):
    """执行 git 命令并返回输出"""
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def detect_git_username():
    """检测 git 用户名"""
    for env_key in ("REPORT_GIT_USERNAME", "GITLAB_USER_LOGIN", "GITLAB_USERNAME"):
        val = os.environ.get(env_key, "")
        if val:
            return val

    email = run_git(["config", "--get", "user.email"])
    if email and "@" in email:
        return email.split("@")[0]

    name = run_git(["config", "--get", "user.name"])
    if name:
        return name

    remote_url = run_git(["remote", "get-url", "origin"])
    if remote_url:
        if remote_url.startswith("git@") and ":" in remote_url:
            path = remote_url.split(":", 1)[1]
        elif remote_url.startswith(("http://", "https://")):
            path = "/".join(remote_url.split("/")[3:])
        else:
            path = remote_url
        path = path.rstrip(".git")
        owner = path.split("/")[0] if "/" in path else path
        if owner:
            return owner

    return "unknown"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/report-usage.py <skill-name> [call-count]", file=sys.stderr)
        sys.exit(1)

    skill_name = sys.argv[1]
    call_count = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 1

    call_source = detect_call_source()
    git_username = detect_git_username()
    called_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = json.dumps({
        "callSource": call_source,
        "gitUsername": git_username,
        "events": [{
            "skillName": skill_name,
            "callCount": call_count,
            "calledAt": called_at
        }]
    })

    try:
        result = subprocess.run(
            ["curl", "--silent", "--show-error", "--fail", "--location",
             ENDPOINT, "--header", "Content-Type: application/json", "--data", payload],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("[report-usage] reported: skill=%s, source=%s, gitUsername=%s" % (skill_name, call_source, git_username))
            sys.exit(0)
    except Exception:
        pass

    print("[report-usage] warning: failed to report usage to %s" % ENDPOINT, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
