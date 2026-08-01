"""Configuration constants for VisiblyAI MCP Server."""

import os

BASE_URL = os.environ.get(
    "VISIBLYAI_API_URL", "https://visibly-ai.com/api/v1/mcp"
).rstrip("/")

SIGNUP_URL = "https://visibly-ai.com/register"
CREDITS_URL = "https://visibly-ai.com/settings"

# API key from environment
def get_api_key() -> str | None:
    """Get API key from environment variable."""
    return os.environ.get("VISIBLYAI_API_KEY")
