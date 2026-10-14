"""Recover a complete flow state from HDF5 metadata."""

from __future__ import annotations

import ast
import math
import re
from pathlib import Path

from flow_state.core import FlowState
from flow_state.gas import PerfectGas
from flow_state.gas.registry import get_gas
from flow_state.io.hdf5 import read_hdf5_attrs
from flow_state.solvers import solve
from flow_state.transport import TransportModel, get_transport_model

_ALIASES = {
    "alt": "altitude",
    "altitude": "altitude",
    "gas": "gas_model",
    "gas_model": "gas_model",
    "gamma": "gamma",
    "lref": "lref",
    "m": "mach",
    "mach": "mach",
    "mach_inf": "mach",
    "p": "pres",
    "p_inf": "pres",
    "pres": "pres",
    "pres_inf": "pres",
    "p0": "pres_stag",
    "pres_stag": "pres_stag",
    "pr": "pr",
    "r_gas": "r_gas",
    "re1": "re1",
    "rgas": "r_gas",
    "t": "temp",
    "t_inf": "temp",
    "temp": "temp",
    "temp_fs": "temp",
    "temp_inf": "temp",
    "t0": "temp_stag",
    "temp_stag": "temp_stag",
    "transport_model": "transport_model",
    "visc_law": "transport_model",
    "viscosity_law": "transport_model",
}

_NUMERIC_FIELDS = {
    "altitude",
    "gamma",
    "lref",
    "mach",
    "pres",
    "pres_stag",
    "pr",
    "r_gas",
    "re1",
    "temp",
    "temp_stag",
}

_SOLVER_COMBINATIONS = (
    ("pres", "temp", "mach"),
    ("pres", "temp", "uvel"),
    ("mach", "pres_stag", "temp_stag"),
    ("re1", "temp", "mach"),
    ("re1", "pres", "mach"),
    ("re1", "pres_stag", "temp_stag"),
    ("re1", "mach", "temp_stag"),
    ("altitude", "mach"),
    ("re1", "mach"),
)


def _attribute_name(key: str) -> str:
    """Extract and normalize an attribute's short name."""
    match = re.search(r";\s*([A-Za-z][A-Za-z0-9_]*)", key)
    name = match.group(1) if match else key
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")


def _number(value: object) -> float | None:
    """Return a scalar numeric metadata value, including unit-tagged pairs."""
    if isinstance(value, str):
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            try:
                return float(value)
            except ValueError:
                return None
    if isinstance(value, (list, tuple)):
        if len(value) != 2:
            return None
        value = value[0]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def normalize_hdf5_attrs(attrs: dict[str, object]) -> dict[str, object]:
    """Map current and legacy HDF5 attribute names to flow-state names."""
    normalized: dict[str, object] = {}
    priorities: dict[str, int] = {}

    for original_key, value in attrs.items():
        short_name = _attribute_name(original_key)
        canonical_name = _ALIASES.get(short_name)
        if canonical_name is None:
            continue

        if canonical_name in _NUMERIC_FIELDS:
            normalized_value: object | None = _number(value)
        elif isinstance(value, bytes):
            normalized_value = value.decode("utf-8")
        elif isinstance(value, str):
            normalized_value = value.strip().lower()
        else:
            normalized_value = None

        if normalized_value is None:
            continue

        priority = 2 if short_name == canonical_name else 1
        if priority >= priorities.get(canonical_name, 0):
            normalized[canonical_name] = normalized_value
            priorities[canonical_name] = priority

    return normalized


def _gas_from_metadata(metadata: dict[str, object]) -> PerfectGas | str | None:
    gas_name = metadata.get("gas_model")
    if isinstance(gas_name, str):
        try:
            get_gas(gas_name)
        except ValueError:
            pass
        else:
            return gas_name

    gamma = metadata.get("gamma")
    r_gas = metadata.get("r_gas")
    if isinstance(gamma, float) and isinstance(r_gas, float):
        if math.isclose(gamma, 1.4) and math.isclose(r_gas, 287.15):
            return "air"
        if math.isclose(gamma, 1.4) and math.isclose(r_gas, 296.8):
            return "nitrogen"
        return PerfectGas.custom(gamma, r_gas, name=gas_name or "custom")

    model_name = metadata.get("transport_model")
    if isinstance(model_name, str):
        _, fluid = _transport_parts(model_name)
        if fluid is not None:
            return fluid
    return gas_name if isinstance(gas_name, str) else None


def _transport_parts(model_name: str) -> tuple[str, str | None]:
    """Split legacy transport names such as ``sutherland_nitrogen``."""
    for suffix, fluid in (
        ("_nitrogen", "nitrogen"),
        ("_air", "air"),
        ("_n2", "nitrogen"),
    ):
        if model_name.endswith(suffix):
            return model_name.removesuffix(suffix), fluid
    return model_name, None


def _transport_from_metadata(
    metadata: dict[str, object],
    gas: PerfectGas | str | None,
) -> TransportModel | None:
    model_name = metadata.get("transport_model")
    if not isinstance(model_name, str):
        return None
    model_name, legacy_fluid = _transport_parts(model_name)
    fluid = legacy_fluid or (gas if isinstance(gas, str) else "air")
    return get_transport_model(model_name, fluid=fluid)


def _solver_inputs(metadata: dict[str, object]) -> dict[str, object]:
    for combination in _SOLVER_COMBINATIONS:
        if all(key in metadata for key in combination):
            return {key: metadata[key] for key in combination}

    available = ", ".join(sorted(metadata)) or "none"
    combinations = "; ".join(" + ".join(keys) for keys in _SOLVER_COMBINATIONS)
    raise ValueError(
        "HDF5 metadata does not contain a complete flow-state input combination. "
        f"Recognized attributes: {available}. Supported combinations: {combinations}"
    )


def recover_from_hdf5(path: str | Path) -> FlowState:
    """Recover a complete ``FlowState`` from HDF5 root attributes."""
    input_path = Path(path)
    attributes = read_hdf5_attrs(input_path)
    metadata = normalize_hdf5_attrs(attributes)
    solve_kwargs = _solver_inputs(metadata)

    gas = _gas_from_metadata(metadata)
    if gas is not None:
        solve_kwargs["gas"] = gas
    transport = _transport_from_metadata(metadata, gas)
    if transport is not None:
        solve_kwargs["transport"] = transport
    for optional_key in ("lref", "pr"):
        if optional_key in metadata:
            solve_kwargs[optional_key] = metadata[optional_key]

    state = solve(**solve_kwargs)
    if state.provenance is None:
        state.provenance = {}
    state.provenance["recovered_from"] = str(input_path)
    state.provenance["hdf5_attributes"] = sorted(attributes)
    return state
