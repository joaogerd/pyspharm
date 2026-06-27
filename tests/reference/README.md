# Legacy numerical reference workflow

This directory establishes the numerical compatibility contract for the
SPHEREPACK-based implementation.

## Capture a candidate snapshot

Use a clean, installed checkout of the designated legacy implementation:

```bash
python -m pip install -e .[tests]
python tests/reference/generate_legacy_baseline.py \
  --output tests/reference/data/legacy-contract-v1.npz
```

The generator refuses to overwrite an existing snapshot.  Use `--force` only
when replacing a reference after a reviewed, documented numerical change.

Review the candidate snapshot before committing it.  Its metadata records the
Python, NumPy and platform environment used for capture.  Do not hand-edit NPZ
files.

## Validate an implementation

```bash
python tests/reference/validate_legacy_baseline.py \
  --reference tests/reference/data/legacy-contract-v1.npz
```

The validator checks array names, shapes, dtypes, finite values and numerical
agreement.  The default tolerances target the existing single-precision Fortran
implementation (`rtol=2e-5`, `atol=5e-6`).

## CI capture

The manual workflow `.github/workflows/capture-legacy-reference.yml` builds the
current branch, captures a candidate and uploads it as an artifact.  The
artifact is for review; the workflow never changes a committed numerical
reference automatically.

Once the reviewed file exists at `tests/reference/data/legacy-contract-v1.npz`,
`tests/reference/test_legacy_baseline.py` becomes an ordinary pytest regression
test.  Until then it is explicitly skipped rather than manufacturing a false
reference.
