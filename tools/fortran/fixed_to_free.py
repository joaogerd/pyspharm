#!/usr/bin/env python3
"""Convert audited fixed-form SPHEREPACK F77 sources to free-form Fortran."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIRECTORY = ROOT / "src"

# Keep exactly aligned with fixed_form_fortran_sources in meson.build.
# Semantic modernizations under src/modern remain as F77 provenance only.
SOURCES = (
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
    source: Path
    target: Path
    comments: int
    continuations: int
    labels: int


def is_comment(line: str) -> bool:
    return bool(line) and line[0] in COMMENT_PREFIXES


def fixed_statement_field(line: str) -> str:
    return line.expandtabs(8)[6:72].rstrip()


def free_comment(line: str) -> str:
    return line.rstrip() if line.startswith("!") else f"!{line[1:].rstrip()}"


def convert_text(text: str, *, source: Path, target: Path) -> tuple[str, ConversionResult]:
    output: list[str] = []
    previous_statement: int | None = None
    comments = continuations = labels = 0
    for lineno, physical in enumerate(text.splitlines(), start=1):
        expanded = physical.expandtabs(8)
        if not expanded.strip():
            output.append("")
            previous_statement = None
            continue
        if is_comment(expanded):
            output.append(free_comment(expanded))
            previous_statement = None
            comments += 1
            continue
        label = expanded[:5].strip()
        if label and not label.isdigit():
            raise ValueError(f"{source.name}:{lineno}: non-numeric fixed-form label {label!r}")
        continuation = len(expanded) > 5 and expanded[5] not in {" ", "0"}
        statement = fixed_statement_field(expanded).strip()
        if not statement:
            raise ValueError(f"{source.name}:{lineno}: empty fixed-form statement field")
        if continuation:
            if label:
                raise ValueError(f"{source.name}:{lineno}: continuation line must not carry a label")
            if previous_statement is None:
                raise ValueError(f"{source.name}:{lineno}: continuation without a preceding statement")
            output[previous_statement] = output[previous_statement].rstrip() + " &"
            output.append(f"  & {statement}")
            previous_statement = len(output) - 1
            continuations += 1
            continue
        output.append(f"{label} {statement}" if label else statement)
        previous_statement = len(output) - 1
        labels += bool(label)
    converted = "\n".join(output).rstrip() + "\n"
    return converted, ConversionResult(source, target, comments, continuations, labels)


def convert_file(source: Path, target: Path) -> ConversionResult:
    if source.name not in SOURCES:
        raise ValueError(f"{source} is not an audited Stage-3 source")
    converted, result = convert_text(source.read_text(encoding="utf-8"), source=source, target=target)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(converted, encoding="utf-8")
    return result


def render_directory(directory: Path) -> int:
    for filename in SOURCES:
        result = convert_file(SOURCE_DIRECTORY / filename, directory / f"{Path(filename).stem}.f90")
        print(f"generated {result.target} (comments={result.comments}, continuations={result.continuations}, labels={result.labels})")
    return 0


def validate() -> int:
    for filename in SOURCES:
        source = SOURCE_DIRECTORY / filename
        convert_text(source.read_text(encoding="utf-8"), source=source, target=Path("validation.f90"))
    print(f"Validated conversion of {len(SOURCES)} fixed-form Fortran sources.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--convert", nargs=2, metavar=("INPUT", "OUTPUT"))
    mode.add_argument("--render-dir", type=Path, metavar="DIRECTORY")
    mode.add_argument("--validate", action="store_true")
    mode.add_argument("--list", action="store_true")
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
    print(f"generated {result.target} (comments={result.comments}, continuations={result.continuations}, labels={result.labels})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
