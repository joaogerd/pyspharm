# Stage 3 — Fortran source-form and interface modernization

## Goal

Make the legacy numerical core build through a modern free-form Fortran path
without altering SPHEREPACK algorithms, default-kind behavior, or the external
symbols used by F2PY.

## Source-form conversion

The historical Fortran 77 files in `src/*.f` are retained as provenance inputs.
During every Meson build, `tools/fortran/fixed_to_free.py` converts the audited
source list into temporary `.f90` files in the build directory.

The converter is intentionally mechanical:

- reads only fixed-form statement columns 7–72;
- preserves numeric labels;
- translates fixed-form continuation markers into free-form `&` continuations;
- preserves comments as `!` comments;
- rejects nonnumeric labels, blank statements and orphan continuations;
- does not edit expressions, variable names, COMMON blocks, precision or
  control flow.

Meson compiles only the generated free-form output. The original fixed-form
files are not part of the extension source list after this stage.

## Modern boundary modules

Two modern modules are compiled beside the generated legacy routines:

- `spharm_kinds` uses `iso_fortran_env`, exports `int32`, `real32` and
  `real64`, and uses `implicit none`.
- `spharm_legacy_interfaces` provides explicit interfaces for selected helper
  routines (`getlegfunc`, `specintrp`, `lap` and `invlap`) while leaving their
  external linker symbols unchanged.

New Fortran code must use these modules rather than relying on implicit kinds
or implicit external procedure declarations.

## Deliberate deferrals

Adding `implicit none` directly to every SPHEREPACK routine is not a mechanical
source-form change: the current files rely on implicit typing for many local
variables. Introducing it safely requires declarations for every routine and a
compiler-warning audit. That is a later substage, protected by
`legacy-contract-v1`.

Likewise, changing default `real` to `real64`, changing array layouts,
introducing modules around SPHEREPACK program units, or altering algorithms are
out of scope here because each could change the F2PY ABI or scientific results.

## Acceptance criteria

1. The converter validates all 30 audited sources.
2. A clean PEP 517 build generates and compiles the free-form outputs.
3. Wheel and sdist installations pass outside the source checkout.
4. `legacy-contract-v1` still passes on all supported Python versions.
