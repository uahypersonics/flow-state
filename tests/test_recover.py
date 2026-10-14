"""Tests for recovering flow conditions from HDF5 metadata."""

from __future__ import annotations

from pathlib import Path

import h5py
import pytest

from flow_state.recover import normalize_hdf5_attrs, recover_from_hdf5


def _write_attrs(path: Path, attrs: dict[str, object]) -> None:
    with h5py.File(path, "w") as hdf5_file:
        for key, value in attrs.items():
            hdf5_file.attrs[key] = value


def test_normalize_hdf5_attrs_supports_legacy_short_names() -> None:
    attrs = {
        "mach number               ; m             (-)": 5.3,
        "stagnation pressure       ; p0           (Pa)": 1_362_869.0,
        "stagnation temperature    ; t0            (k)": 450.0,
        "gas constant              ; rgas   (j/(kg k))": 287.15,
    }

    assert normalize_hdf5_attrs(attrs) == {
        "mach": 5.3,
        "pres_stag": 1_362_869.0,
        "temp_stag": 450.0,
        "r_gas": 287.15,
    }


def test_recover_prefers_complete_static_state_when_metadata_is_redundant(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "base_flow.hdf5"
    _write_attrs(
        input_path,
        {
            "mach": 6.0,
            "pres_inf": 466.1657778752394,
            "temp_inf": 45.73170731707317,
            "re1": 10_000_000.0,
            "gamma": 1.4,
            "rgas": 287.15,
            "visc_law": "sutherland",
            "pr": 0.71,
        },
    )

    state = recover_from_hdf5(input_path)

    assert state.mach == pytest.approx(6.0)
    assert state.pres == pytest.approx(466.1657778752394)
    assert state.temp == pytest.approx(45.73170731707317)
    assert state.re1 == pytest.approx(10_000_000.0, rel=1e-3)
    assert state.gas_model == "air"
    assert state.transport_model is not None
    assert state.transport_model.model_type == "sutherland"
    assert state.provenance is not None
    assert state.provenance["builder"] == "from_mach_pres_temp"
    assert state.provenance["recovered_from"] == str(input_path)


def test_recover_uses_legacy_stagnation_attributes(tmp_path: Path) -> None:
    input_path = tmp_path / "base_flow.hdf5"
    _write_attrs(
        input_path,
        {
            "mach number               ; m             (-)": 5.3,
            "unit reynolds number      ; re1         (1/m)": 17_900_000.0,
            "stagnation pressure       ; p0           (Pa)": 1_362_869.3601819817,
            "stagnation temperature    ; t0            (k)": 450.0,
            "heat capacity ratio       ; gamma         (-)": 1.4,
            "gas constant              ; rgas   (j/(kg k))": 287.15,
        },
    )

    state = recover_from_hdf5(input_path)

    assert state.mach == pytest.approx(5.3)
    assert state.pres_stag == pytest.approx(1_362_869.3601819817)
    assert state.temp_stag == pytest.approx(450.0)
    assert state.provenance is not None
    assert state.provenance["builder"] == "from_mach_pres_stag_temp_stag"


def test_recover_supports_legacy_fluid_specific_transport_name(tmp_path: Path) -> None:
    input_path = tmp_path / "base_flow.hdf5"
    _write_attrs(
        input_path,
        {
            "mach": 6.0,
            "pres_inf": 500.0,
            "temp_inf": 50.0,
            "visc_law": "sutherland_nitrogen",
        },
    )

    state = recover_from_hdf5(input_path)

    assert state.gas_model == "nitrogen"
    assert state.r_gas == pytest.approx(296.8)
    assert state.transport_model is not None
    assert state.transport_model.model_type == "sutherland"
    assert state.transport_model.parameters["S"] == pytest.approx(106.7)


def test_recover_rejects_insufficient_metadata(tmp_path: Path) -> None:
    input_path = tmp_path / "base_flow.hdf5"
    _write_attrs(input_path, {"mach": 6.0, "gamma": 1.4})

    with pytest.raises(ValueError, match="does not contain a complete"):
        recover_from_hdf5(input_path)
