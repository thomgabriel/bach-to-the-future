#!/usr/bin/env python
from setuptools import setup, find_packages
from os.path import join, dirname

here = dirname(__file__)

setup(name='backtest',
      version='0',
      description='',
      long_description=open(join(here, 'README.md')).read(),
      author='',
      author_email='',
      url='',
      install_requires=[
        'tqdm',
        'pandas',
        'numpy',
        'ta',
        'ta-lib',
        'dateparser',
        'ciso8601',
      ],
      packages=find_packages(),
      )