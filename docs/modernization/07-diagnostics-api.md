# Stage 7 — Modern diagnostic API

## Objective

Extend the maintained :mod:`pyspharm` interface with common atmospheric
spectral diagnostics already implemented by the historical :mod:`spharm`
engine. The stage improves usability without changing SPHEREPACK routines,
the single-precision ABI or the Stage 1 legacy numerical contract.

## Initial public methods

The first increment introduces two operations on
`SphericalHarmonicTransform`:

- `gradient(coefficients)`: synthesize the zonal and meridional components of
a scalar field gradient from complex spectral coefficients;
- `streamfunction_velocity_potential(zonal_wind, meridional_wind,
  truncation=...)`: diagnose gridded streamfunction and velocity potential
  from horizontal wind.

Both methods preserve the existing explicit precision boundary:

- gridded input is `float32` with shape `(nlat, nlon)` or
  `(nlat, nlon, nt)`;
- spectral input is `complex64` with triangular coefficient dimension;
- outputs are Fortran-contiguous `float32` arrays;
- non-finite values and incompatible shapes are rejected before delegation.

## Scientific and compatibility boundary

The methods delegate directly to `spharm.Spharmt.getgrad` and
`spharm.Spharmt.getpsichi`. They do not reimplement Laplacian inversion,
vector spherical-harmonic analysis or synthesis in Python.

Acceptance requires modern-API outputs to agree with the corresponding legacy
calls for regular and Gaussian test cases, while the full legacy reference
contract continues to pass unchanged.

## Follow-on candidates

Later Stage 7 increments may expose spectral smoothing, regridding, Gaussian
latitude/weight helpers and coefficient-index utilities. Each addition must
be independently documented and tested against the compatibility engine.
