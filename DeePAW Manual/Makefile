SPHINXBUILD   = /data/home/hzw111111/miniforge3/envs/maceedl/bin/sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

.PHONY: help html clean

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)"

clean:
	@rm -rf $(BUILDDIR)
