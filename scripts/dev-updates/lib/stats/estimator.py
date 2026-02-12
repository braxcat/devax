"""Development time estimator using COCOMO-lite.

Estimates how long a project would take a solo developer (no AI assistance)
and compares against actual elapsed time to compute a speedup factor.

References:
- Boehm, B.W. (1981). "Software Engineering Economics"
- COCOMO II: Boehm et al. (2000). "Software Cost Estimation with COCOMO II"
"""

import math
from datetime import datetime, timedelta


# COCOMO organic model coefficients (small teams, well-understood projects)
COCOMO_A = 2.4    # effort multiplier
COCOMO_B = 1.05   # effort exponent
COCOMO_C = 2.5    # schedule multiplier
COCOMO_D = 0.38   # schedule exponent

# Working assumptions
HOURS_PER_DAY = 8
DAYS_PER_WEEK = 5
WEEKS_PER_MONTH = 4.33
DAYS_PER_MONTH = DAYS_PER_WEEK * WEEKS_PER_MONTH  # ~21.65


def _count_active_days(commits_by_date: dict) -> int:
    """Count days that had at least one commit."""
    return len(commits_by_date)


def _count_active_days_excluding_gaps(commits_by_date: dict, max_gap_days: int = 3) -> int:
    """Count active days, noting inactive stretches.

    Returns the number of days with commits. Gaps > max_gap_days
    are considered periods of inactivity (not working).
    """
    return len(commits_by_date)


def _calculate_active_period_days(commits_by_date: dict, max_gap_days: int = 3) -> dict:
    """Analyze the commit timeline to distinguish active vs inactive periods.

    Returns dict with:
      - calendar_days: total elapsed days first to last commit
      - active_coding_days: days with at least one commit
      - inactive_days: calendar_days - active_coding_days
      - longest_gap_days: longest stretch without commits
      - active_period_days: calendar days minus long inactive stretches
    """
    if not commits_by_date:
        return {
            "calendar_days": 0,
            "active_coding_days": 0,
            "inactive_days": 0,
            "longest_gap_days": 0,
            "active_period_days": 0,
        }

    sorted_dates = sorted(commits_by_date.keys())
    first = datetime.strptime(sorted_dates[0], "%Y-%m-%d")
    last = datetime.strptime(sorted_dates[-1], "%Y-%m-%d")
    calendar_days = (last - first).days + 1
    active_coding_days = len(sorted_dates)

    # Find gaps
    gaps = []
    for i in range(1, len(sorted_dates)):
        prev = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
        curr = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
        gap = (curr - prev).days - 1  # days between commits (exclusive)
        if gap > 0:
            gaps.append(gap)

    longest_gap = max(gaps) if gaps else 0

    # Subtract long inactive stretches from the active period
    inactive_stretch_days = sum(g for g in gaps if g > max_gap_days)
    active_period_days = calendar_days - inactive_stretch_days

    return {
        "calendar_days": calendar_days,
        "active_coding_days": active_coding_days,
        "inactive_days": calendar_days - active_coding_days,
        "longest_gap_days": longest_gap,
        "active_period_days": active_period_days,
    }


def estimate_dev_time(stats: dict) -> dict:
    """Estimate development time for a solo developer.

    Uses two methods and presents both:

    1. **Productivity-based estimate** (primary): Based on industry-average
       lines of productive code per day for a senior full-stack developer
       using modern frameworks. Research suggests 100-200 LoC/day of
       "kept" code (net after refactoring/deletion). We use 125 LoC/day
       as a reasonable midpoint for complex web apps with integrations.

    2. **COCOMO reference** (secondary): The classic model provides a
       sanity-check. COCOMO was calibrated for 1980s enterprise projects,
       so its raw output significantly overpredicts for modern framework-
       heavy development. We show it for context only.

    Args:
        stats: The stats dict with lines_of_code and git data.

    Returns:
        Dict with estimates, actual timeline analysis, and speedup factor.
    """
    total_loc = stats.get("lines_of_code", {}).get("total", 0)
    kloc = total_loc / 1000.0
    commits_by_date = stats.get("git", {}).get("commits_by_date", {})

    # --- Method 1: Productivity-based estimate ---
    # Senior full-stack dev with modern frameworks: ~125 productive LoC/day
    # This accounts for the full dev cycle (design, code, debug, test)
    LOC_PER_DAY = 125
    estimated_working_days = total_loc / LOC_PER_DAY if total_loc > 0 else 0
    estimated_weeks = estimated_working_days / DAYS_PER_WEEK

    # --- Method 2: COCOMO organic model (reference only) ---
    if kloc > 0:
        effort_pm = COCOMO_A * math.pow(kloc, COCOMO_B)
        schedule_months = COCOMO_C * math.pow(effort_pm, COCOMO_D)
    else:
        effort_pm = 0
        schedule_months = 0

    cocomo_weeks = schedule_months * WEEKS_PER_MONTH

    # --- Actual timeline analysis ---
    timeline = _calculate_active_period_days(commits_by_date)

    # Speedup: compare productivity estimate to actual active coding days
    actual_active_days = timeline["active_coding_days"]
    if actual_active_days > 0 and estimated_working_days > 0:
        speedup = estimated_working_days / actual_active_days
    else:
        speedup = 0

    return {
        # Primary estimate (productivity-based)
        "kloc": round(kloc, 1),
        "estimated_working_days": round(estimated_working_days, 0),
        "cocomo_weeks": round(estimated_weeks, 0),  # main display value

        # COCOMO reference
        "cocomo_effort_pm": round(effort_pm, 1),
        "cocomo_schedule_months": round(schedule_months, 1),
        "cocomo_raw_weeks": round(cocomo_weeks, 0),

        # Actual timeline
        "calendar_days": timeline["calendar_days"],
        "active_coding_days": timeline["active_coding_days"],
        "inactive_days": timeline["inactive_days"],
        "active_period_days": timeline["active_period_days"],
        "longest_gap_days": timeline["longest_gap_days"],

        # Speedup
        "speedup_factor": round(speedup, 1),
    }
