---------------
Install
---------------

Dependencies
############

The following dependencies should be installed (via a package manager) before installing morpho:
  - python 3.x (python 2 not supported)
  - python-pip
  - git
  - root 6.22 or newer (ensure that the same version of python is enabled for morpho and ROOT)

Virtual environment-based installation
######################################

We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, including PyStan 2.15.

If necessary, install virtualenv_, then execute: ::

        # Use a flag for virtualenv to specify python3 if necessary: --python /path/to/python3
	virtualenv ~/path/to/the/virtualenvironment
	source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment
	pip install -U pip #Update pip to >= 7.0.0
	cd ~/path/to/morpho
	pip install .
	# When done with morpho, use "bash deactivate" to exit the virtual environment

.. _virtualenv: https://virtualenv.pypa.io/en/stable/

Docker installation
###################

If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a `Docker container`_ instead of a python virtual environment.
To do so:

1.  Install Docker: https://docs.docker.com/engine/installation/.
2.  Clone and pull the latest master version of morpho.
3.  Inside the morpho folder, execute ```docker-compose run morpho```. A new terminal prompter (for example, ```root@413ab10d7a8f:```) should appear.
    You may make changes to morpho either inside or outside of the Docker container. 
    If you wish to work outside of the container, move morpho to the ```morpho_share``` directory that is mounted under the ```/host``` folder created by docker-compose.
    Once inside the container, run ```source /setup.sh``` to be able to access morpho libraries.
4.  You can remove the container image using ```docker rmi morpho_morpho```.
5.  If the morpho Docker image gets updated, you can update the morpho image using ```docker pull morpho```.

If you develop new features or identify bugs, please open a GitHub issue.

.. _Docker Container: https://docs.docker.com/get-started/
