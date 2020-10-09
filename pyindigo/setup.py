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
    name='pyindigo',
    version='0.1.0',
    author='Igor Vaiman',
    author_email='gosha.vaiman@gmail.com',
    description='Python interface for INDIGO client (alpha)',
    # py_modules=['ccd_device.py']
    ext_modules=[module],
    # package_data={
    #     'pyindigo': '../indigo/build/lib/'
    # }
)
