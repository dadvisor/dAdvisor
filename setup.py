import setuptools
import os
from setuptools import setup

loc = os.path.dirname(os.path.abspath(__file__))

with open(loc + '/README.md') as readme:
    info = readme.read()

with open(loc + '/requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='dadvisor',
    version='1.0',
    description=info,
    author='Patrick Vogel',
    author_email='p.p.vogel@student.rug.nl',
    packages=setuptools.find_packages(),
    install_requires=required,
    url='https://github.com/dadvisor/core',
)