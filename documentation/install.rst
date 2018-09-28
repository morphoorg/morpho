---------------
Install
---------------

Dependencies
############

The following dependencies should be installed (via a package manager) before installing morpho:
  - python (2.7.x; 3.x not yet supported)
  - python-pip
  - git
  - root (ensure that the same version of python is enabled for morpho and ROOT)

Virtual environment-based installation
######################################

We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, including PyStan 2.15.

If necessary, install [virtualenv](https://virtualenv.pypa.io/en/stable/), then execute: ::

	virtualenv ~/path/to/the/virtualenvironment
	source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment
	#Use "bash deactivate" to exit the environment
	pip install -U pip #Update pip to >= 7.0.0
	cd ~/path/to/morpho
	pip install .

   
Docker installation
###################

If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a [Docker container](https://docs.docker.com/get-started/) instead of a python virtual environment. 
To do so:

1.  Install Docker: https://docs.docker.com/engine/installation/.
2.  Clone and pull the latest master version of morpho.
3.  Inside the morpho folder, execute ```docker-compose run morpho```. A new terminal prompter (for example, ```root@413ab10d7a8f:```) should appear.
    You may make changes to morpho either inside or outside of the Docker container. 
    If you wish to work outside of the container, move morpho to the ```morpho_share``` directory that is mounted under the ```/host``` folder created by docker-compose.
    Once inside the container, run ```source /setup.sh``` to be able to access morpho and mermithid libraries.
4.  You can remove the container image using ```docker rmi morpho_morpho```.
5.  If the morpho Docker image gets updated, you can update the morpho image using ```docker pull morpho```.

If you develop new features or identify bugs, please open a GitHub issue.


Running Morpho
##############

Using config files
------------------

Once the relevant data, model and configuration files are at your disposal, run morpho by executing:
::

   morpho --config  /path/to/json_or_yaml_config_file --other_options


You can find and run an example in the examples/linear_fit directory:
::

   morpho --config scripts/morpho_linear_fit.yaml

"Help will always be given to those who ask for it":
::

   morpho --help

Using morpho API
----------------

The morpho python API allows you to run custom and more modulable scripts.
In a python script, the processors should be created, configured and run.
Connections between processors are made by setting a internal varible of a processor (like "results" for PyStanSamplingProcessor) as the internal variable of another variable.
Examples of such python scripts can be found in the examples folder.

