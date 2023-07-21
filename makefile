build:
	py -m build

test:
	coverage run -m pytest
	coverage html
	coverage report -m