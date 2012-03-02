pysh
####

pysh is a Shell that mixes Python and Bash syntax.

Discover it
===========

It's really easy to get started. All you need is Python3. Download the zip file, unzip it on the destination of your choice, chmod the `pysh` file and execute it. ::

  unzip aspyct-pysh-xxxx.zip -d pysh
  cd pysh
  chmod +x pysh
  ./pysh

You are now in what looks like a regular python interpreter. Try to write some python::

  > print("Hello")
  > if True:
  .    print("pysh looks terrific ! :)")

Shell commands also work::

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