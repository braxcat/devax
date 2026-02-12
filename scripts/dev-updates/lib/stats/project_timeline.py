"""Project infrastructure and dependency timeline.

Maps development dates to the infrastructure services and dependencies
that were in use on that date. Used by git_collector to provide accurate
per-day infra/deps instead of static values.

Populate the TIMELINE dict with your project's infrastructure snapshots.
"""


# Each entry represents a snapshot of infra/deps as of that date.
# get_timeline_for_date() returns the most recent entry <= the requested date.
#
# Example:
#   TIMELINE = {
#       "2026-01-01": {
#           "infrastructure_services": [
#               "PostgreSQL",
#               "Prisma ORM",
#           ],
#           "dependencies": {"total": 10, "production": 7, "dev": 3},
#       },
#       "2026-02-01": {
#           "infrastructure_services": [
#               "PostgreSQL",
#               "Prisma ORM",
#               "Redis",
#           ],
#           "dependencies": {"total": 14, "production": 10, "dev": 4},
#       },
#   }
TIMELINE = {}

_SORTED_DATES = sorted(TIMELINE.keys())


def get_timeline_for_date(date_str: str) -> dict:
    """Return infra/deps snapshot for a date, falling back to most recent earlier entry.

    Returns empty dict if the date is before any timeline entry.
    """
    best = None
    for d in _SORTED_DATES:
        if d <= date_str:
            best = d
        else:
            break

    if best is None:
        return {}
    return TIMELINE[best]
