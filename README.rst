pysh
####

pysh is a Shell that mixes Python and Bash syntax.

Requirements
============

pysh requires only Python3 to run, and should work on Linux and OSX platforms (and probably other UNIX environments).

Installing
==========

You don't need to install PySH to start working with it. Jump to "Discover it" if you do not wish to install it.

Run the usual setup.py script. The script will run only if you launch it with Python3.
Note: under OSX, you may need to add the path to your python library in order to have pysh in the path.

! Important ! PySH is still beta software, and you should not use it for your everyday work unless your know what you are doing.
If, like me, you want to use PySH as default shell, the best option is to set it only in your terminal emulator (gnome-terminal, Apple terminal app...) via the preferences of the application.

Discover it
===========

It's really easy to get started. All you need is Python3. Download the zip file, unzip it on the destination of your choice, chmod the `pysh` file and execute it. ::

  unzip aspyct-pysh-xxxx.zip -d aspyct-pysh
  cd aspyct-pysh
  chmod +x bin/pysh
  ./bin/pysh

You are now in what looks like a regular python interpreter. Try to write some python::

  > print("Hello")
  > if True:
  .    print("pysh looks terrific ! :)")

Shell commands also work, as well as autocompletion with tab::

  > ls
  > vi <yourfile>

You can also mix python and shell::

  > if True:
  .    ls
  .
  > myvar = `ls`
  > print(myvar)

Internals
=========

pysh uses the built-in *code* module to emulate the python interpreter, and tries to detect whether a line is a shell command or regular python code. Every line is translated before it is fed to the interpreter.

In the pysh shell, there is a special variable named `__pysh__` that is used to make shell commands happen. You may use this class directly, but it will probably not make your code cleaner.