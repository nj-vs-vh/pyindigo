from setuptools import Extension, setup, find_packages
from pathlib import Path


indigo_root = Path('indigo')

pyindigo_core_ext_dir = Path('src/pyindigo_core_ext')

pyindigo_core_ext = Extension(
    "pyindigo.core_ext",
    sources=[str(pyindigo_core_ext_dir / 'pyindigo_core.c')],
    library_dirs=[str(indigo_root / 'build/lib/')],
    libraries=['pyindigo_client', 'indigo'],
    extra_compile_args=[f'-I{indigo_root}/indigo_libs', f'-L{indigo_root}/build/lib'],
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
