from setuptools import Extension, setup, find_packages

import os
from pathlib import Path


indigo_root_dir = os.environ.get('INDIGO_DIR')

indigo_build_libs = Path(indigo_root_dir) / 'build/lib' if indigo_root_dir else '/usr/local/lib'
indigo_libs = Path(indigo_root_dir) / 'indigo_libs' if indigo_root_dir else '/usr/local/include'

pyindigo_core_ext_dir = Path('src/pyindigo_core_ext')

pyindigo_core_ext = Extension(
    "pyindigo.core.core_ext",
    sources=[str(pyindigo_core_ext_dir / 'pyindigo_core.c')],
    library_dirs=[str(indigo_build_libs)],
    libraries=['pyindigo_client', 'indigo'],
    extra_compile_args=[f'-I{indigo_libs}', f'-L{indigo_build_libs}'],
)


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name='pyindigo',
    version='0.1.0',
    author='Igor Vaiman',
    author_email='gosha.vaiman@gmail.com',
    description='Python interface for INDIGO client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nj-vs-vh/pyindigo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',

    package_dir={'': 'src'},
    packages=find_packages(where='src', exclude=['old']),
    ext_modules=[pyindigo_core_ext],
)
