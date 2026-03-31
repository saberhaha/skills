#!/usr/bin/env python3
"""
Git AI Ratio Analyzer
统计 GitHub 仓库中 AI 生成代码与人工代码的占比

用法：
  python3 analyze.py --token <GITHUB_TOKEN> --org <ORG> --since 2026-03-01 --api-key <KEY>
  python3 analyze.py --token <GITHUB_TOKEN> --org <ORG> --since 2026-03-01 --api-key <KEY> --repos repo1,repo2
"""

import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

import urllib.request
import urllib.error

# ─── 过滤规则：这些文件不参与统计 ───
SKIP_PATTERNS = [
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "go.sum", "Gemfile.lock",
    ".pb.go", "_generated.go", "_gen.go", ".min.js", ".min.css",
    "vendor/", "node_modules/", "__pycache__/", ".idea/", ".vscode/",
    "dist/", "build/", "target/",
]

# 只分析这些扩展名
INCLUDE_EXTENSIONS = {
    ".java", ".go", ".py", ".ts", ".tsx", ".js", ".jsx",
    ".kt", ".swift", ".rs", ".c", ".cpp", ".cs", ".rb", ".php",
    ".scala", ".groovy",
}

MAX_COMMITS_PER_AUTHOR = 50   # 每人每月最多采样数
MAX_DIFF_CHARS = 2000          # 每个 diff 截断长度


# ─── GitHub API ───

def github_get(url, token):
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "git-ai-ratio/1.0",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  [ERROR] GitHub API {url}: {e.code} {e.reason}", file=sys.stderr)
        return None


def get_org_repos(org, token):
    repos, page = [], 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}&type=all"
        data = github_get(url, token)
        if not data:
            break
        repos.extend([r["full_name"] for r in data if not r.get("archived")])
        if len(data) < 100:
            break
        page += 1
    return repos


def get_commits(repo, token, since, until):
    commits, page = [], 1
    while True:
        url = (f"https://api.github.com/repos/{repo}/commits"
               f"?per_page=100&page={page}&since={since}T00:00:00Z&until={until}T23:59:59Z")
        data = github_get(url, token)
        if not data:
            break
        commits.extend(data)
        if len(data) < 100:
            break
        page += 1
    return commits


def get_commit_diff(repo, sha, token):
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "git-ai-ratio/1.0",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


# ─── 过滤 diff ───

def should_skip_file(filename):
    for pat in SKIP_PATTERNS:
        if pat in filename:
            return True
    _, ext = os.path.splitext(filename)
    return ext not in INCLUDE_EXTENSIONS


def filter_diff(raw_diff):
    """只保留业务代码文件的变更行"""
    lines, current_skip = [], True
    for line in raw_diff.split("\n"):
        if line.startswith("diff --git"):
            filename = line.split(" b/")[-1] if " b/" in line else ""
            current_skip = should_skip_file(filename)
        if not current_skip:
            lines.append(line)
    return "\n".join(lines)[:MAX_DIFF_CHARS]


# ─── 大模型打分 ───

