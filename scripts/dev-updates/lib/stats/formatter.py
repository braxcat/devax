"""Slack Block Kit message builder for coding stats.

Constructs a list of Block Kit blocks from stats data and chart URLs.
"""

from datetime import datetime


def _header_block(text: str) -> dict:
    return {
        "type": "header",
        "text": {"type": "plain_text", "text": text, "emoji": True},
    }


def _section_block(text: str) -> dict:
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }


def _fields_block(fields: list) -> dict:
    return {
        "type": "section",
        "fields": [{"type": "mrkdwn", "text": f} for f in fields],
    }


def _image_block(url: str, alt_text: str) -> dict:
    return {
        "type": "image",
        "image_url": url,
        "alt_text": alt_text,
    }


def _divider() -> dict:
    return {"type": "divider"}


def _context_block(text: str) -> dict:
    return {
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": text}],
    }


def _difficulty_bar(rating: float, max_rating: float = 10) -> str:
    """Render a visual progress bar for difficulty rating."""
    filled = round(rating)
    empty = round(max_rating) - filled
    return "\u2588" * filled + "\u2591" * empty


def _format_number(n) -> str:
    """Format a number with comma separators."""
    if isinstance(n, float):
        return f"{n:,.1f}"
    return f"{n:,}"


def build_slack_blocks(stats: dict, chart_urls: dict, estimate: dict = None) -> list:
    """Build a complete Slack Block Kit message from stats and chart URLs.

    Args:
        stats: The stats dict (from sample_data or collector).
        chart_urls: Dict of chart_name -> URL from charts.build_all_charts().
        estimate: Optional dev time estimate from estimator.

    Returns:
        List of Block Kit block dicts.
    """
    blocks = []
    project = stats.get("project_name", "Project")
    age = stats.get("project_age_days", "?")
    generated = stats.get("generated_at", datetime.now().strftime("%Y-%m-%d"))

    # Header
    blocks.append(_header_block(f"\U0001f4ca {project} \u2014 Daily Coding Stats"))
    blocks.append(_context_block(f"{generated} \u00b7 Day {age} of development"))

    # Key Metrics
    loc = stats.get("lines_of_code", {})
    git = stats.get("git", {})
    comp = stats.get("components", {})
    deps = stats.get("dependencies", {})

    metrics = [
        f"*Lines of Code*\n{_format_number(loc.get('total', 0))}",
        f"*Total Commits*\n{_format_number(git.get('total_commits', 0))}",
        f"*Components*\n{_format_number(comp.get('component_files', 0))}",
        f"*Pages*\n{_format_number(comp.get('pages', 0))}",
        f"*API Routes*\n{_format_number(comp.get('api_route_files', 0))}",
        f"*DB Models*\n{_format_number(comp.get('prisma_models', 0))}",
        f"*Dependencies*\n{_format_number(deps.get('total', 0))}",
        f"*Functions*\n{_format_number(comp.get('function_definitions', 0))}",
    ]
    # Section fields max 10 items, and they render 2 per row
    blocks.append(_divider())
    blocks.append(_fields_block(metrics[:8]))

    # Code Composition Chart
    if "composition_doughnut" in chart_urls:
        blocks.append(_divider())
        blocks.append(_image_block(chart_urls["composition_doughnut"], "Code composition doughnut chart"))

    # Lines of Code Chart
    if "loc_bar" in chart_urls:
        blocks.append(_image_block(chart_urls["loc_bar"], "Lines of code by category"))

    # Commit Activity Chart
    if "commit_line" in chart_urls:
        blocks.append(_divider())
        blocks.append(_image_block(chart_urls["commit_line"], "Commit activity over time"))

    # Contributor Chart
    if "contributor_bar" in chart_urls:
        blocks.append(_image_block(chart_urls["contributor_bar"], "Commits by contributor"))

    # Punch Card Chart
    if "punch_card" in chart_urls:
        blocks.append(_divider())
        blocks.append(_image_block(chart_urls["punch_card"], "Coding hours punch card"))

    # Infrastructure
    services = stats.get("infrastructure_services", [])
    if services:
        blocks.append(_divider())
        svc_text = ", ".join(services)
        blocks.append(_section_block(
            f"\U0001f3d7\ufe0f *Infrastructure* ({len(services)} services)\n{svc_text}"
        ))

    # Dependencies
    if deps:
        blocks.append(_section_block(
            f"\U0001f4e6 *Dependencies*: {deps.get('total', 0)} packages "
            f"({deps.get('production', 0)} production, {deps.get('dev', 0)} dev)"
        ))

    # Difficulty Rating
    diff = stats.get("difficulty", {})
    if diff:
        rating = diff.get("rating", 0)
        max_r = diff.get("max", 10)
        label = diff.get("label", "")
        bar = _difficulty_bar(rating, max_r)
        blocks.append(_divider())
        blocks.append(_section_block(
            f"\u2b50 *Difficulty: {label} ({rating}/{max_r})*\n`{bar}`"
        ))

    # Dev Time Estimate
    if estimate:
        cocomo_weeks = estimate.get("cocomo_weeks", 0)
        active_days = estimate.get("active_coding_days", 0)
        calendar_days = estimate.get("calendar_days", 0)
        speedup = estimate.get("speedup_factor", 0)

        est_text = (
            f"\u23f1\ufe0f *Estimated Dev Time*\n"
            f"COCOMO estimate (solo dev): ~{cocomo_weeks:.0f} weeks\n"
            f"Actual: {calendar_days} calendar days ({active_days} active coding days)\n"
        )
        if speedup > 1:
            est_text += f"AI-assisted speedup: ~{speedup:.1f}x"

        blocks.append(_divider())
        blocks.append(_section_block(est_text))

    # Largest Files
    largest = stats.get("largest_files", [])
    if largest:
        file_lines = "\n".join(
            f"`{f['path']}` \u2014 {_format_number(f['lines'])} lines"
            for f in largest[:5]
        )
        blocks.append(_divider())
        blocks.append(_section_block(f"\U0001f4c4 *Largest Files*\n{file_lines}"))

    # Footer
    blocks.append(_divider())
    blocks.append(_context_block(
        f"Generated by dev-updates \u00b7 "
        f"`python3 dev_updates.py stats --dry-run` to preview"
    ))

    return blocks


