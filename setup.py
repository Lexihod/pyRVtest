from pathlib import Path

from setuptools import find_packages, setup

read = lambda p: Path(Path(__file__).resolve().parent / p).read_text()
setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='pyRVtest',
    url='https://github.com/chrissullivanecon/pyRVtest',
    author='Marco Duarte, Lorenzo Magnolfi, Mikkel Solvsten, and Christopher Sullivan',
    author_email='chris.sullivan.econ@gmail.com',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=read('requirements.txt').splitlines(),
    version='0.1.2',
    license='MIT',
    description='Code to perform econometric test of firm conduct',
    long_description=open('README.md').read(),
)
