

clean:
	git gc

	rm -rf docs/_build

	find -type d -name __pycache__ -exec rm -rf '{}' \;


test:
	clear
	pyflakes **.py
	tput reset  # clear screen, scrollback
	pytest --capture=no --color=yes


demos:

	env CLICOLOR_FORCE=1 python3 -m console.demos
