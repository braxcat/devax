"""QuickChart.io URL builders for coding stats charts.

Generates Chart.js configs and encodes them as QuickChart URLs.
Uses POST endpoint for configs that exceed URL length limits.
"""

import json
import time
import urllib.parse
import urllib.request

# Consistent color palette
COLORS = {
    "green": "#2D8B55",
    "blue": "#4A90D9",
    "orange": "#FF8C00",
    "purple": "#7B68EE",
    "teal": "#20B2AA",
    "brown": "#8B6914",
    "red": "#D94A4A",
    "gray": "#999999",
}

COLOR_LIST = list(COLORS.values())

CHART_WIDTH = 600
CHART_HEIGHT = 300
CHART_BG = "#FFFFFF"


def _build_quickchart_url(config: dict, width: int = CHART_WIDTH, height: int = CHART_HEIGHT) -> str:
    """Build a QuickChart URL from a Chart.js config.

    Uses GET for short configs, POST for long ones.
    Appends cache-buster to prevent Slack image caching.
    """
    config_json = json.dumps(config, separators=(",", ":"))
    cache_buster = int(time.time())

    # Try GET first (simpler, no round-trip)
    # Note: 'v' param is Chart.js version in QuickChart, so use 'cb' for cache busting
    encoded = urllib.parse.quote(config_json)
    get_url = f"https://quickchart.io/chart?c={encoded}&w={width}&h={height}&bkg={urllib.parse.quote(CHART_BG)}&cb={cache_buster}"

    if len(get_url) < 2000:
        return get_url

    # Fall back to POST for long configs
    payload = json.dumps({
        "chart": config,
        "width": width,
        "height": height,
        "backgroundColor": CHART_BG,
        "version": "4",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://quickchart.io/chart/create",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("url", get_url)
    except Exception:
        # If POST fails, return the long GET URL anyway
        return get_url


def build_loc_bar_chart(lines_of_code: dict) -> str:
    """Horizontal bar chart of lines of code by category."""
    labels = []
    data = []
    colors = []

    categories = [
        ("typescript_javascript", "TypeScript / JS", COLORS["blue"]),
        ("documentation", "Documentation", COLORS["green"]),
        ("sql_migrations", "SQL Migrations", COLORS["orange"]),
        ("prisma_schema", "Prisma Schema", COLORS["purple"]),
        ("css", "CSS", COLORS["teal"]),
    ]

    for key, label, color in categories:
        val = lines_of_code.get(key, 0)
        if val > 0:
            labels.append(label)
            data.append(val)
            colors.append(color)

    config = {
        "type": "horizontalBar",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": colors,
                "borderWidth": 0,
            }],
        },
        "options": {
            "legend": {"display": False},
            "title": {"display": True, "text": "Lines of Code by Category", "fontSize": 14},
            "scales": {
                "xAxes": [{"ticks": {"beginAtZero": True}}],
            },
        },
    }
    return _build_quickchart_url(config)


def build_composition_doughnut_chart(lines_of_code: dict) -> str:
    """Doughnut chart showing code composition percentages."""
    labels = []
    data = []
    colors = []

    categories = [
        ("typescript_javascript", "TS/JS", COLORS["blue"]),
        ("documentation", "Docs", COLORS["green"]),
        ("sql_migrations", "SQL", COLORS["orange"]),
        ("prisma_schema", "Prisma", COLORS["purple"]),
        ("css", "CSS", COLORS["teal"]),
    ]

    total = lines_of_code.get("total", 1)
    for key, label, color in categories:
        val = lines_of_code.get(key, 0)
        if val > 0:
            pct = round(val / total * 100, 1)
            labels.append(f"{label} ({pct}%)")
            data.append(val)
            colors.append(color)

    config = {
        "type": "doughnut",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": colors,
                "borderWidth": 2,
                "borderColor": "#FFFFFF",
            }],
        },
        "options": {
            "title": {"display": True, "text": "Code Composition", "fontSize": 14},
            "plugins": {
                "datalabels": {
                    "display": True,
                    "color": "#FFFFFF",
                    "font": {"weight": "bold", "size": 11},
                },
                "doughnutlabel": {
                    "labels": [{
                        "text": str(total),
                        "font": {"size": 20, "weight": "bold"},
                    }, {
                        "text": "total lines",
                        "font": {"size": 12},
                    }],
                },
            },
        },
    }
    return _build_quickchart_url(config)


