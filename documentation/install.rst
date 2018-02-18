---------------
Install
---------------

Dependencies
############

The following dependencies should be installed (via a package manager) before installing morpho:

  - python (2.7.x; 3.x not yet supported)
  - python-pip
  - git
  - python-matplotlib

Morpho reads and saves files in either **R** or **ROOT.** If you would like to use root, install root-system or see https://root.cern (and ensure that the same version of python is enabled for morpho and ROOT).

Virtual environment-based installation
######################################

We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, including PyStan 2.15.

If necessary, install `virtualenv <https://virtualenv.pypa.io/en/stable/>`_, then execute:
::
   bash
   virtualenv ~/path/to/the/virtualenvironment
   source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment
   #Use "bash deactivate" to exit the environment
   pip install -U pip #Update pip to >= 7.0.0
   cd ~/path/to/morpho
   pip install .
   pip install .[all]

   
Docker installation
###################

If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a `Docker container <https://docs.docker.com/get-started/>`_ instead of a python virtual environment. To do so:

     1. Install Docker: https://docs.docker.com/engine/installation/.
     2. Clone and pull the latest master version of morpho.
     3. Inside the morpho folder, execute ``docker-compose run morpho``. A new terminal prompter (for example, ``root@413ab10d7a8f:``) should appear. You may make changes to morpho either inside or outside of the Docker container. If you wish to work outside of the container,move morpho to the ``morpho_share`` directory that is mounted under the ``/host`` folder created by docker-compose.
     4. You can remove the container image using ``docker rmi morpho_morpho``.

If you develop new features or identify bugs, please open a GitHub issue.


Running Morpho
##############

Once the relevant data, model and configuration files are at your disposal, run morpho by executing:
::
   bash
   morpho --config  /path/to/json_or_yaml_config_file --other_options

You can test morpho using the example in the morpho_test directory:
::
   bash
   morpho --config morpho_test/scripts/morpho_linear_fit.yaml

When you run morpho, it performs each of the following actions, in this order:
   1. If the configuration file includes a ``data`` dictionary, morpho reads any Stan data parameter values under ``type: mc`` in that file and loads any named R or ROOT files.
   2. If ``do_preprocessing`` is ``true`` in the configuration file, morpho executes the methods specified under ``preprocessing`` in that file. See preprocessing options `here <http://morpho.readthedocs.io/en/latest/preprocessing.html>`_.
   3. If ``do_stan`` is ``true``, morpho searches for and uses a cached version of the compiled Stan model file. If the cache file does not exist, morpho compiles the model and creates a new cache file. Morpho then runs Stan, prints out summary statistics regarding posteriors (as well as basic diagnostic information), and outputs results to an R or ROOT file, as specified under ``output`` in the configuration file.
   4. If ``do_plots`` is ``true``, morpho executes the methods specified under ``plot`` in the configuration file to create and save plots. See plotting options `here <http://morpho.readthedocs.io/en/latest/plot.html>`_.
   5. If ``do_postprocessing`` is ``true``, morpho executes the methods specified under ``postprocessing`` in the configuration file and optionally saves results. See post-processing options `here <http://morpho.readthedocs.io/en/latest/postprocessing.html>`_.

"Help will always be given to those who ask for it":
::
   bash
   morpho --help
