# Makefile for Python AFSK Module.
#
# Source:: https://github.com/casebeer/afsk
# Author:: Christopher H. Casebeer <c@chc.name>
# Copyright:: Copyright (c) 2013 Christopher H. Casebeer. All rights reserved.
# License:: Simplified BSD License
#


.DEFAULT_GOAL := all


all: develop

install_requirements:
	pip install -r requirements.txt

develop: remember
	python setup.py develop

install: remember
	python setup.py install

uninstall:
	pip uninstall -y afsk

reinstall: uninstall install

remember:
	@echo
	@echo "Hello from the Makefile..."
	@echo "Don't forget to run: 'make install_requirements'"
	@echo

clean:
	@rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
		nosetests.xml pylint.log output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log .coverage

publish:
	python setup.py register sdist upload

nosetests: remember
	python setup.py nosetests

pep8: remember
	flake8 --max-complexity 12 --exit-zero afsk/*.py tests/*.py

flake8: pep8

lint: remember
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		-r n afsk/*.py tests/*.py || exit 0

pylint: lint

test: lint pep8 nosetests

checkmetadata:
	python setup.py check -s --restructuredtext
