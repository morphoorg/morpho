morpho
======

   Morpho is an analysis tool that organizes data inflow to and outflow from [Stan](http://mc-stan.org/), a platform for Bayesian statistical modeling and computation. It is especially useful for:
   
   A) Generating **pseudo data**, and
   B) Performing **Bayesian statistical analyses** of real or fake data—that is, extracting posterior distributions for parameters of interest using data and a model.

Morpho interfaces with Stan using [Pystan](https://pystan.readthedocs.io/en/latest/), but it is designed to be employed by general Stan users (not only PyStan users).

_Why morpho?_
    1. Morpho **streamlines Stan analyses**. It enables users to load data, run Stan, save results, perform convergence diagnostic tests, and create plots of posteriors and their correlations—all as part of one individual analysis. Users can control some or all of these processes using a single [configuration file](http://morpho.readthedocs.io/en/latest/morpho.html#an-example-file).
    2. Morpho helps users organize and run multiple related Stan models (for example, models that share input data and Stan functions).
    3. Morpho **minimizes the need to recompile** Stan models by using cache files.
    4. Morpho automatically **performs convergence checks** after running Stan, and it provides additional options for convergence analysis and plotting.


Install
---------------

### Dependencies ###

The following dependencies should be installed (via a package manager) before installing morpho:
  - python (2.7.x; 3.x not yet supported)
  - python-pip
  - git
  - python-matplotlib

  Morpho reads and saves files in either **R** or **ROOT.** If you would like to use root, install root-system or see https://root.cern (and ensure that the same version of python is enabled for morpho and ROOT).

### Virtual environment-based installation ###

  We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, including PyStan 2.15.
  
  If necessary, install [virtualenv](https://virtualenv.pypa.io/en/stable/), then execute:
  ```bash
	virtualenv ~/path/to/the/virtualenvironment
	source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment
	#Use```bash deactivate``` to exit the environment
	pip install -U pip #Update pip to >= 7.0.0
	cd ~/path/to/morpho
	pip install .
	pip install .[all]
  ```

### Docker installation ###

   If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a [Docker container](https://docs.docker.com/get-started/) instead of a python virtual environment. To do so:

  1. Install Docker: https://docs.docker.com/engine/installation/.
  2. Clone and pull the latest master version of morpho.
  3. Inside the morpho folder, execute ```docker-compose run morpho```. A new terminal prompter (for example, ```root@413ab10d7a8f:```) should appear.
  You may make changes to morpho either inside or outside of the Docker container. If you wish to work outside of the container, move morpho to the ```morpho_share``` directory that is mounted under the ```/host``` folder created by docker-compose.
  4. You can remove the container image using ```docker rmi morpho_morpho```.

   If you develop new features or identify bugs, please open a GitHub issue or email nsoblath@mit.edu.



Instructions for Use
---------------
### Before You Run Morpho ###

Morpho reads a **configuration file** (.json or .yaml) written by the user. The configuration file dictates what Stan model morpho should run (if any), as well as the pre- and/or post-processing operations that morpho should perform. The file also specifies input parameters that the user may wish to change on a run-to-run basis, such as the desired number of Stan iterations, or Stan initialization and data-block values. See morpho's [documentation](http://morpho.readthedocs.io/en/latest/morpho.html#an-example-file) for more information.

We recommend modeling the organization of your configuration files, Stan models and data files after the **examples** folder in morpho. Your directory structure should be of the form:

```bash
examples
|
+---functions_dir
|	  |
|	  +---Stan_funcs1.functions
|	  +---Stan_funcs2.functions
|	  +---Stan_funcs3.functions
|
+---analysis_dir1
|         |
|         +---data_dir
|         |       |
|     	  |	  +---fileA.data
|	  |       +---fileB.data
|	  |
|	  +---model_dir
|	  |	  |
|	  |	  +---modelA.stan
|	  |	  +---modelB.stan
|	  |
|	  +---scripts_dir
|	  	  |
|	  	  +---configA.yaml
|	  	  +---configB.yaml
|
+---analysis_dir2
|	  |
...	  ...
```
The files in the optional ```functions_dir``` directory contain Stan functions (written in the Stan language) that are used in multiple Stan models.


### Running Morpho ###

Once the relevant data, model and configuration files are at your disposal, run morpho by executing:
```bash
   morpho --config  /path/to/json_or_yaml_config_file --other_options
```

You can test morpho using the example in the morpho_test directory:
```bash
   morpho --config morpho_test/scripts/morpho_linear_fit.yaml
```

When you run morpho, it performs each of the following actions, in this order:
   1. If the configuration file includes a ```data``` dictionary, morpho reads any Stan data parameter values under ```type: mc``` in that file and loads any named R or ROOT files.
   2. If ```do_preprocessing``` is ```true``` in the configuration file, morpho executes the methods specified under ```preprocessing``` in that file. See preprocessing options [here](http://morpho.readthedocs.io/en/latest/preprocessing.html).
   3. If ```do_stan``` is ```true```, morpho searches for and uses a cached version of the compiled Stan model file. If the cache file does not exist, morpho compiles the model and creates a new cache file. Morpho then runs Stan, prints out summary statistics regarding posteriors (as well as basic diagnostic information), and outputs results to an R or ROOT file, as specified under ```output``` in the configuration file.
   4. If ```do_plots``` is ```true```, morpho executes the methods specified under ```plot``` in the configuration file to create and save plots. See plotting options [here](http://morpho.readthedocs.io/en/latest/plot.html).
   5. If ```do_postprocessing``` is ```true```, morpho executes the methods specified under ```postprocessing``` in the configuration file and optionally saves results. See post-processing options [here](http://morpho.readthedocs.io/en/latest/postprocessing.html).
   

"Help will always be given to those who ask for it":
```bash
   morpho --help
```


Documentation
---------------

Hosted at http://www.project8.org/morpho.
