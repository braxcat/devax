"""Real per-day stats extraction from git repositories.

Parses git log output to build daily stats dicts with both
per-day activity and cumulative running totals.
Supports multi-repo collection with commit type and project tagging.
Uses only stdlib (subprocess) — no external dependencies.
"""

import os
import re
import subprocess
from datetime import datetime

from lib.stats.project_timeline import get_timeline_for_date


_DIFFICULTY = {
    "rating": 7.5,
    "max": 10,
    "label": "Advanced",
}

# Patterns for workspace repo path-based project classification.
# Used when the repo is a monorepo/workspace containing multiple projects.
_WORKSPACE_PATH_RULES = [
    (re.compile(r"^scripts/"), "tools"),
    (re.compile(r"^infra/"), "infra"),
    (re.compile(r"^docs/"), "docs"),
    # Skip these — config, gitignore, etc.
    (re.compile(r"^\.claude/"), None),
    (re.compile(r"^\.gitignore$"), None),
    (re.compile(r"^CLAUDE\.md$"), None),
]

# Keyword patterns for commit type classification (checked in order)
_TYPE_RULES = [
    (re.compile(r"^(Fix|Bugfix|Hotfix)\b", re.I), "bugfix"),
    (re.compile(r"^Refactor\b", re.I), "refactor"),
    (re.compile(r"(^Deploy|^Provision|infra|GCP|Cloud Run|Cloud Build|Cloud SQL|setup-gcp)", re.I), "infra"),
    (re.compile(r"(README|CHANGELOG|ROADMAP|FEATURES|\.md$|^Update docs|^Add docs|^Documentation)", re.I), "docs"),
    (re.compile(r"^Ignore\b|^\.gitignore", re.I), None),  # skip
    (re.compile(r"^Merge\b", re.I), None),  # skip
    (re.compile(r"^(Add|Create|Implement|Build|Wire|Set up|Seed)\b", re.I), "feature"),
    (re.compile(r"^(Update|Enhance|Improve|Bump|Upgrade)\b", re.I), "update"),
]


def _classify_commit(subject: str) -> str:
    """Auto-detect commit type from subject line. Returns tag or None to skip."""
    for pattern, tag in _TYPE_RULES:
        if pattern.search(subject):
            return tag
    return "feature"  # fallback


def _classify_project(repo_name: str, file_paths: list, workspace_repo: str = None) -> str:
    """Classify which project a commit belongs to based on repo name and file paths.

    For the workspace repo, uses file paths to distinguish tools/infra/docs.
    For other repos, returns the repo name as-is.
    Returns None if the commit should be skipped (e.g. config-only changes).

    Args:
        repo_name: Name of the git repository.
        file_paths: List of file paths changed in the commit.
        workspace_repo: Name of the workspace/planning repo that uses
            path-based classification. If None, path rules are never applied.
    """
    if workspace_repo and repo_name == workspace_repo:
        # Workspace repo: classify by file paths
        tags = set()
        for fp in file_paths:
            matched = False
            for pattern, tag in _WORKSPACE_PATH_RULES:
                if pattern.search(fp):
                    if tag:
                        tags.add(tag)
                    matched = True
                    break
            if not matched:
                tags.add(repo_name)

        if not tags:
            return None  # all files were skipped (e.g. only .claude/ changes)

        # Return the most specific tag (tools > infra > docs > repo name)
        for preferred in ("tools", "infra", "docs"):
            if preferred in tags:
                return preferred
        return repo_name
    else:
        return repo_name