def score_with_claude(diff, api_key):
    """用 Claude Haiku 打分，返回 0-100"""
    prompt = (
        "以下是一段代码变更（git diff）。"
        "请判断这段代码更像是 AI 生成还是人工编写。\n"
        "只考虑：代码风格、注释密度、命名习惯、错误处理完整度。\n"
        "返回 JSON，格式：{\"ai_probability\": <0-100>, \"reason\": \"一句话\"}\n"
        "只返回 JSON，不要其他内容。\n\n"
        f"```diff\n{diff}\n```"
    )
    import urllib.request
    payload = json.dumps({
        "model": "claude-haiku-4-5",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            text = result["content"][0]["text"].strip()
            data = json.loads(text)
            return int(data.get("ai_probability", 50))
    except Exception as e:
        print(f"  [WARN] 打分失败: {e}", file=sys.stderr)
        return 50  # 无法判断时返回中间值


# ─── 主流程 ───

def main():
    parser = argparse.ArgumentParser(description="统计 GitHub 仓库 AI 代码占比")
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--org", required=True, help="GitHub Organization 名称")
    parser.add_argument("--since", required=True, help="开始日期 YYYY-MM-DD")
    parser.add_argument("--until", default=datetime.now().strftime("%Y-%m-%d"), help="结束日期 YYYY-MM-DD")
    parser.add_argument("--api-key", required=True, help="Claude API Key")
    parser.add_argument("--repos", default="", help="指定 repo 列表（逗号分隔），不传则扫全 org")
    parser.add_argument("--output", default="ai_ratio_report.csv", help="输出 CSV 文件名")
    args = parser.parse_args()

    print(f"\n🔍 Git AI Ratio Analyzer")
    print(f"   Org: {args.org}  |  {args.since} → {args.until}\n")

    # 1. 获取 repo 列表
    if args.repos:
        repos = [f"{args.org}/{r.strip()}" for r in args.repos.split(",")]
    else:
        print("📦 获取仓库列表...")
        repos = get_org_repos(args.org, args.token)
        print(f"   找到 {len(repos)} 个活跃仓库")

    # 2. 按作者收集 commits
    print("\n📊 收集 commit 列表...")
    author_commits = defaultdict(list)  # author_email -> [(repo, sha, message)]

    for repo in repos:
        commits = get_commits(repo, args.token, args.since, args.until)
        for c in commits:
            author = c.get("commit", {}).get("author", {}).get("email", "unknown")
            sha = c.get("sha", "")
            msg = c.get("commit", {}).get("message", "")[:60]
            author_commits[author].append((repo, sha, msg))
        print(f"   {repo}: {len(commits)} commits")
        time.sleep(0.1)  # rate limit 友好

    print(f"\n   共 {sum(len(v) for v in author_commits.values())} commits，{len(author_commits)} 位作者")

    # 3. 采样 + 打分
    print("\n🤖 大模型打分中...\n")
    results = []  # (author, sampled, scored_commits)

    for author, commits in sorted(author_commits.items()):
        sample = commits if len(commits) <= MAX_COMMITS_PER_AUTHOR else random.sample(commits, MAX_COMMITS_PER_AUTHOR)
        scores = []

        print(f"  👤 {author} ({len(sample)}/{len(commits)} commits)")
        for repo, sha, msg in sample:
            raw_diff = get_commit_diff(repo, sha, args.token)
            diff = filter_diff(raw_diff)
            if not diff.strip():
                continue  # 跳过无业务代码的 commit
            score = score_with_claude(diff, args.api_key)
            scores.append(score)
            print(f"     [{score:3d}] {sha[:8]} {msg[:40]}")
            time.sleep(0.3)  # API rate limit

        if scores:
            avg = sum(scores) / len(scores)
            results.append((author, len(commits), len(scores), avg))

    # 4. 输出报告
    print(f"\n{'─'*60}")
    print(f"{'作者':<35} {'commit总数':>8} {'采样':>6} {'AI占比':>8}")
    print(f"{'─'*60}")

    total_commits, total_weighted = 0, 0.0
    csv_lines = ["author,total_commits,sampled,ai_probability"]

    for author, total, sampled, avg in sorted(results, key=lambda x: -x[3]):
        bar = "█" * int(avg / 10) + "░" * (10 - int(avg / 10))
        print(f"{author:<35} {total:>8} {sampled:>6} {avg:>7.1f}%  {bar}")
        total_commits += total
        total_weighted += avg * total
        csv_lines.append(f"{author},{total},{sampled},{avg:.1f}")

    team_avg = total_weighted / total_commits if total_commits else 0
    print(f"{'─'*60}")
    print(f"{'团队整体':<35} {total_commits:>8} {'':>6} {team_avg:>7.1f}%")

    with open(args.output, "w") as f:
        f.write("\n".join(csv_lines))
    print(f"\n✅ 报告已保存至 {args.output}")


if __name__ == "__main__":
    main()
