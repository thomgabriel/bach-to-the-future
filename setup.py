from setuptools import setup, find_packages
from os.path import join, dirname

here = dirname(__file__)

setup(name='Bach to the Future',
      version='0.0.2',
      description="Backtest infrastructure...",
      long_description=open(join(here, 'README.md')).read(),
      license='MIT',
      author='thomgabriel',
      author_email='gthomquan@gmail.com',
      url='https://github.com/thomgabriel/backtest',
      install_requires=[
        'tqdm==4.48.0',
        'numpy==1.19.1',
        'pandas==1.0.5',
        'ta-lib==0.4.18',
        'dateparser==0.7.6',
        'dash==1.14.0',
        'plotly==3.10.0',
        'gunicorn==19.9.0',
        'requests==2.22.0',
      ],
      packages=find_packages(),
      keywords = ['backtest', 'bitcoin', 'crypto-exchange', 'digital-currency', 'trading'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
      ],
      )


# PyPi publish flow
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*