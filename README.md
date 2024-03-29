# morpho

[![DOI](https://zenodo.org/badge/22215458.svg)](https://zenodo.org/badge/latestdoi/22215458)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7b4a6e74b5cd405ea91b6ddb5cb504d1)](https://app.codacy.com/app/guiguem/morpho?utm_source=github.com&utm_medium=referral&utm_content=project8/morpho&utm_campaign=badger)
[![Build Status](https://travis-ci.org/morphoorg/morpho.svg?branch=master)](https://travis-ci.org/morphoorg/morpho)
[![Documentation Status](https://readthedocs.org/projects/morpho/badge/?version=latest)](https://morpho.readthedocs.io/en/latest/?badge=latest)

## Detailed Documentation

https://morpho.readthedocs.io/en/latest/

## Introduction

Morpho is an analysis tool that organizes data inflow to and outflow from [Stan](http://mc-stan.org/), a platform for Bayesian statistical modeling and computation, and [RooFit](https://root.cern.ch/guides/roofit-manual), a toolkit for modeling probability distributions.
It is especially useful for

  1) Generating **pseudo data**,
  2) Performing **Bayesian statistical analyses** of real or fake data—that is, extracting posterior distributions for parameters of interest using data and a model, and
  3) Performing **chi2 fits of data**.

Morpho interfaces with Stan using [PyStan](https://pystan.readthedocs.io/en/latest/), but it is designed to be employed by general Stan users (not only PyStan users).

_Why morpho?_

- Morpho **streamlines Stan analyses**. It enables users to load data, run Stan or RooFit, save results, perform convergence diagnostic tests, and create plots of posteriors and their correlations—all as part of one individual analysis. Users can control some or all of these processes using a single [configuration file](https://morpho.readthedocs.io/en/latest/morpho2example.html).
- Morpho helps users organize and run multiple related Stan models (for example, models that share input data and Stan functions).
- Morpho **minimizes the need to recompile** Stan models by using cache files.
- Morpho automatically **performs convergence checks** after running Stan, and it provides additional options for convergence analysis and plotting.
- Morpho reads and saves files in either **R**, **JSON/YAML**, **CVS**, or **ROOT**.

## Install

### Dependencies

The following dependencies should be installed (via a package manager) before installing morpho 2:

- python 3.x (python 2 not supported)
- python-pip
- git
- root 6.22 or newer (ensure that the same version of python is enabled for morpho and ROOT)

### Virtual environment-based installation

We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, including PyStan 2.17.

If necessary, install [virtualenv](https://virtualenv.pypa.io/en/stable/), then execute:

```bash
# Use a flag for virtualenv to specify python3 if necessary: --python /path/to/python3
virtualenv ~/path/to/the/virtualenvironment
source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment
pip install -U pip #Update pip to >= 7.0.0
cd ~/path/to/morpho
pip install .
# When done with morpho, use "bash deactivate" to exit the virtual environment
```

### Docker installation

#### Developper environment

If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a [Docker container](https://docs.docker.com/get-started/) instead of a python virtual environment. To do so:

  1. Install Docker: https://docs.docker.com/engine/installation/.
  2. Clone and pull the latest master version of morpho.
  3. Inside the morpho folder, execute
  ```docker run -v $(pwd):/my_morpho -v ~/morpho_share:/host -it project8/p8compute_dependencies```
  A new terminal prompter (for example, ```root@413ab10d7a8f:```) should appear.
  Source the setup file, and install morpho inside the container with the following commands:

  ```bash
  . $COMMON_BUILD_PREFIX/setup.sh
  cd /my_morpho
  pip3 install -e .
  ```

  Local modifications to the morpho installation will then appear in the docker container. Files in ~/morpho_share will be available in the docker container in the /host folder.

If you develop new features or identify bugs, please open a GitHub issue.

#### Stable version

If you prefer to install the latest version of morpho via docker, use the following commands. However, this does not allow morpho to be edited locally, so it cannot be used for development.

  1. Install Docker: https://docs.docker.com/engine/installation/.
  2. Clone and pull the latest master version of morpho.
  3. Inside the morpho folder, execute ```docker-compose run morpho```. A new terminal prompter (for example, root@413ab10d7a8f:) should appear. Once inside the container, run ```source $MORPHO_BUILD_PREFIX/setup.sh``` to be able to access morpho and libraries.
  4. You can remove the container image using docker rmi morpho_morpho.
  5. If the morpho Docker image gets updated, you can update the morpho image using ```docker pull morpho/morpho```.

## Instructions for Use

### Before You Run Morpho

Morpho primarly reads a **configuration file** (.json or .yaml) written by the user (it can also be used via the python interface).
The file defines the actions ("processors") the user wants to perform and the order in which these should be done.
The file also specifies input parameters that the user may wish to change on a run-to-run basis, such as the desired number of Stan iterations, or Stan initialization and data-block values. 
See morpho's [documentation](https://morpho.readthedocs.io/en/latest/morpho2example.html#configuration-file) for more information.

We recommend modeling the organization of your configuration files, Stan models and data files after the **examples** folder in morpho. Your directory structure should be of the form:

```bash
examples
|
+---functions_dir
|   |
|   +---Stan_funcs1.functions
|   +---Stan_funcs2.functions
|   +---Stan_funcs3.functions
|
+---analysis_dir1
|   |
|   +---data_dir
|   |   |
|   |   +---fileA.data
|   |   +---fileB.data
|   |
|   +---model_dir
|   |   |
|   |   +---modelA.stan
|   |   +---modelB.stan
|   |
|   +---scripts_dir
|       |
|       +---configA.yaml
|       +---configB.yaml
|
+---analysis_dir2
|   |
...  ...
```

The files in the optional ```functions_dir``` directory contain Stan functions (written in the Stan language) that are used in multiple Stan models.

### Running Morpho

#### Using config files

Once the relevant data, model and configuration files are at your disposal, run morpho by executing:

```bash
   morpho --config  /path/to/json_or_yaml_config_file --other_options
```

You can find and run an example in the examples directory:

```bash
   morpho --config linear_fit/scripts/morpho_linear_fit.yaml
```

"Help will always be given to those who ask for it":

```bash
   morpho --help
```

#### Using morpho API

The morpho python API allows you to run custom and more modulable scripts.
In a python script, the processors should be created, configured and run.
Connections between processors are made by setting a internal varible of a processor (like "results" for PyStanSamplingProcessor) as the internal variable of another variable.
Examples of such python scripts can be found in the examples folder:

```bash
   python linear_fit/scripts/pystan_test.py
```

## Quick debug

### Model compilation takes forever, uses a lot of CPU resources and eventually crashes

When compiling a model inside the docker container, it can happen that the model takes a long time (larger than 2-3 minutes) before crashing with a `gcc error 4` message.
During this compilation, all the CPU available to docker will be used too.
This is due to a lack of memory available to the container (basically when running with 1 GB RAM).
To solve this, increase the RAM to ~4 GB.
