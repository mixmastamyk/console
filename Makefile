
include Makefile.common

ver_pattern := version =


# Python script to render a Jinja template, works around PyPI limitations
define JINJA_FU
from os import environ
from jinja2 import Environment
j2 = Environment(trim_blocks=True, lstrip_blocks=True)
with open('docs/readme.templ') as f:
    template = j2.from_string(f.read())
print(template.render(mode=environ['RM_MODE']))
endef
export JINJA_FU


demos:  ## Show various functionality
	echo | CLICOLOR_FORCE=1 python3 -m console.demos -d # works oddly under make


docs: docs/readme.rst readme.rst docs-default
	rsync --recursive --human-readable --delete-before  --update docs/_build/html/ ../../mixmastamyk.bitbucket.org/console/


docs/readme.rst: docs/readme.templ
	RM_MODE=sphx python3 -c "$$JINJA_FU" > docs/readme.rst


readme.rst: docs/readme.templ
	RM_MODE=pypi python3 -c "$$JINJA_FU" > readme.rst


publish: publish-default
	DOC_DIR='../../mixmastamyk.bitbucket.org/console'
	if [ -d "$$DOC_DIR" ]; then
		cd ../../mixmastamyk.bitbucket.org/console/ \
			&& git add . && git commit -m . && git push
	fi


test:  ## Test suite
	-pyflakes *.py */*.py console/console; \
		if [ $$? -ne 0 ] ; then sleep 3 ; fi
	tput reset  # clear screen, scrollback
	pytest --color=no --showlocals --verbose


.PHONY: demos docs publish test
