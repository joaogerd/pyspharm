# Stage 5 — portable release engineering

## Objective

Turn the validated source tree into auditable release artifacts without
publishing automatically to external package indexes.

## Continuous wheel validation

`build-linux-wheels.yml` builds Linux x86_64 wheels for CPython 3.10, 3.11 and
3.12 with `cibuildwheel` in a manylinux-compatible image. The build image
installs `gcc-gfortran`, which is required by the SPHEREPACK/F2PY extension.

Each wheel is installed in cibuildwheel's isolated test environment. The smoke
test imports both `spharm` and `pyspharm`, verifies the package-local extension,
and performs scalar transforms through both APIs. The wheel files are uploaded
as CI artifacts for inspection.

The initial binary support scope is intentionally narrow: Linux x86_64 only.
The source distribution remains the installation path for other platforms until
they gain equivalent CI coverage.

## Stable release workflow

`create-github-release.yml` starts from an existing `vX.Y.Z` tag. It performs
these jobs in order:

1. validate that the tag, project version and changelog agree;
2. build and install-test the source distribution outside the checkout;
3. build and install-test the portable Linux wheels;
4. attach the verified artifacts to a GitHub Release.

The tag validator rejects development and pre-release versions. Therefore the
current `0.1.0.dev0` development line cannot accidentally create a public
stable release.

The workflow has no PyPI upload step. Publication to PyPI is a separate future
change, after choosing and reviewing a trusted-publishing configuration.

## Integration model

`develop` is the integration branch for the modernization series. Feature PRs
are reviewed against it; the final stable-release integration into `master`
occurs only after the staged acceptance criteria are complete.

## Acceptance criteria

1. Standard source CI remains green on CPython 3.10–3.12.
2. Portable-wheel CI produces and tests one wheel per supported CPython.
3. Stable-tag validation rejects mismatched, development and undocumented
   versions.
4. Release workflow never uploads to PyPI without a separately reviewed
   publishing change.
