# pyspharm-ng modernization program

This directory records the staged modernization of the historical `pyspharm`
code base into a maintained, redistributable scientific package.

The work is deliberately incremental. Numerical correctness and compatibility
with the legacy SPHEREPACK-based implementation take precedence over stylistic
or performance changes.

## Stages

1. **Foundation and scientific baseline**
   - preserve provenance and licensing obligations;
   - document the mixed-license distribution;
   - define deterministic reference cases and a reproducible snapshot format;
   - provide tooling to capture and validate legacy numerical results.
2. **Modern Python packaging and compatibility repair**
   - complete the Meson/PEP 517 transition;
   - remove obsolete `numpy.distutils` build paths;
   - repair Python 3 integer-size handling and package-local extension imports;
   - establish isolated wheel and source-distribution installation tests.
3. **Fortran build-path modernization**
   - migrate fixed-form Fortran sources to free-form generated sources;
   - introduce shared kinds and selected external interfaces;
   - retain the legacy numerical contract proven by the reference suite.
4. **Modern public API and compatibility layer**
   - introduce the maintained `pyspharm` API;
   - preserve `spharm` imports and the historical `Spharmt` interface while
     they remain useful to downstream users.
5. **Portable release engineering**
   - build wheels through CI;
   - publish reproducible source distributions and wheels;
   - add release notes, versioning policy and deprecation policy.
6. **Stable release**
   - publish a documented stable release once supported platforms and the
     numerical compatibility contract are continuously verified.
7. **Scientific API and executable examples**
   - expose frequently used legacy diagnostics, scalar regridding, grid
     metadata and point interpolation through the validated `pyspharm`
     interface;
   - preserve the explicit single-precision boundary and the Stage 1 numerical
     contract;
   - make representative scientific examples executable, parameterized and
     smoke-tested without optional plotting dependencies or compatibility-module
     imports;
   - add further API parity only through independent documentation and
     equivalence tests.
8. **Real Fortran core modernization**
   - replace selected compiled F77 routines with maintained free-form Fortran
     modules while keeping the F77 files as provenance;
   - preserve F2PY external symbols through thin ABI wrappers;
   - modernize one mathematically isolated unit at a time with direct numerical
     regression tests and `legacy-contract-v1` as the release gate.

Each stage is accepted only when its scope is tested and documented. Later
stages may refine implementation details but must not silently weaken the
scientific reference contract created in stage 1.
