morpho
======
The morpho package:

    A python interface between Stan/PyStan Markov Chain Monte Carlo packahe for meta analysis and generation of fake data.


Requirements
======
	We will need PyStan in order to run this system.

	The PyStan (and mc-stan) module can be downloaded via GitHub or directly.

	see   http://mc-stan.org
	and   http://mc-stan.org/pystan.html.

	PyStan has the following dependencies:

	Python: 2.7 or 3.3
	Cython: 0.19 or greater
	NumPy: 1.7 or greater

Install
======
  PyStan and the required packages may be installed from the Python Package Index using pip inside a virtual environment.
                virtualenv ~/path/to/the/virtualenvironment/env
                pip install -r ~/path/to/morpho/requirements.txt
  Once all the required packages are installed on the virtualenvironment, one can load it using
                source ~/path/to/the/virtualenvironment/env

Running
======
	A sample executable is shown in the examples directory:

	  	  python ../morpho/morpho.py --config  model_folder/scripts/<name_of_json_config_file> --other_options

		  Essentially, the following takes place.  One can "generate" fake data according to a specific model (krypton_generator.stan) or run on actual data (krypton_analysis.stan).  The sequence for events is as follows

		  1.  The script looks for cached versions of the .stan model file.  If not, it generates a new one and saves it.  The cached models exist in the cache directory

		  2.  The input files are read into the system.  Right now, my input files are set for R-style formats, but we can use anything that makes a dict file.  I will leave it to higher up programers to deal with this.

		  3.  There are two input files (actually, any number you want).  The first input file has general information common to both the generator and the analysis models (for example, the magnetic field parameters).  The second input file can contain input that is specifc to the model being run (for example, data entries for the analyzer, model parameters for the generator).

		  4.  The model generates a number of Markov Chain files (in the specified directory) according to the specific model.  If there is no data, this in principle can be used to generate fake data.  That feature isn't quite implemented yet.

		  5.  Very generic plots and screen outputs are created, just to flash some results.

		  See the documentation on the Stan homepage for more detail.
