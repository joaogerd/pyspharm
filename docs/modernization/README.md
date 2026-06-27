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
3. **Fortran modernization without numerical change**
   - migrate fixed-form Fortran sources to free-form Fortran;
   - introduce explicit interfaces, kinds and `implicit none`;
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
7. **Scientific diagnostic API**
   - expose frequently used legacy diagnostics through the validated
     `pyspharm` interface;
   - preserve the explicit single-precision boundary and the Stage 1 numerical
     contract;
   - add one independently documented and equivalence-tested diagnostic at a
     time before considering broader API parity.

Each stage is accepted only when its scope is tested and documented. Later
stages may refine implementation details but must not silently weaken the
scientific reference contract created in stage 1.
