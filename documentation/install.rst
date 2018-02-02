------------------
 Installation Instructions
------------------

Dependencies
------------------

The following dependencies should be installed (using a package manager) before installing morpho:

python (2.7.x; 3.x not yet supported)
python-pip
git
python-matplotlib
Morpho can read and save files in either R or root. If you would like to use root, install root-system or see https://root.cern.

Virtual environment installation

We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, include PyStan 2.15.

If necessary, install virtualenv, then execute
::
  virtualenv ~/path/to/the/virtualenvironment
  source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment.
  #Use```bash deactivate``` to exit the environment.
  pip install -U pip # Update pip to >= 7.0.0
  cd ~/path/to/morpho
  pip install .
  pip install .[all]  
  
Docker installation

If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a Docker container instead of a python virtual environment. To do so:

Install Docker: https://docs.docker.com/engine/installation/
Clone and pull the latest master version of morpho
Inside the morpho folder, execute docker-compose run morpho. A new terminal prompter (for example, root@413ab10d7a8f:) should appear. You may make changes to morpho either inside or outside of the Docker container. If you wish to work outside of the container, move morpho to the morpho_share directory that is mounted under a /host folder.
You can remove the container image using docker rmi morpho_morpho.
If you develop new features or identify bugs, please open a github issue or email nsoblath@mit.edu.

------------------
 Running
------------------

See the documentation on the Stan homepage for more detail about the Stan models.
::
  morpho --config  model_folder/<name_of_json/yaml_config_file> --other_options

Essentially, the following takes place. One can "generate" fake data according to a specific model (krypton_generator.stan) or run on actual data (krypton_analysis.stan). The sequence for events is as follows

The information relative to the model such as the seed or the algorithm to be used are read from the json/yaml script or from the command line.

The input files are read into the system. The input files can be in R, root or hdf5. Input values can be directly given directly in the script.

The script looks for cached versions of the .stan model file. If not, it generates a new one and saves it. The cached models exist in the cache directory.

The model generates sample the Likelihood function defined in the model and save the samplesin the specified directory. If there is no data, this in principle can be used to generate fake data.

Postprocessing routines defined in python within the script can occur at the end of the Markov chains in order to generate fake data for example (data_reducer postprocessing).

Very generic plots and screen outputs can be created.

"Help will always be given to those who ask for it"
::
  morpho --help

An simple example of script and model can be found in the examples
folder. You can execute it using::
  morpho --config morpho_test/scripts/morpho_linear_fit.yaml
