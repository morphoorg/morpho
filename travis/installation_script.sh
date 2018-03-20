#!/bin/bash
# Travis installation script
# Author: M. Guigue
# Date: 03/01/2018

if [ "${TRAVIS_OS_NAME}" == "osx" ]; then curl --silent http://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh -o miniconda.sh; fi
if [ "${TRAVIS_OS_NAME}" == "linux" ]; then wget -nv http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh; fi
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a
conda config --add channels http://conda.anaconda.org/NLeSC
conda config --set show_channel_urls yes
travis_wait conda create -q -n testenv python=${PYTHON} root=${ROOT} numpy matplotlib
export CONDA_ENV_PATH=$HOME/miniconda/envs/testenv
source activate testenv
pip install .