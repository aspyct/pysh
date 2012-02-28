#!/usr/bin/env python3

# Copyright (c) 2012 Antoine d'Otreppe de Bouvette
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import shlex
import code
import readline
import os
import os.path
import re
import subprocess

class PySHUtils(object):
	def shrun(shelements):
		# Find subprocesses
		processes = []
		process = []
		for element in shelements:
			if element == "|": # pipe
				processes.append(process)
				process = []
		else:
			processes.append(process)
		
		if 
		
		print("Running " + repr(shelements))
	
	def process(name, args, stdin=sys.stdin, stdout=sys.stdout):
		pass
	
	def inline(shelements):
		pass

class PySH(code.InteractiveConsole):
	banner = """PySH"""
	inlineShellPattern = re.compile(r'`([^`]+)`')
	
	def __init__(self, path=""):
		self.super.__init__({'__pysh__':PySHUtils})
		self.paths = path.split(":")
	
	def push(self, line):
		shelements = shlex.split(line)
		
		isShell = False
		
		# Try to find an executable corresponding to the line
		for path in self.paths:
			filename = os.path.join(path, shelements[0])
			if os.path.isfile(filename):
				# Got it, translate shell into python :)
				line = self.translate(shelements)
				isShell = True
		
		if not isShell:
			# Maybe there are some `` in there
			line = self.processInlineShell(line)
		
		self.super.push(line)
	
	def interact(self):
		self.super.interact(self.banner)
	
	def translate(self, shelements):
		return "__pysh__.shrun(" + repr(shelements) + ")"
	
	def processInlineShell(self, line):
		# TODO Do a regex callback replace with __pysh__.inline
		return line
	
	@property
	def super(self):
		return super(PySH, self)

def main():
	console = PySH(os.getenv("PATH"))
	console.interact()

if __name__ == '__main__':
	main()
