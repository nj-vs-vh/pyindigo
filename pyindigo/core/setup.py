from distutils.core import setup, Extension
from pathlib import Path

indigo_root = Path('../../indigo').resolve()

pyindigo_core = Extension(
    "pyindigo.core",
    sources=['pyindigo_core.c'],
    library_dirs=['../../indigo/build/lib/'],
    libraries=['pyindigo_client', 'indigo'],
    extra_compile_args=[f'-I{indigo_root}/indigo_libs', f'-L{indigo_root}/build/lib'],
)

setup(
    name='pyindigo',
    version='0.1.0',
    author='Igor Vaiman',
    author_email='gosha.vaiman@gmail.com',
    description='Python interface for INDIGO client',
    ext_modules=[pyindigo_core],
)
