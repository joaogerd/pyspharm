"""Create and validate deterministic numerical reference data.

The reference contract intentionally exercises the public legacy API.  It does
not access private work arrays or Fortran entry points directly, so it remains
useful while the implementation moves from F77/F2PY to a modern backend.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
from typing import Any

import numpy as np

CONTRACT_VERSION = "legacy-contract-v1"
DEFAULT_RTOL = 2.0e-5
DEFAULT_ATOL = 5.0e-6


@dataclass(frozen=True)
class ReferenceCase:
    """One compact but representative spherical-harmonic configuration."""

    gridtype: str
    legfunc: str
    nlat: int = 32
    nlon: int = 64
    ntrunc: int = 21

    @property
    def key(self) -> str:
        return (
            f"{self.gridtype}_{self.legfunc}_"
            f"n{self.nlat}x{self.nlon}_t{self.ntrunc}"
        )


CASES = (
    ReferenceCase("regular", "stored"),
    ReferenceCase("regular", "computed"),
    ReferenceCase("gaussian", "stored"),
    ReferenceCase("gaussian", "computed"),
)


def _import_spharm() -> Any:
    """Import the legacy public module with an actionable error message."""

    try:
        import spharm
    except ImportError as exc:  # pragma: no cover - exercised by CLI users
        raise RuntimeError(
            "Unable to import 'spharm'. Install this checkout first, for example "
            "with 'python -m pip install -e .'."
        ) from exc
    return spharm


def _coordinates(case: ReferenceCase, spharm: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    """Return latitude, longitude and optional Gaussian quadrature weights."""

    if case.gridtype == "gaussian":
        latitudes, weights = spharm.gaussian_lats_wts(case.nlat)
        return (
            np.asarray(latitudes, dtype=np.float64),
            np.linspace(0.0, 360.0, case.nlon, endpoint=False, dtype=np.float64),
            np.asarray(weights, dtype=np.float64),
        )

    return (
        np.linspace(90.0, -90.0, case.nlat, dtype=np.float64),
        np.linspace(0.0, 360.0, case.nlon, endpoint=False, dtype=np.float64),
        None,
    )


def _analytic_fields(latitudes: np.ndarray, longitudes: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return deterministic scalar and vector fields in legacy single precision."""

    latitude = np.deg2rad(latitudes)[:, np.newaxis]
    longitude = np.deg2rad(longitudes)[np.newaxis, :]

    scalar = (
        1.25
        + 0.65 * np.sin(latitude)
        + 0.35 * np.cos(2.0 * longitude) * np.cos(latitude) ** 2
        + 0.15 * np.sin(3.0 * longitude) * np.sin(2.0 * latitude)
    )
    zonal_wind = (
        8.0 * np.cos(latitude) * np.cos(longitude)
        + 1.5 * np.sin(2.0 * latitude) * np.sin(2.0 * longitude)
    )
    meridional_wind = (
        5.0 * np.sin(latitude) * np.sin(longitude)
        - 1.0 * np.cos(2.0 * latitude) * np.cos(3.0 * longitude)
    )

    return tuple(np.asarray(field, dtype=np.float32, order="F") for field in (scalar, zonal_wind, meridional_wind))