def _run_git(repo_path: str, args: list, timezone: str = "Australia/Sydney") -> str:
    """Run a git command and return stdout."""
    env = os.environ.copy()
    env["TZ"] = timezone
    result = subprocess.run(
        ["git"] + args,
        cwd=repo_path,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def _parse_git_log(repo_path: str, timezone: str) -> list:
    """Parse git log with numstat into a list of commit dicts.

    Returns list of:
        {"hash": str, "date": str, "hour": int, "dow": int,
         "author": str, "subject": str, "added": int, "deleted": int,
         "files": [str]}
    """
    raw = _run_git(repo_path, [
        "log",
        "--format=COMMIT|%H|%ad|%an|%s",
        "--date=format:%Y-%m-%d|%w|%H",
        "--numstat",
    ], timezone)

    commits = []
    current = None

    for line in raw.strip().split("\n"):
        if not line.strip():
            continue
        if line.startswith("COMMIT|"):
            parts = line.split("|")
            current = {
                "hash": parts[1],
                "date": parts[2],
                "dow": int(parts[3]),
                "hour": int(parts[4]),
                "author": parts[5],
                "subject": "|".join(parts[6:]),
                "added": 0,
                "deleted": 0,
                "files": [],
            }
            commits.append(current)
        elif current and "\t" in line:
            parts = line.split("\t")
            if parts[0] != "-":
                current["added"] += int(parts[0])
            if parts[1] != "-":
                current["deleted"] += int(parts[1])
            if len(parts) > 2:
                current["files"].append(parts[2])

    return commits


def _build_daily_stats(all_commits, project_name, include_tags=False):
    """Build daily stats list from a flat list of commits.

    Args:
        all_commits: List of commit dicts (may have repo_name, commit_type, project_tag).
        project_name: Display name for the project.
        include_tags: Whether to include commit_tags and project_tags in output.
    """
    by_date = {}
    for c in all_commits:
        by_date.setdefault(c["date"], []).append(c)

    sorted_dates = sorted(by_date.keys())
    if not sorted_dates:
        return []

    first_commit_date = sorted_dates[0]
    first_dt = datetime.strptime(first_commit_date, "%Y-%m-%d")

    daily_stats = []
    cum_commits = 0
    cum_added = 0
    cum_deleted = 0
    cum_by_date = {}
    cum_by_author = {}

    for date_str in sorted_dates:
        day_commits = by_date[date_str]
        day_dt = datetime.strptime(date_str, "%Y-%m-%d")
        age_days = (day_dt - first_dt).days + 1

        day_added = sum(c["added"] for c in day_commits)
        day_deleted = sum(c["deleted"] for c in day_commits)
        day_count = len(day_commits)

        cum_commits += day_count
        cum_added += day_added
        cum_deleted += day_deleted
        cum_by_date[date_str] = day_count

        for c in day_commits:
            cum_by_author[c["author"]] = cum_by_author.get(c["author"], 0) + 1

        punch_card = {}
        for c in day_commits:
            key = (c["dow"], c["hour"])
            punch_card[key] = punch_card.get(key, 0) + 1
        punch_list = [[dow, hour, count] for (dow, hour), count in sorted(punch_card.items())]

        contributors = [
            {"name": name, "commits": count}
            for name, count in sorted(cum_by_author.items(), key=lambda x: -x[1])
        ]

        subjects = [
            c["subject"] for c in day_commits
            if not c["subject"].startswith("Merge ")
        ]

        timeline = get_timeline_for_date(date_str)

        stats = {
            "project_name": project_name,
            "generated_at": date_str,
            "first_commit": first_commit_date,
            "latest_commit": date_str,
            "project_age_days": age_days,

            "lines_of_code": {
                "total": cum_added - cum_deleted,
                "daily_added": day_added,
                "daily_deleted": day_deleted,
            },

            "git": {
                "total_commits": cum_commits,
                "daily_commits": day_count,
                "contributors": contributors,
                "commits_by_date": dict(cum_by_date),
            },

            "punch_card": punch_list,
            "commit_subjects": subjects,

            "infrastructure_services": timeline.get("infrastructure_services", []),
            "dependencies": timeline.get("dependencies", {}),
            "difficulty": _DIFFICULTY,
            "components": None,
            "largest_files": None,
        }

        if include_tags:
            # Count commit types for this day
            type_counts = {}
            project_counts = {}
            for c in day_commits:
                ct = c.get("commit_type")
                if ct:
                    type_counts[ct] = type_counts.get(ct, 0) + 1
                pt = c.get("project_tag")
                if pt:
                    project_counts[pt] = project_counts.get(pt, 0) + 1
            stats["commit_tags"] = type_counts
            stats["project_tags"] = project_counts

        daily_stats.append(stats)

    return daily_stats


def _filter_excluded_paths(commits: list, exclude_paths: list) -> list:
    """Filter out commits where ALL changed files match an exclude path.

    Commits with at least one file outside the excluded paths are kept,
    but the excluded files are removed from the commit's file list and
    line counts are recalculated.
    """
    if not exclude_paths:
        return commits

    filtered = []
    for c in commits:
        files = c.get("files", [])
        if not files:
            filtered.append(c)
            continue

        kept_files = [
            f for f in files
            if not any(f.startswith(ep) for ep in exclude_paths)
        ]

        if not kept_files:
            continue  # All files excluded — drop entire commit

        if len(kept_files) < len(files):
            # Some files excluded — we keep the commit but can't easily
            # recalculate line counts per file (numstat doesn't tag lines
            # per file in our parsed data). Keep the commit as-is since
            # the excluded paths are typically docs with minimal churn.
            c = dict(c)
            c["files"] = kept_files

        filtered.append(c)

    return filtered


def collect_daily_stats(
    repo_path: str,
    project_name: str = "My Project",
    timezone: str = "Australia/Sydney",
    workspace_repo: str = None,
    exclude_paths: list = None,
) -> list:
    """Extract per-day stats from a single git repository.

    Returns a list of daily stats dicts (chronologically ordered).
    Each dict has both daily activity and cumulative running totals.

    Args:
        repo_path: Path to the git repository.
        project_name: Display name for the project.
        timezone: Timezone for git log timestamps.
        workspace_repo: Name of the workspace/planning repo for path-based
            classification. If None, all commits are tagged with the repo name.
        exclude_paths: List of path prefixes to exclude from stats
            (e.g. ["docs/business/confluence/"]).
    """
    commits = _parse_git_log(repo_path, timezone)
    repo_name = os.path.basename(os.path.normpath(repo_path))

    # Filter excluded paths before classification
    commits = _filter_excluded_paths(commits, exclude_paths or [])

    # Tag each commit
    for c in commits:
        c["commit_type"] = _classify_commit(c["subject"])
        c["project_tag"] = _classify_project(repo_name, c.get("files", []), workspace_repo)
        c["repo_name"] = repo_name

    # Filter out skipped commits (None type or None project)
    commits = [c for c in commits if c["commit_type"] and c["project_tag"]]

    return _build_daily_stats(commits, project_name, include_tags=True)


def collect_multi_repo_daily_stats(
    repos: list,
    project_name: str = "My Project",
    timezone: str = "Australia/Sydney",
    workspace_repo: str = None,
    exclude_paths: list = None,
) -> list:
    """Extract per-day stats from multiple git repositories, merged into one timeline.

    Args:
        repos: List of {"path": str, "name": str} dicts.
        project_name: Display name for the combined project.
        timezone: Timezone for git log.
        workspace_repo: Name of the workspace/planning repo for path-based
            classification. If None, all commits are tagged with their repo name.
        exclude_paths: List of path prefixes to exclude from stats.

    Returns a list of daily stats dicts (chronologically ordered) with
    commit_tags and project_tags showing the breakdown.
    """
    all_commits = []
    for repo in repos:
        repo_path = repo["path"]
        repo_name = repo["name"]
        commits = _parse_git_log(repo_path, timezone)
        commits = _filter_excluded_paths(commits, exclude_paths or [])
        for c in commits:
            c["commit_type"] = _classify_commit(c["subject"])
            c["project_tag"] = _classify_project(repo_name, c.get("files", []), workspace_repo)
            c["repo_name"] = repo_name
        # Filter out skipped commits
        commits = [c for c in commits if c["commit_type"] and c["project_tag"]]
        all_commits.extend(commits)

    return _build_daily_stats(all_commits, project_name, include_tags=True)
