# API Reference

Technical reference for the `flow_state` package.

## Modules

- [FlowState](core.md): The main dataclass containing flow properties
- [Solvers](solvers.md): The `solve()` function and input combinations
- [Atmosphere](atmosphere.md): Atmosphere models and `AtmosphereState`
- [Transport](transport.md): Viscosity models (Sutherland, Keyes, etc.)

## Package Architecture

![flow_state architecture](../assets/architecture.svg)

[Download architecture (SVG)](../assets/architecture.svg){ .md-button download="flow_state_architecture.svg" }
[View in browser](../assets/architecture.svg){ .md-button target="_blank" }

??? info "Regenerate"

    ```bash
    pydeps src/flow_state --noshow --max-bacon=4 --cluster -o docs/assets/architecture.svg
    ```