def build_commit_line_chart(commits_by_date: dict) -> str:
    """Line chart with area fill showing commits over time."""
    sorted_dates = sorted(commits_by_date.keys())
    labels = [d[5:] for d in sorted_dates]  # MM-DD format
    data = [commits_by_date[d] for d in sorted_dates]

    config = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "Commits",
                "data": data,
                "fill": True,
                "backgroundColor": "rgba(74, 144, 217, 0.2)",
                "borderColor": COLORS["blue"],
                "borderWidth": 2,
                "pointRadius": 3,
                "pointBackgroundColor": COLORS["blue"],
                "tension": 0.3,
            }],
        },
        "options": {
            "title": {"display": True, "text": "Commit Activity Over Time", "fontSize": 14},
            "legend": {"display": False},
            "scales": {
                "yAxes": [{"ticks": {"beginAtZero": True, "stepSize": 1}}],
                "xAxes": [{"ticks": {"maxRotation": 45}}],
            },
        },
    }
    return _build_quickchart_url(config)


def build_contributor_bar_chart(contributors: list) -> str:
    """Horizontal bar chart of commits per contributor."""
    labels = [c["name"] for c in contributors]
    data = [c["commits"] for c in contributors]
    colors = [COLOR_LIST[i % len(COLOR_LIST)] for i in range(len(contributors))]

    config = {
        "type": "horizontalBar",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": data,
                "backgroundColor": colors,
                "borderWidth": 0,
            }],
        },
        "options": {
            "legend": {"display": False},
            "title": {"display": True, "text": "Commits by Contributor", "fontSize": 14},
            "scales": {
                "xAxes": [{"ticks": {"beginAtZero": True, "stepSize": 5}}],
            },
        },
    }
    return _build_quickchart_url(config)


