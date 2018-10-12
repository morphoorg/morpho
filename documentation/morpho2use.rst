---------------
Use
---------------

Configuration Files
############

Morpho primarly reads a **configuration file** (.json or .yaml) written by the user (it can also be used via the python interface).
The file defines the actions ("processors") the user wants to perform and the order in which these should be done.
The file also specifies input parameters that the user may wish to change on a run-to-run basis, such as the desired number of Stan iterations, or Stan initialization and data-block values. 

See morpho's documentation_ for more information.

.. _documentation: https://morpho.readthedocs.io/en/latest/better_apidoc_out/modules.html

We recommend modeling the organization of your configuration files, Stan models and data files after the **examples** folder in morpho. Your directory structure should be of the form:


examples
|
+---functions_dir
|	  |
|	  +---Stan_funcs1.functions
|	  +---Stan_funcs2.functions
|	  +---Stan_funcs3.functions
|
+---analysis_dir1
|   |
|   +---data_dir
|   |   |
|   |	  +---fileA.data
|	  |   +---fileB.data
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

The files in the optional ```functions_dir``` directory contain Stan functions (written in the Stan language) that are used in multiple Stan models.

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

