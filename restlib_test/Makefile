#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
