#
# Copyright (c) rPath, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
