from setuptools import setup
import sys

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
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

major, minor = sys.version_info[:2]

packages = ['greenlet_profiler']
setup(
    name='greenlet-profiler',
    version='0.1',
    packages=packages,
    description=description,
    long_description=long_description,
    author='A. Jesse Jiryu Davis',
    author_email='jesse@emptysquare.net',
    url='http://github.com/ajdavis/greenlet-profiler/',
    install_requires=['yappi'],
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=filter(None, classifiers.split('\n')),
    keywords='greenlet gevent profiler asynchronous')
