#!/usr/bin/env python3
"""
Dev Updates — Post project progress to Slack from markdown files.

Usage:
  python3 dev_updates.py roadmap [--dry-run]      Post roadmap progress
  python3 dev_updates.py release [--dry-run]       Post latest release
  python3 dev_updates.py changelog [--dry-run]     Post latest changelog
  python3 dev_updates.py stats [--dry-run]         Post coding stats
  python3 dev_updates.py confluence [--dry-run]    Post Confluence sync status
  python3 dev_updates.py all [--dry-run]           Post all (incl. confluence if configured)
  python3 dev_updates.py replay [--dry-run]        Post full history (all phases)
  python3 dev_updates.py delete-last N             Delete last N bot messages
  python3 dev_updates.py setup-channels            Create channels (one-time)

Options:
  --dry-run         Print Block Kit JSON, don't post
  --repo PATH       Path to repo (overrides config)
  --project NAME    Project display name (overrides config)
  --config PATH     Config file path (default: ./config.json)
  --json            Output parsed data as JSON (no Slack formatting)
  --type TYPE       For replay: roadmap, release, changelog, stats (default: all)
  --channel NAME    For delete-last: channel name (e.g. dev-roadmap)
  --no-charts       Skip chart generation for stats
"""

import argparse
import json
import os
import sys
import time

# Add parent to path for lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.parsers import parse_roadmap, parse_roadmap_snapshots, parse_changelog, parse_features, parse_confluence_status
from lib.formatters import build_roadmap_blocks, build_release_blocks, build_changelog_blocks, build_confluence_blocks
from lib.slack_client import _get_token, ensure_channels, post_message, delete_bot_messages, delete_all_bot_messages
from lib.stats.git_collector import collect_daily_stats, collect_multi_repo_daily_stats
from lib.stats.charts import build_all_charts, build_daily_charts
from lib.stats.formatter import build_slack_blocks, build_daily_slack_blocks
from lib.stats.estimator import estimate_dev_time


def load_config(config_path):
    """Load config from JSON file. Returns empty dict if not found."""
    if config_path and os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}


def get_repo_path(args, config):
    """Resolve first repo path from args > config > error."""
    repos = args.repo or []
    repo = repos[0] if repos else config.get("repo_path")
    if not repo:
        print("Error: --repo PATH required (or set repo_path in config.json)")
        sys.exit(1)
    repo = os.path.expanduser(repo)
    if not os.path.isdir(repo):
        print(f"Error: repo path not found: {repo}")
        sys.exit(1)
    return repo


def get_repo_list(args, config):
    """Resolve list of repos for multi-repo stats. Returns list of {path, name} dicts."""
    repos = args.repo or []
    if not repos:
        single = config.get("repo_path")
        if single:
            repos = [single]
    if not repos:
        print("Error: --repo PATH required (or set repo_path in config.json)")
        sys.exit(1)
    result = []
    for r in repos:
        r = os.path.expanduser(r)
        if not os.path.isdir(r):
            print(f"Error: repo path not found: {r}")
            sys.exit(1)
        name = os.path.basename(os.path.normpath(r))
        result.append({"path": r, "name": name})
    return result


def get_project_name(args, config):
    """Resolve project name from args > config > fallback."""
    return args.project or config.get("project_name", "Project")


def get_channel_names(config):
    """Get channel names from config or defaults."""
    channels = config.get("channels", {})
    result = {
        "roadmap": channels.get("roadmap", "dev-roadmap"),
        "releases": channels.get("releases", "dev-releases"),
        "changelog": channels.get("changelog", "dev-changelog"),
        "stats": channels.get("stats", "coding-stats"),
    }
    if "confluence" in channels:
        result["confluence"] = channels["confluence"]
    return result


def cmd_roadmap(args, config):
    repo = get_repo_path(args, config)
    project = get_project_name(args, config)
    docs_path = config.get("docs_path", "claude_docs")
    data = parse_roadmap(repo, docs_path=docs_path)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    blocks = build_roadmap_blocks(data, project)

    if args.dry_run:
        print(json.dumps(blocks, indent=2))
        print(f"\n--- Would post to #{get_channel_names(config)['roadmap']} ---")
        return

    token = _get_token()
    ch_names = get_channel_names(config)
    channels = ensure_channels(token, [ch_names["roadmap"]])
    ch_id = channels[ch_names["roadmap"]]
    post_message(token, ch_id, blocks, text=f"{project} Roadmap Progress")
    print(f"Posted roadmap to #{ch_names['roadmap']}")


