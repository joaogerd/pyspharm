Requires: numpy, meson-python and gfortran.

Please read LICENSE.spherepack

Installation:

python -m build

python -m pip install dist/*whl

View documentation by pointing your browser to html/index.html.

Example programs are provided in the examples directory.

Copyright: (applies only to python binding, Spherepack fortran
source code licensing is in LICENSE.spherepack)

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation.
THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO
EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

## Windows Installation

If you are a Windows user, you can download the original compressed package of this project. After downloading, extract the package, open a command prompt, and `cd` into the extracted directory. Then run:

```bash
python windows_installer.py
```

Follow the prompts to complete the installation.

## Maintained-fork modernization

This repository is being prepared as the foundation for an independently
maintained distribution, tentatively named **pyspharm-ng**. The staged plan is
in [docs/modernization/README.md](docs/modernization/README.md).

Stage 1 preserves the provenance and licensing of the legacy code and defines
a numerical reference contract before changes to the packaging, Python API or
Fortran implementation. See:

- [mixed-license overview](LICENSE);
- [third-party notices](NOTICE);
- [scientific baseline contract](docs/modernization/01-scientific-baseline.md).

The current root documentation remains historical and will be replaced during
the packaging modernization stage. Until then, do not interpret this branch as
a new PyPI release.
