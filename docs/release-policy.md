# Release and compatibility policy

## Scope of the first supported release line

The first maintained binary release targets:

- CPython 3.10, 3.11 and 3.12;
- x86_64 GNU/Linux wheels built in a manylinux-compatible environment;
- source distributions for platforms with a compatible C compiler and
  `gfortran`.

macOS, Windows, ARM and alternative Python implementations are not silently
claimed as supported. They may be added only after CI builds and installs a
wheel for each target.

## Versioning

The project follows PEP 440 version identifiers and uses a conservative
pre-1.0 policy:

- development snapshots use `X.Y.Z.devN`;
- release candidates use `X.Y.ZrcN` when a public candidate is needed;
- stable releases use `X.Y.Z` and are created only from an annotated Git tag
  named `vX.Y.Z`;
- while the major version is zero, a minor release may introduce API changes,
  but documented compatibility guarantees are still honored.

A release tag must exactly match the version in `pyproject.toml` after removing
its leading `v`. The release workflow rejects development and pre-release
versions for stable GitHub Releases.

## Release procedure

1. Merge the approved change set into `develop` and pass the complete CI matrix.
2. Update `pyproject.toml`, `CHANGELOG.md` and relevant migration notes to the
   final `X.Y.Z` version.
3. Create and push the annotated `vX.Y.Z` tag from the reviewed release commit.
4. The release workflow verifies the tag/version/changelog relationship,
   builds an sdist and portable Linux wheels, and runs smoke tests using the
   installed wheels.
5. The workflow attaches the verified artifacts to a GitHub Release.
6. Inspect the GitHub Release artifacts and installation instructions before
   any separate PyPI publication.

The release workflow deliberately does **not** upload to PyPI. Adding a PyPI
publisher requires a separate reviewed change using trusted publishing or a
repository secret owned by the maintainer.

## Numerical compatibility

Every release must pass `legacy-contract-v1`. A change to expected numerical
output requires a new, explicitly reviewed reference contract with an
explanation of scientific impact. Numerical changes are never smuggled into a
patch release.

## Python API compatibility and deprecation

- `pyspharm` is the maintained public API.
- `spharm` and `spharm.Spharmt` remain supported compatibility interfaces during
  the pre-1.0 release line.
- No removal of `spharm` will occur before a documented migration path has been
  available in at least two released minor versions and a deprecation warning
  has been emitted for at least one released minor version.
- Deprecations state the replacement API, the earliest removal version and a
  migration example.

## Security and provenance

Release artifacts include the mixed-license notices and are built from the
reviewed Git tag. Generated artifacts are never committed to the repository.
