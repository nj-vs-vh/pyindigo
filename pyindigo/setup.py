from distutils.core import setup, Extension
from pathlib import Path

indigo_root = Path('../indigo').resolve()

module = Extension(
    "_pyindigo",
    sources=['_pyindigo.c'],
    library_dirs=['./bin', '../indigo/build/lib/'],
    libraries=['pyindigo_ccd_client', 'indigo'],
    extra_compile_args=[f'-I{indigo_root}/indigo_libs', f'-L{indigo_root}/build/lib'],
)

setup(
    name='_pyindigo',
    version='0.0.1',
    description='Python interface for INDIGO client',
    ext_modules=[module]
)
