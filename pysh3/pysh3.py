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
import keyword

# TODO Implement completion for files

class PySHUtils(object):
	def __init__(self, path):
		self.path = path
	
	def cmd_cd(self, arguments):
		if arguments:
			target = os.path.expanduser(arguments[0])
			if os.path.isdir(target):
				os.chdir(target)
			else:
				print("Not a directory: %s" % target, file=sys.stderr)
		else:
			os.chdir(os.path.expanduser("~"))
	
	def shrun(self, shelements):
		# Find subprocesses
		processes = []
		process = []
		for element in shelements:
			if element == "|": # pipe
				processes.append(process)
				process = []
			else:
				process.append(element)
		else:
			processes.append(process)
		
		lastProcess = processes.pop()
		stdin = sys.stdin
		
		for process in processes:
			p = self.makeProcess(process, stdin, subprocess.PIPE)
			stdin = p.stdout
		
		p = self.makeProcess(lastProcess, stdin, sys.stdout)
		p.wait()
	
	def find(self, command):
		if command.startswith("./"):
			return command
		
		for path in self.path:
			filename = os.path.join(path, command)
			if os.path.isfile(filename):
				return filename
	
	def makeProcess(self, args, stdin, stdout):
		name = self.find(args[0])
		
		if name is None:
			# TODO Add a relevant exception type here
			raise Exception("Command not found: %s" % name)
		
		args[0] = name
		return subprocess.Popen(args, stdin=stdin, stdout=stdout)
	
	def inline(self, shelements):
		pass

class PySH(code.InteractiveConsole):
	banner = """PySH"""
	inlineShellPattern = re.compile(r'`([^`]+)`')
	linePattern = re.compile(r'(\s*)(.+)')
	
	def __init__(self, path=""):
		self.paths = path.split(":")
		self.util = PySHUtils(self.paths)
		self.super.__init__({
			'__pysh__' : self.util
		})
	
	def push(self, line):
		# FIXME While in block mode, the prompt is not the usual "..."
		
		m = self.linePattern.match(line)
		
		if m is not None:
			indent = m.group(1)
			line = m.group(2)
			
			shelements = shlex.split(line)
			first = shelements[0]
			
			if first in keyword.kwlist:
				# The first word is a keyword, looks like python
				line = self.processInlineShell(line)
			
			elif hasattr(self.util, "cmd_" + first):
				# It's a shell internal command like cd, help...
				line = self.processCommand(shelements)
			
			elif self.util.find(first) is not None:
				# Shell command: ls, cat...
				line = self.translate(shelements)
			
			else:
				# Ok, assume it's python by default
				line = self.processInlineShell(line)
			
			line = indent + line
		
		self.super.push(line)
	
	def interact(self):
		self.super.interact(self.banner)
	
	def translate(self, shelements):
		return "__pysh__.shrun(" + repr(shelements) + ")"
	
	def processInlineShell(self, line):
		# TODO Do a regex callback replace with __pysh__.inline
		return line
	
	def processCommand(self, shelements):
		return "__pysh__.cmd_" + shelements[0] + "(" + repr(shelements[1:]) + ")"
	
	@property
	def super(self):
		return super(PySH, self)

def main():
	console = PySH(os.getenv("PATH"))
	console.interact()

if __name__ == '__main__':
	main()
