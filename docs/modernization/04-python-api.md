# Stage 4 — maintained Python API

## Goal

Provide a stable, typed and maintainable public interface without changing the
numerical behavior of the historical `spharm.Spharmt` implementation.

The new import is:

```python
import pyspharm
```

The existing `import spharm` and `spharm.Spharmt` interfaces remain supported
as compatibility APIs during the migration period.

## Main API

```python
transform = pyspharm.SphericalHarmonicTransform(
    nlon=360,
    nlat=181,
    grid="regular",
    legendre="stored",
)

field = pyspharm.as_real32(field_from_application)
coefficients = transform.analyze_scalar(field, truncation=90)
restored_field = transform.synthesize_scalar(coefficients)
```

For winds:

```python
u = pyspharm.as_real32(zonal_wind)
v = pyspharm.as_real32(meridional_wind)
vorticity, divergence = transform.analyze_wind(u, v, truncation=90)
u_restored, v_restored = transform.synthesize_wind(vorticity, divergence)
```

## Precision contract

The retained SPHEREPACK/F2PY ABI uses single precision.  Therefore:

- scalar fields and winds passed to transform methods must be `float32`;
- spectral coefficients passed to transform methods must be `complex64`;
- the API returns `float32` fields and `complex64` coefficients;
- `as_real32` and `as_complex64` are explicit conversion utilities for
  application boundaries.

The API does not silently downcast inside a transform method.  Passing a
`float64` field raises `pyspharm.PrecisionError`, making a precision decision
visible in user code and reviews.

## Naming migration

| Historical compatibility API | Maintained API |
| --- | --- |
| `spharm.Spharmt(nlon, nlat, rsphere=..., gridtype=..., legfunc=...)` | `pyspharm.SphericalHarmonicTransform(nlon, nlat, radius=..., grid=..., legendre=...)` |
| `grdtospec(field, ntrunc=...)` | `analyze_scalar(field, truncation=...)` |
| `spectogrd(coefficients)` | `synthesize_scalar(coefficients)` |
| `getvrtdivspec(u, v, ntrunc=...)` | `analyze_wind(u, v, truncation=...)` |
| `getuv(vorticity, divergence)` | `synthesize_wind(vorticity, divergence)` |

## Scope boundary

This stage is an adapter layer.  It delegates all transforms to the legacy
engine and does not replace the numerical routines.  New methods should be
added here first, with a direct mapping to a tested compatibility routine.  A
future API-major release may deprecate `spharm`, but only after real-user
migration feedback and a documented support window.
