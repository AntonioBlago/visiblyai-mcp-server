"""VisiblyAI MCP Server - SEO tools for Claude Code."""

# Single source of truth for the version. pyproject.toml reads it from here via
# hatchling's dynamic version, so the two can no longer disagree -- they did for
# four releases (0.7.1 here while pyproject said 0.11.0), unnoticed because
# nothing reads this constant, which is exactly why it could drift.
#
# Deliberately not importlib.metadata: that reports the version of the INSTALLED
# distribution, so running from a source tree would report whatever happens to be
# installed in the environment rather than the code actually executing.
__version__ = "0.11.0"
