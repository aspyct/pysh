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
import glob
import pydoc

from pysh.meta import __version__, __author__

PYSHRC = os.path.expanduser("~/.pyshrc")

class PySHUtils(object):
	def __init__(self, path):
		self.path = path
	
	def cmd_cd(self, arguments):
		"""Change current working directory"""
		
		if arguments:
			target = os.path.expanduser(arguments[0])
			if os.path.isdir(target):
				os.chdir(target)
			else:
				print("Not a directory: %s" % target, file=sys.stderr)
		else:
			os.chdir(os.path.expanduser("~"))
	
	def cmd_migrate(self, arguments):
		"""Migrate from your previous shell to pysh
		
		When you're ready to install pysh, execute this command first
		to migrate your current settings to the ~/.pyshrc file.
		This is necessary to keep your PATH and other important variables.
		"""
		
		print("Warning: this will overwrite your .pyshrc file.")
		yesno = input("Do you wish to continue ? y/n: ")
		if yesno == "y":
			with open(PYSHRC, "w") as f:
				f.write("export PATH={!r}\n".format(os.getenv("PATH")))
	
	def cmd_help(self, arguments):
		"""Get help on pysh"""
		
		if arguments:
			command = arguments[0]
			
			if command.startswith("("):
				# Bet user wanted pydoc's help ?
				print("For pydoc help, type \"help(...)\" with no space or use pyhelp()")
			else:
				# Get info for a specific command
				attrName = "cmd_" + command
				try:
					method = getattr(self, attrName)
				except AttributeError:
					print("No such command: " + command)
				else:
					# TODO Parse doc to remove extra whitespaces at the beginning of lines
					for line in map(lambda x: x.lstrip(), method.__doc__.split("\n")):
						print(line)
		else:
			# List available shell commands
			commands = []
			for attrName in dir(self):
				if attrName.startswith("cmd_"):
					commands.append(attrName)
		
			longest = max(map(lambda x: len(x), commands))
		
			print("For python help, use \"pyhelp()\"")
			print("For detailed help on a specific command, type \"help <command>\"")
			print()
			
			for command in commands:
				method = getattr(self, command)
				command = command[4:]
				brief = method.__doc__.split("\n", 1)[0]
				print("  {:<{}}{}".format(command, longest, brief))
	
	def shrun(self, shelements):
		try:
			self.parseAndMake(shelements).wait()
		except OSError as e:
			print(e)
	
	def parseAndMake(self, shelements, stdout=sys.stdout):
		# Find subprocesses
		processes = []
		process = []
		for element in shelements:
			if element == "|": # pipe
				processes.append(process)
				process = []
			else:
				if "~" in element:
					element = os.path.expanduser(element)
				if glob.has_magic(element):
					process.extend(glob.glob(element))
				else:
					process.append(element)
		else:
			processes.append(process)

		lastProcess = processes.pop()
		stdin = sys.stdin

		for process in processes:
			p = self.makeProcess(process, stdin, subprocess.PIPE)
			stdin = p.stdout

		return self.makeProcess(lastProcess, stdin, stdout)
	
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
		return InlineExec(self.parseAndMake(shelements, subprocess.PIPE))

class InlineExec(object):
	def __init__(self, process):
		self.process = process
	
	def __str__(self, encoding=None):
		encoding = self.getencoding(encoding)
		return self.process.stdout.read().decode(encoding)
	
	def __bytes__(self):
		return self.process.stdout.read()
	
	def __iter__(self, encoding=None):
		encoding = self.getencoding(encoding)
		
		data = self.process.stdout.readline()
		while data:
			yield data.decode(encoding).rstrip(os.linesep)
			data = self.process.stdout.readline()	

	def getencoding(self, encoding):
		if encoding is None:
			encoding = sys.getdefaultencoding()
		return encoding

class InlineVar(object):
	def __init__(self, name):
		self.name = name
	
	def __repr__(self):
		return self.name

