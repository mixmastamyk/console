
# runs twice
#~ VERSION := `python3 -c 'from console.constants import __version__ as v; print(v)'`

clean:
	git gc
	rm -f readme.html
	rm -rf .pytest_cache/
	make -C docs clean

	find -type d -name __pycache__ -exec rm -rf '{}' \;


demos:
	CLICOLOR_FORCE=1 python3 -m console.demos


docs:
	rst2html.py readme.rst > readme.html
	make -C docs html
	refresh.sh Console


publish: test
	python3 setup.py check --restructuredtext --strict # required: readme_renderer
	python3 setup.py sdist upload
	# backslash at end of line very important:
#~ 	VERSION=`python3 -c 'from console.constants import __version__ as v; print(v)'`;\
#~ 	git tag -a $$VERSION -m "version $$VERSION"
#~ 	git push --tags


tag:
	# backslash at end of line very important:
	VERSION=`python3 -c 'from console.constants import __version__ as v; print(v)'`;\
	git tag -a $$VERSION -m "version $$VERSION"
	git push --tags


test:
	clear
	pyflakes *.py console/*.py
	tput reset  # clear screen, scrollback
	pytest --capture=no --color=no


tests: test


# all targets for now
.PHONY: $(MAKECMDGOALS)

