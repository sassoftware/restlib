#
# Copyright (c) 2006-2008 rPath, Inc.
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

python_files =	*.py


dist_files = Makefile $(python_files)

SUBDIRS = 

all: default-subdirs default-all

install: all install-subdirs pyfiles-install default-install
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)$(restlibdir)/http', ddir='$(restlibdir)/http', quiet=1)"
	$(PYTHON) -OO -c "import compileall; compileall.compile_dir('$(DESTDIR)$(restlibdir)/http', ddir='$(restlibdir)/http', quiet=1)"

dist: default-dist

clean: clean-subdirs default-clean

include ../../Make.rules
include ../../Make.defs
