#!/usr/bin/env python3

import sys

if sys.version_info.major < 3:
	print("Install me with Python3 only.  -- pysh")
	sys.exit()

from distutils.core import setup

setup(
	name="pysh",
	version="0.1",
	description="A shell mixing Python and Bash syntax",
	author="Antoine d'Otreppe de Bouvette",
	author_email="a.dotreppe@aspyct.org",
	url="http://www.github.com/aspyct/pysh",
	scripts=["bin/pysh"],
	packages=["pysh"],
	license="MIT"
)
