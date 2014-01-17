import os
import sys
from distutils.ccompiler import new_compiler
from setuptools import Extension
from setuptools import setup

# For now, greenlet-profiler includes a patched version of Sumer Cip's yappi.
# The original yappi source is at https://bitbucket.org/sumerc/yappi, and my
# fork is at https://bitbucket.org/emptysquare/gappi. The patched source is
# included in this project in the _vendorized_yappi directory, and the
# following extension configuration is adapted from yappi's setup.py.
user_macros = []
user_libraries = []
compile_args = []
link_args = []

if os.name == 'posix' and sys.platform != 'darwin': 
    compiler = new_compiler()
    if compiler.has_function('timer_create', libraries=('rt',)):
        user_macros.append(('LIB_RT_AVAILABLE', '1'))
        user_libraries.append('rt')

yappi_extension = Extension(
    '_yappi',
    sources=[
        '_vendorized_yappi/_yappi.c',
        '_vendorized_yappi/callstack.c',
        '_vendorized_yappi/hashtab.c',
        '_vendorized_yappi/mem.c',
        '_vendorized_yappi/freelist.c',
        '_vendorized_yappi/timing.c'],
    define_macros=user_macros,
    libraries=user_libraries,
    extra_compile_args=compile_args,
    extra_link_args=link_args)

# End of setup code adapted from yappi.

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Development Status :: 1 - Planning
Natural Language :: English
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Operating System :: MacOS :: MacOS X
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
"""

description = 'Greenlet-aware Python performance profiler, built on yappi.'
long_description = open("README.rst").read()
packages = []
if 'nosetests' in sys.argv:
    packages.append('test')

setup(
    name='greenlet-profiler',
    version='0.1',
    packages=packages,
    # Include yappi's C extension, _yappi.so.
    ext_modules=[yappi_extension],
    # Include yappi.py along with our own greenlet_profiler.py.
    py_modules=['_vendorized_yappi/yappi', '_vendorized_yappi/__init__', 'greenlet_profiler'],
    description=description,
    long_description=long_description,
    author='A. Jesse Jiryu Davis',
    author_email='jesse@emptysquare.net',
    url='http://github.com/ajdavis/greenlet-profiler/',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=filter(None, classifiers.split('\n')),
    keywords='greenlet gevent profiler asynchronous',
    # use python setup.py nosetests to test
    setup_requires=['nose'],
    zip_safe=False)
