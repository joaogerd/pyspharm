#!/usr/bin/env python3
"""Convert the audited SPHEREPACK F77 sources from fixed to free form.

The converter reads only the fixed-form statement field (columns 7–72),
preserves labels and continuation semantics, and rewrites column-one comments
as free-form comments. It deliberately does not alter identifiers, types,
arithmetic, COMMON blocks, or control flow.

Meson invokes this tool once per source during the build, producing temporary
`.f90` files in the build directory. The historical `.f` files remain the
version-controlled provenance inputs until a routine is replaced by a semantic
modernization unit in ``src/modern``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIRECTORY = ROOT / "src"

# Keep this list aligned with the fixed-form source list in meson.build.
# Modernized routines remain under src/ as provenance but are deliberately not
# converted or compiled through this Stage-3 compatibility path.
SOURCES = (
    "getlegfunc.f",
    "specintrp.f",
    "onedtotwod.f",
    "onedtotwod_vrtdiv.f",
    "twodtooned.f",
    "twodtooned_vrtdiv.f",
    "multsmoothfact.f",
    "gaqd.f",
    "shses.f",
    "shaes.f",
    "vhaes.f",
    "vhses.f",
    "shsgs.f",
    "shags.f",
    "vhags.f",
    "vhsgs.f",
    "sphcom.f",
    "hrfft.f",
    "shaec.f",
    "shagc.f",
    "shsec.f",
    "shsgc.f",
    "vhaec.f",
    "vhagc.f",
    "vhsec.f",
    "vhsgc.f",
    "ihgeod.f",
    "alf.f",
)

COMMENT_PREFIXES = frozenset("Cc*!Dd")


@dataclass(frozen=True)
class ConversionResult:
    """Conversion statistics for one source file."""

    source: Path
    target: Path
    comments: int
    continuations: int
    labels: int


def is_comment(line: str) -> bool:
    """Return whether a physical fixed-form line is a comment line."""

    return bool(line) and line[0] in COMMENT_PREFIXES


def fixed_statement_field(line: str) -> str:
    """Return the F77 statement field, excluding sequence columns after 72."""

    return line.expandtabs(8)[6:72].rstrip()


def free_comment(line: str) -> str:
    """Convert a fixed-form comment while preserving its text."""

    if line.startswith("!"):
        return line.rstrip()
    return f"!{line[1:].rstrip()}"


def convert_text(text: str, *, source: Path, target: Path) -> tuple[str, ConversionResult]:
    """Convert one fixed-form source text to free form without semantic edits."""

    output: list[str] = []
    previous_statement: int | None = None
    comment_count = 0
    continuation_count = 0
    label_count = 0

    for lineno, physical in enumerate(text.splitlines(), start=1):
        expanded = physical.expandtabs(8)
        if not expanded.strip():
            output.append("")
            previous_statement = None
            continue
        if is_comment(expanded):
            output.append(free_comment(expanded))
            previous_statement = None
            comment_count += 1
            continue

        label = expanded[:5].strip()
        if label and not label.isdigit():
            raise ValueError(
                f"{source.name}:{lineno}: non-numeric fixed-form label {label!r}"
            )
        continuation = len(expanded) > 5 and expanded[5] not in {" ", "0"}
        statement = fixed_statement_field(expanded).strip()
        if not statement:
            raise ValueError(
                f"{source.name}:{lineno}: empty fixed-form statement field"
            )

        if continuation:
            if label:
                raise ValueError(
                    f"{source.name}:{lineno}: continuation line must not carry a label"
                )
            if previous_statement is None:
                raise ValueError(
                    f"{source.name}:{lineno}: continuation without a preceding statement"
                )
            output[previous_statement] = output[previous_statement].rstrip() + " &"
            output.append(f"  & {statement}")
            previous_statement = len(output) - 1
            continuation_count += 1
            continue

        prefix = f"{label} " if label else ""
        output.append(f"{prefix}{statement}")
        previous_statement = len(output) - 1
        label_count += bool(label)

    converted = "\n".join(output).rstrip() + "\n"
    return converted, ConversionResult(
        source=source,
        target=target,
        comments=comment_count,
        continuations=continuation_count,
        labels=label_count,
    )


def convert_file(source: Path, target: Path) -> ConversionResult:
    """Convert one source file and write the resulting free-form file."""

    if source.name not in SOURCES:
        raise ValueError(f"{source} is not an audited Stage-3 source")
    converted, result = convert_text(
        source.read_text(encoding="utf-8"), source=source, target=target
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(converted, encoding="utf-8")
    return result


def render_directory(directory: Path) -> int:
    """Render all audited sources to one directory for review or inspection."""

    for filename in SOURCES:
        result = convert_file(SOURCE_DIRECTORY / filename, directory / f"{Path(filename).stem}.f90")
        print(
            f"generated {result.target} "
            f"(comments={result.comments}, continuations={result.continuations}, "
            f"labels={result.labels})"
        )
    return 0


def validate() -> int:
    """Parse and convert every audited source without persisting generated files."""

    for filename in SOURCES:
        source = SOURCE_DIRECTORY / filename
        convert_text(source.read_text(encoding="utf-8"), source=source, target=Path("/dev/null"))
    print(f"Validated conversion of {len(SOURCES)} fixed-form Fortran sources.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--convert",
        nargs=2,
        metavar=("INPUT", "OUTPUT"),
        help="convert one audited fixed-form source to one free-form output",
    )
    mode.add_argument(
        "--render-dir",
        type=Path,
        metavar="DIRECTORY",
        help="render every audited source to DIRECTORY",
    )
    mode.add_argument("--validate", action="store_true", help="validate all conversions")
    mode.add_argument("--list", action="store_true", help="list audited conversion inputs")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list:
        print("\n".join(SOURCES))
        return 0
    if args.validate:
        return validate()
    if args.render_dir:
        return render_directory(args.render_dir)

    source_arg, target_arg = args.convert
    result = convert_file(Path(source_arg), Path(target_arg))
    print(
        f"generated {result.target} "
        f"(comments={result.comments}, continuations={result.continuations}, "
        f"labels={result.labels})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
