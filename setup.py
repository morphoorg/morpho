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


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []

        # for some reason we have to do this to get it to function correctly.
        self.pytest_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, because outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

extras_require={
    'doc': ['sphinx', 'sphinx_rtd_theme', 'sphinxcontrib-programoutput'],
    'other': ['colorlog', 'ipython', 'ipdb'],
}
everything = set()
for deps in extras_require.values():
    everything.update(deps)
extras_require['all'] = everything

setup(
    name='morpho',
    version=verstr,
    packages=['morpho'],
    install_requires=['pika>=0.9.8,<0.10', 'PyYAML', 'msgpack-python'],
    extras_require=extras_require,
    url='http://www.github.com/project8/morpho',
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
