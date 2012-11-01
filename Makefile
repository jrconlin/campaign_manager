APPNAME = campaign
VE = virtualenv
PY = bin/python
PI = bin/pip
NO = bin/nosetests -s --with-xunit
NC = --with-coverage --cover-package=$(APPNAME)
PS = bin/pserve

all: build

build:
	$(VE) --no-site-packages .
	bin/easy_install -U distribute
	$(PI) install -r prod-reqs.txt
	$(PY) setup.py develop

test:
	$(NO) $(APPNAME)

run:
	$(PS) campaign-local.ini

