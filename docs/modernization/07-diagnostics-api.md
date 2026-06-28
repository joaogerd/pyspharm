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

## Increment 7.3 — grid metadata and point interpolation

The third increment completes the migration of the bundled examples away from
direct `spharm` imports by adding:

- `gaussian_latitudes_weights(nlat)` for Gaussian latitude coordinates in
  degrees north and quadrature weights;
- `spectral_indices(truncation)` for compact triangular coefficient metadata;
- `geodesic_points(edge_points)` for icosahedral geodesic coordinates;
- `interpolate_scalar(coefficients, latitude=..., longitude=...)` for one
  scalar spectrum at one point.

The utilities preserve documented legacy units and numerical values. Grid
metadata remains `float64`, while geodesic coordinates are `float32` and point
interpolation requires an explicit `complex64` spectral boundary. Their
results are directly compared to their legacy counterparts.

## Scientific and compatibility boundary

The diagnostic methods delegate directly to `spharm.Spharmt.getgrad` and
`spharm.Spharmt.getpsichi`. The regridding helper delegates to
`spharm.regrid`. Grid and point utilities delegate to `spharm` helpers.
None of the Stage 7 methods reimplement Laplacian inversion, vector
spherical-harmonic analysis, spectral interpolation or synthesis in Python.

Acceptance requires modern-API outputs to agree with the corresponding legacy
calls for regular and Gaussian test cases, while the full legacy reference
contract continues to pass unchanged. Examples are acceptance-tested as
executable scripts in their non-plotting mode.

## Follow-on candidate

A future Stage 7 increment may expose isotropic spectral smoothing through a
validated `SphericalHarmonicTransform` method. It should be documented and
tested independently against `Spharmt.specsmooth` before integration.