def build_daily_slack_blocks(day_stats: dict, day_number: int, total_days: int,
                              chart_urls: dict = None, prev_day_stats: dict = None) -> list:
    """Build a compact Slack Block Kit message for a single development day.

    Shows that day's activity plus cumulative running totals.
    Infrastructure/dependencies/difficulty only shown when new or changed from previous day.

    Args:
        day_stats: Stats dict for this day (from git_collector).
        day_number: 1-indexed day number in the sequence.
        total_days: Total number of development days.
        chart_urls: Optional dict of chart_name -> URL.
        prev_day_stats: Previous day's stats (to detect changes). None for first day.

    Returns:
        List of Block Kit block dicts.
    """
    if chart_urls is None:
        chart_urls = {}

    blocks = []
    project = day_stats.get("project_name", "Project")
    date = day_stats.get("generated_at", "")
    age = day_stats.get("project_age_days", "?")
    loc = day_stats.get("lines_of_code", {})
    git = day_stats.get("git", {})

    # Header
    blocks.append(_header_block(
        f"\U0001f4ca {project} \u2014 Day {day_number}/{total_days}"
    ))
    blocks.append(_context_block(f"{date} \u00b7 Day {age} since first commit"))

    # Today's activity
    daily_commits = git.get("daily_commits", 0)
    daily_added = loc.get("daily_added", 0)
    daily_deleted = loc.get("daily_deleted", 0)
    daily_net = daily_added - daily_deleted

    activity_text = (
        f"\U0001f525 *Today's Activity*\n"
        f"{_format_number(daily_commits)} commits \u00b7 "
        f"+{_format_number(daily_added)} / -{_format_number(daily_deleted)} lines "
        f"(net {'+' if daily_net >= 0 else ''}{_format_number(daily_net)})"
    )
    blocks.append(_divider())
    blocks.append(_section_block(activity_text))

    # Tags line (commit types + project sources)
    commit_tags = day_stats.get("commit_tags", {})
    project_tags = day_stats.get("project_tags", {})
    if commit_tags or project_tags:
        parts = []
        if commit_tags:
            type_parts = [f"{tag} ({count})" for tag, count in sorted(commit_tags.items(), key=lambda x: -x[1])]
            parts.append(" \u00b7 ".join(type_parts))
        if project_tags and len(project_tags) > 1:
            proj_parts = [f"{tag} ({count})" for tag, count in sorted(project_tags.items(), key=lambda x: -x[1])]
            parts.append(" \u00b7 ".join(proj_parts))
        elif project_tags:
            tag = list(project_tags.keys())[0]
            parts.append(tag)
        blocks.append(_context_block("\U0001f3f7\ufe0f " + " \u2014 ".join(parts)))

    # Cumulative totals
    total_commits = git.get("total_commits", 0)
    total_loc = loc.get("total", 0)
    contributors = git.get("contributors", [])
    contrib_text = ", ".join(
        f"{c['name']} ({c['commits']})" for c in contributors
    )

    cumulative_fields = [
        f"*Total LOC*\n{_format_number(total_loc)}",
        f"*Total Commits*\n{_format_number(total_commits)}",
    ]
    blocks.append(_fields_block(cumulative_fields))

    if contrib_text:
        blocks.append(_context_block(f"Contributors: {contrib_text}"))

    # Summary from commit subjects
    subjects = day_stats.get("commit_subjects", [])
    if subjects:
        summary = "; ".join(subjects)
        if len(summary) > 200:
            summary = summary[:197] + "..."
        blocks.append(_section_block(f"\U0001f4dd *Summary:* {summary}"))

    # Charts (subset: commit timeline + punch card)
    if "commit_line" in chart_urls:
        blocks.append(_divider())
        blocks.append(_image_block(chart_urls["commit_line"], "Commit activity over time"))

    if "punch_card" in chart_urls:
        blocks.append(_image_block(chart_urls["punch_card"], "Coding hours heatmap"))

    # Infrastructure — only show if new/changed from previous day
    services = set(day_stats.get("infrastructure_services", []))
    prev_services = set((prev_day_stats or {}).get("infrastructure_services", []))
    new_services = services - prev_services
    if new_services:
        blocks.append(_divider())
        new_list = ", ".join(sorted(new_services))
        blocks.append(_section_block(
            f"\U0001f3d7\ufe0f *Infrastructure* ({len(services)} services, "
            f"+{len(new_services)} new)\n{new_list}"
        ))

    # Dependencies — only show if changed
    deps = day_stats.get("dependencies", {})
    prev_deps = (prev_day_stats or {}).get("dependencies", {})
    if deps and deps != prev_deps:
        total = deps.get("total", 0)
        prev_total = prev_deps.get("total", 0)
        delta = total - prev_total
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        blocks.append(_section_block(
            f"\U0001f4e6 *Dependencies*: {total} packages "
            f"({deps.get('production', 0)} prod, {deps.get('dev', 0)} dev) "
            f"({delta_str} new)" if delta != 0 else
            f"\U0001f4e6 *Dependencies*: {total} packages "
            f"({deps.get('production', 0)} prod, {deps.get('dev', 0)} dev)"
        ))

    # Difficulty Rating — only show if new/changed
    diff = day_stats.get("difficulty", {})
    prev_diff = (prev_day_stats or {}).get("difficulty", {})
    if diff and diff != prev_diff:
        rating = diff.get("rating", 0)
        max_r = diff.get("max", 10)
        label = diff.get("label", "")
        bar = _difficulty_bar(rating, max_r)
        blocks.append(_divider())
        blocks.append(_section_block(
            f"\u2b50 *Difficulty: {label} ({rating}/{max_r})*\n`{bar}`"
        ))

    # Footer
    blocks.append(_divider())
    project_tags = day_stats.get("project_tags", {})
    repo_names = ", ".join(sorted(project_tags.keys())) if project_tags else ""
    footer = f"Generated by dev-updates \u00b7 Day {day_number} of {total_days}"
    if repo_names:
        footer += f" \u00b7 {repo_names}"
    blocks.append(_context_block(footer))

    return blocks
