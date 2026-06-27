#!/usr/bin/env python3
"""Replace legacy Python-2 integer divisions used for SPHEREPACK sizes.

The legacy wrapper uses `/ 2` in formulas for latitude counts and Fortran
workspace lengths.  Python 3 evaluates those expressions as floats, while the
F2PY wrappers require integer sizes.  This migration intentionally changes only
expressions whose assignment target or operands identify them as dimensions or
workspaces; mathematical divisions elsewhere are left untouched.

Run with `--check` in CI to ensure no legacy size division is reintroduced.
Run with `--apply` only as a one-time source migration.
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "Lib" / "spharm.py"
DIMENSION_NAMES = {"nlat", "nlon", "n1", "n2", "ntrunc", "nt"}
WORKSPACE_NAMES = {
    "ldwork",
    "lshaec",
    "lshaes",
    "lshagc",
    "lshags",
    "lshsec",
    "lshses",
    "lshsgc",
    "lshsgs",
    "lvhaec",
    "lvhaes",
    "lvhagc",
    "lvhags",
    "lvhsec",
    "lvhses",
    "lvhsgc",
    "lvhsgs",
    "lwork",
}


def assigned_names(node: ast.Assign | ast.AnnAssign) -> set[str]:
    """Return simple names assigned by one statement."""

    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return {target.id for target in targets if isinstance(target, ast.Name)}


def source_offsets(source: str) -> list[int]:
    """Return the character offset at the beginning of each source line."""

    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def candidate_divisions(source: str) -> list[tuple[int, int, str]]:
    """Locate `/ 2` operations that determine discrete sizes."""

    tree = ast.parse(source)
    offsets = source_offsets(source)
    candidates: list[tuple[int, int, str]] = []

    for statement in ast.walk(tree):
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = assigned_names(statement)
        value = statement.value
        for expression in ast.walk(value):
            if not (
                isinstance(expression, ast.BinOp)
                and isinstance(expression.op, ast.Div)
                and isinstance(expression.right, ast.Constant)
                and expression.right.value == 2
            ):
                continue

            names = {
                node.id
                for node in ast.walk(expression.left)
                if isinstance(node, ast.Name)
            }
            is_size_expression = bool(names & DIMENSION_NAMES) or bool(
                targets & WORKSPACE_NAMES
            )
            if not is_size_expression:
                continue

            start = offsets[expression.lineno - 1] + expression.col_offset
            end = offsets[expression.end_lineno - 1] + expression.end_col_offset
            operator = source.rfind("/", start, end)
            if operator < start:
                raise RuntimeError(
                    f"Could not locate division operator at line {expression.lineno}"
                )
            candidates.append((operator, expression.lineno, source[start:end]))

    return sorted(candidates, reverse=True)


def migrate(source: str) -> tuple[str, list[tuple[int, str]]]:
    """Apply package-local extension import and integer-division corrections."""

    import_line = "import _spherepack, numpy, math, sys"
    package_import = "from . import _spherepack\n\nimport math\nimport numpy\nimport sys"
    if import_line in source:
        source = source.replace(import_line, package_import, 1)

    changes: list[tuple[int, str]] = []
    for operator, line, expression in candidate_divisions(source):
        source = f"{source[:operator]}//{source[operator + 1:]}"
        changes.append((line, expression))
    return source, list(reversed(changes))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = TARGET.read_text(encoding="utf-8")
    migrated, changes = migrate(source)

    if args.check:
        if changes or source != migrated:
            print("Legacy Python-2 compatibility changes are still required:")
            if source != migrated:
                print("  - package-local _spherepack import")
            for line, expression in changes:
                print(f"  - line {line}: {expression}")
            return 1
        print("No legacy size divisions or global extension import remain.")
        return 0

    if not changes and source == migrated:
        print("No source changes required.")
        return 0

    TARGET.write_text(migrated, encoding="utf-8")
    print(f"Updated {TARGET.relative_to(ROOT)}")
    for line, expression in changes:
        print(f"  line {line}: {expression}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
