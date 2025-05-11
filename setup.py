#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
from io import open

about = {}
# Read version number from sapiens.__version__.py (see PEP 396)
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'sapiens', '__version__.py'), encoding='utf-8') as f:
    exec(f.read(), about)

# Read contents of readme file into string
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sapiens',
    version=about['__version__'],
    description='Sapiens: Human antibody language model based on BERT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='David Prihoda',
    packages=find_packages(include=['sapiens.*', 'sapiens']),
    author_email='david.prihoda@gmail.com',
    license='MIT',
    python_requires=">=3.7",
    install_requires=[
        'pandas',
        'transformers',
        'torch',
    ],
    keywords='sapiens, antibody humanization, bert, biophi',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    include_package_data=True,
    package_data={'': ['*.pt', '*.txt']},
    url='https://github.com/Merck/Sapiens'
)
