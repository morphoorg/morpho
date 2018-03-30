from setuptools import setup, find_packages
from glob import glob

import sys, os
from setuptools.command.test import test as TestCommand

verstr = "none"
try:
    import subprocess
    verstr = subprocess.check_output(['git','describe', '--long']).decode('utf-8').strip()
except EnvironmentError:
    pass
except Exception as err:
    print(err)
    verstr = 'v0.0.0-???'

on_rtd = os.environ.get("READTHEDOCS", None) == 'True'

requirements = []
extras_require = {
    'h5': ['h5py<=2.6'],
    'core':['uproot>=2.8.13','matplotlib==1.5.1','colorlog', 'PyYAML==3.11','pyparsing>=2.1.5','numpy>=1.14','pystan==2.17.0.0','dnspython==1.12.0','pbr==0.10.8','cycler==0.10.0','python-dateutil==2.5.3'],
    'doc': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput']
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
    packages=find_packages(),
    scripts=['bin/morpho','bin/BasicTest'],
    install_requires=requirements,
    extras_require=extras_require,
    url='http://www.github.com/project8/morpho',
    dependency_links=[
        'git+https://github.com/guiguem/uproot.git@master#egg=uproot-2.8.13'
    ]
)