def build_payload() -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Evaluate the complete reference suite through the public legacy API."""

    spharm = _import_spharm()
    payload: dict[str, np.ndarray] = {}

    for case in CASES:
        latitudes, longitudes, weights = _coordinates(case, spharm)
        scalar, zonal_wind, meridional_wind = _analytic_fields(latitudes, longitudes)
        transform = spharm.Spharmt(
            case.nlon,
            case.nlat,
            gridtype=case.gridtype,
            legfunc=case.legfunc,
        )

        scalar_spectrum = transform.grdtospec(scalar, case.ntrunc)
        scalar_roundtrip = transform.spectogrd(scalar_spectrum)
        vorticity_spectrum, divergence_spectrum = transform.getvrtdivspec(
            zonal_wind,
            meridional_wind,
            case.ntrunc,
        )
        zonal_roundtrip, meridional_roundtrip = transform.getuv(
            vorticity_spectrum,
            divergence_spectrum,
        )
        legendre = spharm.legendre(15.0, case.ntrunc)

        prefix = case.key
        payload[f"{prefix}/latitudes"] = latitudes
        payload[f"{prefix}/longitudes"] = longitudes
        payload[f"{prefix}/scalar_input"] = scalar
        payload[f"{prefix}/scalar_spectrum"] = np.asarray(scalar_spectrum)
        payload[f"{prefix}/scalar_roundtrip"] = np.asarray(scalar_roundtrip)
        payload[f"{prefix}/zonal_wind_input"] = zonal_wind
        payload[f"{prefix}/meridional_wind_input"] = meridional_wind
        payload[f"{prefix}/vorticity_spectrum"] = np.asarray(vorticity_spectrum)
        payload[f"{prefix}/divergence_spectrum"] = np.asarray(divergence_spectrum)
        payload[f"{prefix}/zonal_wind_roundtrip"] = np.asarray(zonal_roundtrip)
        payload[f"{prefix}/meridional_wind_roundtrip"] = np.asarray(meridional_roundtrip)
        payload[f"{prefix}/legendre_lat15"] = np.asarray(legendre)
        if weights is not None:
            payload[f"{prefix}/gaussian_weights"] = weights

    metadata = {
        "contract_version": CONTRACT_VERSION,
        "cases": [asdict(case) for case in CASES],
        "package_version": getattr(spharm, "__version__", "unknown"),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "platform": platform.platform(),
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    return payload, metadata


def write_snapshot(path: str | Path, *, overwrite: bool = False) -> Path:
    """Write a compressed reference snapshot and return its resolved path."""

    destination = Path(path)
    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to replace existing reference snapshot: {destination}. "
            "Use --force only after scientific review."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload, metadata = build_payload()
    np.savez_compressed(
        destination,
        metadata_json=np.asarray(json.dumps(metadata, sort_keys=True)),
        **payload,
    )
    return destination


def read_snapshot(path: str | Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Read a reference snapshot without allowing pickle deserialization."""

    with np.load(Path(path), allow_pickle=False) as snapshot:
        if "metadata_json" not in snapshot.files:
            raise ValueError("Reference snapshot does not contain metadata_json")
        metadata = json.loads(str(snapshot["metadata_json"].item()))
        payload = {
            name: np.asarray(snapshot[name])
            for name in snapshot.files
            if name != "metadata_json"
        }
    return payload, metadata


def validate_snapshot(
    path: str | Path,
    *,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> None:
    """Recompute the contract and compare it with a committed snapshot."""

    expected, metadata = read_snapshot(path)
    if metadata.get("contract_version") != CONTRACT_VERSION:
        raise ValueError(
            "Unexpected reference contract version: "
            f"{metadata.get('contract_version')!r}"
        )

    actual, _ = build_payload()
    if expected.keys() != actual.keys():
        missing = sorted(expected.keys() - actual.keys())
        extra = sorted(actual.keys() - expected.keys())
        raise AssertionError(f"Reference keys changed; missing={missing}, extra={extra}")

    for name in sorted(expected):
        expected_array = expected[name]
        actual_array = actual[name]
        if expected_array.shape != actual_array.shape:
            raise AssertionError(
                f"{name}: expected shape {expected_array.shape}, got {actual_array.shape}"
            )
        if expected_array.dtype != actual_array.dtype:
            raise AssertionError(
                f"{name}: expected dtype {expected_array.dtype}, got {actual_array.dtype}"
            )
        if not np.all(np.isfinite(actual_array)):
            raise AssertionError(f"{name}: computation produced NaN or infinity")
        np.testing.assert_allclose(
            actual_array,
            expected_array,
            rtol=rtol,
            atol=atol,
            err_msg=f"Legacy numerical contract changed for {name}",
        )
