"""
Markdown file parsers for ROADMAP.md, CHANGELOG.md, and FEATURES.md.

All parsers take a repo_path and construct file paths from it.
"""

import os
import re
from collections import OrderedDict
from datetime import date, datetime


def format_date(date_str):
    """Convert ISO date (2026-02-08) to friendly format (Feb 8).
    Handles date ranges like '2026-01-22 to 2026-02-04' → 'Jan 22 to Feb 4'.
    Passes through non-ISO strings unchanged (—, TBD, etc)."""
    if not date_str or date_str in ("—", "TBD", ""):
        return date_str
    # Handle date ranges: "2026-01-22 to 2026-02-04"
    if " to " in date_str:
        parts = date_str.split(" to ")
        return f"{format_date(parts[0].strip())} to {format_date(parts[1].strip())}"
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return dt.strftime("%b %-d")  # Feb 8, not Feb 08
    except ValueError:
        return date_str


def _parse_roadmap_phases(repo_path):
    """Parse the Phase Summary table from ROADMAP.md. Returns list of phase dicts."""
    filepath = os.path.join(repo_path, "claude_docs", "ROADMAP.md")
    with open(filepath, "r") as f:
        content = f.read()

    phases = []
    for match in re.finditer(
        r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
        content,
        re.MULTILINE,
    ):
        number = int(match.group(1))
        name = match.group(2).strip()
        date_str = match.group(3).strip()
        status = match.group(4).strip()
        phases.append({
            "number": number,
            "name": name,
            "date": date_str,
            "date_display": format_date(date_str),
            "status": status,
        })
    return phases


def parse_roadmap(repo_path):
    """Parse docs/ROADMAP.md Phase Summary table.

    Returns:
        {
            "phases": [{"number": int, "name": str, "date": str, "date_display": str, "status": str}],
            "completed_count": int,
            "total_count": int,
            "next_planned": {"number": int, "name": str} or None,
            "date": str  # today in friendly format
        }
    """
    phases = _parse_roadmap_phases(repo_path)

    completed = [p for p in phases if p["status"] == "COMPLETE"]
    next_planned = None
    for p in phases:
        if p["status"] in ("PENDING", "PLANNED"):
            next_planned = {"number": p["number"], "name": p["name"]}
            break

    return {
        "phases": phases,
        "completed_count": len(completed),
        "total_count": len(phases),
        "next_planned": next_planned,
        "date": format_date(date.today().isoformat()),
    }


def parse_roadmap_snapshots(repo_path):
    """Build cumulative roadmap snapshots grouped by shipping date.

    Returns list of snapshots, oldest first:
    [
        {
            "date": "2026-02-08",
            "date_display": "Feb 8",
            "phases": [...all phases with status overridden to COMPLETE only up to this date...],
            "completed_count": int,
            "total_count": int,
            "next_planned": {...} or None,
            "shipped_phases": [phases that shipped on this date]
        }
    ]
    """
    all_phases = _parse_roadmap_phases(repo_path)
    total = len(all_phases)

    # Group completed phases by date
    dates_seen = OrderedDict()
    for p in all_phases:
        if p["status"] == "COMPLETE" and p["date"] not in ("—", "TBD", ""):
            dates_seen.setdefault(p["date"], []).append(p)

    snapshots = []
    cumulative_completed = set()

    for snap_date, shipped in sorted(dates_seen.items()):
        # Add newly shipped phases
        for p in shipped:
            cumulative_completed.add(p["number"])

        # Build full phase list with status overrides
        snapshot_phases = []
        for p in all_phases:
            sp = dict(p)
            if p["number"] in cumulative_completed:
                sp["status"] = "COMPLETE"
            elif p["status"] == "COMPLETE":
                # Not yet completed at this snapshot date
                sp["status"] = "PENDING"
            snapshot_phases.append(sp)

        # Find next planned
        next_planned = None
        for sp in snapshot_phases:
            if sp["status"] in ("PENDING", "PLANNED"):
                next_planned = {"number": sp["number"], "name": sp["name"]}
                break

        snapshots.append({
            "date": snap_date,
            "date_display": format_date(snap_date),
            "phases": snapshot_phases,
            "completed_count": len(cumulative_completed),
            "total_count": total,
            "next_planned": next_planned,
            "shipped_phases": shipped,
        })

    return snapshots


