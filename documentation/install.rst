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


Installation Instructions
------------------

Virtual environment installation

  PyStan and the required packages may be installed from the Python Index Package using pip inside a virtual environment.

  1.  virtualenv ~/path/to/the/virtualenvironment/env
  2.  source ~/path/to/the/virtualenvironment/env/bin/activate
  3.  pip install -U pip # must update pip to >= 7.0.0
  4.  Go inside the morpho repository
  5.  pip install .
  6.  pip install .[all]
      
  Once all the required packages are installed on the virtualenvironment, one can load it using

  source ~/path/to/the/virtualenvironment/env/bin/activate

Docker installation

   Docker provides a uniform test bed for development and bug testing. Please use this environment to testing/resolving bugs.

   1. Install Docker (Desktop version): https://docs.docker.com/engine/installation/
   2. Clone and pull the latest master version of morpho
   3. Go inside morpho folder
   4. Execute docker-compose run morpho.

The container prompter should appear at the end of the installation. A directory (morpho_share) should be created in your home and mounted under the /host folder: you can modify this by editing the docker-compose file.

When reinstalling, you can remove the image using docker rmi morpho_morpho



  

  
