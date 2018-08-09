------------------
Contribute
------------------

Branching Model
------------------

Morpho uses the git flow branching model, as described here_. 
In summary, the master branch is reserved for numbered releases of morpho. 
The only branches that may branch off of master are hotfixes. 
All development should branch off of the develop branch, and merge back into the develop branch when complete. 
Once the develop branch is ready to go into a numbered release, a release branch is created where any final testing and bug fixing is carried out. 
This release branch is then merged into master, and the resulting commit is tagged with the number of the new release.

.. _here: http://nvie.com/posts/a-successful-git-branching-model/

Style
------------------

Morpho loosely follows the style suggested in the Style Guide for Python (`PEP 8`_).

.. _`PEP 8`: https://www.python.org/dev/peps/pep-0008/

Every package, module, class, and function should contain a docstring, that is, a comment beginning and ending with three double quotes. We use the `Google format`_, because the docstrings can then be automatically formatted by sphinx and shown in the API.

.. _`Google format`: https://google.github.io/styleguide/pyguide.html?showone=Comments#Comments

Every docstring should start with a single line (<=72 characters) summary of the code. This is followed by a blank line, then further description is in paragraphs separated by blank lines. Functions should contain "Args:", "Returns:", and if necessary, "Raises" sections to specify the inputs, outputs, and exceptions for the function. All text should be wrapped to around 72 characters to improve readability. 

Other Conventions
------------------

- __init__.py files:

In morpho 1, __init__.py files are set up such that
::
     from package import *

will import all functions from all subpackages and modules into the namespace. If a package contains the subpackages "subpackage1" and "subpackage2", and the modules "module1" and "module2", then the __init__.py file should include imports of the form:
::

   from . import subpackage1
   from . import subpackage2
   from ./module1 import *
   from ./module2 import *

In morpho 2, __init__.py files are set up such that
::

   from package import *

will import all  modules into the namespace, but it will not directly import the functions into the namespace. For our package containing "subpackage1", "subpackage2", "module1", and "module2", __init__.py should be of the form:
::

   __all__ = ["module1", "module2"]

In this case, functions would be called via module1.function_name(). If one wants all of the functions from module1 in the namespace, then they can include "from package.module1 import *" at the top of their code. This change to more explicit imports should prevent any issues with function names clashing as Morpho grows.

