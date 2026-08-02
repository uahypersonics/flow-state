"""Transport core types."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


# --------------------------------------------------
# TransportSpec: serializable transport model definition
# --------------------------------------------------
@dataclass(frozen=True, slots=True)
class TransportSpec:
    """Canonical transport model specification."""

    model_type: str
    parameters: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        """Convert the transport specification to serialized data."""

        spec_dict = {
            "type": self.model_type,
            "parameters": dict(self.parameters),
        }

        return spec_dict

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TransportSpec:
        """Build a transport specification from serialized data."""

        model_type = str(data["type"]).strip().lower()
        raw_parameters = data["parameters"]
        if not isinstance(raw_parameters, dict):
            raise TypeError("transport_model.parameters must be a dictionary")

        parameters = {str(key): float(value) for key, value in raw_parameters.items()}
        spec = cls(
            model_type=model_type,
            parameters=parameters,
        )

        return spec


# --------------------------------------------------
# TransportModel: protocol for type hints
#
# the TransportModel protocol defines the expected interface for transport models,
# allowing us to use type hints to indicate that a function returns a valid transport model instance
#
# compile time/linter type check to verify that any class we use as a transport model has the required methods and attributes
# --------------------------------------------------
class TransportModel(Protocol):
    """
    Protocol for transport models.

    Enables return type hints like `-> TransportModel` so that registries
    and factories can guarantee they return a valid model instance.

    this uses structural subtyping (duck typing with type-checker support):
    any class that has these members is considered a valid TransportModel
    without needing to explicitly inherit from this class.
    """

    # --------------------------------------------------
    # required attributes
    # --------------------------------------------------

    # transport law identifier (e.g. "sutherland" or "power_law")
    model_type: str

    # --------------------------------------------------
    # required methods
    # --------------------------------------------------

    # function to compute dynamic viscosity (mu) given temperature
    def mu(self, temp: float) -> float:
        """Compute dynamic viscosity [Pa s] at temperature temp [K]."""
        ...

    # derivative of dynamic viscosity w.r.t. temperature (dmu/dT)
    def dmudt(self, temp: float) -> float:
        """Compute d(mu)/dT [Pa s / K] at temperature temp [K]."""
        ...

    # function to compute kinematic viscosity (nu) given temperature and density
    def nu(self, temp: float, dens: float) -> float:
        """Compute kinematic viscosity [m^2/s] at temp [K] and dens [kg/m^3]."""
        ...
