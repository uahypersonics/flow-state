"""Gas model registry and factory.

Maps gas name strings to (PerfectGas, default transport) pairs so that
callers only need to specify a name (e.g. "air", "n2") and get back both
the thermodynamic model and the matching viscosity law automatically.

Adding a new gas: add one entry to GAS_PRESETS and the alias table below.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from flow_state.gas.perfect import PerfectGas
from flow_state.transport.sutherland import Sutherland

# --------------------------------------------------
# gas presets: name -> (PerfectGas, default Sutherland transport)
# --------------------------------------------------
_GAS_PRESETS: dict[str, tuple[PerfectGas, Sutherland]] = {
    "air":      (PerfectGas.air(),      Sutherland.air()),
    "nitrogen": (PerfectGas.nitrogen(), Sutherland.nitrogen()),
}

# aliases: alternate names that resolve to the same preset key
_ALIASES: dict[str, str] = {
    "n2": "nitrogen",
}

# --------------------------------------------------
# get_gas: factory to resolve gas name to (gas, transport) pair
# --------------------------------------------------
def get_gas(name: str) -> tuple[PerfectGas, Sutherland]:
    """Return the (gas model, default transport model) for a named gas.

    Resolves aliases so both "n2" and "nitrogen" work.

    Args:
        name: Gas name string (case-insensitive). Supported: "air", "n2" / "nitrogen".

    Returns:
        Tuple of (PerfectGas, Sutherland) for the named gas.

    Raises:
        ValueError: If the name is not recognized.

    Examples:
        >>> gas, transport = get_gas("air")
        >>> gas, transport = get_gas("n2")
        >>> gas, transport = get_gas("nitrogen")
    """
    # normalize to lowercase
    key = name.lower()

    # resolve alias to canonical key
    key = _ALIASES.get(key, key)

    # look up preset
    if key not in _GAS_PRESETS:
        available = list(_GAS_PRESETS) + list(_ALIASES)
        raise ValueError(f"Unknown gas '{name}'. Available: {sorted(available)}")

    # return a fresh copy of the preset pair
    return _GAS_PRESETS[key]


# --------------------------------------------------
# available_gases: list recognized gas names including aliases
# --------------------------------------------------
def available_gases() -> list[str]:
    """Return all recognized gas name strings (including aliases).

    Returns:
        Sorted list of names accepted by get_gas().
    """
    return sorted(list(_GAS_PRESETS) + list(_ALIASES))