class Completer(object):
	def __init__(self):
		self.lastText = None
		self.lastResults = None
	
	def complete(self, text, index):
		if text != self.lastText or index == 0:
			# Do a new search
			self.lastText = text
			self.results = self.search(text)
		
		try:
			return self.results[index]
		except IndexError:
			return None
	
	def search(self, text):
		results = []
		
		# If the text corresponds to a directory, add it to the result list
		if text != "." and os.path.isdir(text):
			if text[-1] == os.path.sep:
				dirname = text
			else:
				dirname = text + os.path.sep
			
			fname = ""
			results.append(dirname)
		
		else:
			dirname = os.path.dirname(text)
			fname = os.path.basename(text)
		
		# List the directory
		files = os.listdir(os.path.expanduser(dirname) or ".")
		
		for f in files:
			if f.startswith(fname):
				full = os.path.join(dirname, f)
				
				# If it's a directory, suffix with /
				if os.path.isdir(os.path.expanduser(full)):
					full += os.path.sep
				
				results.append(full)
		
		return results
	
	def install(self):
		readline.set_completer(self.complete)
		
		# Simple hack to detect if readline is actually libedit, might break
		if "libedit" in readline.__doc__:
			readline.parse_and_bind("bind '\t' rl_complete")
		else:
			readline.parse_and_bind("tab: complete")
	

class PySH(code.InteractiveConsole):
	banner = "PySH " + __version__ + " / Python " + sys.version + \
		os.linesep + "Type \"help\" for available commands."
	inlineShellPattern = re.compile(r'`([^`]+)`')
	linePattern = re.compile(r'(\s*)(.+)')
	
	def __init__(self, path=""):
		self.paths = path.split(":")
		self.util = PySHUtils(self.paths)
		self.super.__init__({
			'__pysh__' : self.util,
			'pyhelp'   : pydoc.help
		})
	
	def runscript(self, f):
		# TODO There should be a better way to do this.
		for line in f:
			self.push(line)
		else:
			# Be sure to finish the execution if the script does not end with a newline
			self.push("\n")
	
	def push(self, line):
		m = self.linePattern.match(line)
		
		if m is not None:
			indent = m.group(1)
			line = m.group(2)
			
			try:
				shelements = shlex.split(line)
				first = shelements[0]
			
			except ValueError: # Shell syntax error, not shell then
				line = self.processInlineShell(line)
			
			else:
				if first in keyword.kwlist:
					# The first word is a keyword, looks like python
					line = self.processInlineShell(line)

				elif shelements is not None and hasattr(self.util, "cmd_" + first):
					# It's a shell internal command like cd, help...
					line = self.processCommand(shelements)

				elif self.util.find(first) is not None:
					# Shell command: ls, cat...
					line = self.translate(shelements)

				else:
					# Ok, assume it's python by default
					line = self.processInlineShell(line)
			
			line = indent + line
		
		return self.super.push(line)
	
	def interact(self):
		self.super.interact(self.banner)
	
	def translate(self, shelements):
		return "(__pysh__.shrun(" + repr(self.inlineVars(shelements)) + "))"
	
	def inlineVars(self, command):
		# Find inline variables
		for i, arg in enumerate(command):
			if arg.startswith("$"): # It's an inline variable
				varname = arg[1:]
				if varname:
					command[i] = InlineVar(varname)
				else:
					raise SyntaxError("Empty variable name")
		
		return command
	
	def processInlineShell(self, line):
		def replacer(match):
			command = shlex.split(match.group(1))
			command = self.inlineVars(command)
			return "(__pysh__.inline(" + repr(command) + "))"
		
		return self.inlineShellPattern.sub(replacer, line)
	
	def processCommand(self, shelements):
		shelements = self.inlineVars(shelements)
		return "(__pysh__.cmd_" + shelements[0] + "(" + repr(shelements[1:]) + "))"
	
	@property
	def super(self):
		return super(PySH, self)
