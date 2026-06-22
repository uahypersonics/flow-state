"""Bundled example config files for the flow-state CLI.

Provides a registry mapping short names to TOML files stored as
package data under flow_state/examples/. The CLI ``examples`` command
uses this module to list available examples and copy them to the CWD.

Adding a new example
--------------------
1. Add a TOML file to ``src/flow_state/examples/<name>.toml``.
2. Add one entry to ``EXAMPLES_REGISTRY`` below.
3. Add a symlink in ``examples/configs/`` pointing to the new file.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from importlib.resources import files

# --------------------------------------------------
# registry: short name -> (filename, one-line description)
#
# keep entries sorted alphabetically by key for clean list output
# --------------------------------------------------
EXAMPLES_REGISTRY: dict[str, tuple[str, str]] = {
    "aedc_t9": (
        "aedc_t9.toml",
        "AEDC Tunnel 9 — Mach 9.86, nitrogen, freestream conditions",
    ),
    "bam6qt": (
        "bam6qt.toml",
        "BAM6QT Mach 6 Quiet Tunnel (Purdue) — Mach 6, air, stag conditions",
    ),
    "sandia": (
        "sandia.toml",
        "Sandia Hypersonic Wind Tunnel — Mach 5, air, stag conditions",
    ),
    "stort": (
        "stort.toml",
        "STORT flight — Mach 7.1, 33.2 km altitude",
    ),
}


# --------------------------------------------------
# list_examples: return {name: description} for all registered examples
# --------------------------------------------------
def list_examples() -> dict[str, str]:
    """Return a name -> description mapping for all available examples.

    Returns:
        Dict of {name: description} sorted alphabetically by name.
    """
    # build sorted dict for consistent display order
    return {name: desc for name, (_, desc) in sorted(EXAMPLES_REGISTRY.items())}


# --------------------------------------------------
# get_example_text: return TOML text for a named example
# --------------------------------------------------
def get_example_text(name: str) -> str:
    """Return the TOML text of a named example config.

    Args:
        name: Short example name (e.g. "bam6qt"). Case-insensitive.

    Returns:
        TOML file contents as a string.

    Raises:
        KeyError: If ``name`` is not in the registry.
    """
    # normalize name
    key = name.lower()

    # look up registry
    if key not in EXAMPLES_REGISTRY:
        raise KeyError(key)

    # read file from package data
    filename, _ = EXAMPLES_REGISTRY[key]
    return (files("flow_state") / "examples" / filename).read_text(encoding="utf-8")


# --------------------------------------------------
# available_example_names: convenience list for validation / help text
# --------------------------------------------------
def available_example_names() -> list[str]:
    """Return sorted list of registered example names.

    Returns:
        Sorted list of names accepted by get_example_text().
    """
    return sorted(EXAMPLES_REGISTRY.keys())
