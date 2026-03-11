"""Configuration constants for VisiblyAI MCP Server."""

import os

BASE_URL = "https://www.antonioblago.com/api/v1/mcp"

SIGNUP_URL = "https://www.antonioblago.com/register"
CREDITS_URL = "https://www.antonioblago.com/credits"

# API key from environment
def get_api_key() -> str | None:
    """Get API key from environment variable."""
    return os.environ.get("VISIBLYAI_API_KEY")
