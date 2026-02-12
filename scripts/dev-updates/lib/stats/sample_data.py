"""Sample stats data showing the canonical schema.

This module defines the data schema consumed by all other modules.
Phase 1 uses this hard-coded data; Phase 2 will generate it dynamically.

Replace the values below with your project's data.
"""

SAMPLE_STATS = {
    "project_name": "My Project",
    "generated_at": "2026-01-15",
    "first_commit": "2026-01-01",
    "latest_commit": "2026-01-15",
    "project_age_days": 15,

    "lines_of_code": {
        "typescript_javascript": 5000,
        "css": 200,
        "prisma_schema": 100,
        "sql_migrations": 50,
        "documentation": 500,
        "total": 5850,
    },

    "dependencies": {
        "total": 12,
        "production": 9,
        "dev": 3,
    },

    "components": {
        "function_definitions": 100,
        "exported_components": 20,
        "custom_hooks": 2,
        "api_route_files": 5,
        "api_handlers": 8,
        "pages": 6,
        "component_files": 15,
        "prisma_models": 5,
        "db_migrations": 2,
        "import_statements": 80,
    },

    "git": {
        "total_commits": 30,
        "contributors": [
            {"name": "Dev", "commits": 20},
            {"name": "Claude", "commits": 10},
        ],
        "commits_by_date": {
            "2026-01-01": 3,
            "2026-01-02": 2,
            "2026-01-03": 3,
            "2026-01-05": 2,
            "2026-01-07": 3,
            "2026-01-08": 2,
            "2026-01-10": 3,
            "2026-01-12": 4,
            "2026-01-14": 3,
            "2026-01-15": 5,
        },
    },

    "largest_files": [
        {"path": "src/lib/config.ts", "lines": 500},
        {"path": "src/app/dashboard/page.tsx", "lines": 400},
        {"path": "src/lib/utils.ts", "lines": 350},
        {"path": "src/components/Layout.tsx", "lines": 300},
        {"path": "src/app/api/main/route.ts", "lines": 250},
    ],

    "infrastructure_services": [
        "PostgreSQL",
        "Prisma ORM",
        "NextAuth.js",
    ],

    "difficulty": {
        "rating": 5.0,
        "max": 10,
        "label": "Intermediate",
    },

    # Placeholder for GitHub API stats (Phase 2)
    "github_stats": None,

    # Punch card data: [day_of_week (0=Sun), hour (0-23), commit_count]
    "punch_card": [
        [1, 9, 3], [1, 10, 2], [1, 14, 1],
        [2, 10, 2], [2, 15, 3],
        [3, 9, 1], [3, 11, 2],
        [4, 10, 3], [4, 14, 2],
        [5, 9, 2], [5, 16, 1],
    ],
}
