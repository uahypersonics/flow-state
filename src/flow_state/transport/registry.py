"""Transport model registry and factory."""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from flow_state.transport.core import TransportModel, TransportSpec
from flow_state.transport.keyes import Keyes
from flow_state.transport.power_law import PowerLaw
from flow_state.transport.sutherland import Sutherland, SutherlandBlended, SutherlandLowTemp

# --------------------------------------------------
# model registry
# --------------------------------------------------
MODELS: dict[str, type] = {
    "sutherland": Sutherland,
    "sutherland_low_temp": SutherlandLowTemp,
    "sutherland_blended": SutherlandBlended,
    "keyes": Keyes,
    "power_law": PowerLaw,
}

MODEL_PARAMETERS: dict[str, tuple[str, ...]] = {
    "sutherland": ("mu_ref", "T_ref", "S"),
    "sutherland_low_temp": ("c1", "c2", "S", "T1", "T2"),
    "sutherland_blended": ("c1", "c2", "S"),
    "keyes": ("a0", "a1", "a2"),
    "power_law": ("mu_ref", "T_ref", "m"),
}

MODEL_PRESETS: dict[tuple[str, str], Callable[[], TransportModel]] = {
    ("sutherland", "air"): Sutherland.air,
    ("sutherland", "nitrogen"): Sutherland.nitrogen,
    ("sutherland_low_temp", "air"): SutherlandLowTemp.air,
    ("sutherland_blended", "air"): SutherlandBlended.air,
    ("keyes", "air"): Keyes.air,
    ("keyes", "nitrogen"): Keyes.nitrogen,
    ("power_law", "air"): PowerLaw.air,
}


# --------------------------------------------------
# get_transport_model: factory to instantiate transport models by name
# --------------------------------------------------
def get_transport_model(
    model_type: str,
    fluid: str = "air",
    **parameters: Any,
) -> TransportModel:
    """
    Get a transport model instance by name.

    Args:
        model_type: Model type (case-insensitive). One of:
            "sutherland", "sutherland_low_temp", "sutherland_blended",
            "keyes", "power_law"
        fluid: Fluid preset to use when no model parameters are provided.
        **parameters: Model-specific parameters. If none provided, uses the
            registered preset for the model type and fluid.
            For Sutherland: mu_ref, T_ref, S
            For Keyes: a0, a1, a2
            For PowerLaw: mu_ref, T_ref, m

    Returns:
        A transport model instance with mu() and nu() methods.

    Raises:
        ValueError: If model name is not recognized.

    Example:
        >>> model = get_transport_model("sutherland")  # uses .air() preset
        >>> mu = model.mu(300)

        >>> model = get_transport_model("keyes")
        >>> mu = model.mu(2000)  # high temperature
    """
    key = model_type.strip().lower()
    if key not in MODELS:
        available = ", ".join(MODELS.keys())
        raise ValueError(f"Unknown transport model type '{model_type}'. Available: {available}")

    if parameters:
        model_class = MODELS[key]
        model = model_class(**parameters)
    else:
        fluid_key = fluid.strip().lower()
        preset_key = (key, fluid_key)
        if preset_key not in MODEL_PRESETS:
            raise ValueError(f"No transport preset for type '{key}' and fluid '{fluid_key}'")
        model = MODEL_PRESETS[preset_key]()

    return model


# --------------------------------------------------
# transport model serialization
# --------------------------------------------------
def transport_model_to_spec(model: TransportModel) -> TransportSpec:
    """Convert a transport model to its canonical specification."""

    model_type = model.model_type
    if model_type not in MODEL_PARAMETERS:
        raise ValueError(f"Unsupported transport model type: {model_type}")

    parameter_names = MODEL_PARAMETERS[model_type]
    parameters = {
        parameter_name: float(getattr(model, parameter_name)) for parameter_name in parameter_names
    }
    spec = TransportSpec(
        model_type=model_type,
        parameters=parameters,
    )

    return spec


def transport_model_from_spec(spec: TransportSpec) -> TransportModel:
    """Reconstruct a transport model from its canonical specification."""

    model = get_transport_model(
        spec.model_type,
        **spec.parameters,
    )

    return model


def transport_model_from_dict(data: dict[str, object]) -> TransportModel:
    """Reconstruct a transport model from serialized specification data."""

    spec = TransportSpec.from_dict(data)
    model = transport_model_from_spec(spec)

    return model


# --------------------------------------------------
# available_transport_models: list available transport model names
# --------------------------------------------------
def available_transport_models() -> list[str]:
    """
    List available transport model names.

    Returns:
        List of model names that can be passed to get_transport_model().
    """
    return list(MODELS.keys())
