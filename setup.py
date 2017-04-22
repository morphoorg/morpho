from setuptools import setup
from glob import glob

import sys
from setuptools.command.test import test as TestCommand

verstr = "none"
try:
    import subprocess
    verstr = subprocess.check_output(['git','describe','--long']).decode('utf-8').strip()
except EnvironmentError:
    pass
except Exception as err:
    print(err)
    verstr = 'v0.0.0-???'

extras_require={
    'postprocessing': ['matplotlib'],
    'h5': ['h5py<=2.6'],
}
everything = set()
for deps in extras_require.values():
    everything.update(deps)
extras_require['all'] = everything

setup(
    name='morpho',
    version=verstr,
    packages=['morpho','morpho/loader', 'morpho/plot', 'morpho/postprocessing'],
    scripts=['bin/morpho'],
    #install_requires=['PyYAML>=3.11'],
    install_requires=['colorlog','PyYAML==3.11','pyparsing>=2.1.5','numpy==1.11.0','pystan==2.14','dnspython==1.12.0','pbr==0.10.8','wsgiref==0.1.2','cycler==0.10.0','python-dateutil==2.5.3'],
    extras_require=extras_require,
    # url='http://www.github.com/project8/morpho',
    # tests_require=['pytest'],
    # cmdclass={'test': PyTest}
)
