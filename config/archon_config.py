"""Archon Configuration - Centralized URL management.

Change Archon server via environment variable:
    ARCHON_URL=https://autre-archon.com python cli/kiro_education.py go "lesson-001"

Or edit the defaults here.
"""

import os

# === ARCHON SERVER CONFIGURATION ===
# API endpoint for project/task management
ARCHON_API_URL = os.getenv("ARCHON_URL", "https://archon.nxtcloud.ca")

# Dashboard URL for user-facing links (defaults to API URL)
ARCHON_DASHBOARD_URL = os.getenv("ARCHON_DASHBOARD", ARCHON_API_URL)

# HTTP timeout for API calls (seconds)
ARCHON_TIMEOUT = float(os.getenv("ARCHON_TIMEOUT", "30.0"))


def get_dashboard_url(project_id: str) -> str:
    """Get the dashboard URL for a project."""
    return f"{ARCHON_DASHBOARD_URL}/projects/{project_id}"


def get_api_url(endpoint: str = "") -> str:
    """Get the API URL for an endpoint."""
    return f"{ARCHON_API_URL}{endpoint}"
