APPNAME = geoip
VE = virtualenv
PY = bin/python
PI = bin/pip
NO = bin/nosetests -s --with-xunit
PS = bin/pserve

all: build

build:
	$(VE) --no-site-packages .
	$(PI) install -r prod-reqs.txt
	$(PY) setup.py build

test:
	$(NO) $(APPNAME)

run:
	$(PS) campaign-local.ini
