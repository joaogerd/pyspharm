#!/usr/bin/env python3
"""Validate metadata required before creating a stable GitHub Release.

The check is intentionally dependency-free so it can run in a release job
before the package is installed. Stable releases use an exact PEP 440 final
version such as ``0.1.0``, a matching Git tag such as ``v0.1.0``, and a
versioned release-notes document.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
RELEASE_NOTES_DIRECTORY = ROOT / "docs" / "releases"
FINAL_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
PROJECT_VERSION = re.compile(r'^version\s*=\s*"(?P<version>[^"]+)"\s*$', re.MULTILINE)


def project_version() -> str:
    """Read the static project version without importing build dependencies."""

    match = PROJECT_VERSION.search(PYPROJECT.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError("could not locate [project].version in pyproject.toml")
    return match.group("version")


def validate(tag: str) -> list[str]:
    """Return all metadata validation errors for a requested release tag."""

    errors: list[str] = []
    version = project_version()
    expected_tag = f"v{version}"

    if not FINAL_VERSION.fullmatch(version):
        errors.append(
            f"project version {version!r} is not a final X.Y.Z release version"
        )
    if tag != expected_tag:
        errors.append(
            f"tag {tag!r} does not match project version; expected {expected_tag!r}"
        )

    changelog = CHANGELOG.read_text(encoding="utf-8")
    if f"## {version} " not in changelog and f"## {version}\n" not in changelog:
        errors.append(f"CHANGELOG.md has no heading for version {version!r}")

    release_notes = RELEASE_NOTES_DIRECTORY / f"{version}.md"
    if not release_notes.is_file():
        errors.append(f"missing versioned release notes: docs/releases/{version}.md")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Git tag to validate, for example v0.1.0")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        errors = validate(args.tag)
    except (OSError, ValueError) as error:
        print(f"release metadata validation failed: {error}", file=sys.stderr)
        return 1

    if errors:
        print("release metadata validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"release metadata is valid for {args.tag}")
    return 0


if __name__ == "__main__":n    raise SystemExit(main())
