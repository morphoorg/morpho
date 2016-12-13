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
    'other': ['colorlog', 'ipython', 'ipdb'],
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
    install_requires=['PyYAML', 'msgpack-python'],
    extras_require=extras_require,
    # url='http://www.github.com/project8/morpho',
    # tests_require=['pytest'],
    # cmdclass={'test': PyTest}
)
