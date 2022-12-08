"""Sets up the package."""

from pathlib import Path

from setuptools import find_packages, setup

# define a function that reads a file in this directory
read = lambda p: Path(Path(__file__).resolve().parent / p).read_text()

# set up the package
setup(
    name='pyRVtest',
    author='Marco Duarte, Lorenzo Magnolfi, Mikkel Solvsten, and Christopher Sullivan',
    author_email='chris.sullivan.econ@gmail.com',
    url='https://github.com/chrissullivanecon/pyRVtest',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=read('requirements.txt').splitlines(),
    license='MIT',
    description='Code to perform econometric test of firm conduct',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    version='0.1.2'
)
