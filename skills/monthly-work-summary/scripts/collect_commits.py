#!/usr/bin/env python3
"""收集多个 git 仓库中指定作者、指定时间范围的提交(排除 merge)。

每个仓库作为一个「项目」分组输出,供月度工作总结 skill 归纳。
默认作者取各仓库自身的 user.name / user.email,用 --author 可统一覆盖。

用法:
  python collect_commits.py --repos <repo1> <repo2> --since 2026-06-01 --until 2026-07-01
  python collect_commits.py --repos . --since 2026-06-01 --until 2026-07-01 --author zhangwl
"""

import argparse
import json
import os
import subprocess
import sys


def git(repo, args):
    """在 repo 下执行 git,返回 stdout(失败返回 None)。"""
    try:
        # 强制 git 以 UTF-8 输出日志,避免 Windows 本地化编码导致乱码
        out = subprocess.run(
            ["git", "-C", repo, "-c", "i18n.logOutputEncoding=UTF-8"] + args,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        sys.exit("error: 找不到 git,请确认已安装并在 PATH 中")
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def repo_name(repo):
    """优先用 remote origin 仓库名,否则用文件夹名。"""
    url = git(repo, ["config", "--get", "remote.origin.url"])
    if url:
        name = url.rstrip("/").rsplit("/", 1)[-1]
        if name.endswith(".git"):
            name = name[:-4]
        if name:
            return name
    return os.path.basename(os.path.abspath(repo.rstrip("/\\"))) or repo


def collect(repo, since, until, author):
    """返回某仓库过滤后的 commit subject 列表。author 为 None 时取仓库配置身份。"""
    authors = []
    if author:
        authors = [author]
    else:
        for key in ("user.name", "user.email"):
            v = git(repo, ["config", key])
            if v:
                authors.append(v)

    log_args = [
        "log", "--no-merges",
        f"--since={since}", f"--until={until}",
        "--pretty=format:%H%x1f%ad%x1f%s", "--date=short",
    ]
    for a in authors:
        log_args.append(f"--author={a}")

    out = git(repo, log_args)
    if out is None:
        return None  # 不是 git 仓库或 git 出错

    commits = []
    seen = set()
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        h, date, subject = parts
        subject = subject.strip()
        # 同一文案的重复提交去重(cherry-pick / 重复合并等)
        if subject in seen:
            continue
        seen.add(subject)
        commits.append({"hash": h[:8], "date": date, "subject": subject})
    return commits


def main():
    ap = argparse.ArgumentParser(description="收集 git 提交供月度总结归纳")
    ap.add_argument("--repos", nargs="+", required=True, help="一个或多个仓库路径")
    ap.add_argument("--since", required=True, help="起始日期(含),如 2026-06-01")
    ap.add_argument("--until", required=True, help="截止日期(不含),如 2026-07-01")
    ap.add_argument("--author", default=None, help="统一作者标识(name 或 email);省略则各仓库取自身配置")
    args = ap.parse_args()

    # Windows 控制台默认非 UTF-8,强制 stdout 用 UTF-8 输出中文
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    result = []
    for repo in args.repos:
        if not os.path.isdir(repo):
            print(f"warning: 路径不存在,跳过: {repo}", file=sys.stderr)
            continue
        commits = collect(repo, args.since, args.until, args.author)
        if commits is None:
            print(f"warning: 不是 git 仓库或读取失败,跳过: {repo}", file=sys.stderr)
            continue
        result.append({
            "repo": repo,
            "project": repo_name(repo),
            "count": len(commits),
            "commits": commits,
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
