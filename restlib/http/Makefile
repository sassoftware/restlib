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
