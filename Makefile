APPNAME = campaign
VE = virtualenv
PY = bin/python
PI = bin/pip
NO = bin/nosetests -s --with-xunit
PS = bin/pserve

all: build

build:
	$(VE) --no-site-packages .
	bin/easy_install -U distribute
	$(PI) install -r prod-reqs.txt
<<<<<<< HEAD
	$(PY) setup.py develop
=======
	$(PY) setup.py build
	$(PY) setup.py install
>>>>>>> 217f033e4178c923a7385f418aff63e31fa3ae29

test:
	$(NO) $(APPNAME)

run:
	$(PS) campaign-local.ini
<<<<<<< HEAD

=======
>>>>>>> 217f033e4178c923a7385f418aff63e31fa3ae29
