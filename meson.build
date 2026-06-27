# F2PY/Meson integration follows the NumPy Meson build guidance.
project(
  'pyspharm-ng',
  'c',
  'fortran',
  version: '0.1.0.dev0',
  license: ['BSD-3-Clause', 'LicenseRef-UCAR-SPHEREPACK'],
  license_files: [
    'LICENSE',
    'NOTICE',
    'LICENSES/BSD-3-Clause.txt',
    'LICENSES/PYSPHARM-LEGACY-PYTHON.txt',
    'LICENSES/UCAR-SPHEREPACK.txt',
  ],
  meson_version: '>=1.1.0',
  default_options: ['warning_level=2'],
)

py_mod = import('python')
py = py_mod.find_installation(pure: false)
py_dep = py.dependency()

py.install_sources(
  [
    'Lib/__init__.py',
    'Lib/spharm.py',
  ],
  subdir: 'spharm',
)

incdir_numpy = run_command(
  py,
  ['-c', 'import numpy; print(numpy.get_include())'],
  check: true,
).stdout().strip()

incdir_f2py = run_command(
  py,
  ['-c', 'import numpy.f2py; print(numpy.f2py.get_include())'],
  check: true,
).stdout().strip()

spherepack_source = custom_target(
  '_spherepackmodule.c',
  input: ['src/_spherepack.pyf'],
  output: ['_spherepackmodule.c', '_spherepack-f2pywrappers.f'],
  command: [py, '-m', 'numpy.f2py', '--lower', '@INPUT@'],
)

inc_np = include_directories(incdir_numpy, incdir_f2py)

# These free-form sources are generated deterministically from the retained
# fixed-form provenance sources by tools/fortran/fixed_to_free.py.
free_form_fortran_sources = [
  'src/free_form/getlegfunc.f90',
  'src/free_form/specintrp.f90',
  'src/free_form/onedtotwod.f90',
  'src/free_form/onedtotwod_vrtdiv.f90',
  'src/free_form/twodtooned.f90',
  'src/free_form/twodtooned_vrtdiv.f90',
  'src/free_form/multsmoothfact.f90',
  'src/free_form/lap.f90',
  'src/free_form/invlap.f90',
  # SPHEREPACK sources
  'src/free_form/gaqd.f90',
  'src/free_form/shses.f90',
  'src/free_form/shaes.f90',
  'src/free_form/vhaes.f90',
  'src/free_form/vhses.f90',
  'src/free_form/shsgs.f90',
  'src/free_form/shags.f90',
  'src/free_form/vhags.f90',
  'src/free_form/vhsgs.f90',
  'src/free_form/sphcom.f90',
  'src/free_form/hrfft.f90',
  'src/free_form/shaec.f90',
  'src/free_form/shagc.f90',
  'src/free_form/shsec.f90',
  'src/free_form/shsgc.f90',
  'src/free_form/vhaec.f90',
  'src/free_form/vhagc.f90',
  'src/free_form/vhsec.f90',
  'src/free_form/vhsgc.f90',
  'src/free_form/ihgeod.f90',
  'src/free_form/alf.f90',
]

py.extension_module(
  '_spherepack',
  [free_form_fortran_sources, spherepack_source],
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies: py_dep,
  subdir: 'spharm',
  install: true,
)