def cmd_release(args, config):
    repo = get_repo_path(args, config)
    project = get_project_name(args, config)
    docs_path = config.get("docs_path", "claude_docs")
    changelog_data = parse_changelog(repo, latest_only=True, docs_path=docs_path)

    features_data = None
    try:
        features_data = parse_features(repo, docs_path=docs_path)
    except FileNotFoundError:
        pass

    if args.json:
        out = {"changelog": changelog_data}
        if features_data:
            out["features"] = features_data
        print(json.dumps(out, indent=2))
        return

    blocks = build_release_blocks(changelog_data, project, features_data, context=args.context)

    if args.dry_run:
        print(json.dumps(blocks, indent=2))
        print(f"\n--- Would post to #{get_channel_names(config)['releases']} ---")
        return

    token = _get_token()
    ch_names = get_channel_names(config)
    channels = ensure_channels(token, [ch_names["releases"]])
    ch_id = channels[ch_names["releases"]]
    post_message(token, ch_id, blocks, text=f"{project} Release")
    print(f"Posted release to #{ch_names['releases']}")


def cmd_changelog(args, config):
    repo = get_repo_path(args, config)
    project = get_project_name(args, config)
    docs_path = config.get("docs_path", "claude_docs")
    data = parse_changelog(repo, docs_path=docs_path)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    blocks = build_changelog_blocks(data, project, context=args.context)

    if args.dry_run:
        print(json.dumps(blocks, indent=2))
        print(f"\n--- Would post to #{get_channel_names(config)['changelog']} ---")
        return

    token = _get_token()
    ch_names = get_channel_names(config)
    channels = ensure_channels(token, [ch_names["changelog"]])
    ch_id = channels[ch_names["changelog"]]
    post_message(token, ch_id, blocks, text=f"{project} Changelog")
    print(f"Posted changelog to #{ch_names['changelog']}")


def cmd_stats(args, config):
    """Post coding stats to #coding-stats."""
    repos = get_repo_list(args, config)
    project = get_project_name(args, config)
    ch_names = get_channel_names(config)
    no_charts = getattr(args, "no_charts", False)
    exclude_paths = config.get("stats_exclude_paths", [])

    if len(repos) > 1:
        daily = collect_multi_repo_daily_stats(repos, project, exclude_paths=exclude_paths)
    else:
        daily = collect_daily_stats(repos[0]["path"], project, exclude_paths=exclude_paths)
    if not daily:
        print("No git history found")
        return

    stats = daily[-1]  # Latest day (cumulative snapshot)

    if args.json:
        print(json.dumps(stats, indent=2, default=str))
        return

    chart_urls = build_daily_charts(stats) if not no_charts else {}
    prev = daily[-2] if len(daily) > 1 else None
    blocks = build_daily_slack_blocks(stats, len(daily), len(daily), chart_urls, prev)

    if args.dry_run:
        print(json.dumps(blocks, indent=2))
        print(f"\n--- Would post to #{ch_names['stats']} ---")
        return

    token = _get_token()
    channels = ensure_channels(token, [ch_names["stats"]])
    ch_id = channels[ch_names["stats"]]
    post_message(token, ch_id, blocks, text=f"{project} Coding Stats")
    print(f"Posted stats to #{ch_names['stats']}")


def cmd_confluence(args, config):
    """Post Confluence sync status."""
    repo = get_repo_path(args, config)
    project = get_project_name(args, config)
    ch_names = get_channel_names(config)

    if "confluence" not in ch_names:
        print("No confluence channel configured — skipping")
        return

    data = parse_confluence_status(repo)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    blocks = build_confluence_blocks(data, project, context=args.context)

    if args.dry_run:
        print(json.dumps(blocks, indent=2))
        print(f"\n--- Would post to #{ch_names['confluence']} ---")
        return

    token = _get_token()
    channels = ensure_channels(token, [ch_names["confluence"]])
    ch_id = channels[ch_names["confluence"]]
    post_message(token, ch_id, blocks, text=f"{project} Confluence Status")
    print(f"Posted confluence status to #{ch_names['confluence']}")


def cmd_all(args, config):
    steps = [
        ("Roadmap", cmd_roadmap),
        ("Release", cmd_release),
        ("Changelog", cmd_changelog),
        ("Stats", cmd_stats),
    ]
    ch_names = get_channel_names(config)
    if "confluence" in ch_names:
        steps.append(("Confluence", cmd_confluence))

    for name, func in steps:
        print(f"=== {name} ===")
        try:
            func(args, config)
        except FileNotFoundError as e:
            print(f"Skipped — {e}")
        print()


