morpho
======
The morpho package:

    A python interface between Stan/PyStan Markov Chain Monte Carlo package for meta analysis and generation of fake data.


Requirements
======
	We will need PyStan in order to run this system.

<<<<<<< HEAD
	The PyStan (and mc-stan) module can be downloaded via GitHub or directly.
	
	see   http://mc-stan.org	
=======
	The pystan (and mc-stan module) can be downloaded via github or directly.

	see   http://mc-stan.org
>>>>>>> 535ed1ceb833a0999837fd4df33a14339a70a463
	and   http://mc-stan.org/pystan.html

	PyStan has the following dependencies:

	Python: 2.7 or 3.3
	Cython: 0.19 or greater
	NumPy: 1.7 or greater

Install
======
	PyStan and the required packages may be installed from the Python Package Index using pip.

	       	      pip install pystan

	One can install Cython and NumPy in a similar manner


Running
======
<<<<<<< HEAD
	A sample executable is shown in the examples directory:
=======
	A sample executible is shown in the examples directory:
>>>>>>> 535ed1ceb833a0999837fd4df33a14339a70a463

	  	  python ../morpho/morpho.py --config  model_folder/scripts/<name_of_json_config_file>
		  
		  Essentially, the following takes place.  One can "generate" fake data according to a specific model (krypton_generator.stan) or run on actual data (krypton_analysis.stan).  The sequence of events is as follows:

		  1.  The script looks for cached versions of the .stan model file.  If it does not find a cached version, the script generates a new one and saves it.  The cached models exist in the cache directory.

		  2.  The input files are read into the system.  Right now, my input files are set for hdf5, root, and R-style formats, but we can use anything that makes a dict file.  I will leave it to higher up programers to deal with this.

<<<<<<< HEAD
		  3.  There are two input files (actually, any number you want).  The first input file has general information common to both the generator and the analysis models (for example, the magnetic field parameters).  The second input file can contain input that is specifc to the model being run (for example, data entries for the analyzer, model parameters for the generator).

		  4.  The model generates a number of Markov Chain files (in the specified directory) according to the specific model.  If there is no data, this in principle can be used to generate fake data.  That feature isn't quite implemented yet.

		  5.  Very generic plots and screen outputs are created, just to flash some results.
		  
		  See the documentation on the Stan homepage for more detail.
=======
		  3.  There are two input files (actually, any number you want).  The first input file has general information common to both the generator and the analysis models (for example, the magnetic field parameters).  The second input file can contain input that is specific to the model being run (for example, data entries for data, model parameters for the generator).

		  4.  The model generates a number of Markov Chain files (in the specified directory) according to the specific model.  If there is no data, this in principle can be used to generate fake data.  That feature isn't quite implemented yet.

		  5.  Very generic plots and screen output is created, just to flash some results.

		  See the documentation on the STAN homepage for greater details.
>>>>>>> 535ed1ceb833a0999837fd4df33a14339a70a463
