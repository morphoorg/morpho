Validation Log
==============

Log
---

Version: v2.7.2
~~~~~~~~~~~~~~~

Release Date: July 20, 2021
''''''''''''''''''''''''''''''

Hotfixes:
'''''''''

* Updated PyBindRooFitProcessor to deal with PyROOT updates
* ROOT 6.22 or newer is now required

Version: v2.7.1
~~~~~~~~~~~~~~~

Release Date: June 3rd 2020
''''''''''''''''''''''''''''''

Hotfixes:
'''''''''

* Minor fixes on CalibrationProcessor
* Default logging level changed from warning to info

Version: v2.7.0
~~~~~~~~~~~~~~~

Release Date: June 3rd 2020
''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* CalibrationProcessor:
   * Processor performing Bayesian sensitivity calibration for continuous parameters
* Improved logger system: verbosity level can be read from analysis scripts   

Version: v2.6.0
~~~~~~~~~~~~~~~

Release Date: May 26th 2020
''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* PriorSamplingProcessor:
   * Processor for sampling inputs to a data generator from priors
   

Version: v2.5.0
~~~~~~~~~~~~~~~

Release Date: August 27th 2019
''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* P8 Compute Dependencies image update to v0.9.0
* PyBindRooFitProcessor:
   * Load external python functions to create pdfs
   * Generate fake data and fit them using user-defined pdfs

Version: v2.4.0
~~~~~~~~~~~~~~~

Release Date: August 19th 2019
''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* Divergence checks plot generator for PyStan #126
* Data vector length automatic  computation
* Possibility to set histo range from data in _create_histo
* RooFitInterfaceProcessor: plot fit and data on demand

Hotfixes:
'''''''''

* Docker-compose repair and documentation
* Fixing not random data generation with RooFit

Version: v2.3.3
~~~~~~~~~~~~~~~

Release Date: May 17th 2018
''''''''''''''''''''''''''''''

Hotfixes:
'''''''''

* Travis repair: 
   * docker-based installation
   * single test bash script

Version: v2.3.2
~~~~~~~~~~~~~~~

Release Date: April 17th 2019
''''''''''''''''''''''''''''''

Hotfixes:
'''''''''

* Downgrade pystan to v2.17.1

Version: v2.3.1
~~~~~~~~~~~~~~~

Release Date: March 28th 2019
''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* Debug section in README.md
* Upgrade pystan to v2.18.1

Version: v2.3.0
~~~~~~~~~~~~~~~

Release Date: November 13 2018
''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* RooFit base interface processor:
    * All RooFit processors now inherit from RooFitInterfaceProcessor
    * Allow to do sampling, likelihood sampling and fitting by defining the model only once
* Python API example: gaussian model



Version: v2.2.1
~~~~~~~~~~~~~~~

Release Date: Thursday November 8th 2018
''''''''''''''''''''''''''''''''''''''''

Fixes:
'''''''''''''

* Fixing the import of RootCanvas and RootHistogram in Histogram

Version: v2.2.0
~~~~~~~~~~~~~~~

Release Date: Sunday November 4th 2018
''''''''''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* Possibility to generate several histograms on the same RootCanvas
* A huge effort in documenting the code and on RTD!

Version: v2.1.5
~~~~~~~~~~~~~~~

Release Date: Friday September 28th 2018 
''''''''''''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* Add access to processors properties from ToolBox
* Travis: adding linux via Docker

Fixes:
''''''

* Documentation update: 
    * Adding docstring for processors
    * Update example
    * Adding descriptions about morpho 2, reworking the morpho 1's
* Issue tracker: adding template issues
* Plotting: better RootCanvas class, more RootHistogram methods

Version: v2.1.4
~~~~~~~~~~~~~~~

Release Date: Tues. July 31st 2018
''''''''''''''''''''''''''''''''''

Fixes:
''''''

* Travis fix: switch to XCode 9.4

Version: v2.1.3
~~~~~~~~~~~~~~~

Release Date: Thur. July 26th 2018
''''''''''''''''''''''''''''''''''

Fixes:
''''''

* RTD
    * Changed CPython to 3
    * Edited conf.py to use better_apidoc
    * Defined try/except for additional modules like ROOT and pystan
* Dependencies cleanup (matplotlib)

Version: v2.1.2
~~~~~~~~~~~~~~~

Release Date: Thur. July 19th 2018
''''''''''''''''''''''''''''''''''

Fixes:
''''''

* Update dependencies to support python 3.7

Version: v2.1.1
~~~~~~~~~~~~~~~

Release Date: Fri. June 29th 2018
'''''''''''''''''''''''''''''''''

Fixes:
''''''

* Debug of the docker and docker-compose


Version: v2.1.0
~~~~~~~~~~~~~~~

Release Date: Wed. June 27th 2018
'''''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* Morpho executable:
    * Use configuration file similar to Katydid: configuration can be edited via the CLI
    * Toolbox that creates, configures, runs and connects processors
    * Can import processors from other modules (mermithid tested)
    * Add main executable

Fixes:
''''''

Version: v2.0.0
~~~~~~~~~~~~~~~

Release Date: Sat. June 9th 2018
''''''''''''''''''''''''''''''''

New Features:
'''''''''''''

* Upgrade to morpho2:
    * Create basic processors for
           * sampling (PyStan and RooFit)
           * plotting
           * IO (ROOT, csv, json, yaml, R)
    * Added tests scripts and main example

Fixes:
''''''

* Use brew instead of conda for Travis CI


Guidelines
----------

* All new features incorporated into a tagged release should have their validation documented.
  * Document the new feature.
  * Perform tests to validate the new feature.
  * If the feature is slated for incorporation into an official analysis, perform tests to show that the overall analysis works and benefits from this feature.
  * Indicate in this log where to find documentation of the new feature.
  * Indicate in this log what tests were performed, and where to find a writeup of the results.
* Fixes to existing features should also be validated.
  * Perform tests to show that the fix solves the problem that had been indicated.
  * Perform tests to show that the fix does not cause other problems.
  * Indicate in this log what tests were performed and how you know the problem was fixed.


Template
--------

Version:
~~~~~~~~

Release Date:
'''''''''''''

New Features:
'''''''''''''

* Feature 1
    * Details
* Feature 2
    * Details

Fixes:
''''''

* Fix 1
    * Details
* Fix 2
    * Details