def _build_quickchart_url_raw(config_str: str, width: int = CHART_WIDTH, height: int = CHART_HEIGHT) -> str:
    """Build a QuickChart URL from a raw JS config string (supports callbacks).

    Always uses POST since raw JS configs with callbacks exceed GET length limits.
    """
    cache_buster = int(time.time())

    # Try GET first in case it fits
    encoded = urllib.parse.quote(config_str)
    get_url = f"https://quickchart.io/chart?c={encoded}&w={width}&h={height}&bkg={urllib.parse.quote(CHART_BG)}&cb={cache_buster}"

    if len(get_url) < 2000:
        return get_url

    # POST with raw string chart config (QuickChart evaluates JS in string form)
    payload = json.dumps({
        "chart": config_str,
        "width": width,
        "height": height,
        "backgroundColor": CHART_BG,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://quickchart.io/chart/create",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("url", get_url)
    except Exception:
        return get_url


def build_punch_card_chart(punch_card: list) -> str:
    """Heatmap-style bubble chart showing coding activity across all 24 hours x 7 days.

    Each cell is a bubble sized and colored by commit intensity.
    Warm color palette (oranges/reds) — visually distinct from other charts.
    Uses raw JS config string for tick callbacks (day names, hour labels).
    """
    # Day mapping: data uses 0=Sun..6=Sat, display Mon(0)..Sun(6) on y-axis
    day_to_y = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 0: 6}

    # Build lookup and find max
    grid = {}
    max_c = 0
    for day, hour, commits in punch_card:
        grid[(day, hour)] = commits
        if commits > max_c:
            max_c = commits
    if max_c == 0:
        max_c = 1

    # Color + size thresholds (warm palette)
    # Each bucket: (label, min_commits, max_commits, color, min_radius)
    levels = [
        ("1-2",  1, 2, "#FFCC80", 5),
        ("3-4",  3, 4, "#FF9800", 8),
        ("5+",   5, 99, "#D84315", 11),
    ]

    # Build bubble data points grouped by level
    level_points = {l[0]: [] for l in levels}
    for day_data in range(7):
        for hour in range(24):
            c = grid.get((day_data, hour), 0)
            if c == 0:
                continue
            y = day_to_y[day_data]
            for label, lo, hi, _, base_r in levels:
                if lo <= c <= hi:
                    r = base_r + min(c - lo, 3)
                    level_points[label].append(f"{{x:{hour},y:{y},r:{r}}}")
                    break

    # Build datasets JS fragments
    ds_parts = []
    for label, _, _, color, _ in levels:
        pts = level_points[label]
        if pts:
            ds_parts.append(
                f"{{label:'{label} commits',"
                f"data:[{','.join(pts)}],"
                f"backgroundColor:'{color}',"
                f"borderColor:'{color}',"
                f"borderWidth:0,"
                f"hoverRadius:0}}"
            )

    # Assemble raw JS config (supports callback functions for axis labels)
    config_str = (
        "{"
        "type:'bubble',"
        "data:{datasets:[" + ",".join(ds_parts) + "]},"
        "options:{"
        "title:{display:true,text:'Coding Activity Heatmap',fontSize:14},"
        "legend:{display:true,position:'bottom',labels:{boxWidth:12,fontSize:10,padding:8}},"
        "scales:{"
        "xAxes:[{"
        "ticks:{min:-1,max:24,stepSize:1,"
        "callback:function(v){"
        "if(v<0||v>23)return '';"
        "if(v%3!==0)return '';"
        "if(v===0)return '12a';"
        "if(v<12)return v+'a';"
        "if(v===12)return '12p';"
        "return(v-12)+'p'"
        "}},"
        "gridLines:{display:false},"
        "scaleLabel:{display:true,labelString:'Hour of Day',fontSize:11}"
        "}],"
        "yAxes:[{"
        "ticks:{min:-0.5,max:6.5,stepSize:1,"
        "callback:function(v){"
        "return['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][v]||''"
        "}},"
        "gridLines:{color:'rgba(0,0,0,0.05)',drawBorder:false}"
        "}]"
        "}"
        "}"
        "}"
    )

    return _build_quickchart_url_raw(config_str, width=700, height=300)


def build_daily_charts(day_stats: dict) -> dict:
    """Build chart URLs for a daily report (subset: commit timeline + punch card)."""
    charts = {}

    commits_by_date = day_stats.get("git", {}).get("commits_by_date", {})
    if commits_by_date:
        charts["commit_line"] = build_commit_line_chart(commits_by_date)

    punch_card = day_stats.get("punch_card", [])
    if punch_card:
        charts["punch_card"] = build_punch_card_chart(punch_card)

    return charts


def build_all_charts(stats: dict) -> dict:
    """Build all chart URLs from a stats dict. Returns a dict of chart_name -> url."""
    charts = {}

    loc = stats.get("lines_of_code", {})
    if loc:
        charts["loc_bar"] = build_loc_bar_chart(loc)
        charts["composition_doughnut"] = build_composition_doughnut_chart(loc)

    commits_by_date = stats.get("git", {}).get("commits_by_date", {})
    if commits_by_date:
        charts["commit_line"] = build_commit_line_chart(commits_by_date)

    contributors = stats.get("git", {}).get("contributors", [])
    if contributors:
        charts["contributor_bar"] = build_contributor_bar_chart(contributors)

    punch_card = stats.get("punch_card", [])
    if punch_card:
        charts["punch_card"] = build_punch_card_chart(punch_card)

    return charts
