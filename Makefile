
# runs twice
#~ VERSION := `python3 -c 'from console.constants import __version__ as v; print(v)'`

# Python script to render a Jinja template, work around PyPI limitations
define JINJA_FU
from os import environ
from jinja2 import Environment
j2 = Environment(trim_blocks=True, lstrip_blocks=True)
with open('docs/readme.templ') as f:
    template = j2.from_string(f.read())
print(template.render(mode=environ['RM_MODE']))
endef
export JINJA_FU


docs/readme.rst: docs/readme.templ
	RM_MODE=sphx python3 -c "$$JINJA_FU" > docs/readme.rst


readme.rst: docs/readme.templ
	RM_MODE=pypi python3 -c "$$JINJA_FU" > readme.rst


readme.html: readme.rst
	rst2html.py readme.rst > readme.html


check_readme: readme.rst
	# requires readme_renderer
	python3 setup.py check --restructuredtext --strict


clean:
	git gc
	rm -rf readme.html .pytest_cache build dist .eggs htmlcov
	make -C docs clean

	-find -type d -name __pycache__ -exec rm -rf '{}' \;


demos:
	CLICOLOR_FORCE=1 python3 -m console.demos


docs: docs/readme.rst readme.rst
	make -C docs html
	refresh.sh Console
	rsync --recursive --human-readable --delete-before  --update docs/_build/html/ ../../mixmastamyk.bitbucket.org/console/


publish: test check_readme docs
	rm -rf build  # possible wheel bug
	python3 setup.py sdist bdist_wheel --universal upload

	pip3 install --user -e .  # fix bug on next invocation
	cd ../../mixmastamyk.bitbucket.org/console/ && git add . && git commit -m . && git push


test:
	clear
	pyflakes *.py */*.py
	tput reset  # clear screen, scrollback
	pytest --capture=no --color=no


tests: test


# all targets for now
.PHONY: $(MAKECMDGOALS)
