# F2PY/Meson integration follows the NumPy Meson build guidance.
project(
  'pyspharm-ng',
  'c',
  'fortran',
  version: '0.2.1.dev0',
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

# ``spharm`` remains the compatibility API while ``pyspharm`` is the
# maintained, typed facade introduced in Stage 4.
py.install_sources(
  [
    'Lib/__init__.py',
    'Lib/spharm.py',
  ],
  subdir: 'spharm',
)
py.install_sources(
  [
    'Lib/pyspharm/__init__.py',
    'Lib/pyspharm/api.py',
    'Lib/pyspharm/regrid.py',
    'Lib/pyspharm/utilities.py',
    'Lib/pyspharm/py.typed',
  ],
  subdir: 'pyspharm',
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

# Most F77 provenance sources remain versioned in src/. Meson converts these
# sources deterministically and compiles the free-form outputs from its private
# build directory. Laplacian, inverse-Laplacian and isotropic smoothing are
# intentionally replaced subsets: their historical sources remain as
# provenance, while the extension compiles ABI-preserving implementations in
# src/modern/.
fixed_form_fortran_sources = files(
  'src/getlegfunc.f',
  'src/specintrp.f',
  'src/onedtotwod.f',
  'src/onedtotwod_vrtdiv.f',
  'src/twodtooned.f',
  'src/twodtooned_vrtdiv.f',
  # SPHEREPACK sources
  'src/gaqd.f',
  'src/shses.f',
  'src/shaes.f',
  'src/vhaes.f',
  'src/vhses.f',
  'src/shsgs.f',
  'src/shags.f',
  'src/vhags.f',
  'src/vhsgs.f',
  'src/sphcom.f',
  'src/hrfft.f',
  'src/shaec.f',
  'src/shagc.f',
  'src/shsec.f',
  'src/shsgc.f',
  'src/vhaec.f',
  'src/vhagc.f',
  'src/vhsec.f',
  'src/vhsgc.f',
  'src/ihgeod.f',
  'src/alf.f',
)

fortran_converter_script = join_paths(
  meson.project_source_root(),
  'tools/fortran/fixed_to_free.py',
)
fixed_to_free = generator(
  py,
  output: '@BASENAME@.f90',
  arguments: [
    fortran_converter_script,
    '--convert', '@INPUT@', '@OUTPUT@',
  ],
)
free_form_fortran_sources = fixed_to_free.process(fixed_form_fortran_sources)

modern_fortran_sources = files(
  'src/modern/spharm_kinds.f90',
  'src/modern/spharm_spectral_operators.f90',
  'src/modern/spharm_legacy_interfaces.f90',
)

py.extension_module(
  '_spherepack',
  [modern_fortran_sources, free_form_fortran_sources, spherepack_source],
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies: py_dep,
  subdir: 'spharm',
  install: true,
)