def parse_changelog(repo_path, latest_only=False):
    """Parse CHANGELOG.md into structured phase entries.

    Returns:
        {
            "phases": [
                {
                    "name": "Phase 9",
                    "date": "2026-02-10",
                    "sections": {"Added": [...], "Fixed": [...], ...}
                }
            ]
        }
    """
    filepath = os.path.join(repo_path, "claude_docs", "CHANGELOG.md")
    with open(filepath, "r") as f:
        content = f.read()

    phases = []
    # Split on ## [Phase N] or ## [Pre-Phase 1] headers
    phase_blocks = re.split(r"(?=^## \[)", content, flags=re.MULTILINE)

    for block in phase_blocks:
        # Match phase header: ## [Phase N] — date  or  ## [Pre-Phase 1] — date
        header = re.match(
            r"^## \[(.+?)\]\s*(?:—\s*(.+?))?$", block, re.MULTILINE
        )
        if not header:
            continue

        name = header.group(1)
        date_str = (header.group(2) or "").strip()

        sections = {}
        # Split on ### Added/Fixed/Changed/Database/Dependencies
        section_blocks = re.split(r"(?=^### )", block, flags=re.MULTILINE)
        for sec in section_blocks:
            sec_header = re.match(r"^### (.+?)$", sec, re.MULTILINE)
            if not sec_header:
                continue
            sec_name = sec_header.group(1).strip()
            items = []
            for line in sec.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    items.append(line[2:].strip())
            sections[sec_name] = items

        phases.append({
            "name": name,
            "date": date_str,
            "date_display": format_date(date_str),
            "sections": sections,
        })

        if latest_only:
            break

    return {"phases": phases}


def parse_features(repo_path):
    """Parse docs/FEATURES.md into section summaries.

    Returns:
        {
            "sections": [{"name": str, "route": str or None, "bullet_count": int}],
            "total_sections": int,
            "coming_soon": [{"name": str, "description": str}]
        }
    """
    filepath = os.path.join(repo_path, "claude_docs", "FEATURES.md")
    with open(filepath, "r") as f:
        content = f.read()

    sections = []
    # Split on ## N. headers
    sec_blocks = re.split(r"(?=^## \d+\.)", content, flags=re.MULTILINE)

    for block in sec_blocks:
        header = re.match(r"^## \d+\.\s+(.+?)$", block, re.MULTILINE)
        if not header:
            continue
        name = header.group(1).strip()

        # Extract route
        route_match = re.search(r"\*\*Route:\*\*\s*`(.+?)`", block)
        route = route_match.group(1) if route_match else None

        # Count feature bullets (lines starting with - **)
        bullets = len(re.findall(r"^- \*\*", block, re.MULTILINE))
        # Also count simple bullets as features
        if bullets == 0:
            bullets = len(re.findall(r"^- ", block, re.MULTILINE))

        sections.append({
            "name": name,
            "route": route,
            "bullet_count": bullets,
        })

    # Parse Coming Soon table
    coming_soon = []
    coming_match = re.search(
        r"## \d+\.\s+Coming Soon\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    if coming_match:
        table_text = coming_match.group(1)
        for row in re.finditer(
            r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|",
            table_text,
            re.MULTILINE,
        ):
            coming_soon.append({
                "name": row.group(1).strip(),
                "description": row.group(2).strip(),
            })

    # Filter out "Coming Soon" from sections count
    feature_sections = [s for s in sections if "Coming Soon" not in s["name"]]

    return {
        "sections": feature_sections,
        "total_sections": len(feature_sections),
        "coming_soon": coming_soon,
    }
