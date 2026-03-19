"""Integration test configuration - requires VISIBLYAI_API_KEY."""

import os
import pytest

# Skip all integration tests if no API key
pytestmark = pytest.mark.skipif(
    not os.environ.get("VISIBLYAI_API_KEY"),
    reason="VISIBLYAI_API_KEY not set - skipping integration tests",
)
