"""Read serialized FlowState data from files."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flow_state.core import FlowState


# --------------------------------------------------
# read JSON output
# --------------------------------------------------
def read_json(path: str | Path) -> FlowState:
    """Read a FlowState from a canonical JSON file.

    Args:
        path: Path to a JSON file written by :func:`flow_state.io.write_json`.

    Returns:
        Reconstructed flow state.

    Raises:
        TypeError: If the JSON root is not an object.
    """

    # convert to Path object
    path = Path(path)

    # read
    text = path.read_text(encoding="utf-8")
    data: Any = json.loads(text)

    # validate the document root
    if not isinstance(data, dict):
        raise TypeError("FlowState JSON root must be an object")

    # build
    state = FlowState.from_dict(data)

    return state
