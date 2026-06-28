# Stage 7 — Modern diagnostic API and executable examples

## Objective

Extend the maintained :mod:`pyspharm` interface with common atmospheric
spectral diagnostics already implemented by the historical :mod:`spharm`
engine. The stage improves usability without changing SPHEREPACK routines,
the single-precision ABI or the Stage 1 legacy numerical contract.

## Increment 7.1 — diagnostic methods

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

## Increment 7.2 — regridding and examples

The second increment adds:

- `pyspharm.regrid_scalar(source, destination, field, ...)`, a validated
  maintained facade over scalar spectral regridding;
- command-line examples for scalar regridding, geodesic points, a spherical
  harmonic basis field and the Galewsky shallow-water test case;
- smoke tests that execute the numerical mode of every example without
  requiring a plotting library.

The examples default to bounded, reproducible numerical work. Plotting is
optional through `--output` or `--show`, and is the only feature that needs the
`examples` optional dependency group.

## Scientific and compatibility boundary

The diagnostic methods delegate directly to `spharm.Spharmt.getgrad` and
`spharm.Spharmt.getpsichi`. The regridding helper delegates to
`spharm.regrid`. None of the Stage 7 methods reimplement Laplacian inversion,
vector spherical-harmonic analysis, spectral interpolation or synthesis in
Python.

Acceptance requires modern-API outputs to agree with the corresponding legacy
calls for regular and Gaussian test cases, while the full legacy reference
contract continues to pass unchanged. Examples are acceptance-tested as
executable scripts in their non-plotting mode.

## Follow-on candidates

Later Stage 7 increments may expose spectral smoothing, Gaussian
latitude/weight helpers, coefficient-index utilities and point interpolation.
Each addition must be independently documented and tested against the
compatibility engine.
