Validation Log
==============

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

Log
---

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

* RTD
    * Changed CPython to 3
    * Edited conf.py to use better_apidoc
    * Defined try/except for additional modules like ROOT and pystan

Version: v2.1.2
~~~~~~~~~~~~~~~

Release Date: Thur. July 19th 2018
'''''''''''''''''''''''''''''''''

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
