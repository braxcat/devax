"""
Block Kit message builders for Slack.

Post types:
- Roadmap progress     → #dev-roadmap
- Release notes        → #dev-releases
- Changelog            → #dev-changelog
- Confluence sync      → #dev-confluence

Dates use friendly format: "Feb 8" (not "2026-02-08") for international clarity.
"""

from datetime import date


# ─── Block helpers ───


def _header_block(text):
    return {"type": "header", "text": {"type": "plain_text", "text": text[:150]}}


def _section_block(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _fields_block(fields):
    return {
        "type": "section",
        "fields": [{"type": "mrkdwn", "text": f} for f in fields[:10]],
    }


def _divider():
    return {"type": "divider"}


def _context_block(text):
    return {
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": text}],
    }


def _progress_bar(completed, total, width=16):
    """Build a text progress bar: ██████░░░░░░ 62%"""
    if total == 0:
        return "No phases"
    ratio = completed / total
    filled = round(ratio * width)
    empty = width - filled
    pct = round(ratio * 100)
    return f"{'█' * filled}{'░' * empty} {pct}%"


def _display_date(phase):
    """Get display date from a phase dict, preferring date_display over date."""
    return phase.get("date_display") or phase.get("date", "")


# ─── Roadmap ───


def build_roadmap_blocks(data, project_name):
    """Build Block Kit blocks for roadmap progress post."""
    blocks = []

    display_date = data.get("date_display") or data.get("date", "")

    # Header
    blocks.append(_header_block(f"🗺️ {project_name} — Roadmap Progress"))

    # Summary line
    blocks.append(
        _context_block(
            f"{data['completed_count']} of {data['total_count']} phases complete · {display_date}"
        )
    )

    blocks.append(_divider())

    # Phase list
    lines = []
    for p in data["phases"]:
        status = p["status"]
        pd = _display_date(p)
        if status == "COMPLETE":
            icon = "✅"
            date_part = f" ({pd})" if pd and pd not in ("—", "TBD", "") else ""
            lines.append(f"{icon} Phase {p['number']}: {p['name']}{date_part}")
        elif status == "PENDING":
            lines.append(f"⏳ Phase {p['number']}: {p['name']}")
        elif status == "PLANNED":
            lines.append(f"📋 Phase {p['number']}: {p['name']}")
        else:
            lines.append(f"🔮 Phase {p['number']}: {p['name']}")

    # Slack has a 3000 char limit per text field — chunk if needed
    text = "\n".join(lines)
    if len(text) > 2900:
        text = "\n".join(lines[:10]) + "\n...\n" + "\n".join(lines[-3:])
    blocks.append(_section_block(text))

    blocks.append(_divider())

    # Progress bar
    bar = _progress_bar(data["completed_count"], data["total_count"])
    blocks.append(_section_block(f"*Progress:* `{bar}`"))

    # Next up
    if data["next_planned"]:
        np = data["next_planned"]
        blocks.append(
            _context_block(f"Next up: Phase {np['number']} — {np['name']}")
        )

    return blocks


# ─── Release ───


def build_release_blocks(data, project_name, features_data=None, context="deploy"):
    """Build Block Kit blocks for a release post. data has one phase entry.

    context: "deploy" (default), "session", or "wrap" — controls the header text.
    """
    blocks = []

    if not data.get("phases"):
        return [_section_block("No releases found in CHANGELOG.md")]

    phase = data["phases"][0]
    display_date = _display_date(phase)

    # Header — varies by context
    if context == "session":
        header = f"🛠️ {project_name} — Development Progress"
    elif context == "wrap":
        header = f"🏁 {project_name} — Session Wrap"
    else:
        header = f"🚀 {project_name} — {phase['name']} Shipped!"
    blocks.append(_header_block(header))

    if display_date:
        blocks.append(_context_block(display_date))

    blocks.append(_divider())

    # Added section
    added = phase["sections"].get("Added", [])
    if added:
        items = "\n".join(f"• {item}" for item in added[:15])
        blocks.append(_section_block(f"*✨ What's New*\n{items}"))

    # Fixed section
    fixed = phase["sections"].get("Fixed", [])
    if fixed:
        items = "\n".join(f"• {item}" for item in fixed[:10])
        blocks.append(_section_block(f"*🔧 Fixed*\n{items}"))

    # Changed section
    changed = phase["sections"].get("Changed", [])
    if changed:
        items = "\n".join(f"• {item}" for item in changed[:10])
        blocks.append(_section_block(f"*♻️ Changed*\n{items}"))

    # Database section
    db = phase["sections"].get("Database", [])
    if db:
        items = "\n".join(f"• {item}" for item in db[:5])
        blocks.append(_section_block(f"*🗄️ Database*\n{items}"))

    # Dependencies section
    deps = phase["sections"].get("Dependencies", [])
    if deps:
        items = "\n".join(f"• {item}" for item in deps[:5])
        blocks.append(_section_block(f"*📦 Dependencies*\n{items}"))

    blocks.append(_divider())

    # Platform stats from features data
    if features_data:
        stats_parts = [
            f"Features: {features_data['total_sections']} sections",
        ]
        if features_data["coming_soon"]:
            stats_parts.append(
                f"Coming Soon: {len(features_data['coming_soon'])} planned"
            )
        blocks.append(_section_block(f"*📊 Platform Stats*\n{' · '.join(stats_parts)}"))

    return blocks


# ─── Changelog ───


def build_changelog_blocks(data, project_name, context="deploy"):
    """Build Block Kit blocks for changelog post.

    context: "deploy" (default), "session", or "wrap" — controls the header text.
    """
    blocks = []

    if not data.get("phases"):
        return [_section_block("No entries found in CHANGELOG.md")]

    phase = data["phases"][0]
    display_date = _display_date(phase)

    # Header — varies by context
    if context == "session":
        header = f"📝 {project_name} — Session Update"
    elif context == "wrap":
        header = f"🏁 {project_name} — Session Changes"
    else:
        header = f"📝 {project_name} — Changelog"
    blocks.append(_header_block(header))
    blocks.append(_context_block(f"{phase['name']} · {display_date}"))

    blocks.append(_divider())

    # All sections
    for sec_name, items in phase["sections"].items():
        if not items:
            continue
        formatted = "\n".join(f"• {item}" for item in items[:10])
        blocks.append(_section_block(f"*{sec_name}*\n{formatted}"))

    blocks.append(_divider())

    # Previous phase reference
    if len(data.get("phases", [])) > 1:
        prev = data["phases"][1]
        prev_date = _display_date(prev)
        blocks.append(
            _context_block(f"Previous: {prev['name']} — {prev_date}")
        )

    return blocks


# ─── Confluence ───


def build_confluence_blocks(data, project_name, context="deploy"):
    """Build Block Kit blocks for Confluence sync status post.

    context: "deploy" (default), "session", or "wrap" — controls the header text.
    """
    blocks = []

    if context == "wrap":
        header = f"📚 {project_name} — Confluence Activity"
    elif context == "session":
        header = f"📚 {project_name} — Confluence Status"
    else:
        header = f"📚 {project_name} — Confluence Sync"
    blocks.append(_header_block(header))

    today = date.today().strftime("%b %-d")
    blocks.append(_context_block(f"Wiki mirror status · {today}"))

    blocks.append(_divider())

    total = data.get("total_pages", 0)
    spaces = data.get("spaces", [])

    if total == 0:
        blocks.append(_section_block("No Confluence pages found in mirror."))
        return blocks

    # Summary stats
    space_lines = []
    for s in spaces:
        recent = f" ({s['recent_changes']} changed)" if s["recent_changes"] > 0 else ""
        space_lines.append(f"• *{s['name']}*: {s['count']} pages{recent}")

    blocks.append(_section_block(
        f"*📊 Mirror Summary*\n"
        f"Total pages: *{total}*\n\n"
        + "\n".join(space_lines)
    ))

    # Recent commits
    commits = data.get("recent_commits", [])
    if commits:
        blocks.append(_divider())
        commit_lines = [f"• `{c['hash']}` {c['subject']} ({c['date']})" for c in commits[:8]]
        blocks.append(_section_block(
            f"*🔄 Recent Changes (7 days)*\n" + "\n".join(commit_lines)
        ))
    else:
        blocks.append(_divider())
        blocks.append(_section_block("_No changes in the last 7 days_"))

    return blocks
