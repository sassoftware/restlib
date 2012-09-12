#
# Copyright (C) 2004-2006 rPath, Inc.
# All rights reserved
#

SUBDIRS=localtest buildtest

.PHONY: clean test debug-test

dist_files = *.py Makefile archive/*

all:
	for dir in `find . -type d -name '*test' | fgrep -v .hg`; do \
relativelink=`echo "$$dir" | sed s,/[^/]*,/..,g | sed 's,./,,'`; \
ln -fs $${relativelink}/testsetup.py $$dir; \
done

install:
	echo "nothing to install"

test:
	python2.4 testsuite.py

debug-test:
	python2.4 testsuite.py --debug

clean: clean-coverage
	@find . \( -name \*~ -o -name \*.pyc \) -exec rm -fv {} \;
	for dir in `find . -type d -name '*test'`; do \
            rm -f $${dir}/testsetup.py*;\
        done

clean-coverage:
	@find . \( -name \*,cover \) -exec rm -fv {} \;
	@rm -rf .coverage

