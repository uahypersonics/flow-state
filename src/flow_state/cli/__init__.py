"""Command-line interface for flow-state."""

from flow_state.cli.app import app

# Preserve the existing ``flow_state.cli:cli`` console entry point.
cli = app

__all__ = ["app", "cli"]
