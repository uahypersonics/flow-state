"""Read metadata from HDF5 flow files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import h5py


def _to_python(value: Any) -> object:
    """Convert HDF5 scalar values to ordinary Python values."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if hasattr(value, "item"):
        try:
            return _to_python(value.item())
        except ValueError:
            pass
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def read_hdf5_attrs(path: str | Path) -> dict[str, object]:
    """Read root attributes from an HDF5 file without loading its datasets."""
    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(f"HDF5 file not found: {input_path}")

    try:
        with h5py.File(input_path, "r") as hdf5_file:
            return {key: _to_python(value) for key, value in hdf5_file.attrs.items()}
    except OSError as error:
        raise ValueError(f"Could not read HDF5 file {input_path}: {error}") from error
