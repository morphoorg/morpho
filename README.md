morpho
======

  A python interface between Stan/PyStan Markov Chain Monte Carlo package for meta analysis and generation of fake data.

  [![Build Status](https://travis-ci.org/project8/morpho.svg?branch=morpho2/develop)](https://travis-ci.org/project8/morpho)

Requirements
======

  You will need to install via a package manager (such as apt-get):    
  * python (2.7.x; 3.x not supported)   
  * python-matplotlib   
  * python-pip   
  * git   

  To read and save files, you will need either hdf5 or root:   
  * **hdf5:** libhdf5-serial-dev libhdf5-dev 
  * **root:** root-system from apt-get or sources from https://root.cern (with python enabled).   

  PyStan (see http://mc-stan.org/pystan.html) (a Python implementation of Stan) needs to be installed (version 2.15).
  Using the following installation methods should take care of this requirement.

Install
======

  _Virtual environment installation_

  PyStan and the required packages may be installed from the Python Index Package using pip inside a virtual environment.
  ```bash
	virtualenv ~/path/to/the/virtualenvironment/env
	source ~/path/to/the/virtualenvironment/env/bin/activate
	pip install -U pip # must update pip to >= 7.0.0
	# inside the morpho repository
	pip install .
	pip install .[all]
  ```

  Once all the required packages are installed on the virtual environment, one can load it using
  ```bash
	source ~/path/to/the/virtualenvironment/env/bin/activate
  ```

  _Docker installation_

  Docker provides a uniform test bed for development and bug testing.
  Please use this environment to testing/resolving bugs.

  - Install Docker (Desktop version): https://docs.docker.com/engine/installation/
  - Clone and pull the latest master version of morpho
  - Inside the morpho folder, execute ```docker-compose run morpho```.
  The container prompter should appear at the end of the installation.
  A directory (```morpho_share```) should be created in your home and mounted under the ```/host``` folder: you can modify this by editing the docker-compose file.
  - When reinstalling, you can remove the image using ```docker rmi morpho_morpho```

Running
======

  See the documentation on the Stan homepage for more detail about the Stan models.
  ```bash
	morpho --config  model_folder/<name_of_json/yaml_config_file> --other_options
  ```

  Essentially, the following takes place.  One can "generate" fake data according to a specific model (krypton_generator.stan) or run on actual data (krypton_analysis.stan).  The sequence for events is as follows

  1.  The information relative to the model such as the seed or the algorithm to be used are read from the json/yaml script or from the command line.

  2.  The input files are read into the system.  The input files can be in R, root or hdf5. Input values can be directly given directly in the script.

  3. The script looks for cached versions of the .stan model file.  If not, it generates a new one and saves it.  The cached models exist in the cache directory.

  4.  The model generates sample the Likelihood function defined in the model and save the samplesin the specified directory.  If there is no data, this in principle can be used to generate fake data.

  5.  Postprocessing routines defined in python within the script can occur at the end of the Markov chains in order to generate fake data for example (data_reducer postprocessing).

  6. Very generic plots and screen outputs can be created.

  "Help will always be given to those who ask for it":
  ```bash
	morpho --help
  ```

  An simple example of script and model can be found in the examples folder.
  You can execute it using:
  ```bash
	morpho --config morpho_test/scripts/morpho_linear_fit.yaml
  ```

Known bugs and solutions
======	  

1.  When running matplotlib in a virtual environment, the following error can be encountered:

    ```
    Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a
    framework. See the Python documentation for more information on installing Python as a framework on Mac OS X. Please either reinstall
    Python as a framework, or try one of the other backends. If you are Working with Matplotlib in a virtual enviroment see 'Working with
    Matplotlib in Virtual environments' in the Matplotlib FAQ.
    ```
    A solution is given [here](http://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python)
