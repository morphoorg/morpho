from setuptools import setup, find_packages
from glob import glob

import sys
import os
from setuptools.command.test import test as TestCommand

verstr = "none"
try:
    import subprocess
    verstr = subprocess.check_output(
        ['git', 'describe', '--long']).decode('utf-8').strip()
except EnvironmentError:
    pass
except Exception as err:
    print(err)
    verstr = 'v0.0.0-???'

on_rtd = os.environ.get("READTHEDOCS", None) == 'True'

requirements = []
extras_require = {
    'core': ['uproot>=2.8.13', 'colorlog', 'PyYAML>=3.13', 'pyparsing>=2.1.5',
             'pystan==2.17.1.0', 'dnspython==1.12.0',
             'pbr==0.10.8', 'cycler==0.10.0', 'lz4', 'six', 'asteval', 'awkward'],
    'doc': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput', 'six', 'colorlog']
}

if on_rtd:
    requirements.append('better-apidoc')
    requirements += extras_require['doc']
else:
    requirements = extras_require['core']

everything = set()
for deps in extras_require.values():
    everything.update(deps)
extras_require['all'] = everything

setup(
    name='morpho',
    version=verstr,
    description="A python interface with Stan/PyStan Markov Chain Monte Carlo package",
    packages=find_packages(),
    scripts=["bin/morpho"],
    install_requires=requirements,
    extras_require=extras_require,
    url='http://www.github.com/project8/morpho',
    author="J. Formaggio, J. Johnston (MIT), T. Weiss (Yale), M. Guigue (Sorbonne Université), B. LaRoque, N. Oblath (PNNL)",
    maintainer="T. Weiss",
    maintainer_email="talia.weiss@yale.edu"
)