def cmd_replay(args, config):
    """Post full historical timeline to channels."""
    repo = get_repo_path(args, config)
    project = get_project_name(args, config)
    docs_path = config.get("docs_path", "claude_docs")
    replay_type = args.type or "all"
    ch_names = get_channel_names(config)

    token = None
    channels = {}
    if not args.dry_run:
        token = _get_token()
        needed = []
        if replay_type in ("all", "roadmap"):
            needed.append(ch_names["roadmap"])
        if replay_type in ("all", "release"):
            needed.append(ch_names["releases"])
        if replay_type in ("all", "changelog"):
            needed.append(ch_names["changelog"])
        if replay_type in ("all", "stats"):
            needed.append(ch_names["stats"])
        channels = ensure_channels(token, needed)

    # ── Roadmap replay: one post per shipping date ──
    if replay_type in ("all", "roadmap"):
        print("\n=== Roadmap Replay ===")
        snapshots = parse_roadmap_snapshots(repo, docs_path=docs_path)
        for i, snap in enumerate(snapshots):
            data = {
                "phases": snap["phases"],
                "completed_count": snap["completed_count"],
                "total_count": snap["total_count"],
                "next_planned": snap["next_planned"],
                "date": snap["date"],
                "date_display": snap["date_display"],
            }
            blocks = build_roadmap_blocks(data, project)
            shipped_names = ", ".join(
                f"Phase {p['number']}" for p in snap["shipped_phases"]
            )
            print(f"  [{snap['date_display']}] {snap['completed_count']}/{snap['total_count']} complete ({shipped_names})")

            if args.dry_run:
                if i == 0:
                    print(json.dumps(blocks, indent=2))
                    print("  (showing first snapshot only)")
            else:
                ch_id = channels[ch_names["roadmap"]]
                post_message(token, ch_id, blocks, text=f"{project} Roadmap — {snap['date_display']}")
                if i < len(snapshots) - 1:
                    time.sleep(2)

    # ── Release replay: one post per phase (reversed to oldest first) ──
    if replay_type in ("all", "release"):
        print("\n=== Release Replay ===")
        changelog_data = parse_changelog(repo, docs_path=docs_path)
        # Reverse so oldest phase is first
        all_phases = list(reversed(changelog_data["phases"]))

        features_data = None
        try:
            features_data = parse_features(repo, docs_path=docs_path)
        except FileNotFoundError:
            pass

        for i, phase in enumerate(all_phases):
            # Build single-phase data for the formatter
            single = {"phases": [phase]}
            # Only include features stats on the latest phase
            feat = features_data if i == len(all_phases) - 1 else None
            blocks = build_release_blocks(single, project, feat, context="deploy")
            print(f"  [{phase.get('date_display', phase.get('date', '?'))}] {phase['name']}")

            if args.dry_run:
                if i == 0:
                    print(json.dumps(blocks, indent=2))
                    print("  (showing first phase only)")
            else:
                ch_id = channels[ch_names["releases"]]
                post_message(token, ch_id, blocks, text=f"{project} — {phase['name']}")
                if i < len(all_phases) - 1:
                    time.sleep(2)

    # ── Changelog replay: one post per phase (reversed to oldest first) ──
    if replay_type in ("all", "changelog"):
        print("\n=== Changelog Replay ===")
        changelog_data = parse_changelog(repo, docs_path=docs_path)
        all_phases = list(reversed(changelog_data["phases"]))

        for i, phase in enumerate(all_phases):
            # Build with current + next phase (for "Previous:" reference)
            if i > 0:
                prev_phase = all_phases[i - 1]
                single = {"phases": [phase, prev_phase]}
            else:
                single = {"phases": [phase]}
            blocks = build_changelog_blocks(single, project, context="deploy")
            print(f"  [{phase.get('date_display', phase.get('date', '?'))}] {phase['name']}")

            if args.dry_run:
                if i == 0:
                    print(json.dumps(blocks, indent=2))
                    print("  (showing first phase only)")
            else:
                ch_id = channels[ch_names["changelog"]]
                post_message(token, ch_id, blocks, text=f"{project} — {phase['name']}")
                if i < len(all_phases) - 1:
                    time.sleep(2)

    # ── Stats replay: one post per development day ──
    if replay_type in ("all", "stats"):
        print("\n=== Stats Replay ===")
        no_charts = getattr(args, "no_charts", False)
        exclude_paths = config.get("stats_exclude_paths", [])
        repos = get_repo_list(args, config)
        if len(repos) > 1:
            daily = collect_multi_repo_daily_stats(repos, project, exclude_paths=exclude_paths)
        else:
            daily = collect_daily_stats(repos[0]["path"], project, exclude_paths=exclude_paths)
        total_days = len(daily)
        print(f"  Found {total_days} development days")

        for i, day_stats in enumerate(daily):
            day_num = i + 1
            date_str = day_stats["generated_at"]
            daily_commits = day_stats["git"]["daily_commits"]
            print(f"  [{date_str}] Day {day_num}/{total_days}: {daily_commits} commits")

            chart_urls = build_daily_charts(day_stats) if not no_charts else {}
            prev = daily[i - 1] if i > 0 else None
            blocks = build_daily_slack_blocks(day_stats, day_num, total_days, chart_urls, prev)

            if args.dry_run:
                if i == 0:
                    print(json.dumps(blocks, indent=2))
                    print("  (showing first day only)")
            else:
                ch_id = channels[ch_names["stats"]]
                post_message(token, ch_id, blocks, text=f"{project} Stats — {date_str}")
                if i < total_days - 1:
                    time.sleep(2)

    if not args.dry_run:
        print("\nReplay complete!")


