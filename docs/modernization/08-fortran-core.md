# Stage 8 — Real Fortran core modernization

## Motivation

Stage 3 introduced a safe build-time conversion from fixed-form F77 to
free-form `.f90` sources. That preserved numerical behavior and made the build
portable, but it did not replace the historical routines themselves with
maintained Fortran code. Stage 8 addresses that distinction in small,
independently validated units.

A Stage 8 unit must satisfy all of the following:

1. preserve the public Python and F2PY ABI;
2. retain the original F77 file as immutable provenance;
3. compile a real maintained Fortran implementation instead of the generated
   F77 conversion for the selected routine;
4. use explicit kinds, intents and `implicit none`;
5. document the mathematical contract and validate it independently;
6. pass `legacy-contract-v1` unchanged.

## Increment 8.1 — Laplacian operators

This increment replaces the compiled implementations of `lap` and `invlap`.
The historical `src/lap.f` and `src/invlap.f` are retained as reference files,
but Meson no longer passes them to the fixed-to-free converter.

The compiled replacement is `src/modern/spharm_spectral_operators.f90`:

- module procedures implement the scalar spherical Laplacian and inverse
  Laplacian with `real32` / `complex(real32)` data;
- compact triangular spectral storage is traversed explicitly using the
  documented `(m, n)` ordering;
- the global-mean coefficient has zero inverse Laplacian, exactly as before;
- external wrappers named `lap` and `invlap` retain the symbols expected by the
  existing F2PY interface and downstream callers.

The modern code intentionally uses the same analytical factors as the legacy
routines:

```text
L[n]      = -n(n + 1) / r²
L⁻¹[n>0]  = -r² / (n(n + 1))
L⁻¹[0]    = 0
```

## Verification

`tests/test_spectral_operators.py` checks:

- each factor against the analytical spectral formula;
- the compact triangular coefficient ordering;
- the zero global-mean convention;
- `invlap(lap(x)) = x` for every non-mean coefficient.

The normal CI matrix also compiles the F2PY extension, runs the complete
regression suite, validates `legacy-contract-v1`, installs wheel and sdist
artifacts outside the checkout, and runs manylinux wheel tests.

## Follow-on units

Future Stage 8 increments should modernize only similarly isolated routines.
The likely order is:

1. `multsmoothfact` — scalar coefficient-wise smoothing;
2. `getlegfunc` and `specintrp` — associated-Legendre values and point
   interpolation;
3. compact/expanded spectral-array conversion helpers;
4. larger SPHEREPACK kernels only after the smaller routines establish the
   wrapper and verification pattern.
