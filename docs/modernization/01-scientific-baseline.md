# Stage 1 — scientific baseline contract

## Purpose

The historical SPHEREPACK implementation is the numerical reference for the
initial modernization.  Before changing build machinery, the Python interface
or the Fortran source form, we need reproducible evidence of its observable
behaviour.

This stage defines that evidence.  It does **not** certify that every legacy
behaviour is scientifically ideal; it prevents unintentional numerical changes
while later stages make the implementation maintainable.

## Reference suite `legacy-contract-v1`

The generator at `tests/reference/generate_legacy_baseline.py` evaluates four
small but representative configurations:

| Grid | Legendre workspace mode | `nlat` × `nlon` | Truncation |
| --- | --- | ---: | ---: |
| regular | stored | 32 × 64 | 21 |
| regular | computed | 32 × 64 | 21 |
| gaussian | stored | 32 × 64 | 21 |
| gaussian | computed | 32 × 64 | 21 |

For every configuration it records deterministic single-precision inputs and
outputs for:

- scalar grid-to-spectral and spectral-to-grid transforms;
- wind-to-vorticity/divergence and inverse wind reconstruction;
- associated Legendre functions;
- Gaussian latitudes and quadrature weights where applicable.

The scalar field and wind field are analytic combinations of longitude and
latitude.  They are deterministic, non-constant and exercise zonal and
meridional structure without relying on external data files.

## Snapshot format

A snapshot is an `.npz` file containing arrays and one JSON metadata string.
Metadata identifies the suite version, package version, Python version, NumPy
version, operating-system platform and the capture time.  Dynamic metadata is
informational only; numerical validation compares arrays, shapes and dtypes.

The intended committed location is:

```text
tests/reference/data/legacy-contract-v1.npz
```

The binary file must be captured from the designated legacy compatibility
commit and committed in its own reviewed change.  No code change may silently
replace it.

## Numerical acceptance policy

For the legacy single-precision contract:

- shapes and NumPy dtypes must match exactly;
- finite values must remain finite;
- numerical arrays are compared with `rtol=2e-5` and `atol=5e-6`;
- any larger difference requires an explicit issue, an explanation of the
  intended numerical change, and a deliberate update of the reference suite
  version.

The tolerances acknowledge compiler and platform variation in historical
single-precision Fortran.  They are intentionally much stricter than the
expected scientific error of the transforms.

## Capture and validation

From an installed editable checkout:

```bash
python tests/reference/generate_legacy_baseline.py \
  --output tests/reference/data/legacy-contract-v1.npz
python tests/reference/validate_legacy_baseline.py \
  --reference tests/reference/data/legacy-contract-v1.npz
```

The GitHub Actions workflow `capture-legacy-reference.yml` performs the same
steps and publishes the snapshot as an artifact for review.  It deliberately
does not overwrite a committed reference file.

## Stage-1 completion criteria

1. Provenance and mixed-license obligations are documented and retained.
2. The reference generator and validator run from an installed checkout.
3. A reviewed `legacy-contract-v1.npz` snapshot is committed.
4. Future CI verifies the snapshot before accepting implementation changes.

The first three source-controlled elements are added in this stage.  The
snapshot itself is intentionally produced by the repository's build environment
rather than fabricated manually, so the captured arrays always have a known
compiler and dependency provenance.