def cmd_delete_last(args, config):
    """Delete last N bot messages from a channel."""
    token = _get_token()
    ch_names = get_channel_names(config)

    channel_name = args.channel
    if not channel_name:
        # Delete from all 3 channels
        all_channels = ensure_channels(token, list(ch_names.values()))
        count = int(args.count) if args.count else 1
        for name, ch_id in all_channels.items():
            print(f"#{name}:")
            deleted = delete_bot_messages(token, ch_id, count)
            print(f"  Deleted {deleted} messages")
        return

    # Single channel
    all_channels = ensure_channels(token, [channel_name])
    ch_id = all_channels[channel_name]
    count = int(args.count) if args.count else 1
    print(f"Deleting last {count} bot messages from #{channel_name}...")
    deleted = delete_bot_messages(token, ch_id, count)
    print(f"Deleted {deleted} messages")


def cmd_clear_all(args, config):
    """Delete ALL bot messages from channels."""
    token = _get_token()
    ch_names = get_channel_names(config)

    if args.channel:
        names = [args.channel]
    else:
        names = list(ch_names.values())

    all_channels = ensure_channels(token, names)

    for name, ch_id in all_channels.items():
        print(f"#{name}: ", end="", flush=True)
        deleted = delete_all_bot_messages(token, ch_id)
        print(f"deleted {deleted} messages")

    print("\nAll channels cleared.")


def cmd_setup_channels(args, config):
    token = _get_token()
    ch_names = get_channel_names(config)
    names = list(ch_names.values())
    print(f"Ensuring channels exist: {', '.join('#' + n for n in names)}")
    result = ensure_channels(token, names)
    print(f"\nChannels ready:")
    for name, ch_id in result.items():
        print(f"  #{name} -> {ch_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Post project progress updates to Slack",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "command",
        choices=["roadmap", "release", "changelog", "stats", "confluence", "all", "replay", "delete-last", "clear-all", "setup-channels"],
        help="What to post",
    )
    parser.add_argument("count", nargs="?", help="For delete-last: number of messages to delete")
    parser.add_argument("--dry-run", action="store_true", help="Print blocks, don't post")
    parser.add_argument("--repo", action="append", help="Path to repo root (can specify multiple)")
    parser.add_argument("--project", help="Project display name")
    parser.add_argument("--config", help="Config file path (default: ./config.json)")
    parser.add_argument("--json", action="store_true", help="Output parsed data as JSON")
    parser.add_argument("--type", choices=["roadmap", "release", "changelog", "stats"], help="For replay: which type")
    parser.add_argument("--channel", help="For delete-last: channel name (default: all)")
    parser.add_argument("--no-charts", action="store_true", help="Skip chart generation for stats")
    parser.add_argument("--context", choices=["deploy", "session", "wrap"], default="deploy",
                        help="Message context — changes Slack headings (default: deploy)")

    args = parser.parse_args()

    # Load config
    config_path = args.config or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config.json"
    )
    config = load_config(config_path)

    commands = {
        "roadmap": cmd_roadmap,
        "release": cmd_release,
        "changelog": cmd_changelog,
        "stats": cmd_stats,
        "confluence": cmd_confluence,
        "all": cmd_all,
        "replay": cmd_replay,
        "delete-last": cmd_delete_last,
        "clear-all": cmd_clear_all,
        "setup-channels": cmd_setup_channels,
    }

    try:
        commands[args.command](args, config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
