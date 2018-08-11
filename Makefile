

clean:
	git gc

	rm -rf docs/_build
	rm -rf .pytest_cache/

	find -type d -name __pycache__ -exec rm -rf '{}' \;


test:
	clear
	pyflakes **.py
	tput reset  # clear screen, scrollback
	pytest --capture=no --color=no


demos:

	env CLICOLOR_FORCE=1 python3 -m console.demos

docs:
	make -C docs html
	refresh.sh Console

.PHONY: docs
