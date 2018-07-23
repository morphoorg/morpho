# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = morpho
SOURCEDIR     = .
BUILDDIR      = build

PY_CMD = import better_apidoc; better_apidoc.main(['better_apidoc','-t', '_templates','--force','--separate','-o','better_apidoc_out','../$(SPHINXPROJ)'])  # overwrite existing files
APIDOC_CMD = python -c "$(PY_CMD)"

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

betterapi:
	@$(APIDOC_CMD)