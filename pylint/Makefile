#
# Copyright (c) 2008 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#

dist_files = init_pylint.py  Makefile  pylintrc  run_pylint

all: pylint
install:

dist: default-dist

pylint:
	@echo running pylint...
	@./run_pylint
	@echo Done.  Error output is in the reports/ directory.

clean:
	rm -rf reports *,cover

include ../Make.rules
include ../Make.defs
